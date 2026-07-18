---
validation:
  az_cli:
    last_tested:
    result: not_tested
  bicep:
    last_tested:
    result: not_tested
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-develop-local
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local
---
# 08 - Testing and Local Debugging (Flex Consumption)

Test your Python function logic in isolation, mock triggers and bindings, run local integration tests against Azurite, and attach a debugger with Azure Functions Core Tools.

## Prerequisites

| Tool | Minimum version | Purpose |
|---|---|---|
| Python | 3.11 | Run function code and tests |
| Azure Functions Core Tools | 4.x | Local host and debugging |
| pytest | 8.x | Unit and integration test runner |
| Azurite | 3.x | Local Azure Storage emulator |
| Visual Studio Code | Latest | Breakpoint debugging (optional) |

## What You'll Build

You will add a `tests/` suite to the Flex Consumption app that unit-tests HTTP handler logic, mocks a queue binding, runs an integration test against the Azurite storage emulator, and attaches the VS Code debugger to a running function host.

## 1. Unit Test the Function Logic

Keep business logic in plain functions so it can be tested without the Functions runtime. The trigger entry point should be a thin wrapper.

```python
# function_app.py
import azure.functions as func
from logic import build_greeting

app = func.FunctionApp()

@app.route(route="hello", auth_level=func.AuthLevel.FUNCTION)
def hello(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get("name") or "world"
    return func.HttpResponse(build_greeting(name), status_code=200)
```

```python
# logic.py
def build_greeting(name: str) -> str:
    return f"Hello, {name.strip().title()}!"
```

```python
# tests/test_logic.py
from logic import build_greeting

def test_build_greeting_titlecases():
    assert build_greeting("  ada lovelace ") == "Hello, Ada Lovelace!"
```

Run the tests:

```bash
pip install pytest azure-functions
python -m pytest -v
```

## 2. Mock Triggers and Bindings

Construct an `HttpRequest` directly to exercise the trigger without a running host.

```python
# tests/test_hello.py
import azure.functions as func
from function_app import hello

def test_hello_returns_greeting():
    req = func.HttpRequest(
        method="GET",
        url="/api/hello",
        params={"name": "grace"},
        body=b"",
    )
    resp = hello.build().get_user_function()(req)
    assert resp.status_code == 200
    assert resp.get_body() == b"Hello, Grace!"
```

!!! tip "Testing decorated functions"
    In the Python v2 model, `hello` is a `Function` object. Use `.build().get_user_function()` to reach the underlying callable, or refactor the body into `logic.py` and unit-test that directly.

## 3. Integration Test Against Azurite

Azurite emulates Blob, Queue, and Table storage locally so tests never touch a real account.

```bash
npm install -g azurite
azurite --silent --location ./.azurite &
```

Point `AzureWebJobsStorage` at the emulator in `local.settings.json`:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

```python
# tests/test_queue_integration.py
from azure.storage.queue import QueueClient

CONN = "UseDevelopmentStorage=true"

def test_queue_message_roundtrip():
    queue = QueueClient.from_connection_string(CONN, "work-items")
    queue.create_queue()
    queue.send_message("job-42")
    msg = queue.receive_message()
    assert msg.content == "job-42"
    queue.delete_queue()
```

## 4. Breakpoint Debugging with Core Tools

Start the host so it waits for a debugger and attach from VS Code.

```bash
func start --verbose
```

Add an attach configuration to `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Attach to Python Functions",
      "type": "debugpy",
      "request": "attach",
      "connect": { "host": "localhost", "port": 9091 }
    }
  ]
}
```

Set a breakpoint in `hello`, start the attach configuration, then call `http://localhost:7071/api/hello?name=ada`. Execution pauses at the breakpoint.

!!! info "Flex Consumption note"
    Testing and debugging happen entirely on your local machine and are identical across hosting plans. The Flex Consumption plan only affects how the app scales and networks once deployed — it does not change how you test.

## Verification

- [ ] `python -m pytest -v` reports all tests passing.
- [ ] The Azurite integration test creates, reads, and deletes a queue without a real storage account.
- [ ] A VS Code breakpoint in `hello` is hit when you invoke the local endpoint.

## Next Steps

- Wire these tests into your pipeline — see [06 - CI/CD](06-ci-cd.md).
- Extend coverage to the triggers you added in [07 - Extending with Triggers](07-extending-triggers.md).

## See Also

- [Testing recipe](../../recipes/testing.md) — Framework-agnostic testing patterns
- [Run functions locally](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local) — Core Tools reference
- [07 - Extending with Triggers](07-extending-triggers.md)

## Sources

- [Code and test Azure Functions locally (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-develop-local)
- [Azure Functions Python developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Use Azurite emulator for local Azure Storage development (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite)
</content>
</invoke>
