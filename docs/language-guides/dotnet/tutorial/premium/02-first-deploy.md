# 02 - First Deploy (Premium)

Deploy your .NET isolated worker app to the Premium plan with long-form Azure CLI commands and validate your first production endpoint.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| .NET SDK | 8.0 (LTS) | Build and run isolated worker functions |
| Azure Functions Core Tools | v4 | Local host and deployment commands |
| Azure CLI | 2.61+ | Provision and configure Azure resources |

!!! info "Plan basics"
    Premium (EP) keeps warm instances, supports deployment slots, and is suitable for low-latency and long-running functions.
    Supports VNet integration, private endpoints, and deployment slots.

## What You'll Build

- A Linux Premium Function App running .NET 8 isolated worker
- A first deployment from local build artifacts to Azure
- A secured `Health` endpoint validation using a function key

## Steps
### Step 1 - Set deployment variables
```bash
export RG="rg-dotnet-premium-demo"
export APP_NAME="func-dotnet-premium-demo"
export STORAGE_NAME="stdotnetpremiumdemo"
export PLAN_NAME="plan-dotnet-premium-demo"
export LOCATION="koreacentral"
```

### Step 2 - Create required Azure resources
```bash
az group create --name "$RG" --location "$LOCATION"
az storage account create \
  --name "$STORAGE_NAME" \
  --resource-group "$RG" \
  --location "$LOCATION" \
  --sku Standard_LRS \
  --kind StorageV2
az functionapp plan create \
  --name "$PLAN_NAME" \
  --resource-group "$RG" \
  --location "$LOCATION" \
  --sku EP1 \
  --is-linux true
az functionapp create \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --storage-account "$STORAGE_NAME" \
  --plan "$PLAN_NAME" \
  --functions-version 4 \
  --runtime dotnet-isolated \
  --runtime-version 8 \
  --os-type Linux
```

### Step 3 - Build and publish the app
```bash
dotnet build
dotnet publish --configuration Release --output ./publish
func azure functionapp publish "$APP_NAME"
```

### Step 4 - Verify the endpoint
```bash
export FUNCTION_KEY=$(az functionapp function keys list \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --function-name "Health" \
  --query "default" \
  --output tsv)
curl --request GET "https://$APP_NAME.azurewebsites.net/api/health?code=$FUNCTION_KEY"
```

```mermaid
flowchart TD
    A[Local source] --> B[dotnet publish]
    B --> C[func azure functionapp publish]
    C --> D[Premium Function App]
    D --> E[HTTP validation]
```
### Step X - Validate isolated worker conventions
```bash
grep "FUNCTIONS_WORKER_RUNTIME" "local.settings.json"
grep "ConfigureFunctionsWebApplication" "Program.cs"
```

Confirm that HTTP functions use `HttpRequestData` and `HttpResponseData`, and that logging is constructor-injected with `ILogger<T>`.

## Verification
```text
{"status":"healthy"}
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
