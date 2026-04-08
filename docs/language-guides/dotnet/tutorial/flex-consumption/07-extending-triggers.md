# 07 - Extending Triggers (Flex Consumption)

Extend the Flex Consumption app beyond HTTP by adding Queue, Blob, and Timer triggers using the .NET isolated worker model.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| .NET SDK | 8.0 (LTS) | Build and run isolated worker functions |
| Azure Functions Core Tools | v4 | Local host and deployment commands |
| Azure CLI | 2.61+ | Provision and configure Azure resources |

!!! info "Plan basics"
    Flex Consumption (FC1) scales to zero with per-function scaling, VNet support, and configurable memory. It is the recommended default for new serverless workloads.
    Supports VNet integration and private endpoints.
    No Kudu/SCM endpoints and no custom container support on this plan.
    All traffic routes through the integrated VNet.

## What You'll Build

- Queue, Blob, and Timer trigger support in a .NET isolated worker app
- Required trigger extension package references for the isolated model
- Trigger execution verification using Application Insights queries

## Steps
### Step 1 - Add required trigger extension packages
```bash
dotnet add package Microsoft.Azure.Functions.Worker.Extensions.Storage.Queues
dotnet add package Microsoft.Azure.Functions.Worker.Extensions.Storage.Blobs
dotnet add package Microsoft.Azure.Functions.Worker.Extensions.Timer
```

### Step 2 - Add queue trigger and queue output
```csharp
using Microsoft.Azure.Functions.Worker;

namespace MyProject.Functions;

public class QueueFunctions
{
    [Function("QueueProcessor")]
    [QueueOutput("processed-items", Connection = "AzureWebJobsStorage")]
    public string Process(
        [QueueTrigger("work-items", Connection = "AzureWebJobsStorage")] string message)
    {
        return $"processed: {message}";
    }
}
```

### Step 3 - Add blob and timer triggers
```csharp
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace MyProject.Functions;

public class TimerFunctions
{
    private readonly ILogger<TimerFunctions> _logger;

    public TimerFunctions(ILogger<TimerFunctions> logger)
    {
        _logger = logger;
    }

    [Function("BlobProcessor")]
    public void BlobProcessor(
        [BlobTrigger("uploads/{name}", Connection = "AzureWebJobsStorage")] byte[] content,
        string name)
    {
        _logger.LogInformation("Blob '{BlobName}' processed with {Length} bytes.", name, content.Length);
    }

    [Function("ScheduledCleanup")]
    public void ScheduledCleanup([TimerTrigger("0 */5 * * * *")] TimerInfo timer)
    {
        _logger.LogInformation("Timer fired at: {Timestamp}", DateTime.UtcNow);
    }
}
```

### Step 4 - Publish and send test events
```bash
dotnet publish --configuration Release --output ./publish
func azure functionapp publish "$APP_NAME"

az storage queue create \
  --name "work-items" \
  --account-name "$STORAGE_NAME" \
  --auth-mode login
az storage message put \
  --queue-name "work-items" \
  --content '{"id":"1001","action":"reindex"}' \
  --account-name "$STORAGE_NAME" \
  --auth-mode login
```

### Step 5 - Review trigger execution
```bash
az monitor app-insights query \
  --app "appi-dotnet-flex-consumption-demo" \
  --resource-group "$RG" \
  --analytics-query "traces | where message has_any ('QueueProcessor','ScheduledCleanup') | take 20" \
  --output table
```

`az functionapp log tail` is not a reliable primary signal on Flex Consumption because Kudu/SCM streaming behavior differs from Premium and Dedicated plans.

```mermaid
flowchart TD
    A[Queue message] --> B[QueueTrigger]
    B --> C[QueueOutput]
    D[Blob upload] --> E[BlobTrigger]
    F[Cron schedule] --> G[TimerTrigger]
```
### Step X - Validate isolated worker conventions
```bash
grep "FUNCTIONS_WORKER_RUNTIME" "local.settings.json"
grep "ConfigureFunctionsWebApplication" "Program.cs"
```

Confirm that HTTP functions use `HttpRequestData` and `HttpResponseData`, and that logging is constructor-injected with `ILogger<T>`.

## Verification
```text
Timestamp                    Message
---------------------------  ------------------------------------------
2026-04-06T10:00:00.000000Z  Executing 'Functions.QueueProcessor'
2026-04-06T10:00:01.000000Z  Executed 'Functions.QueueProcessor' (Succeeded)
2026-04-06T10:05:00.000000Z  Executing 'Functions.ScheduledCleanup'
2026-04-06T10:05:01.000000Z  Executed 'Functions.ScheduledCleanup' (Succeeded)
```

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
