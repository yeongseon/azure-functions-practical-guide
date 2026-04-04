# Retries and Poison Handling

This guide explains retry execution and poison/dead-letter handling for Azure Functions event-driven workloads.
Use these patterns to protect reliability under transient failures and malformed messages.

!!! tip "Platform Guide"
    For scaling architecture and plan comparison, see [Scaling](../platform/scaling.md).

!!! tip "Language Guide"
    For Python deployment specifics, see the [Python Tutorial](../language-guides/python/tutorial/index.md).

## Reliability model

Azure Functions reliability for triggers is a combination of:

1. Trigger-level delivery semantics.
2. Runtime retry policy behavior.
3. Message destination after retry exhaustion (poison queue or dead-letter).

Design for idempotency first, then tune retries.

## Built-in retry support

Azure Functions supports retry behavior for selected triggers.
Common trigger categories with retry support include:

- Azure Storage Queue trigger.
- Azure Service Bus trigger.
- Azure Event Hubs trigger.

Configure retry behavior according to binding/runtime model for your language and extension.

## `host.json` and trigger extension settings

Some retry and poison behavior is controlled in `host.json` extension sections.

Example storage queue extension settings:

```json
{
  "version": "2.0",
  "extensions": {
    "queues": {
      "maxDequeueCount": 5,
      "visibilityTimeout": "00:00:30",
      "batchSize": 16,
      "newBatchThreshold": 8
    }
  }
}
```

`maxDequeueCount` determines when a message is treated as poison for Storage Queue trigger processing.

## Poison queue behavior (Storage Queue)

For Storage Queue triggers, messages that exceed `maxDequeueCount` are moved to a poison queue.

Operational pattern:

- Main queue: `orders`.
- Poison queue: `orders-poison`.
- Build a dedicated poison-message processor for triage and replay.

This prevents infinite reprocessing loops and preserves failed payloads for investigation.

## Dead-letter behavior (Service Bus)

Service Bus uses dead-lettering semantics.
Messages can be moved to the dead-letter subqueue after max delivery attempts or explicit dead-letter action.

Operational responsibilities:

- Monitor dead-letter message count.
- Capture reason and error metadata.
- Provide controlled replay tools or manual remediation workflow.

## Retry strategy design

Use layered retry design:

1. **Trigger/runtime retries** for transient infrastructure issues.
2. **Application-level retries** for outbound dependencies when safe.
3. **Circuit breaker/timeouts** to avoid cascading failure.

Keep overall retry budget bounded to avoid queue starvation.

## Custom retry in function code

Language-level retry libraries can be used around dependency calls.

Examples:

- .NET: Polly policies (retry with jittered backoff).
- Python: retry decorator pattern.
- Node.js: policy-based retry utilities.

!!! warning "Do not duplicate retries blindly"
    If trigger-level retries are already active, excessive in-code retries can amplify latency and cost.

## Idempotency requirements

Because retries and at-least-once delivery are common, handlers should be idempotent:

- Use deterministic operation keys.
- Record processed message identifiers where required.
- Make writes safe for duplicate delivery.

Without idempotency, retries can create duplicate side effects.

## Monitoring retry and poison health

Track these operational signals:

- Retry attempt trend by function.
- Poison queue message count growth.
- Dead-letter count and age.
- Processing lag between enqueue and completion.

Use alerts when poison/dead-letter counts grow continuously.

## Operational triage workflow

1. Inspect message payload and metadata.
2. Classify failure type (transient, schema, business rule, dependency outage).
3. Fix root cause.
4. Replay safely from poison/dead-letter store.
5. Verify no duplicate side effects.

## See Also

- [Monitoring](monitoring.md)
- [Alerts](alerts.md)
- [Platform Reliability](../platform/reliability.md)

## Sources

- [Azure Functions error handling and retries](https://learn.microsoft.com/azure/azure-functions/functions-bindings-error-pages)
- [Azure Queue Storage trigger for Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-bindings-storage-queue-trigger)
- [Azure Service Bus trigger for Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-bindings-service-bus-trigger)
- [Azure Event Hubs trigger for Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-bindings-event-hubs-trigger)
