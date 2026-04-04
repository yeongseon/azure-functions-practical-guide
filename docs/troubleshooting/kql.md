# KQL Query Library for Azure Functions

Use these KQL queries during incidents to validate hypotheses with telemetry.
Queries target Azure Functions data in Application Insights with these core tables:

- `requests`
- `traces`
- `exceptions`
- `dependencies`
- `customMetrics`

## Usage notes

1. Keep time range tight (`ago(30m)`, `ago(1h)`) during triage.
2. Always filter by app role name to avoid cross-app noise.
3. Save high-value queries to your incident workbook.

Template variable:

```kusto
let appName = "func-myapp-prod";
```

!!! tip "Operations Guide"
    For monitoring setup and alert configuration, see [Monitoring](../operations/monitoring.md) and [Alerts](../operations/alerts.md).

## 1) Function execution summary (success/failure/duration)

```kusto
let appName = "func-myapp-prod";
requests
| where timestamp > ago(1h)
| where cloud_RoleName =~ appName
| where operation_Name startswith "Functions."
| summarize
    Invocations = count(),
    Failures = countif(success == false),
    FailureRatePercent = round(100.0 * countif(success == false) / count(), 2),
    P95Ms = percentile(duration, 95)
  by FunctionName = operation_Name
| order by Failures desc, P95Ms desc
```

## 2) Failed invocations with error details

```kusto
let appName = "func-myapp-prod";
requests
| where timestamp > ago(2h)
| where cloud_RoleName =~ appName
| where operation_Name startswith "Functions."
| where success == false
| project timestamp, operation_Id, FunctionName = operation_Name, resultCode, duration
| join kind=leftouter (
    exceptions
    | where timestamp > ago(2h)
    | where cloud_RoleName =~ appName
    | project operation_Id, ExceptionType = type, ExceptionMessage = outerMessage
) on operation_Id
| order by timestamp desc
```

## 3) Cold start analysis

```kusto
let appName = "func-myapp-prod";
traces
| where timestamp > ago(6h)
| where cloud_RoleName =~ appName
| where message has_any ("Host started", "Initializing Host", "Host lock lease acquired")
| summarize StartupEvents=count() by bin(timestamp, 15m)
| join kind=leftouter (
    requests
    | where timestamp > ago(6h)
    | where cloud_RoleName =~ appName
    | where operation_Name startswith "Functions."
    | summarize FirstInvocation=min(timestamp), FirstDurationMs=min(duration) by bin(timestamp, 15m)
) on timestamp
| order by timestamp desc
```

## 4) Dependency call failures

```kusto
let appName = "func-myapp-prod";
dependencies
| where timestamp > ago(1h)
| where cloud_RoleName =~ appName
| summarize
    Calls=count(),
    Failed=countif(success == false),
    FailureRatePercent=round(100.0 * countif(success == false) / count(), 2),
    P95Ms=percentile(duration, 95)
  by target, type
| order by Failed desc, P95Ms desc
```

## 5) Queue processing latency

```kusto
let appName = "func-myapp-prod";
customMetrics
| where timestamp > ago(2h)
| where cloud_RoleName =~ appName
| where name in ("QueueMessageAgeMs", "QueueProcessingLatencyMs", "QueueDequeueDelayMs")
| summarize AvgMs=avg(value), P95Ms=percentile(value, 95), MaxMs=max(value) by MetricName=name, bin(timestamp, 5m)
| order by timestamp desc
```

## 6) Exception trends

```kusto
let appName = "func-myapp-prod";
exceptions
| where timestamp > ago(24h)
| where cloud_RoleName =~ appName
| summarize Count=count() by bin(timestamp, 15m), type
| order by timestamp desc
```

Top exceptions by impact:

```kusto
let appName = "func-myapp-prod";
exceptions
| where timestamp > ago(24h)
| where cloud_RoleName =~ appName
| summarize Total=count(), FirstSeen=min(timestamp), LastSeen=max(timestamp) by type, outerMessage
| order by Total desc
```

## 7) Scaling events timeline

```kusto
let appName = "func-myapp-prod";
traces
| where timestamp > ago(6h)
| where cloud_RoleName =~ appName
| where message has_any ("scale", "instance", "worker", "concurrency", "drain")
| project timestamp, severityLevel, message
| order by timestamp desc
```

## 8) Host startup/shutdown events

```kusto
let appName = "func-myapp-prod";
traces
| where timestamp > ago(12h)
| where cloud_RoleName =~ appName
| where message has_any ("Host started", "Job host started", "Host shutdown", "Host is shutting down", "Stopping JobHost")
| project timestamp, severityLevel, message
| order by timestamp desc
```

## Correlation helper (single invocation)

Use when you already have an `operation_Id` from a failed request.

```kusto
let opId = "<operation-id>";
union isfuzzy=true
(
    requests
    | where operation_Id == opId
    | project timestamp, itemType="request", name=operation_Name, success, resultCode, duration, details=tostring(url)
),
(
    dependencies
    | where operation_Id == opId
    | project timestamp, itemType="dependency", name=target, success, resultCode, duration, details=tostring(data)
),
(
    exceptions
    | where operation_Id == opId
    | project timestamp, itemType="exception", name=type, success=bool(false), resultCode="", duration=timespan(null), details=outerMessage
),
(
    traces
    | where operation_Id == opId
    | project timestamp, itemType="trace", name="trace", success=bool(true), resultCode="", duration=timespan(null), details=message
)
| order by timestamp asc
```

## See Also

- [First 10 Minutes](first-10-minutes.md)
- [Playbooks](playbooks.md)
- [Methodology](methodology.md)
- [Azure Monitor Logs query overview](https://learn.microsoft.com/azure/azure-monitor/logs/log-query-overview)
- [Application Insights data model](https://learn.microsoft.com/azure/azure-monitor/app/data-model)
