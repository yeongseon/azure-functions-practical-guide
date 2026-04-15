---
content_sources:
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/dotnet-isolated-process-guide
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-triggers-bindings
---

# Durable Orchestration

Coordinate long-running workflows with Durable Functions in .NET isolated worker.

<!-- diagram-id: durable-orchestration -->
```mermaid
flowchart TD
    A[Trigger] --> B[Function]
    B --> C[Binding or SDK]
    C --> D[Azure service]
```

## Topic/Command Groups

### Orchestrator skeleton
```csharp
[Function("OrderOrchestrator")]
public async Task<string> RunOrchestrator(
    [OrchestrationTrigger] TaskOrchestrationContext context)
{
    var id = context.GetInput<string>();
    await context.CallActivityAsync("ReserveInventory", id);
    await context.CallActivityAsync("ChargePayment", id);
    return "completed";
}
```

### HTTP starter
```csharp
[Function("StartOrder")]
public async Task<HttpResponseData> StartOrder(
    [HttpTrigger(AuthorizationLevel.Function, "post", Route = "orders/start")] HttpRequestData req,
    [DurableClient] DurableTaskClient client)
{
    string instanceId = await client.ScheduleNewOrchestrationInstanceAsync("OrderOrchestrator");
    return await client.CreateCheckStatusResponseAsync(req, instanceId);
}
```

## See Also
- [Recipes Index](index.md)
- [.NET Language Guide](../index.md)
- [Troubleshooting](../troubleshooting.md)

## Sources
- [Azure Functions .NET isolated worker guide](https://learn.microsoft.com/azure/azure-functions/dotnet-isolated-process-guide)
- [Azure Functions triggers and bindings](https://learn.microsoft.com/azure/azure-functions/functions-triggers-bindings)
