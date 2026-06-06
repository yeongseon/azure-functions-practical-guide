---
content_sources:

- type: mslearn-adapted
  url: https://learn.microsoft.com/azure/azure-functions/dotnet-isolated-process-guide
- type: mslearn-adapted
  url: https://learn.microsoft.com/azure/azure-functions/functions-triggers-bindings
content_validation:
  status: verified
  last_reviewed: '2026-05-23'
  reviewer: agent
  core_claims:
  - claim: This page uses Microsoft Learn as the primary source basis for its Azure-specific
      guidance.
    source: https://learn.microsoft.com/azure/azure-functions/dotnet-isolated-process-guide
    verified: true
---
# HTTP API Patterns

Build robust HTTP APIs with `HttpRequestData` and `HttpResponseData` in .NET isolated worker.

<!-- diagram-id: http-api-patterns -->
```mermaid
flowchart TD
    A[Trigger] --> B[Function]
    B --> C[Binding or SDK]
    C --> D[Azure service]
```

## Topic/Command Groups

### Route templates and verbs
```csharp
[Function("GetOrder")]
public async Task<HttpResponseData> GetOrder(
    [HttpTrigger(AuthorizationLevel.Function, "get", Route = "orders/{id}")] HttpRequestData req,
    string id)
{
    var response = req.CreateResponse(HttpStatusCode.OK);
    await response.WriteAsJsonAsync(new { id });
    return response;
}
```

### Request body handling
```csharp
using System.Text.Json;

var payload = await JsonSerializer.DeserializeAsync<CreateOrderRequest>(req.Body);
```

### Response envelope pattern
```csharp
var response = req.CreateResponse(HttpStatusCode.Created);
await response.WriteAsJsonAsync(new { orderId = "ord-1001", status = "created" });
return response;
```

## Review Matrix

| Review area | Page-specific check |
|---|---|
| Scope | Confirm the guidance applies to HTTP API Patterns. |
| Source basis | Validate the recommendation against the Microsoft Learn sources in this page. |
| Evidence | Capture command output, portal state, metrics, logs, or screenshots before treating the result as proven. |

## See Also
- [Recipes Index](index.md)
- [.NET Language Guide](../index.md)
- [Troubleshooting](../troubleshooting.md)

## Sources
- [Azure Functions .NET isolated worker guide](https://learn.microsoft.com/azure/azure-functions/dotnet-isolated-process-guide)
- [Azure Functions triggers and bindings](https://learn.microsoft.com/azure/azure-functions/functions-triggers-bindings)
