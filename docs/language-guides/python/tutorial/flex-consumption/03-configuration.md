# 03 - Configuration (Flex Consumption)

Configure runtime, app settings, and host storage correctly for Flex Consumption so your app deploys cleanly and scales predictably.

## Prerequisites

| Tool | Minimum version | Purpose |
|---|---|---|
| Azure CLI | 2.60+ | Manage app configuration |
| jq | Latest | Read JSON output |
| Existing FC1 app | Deployed | Target for configuration |

## Step 1 - Set Variables

```bash
export BASE_NAME="flexdemo"
export RG="rg-flexdemo"
export APP_NAME="flexdemo-func"
export PLAN_NAME="flexdemo-plan"
export STORAGE_NAME="flexdemostorage"
export APPINSIGHTS_NAME="flexdemo-insights"
export LOCATION="eastus2"

Expected output:

```

```text
```

## Step 2 - Configure Identity-Based Host Storage

Flex Consumption host storage must be identity-based. Use `AzureWebJobsStorage__accountName` and related identity keys, not connection strings.

```

```bash
az functionapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --settings \
    "AzureWebJobsStorage__accountName=$STORAGE_NAME" \
    "AzureWebJobsStorage__credential=managedidentity" \
    "AzureWebJobsStorage__clientId=<managed-identity-client-id>" \
  --output json
```

!!! tip "Why __clientId is required"
    When using a **user-assigned managed identity** (UAMI), you must provide `AzureWebJobsStorage__clientId` so the Functions host knows which identity to authenticate with. Without it, the host cannot resolve which UAMI to use and storage operations will fail. See `infra/flex-consumption/main.bicep` lines 250–252 for the Bicep equivalent.

Expected output:

```

```json
[
  {
    "name": "AzureWebJobsStorage__accountName",
    "slotSetting": false,
    "value": null
  },
  {
    "name": "AzureWebJobsStorage__credential",
    "slotSetting": false,
    "value": null
  },
  {
    "name": "AzureWebJobsStorage__clientId",
    "slotSetting": false,
    "value": null
  }
]
```

## Step 3 - Set Additional App Settings

On Flex Consumption, the runtime name and version are defined in `functionAppConfig` (not in `FUNCTIONS_WORKER_RUNTIME`). Set only the remaining app-level settings here.

```

```bash
az functionapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --settings \
    "AZURE_FUNCTIONS_ENVIRONMENT=Production" \
  --output json
```

!!! warning "Do not set FUNCTIONS_WORKER_RUNTIME on Flex"
    `FUNCTIONS_WORKER_RUNTIME` is **not supported** on Flex Consumption. The runtime is configured via `functionAppConfig.runtime` (see Step 4). Setting it as an app setting may cause unexpected behavior.

Expected output:

```

```json
[
  {
    "name": "AZURE_FUNCTIONS_ENVIRONMENT",
    "slotSetting": false,
    "value": null
  }
]
```

## Step 4 - Validate Runtime Configuration Source

On Flex, runtime/version and scale settings are defined in `functionAppConfig` (resource properties), not classic `siteConfig.appSettings` for runtime identity.

```

```bash
az functionapp show --name "$APP_NAME" --resource-group "$RG" --query "properties.functionAppConfig" --output json
```

Expected output:

```

```json
{
  "deployment": {
    "storage": {
      "type": "blobContainer"
    }
  },
  "runtime": {
    "name": "python",
    "version": "3.11"
  },
  "scaleAndConcurrency": {
    "instanceMemoryMB": 2048,
    "maximumInstanceCount": 100
  }
}
```

## Step 5 - Confirm Flex Plan Characteristics

```

```bash
az appservice plan show --name "$PLAN_NAME" --resource-group "$RG" --query "{sku:sku,reserved:reserved,kind:kind}" --output json
```

Expected output:

```

```json
{
  "kind": "functionapp",
  "reserved": true,
  "sku": {
    "name": "FC1",
    "tier": "FlexConsumption"
  }
}
```

## Step 6 - Configuration Checklist for Flex

- Linux only (`reserved: true`).
- Host storage uses identity (`AzureWebJobsStorage__accountName`, `__credential`, `__clientId` for UAMI).
- Deployment package source is blob container (`functionAppConfig.deployment.storage.type = blobContainer`).
- Blob triggers in production must use Event Grid integration.
- No deployment slots.

## Next Steps

> **Next:** [04 - Logging and Monitoring](04-logging-monitoring.md)

## Sources

- [App settings reference for Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-app-settings)
- [Flex Consumption how-to](https://learn.microsoft.com/azure/azure-functions/flex-consumption-how-to)
- [Identity-based connections for Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-reference#connecting-to-host-storage-with-an-identity)
