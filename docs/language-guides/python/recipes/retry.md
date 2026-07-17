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

Azure Functions runtime-enforced retry policies rerun a failed execution until it succeeds or the maximum retry count is reached. In the Python v2 model you attach a policy with the `@app.retry` decorator. Retry policies are only supported for a specific set of trigger types; other triggers rely on their own built-in retry behavior.

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
    EXEC[Function execution] --> ERR{Uncaught exception?}
    ERR -->|No| DONE[Success: checkpoint/commit]
    ERR -->|Yes| COUNT{retry_count < max?}
    COUNT -->|Yes| WAIT[Wait per strategy] --> EXEC
    COUNT -->|No| FAIL[Give up: execution fails]
```

## Fixed Delay

A fixed amount of time elapses between each retry.

```python
import azure.functions as func

app = func.FunctionApp()


@app.timer_trigger(schedule="0 */5 * * * *", arg_name="mytimer",
                   run_on_startup=False, use_monitor=False)
@app.retry(strategy="fixed_delay", max_retry_count="3",
           delay_interval="00:00:10")
def scheduled_job(mytimer: func.TimerRequest, context: func.Context) -> None:
    if context.retry_context.retry_count == context.retry_context.max_retry_count:
        # Final attempt failed — log and stop retrying.
        return
    raise Exception("This is a retryable exception")
```

## Exponential Backoff

The first retry waits the minimum interval; each subsequent retry adds time exponentially (with small randomization) up to the maximum interval.

```python
@app.timer_trigger(schedule="0 */5 * * * *", arg_name="mytimer",
                   run_on_startup=False, use_monitor=False)
@app.retry(strategy="exponential_backoff", max_retry_count="5",
           minimum_interval="00:00:10", maximum_interval="00:15:00")
def scheduled_job(mytimer: func.TimerRequest, context: func.Context) -> None:
    raise Exception("This is a retryable exception")
```

## Policy Properties

| Property | Description |
|---|---|
| `strategy` | Required. `fixed_delay` or `exponential_backoff`. |
| `max_retry_count` | Required. Max retries per execution. `-1` retries indefinitely. |
| `delay_interval` | Fixed-delay interval, format `HH:mm:ss`. |
| `minimum_interval` | Exponential-backoff minimum delay, format `HH:mm:ss`. |
| `maximum_interval` | Exponential-backoff maximum delay, format `HH:mm:ss`. |

!!! warning "Max retry count is best-effort"
    The retry count is stored in instance memory. If the instance fails between retries, the count is lost — Event Hubs resumes on a new instance with the count reset, while Timer does not resume. Design your functions to be idempotent.

!!! note "Event Hubs checkpoint behavior"
    Event Hubs checkpoints are not written until the retry policy finishes, so progress on that partition is paused until the current batch completes.

## See Also

- [Event Hubs](event-hub.md)
- [Timer Trigger](timer.md)

## Sources

- [Azure Functions error handling and retry guidance (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-error-pages)
