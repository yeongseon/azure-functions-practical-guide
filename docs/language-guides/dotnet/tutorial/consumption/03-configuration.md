# 03 - Configuration (Consumption)

Configure runtime and app settings for Consumption using explicit app settings, host-level options, and safe environment separation.

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

Production-safe host configuration for a Linux Consumption Function App, including runtime settings, environment designation, and verification through deployed app settings.

## Steps
### Step 1 - Set baseline runtime settings
```bash
az functionapp config appsettings set   --name "$APP_NAME"   --resource-group "$RG"   --settings     "FUNCTIONS_WORKER_RUNTIME=dotnet-isolated"     "FUNCTIONS_EXTENSION_VERSION=~4"     "AZURE_FUNCTIONS_ENVIRONMENT=Production"     "APP_ENV=production"
```

### Step 2 - Configure worker and feature settings
```bash
az functionapp config appsettings set   --name "$APP_NAME"   --resource-group "$RG"   --settings     "WEBSITE_RUN_FROM_PACKAGE=1"     "AzureWebJobsStorage=DefaultEndpointsProtocol=https;AccountName=$STORAGE_NAME;AccountKey=<masked-key>;EndpointSuffix=core.windows.net"
```

### Step 3 - Update host.json for routing and timeout
```json
{
  "version": "2.0",
  "functionTimeout": "00:10:00",
  "extensions": {
    "http": {
      "routePrefix": "api"
    }
  }
}
```

### Step 4 - Confirm effective settings
```bash
az functionapp config appsettings list   --name "$APP_NAME"   --resource-group "$RG"   --output table
```

```mermaid
flowchart LR
    A[App Settings] --> B[Functions Host]
    B --> C[dotnet-isolated worker]
    C --> D[Functions execution]
```
### Step X - Validate isolated worker conventions
```bash
grep "FUNCTIONS_WORKER_RUNTIME" "local.settings.json"
grep "ConfigureFunctionsWebApplication" "Program.cs"
```

Confirm that HTTP functions use `HttpRequestData` and `HttpResponseData`, and that logging is constructor-injected with `ILogger<T>`.

## Verification
```text
Name                          Value                SlotSetting
----------------------------  -------------------  -----------
FUNCTIONS_WORKER_RUNTIME      dotnet-isolated      False
FUNCTIONS_EXTENSION_VERSION   ~4                   False
AZURE_FUNCTIONS_ENVIRONMENT   Production           False
APP_ENV                       production           False
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
