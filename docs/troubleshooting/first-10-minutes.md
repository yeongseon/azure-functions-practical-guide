# First 10 Minutes of an Azure Functions Incident

When an incident starts, focus on three outcomes: **confirm platform status, assess app health, and identify recent change signals**.
This checklist is designed for fast triage before deeper root-cause analysis.

## Prerequisites

- Azure CLI access to the production subscription.
- Access to Application Insights and Log Analytics.
- Health endpoint implemented at `GET /api/health`.

Set shared variables:

```bash
RG="rg-myapp-prod"
APP_NAME="func-myapp-prod"
SUBSCRIPTION_ID="<subscription-id>"
APP_INSIGHTS_NAME="appi-myapp-prod"
WORKSPACE_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

!!! tip "Operations Guide"
    For monitoring setup and alert configuration, see [Monitoring](../operations/monitoring.md) and [Alerts](../operations/alerts.md).

## Triage steps

## 1) Check Azure status and regional incidents

Rule out platform-wide issues first.
If a regional outage exists, your app-level actions are secondary.

```bash
az account set --subscription "$SUBSCRIPTION_ID"
az account show --output table
az monitor activity-log list \
  --subscription "$SUBSCRIPTION_ID" \
  --resource-group "$RG" \
  --offset 1h \
  --max-events 20 \
  --output table
```

Also review Azure Service Health in the portal for active advisories on App Service, Storage, and Azure Monitor.

## 2) Check Application Insights Live Metrics

Live Metrics quickly shows whether failures are active, rising, or already stabilized.

```bash
az monitor app-insights component show \
  --app "$APP_INSIGHTS_NAME" \
  --resource-group "$RG" \
  --output table

az monitor metrics list \
  --resource "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.Web/sites/$APP_NAME" \
  --metric "Requests" "Http5xx" "AverageResponseTime" \
  --interval PT1M \
  --aggregation Total Average \
  --offset 30m \
  --output table
```

Interpretation:

- Rising requests + rising failures usually indicate app/dependency failure.
- Flat requests during expected traffic suggests trigger, routing, or ingress issues.

## 3) Check function app health endpoint

Verify if the app can serve a lightweight health probe.

```bash
az functionapp show \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --query "state" \
  --output tsv

curl --silent --show-error --location \
  "https://$APP_NAME.azurewebsites.net/api/health"
```

Interpretation:

- `200 OK` with failing business endpoints points to function-level or dependency issues.
- Health failure indicates host startup/configuration/dependency-critical problems.

## 4) Check host logs in Log Analytics

Look for startup, listener, and runtime errors in the incident window.

```bash
az monitor log-analytics query \
  --workspace "$WORKSPACE_ID" \
  --analytics-query "traces | where timestamp > ago(30m) | where cloud_RoleName =~ '$APP_NAME' | order by timestamp desc | take 100" \
  --output table

az monitor log-analytics query \
  --workspace "$WORKSPACE_ID" \
  --analytics-query "exceptions | where timestamp > ago(30m) | where cloud_RoleName =~ '$APP_NAME' | summarize count() by type, outerMessage" \
  --output table
```

High-signal patterns:

- `Host started` missing or delayed.
- Trigger listener initialization failures.
- Timeout, DNS, storage auth, or Managed Identity errors.

## 5) Check recent deployments and configuration changes

Most incidents are linked to recent changes.
Confirm code, settings, or identity updates in the blast window.

```bash
az monitor activity-log list \
  --resource-group "$RG" \
  --offset 2h \
  --status Succeeded \
  --output table

az functionapp config appsettings list \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --output table
```

If a deployment just happened, prepare rollback and compare app settings with baseline.

## 6) Check scaling and backlog indicators

For event-driven failures, verify whether scale behavior matches incoming demand.

```bash
az monitor metrics list \
  --resource "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.Web/sites/$APP_NAME" \
  --metric "FunctionExecutionCount" "FunctionExecutionUnits" \
  --interval PT1M \
  --aggregation Total \
  --offset 30m \
  --output table

az monitor metrics list \
  --resource "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.Storage/storageAccounts/<storage-account-name>" \
  --metric "QueueMessageCount" \
  --interval PT1M \
  --aggregation Average \
  --offset 30m \
  --output table
```

Interpretation:

- Backlog up + executions flat = trigger/scaling bottleneck.
- Enqueue rate stable + errors rising = likely processing or dependency regression.

## Fast routing after triage

| What you see | Likely area | Next action |
|---|---|---|
| Regional advisory active | Platform dependency | Communicate impact, apply mitigation |
| Health endpoint failing | Host/config/dependency | Use [Playbooks](playbooks.md) error scenarios |
| Queue depth rising rapidly | Scale/poison path | Use queue backlog playbook |
| Failures started after deploy | Release regression | Roll back, then follow [Methodology](methodology.md) |

## Escalate immediately when

- SLA breach is in progress with no safe quick mitigation.
- Data loss risk appears (message drop, poison saturation).
- Security-impacting symptoms are observed.

## See Also

- [Playbooks](playbooks.md)
- [Methodology](methodology.md)
- [KQL Query Library](kql.md)
- [Azure Functions monitoring](https://learn.microsoft.com/azure/azure-functions/functions-monitoring)
- [Azure Service Health overview](https://learn.microsoft.com/azure/service-health/overview)
