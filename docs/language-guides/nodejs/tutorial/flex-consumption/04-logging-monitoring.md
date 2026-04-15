---
validation:
  az_cli:
    last_tested: 2026-04-10
    cli_version: "2.83.0"
    core_tools_version: "4.8.0"
    result: pass
  bicep:
    last_tested: null
    result: not_tested
content_sources:
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-reference-node
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-monitoring
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/flex-consumption-plan
---

# 04 - Logging and Monitoring (Flex Consumption)

Capture structured logs, connect Application Insights, and validate telemetry queries.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 20+ | Local runtime and package execution |
| Azure Functions Core Tools | v4 | Local host and publishing |
| Azure CLI | 2.61+ | Azure resource provisioning and management |

!!! info "Flex Consumption plan basics"
    Flex Consumption (FC1) supports VNet integration, identity-based storage, per-function scaling, and remote build workflows.

## What You'll Build

You will emit structured logs from Node.js v4 handlers, verify Application Insights connectivity, and query telemetry data.

!!! info "Infrastructure Context"
    **Plan**: Flex Consumption (FC1) | **Network**: VNet integration supported

    This tutorial verifies Application Insights monitoring on your deployed function app.

    <!-- diagram-id: what-you-ll-build -->
```mermaid
flowchart TD
    FA[Function App\nFlex Consumption FC1] -->|telemetry| AI[Application Insights]
    AI -->|query| KQL["KQL Queries\n• traces\n• requests\n• dependencies"]
    CLI["Azure CLI"] -->|"az monitor app-insights query"| AI

    style FA fill:#0078d4,color:#fff
    style AI fill:#68217A,color:#fff
```

<!-- diagram-id: what-you-ll-build-2 -->
```mermaid
flowchart TD
    A[Log with context.log] --> B[Verify App Insights]
    B --> C[Generate telemetry]
    C --> D[Query traces via KQL]
```

## Steps

### Step 1 - Set variables (if not already set)

```bash
export RG="rg-func-node-flex-demo"
export APP_NAME="<your-function-app-name>"
```

### Step 2 - Understand structured logging

The Node.js v4 model uses `context.log()` for structured logging:

```javascript
const { app } = require('@azure/functions');

app.http('status', {
    methods: ['GET'],
    handler: async (_request, context) => {
        context.log('status endpoint called');
        context.warn('this is a warning');
        context.error('this is an error');
        return { status: 200, jsonBody: { status: 'ok' } };
    }
});
```

### Step 3 - Verify Application Insights

Flex Consumption auto-creates Application Insights with the **same name as the function app** (not `$APP_NAME-ai`):

```bash
az monitor app-insights component show \
  --resource-group "$RG" \
  --query "[].{name:name}" \
  --output table
```

!!! note "Auto-created App Insights"
    `az functionapp create` on Flex Consumption automatically provisions Application Insights using the function app name. The connection string is already set in app settings.

### Step 4 - Generate telemetry

```bash
curl --request GET "https://$APP_NAME.azurewebsites.net/api/health"
curl --request GET "https://$APP_NAME.azurewebsites.net/api/hello/TelemetryTest"
curl --request GET "https://$APP_NAME.azurewebsites.net/api/requests/log-levels"
```

!!! warning "Telemetry ingestion delay"
    Application Insights typically has a 2-5 minute ingestion delay. Wait at least 3 minutes after invoking functions before querying.

### Step 5 - Query traces

```bash
az monitor app-insights query \
  --app "$APP_NAME" \
  --resource-group "$RG" \
  --analytics-query "traces | take 5" \
  --output json
```

!!! note "Use function app name for `--app`"
    On Flex Consumption, the App Insights resource has the same name as the function app. Use `--app "$APP_NAME"` (not `--app "$APP_NAME-ai"`).

### Step 6 - Review Flex Consumption-specific notes

- Flex Consumption does not support Kudu/SCM, so `az functionapp log tail` is not available.
- Use Application Insights queries or the Azure Portal Log Stream for log access.

## Verification

The `traces | take 5` query should return rows with log messages:

```json
{
  "tables": [
    {
      "columns": [
        { "name": "timestamp", "type": "datetime" },
        { "name": "message", "type": "string" },
        { "name": "severityLevel", "type": "int" }
      ],
      "rows": [
        ["2026-04-10T00:28:00.0000000Z", "Handled hello for TelemetryTest", 1],
        ["2026-04-10T00:28:00.0000000Z", "Health check requested", 1]
      ]
    }
  ]
}
```

## Next Steps

> **Next:** [05 - Infrastructure as Code](05-infrastructure-as-code.md)

## See Also

- [Tutorial Overview & Plan Chooser](../index.md)
- [Node.js Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Monitoring](../../../../operations/monitoring.md)
- [Recipes Index](../../recipes/index.md)

## Sources

- [Azure Functions Node.js developer guide (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-node)
- [Monitor Azure Functions with Application Insights (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-monitoring)
- [Azure Functions Flex Consumption plan (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/flex-consumption-plan)
