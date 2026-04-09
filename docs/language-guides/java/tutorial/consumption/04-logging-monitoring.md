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

# 04 - Logging and Monitoring (Consumption)

Enable production-grade observability with Application Insights, structured logs, and baseline alerting for Java handlers.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| JDK | 17+ | Compile and run Java functions locally |
| Maven | 3.6+ | Build and package Java artifacts |
| Azure Functions Core Tools | v4 | Start local host and publish artifacts |
| Azure CLI | 2.61+ | Provision Azure resources and inspect app state |

!!! info "Consumption plan basics"
    Consumption (Y1) is serverless with scale-to-zero, up to 200 instances, 1.5 GB memory per instance, and a default 5-minute timeout (max 10 minutes).

## What You'll Build

You will instrument Java handlers with structured logs, route telemetry to Application Insights, and validate query-based monitoring signals for a Consumption-hosted app.

```mermaid
flowchart LR
    A[ExecutionContext logger] --> B[FunctionAppLogs]
    B --> C[Application Insights]
    C --> D[Dashboards and alerts]
```

## Steps

### Step 1 - Emit structured logs in handler methods

The Java reference app uses `ExecutionContext.getLogger()` for structured logging. Here is the `LogLevelsFunction` that emits at multiple severity levels:

```java
@FunctionName("logLevels")
public HttpResponseMessage run(
        @HttpTrigger(
            name = "req",
            methods = {HttpMethod.GET},
            authLevel = AuthorizationLevel.ANONYMOUS,
            route = "loglevels")
        HttpRequestMessage<Optional<String>> request,
        final ExecutionContext context) {

    context.getLogger().info("Info-level message from logLevels");
    context.getLogger().warning("Warning-level message from logLevels");
    context.getLogger().severe("Error-level message from logLevels");

    return request.createResponseBuilder(HttpStatus.OK)
            .header("Content-Type", "application/json")
            .body("{\"logged\":true}")
            .build();
}
```

### Step 2 - Generate telemetry by calling endpoints

```bash
# Trigger structured logging
curl --request GET "https://$APP_NAME.azurewebsites.net/api/loglevels"

# Trigger health check
curl --request GET "https://$APP_NAME.azurewebsites.net/api/health"

# Trigger intentional errors for error telemetry
curl --request GET "https://$APP_NAME.azurewebsites.net/api/testerror"
```

!!! note "Telemetry ingestion delay"
    Application Insights telemetry takes 2-5 minutes to become available for queries after the first request. Wait before running queries.

### Step 3 - Confirm Application Insights connection

Application Insights is auto-created with the function app. Verify the connection:

```bash
az functionapp config appsettings list \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --query "[?name=='APPLICATIONINSIGHTS_CONNECTION_STRING'].value" \
  --output tsv
```

### Step 4 - Query recent traces

```bash
az monitor app-insights query \
  --app "$APP_NAME" \
  --analytics-query "traces | where timestamp > ago(30m) | project timestamp, message, severityLevel | order by timestamp desc | take 20"
```

!!! note "Use function app name for `--app`"
    Since Application Insights is auto-created with the same name as the function app, use `--app "$APP_NAME"` for queries.

### Step 5 - Query request metrics

```bash
az monitor app-insights query \
  --app "$APP_NAME" \
  --analytics-query "requests | where timestamp > ago(30m) | project timestamp, name, resultCode, duration | order by timestamp desc | take 20"
```

### Step 6 - View live log stream

```bash
az webapp log tail \
  --name "$APP_NAME" \
  --resource-group "$RG"
```

!!! warning "`az functionapp log tail` does not exist"
    As of Azure CLI 2.83.0, use `az webapp log tail` (not `az functionapp log tail`) to stream live logs from a function app.

### Step 7 - Add an alert for HTTP 5xx spikes

```bash
FUNCTION_APP_ID=$(az functionapp show \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --query "id" \
  --output tsv)

az monitor metrics alert create \
  --name "func-java-http5xx" \
  --resource-group "$RG" \
  --scopes "$FUNCTION_APP_ID" \
  --condition "total Http5xx > 5" \
  --window-size 5m \
  --evaluation-frequency 1m
```

## Verification

Traces query output:

```text
timestamp                    message                                    severityLevel
---------------------------  -----------------------------------------  -------------
2026-04-09T16:34:06.000Z     Info-level message from logLevels          1
2026-04-09T16:34:06.000Z     Warning-level message from logLevels       2
2026-04-09T16:34:06.000Z     Error-level message from logLevels         3
```

Requests query output:

```text
timestamp                    name            resultCode    duration
---------------------------  --------------  ----------    --------
2026-04-09T16:34:06.000Z     logLevels       200           45.12
2026-04-09T16:34:05.000Z     health          200           12.34
2026-04-09T16:34:04.000Z     testerror       500           8.56
```

LogLevels endpoint response:

```json
{"logged":true}
```

## Next Steps

> **Next:** [05 - Infrastructure as Code](05-infrastructure-as-code.md)

## See Also

- [Tutorial Overview & Plan Chooser](../index.md)
- [Java Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources

- [Azure Functions Java developer guide (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-java)
- [Azure Functions hosting options (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-scale)
- [Create a Java function with Azure Functions Core Tools (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/create-first-function-cli-java)
