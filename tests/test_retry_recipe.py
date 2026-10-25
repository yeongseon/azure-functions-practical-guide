"""Execute the documented recipe locally; no Azure host or checkpoint evidence."""

import logging
import re
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import azure.functions as func
import pytest


class Recipe(ModuleType):
    def __init__(self) -> None:
        super().__init__("retry_recipe")
        self.app: func.FunctionApp = func.FunctionApp()


@pytest.fixture
def recipe(monkeypatch: pytest.MonkeyPatch) -> func.Function:
    """Load the actual fixed-delay Markdown example with the real decorators."""
    monkeypatch.setenv("SIMULATED_FAILURES", "2")
    path = Path(__file__).resolve().parents[1] / "docs/language-guides/python/recipes/retry.md"
    source: str = re.findall(r"```python\n(.*?)```", path.read_text(), re.DOTALL)[0]
    module = Recipe()
    exec(compile(source, str(path), "exec"), module.__dict__)  # noqa: S102 -- trusted repository example under test
    return module.app.get_functions()[0]


def invoke(recipe: func.Function, retry_count: int) -> None:
    """Supply invocation metadata; the SDK does not execute runtime retries."""
    context = Mock(spec=func.Context)
    context.retry_context = Mock(
        spec=["retry_count", "max_retry_count"], retry_count=retry_count, max_retry_count=3,
    )
    job: Callable[[func.TimerRequest, func.Context], None] = recipe.get_user_function()
    job(Mock(spec=func.TimerRequest), context)


def test_transient_failure_propagates(recipe: func.Function) -> None:
    # Given a dependency that fails on its initial execution.
    # When the host invokes it with retry_count=0.
    # Then an exception escapes so the host can mark the invocation failed.
    with pytest.raises(ConnectionError):
        invoke(recipe, 0)


def test_success_after_retry_returns_normally(recipe: func.Function) -> None:
    # Given the simulated dependency has recovered after two failed attempts.
    # When the third attempt runs.
    result = invoke(recipe, 2)
    # Then completed work can return normally.
    assert result is None


@pytest.mark.parametrize("retry_count", [0, 1, 2, 3])
def test_persistent_failure_never_becomes_success(
    recipe: func.Function, monkeypatch: pytest.MonkeyPatch, retry_count: int,
) -> None:
    # Given a dependency that remains unavailable through the retry budget.
    monkeypatch.setenv("SIMULATED_FAILURES", "4")
    # When any attempt runs, including retry_count=max_retry_count.
    # Then terminal failure must escape just like a transient failure.
    with pytest.raises(ConnectionError):
        invoke(recipe, retry_count)


def test_terminal_failure_is_observable(
    recipe: func.Function, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture,
) -> None:
    # Given the last attempt still cannot complete the work.
    monkeypatch.setenv("SIMULATED_FAILURES", "4")
    # When the function fails on its fourth attempt.
    with caplog.at_level(logging.INFO), pytest.raises(ConnectionError):
        invoke(recipe, 3)
    # Then operators get failure metadata and a traceback, not success logging.
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.ERROR
    assert record.exc_info is not None
    assert record.__dict__["retry_count"] == 3
    assert record.__dict__["attempt"] == 4
    assert record.__dict__["terminal"] is True


def test_success_is_observable(recipe: func.Function, caplog: pytest.LogCaptureFixture) -> None:
    # Given the dependency has recovered.
    # When the function completes a retry successfully.
    with caplog.at_level(logging.INFO):
        invoke(recipe, 2)
    # Then there is one successful completion record without an exception.
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.INFO
    assert record.exc_info is None
    assert record.__dict__["attempt"] == 3


def test_real_sdk_indexes_timer_and_retry_policy(recipe: func.Function) -> None:
    # Given the complete documented Python v2 example.
    # When the SDK indexes its decorators.
    function = recipe
    # Then the timer binding and fixed-delay budget are attached to the function.
    trigger = function.get_trigger()
    assert trigger is not None
    assert trigger.type == "timerTrigger"
    assert function.get_settings_dict("retry_policy") == {
        "setting_name": "retry_policy", "strategy": "fixed_delay",
        "max_retry_count": "3", "delay_interval": "00:00:10",
    }
