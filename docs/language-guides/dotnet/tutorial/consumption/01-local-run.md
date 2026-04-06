# 01 - Run Locally (Consumption)

Build and run a .NET isolated worker Function App locally before touching Azure resources. This creates predictable deployment behavior later in the track.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| .NET SDK | 8.0 (LTS) | Build and run isolated worker functions |
| Azure Functions Core Tools | v4 | Local host and deployment commands |
| Azure CLI | 2.61+ | Provision and configure Azure resources |
| Azurite | latest | Local storage emulator for `UseDevelopmentStorage=true` |

!!! info "Plan basics"
    Consumption (Y1) scales to zero and charges per execution. It has a default 5-minute timeout and up to 10 minutes maximum per execution.
    No VNet integration on this plan.

## What You'll Build

A .NET isolated worker HTTP-triggered function named `Health` that runs locally, returns JSON from `/api/health`, and validates the isolated hosting model before deployment.

## Steps
### Step 1 - Initialize a .NET isolated project
```bash
func init MyProject --worker-runtime dotnet-isolated
cd MyProject
func new --template "HTTP trigger" --name Health --authlevel function
```

### Step 2 - Use a production-aligned project structure
```text
project-root/
├── Functions/
│   ├── HealthFunction.cs
│   ├── TimerFunctions.cs
│   └── QueueFunctions.cs
├── Program.cs
├── host.json
├── local.settings.json
└── MyProject.csproj
```

### Step 3 - Configure Program.cs for isolated hosting
```csharp
using Microsoft.Extensions.Hosting;

var host = new HostBuilder()
    .ConfigureFunctionsWebApplication()
    .Build();

host.Run();
```

### Step 4 - Implement the HTTP function with DI logger
```csharp
using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Http;
using Microsoft.Extensions.Logging;
using System.Net;

namespace MyProject.Functions;

public class HealthFunction
{
    private readonly ILogger<HealthFunction> _logger;

    public HealthFunction(ILogger<HealthFunction> logger)
    {
        _logger = logger;
    }

    [Function("Health")]
    public HttpResponseData Run(
        [HttpTrigger(AuthorizationLevel.Function, "get", "post", Route = "health")] HttpRequestData req)
    {
        _logger.LogInformation("Health check executed.");
        var response = req.CreateResponse(HttpStatusCode.OK);
        response.WriteString("{\"status\":\"healthy\"}");
        return response;
    }
}
```

### Step 5 - Configure local settings and start the host

!!! tip "Azurite for local storage"
    The `UseDevelopmentStorage=true` setting requires [Azurite](https://learn.microsoft.com/azure/storage/common/storage-use-azurite) running locally. For HTTP-only functions, you can also set `AzureWebJobsStorage` to an empty string `""` to skip the storage requirement during development.
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "dotnet-isolated"
  }
}
```

```bash
dotnet build
func start
```

In a second terminal, test the endpoint:

```bash
curl --request GET "http://localhost:7071/api/health"
```

```mermaid
flowchart LR
    A[dotnet build] --> B[func start]
    B --> C[HTTP Trigger endpoint]
    C --> D[HttpRequestData]
    D --> E[HttpResponseData]
```
### Step 6 - Validate isolated worker conventions

Confirm that your `local.settings.json` contains `"FUNCTIONS_WORKER_RUNTIME": "dotnet-isolated"` and that `Program.cs` uses `ConfigureFunctionsWebApplication()`.

Verify that HTTP functions use `HttpRequestData` and `HttpResponseData`, and that logging is constructor-injected with `ILogger<T>`.

## Verification
```text
Azure Functions Core Tools
Core Tools Version:       4.x.x
Function Runtime Version: 4.x.x.x

Functions:
    Health: [GET,POST] http://localhost:7071/api/health
```

Confirm that Core Tools lists `Health: [GET,POST] http://localhost:7071/api/health`, then run `curl --request GET "http://localhost:7071/api/health"` and verify a JSON response `{"status":"healthy"}`.
## Next Steps

> **Next:** [02 - First Deploy](02-first-deploy.md)

## See Also
- [Tutorial Overview & Plan Chooser](../index.md)
- [.NET Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources
- [Azure Functions .NET isolated worker guide](https://learn.microsoft.com/azure/azure-functions/dotnet-isolated-process-guide)
- [Develop Azure Functions locally with Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-develop-local)
- [Azure Functions hosting options](https://learn.microsoft.com/azure/azure-functions/functions-scale)
