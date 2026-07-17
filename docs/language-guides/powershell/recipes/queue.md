---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# Queue Storage

Consume and produce Azure Storage queue messages in PowerShell.

## Queue Trigger

`function.json`:

```json
{
  "bindings": [
    {
      "name": "QueueItem",
      "type": "queueTrigger",
      "direction": "in",
      "queueName": "work-items",
      "connection": "AzureWebJobsStorage"
    }
  ]
}
```

`run.ps1`:

```powershell
param($QueueItem, $TriggerMetadata)

# JSON messages are deserialized automatically into a Hashtable/PSObject
Write-Information "Processing item $($QueueItem.id)"

Write-Information "Dequeue count: $($TriggerMetadata.DequeueCount)"
```

## Output Queue Binding

Emit messages to another queue:

```json
{
  "name": "OutputQueue",
  "type": "queue",
  "direction": "out",
  "queueName": "results",
  "connection": "AzureWebJobsStorage"
}
```

```powershell
Push-OutputBinding -Name OutputQueue -Value (@{ id = $QueueItem.id; status = "done" } | ConvertTo-Json)
```

## Poison Messages

After the runtime exhausts retries (default 5 dequeues), the message moves to `<queueName>-poison`. Add a trigger on that queue to handle failures:

```powershell
param($QueueItem, $TriggerMetadata)
Write-Error "Poison message received: $($QueueItem | ConvertTo-Json)"
```

!!! tip "Idempotency"
    A message can be delivered more than once. Make handlers idempotent — key writes on a stable message id.

## See Also

- [Blob Storage](blob-storage.md)
- [Service Bus](service-bus.md)
- [Recipes Index](index.md)

## Sources

- [Queue storage bindings (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
