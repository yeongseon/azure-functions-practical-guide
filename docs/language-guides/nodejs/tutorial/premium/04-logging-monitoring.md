---
hide:
  - toc
validation:
  az_cli:
    last_tested: 2026-04-10
    cli_version: "2.83.0"
    core_tools_version: "4.8.0"
    result: pass
  bicep:
    last_tested: null
    result: not_tested
---

# 04 - Logging and Monitoring (Premium)

Capture structured logs, query telemetry, and validate operational visibility.

## Prerequisites

- You completed [03 - Configuration](03-configuration.md).
- Your function app has Application Insights connected.

| Tool | Version | Purpose |
|---|---|---|
| Node.js | 20+ | Local runtime and package execution |
| Azure Functions Core Tools | v4 | Local host and publishing |
| Azure CLI | 2.61+ | Azure resource provisioning and management |

!!! info "Plan basics"
    Premium provides always-warm instances, VNet integration, deployment slots, and unlimited timeout support.

## What You'll Build

You will emit structured application logs from a Node.js HTTP function and connect the app to Application Insights.
You will query recent traces to verify that runtime events are captured and searchable.

!!! info "Infrastructure Context"
    **Plan**: Premium (EP1) | **Monitoring**: Application Insights (auto-created)

    Application Insights is auto-created with the **same name** as the function app during `az functionapp create`. The `APPLICATIONINSIGHTS_CONNECTION_STRING` is auto-configured — no manual setup needed.

    ```mermaid
    flowchart LR
        FA[Function App\nPremium EP1] -->|APPLICATIONINSIGHTS_CONNECTION_STRING| AI[Application Insights\nsame name as function app]
        AI --> LAW[Log Analytics\nWorkspace]
        USER[Developer] -->|az monitor app-insights query| AI

        style FA fill:#ff8c00,color:#fff
        style AI fill:#E3F2FD
        style LAW fill:#FFF3E0
    ```

## Steps

### Step 1 — Verify Application Insights is connected

Application Insights was auto-created during `az functionapp create`. Verify:

```bash
az monitor app-insights component show \
  --app "$APP_NAME" \
  --resource-group "$RG" \
  --query "{name:name, connectionString:connectionString}" \
  --output json
```

Expected output (abridged):

```json
{
  "connectionString": "InstrumentationKey=<key>;IngestionEndpoint=https://koreacentral-0.in.applicationinsights.azure.com/;...",
  "name": "func-ndprem-04100022"
}
```

!!! note "App Insights name = function app name"
    Unlike some tutorials that suggest creating `$APP_NAME-ai`, the auto-created App Insights uses the **exact function app name**. Use `--app "$APP_NAME"` (not `--app "$APP_NAME-ai"`) for queries.

### Step 2 — Generate log traffic

Invoke the `logLevels` endpoint to emit logs at all severity levels:

```bash
curl --request GET "https://$APP_NAME.azurewebsites.net/api/requests/log-levels"
```

Expected output:

```json
{"message":"Logged at all levels","levels":["DEBUG","INFO","WARNING","ERROR","CRITICAL"]}
```

### Step 3 — Query traces

Wait 2–5 minutes for telemetry ingestion, then query:

```bash
az monitor app-insights query \
  --app "$APP_NAME" \
  --resource-group "$RG" \
  --analytics-query "traces | where timestamp > ago(10m) | project timestamp, message, severityLevel | take 10" \
  --output json
```

Expected output (abridged):

```json
{
  "tables": [
    {
      "name": "PrimaryResult",
      "columns": [
        { "name": "timestamp", "type": "datetime" },
        { "name": "message", "type": "string" },
        { "name": "severityLevel", "type": "int" }
      ],
      "rows": [
        ["2026-04-09T15:39:49Z", "Using the AzureStorage storage provider.", 1],
        ["2026-04-09T15:39:50Z", "Initializing Warmup Extension.", 1],
        ["2026-04-09T15:42:26Z", "status endpoint called", 1]
      ]
    }
  ]
}
```

### Step 4 — Query function execution requests

```bash
az monitor app-insights query \
  --app "$APP_NAME" \
  --resource-group "$RG" \
  --analytics-query "requests | where timestamp > ago(30m) | summarize count() by name | order by count_ desc" \
  --output json
```

Expected output (abridged):

```json
{
  "tables": [
    {
      "columns": [
        { "name": "name", "type": "string" },
        { "name": "count_", "type": "long" }
      ],
      "rows": [
        ["health", 3],
        ["helloHttp", 2],
        ["queueProcessor", 2],
        ["scheduledCleanup", 1],
        ["logLevels", 1]
      ]
    }
  ]
}
```

!!! tip "Telemetry ingestion delay"
    New Application Insights resources may take 2–5 minutes to start receiving data. If queries return empty results, wait and retry.

### Plan-specific notes

- Premium auto-creates Application Insights with the function app name.
- Unlike Consumption, Premium's always-warm instances produce continuous telemetry (warmup events, timer executions) even without user traffic.
- Use `requests` table for function execution metrics and `traces` for application logs.

## Verification

Verify that:

1. `az monitor app-insights component show` returns the App Insights resource with a valid connection string.
2. `traces` query returns recent log entries with severity levels.
3. `requests` query shows function execution counts by name.

## See Also
- [Tutorial Overview & Plan Chooser](../index.md)
- [Node.js Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources
- [Azure Functions Node.js developer guide (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-node)
- [Monitor Azure Functions with Application Insights (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-monitoring)
- [Azure Functions hosting options (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-scale)
