"""Source/local SDK handler checks; no deployed authorization claims."""

import asyncio
import importlib
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import azure.functions as func
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps/python"))
from blueprints import diagnostics, durable_lab
from config.lab_limits import LabInputError, parse_delay, parse_replay


@pytest.mark.parametrize("setting", [None, "false", "TRUE", "1"])
def test_lab_routes_absent_when_not_explicitly_enabled(monkeypatch, setting):
    # Given no explicit opt-in and no telemetry exporter.
    from config import telemetry
    monkeypatch.setattr(telemetry, "configure_telemetry", lambda: None)
    monkeypatch.delenv("LAB_ENDPOINTS_ENABLED", raising=False)
    if setting is not None:
        monkeypatch.setenv("LAB_ENDPOINTS_ENABLED", setting)
    # When the app is indexed.
    import function_app
    app = importlib.reload(function_app).app
    functions = app.get_functions()
    routes = [b.get_dict_repr()["route"] for f in functions
              for b in f.get_bindings() if b.type == "httpTrigger"]
    # Then health remains but diagnostics and fault injection are absent.
    assert "health" in routes
    assert not any(r.startswith(("diagnostics/", "durable/", "exceptions/")) for r in routes)
    assert {f.get_function_name() for f in functions} >= {
        "replay_storm_orchestrator", "replay_lab_activity"}


@pytest.mark.parametrize("body", [
    b"{", b"[]", b"null", b'"text"', b"\xff", b" " * 4097,
    b'{"instances":0}', b'{"instances":-1}', b'{"instances":11}',
    b'{"instances":true}', b'{"instances":1.5}', b'{"iterations":"100"}',
    b'{"iterations":0}', b'{"iterations":5001}', b'{"iterations":NaN}',
    b'{"continueAsNewEvery":-1}', b'{"continueAsNewEvery":5001}',
    b'{"continueAsNewEvery":null}', b'{"instances":3,"iterations":2000}',
])
def test_invalid_start_does_not_schedule_work(body):
    # Given untrusted request bytes and a client that records scheduling.
    req = func.HttpRequest("POST", "http://localhost", body=body)
    client = AsyncMock()
    # When the SDK handler is invoked.
    response = asyncio.run(durable_lab.start_replay_lab.build().get_user_function().__wrapped__(req, client))
    # Then rejection happens before any work starts.
    assert response.status_code in (400, 413)
    client.start_new.assert_not_called()


@pytest.mark.parametrize("reset", [0, 250])
def test_documented_replay_workload_remains_supported(monkeypatch, reset):
    # Given the documented incident/recovery workloads.
    monkeypatch.setenv("DurableLab__ContinueAsNewEvery", "250")
    req = func.HttpRequest("POST", "http://localhost", body=json.dumps(
        {"instances": 1, "iterations": 2000, "continueAsNewEvery": reset}).encode())
    client = AsyncMock()
    client.start_new.return_value = "instance"
    # When scheduling the lab.
    response = asyncio.run(durable_lab.start_replay_lab.build().get_user_function().__wrapped__(req, client))
    # Then exactly the bounded requested work is scheduled.
    assert response.status_code == 202
    assert client.start_new.call_args.args[2]["continueAsNewEvery"] == reset
    assert client.start_new.await_count == 1


@pytest.mark.parametrize("delay", ["-1", "25001", "1.5", "NaN", "Infinity", "", "1x"])
def test_invalid_delay_never_sleeps(monkeypatch, delay):
    # Given an invalid delay and a sleep recorder.
    sleeps = []
    monkeypatch.setattr(diagnostics.time, "sleep", sleeps.append)
    req = func.HttpRequest("GET", "http://localhost", params={"delay_ms": delay}, body=b"")
    # When invoking the slow endpoint.
    response = diagnostics.slow_response.build().get_user_function()(req)
    # Then it rejects instead of clamping or executing.
    assert response.status_code == 400
    assert sleeps == []


def test_enabled_lab_bindings_require_keys(monkeypatch):
    from config import telemetry
    monkeypatch.setattr(telemetry, "configure_telemetry", lambda: None)
    monkeypatch.setenv("LAB_ENDPOINTS_ENABLED", "true")
    import function_app
    functions = importlib.reload(function_app).app.get_functions()
    bindings = [b.get_dict_repr() for f in functions for b in f.get_bindings()
                if b.type == "httpTrigger"]
    lab = [b for b in bindings if b["route"].startswith(("diagnostics/", "durable/", "exceptions/"))]
    assert len(lab) == 8
    assert all(b["authLevel"] == func.AuthLevel.FUNCTION for b in lab)


@pytest.mark.parametrize("endpoint", ["storage_probe", "identity_probe", "dns_resolve"])
def test_backend_error_is_only_in_operator_logs(monkeypatch, caplog, endpoint):
    import azure.identity
    monkeypatch.setenv("AzureWebJobsStorage__accountName", "examplestorage")
    monkeypatch.setattr(azure.identity, "ManagedIdentityCredential",
                        Mock(side_effect=RuntimeError("private-backend-detail")))
    monkeypatch.setattr(diagnostics.socket, "getaddrinfo",
                        Mock(side_effect=diagnostics.socket.gaierror("private-backend-detail")))
    req = func.HttpRequest("GET", "http://localhost", params={"host": "example.com"}, body=b"")
    with caplog.at_level("ERROR"):
        response = getattr(diagnostics, endpoint).build().get_user_function()(req)
    assert response.status_code == 502
    assert b"private-backend-detail" not in response.get_body()
    assert "private-backend-detail" in caplog.text


def test_storage_probe_does_not_expose_listing(monkeypatch):
    import azure.identity
    import azure.storage.blob
    monkeypatch.setenv("AzureWebJobsStorage__accountName", "examplestorage")
    monkeypatch.setattr(azure.identity, "ManagedIdentityCredential", Mock())
    client = Mock()
    client.list_containers.return_value.by_page.return_value = iter([[{"name": "private-container"}]])
    monkeypatch.setattr(azure.storage.blob, "BlobServiceClient", Mock(return_value=client))
    req = func.HttpRequest("GET", "http://localhost", body=b"")
    response = diagnostics.storage_probe.build().get_user_function()(req)
    assert response.status_code == 200
    assert set(json.loads(response.get_body())) == {"status", "elapsedMs"}
    client.list_containers.assert_called_once_with(results_per_page=1)


def test_identity_probe_does_not_expose_client_id(monkeypatch):
    import azure.identity
    monkeypatch.setenv("AzureWebJobsStorage__clientId", "private-identity-id")
    credential = Mock()
    credential.get_token.return_value.expires_on = 1800000000
    monkeypatch.setattr(azure.identity, "ManagedIdentityCredential", Mock(return_value=credential))
    req = func.HttpRequest("GET", "http://localhost", body=b"")
    response = diagnostics.identity_probe.build().get_user_function()(req)
    assert response.status_code == 200
    assert "clientId" not in json.loads(response.get_body())
    assert b"private-identity-id" not in response.get_body()


def test_maximum_workload_and_delay_boundaries():
    workload = parse_replay(b'{"instances":10,"iterations":500,"continueAsNewEvery":5000}', ("100", "0"))
    assert workload.instances * workload.iterations == 5000
    assert workload.continue_every == 5000
    assert parse_delay("0") == 0
    assert parse_delay("25000") == 25000


@pytest.mark.parametrize("value", ["-1", "5001", "1x", "Infinity", "1.5"])
def test_environment_defaults_cannot_bypass_workload_bounds(value):
    with pytest.raises(LabInputError):
        parse_replay(b"", (value, "0"))
