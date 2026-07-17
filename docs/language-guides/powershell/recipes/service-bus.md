---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# Service Bus

Handle enterprise messaging with Service Bus queue and topic triggers in PowerShell.

## Queue Trigger

`function.json`:

```json
{
  "bindings": [
    {
      "name": "Message",
      "type": "serviceBusTrigger",
      "direction": "in",
      "queueName": "orders",
      "connection": "ServiceBusConnection"
    }
  ]
}
```

`run.ps1`:

```powershell
param($Message, $TriggerMetadata)

Write-Information "Received message id $($TriggerMetadata.MessageId)"
Write-Information "Delivery count: $($TriggerMetadata.DeliveryCount)"
```

## Topic and Subscription Trigger

```json
{
  "name": "Message",
  "type": "serviceBusTrigger",
  "direction": "in",
  "topicName": "events",
  "subscriptionName": "audit",
  "connection": "ServiceBusConnection"
}
```

## Output Binding

```json
{
  "name": "OutputMessage",
  "type": "serviceBus",
  "direction": "out",
  "queueName": "notifications",
  "connection": "ServiceBusConnection"
}
```

```powershell
Push-OutputBinding -Name OutputMessage -Value (@{ event = "order.created" } | ConvertTo-Json)
```

## Dead-Lettering

Messages that exceed max delivery count move to the dead-letter subqueue automatically. Monitor and reprocess it separately.

!!! tip "Identity-based connections"
    Prefer a `ServiceBusConnection__fullyQualifiedNamespace` app setting with a managed identity over a shared access key connection string. See [Managed Identity](managed-identity.md).

## See Also

- [Queue Storage](queue.md)
- [Managed Identity](managed-identity.md)
- [Recipes Index](index.md)

## Sources

- [Service Bus bindings (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
