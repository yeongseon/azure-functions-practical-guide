"""Focused Markdown examples, following test_retry_recipe's compile/exec pattern.

Local SDK contracts only: no Azure authentication, storage, or host evidence.
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Final
from unittest.mock import Mock, patch

import azure.functions as func
import pytest
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobProperties, BlobServiceClient, ContainerClient

ROOT: Final = Path(__file__).resolve().parents[1]
EXAMPLES: Final = [
    ("docs/reference/platform-limits.md", "## Reusable Python HTTP Client"),
    ("docs/language-guides/python/recipes/http-api.md", "## Complete Example: CRUD API"),
    ("docs/language-guides/python/recipes/managed-identity.md",
     "### Example: Access Blob Storage with Managed Identity"),
]


@pytest.fixture
def example(request: pytest.FixtureRequest) -> ModuleType:
    """Execute the selected, complete function_app.py without injecting globals."""
    relative_path, heading = request.param
    path = ROOT / relative_path
    text = path.read_text(encoding="utf-8")
    assert heading in text, f"Missing documented example: {path}: {heading}"
    section = text.split(heading, 1)[1]
    blocks = re.findall(r"```python\n(.*?)```", section, re.DOTALL)
    assert blocks, f"Missing Python code block: {path}: {heading}"
    source = blocks[0]
    # Undefined names inside uncalled branches must fail too, not just at import.
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--select", "F821",
         "--stdin-filename", str(path.with_suffix(".py")), "-"],
        input=source, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, f"{path}: {result.stdout}{result.stderr}"
    module = ModuleType("python_doc_example")
    exec(compile(source, str(path), "exec"), module.__dict__)  # noqa: S102 -- trusted repository example
    return module


@pytest.mark.parametrize(("example", "expected_routes"), [
    (EXAMPLES[0], [("get_data", "data", ("GET",))]),
    (EXAMPLES[1], [
        ("create_item", "items", ("POST",)),
        ("delete_item", "items/{item_id}", ("DELETE",)),
        ("get_item", "items/{item_id}", ("GET",)),
        ("list_items", "items", ("GET",)),
        ("update_item", "items/{item_id}", ("PUT",)),
    ]),
    (EXAMPLES[2], [("list_blobs", "blobs", ("GET",))]),
], indirect=["example"])
def test_complete_examples_index_without_injected_names(
    example: ModuleType, expected_routes: list[tuple[str, str, tuple[str, ...]]],
) -> None:
    # Given a complete Markdown example with no test-provided bp/func/app globals.
    # When the real SDK indexes its registered blueprint.
    functions = example.__dict__["app"].get_functions()
    routes = []
    for function in functions:
        trigger, = (
            binding for binding in function.get_bindings_dict()["bindings"]
            if binding["type"] == "httpTrigger"
        )
        routes.append((
            function.get_function_name(), trigger["route"],
            tuple(sorted(method.value for method in trigger["methods"])),
        ))
    # Then every handler has exactly its documented route and HTTP methods.
    assert sorted(routes) == expected_routes


@pytest.mark.parametrize("example", [EXAMPLES[0]], indirect=True)
def test_connection_client_is_reused(
    example: ModuleType, monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given a synthetic upstream response at the external HTTP seam.
    monkeypatch.delenv("UPSTREAM_URL", raising=False)
    session = example.__dict__["session"]
    upstream = Mock()
    upstream.json.return_value = {"value": 42}
    request = func.HttpRequest("GET", "http://localhost:7071/api/data", body=b"")
    # When two invocations fetch data.
    with patch.object(session, "get", return_value=upstream) as get:
        responses = [example.__dict__["get_data"](request) for _ in range(2)]
    # Then both use the same session with a timeout and preserve the JSON response.
    assert [json.loads(response.get_body()) for response in responses] == [{"value": 42}] * 2
    assert get.call_count == 2
    get.assert_called_with("https://example.com/data", timeout=10)
    assert upstream.raise_for_status.call_count == 2


@pytest.mark.parametrize("example", [EXAMPLES[1]], indirect=True)
def test_crud_round_trip(example: ModuleType) -> None:
    # Given an empty in-memory blueprint and a synthetic item.
    namespace = example.__dict__
    request = func.HttpRequest(
        "POST", "http://localhost:7071/api/items", body=b'{"name":"demo"}',
    )
    # When the documented create/read/update/list/delete sequence runs.
    created = namespace["create_item"](request)
    item_id = json.loads(created.get_body())["id"]
    item_request = func.HttpRequest(
        "GET", f"http://localhost:7071/api/items/{item_id}",
        route_params={"item_id": item_id}, body=b'{"name":"updated"}',
    )
    fetched = namespace["get_item"](item_request)
    updated = namespace["update_item"](item_request)
    listed = namespace["list_items"](request)
    deleted = namespace["delete_item"](item_request)
    missing = namespace["get_item"](item_request)
    # Then externally visible statuses and payloads follow the CRUD contract.
    assert created.status_code == 201
    assert json.loads(fetched.get_body())["name"] == "demo"
    assert json.loads(updated.get_body())["name"] == "updated"
    assert json.loads(listed.get_body())["total"] == 1
    assert deleted.status_code == 204
    assert missing.status_code == 404


@pytest.mark.parametrize("body", [b"not-json", b"[]", b"null", b"{}"])
@pytest.mark.parametrize("example", [EXAMPLES[1]], indirect=True)
def test_crud_rejects_invalid_create(example: ModuleType, body: bytes) -> None:
    # Given malformed JSON, a non-object, or an object missing its name.
    request = func.HttpRequest("POST", "http://localhost:7071/api/items", body=body)
    # When creation is attempted.
    response = example.__dict__["create_item"](request)
    # Then invalid input is a client error rather than an exception or stored item.
    assert response.status_code == 400


@pytest.mark.parametrize("example", [EXAMPLES[2]], indirect=True)
def test_blob_identity_client_is_cached(
    example: ModuleType, monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given SDK-shaped boundary doubles, never a real token or network request.
    monkeypatch.setenv("STORAGE_ACCOUNT_NAME", "examplestorage")
    credential = Mock(spec=DefaultAzureCredential)
    client = Mock(spec=BlobServiceClient)
    container = Mock(spec=ContainerClient)
    client.get_container_client.return_value = container
    container.list_blobs.return_value = [BlobProperties(name="demo.txt", **{"Content-Length": 7})]
    request = func.HttpRequest("GET", "http://localhost:7071/api/blobs", body=b"")
    # When two requests use the documented lazy client factory.
    with patch.dict(example.__dict__, {
            "DefaultAzureCredential": Mock(spec=DefaultAzureCredential, return_value=credential),
            "BlobServiceClient": Mock(spec=BlobServiceClient, return_value=client),
    }):
        responses = [example.__dict__["list_blobs"](request) for _ in range(2)]
        example.__dict__["DefaultAzureCredential"].assert_called_once_with()
        example.__dict__["BlobServiceClient"].assert_called_once_with(
            account_url="https://examplestorage.blob.core.windows.net", credential=credential,
        )
    # Then identity is passed to the cached SDK client and blobs are serialized.
    assert [json.loads(response.get_body()) for response in responses] == [
        {"blobs": [{"name": "demo.txt", "size": 7}]},
    ] * 2
    assert client.get_container_client.call_args_list == [(('uploads',), {})] * 2


def test_connection_route_uses_declared_prefix() -> None:
    # Given the complete connection-reuse example and its adjacent host.json.
    path = ROOT / EXAMPLES[0][0]
    section = path.read_text(encoding="utf-8").split(EXAMPLES[0][1], 1)[1]
    source = re.findall(r"```python\n(.*?)```", section, re.DOTALL)[0]
    host = json.loads(re.findall(r"```json\n(.*?)```", section, re.DOTALL)[0])
    module = ModuleType("connection_route")
    exec(compile(source, str(path), "exec"), module.__dict__)  # noqa: S102 -- trusted repository example
    # When real SDK binding metadata is combined with the declared host prefix.
    function = module.__dict__["app"].get_functions()[0]
    trigger = function.get_trigger().get_dict_repr()
    route = "/" + host["extensions"]["http"]["routePrefix"] + "/" + trigger["route"]
    # Then exactly one api prefix is present, with anonymous GET access.
    assert route == "/api/data"
    assert trigger["methods"] == [func.HttpMethod.GET]
    assert trigger["authLevel"] == func.AuthLevel.ANONYMOUS
