# 03 - Configuration (Premium)

Configure runtime settings, storage options, and networking-related app configuration for Azure Functions on Elastic Premium.

## Prerequisites

- You completed [02 - First Deploy](02-first-deploy.md).
- You exported `$RG`, `$APP_NAME`, `$PLAN_NAME`, `$STORAGE_NAME`, `$LOCATION`.
- Your Function App is running on `EP1`, `EP2`, or `EP3` (`ElasticPremium`).

## Steps

1. Confirm plan SKU and operating system.

    ```bash
    az functionapp plan show \
      --name "$PLAN_NAME" \
      --resource-group "$RG" \
      --query "{sku:sku.name,tier:sku.tier,kind:kind,reserved:reserved}" \
      --output json
    ```

2. Set required runtime app settings (classic app settings path).

    ```bash
    az functionapp config appsettings set \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --settings \
        "FUNCTIONS_WORKER_RUNTIME=python" \
        "FUNCTIONS_EXTENSION_VERSION=~4" \
        "AzureWebJobsFeatureFlags=EnableWorkerIndexing" \
        "WEBSITE_RUN_FROM_PACKAGE=1"
    ```

3. Configure host storage as a connection string.

    ```bash
    STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
      --name "$STORAGE_NAME" \
      --resource-group "$RG" \
      --query "connectionString" \
      --output tsv)

    az functionapp config appsettings set \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --settings "AzureWebJobsStorage=$STORAGE_CONNECTION_STRING"
    ```

4. (Alternative) configure host storage as identity-based.

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


5. Configure file share-based content settings (Premium-supported).

    ```bash
    az functionapp config appsettings set \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --settings \
        "WEBSITE_CONTENTSHARE=$APP_NAME" \
        "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING=$STORAGE_CONNECTION_STRING"
    ```

6. Set Premium behavior settings and environment values.

    ```bash
    az functionapp config appsettings set \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --settings \
        "AZURE_FUNCTIONS_ENVIRONMENT=Production" \
        "WEBSITE_CONTENTOVERVNET=1" \
        "WEBSITE_VNET_ROUTE_ALL=1"
    ```

7. Inspect current app settings and verify key values.

    ```bash
    az functionapp config appsettings list \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --output table
    ```

8. Review Premium configuration constraints.

    - Premium uses plan-level scaling and keeps at least one warm instance running.
    - Maximum scale is 100 instances for the plan.
    - Execution timeout default is 30 minutes; maximum is unlimited.
    - Kudu/SCM endpoint is available at `https://$APP_NAME.scm.azurewebsites.net`.
    - File share-based deployment/content is supported on Premium.

## Expected Output

```json
{
  "sku": "EP1",
  "tier": "ElasticPremium",
  "kind": "elastic",
  "reserved": true
}
```

```text
[
  {
    "name": "FUNCTIONS_WORKER_RUNTIME",
    "slotSetting": false,
    "value": "python"
  },
  {
    "name": "AzureWebJobsStorage",
    "slotSetting": false,
    "value": "DefaultEndpointsProtocol=https;AccountName=stpremdemo123;AccountKey=<masked>;EndpointSuffix=core.windows.net"
  }
]
```

## Next Steps

> **Next:** [04 - Logging and Monitoring](04-logging-monitoring.md)

## References

- [App settings reference for Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-app-settings)
- [Functions scale and hosting](https://learn.microsoft.com/azure/azure-functions/functions-scale)
- [Azure Functions networking options](https://learn.microsoft.com/azure/azure-functions/functions-networking-options)
