# 04 - Logging and Monitoring (Consumption)

Set up baseline observability for a Consumption (Y1) Function App with Application Insights and CLI log queries.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Azure CLI | 2.61+ | Configure diagnostics and query logs |
| Deployed Function App | Y1 | Existing app from tutorial 02 |
| Application Insights | Workspace-based | Telemetry destination |

## What You'll Build

You will connect the Function App to Application Insights, generate sample traffic, and verify request telemetry and live logs for a Linux Consumption deployment.

!!! info "Infrastructure Context"
    **Plan**: Consumption (Y1) | **Network**: Public internet only | **VNet**: ❌ Not supported

    Consumption has no VNet integration or private endpoint support. All traffic flows over the public internet. Storage uses connection string authentication.

    ```mermaid
    flowchart LR
        INET["Internet"] -->|HTTPS| FA["Function App Y1"]
        FA --> ST["Storage Account\npublic access"]
        FA --> AI["App Insights"]
    ```

```mermaid
flowchart LR
    A[Function App requests] --> B[Application Insights]
    B --> C[CLI query for recent requests]
    A --> D[Live log tail]
```

## Steps

### Step 1 - Set variables

```bash
export RG="rg-func-consumption-demo"
export APP_NAME="func-consumption-demo-001"
export STORAGE_NAME="stconsumptiondemo001"
export LOCATION="eastus"
```

### Step 2 - Create Application Insights

```bash
az monitor app-insights component create \
  --app "appi-func-consumption-demo" \
  --resource-group "$RG" \
  --location "$LOCATION" \
  --application-type web
```

### Step 3 - Link Function App to Application Insights

```bash
export APPINSIGHTS_CONNECTION_STRING=$(az monitor app-insights component show \
  --app "appi-func-consumption-demo" \
  --resource-group "$RG" \
  --query "connectionString" \
  --output tsv)

az functionapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --settings "APPLICATIONINSIGHTS_CONNECTION_STRING=$APPINSIGHTS_CONNECTION_STRING"
```

### Step 4 - Generate test traffic

```bash
curl --request GET "https://$APP_NAME.azurewebsites.net/api/health"
curl --request GET "https://$APP_NAME.azurewebsites.net/api/requests/log-levels"
curl --request GET "https://$APP_NAME.azurewebsites.net/api/exceptions/test-error"
```

### Step 5 - Query recent requests

```bash
az monitor app-insights query \
  --app "appi-func-consumption-demo" \
  --resource-group "$RG" \
  --analytics-query "requests | take 5 | project timestamp, name, resultCode, success" \
  --output table
```

### Step 6 - Stream host logs from CLI

```bash
az webapp log tail \
  --name "$APP_NAME" \
  --resource-group "$RG"
```

Use log streaming and Application Insights for diagnostics on Linux Consumption.

## Verification

Application Insights query output excerpt:

```text
Timestamp                    Name                    ResultCode    Success
---------------------------  ----------------------  ------------  --------
2026-04-03T09:37:10.123456Z GET /api/health         200           True
2026-04-03T09:37:13.012345Z GET /api/requests/...   200           True
2026-04-03T09:37:16.456789Z GET /api/exceptions/... 200           True
```

Log tail excerpt:

```text
2026-04-03T09:37:10.100Z  Executing 'Functions.health' (Reason='This function was programmatically called...')
2026-04-03T09:37:10.123Z  Executed 'Functions.health' (Succeeded, Duration=23ms)
2026-04-03T09:37:16.430Z  Executed 'Functions.test_error' (Succeeded, Duration=44ms)
```

## Next Steps

Use Infrastructure as Code to make this setup repeatable.

> **Next:** [05 - Infrastructure as Code](05-infrastructure-as-code.md)

## See Also

- [Tutorial Overview & Plan Chooser](../index.md)
- [Python Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources

- [Monitor Azure Functions](https://learn.microsoft.com/azure/azure-functions/monitor-functions)
- [Application Insights query with Azure CLI](https://learn.microsoft.com/cli/azure/monitor/app-insights/query)
- [Stream logs with Azure CLI](https://learn.microsoft.com/cli/azure/webapp/log)
