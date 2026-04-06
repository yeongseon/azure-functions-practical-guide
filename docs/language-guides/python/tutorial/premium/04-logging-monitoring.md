# 04 - Logging and Monitoring (Premium)

Enable observability for a Premium Function App using Application Insights, Log Analytics queries, and Kudu/SCM diagnostics.

## Prerequisites

- You completed [03 - Configuration](03-configuration.md).
- You exported `$RG`, `$APP_NAME`, `$PLAN_NAME`, `$STORAGE_NAME`, `$LOCATION`.
- Your Function App is deployed and returning `200` from `/api/health`.

## Steps

1. Create a Log Analytics workspace and Application Insights component.

    ```bash
    az monitor log-analytics workspace create \
      --workspace-name "log-$APP_NAME" \
      --resource-group "$RG" \
      --location "$LOCATION"

    az monitor app-insights component create \
      --app "appi-$APP_NAME" \
      --resource-group "$RG" \
      --location "$LOCATION" \
      --workspace "/subscriptions/<subscription-id>/resourceGroups/$RG/providers/Microsoft.OperationalInsights/workspaces/log-$APP_NAME" \
      --application-type "web"
    ```

2. Attach Application Insights connection string to the Function App.

    ```bash
    APPINSIGHTS_CONNECTION_STRING=$(az monitor app-insights component show \
      --app "appi-$APP_NAME" \
      --resource-group "$RG" \
      --query "connectionString" \
      --output tsv)

    az functionapp config appsettings set \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --settings "APPLICATIONINSIGHTS_CONNECTION_STRING=$APPINSIGHTS_CONNECTION_STRING"
    ```

3. Stream live logs from the app.

    ```bash
    az webapp log tail \
      --name "$APP_NAME" \
      --resource-group "$RG"
    ```

4. Query recent request telemetry.

    ```bash
    az monitor app-insights query \
      --app "appi-$APP_NAME" \
      --resource-group "$RG" \
      --analytics-query "requests | where timestamp > ago(15m) | project timestamp, name, resultCode, duration | order by timestamp desc | take 20" \
      --output table
    ```

5. Query exceptions and traces.

    ```bash
    az monitor app-insights query \
      --app "appi-$APP_NAME" \
      --resource-group "$RG" \
      --analytics-query "exceptions | where timestamp > ago(24h) | project timestamp, type, outerMessage | order by timestamp desc | take 20" \
      --output table

    az monitor app-insights query \
      --app "appi-$APP_NAME" \
      --resource-group "$RG" \
      --analytics-query "traces | where timestamp > ago(15m) | project timestamp, severityLevel, message | order by timestamp desc | take 20" \
      --output table
    ```

6. Use Kudu/SCM for runtime diagnostics (Premium supports SCM).

    ```bash
    az functionapp deployment list-publishing-profiles \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --output table
    ```

    Then open `https://$APP_NAME.scm.azurewebsites.net` and inspect:
    - `LogFiles/Application/Functions/Function/*`
    - `Debug console` for filesystem checks
    - deployed artifacts (file share-based content)

7. Confirm Premium monitoring expectations.

    - Pre-warmed instances reduce trigger and HTTP cold-start latency.
    - Because at least one instance always runs, baseline telemetry remains active.
    - Scaling events occur at plan level across functions in the same app plan.

## Expected Output

```text
Live Log Stream --- Connected
2026-01-01T00:01:02.345 [Information] Executing 'Functions.health' (Reason='This function was programmatically called via the host APIs.', Id=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
2026-01-01T00:01:02.512 [Information] Executed 'Functions.health' (Succeeded, Id=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx, Duration=167ms)
```

```text
Timestamp                  Name    ResultCode    Duration
-------------------------  ------  ----------    --------
2026-01-01T00:01:02.512Z   health  200           00:00:00.167
```

## Next Steps

> **Next:** [05 - Infrastructure as Code](05-infrastructure-as-code.md)

## See Also

- [Tutorial Overview & Plan Chooser](../index.md)
- [Python Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources

- [Monitor Azure Functions](https://learn.microsoft.com/azure/azure-functions/monitor-functions)
- [Application Insights query with Azure CLI](https://learn.microsoft.com/azure/azure-monitor/app/azure-cli)
- [Kudu service overview](https://github.com/projectkudu/kudu/wiki)
