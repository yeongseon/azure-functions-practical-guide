# Monitoring

This guide describes how to monitor Azure Functions in production using Azure Monitor and Application Insights.
It combines metrics, logs, traces, and dashboards into a practical operational workflow.

!!! tip "Platform Guide"
    For scaling architecture and plan comparison, see [Scaling](../platform/scaling.md).

!!! tip "Language Guide"
    For Python deployment specifics, see the [Python Tutorial](../language-guides/python/tutorial/index.md).

## Monitoring architecture

Azure Functions emits multiple telemetry streams:

- **Platform metrics** in Azure Monitor (execution count, failures, instance activity).
- **Application telemetry** in Application Insights (requests, dependencies, traces, exceptions).
- **Activity logs** for control-plane changes.

Use all three for complete operational visibility.

## Enable Application Insights

Set the connection string in app settings:

```bash
az functionapp config appsettings set \
    --resource-group <resource-group> \
    --name <app-name> \
    --settings APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=<masked>;IngestionEndpoint=https://<region>.in.applicationinsights.azure.com/"
```

Prefer connection strings over legacy instrumentation-key-only configuration.

## Core metrics to track

Track a small set of high-signal metrics first:

| Signal | Why it matters |
|---|---|
| Execution count | Detect traffic shifts and workload volume |
| Execution duration | Detect latency regressions and cold start symptoms |
| Failure count/rate | Detect runtime and dependency instability |
| Instance count | Observe scale behavior per plan |
| Queue or backlog depth | Detect processing lag in event-driven flows |

!!! note "Backlog metrics"
    Queue-length and lag metrics usually come from the messaging service (for example, Storage Queue or Service Bus), not only from the Function App resource.

## Live Metrics stream

Use Live Metrics during deployments and incidents for near real-time visibility:

1. Open Application Insights.
2. Select **Live Metrics**.
3. Watch request rate, failures, and server response time during rollout.

This is especially useful during slot swaps and traffic ramp-up windows.

## Log Analytics and KQL basics

Application Insights data is queryable with KQL.

### Recent failed invocations

```kql
requests
| where timestamp > ago(1h)
| where success == false
| project timestamp, name, resultCode, duration, operation_Id
| order by timestamp desc
```

### Slow operations over time

```kql
requests
| where timestamp > ago(24h)
| summarize p95_duration=percentile(duration, 95), avg_duration=avg(duration) by bin(timestamp, 5m)
| render timechart
```

### Exceptions by type

```kql
exceptions
| where timestamp > ago(7d)
| summarize failures=count() by type, outerMessage
| order by failures desc
```

### End-to-end correlation

```kql
union requests, dependencies, traces, exceptions
| where operation_Id == "<operation-id>"
| project timestamp, itemType, name, message, resultCode, duration
| order by timestamp asc
```

## Dashboards and workbooks

Build a workbook that answers these operational questions:

- Is availability stable?
- Are failures isolated to a function, dependency, or region?
- Did a deployment change latency or error distribution?
- Is queue backlog growing faster than throughput?

Recommended workbook visuals:

- Timechart of request count and failure rate.
- P95/P99 duration trend by function name.
- Exceptions by type and operation.
- Dependency failure trend for external calls.
- Queue depth trend alongside execution rate.

## Sampling and data volume control

Adjust Application Insights sampling in `host.json` when telemetry volume grows.

```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 5,
        "excludedTypes": "Request;Exception"
      }
    }
  }
}
```

Keep request and exception data unsampled for reliable incident triage.

## Operational monitoring routine

Daily:

- Check failure trend and top exception signatures.
- Verify queue backlog and processing lag.

Per deployment:

- Monitor Live Metrics during release window.
- Compare before/after latency and failure ratio.

Weekly:

- Review dashboard trends and adjust alert sensitivity.
- Validate telemetry cost and sampling strategy.

## Common blind spots

- Monitoring only HTTP success and ignoring non-HTTP triggers.
- Missing downstream dependency metrics.
- Over-sampling that removes needed forensic signals.
- No version marker in logs, making release impact hard to isolate.

## See Also

- [Alerts](alerts.md)
- [Cold Start](cold-start.md)
- [Troubleshooting KQL](../troubleshooting/kql.md)

## Sources

- [Monitor Azure Functions](https://learn.microsoft.com/azure/azure-functions/monitor-functions)
- [Application Insights overview](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- [Logs in Azure Monitor](https://learn.microsoft.com/azure/azure-monitor/logs/data-platform-logs)
- [Create and share Azure Monitor workbooks](https://learn.microsoft.com/azure/azure-monitor/visualize/workbooks-overview)
