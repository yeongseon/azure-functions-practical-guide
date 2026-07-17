---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-error-pages
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# Retries and Error Handling

Recover from transient failures with retry policies and defensive error handling in PowerShell.

## Retry Policies

Configure a retry policy in `host.json`. It applies to trigger types that support it (such as Timer, Event Hubs, and Service Bus). The policy re-runs the whole function on an unhandled exception.

`host.json`:

```json
{
  "version": "2.0",
  "retry": {
    "strategy": "exponentialBackoff",
    "maxRetryCount": 5,
    "minimumInterval": "00:00:02",
    "maximumInterval": "00:01:00"
  }
}
```

Use `"strategy": "fixedDelay"` with a `"delayInterval"` for a constant wait instead of exponential backoff.

!!! warning "Retry support varies by trigger"
    Built-in retry policies do not apply to every trigger. HTTP triggers, for example, do not retry. Check the binding documentation and, where the source supports it (Service Bus, Queue), rely on the platform's native delivery-count and dead-letter behavior.

## Handling Errors in Code

Wrap fallible work in `try/catch` and throw to signal failure so the retry policy or platform dead-lettering engages:

```powershell
param($Message, $TriggerMetadata)

try {
    Invoke-RestMethod -Uri $env:DownstreamApi -Method Post -Body $Message -ErrorAction Stop
}
catch {
    Write-Error "Downstream call failed: $($_.Exception.Message)"
    throw
}
```

Set `-ErrorAction Stop` on cmdlets so non-terminating errors become catchable terminating errors.

## Idempotency

Because a function may run more than once, make handlers idempotent — use a natural key or a processed-message table so reprocessing the same message is safe.

!!! tip "Poison messages"
    For Queue and Service Bus triggers, messages that keep failing move to a poison queue or dead-letter subqueue after the max delivery count. Monitor and reprocess these separately.

## See Also

- [Service Bus](service-bus.md)
- [Queue Storage](queue.md)
- [Recipes Index](index.md)

## Sources

- [Azure Functions error handling and retries (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-error-pages)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
