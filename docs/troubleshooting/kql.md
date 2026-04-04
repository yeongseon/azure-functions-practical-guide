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

## KQL Tables Quick Reference

| Table | What It Contains | Use When |
|---|---|---|
| `requests` | HTTP trigger invocations | Checking request success/failure/latency |
| `traces` | Host lifecycle, custom logs | Checking startup, listeners, runtime events |
| `exceptions` | Error details with stack traces | Identifying error types and root causes |
| `dependencies` | Outbound calls to external services | Checking dependency health and latency |
| `customMetrics` | Metrics explicitly emitted by your app/SDK (for example `TelemetryClient.TrackMetric`) plus selected Azure Functions runtime metrics (for example `FunctionExecutionCount`) | Checking custom processing/latency metrics and runtime counters |

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

**Example result:**

| FunctionName | Invocations | Failures | FailureRatePercent | P95Ms |
|---|---|---|---|---|
| Functions.QueueProcessor | 4,521 | 12 | 0.27 | 245 |
| Functions.HttpTrigger | 8,932 | 2,104 | 23.56 | 12,500 |
| Functions.TimerCleanup | 240 | 0 | 0.00 | 180 |

**How to interpret:**

| Indicator | Normal | Warning | Critical |
|---|---|---|---|
| FailureRatePercent | < 1% | 1-5% | > 5% |
| P95Ms (HTTP) | < 500ms | 500-2000ms | > 2000ms |
| P95Ms (Queue) | < 1000ms | 1000-5000ms | > 5000ms |

!!! note "Normal vs abnormal"
    **Normal sample:**

    | FunctionName | FailureRatePercent | P95Ms |
    |---|---|---|
    | Functions.QueueProcessor | 0.27 | 245 |
    | Functions.TimerCleanup | 0.00 | 180 |

    **Abnormal sample:**

    | FunctionName | FailureRatePercent | P95Ms |
    |---|---|---|
    | Functions.HttpTrigger | 23.56 | 12,500 |

    If one function is critical while others are normal, focus on that function's dependencies and exception types first.

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

**Example result:**

| timestamp | operation_Id | FunctionName | resultCode | duration | ExceptionType | ExceptionMessage |
|---|---|---|---|---|---|---|
| 2026-04-04T09:11:22Z | op-9f2a1c73 | Functions.HttpTrigger | 500 | 00:00:10.845 | System.UnauthorizedAccessException | Access to downstream API denied for managed identity. |
| 2026-04-04T09:10:58Z | op-75d31e9b | Functions.QueueProcessor | 500 | 00:00:03.294 | Azure.RequestFailedException | Status: 403 (Forbidden) on storage queue update. |
| 2026-04-04T09:10:41Z | op-c2bb6d44 | Functions.HttpTrigger | 502 | 00:00:07.511 | System.Net.Http.HttpRequestException | Connection timed out to backend endpoint. |

**How to interpret:**

| Indicator | Normal | Warning | Critical |
|---|---|---|---|
| Failed rows in 15m | 0-2 | 3-10 | > 10 |
| Repeated ExceptionType | None | Same type repeats 3-5 times | Same type dominates failures |
| duration on failed requests | < 1000ms | 1000-5000ms | > 5000ms |

