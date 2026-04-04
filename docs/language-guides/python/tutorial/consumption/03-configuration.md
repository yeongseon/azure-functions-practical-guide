# 03 - Configuration (Consumption)

Configure your deployed Consumption (Y1) function app using classic `siteConfig.appSettings` semantics and CLI app settings commands.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Azure CLI | 2.61+ | Manage function app settings |
| Deployed Function App | Y1 | Target app from tutorial 02 |
| Storage account | Standard_LRS | Runtime state and triggers |

## Steps

### Step 1 - Set variables

```bash
export RG="rg-func-consumption-demo"
export APP_NAME="func-consumption-demo-001"
export STORAGE_NAME="stconsumptiondemo001"
export LOCATION="eastus"
```

### Step 2 - Read current app settings

```bash
az functionapp config appsettings list \
  --name "$APP_NAME" \
  --resource-group "$RG"
```

### Step 3 - Set required and custom app settings

```bash
az functionapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --settings \
    "FUNCTIONS_WORKER_RUNTIME=python" \
    "AzureWebJobsStorage=DefaultEndpointsProtocol=https;AccountName=$STORAGE_NAME;AccountKey=<masked-key>;EndpointSuffix=core.windows.net" \
    "APP_ENV=production" \
    "LOG_LEVEL=Information"
```

For Consumption, app settings are handled as classic app settings (backed by `siteConfig.appSettings`), not the Flex-specific configuration model.

### Step 4 - Optional: identity-based host storage pattern

Instead of a connection string, you can configure identity-based host storage values (both models are valid on Consumption):

```bash
az functionapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --settings \
    "AzureWebJobsStorage__accountName=$STORAGE_NAME" \
    "AzureWebJobsStorage__credential=managedidentity"
```

!!! warning "Identity-based storage requires Managed Identity and RBAC"
    Before using identity-based host storage, you must:

    1. Enable system-assigned managed identity on the Function App: `az functionapp identity assign --name "$APP_NAME" --resource-group "$RG"`
    2. Grant the identity the **Storage Blob Data Owner** role on the storage account: `az role assignment create --assignee-object-id "<principal-id>" --role "Storage Blob Data Owner" --scope "/subscriptions/<subscription-id>/resourceGroups/$RG/providers/Microsoft.Storage/storageAccounts/$STORAGE_NAME"`
    3. Set both `AzureWebJobsStorage__accountName` and `AzureWebJobsStorage__credential=managedidentity` app settings.


### Step 5 - Confirm runtime limits relevant to configuration

- Consumption defaults to a 5-minute timeout and supports up to 10 minutes.
- Memory is fixed at 1.5 GB per instance.
- No always-ready instances are available; cold start is typically more noticeable than Premium.

## Expected Output

App settings update excerpt:

```json
[
  {
    "name": "FUNCTIONS_WORKER_RUNTIME",
    "slotSetting": false,
    "value": null
  },
  {
    "name": "AzureWebJobsStorage",
    "slotSetting": false,
    "value": null
  },
  {
    "name": "APP_ENV",
    "slotSetting": false,
    "value": null
  }
]
```

App details excerpt:

```json
{
  "id": "/subscriptions/<subscription-id>/resourceGroups/rg-func-consumption-demo/providers/Microsoft.Web/sites/func-consumption-demo-001",
  "kind": "functionapp,linux",
  "state": "Running"
}
```

## Next Steps

Now enable operational visibility with logs and monitoring.

> **Next:** [04 - Logging and Monitoring](04-logging-monitoring.md)

## Sources

- [App settings reference for Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-app-settings)
- [Identity-based host storage for Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-reference#connecting-to-host-storage-with-an-identity)
- [host.json reference](https://learn.microsoft.com/azure/azure-functions/functions-host-json)
