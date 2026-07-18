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
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-node
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local
---
# 08 - Testing and Local Debugging (Flex Consumption)

Test your Node.js v4 handlers in isolation, mock the invocation context and bindings, run local integration tests against Azurite, and attach the Node inspector for breakpoint debugging.

## Prerequisites

| Tool | Minimum version | Purpose |
|---|---|---|
| Node.js | 20 LTS | Run function code and tests |
| Azure Functions Core Tools | 4.x | Local host and debugging |
| Jest or Vitest | Latest | Test runner |
| Azurite | 3.x | Local Azure Storage emulator |
| Visual Studio Code | Latest | Breakpoint debugging (optional) |

## What You'll Build

You will add a test suite to the Flex Consumption app that unit-tests an HTTP handler, mocks the `InvocationContext`, runs an integration test against Azurite, and attaches the Node inspector to a running host.

## 1. Unit Test the Handler

In the v4 model a handler is a plain async function, so it tests cleanly. Keep logic separate from the trigger registration.

```javascript
// src/logic.js
export function buildGreeting(name) {
  return `Hello, ${(name ?? "world").trim()}!`;
}
```

```javascript
// src/functions/hello.js
import { app } from "@azure/functions";
import { buildGreeting } from "../logic.js";

export async function hello(request, context) {
  const name = request.query.get("name");
  return { status: 200, body: buildGreeting(name) };
}

app.http("hello", { methods: ["GET"], authLevel: "function", handler: hello });
```

```javascript
// test/logic.test.js
import { buildGreeting } from "../src/logic.js";

test("buildGreeting trims and formats", () => {
  expect(buildGreeting("  ada ")).toBe("Hello, ada!");
});
```

```bash
npm install --save-dev jest
npx jest
```

## 2. Mock the Invocation Context and Request

Build lightweight fakes for `HttpRequest` and `InvocationContext` to exercise the handler directly.

```javascript
// test/hello.test.js
import { hello } from "../src/functions/hello.js";

function fakeRequest(query = {}) {
  return { query: new Map(Object.entries(query)) };
}

function fakeContext() {
  return { log: () => {}, error: () => {}, invocationId: "test-1" };
}

test("hello returns a greeting", async () => {
  const res = await hello(fakeRequest({ name: "grace" }), fakeContext());
  expect(res.status).toBe(200);
  expect(res.body).toBe("Hello, grace!");
});
```

!!! tip "Keep the handler exportable"
    Export the handler function separately from the `app.http(...)` registration so tests can import it without booting the Functions host.

## 3. Integration Test Against Azurite

Azurite emulates Blob, Queue, and Table storage locally.

```bash
npm install -g azurite
azurite --silent --location ./.azurite &
```

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "node"
  }
}
```

```javascript
// test/queue.integration.test.js
import { QueueServiceClient } from "@azure/storage-queue";

const CONN = "UseDevelopmentStorage=true";

test("queue roundtrip against Azurite", async () => {
  const svc = QueueServiceClient.fromConnectionString(CONN);
  const queue = svc.getQueueClient("work-items");
  await queue.createIfNotExists();
  await queue.sendMessage(Buffer.from("job-42").toString("base64"));
  const msgs = await queue.receiveMessages();
  expect(Buffer.from(msgs.receivedMessageItems[0].messageText, "base64").toString()).toBe("job-42");
  await queue.deleteIfExists();
});
```

## 4. Breakpoint Debugging with the Node Inspector

Start the host with the inspector enabled:

```bash
func start --node-inspect
```

Attach from VS Code with `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Attach to Node Functions",
      "type": "node",
      "request": "attach",
      "port": 9229
    }
  ]
}
```

Set a breakpoint in `hello`, attach, then call `http://localhost:7071/api/hello?name=ada`.

!!! info "Flex Consumption note"
    Testing and debugging run entirely on your local machine and are identical across hosting plans. The Flex Consumption plan changes only how the deployed app scales and networks.

## Verification

- [ ] `npx jest` reports all tests passing.
- [ ] The Azurite integration test round-trips a queue message without a real storage account.
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
- [Azure Functions Node.js developer guide (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-node)
- [Use Azurite emulator for local Azure Storage development (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite)
</content>
