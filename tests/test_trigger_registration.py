"""Local SDK indexing checks only; no Azure listener or execution evidence."""

import importlib
import sys
from pathlib import Path
from typing import Final

import azure.functions as func
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps/python"))

DEFAULT_FUNCTIONS: Final = {
    "health", "info", "log_levels", "external_dependency",
    "replay_storm_orchestrator", "replay_lab_activity", "eventhub_lag_processor",
}
OPTIONAL_TRIGGERS: Final = (
    ("QUEUE_LAB_ENABLED", "queue_processor", "queueTrigger"),
    ("TIMER_LAB_ENABLED", "timer_lab", "timerTrigger"),
    ("SCHEDULED_TRIGGER_ENABLED", "scheduled_cleanup", "timerTrigger"),
    ("BLOB_TRIGGER_ENABLED", "process_blob", "blobTrigger"),
)


@pytest.fixture(autouse=True)
def isolated_registration_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep indexing independent of developer settings and telemetry exporters."""
    from config import telemetry

    monkeypatch.setattr(telemetry, "configure_telemetry", lambda: None)
    monkeypatch.delenv("LAB_ENDPOINTS_ENABLED", raising=False)
    for setting, _, _ in OPTIONAL_TRIGGERS:
        monkeypatch.delenv(setting, raising=False)


def indexed_functions() -> list[func.Function]:
    """Index a fresh entrypoint with the real Azure Functions SDK."""
    import function_app

    return importlib.reload(function_app).app.get_functions()


def test_default_app_has_only_existing_functions() -> None:
    # Given no optional trigger or HTTP lab opt-in.
    # When the entrypoint is indexed.
    functions = indexed_functions()
    # Then no unrelated queue, timer or blob listener is activated.
    assert {f.get_function_name() for f in functions} == DEFAULT_FUNCTIONS


@pytest.mark.parametrize("setting,name,trigger_type", OPTIONAL_TRIGGERS)
def test_selected_trigger_is_indexed_without_unrelated_listeners(
    monkeypatch: pytest.MonkeyPatch, setting: str, name: str, trigger_type: str,
) -> None:
    # Given exactly one explicitly selected lab/tutorial variant.
    monkeypatch.setenv(setting, "true")
    # When the real entrypoint is indexed (not the blueprint in isolation).
    functions = indexed_functions()
    # Then its trigger must exist and the other optional listeners stay absent.
    assert {f.get_function_name() for f in functions} == DEFAULT_FUNCTIONS | {name}
    selected = next(f for f in functions if f.get_function_name() == name)
    binding = next(b.get_dict_repr() for b in selected.get_bindings() if b.type == trigger_type)
    expected = {
        "queue_processor": {"queueName": "work-items", "connection": "QueueStorage"},
        "timer_lab": {"schedule": "%TIMER_LAB_SCHEDULE%", "runOnStartup": False},
        "scheduled_cleanup": {"schedule": "0 */5 * * * *", "runOnStartup": False},
        "process_blob": {"path": "uploads/{name}", "connection": "AzureWebJobsStorage", "source": "EventGrid"},
    }
    assert binding.items() >= expected[name].items()


@pytest.mark.parametrize("value", ["false", "TRUE", "1", ""])
def test_optional_triggers_require_exact_opt_in(
    monkeypatch: pytest.MonkeyPatch, value: str,
) -> None:
    # Given settings that do not explicitly opt in.
    for setting, _, _ in OPTIONAL_TRIGGERS:
        monkeypatch.setenv(setting, value)
    # When the entrypoint is indexed.
    functions = indexed_functions()
    # Then the default function set is unchanged.
    assert {f.get_function_name() for f in functions} == DEFAULT_FUNCTIONS


def test_combined_trigger_selection_does_not_enable_http_labs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given an isolated app deliberately selecting all four optional listeners.
    for setting, _, _ in OPTIONAL_TRIGGERS:
        monkeypatch.setenv(setting, "true")
    # When the entrypoint is indexed.
    functions = indexed_functions()
    # Then each selected function appears once without bypassing #167's gate.
    names = [f.get_function_name() for f in functions]
    assert set(names) == DEFAULT_FUNCTIONS | {name for _, name, _ in OPTIONAL_TRIGGERS}
    assert len(names) == len(set(names))
