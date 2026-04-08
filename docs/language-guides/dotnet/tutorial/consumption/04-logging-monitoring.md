# 04 - Logging and Monitoring (Consumption)

Enable baseline observability for the Consumption deployment with Application Insights, structured logs, and simple KQL validation.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| .NET SDK | 8.0 (LTS) | Build and run isolated worker functions |
| Azure Functions Core Tools | v4 | Local host and deployment commands |
| Azure CLI | 2.61+ | Provision and configure Azure resources |

!!! info "Plan basics"
    Consumption (Y1) scales to zero and charges per execution. It has a default 5-minute timeout and up to 10 minutes maximum per execution.
    No VNet integration on this plan.

## What You'll Build

Application Insights-backed monitoring for a Linux Consumption Function App, including a verified `Health` request and a KQL query that confirms request telemetry.

## Steps
### Step 1 - Create Application Insights
```bash
az monitor app-insights component create \
  --app "appi-dotnet-consumption-demo" \
  --resource-group "$RG" \
  --location "$LOCATION" \
  --application-type web
```

### Step 2 - Link Function App to telemetry
```bash
export APPINSIGHTS_CONNECTION_STRING=$(az monitor app-insights component show \
  --app "appi-dotnet-consumption-demo" \
  --resource-group "$RG" \
  --query "connectionString" \
  --output tsv)

az functionapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --settings "APPLICATIONINSIGHTS_CONNECTION_STRING=$APPINSIGHTS_CONNECTION_STRING"
```

### Step 3 - Register Application Insights in isolated worker
```bash
dotnet add package Microsoft.ApplicationInsights.WorkerService
dotnet add package Microsoft.Azure.Functions.Worker.ApplicationInsights
```

Update `Program.cs` to register Application Insights services:
```csharp
var host = new HostBuilder()
    .ConfigureFunctionsWebApplication()
    .ConfigureServices(services =>
    {
        services.AddApplicationInsightsTelemetryWorkerService();
        services.ConfigureFunctionsApplicationInsights();
    })
    .Build();

host.Run();
```

### Step 4 - Generate and inspect traces
```bash
curl "https://$APP_NAME.azurewebsites.net/api/health?code=$(az functionapp keys list --resource-group $RG --name $APP_NAME --query 'functionKeys.default' --output tsv)"

WORKSPACE_ID=$(az monitor app-insights component show \
  --app "appi-dotnet-consumption-demo" \
  --resource-group "$RG" \
  --query "workspaceResourceId" \
  --output tsv | xargs -I {} az monitor log-analytics workspace show --ids {} --query "customerId" --output tsv)

az monitor log-analytics query \
  --workspace "$WORKSPACE_ID" \
  --analytics-query "AppRequests | take 5 | project TimeGenerated, name, ResultCode, success" \
  --output table
```

### Step 5 - Use structured logs in code
```csharp
_logger.LogInformation("Order {OrderId} processed in {DurationMs} ms", orderId, durationMs);
_logger.LogWarning("Queue depth high: {QueueDepth}", queueDepth);
```

```mermaid
flowchart TD
    A[Function invocation] --> B[ILogger<T>]
    B --> C[Application Insights]
    C --> D[KQL query]
    D --> E[Operational decision]
```
### Step 6 - Validate isolated worker conventions
```bash
grep "FUNCTIONS_WORKER_RUNTIME" "local.settings.json"
grep "ConfigureFunctionsWebApplication" "Program.cs"
```

Confirm that HTTP functions use `HttpRequestData` and `HttpResponseData`, and that logging is constructor-injected with `ILogger<T>`.

## Verification
```text
{"status":"healthy"}

TimeGenerated                name            ResultCode    success
---------------------------  --------------  ----------    -------
2026-04-06T09:10:10.000000Z GET /api/health 200           True
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
