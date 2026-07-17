---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-hubs
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# Event Hubs

Ingest high-throughput event streams with Event Hubs triggers and output bindings in PowerShell.

## Event Hub Trigger

`function.json`:

```json
{
  "bindings": [
    {
      "name": "Events",
      "type": "eventHubTrigger",
      "direction": "in",
      "eventHubName": "telemetry",
      "connection": "EventHubConnection",
      "cardinality": "many",
      "consumerGroup": "$Default"
    }
  ]
}
```

`run.ps1`:

```powershell
param($Events, $TriggerMetadata)

Write-Information "Received batch of $($Events.Count) event(s)"
foreach ($event in $Events) {
    Write-Information "Event body: $event"
}
```

With `cardinality` set to `many`, the trigger delivers events as an array for efficient batch processing. Use `one` only for low-volume debugging.

## Accessing Event Metadata

The `$TriggerMetadata` object exposes per-event system properties such as `PartitionContext`, `EnqueuedTimeUtc`, and `SequenceNumber`:

```powershell
Write-Information "Partition: $($TriggerMetadata.PartitionContext.PartitionId)"
```

## Output Binding

```json
{
  "name": "OutputEvent",
  "type": "eventHub",
  "direction": "out",
  "eventHubName": "processed",
  "connection": "EventHubConnection"
}
```

```powershell
Push-OutputBinding -Name OutputEvent -Value (@{ deviceId = "sensor-01"; value = 42 } | ConvertTo-Json)
```

!!! warning "Checkpoint and scaling"
    Event Hubs triggers checkpoint per partition. A slow function increases checkpoint lag and delays scaling. Keep per-event work minimal and offload heavy processing.

## See Also

- [Service Bus](service-bus.md)
- [Event Grid](event-grid.md)
- [Recipes Index](index.md)

## Sources

- [Event Hubs bindings (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-hubs)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
