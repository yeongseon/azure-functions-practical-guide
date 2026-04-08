# HTTP Authentication

Apply API auth patterns for .NET isolated worker with function keys, Easy Auth, and token validation.

```mermaid
flowchart LR
    A[Trigger] --> B[Function]
    B --> C[Binding or SDK]
    C --> D[Azure service]
```

## Topic/Command Groups

### Function-level auth
```csharp
[Function("SecureEndpoint")]
public HttpResponseData SecureEndpoint(
    [HttpTrigger(AuthorizationLevel.Function, "get", Route = "secure")] HttpRequestData req)
{
    var response = req.CreateResponse(HttpStatusCode.OK);
    response.WriteString("authorized");
    return response;
}
```

### Enable app-level authentication
```bash
az webapp auth config-version upgrade --name "$APP_NAME" --resource-group "$RG"
az webapp auth update --name "$APP_NAME" --resource-group "$RG" --enabled true
```

### Validate JWT claims in code (ASP.NET Core integration)
```csharp
var principal = HttpContext.User;
```

### Validate JWT claims in code (basic isolated worker)
```csharp
using System.Text;
using System.Text.Json;

if (req.Headers.TryGetValues("x-ms-client-principal", out var values))
{
    var encoded = string.Join(string.Empty, values);
    if (!string.IsNullOrEmpty(encoded))
    {
        var json = Encoding.UTF8.GetString(Convert.FromBase64String(encoded));
        var principal = JsonSerializer.Deserialize<ClientPrincipal>(json);
    }
}
```

## See Also
- [Recipes Index](index.md)
- [.NET Language Guide](../index.md)
- [Troubleshooting](../troubleshooting.md)

## Sources
- [Azure Functions .NET isolated worker guide](https://learn.microsoft.com/azure/azure-functions/dotnet-isolated-process-guide)
- [Azure Functions triggers and bindings](https://learn.microsoft.com/azure/azure-functions/functions-triggers-bindings)