!!! note "Normal vs abnormal"
    **Normal:** Isolated failures with mixed exception types and quick recovery.

    **Abnormal:** Same `ExceptionType` repeats continuously (for example `System.UnauthorizedAccessException`) with consistent `403`/`500` codes.

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
    | summarize FirstInvocation=min(timestamp), FirstDurationMs=arg_min(timestamp, toreal(duration / 1ms)) by bin(timestamp, 15m)
) on timestamp
| order by timestamp desc
```

**Example result:**

| timestamp | StartupEvents | FirstInvocation | FirstDurationMs |
|---|---|---|---|
| 2026-04-04T09:00:00Z | 3 | 2026-04-04T09:00:24Z | 00:00:06.842 |
| 2026-04-04T08:45:00Z | 1 | 2026-04-04T08:45:02Z | 00:00:00.412 |
| 2026-04-04T08:30:00Z | 4 | 2026-04-04T08:30:31Z | 00:00:08.901 |

**How to interpret:**

| Indicator | Normal | Warning | Critical |
|---|---|---|---|
| StartupEvents per 15m bin | 0-1 | 2 | >= 3 |
| FirstDurationMs after startup | < 1000ms | 1000-5000ms | > 5000ms |
| Startup-to-first-invocation gap | < 5s | 5-20s | > 20s |

!!! note "Normal vs abnormal"
    **Normal:** One startup event and first invocation under 1 second.

    **Abnormal:** Multiple startup events plus first invocation over 5 seconds indicates cold start pressure or host recycling.

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

**Example result:**

| target | type | Calls | Failed | FailureRatePercent | P95Ms |
|---|---|---|---|---|---|
| api.contoso.internal | HTTP | 6,140 | 1,248 | 20.33 | 4,920 |
| stfuncprod.queue.core.windows.net | Azure queue | 8,022 | 12 | 0.15 | 182 |
| sql-prod.contoso.database.windows.net | SQL | 3,104 | 4 | 0.13 | 275 |

**How to interpret:**

| Indicator | Normal | Warning | Critical |
|---|---|---|---|
| Dependency failure rate | < 0.5% | 0.5-2% | > 2% |
| Dependency P95Ms | < 300ms | 300-1000ms | > 1000ms |
| Failed calls concentration by target | No single target > 30% | One target 30-60% | One target > 60% |

!!! note "Normal vs abnormal"
    **Normal:** Failures are sparse across multiple targets with low latency.

    **Abnormal:** A single target has both high failure rate and high latency. Treat that target as the primary blast radius source.

## 5) Queue processing latency

!!! warning "Custom instrumentation required"
    The following queue metrics (`QueueMessageAgeMs`, `QueueProcessingLatencyMs`, `QueueDequeueDelayMs`) are **not** emitted by the Azure Functions runtime by default. Your application must explicitly emit these using `TelemetryClient.TrackMetric()` (C#) or the OpenTelemetry SDK. If you have not added custom instrumentation, these queries will return empty results. For built-in queue monitoring, use Azure Storage metrics via `az monitor metrics list`.

```kusto
let appName = "func-myapp-prod";
customMetrics
| where timestamp > ago(2h)
| where cloud_RoleName =~ appName
| where name in ("QueueMessageAgeMs", "QueueProcessingLatencyMs", "QueueDequeueDelayMs")
| summarize AvgMs=avg(value), P95Ms=percentile(value, 95), MaxMs=max(value) by MetricName=name, bin(timestamp, 5m)
| order by timestamp desc
```

**Example result:**

| MetricName | timestamp | AvgMs | P95Ms | MaxMs |
|---|---|---|---|---|
| QueueProcessingLatencyMs | 2026-04-04T09:10:00Z | 420 | 860 | 1,430 |
| QueueProcessingLatencyMs | 2026-04-04T09:05:00Z | 5,220 | 12,480 | 28,200 |
| QueueMessageAgeMs | 2026-04-04T09:05:00Z | 41,800 | 79,200 | 124,000 |
| QueueDequeueDelayMs | 2026-04-04T09:05:00Z | 3,880 | 7,120 | 11,340 |

**How to interpret:**

| Indicator | Normal | Warning | Critical |
|---|---|---|---|
| QueueProcessingLatencyMs Avg | < 1000ms | 1000-5000ms | > 5000ms |
| QueueMessageAgeMs P95 | < 10000ms | 10000-60000ms | > 60000ms |
| QueueDequeueDelayMs Avg | < 500ms | 500-2000ms | > 2000ms |

!!! note "Normal vs abnormal"
    **Normal:** `AvgMs` and `P95Ms` move together at low values.

    **Abnormal:** Short-window spike where `QueueMessageAgeMs` and `QueueProcessingLatencyMs` jump together indicates throughput collapse or scaling lag.

## 6) Exception trends

```kusto
let appName = "func-myapp-prod";
exceptions
| where timestamp > ago(24h)
| where cloud_RoleName =~ appName
| summarize Count=count() by bin(timestamp, 15m), type
| order by timestamp desc
```

**Example result:**

| timestamp | type | Count |
|---|---|---|
| 2026-04-04T09:00:00Z | Azure.RequestFailedException | 3 |
| 2026-04-04T09:15:00Z | Azure.RequestFailedException | 5 |
| 2026-04-04T09:30:00Z | Azure.RequestFailedException | 96 |
| 2026-04-04T09:45:00Z | Azure.RequestFailedException | 118 |
| 2026-04-04T09:45:00Z | System.TimeoutException | 12 |

**How to interpret:**

| Indicator | Normal | Warning | Critical |
|---|---|---|---|
| Exception Count per 15m bin | 0-5 | 6-25 | > 25 |
| Dominant exception type share | < 40% | 40-70% | > 70% |
| Spike slope (current bin vs previous) | < 2x | 2-4x | > 4x |

!!! note "Normal vs abnormal"
    **Normal:** Low, noisy background exceptions without sustained growth.

    **Abnormal:** Sudden multi-bin spike in one exception type signals a regression window. Correlate with deployment and configuration changes.

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

**Example result:**

| timestamp | severityLevel | message |
|---|---|---|
| 2026-04-04T09:20:44Z | 1 | Scaling out worker count from 2 to 4 based on queue pressure. |
| 2026-04-04T09:20:47Z | 1 | New instance allocated: instanceId=rd0003ffxxxx. |
| 2026-04-04T09:21:13Z | 2 | Drain mode enabled for instance rd0003aaxxxx before recycle. |
| 2026-04-04T09:21:42Z | 1 | Concurrency manager increased max concurrent invocations to 32. |

**How to interpret:**

| Indicator | Normal | Warning | Critical |
|---|---|---|---|
| Scale events under sustained load | Present | Delayed | Missing |
| New instance allocation after scale out command | < 60s | 60-180s | > 180s |
| Frequent drain/recycle messages | Rare | Intermittent | Continuous |

!!! note "Normal vs abnormal"
    **Normal:** `Scaling out` followed by `New instance allocated` and then stable processing.

    **Abnormal:** Repeated `Drain mode` and recycle logs without sustained capacity growth indicate unstable workers or platform constraints.

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

**Example result:**

| timestamp | severityLevel | message | Pattern |
|---|---|---|---|
| 2026-04-04T09:00:12Z | 1 | Host started (284ms) | Healthy |
| 2026-04-04T08:58:31Z | 2 | Host is shutting down | Unhealthy cycle |
| 2026-04-04T08:58:24Z | 1 | Job host started | Unhealthy cycle |
| 2026-04-04T08:57:52Z | 2 | Stopping JobHost | Unhealthy cycle |

**How to interpret:**

| Indicator | Normal | Warning | Critical |
|---|---|---|---|
| Host start count per hour | 1-2 | 3-5 | > 5 |
| Start-stop cycle interval | N/A | 10-30m | < 10m |
| Shutdown messages with errors nearby | None | Occasional | Repeated |

!!! note "Normal vs abnormal"
    **Normal:** One startup event after deployment or planned restart.

    **Abnormal:** Repeated startup/shutdown cycling in short intervals usually indicates crash loops, configuration churn, or failing dependencies.

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

**Example result:**

| timestamp | itemType | name | success | resultCode | duration | details |
|---|---|---|---|---|---|---|
| 2026-04-04T09:10:40.101Z | request | Functions.HttpTrigger | false | 500 | 00:00:07.511 | https://func-myapp-prod.azurewebsites.net/api/orders |
| 2026-04-04T09:10:40.414Z | dependency | api.contoso.internal | false | 403 | 00:00:02.103 | POST /v1/orders/validate |
| 2026-04-04T09:10:42.622Z | exception | Azure.RequestFailedException | false |  |  | Status: 403 (Forbidden). Managed identity lacks role assignment. |
| 2026-04-04T09:10:42.781Z | trace | trace | true |  |  | Retry attempt 1 of 3 for outbound validation call. |
| 2026-04-04T09:10:47.612Z | trace | trace | true |  |  | Invocation failed and message moved to poison queue after retries. |

**How to interpret:**

| Indicator | Normal | Warning | Critical |
|---|---|---|---|
| request -> dependency -> trace sequence | Complete and successful | Complete with retries | Broken by exception/failure |
| First failing component in timeline | None | Delayed dependency | Immediate dependency/auth failure |
| Total invocation timeline | < 1000ms | 1000-5000ms | > 5000ms |

!!! note "Normal vs abnormal"
    **Normal:** Request and dependencies succeed, no exception event, short timeline.

    **Abnormal:** Request failure follows dependency `403` and exception record in the same `operation_Id`, proving downstream auth or connectivity as root cause.

## See Also

- [First 10 Minutes](first-10-minutes.md)
- [Playbooks](playbooks.md)
- [Methodology](methodology.md)
- [Azure Monitor Logs query overview](https://learn.microsoft.com/azure/azure-monitor/logs/log-query-overview)
- [Application Insights data model](https://learn.microsoft.com/azure/azure-monitor/app/data-model)

## References

- [Kusto Query Language overview](https://learn.microsoft.com/azure/data-explorer/kusto/query/)
- [Application Insights telemetry data model](https://learn.microsoft.com/azure/azure-monitor/app/data-model-complete)
- [Monitor Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-monitoring)
