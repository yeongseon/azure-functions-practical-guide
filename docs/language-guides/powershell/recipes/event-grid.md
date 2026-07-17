---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-grid
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# Event Grid

Handle discrete events from Azure services and custom topics with Event Grid triggers in PowerShell.

## Event Grid Trigger

`function.json`:

```json
{
  "bindings": [
    {
      "name": "EventGridEvent",
      "type": "eventGridTrigger",
      "direction": "in"
    }
  ]
}
```

`run.ps1`:

```powershell
param($EventGridEvent, $TriggerMetadata)

Write-Information "Event type: $($EventGridEvent.eventType)"
Write-Information "Subject: $($EventGridEvent.subject)"
Write-Information "Data: $($EventGridEvent.data | ConvertTo-Json -Compress)"
```

Event Grid delivers a single event per invocation. The runtime handles the subscription validation handshake automatically for the Event Grid schema.

## Routing by Event Type

```powershell
switch ($EventGridEvent.eventType) {
    "Microsoft.Storage.BlobCreated" {
        Write-Information "New blob: $($EventGridEvent.data.url)"
    }
    "Microsoft.Storage.BlobDeleted" {
        Write-Information "Blob removed: $($EventGridEvent.data.url)"
    }
    default {
        Write-Information "Unhandled event type"
    }
}
```

## Output Binding

Publish events to a custom topic:

```json
{
  "name": "OutputEvent",
  "type": "eventGrid",
  "direction": "out",
  "topicEndpointUri": "EventGridTopicEndpoint",
  "topicKeySetting": "EventGridTopicKey"
}
```

```powershell
Push-OutputBinding -Name OutputEvent -Value @{
    id        = [guid]::NewGuid().ToString()
    subject   = "orders/created"
    eventType = "Contoso.Order.Created"
    eventTime = (Get-Date).ToUniversalTime().ToString("o")
    data      = @{ orderId = 1234 }
}
```

!!! tip "Event Grid vs Event Hubs"
    Use Event Grid for reactive, discrete event handling and Event Hubs for high-throughput streaming. See [Event Hubs](event-hub.md).

## See Also

- [Event Hubs](event-hub.md)
- [Blob Storage](blob-storage.md)
- [Recipes Index](index.md)

## Sources

- [Event Grid bindings (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-grid)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
