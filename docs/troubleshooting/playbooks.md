# Azure Functions Incident Playbooks

These scenario playbooks are for active incidents.
Each follows the same structure: **Symptoms → Possible Causes → Diagnostic Steps → Resolution**.

## Prerequisites
- Access to Azure CLI, Application Insights, and Log Analytics.
- Subscription and app context prepared.

```bash
RG="rg-myapp-prod"
APP_NAME="func-myapp-prod"
SUBSCRIPTION_ID="<subscription-id>"
WORKSPACE_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

!!! tip "Operations Guide"
    For monitoring setup and alert configuration, see [Monitoring](../operations/monitoring.md) and [Alerts](../operations/alerts.md).

## Functions not executing
### Symptoms
- Events arrive, but invocation count is near zero.
- App appears running, but trigger output is absent.

### Possible Causes
- Function disabled via app setting.
- Trigger connection setting invalid.
- Host listener failed to initialize.

### Diagnostic Steps
```bash
az functionapp function list --name "$APP_NAME" --resource-group "$RG" --output table
az functionapp config appsettings list --name "$APP_NAME" --resource-group "$RG" --output table
az monitor log-analytics query \
  --workspace "$WORKSPACE_ID" \
  --analytics-query "traces | where timestamp > ago(30m) | where cloud_RoleName =~ '$APP_NAME' | where message has_any ('disabled','listener','Host started') | order by timestamp desc" \
  --output table
```

### Resolution
- Remove incorrect `AzureWebJobs.<FunctionName>.Disabled` settings.
- Fix trigger connection setting and restart the app.
- Roll back if failure began right after deployment.

## High latency / slow responses
### Symptoms
- P95 latency spikes and timeout rate increases.
- Failures appear during traffic surges or after idle periods.

### Possible Causes
- Cold start delays.
- Slow downstream API or database.
- Concurrency saturation.

### Diagnostic Steps
```bash
az monitor metrics list \
  --resource "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.Web/sites/$APP_NAME" \
  --metric "AverageResponseTime" "Requests" "Http5xx" \
  --interval PT1M \
  --aggregation Average Total \
  --offset 1h \
  --output table

az monitor log-analytics query \
  --workspace "$WORKSPACE_ID" \
  --analytics-query "dependencies | where timestamp > ago(1h) | where cloud_RoleName =~ '$APP_NAME' | summarize p95=percentile(duration,95), failures=countif(success==false) by target" \
  --output table
```

### Resolution
- Reduce cold-start cost (always-ready, dependency trimming).
- Tune dependency timeouts/retries.
- Adjust concurrency and processing model to avoid blocking.

## Functions failing with errors
### Symptoms
- Exception count and `5xx` increase quickly.
- Retries and poison-message rates rise.

### Possible Causes
- Auth failures to downstream resources.
- Function timeout reached.
- Memory pressure or runtime mismatch.

### Diagnostic Steps
```bash
az monitor log-analytics query \
  --workspace "$WORKSPACE_ID" \
  --analytics-query "exceptions | where timestamp > ago(1h) | where cloud_RoleName =~ '$APP_NAME' | summarize count() by type, outerMessage" \
  --output table

az functionapp config show --name "$APP_NAME" --resource-group "$RG" --output json
```

### Resolution
- Repair identity/RBAC or secrets configuration.
- Correct timeout and runtime alignment issues.
- Roll back to last known good artifact if regression is confirmed.

## Queue messages piling up
### Symptoms
- Queue depth and message age rise steadily.
- Processing throughput stays below enqueue rate.

### Possible Causes
- Scale-out not keeping up.
- Poison-message loop.
- Per-message processing regression.

### Diagnostic Steps
```bash
az storage message peek \
  --account-name "<storage-account-name>" \
  --queue-name "<queue-name>" \
  --num-messages 5 \
  --auth-mode login

az monitor metrics list \
  --resource "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.Storage/storageAccounts/<storage-account-name>" \
  --metric "QueueMessageCount" \
  --interval PT1M \
  --aggregation Average \
  --offset 1h \
  --output table
```

### Resolution
- Isolate poison messages and validate retry policy.
- Reduce processing time per message.
- Reassess scale limits and hosting plan fit.

## Blob trigger not firing
### Symptoms
- Blob uploads succeed, but invocations never appear.
- Issue starts after Flex Consumption migration.

### Possible Causes
- Event Grid subscription missing.
- Storage networking or RBAC blocks notifications.
- Trigger binding misconfiguration.

### Diagnostic Steps
```bash
az eventgrid event-subscription list \
  --source-resource-id "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.Storage/storageAccounts/<storage-account-name>" \
  --output table

az monitor log-analytics query \
  --workspace "$WORKSPACE_ID" \
  --analytics-query "traces | where timestamp > ago(1h) | where cloud_RoleName =~ '$APP_NAME' | where message has_any ('BlobTrigger','EventGrid','listener') | order by timestamp desc" \
  --output table
```

### Resolution
- Use Event Grid-based blob trigger on Flex Consumption.
- Recreate missing subscription and verify endpoint delivery.
- Confirm storage access permissions for managed identity.

## Deployment failures
### Symptoms
- Deployment fails or app degrades immediately after release.
- Functions disappear or host startup fails.

### Possible Causes
- Runtime mismatch.
- Missing required app settings.
- Deployment method not suited to hosting model.

### Diagnostic Steps
```bash
az functionapp show --name "$APP_NAME" --resource-group "$RG" --output json
az functionapp config appsettings list --name "$APP_NAME" --resource-group "$RG" --output table
az monitor activity-log list --resource-group "$RG" --offset 2h --output table
```

### Resolution
- Align artifact runtime and app runtime settings.
- Restore required configuration before activation.
- Roll back quickly, then apply a controlled forward fix.

## See Also
- [First 10 Minutes](first-10-minutes.md)
- [Methodology](methodology.md)
- [KQL Query Library](kql.md)
- [Azure Functions best practices](https://learn.microsoft.com/azure/azure-functions/functions-best-practices)
