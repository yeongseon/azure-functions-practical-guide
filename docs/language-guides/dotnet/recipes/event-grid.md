---
content_sources:
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/dotnet-isolated-process-guide
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-triggers-bindings
---

# Event Grid

Subscribe to Event Grid events and route them into isolated worker handlers.

<!-- diagram-id: event-grid -->
```mermaid
flowchart TD
    A[Trigger] --> B[Function]
    B --> C[Binding or SDK]
    C --> D[Azure service]
```

## Topic/Command Groups

### Event Grid trigger
```csharp
[Function("BlobCreatedEvent")]
public void BlobCreatedEvent([EventGridTrigger] BinaryData eventData)
{
}
```

### Subscription setup
```bash
az eventgrid event-subscription create   --name "sub-func-events"   --source-resource-id "<source-resource-id>"   --endpoint-type azurefunction   --endpoint "/subscriptions/<subscription-id>/resourceGroups/$RG/providers/Microsoft.Web/sites/$APP_NAME/functions/BlobCreatedEvent"
```

## See Also
- [Recipes Index](index.md)
- [.NET Language Guide](../index.md)
- [Troubleshooting](../troubleshooting.md)

## Sources
- [Azure Functions .NET isolated worker guide](https://learn.microsoft.com/azure/azure-functions/dotnet-isolated-process-guide)
- [Azure Functions triggers and bindings](https://learn.microsoft.com/azure/azure-functions/functions-triggers-bindings)
