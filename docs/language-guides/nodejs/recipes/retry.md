---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-error-pages
  diagrams:
    - id: architecture
      type: flowchart
      source: self-generated
      justification: Flow view of architecture, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-error-pages
---
# Retry Policies

Azure Functions runtime-enforced retry policies rerun a failed execution until it succeeds or the maximum retry count is reached. In the Node.js v4 model you set the policy in the trigger's `retry` option. Retry policies are only supported for a specific set of trigger types; other triggers rely on their own built-in retry behavior.

## Supported Triggers

Runtime retry policies apply only to these triggers:

| Trigger | Retry source |
|---|---|
| Timer | Retry policies |
| Event Hubs | Retry policies |
| Azure Cosmos DB | Retry policies |
| Kafka | Retry policies |

Queue Storage, Blob Storage, and Service Bus triggers do **not** use retry policies — they retry through their own binding extensions (poison-queue handling, `maxDeliveryCount`, dead-lettering). HTTP triggers have no automatic retry; the caller must retry.

## Architecture

<!-- diagram-id: architecture -->
```mermaid
flowchart TD
    EXEC[Function execution] --> ERR{Handler throws?}
    ERR -->|No| DONE[Success: checkpoint/commit]
    ERR -->|Yes| COUNT{retryCount < max?}
    COUNT -->|Yes| WAIT[Wait per strategy] --> EXEC
    COUNT -->|No| FAIL[Give up: execution fails]
```

## Fixed Delay

A fixed amount of time elapses between each retry.

```javascript
const { app } = require("@azure/functions");

app.timer("scheduledJob", {
    schedule: "0 */5 * * * *",
    retry: {
        strategy: "fixedDelay",
        delayInterval: { seconds: 10 },
        maxRetryCount: 4,
    },
    handler: (myTimer, context) => {
        if (context.retryContext?.retryCount < 2) {
            throw new Error("Retry!");
        }
        context.log("Timer function processed request.");
    },
});
```

## Exponential Backoff

The first retry waits the minimum interval; each subsequent retry adds time exponentially (with small randomization) up to the maximum interval.

```javascript
app.timer("scheduledJob", {
    schedule: "0 */5 * * * *",
    retry: {
        strategy: "exponentialBackoff",
        minimumInterval: { seconds: 10 },
        maximumInterval: { minutes: 15 },
        maxRetryCount: 5,
    },
    handler: (myTimer, context) => {
        throw new Error("Retry!");
    },
});
```

## Policy Properties

| Property | Description |
|---|---|
| `strategy` | Required. `fixedDelay` or `exponentialBackoff`. |
| `maxRetryCount` | Required. Max retries per execution. `-1` retries indefinitely. |
| `delayInterval` | Fixed-delay interval (duration object, e.g. `{ seconds: 10 }`). |
| `minimumInterval` | Exponential-backoff minimum delay. |
| `maximumInterval` | Exponential-backoff maximum delay. |

Read the current attempt from `context.retryContext.retryCount` to decide whether to keep throwing or handle the failure gracefully on the final attempt.

!!! warning "Max retry count is best-effort"
    The retry count is stored in instance memory. If the instance fails between retries, the count is lost — Event Hubs resumes on a new instance with the count reset, while Timer does not resume. Design your functions to be idempotent.

!!! note "Event Hubs checkpoint behavior"
    Event Hubs checkpoints are not written until the retry policy finishes, so progress on that partition is paused until the current batch completes.

## See Also

- [Event Hubs](event-hub.md)
- [Timer](timer.md)

## Sources

- [Azure Functions error handling and retry guidance (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-error-pages)
