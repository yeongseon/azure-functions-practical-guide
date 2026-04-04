# Alerts

This guide explains how to build actionable alerting for Azure Functions.
It covers metric alerts, log query alerts, smart detection, and action groups.

!!! tip "Platform Guide"
    For scaling architecture and plan comparison, see [Scaling](../platform/scaling.md).

!!! tip "Language Guide"
    For Python deployment specifics, see the [Python Tutorial](../language-guides/python/tutorial/index.md).

## Alerting principles

Use alert rules that are:

- **Actionable**: someone can do something immediately.
- **Low-noise**: avoid alert fatigue from unstable thresholds.
- **Correlated**: combine function metrics and dependency signals.
- **Owner-mapped**: every alert routes to a responsible team.

## Action groups first

Create action groups before rules so all alerts route consistently.

```bash
az monitor action-group create \
    --resource-group <resource-group> \
    --name <action-group-name> \
    --short-name <short-name>
```

Add receivers (email, webhook, SMS, automation runbook) according to incident process.

## Metric alerts

Metric alerts are ideal for fast detection of high-level service degradation.

Typical Azure Functions metric alert candidates:

- Function execution failures.
- HTTP 5xx response trend.
- High execution duration percentile.
- Instance count saturation relative to configured limits.

Example metric alert (placeholder threshold, tune per baseline):

```bash
az monitor metrics alert create \
    --resource-group <resource-group> \
    --name <alert-name> \
    --scopes <function-app-resource-id> \
    --condition "total FunctionExecutionCount > <threshold>" \
    --description "Execution anomaly detected" \
    --evaluation-frequency 1m \
    --window-size 5m \
    --action <action-group-resource-id>
```

## Log query alerts

Log alerts are better for nuanced failure patterns not represented by one metric.

Common KQL-based alert scenarios:

- Failure rate exceeds baseline for specific functions.
- Repeated exception signature appears in short window.
- Queue backlog age exceeds acceptable processing delay.

Example KQL pattern for failed requests count:

```kql
requests
| where timestamp > ago(5m)
| where success == false
| summarize failures=count()
```

## Smart detection

Application Insights smart detection can identify anomalies such as sudden failure spikes or performance degradation.

Use smart detection as supplementary signal, not your only paging mechanism.

## Recommended baseline alert set

Start with this minimum set and tune after two to four weeks of production data:

1. **Availability / health endpoint failures**.
2. **Function failure count spike**.
3. **P95 duration increase**.
4. **Queue backlog growth**.
5. **Critical dependency failures** (database, messaging, external API).

## Tuning guidance

- Build thresholds from observed baseline and SLO targets.
- Use dynamic thresholds where workloads are highly seasonal.
- Separate warning and critical severities.
- Suppress expected noise during planned maintenance windows.

## Incident routing patterns

- Route warning severity to chat and ticket systems.
- Route critical severity to paging channel.
- Attach runbook links in alert descriptions.
- Include ownership metadata by service or function group.

## Alert quality checklist

- Rule has clear owner.
- Rule has clear remediation path.
- Rule uses tested query/metric scope.
- Rule avoids duplicate pages for same incident.
- Rule is reviewed after every major incident.

## See Also

- [Monitoring](monitoring.md)
- [Recovery](recovery.md)
- [Troubleshooting Playbooks](../troubleshooting/playbooks.md)

## Sources

- [Create and manage action groups](https://learn.microsoft.com/azure/azure-monitor/alerts/action-groups)
- [Create metric alerts in Azure Monitor](https://learn.microsoft.com/azure/azure-monitor/alerts/alerts-metric)
- [Create log search alerts in Azure Monitor](https://learn.microsoft.com/azure/azure-monitor/alerts/alerts-log)
- [Smart detection in Application Insights](https://learn.microsoft.com/azure/azure-monitor/alerts/proactive-diagnostics)
