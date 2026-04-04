# .NET Language Guide

This guide introduces Azure Functions for .NET with emphasis on the **isolated worker model**, which is the recommended default for new projects.

The isolated model gives clearer dependency boundaries, independent .NET versioning, and modern hosting patterns aligned with current platform direction.

## Official reference

- [Azure Functions .NET class library guide (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-dotnet-class-library)

!!! note "Recommendation baseline"
    For new apps, prefer the isolated worker model unless you have a specific compatibility dependency on in-process behavior.

## .NET worker model overview

| Model | Status for new projects | Characteristics |
|-------|--------------------------|-----------------|
| In-process | Legacy/compatibility path | Functions runtime and app code run in one process |
| Isolated worker | **Recommended** | App code runs in separate worker process with explicit host setup |

## Runtime support baseline

- **.NET 8 (LTS)** is the hub baseline for new .NET guidance; validate target framework and extension compatibility in Microsoft Learn before production rollouts.

## Key concepts

- Attribute-based trigger and binding declarations.
- Dependency injection via modern host builder patterns.
- Separation between Functions host process and isolated worker process.

## In-process vs isolated: practical differences

| Concern | In-process | Isolated |
|---------|------------|----------|
| Process boundary | Shared with Functions runtime | Separate worker process |
| Startup model | Runtime-managed startup hooks | Standard .NET host builder style |
| Middleware/control | More constrained | More explicit/extensible pipeline control |
| Recommended for net-new | No | Yes |

## Quick start: HTTP trigger (.NET isolated)

```csharp
using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Http;
using Microsoft.Extensions.Logging;
using System.Net;

public class HelloFunction
{
    private readonly ILogger _logger;

    public HelloFunction(ILoggerFactory loggerFactory)
    {
        _logger = loggerFactory.CreateLogger<HelloFunction>();
    }

    [Function("HelloHttp")]
    public HttpResponseData Run(
        [HttpTrigger(AuthorizationLevel.Function, "get", Route = "hello/{name?}")] HttpRequestData req,
        string? name)
    {
        name ??= "world";
        _logger.LogInformation("Processed .NET isolated request for {Name}", name);

        HttpResponseData response = req.CreateResponse(HttpStatusCode.OK);
        response.WriteString($"Hello, {name}! (Azure Functions .NET isolated)");
        return response;
    }
}
```

### What this example demonstrates

- `[Function]` method registration.
- `[HttpTrigger]` attribute with route and auth level.
- DI-driven logging in isolated worker.
- `HttpRequestData`/`HttpResponseData` primitives.

## Planned content (Coming Soon)

- **Tutorial track**: local development, first deploy, configuration, monitoring, IaC, CI/CD.
- **Recipes**: Storage, Cosmos DB, Key Vault, Managed Identity, durable workflows.
- **Reference app**: `apps/dotnet/` parity implementation aligned to Python capability set.

!!! tip "Use shared sections while .NET track expands"
    Combine this page with [Platform](../../platform/index.md), [Operations](../../operations/index.md), and [Troubleshooting](../../troubleshooting/index.md) for production-ready guidance today.

## Cross-language links

- [Language Guides overview](../index.md)
- [Python guide](../python/index.md)
- [Node.js guide](../nodejs/index.md)
- [Java guide](../java/index.md)

## See Also

- [Platform: Architecture](../../platform/architecture.md)
- [Platform: Reliability](../../platform/reliability.md)
- [Operations: Deployment](../../operations/deployment.md)
- [Operations: Monitoring](../../operations/monitoring.md)
