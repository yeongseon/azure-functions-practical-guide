"""Local SDK contract for the automatic-completion example, not broker evidence.

Run: uv run --with pytest --with azure-functions pytest tests/test_service_bus_settlement.py
"""

import json
import re
from pathlib import Path
from types import ModuleType
from typing import Final

import azure.functions as func
import pytest

PAGE: Final = (
    Path(__file__).resolve().parents[1]
    / "docs/operations/retries-and-poison-handling.md"
)


@pytest.fixture
def automatic_function() -> func.Function:
    """Index the actual Markdown example with the real Python Functions SDK."""
    section = PAGE.read_text().split("<!-- service-bus-automatic-example -->", 1)[1]
    source = re.findall(r"```python\n(.*?)```", section, re.DOTALL)[0]
    module = ModuleType("service_bus_automatic_example")
    exec(compile(source, str(PAGE), "exec"), module.__dict__)  # noqa: S102 -- trusted repository snippet
    app = module.__dict__["app"]
    return app.get_functions()[0]


def test_success_returns_after_processing(automatic_function: func.Function) -> None:
    # Given a valid synthetic order and the documented automatic handler.
    message = func.ServiceBusMessage(body=b'{"orderId":"order-001"}')
    # When the SDK user function processes it (no host or broker involved).
    result = automatic_function.get_user_function()(message)
    # Then completed work returns normally, making it eligible for auto-completion.
    assert result is None


def test_malformed_message_propagates(automatic_function: func.Function) -> None:
    # Given malformed JSON rather than a processable order.
    message = func.ServiceBusMessage(body=b"not-json")
    # When processing fails, then the exception escapes instead of reporting success.
    with pytest.raises(json.JSONDecodeError):
        automatic_function.get_user_function()(message)


def test_binding_is_single_message_service_bus(automatic_function: func.Function) -> None:
    # Given the function indexed by the real SDK.
    # When generated trigger metadata is inspected.
    binding = automatic_function.get_bindings_dict()["bindings"][0]
    # Then the intended queue, connection setting and single-message binding are used.
    assert binding["type"] == "serviceBusTrigger"
    assert binding["queueName"] == "orders"
    assert binding["connection"] == "ServiceBusConnection"
    assert binding.get("cardinality", "one") == "one"


def test_host_retains_automatic_completion() -> None:
    # Given the documented host.json blocks.
    examples = re.findall(r"```json\n(.*?)```", PAGE.read_text(), re.DOTALL)
    # When the Service Bus configuration is parsed.
    settings = next(
        json.loads(source)["extensions"]["serviceBus"]
        for source in examples
        if "serviceBus" in json.loads(source).get("extensions", {})
    )
    # Then automatic completion is enabled; transport retries are a separate setting.
    assert settings["autoCompleteMessages"] is True
    assert settings["clientRetryOptions"]["maxRetries"] == 5
