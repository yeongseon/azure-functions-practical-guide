# Scaling Queries

KQL queries for analyzing cold starts, scaling behavior, and host lifecycle events.

## Cold start analysis

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
| 2026-04-04T11:30:00Z | 83 | 2026-04-04T11:30:00.003Z | 3.0249 |
| 2026-04-04T11:15:00Z | 19 | 2026-04-04T11:29:25.000Z | 1600.4633 |

**How to interpret:**

| Indicator | Normal | Warning | Critical |
|---|---|---|---|
| StartupEvents per 15m bin | Consistent with plan type (FC1: dozens per bin is normal; Y1/EP: 1-3 per bin) | Sudden spike vs baseline (for example 10x normal) | Startup events with no subsequent successful invocations |
| FirstDurationMs after startup | < 1000ms | 1000-5000ms | > 5000ms |
| Startup-to-first-invocation gap | < 5s | 5-20s | > 20s |

!!! tip "FC1 Flex Consumption"
    Flex Consumption plans scale by spinning up many worker instances rapidly. Seeing 50-100+ startup events in a 15-minute bin is normal under load. Focus on whether startup events correlate with successful invocations, not the raw count.

!!! note "Normal vs abnormal"
    **Normal:** One startup event and first invocation under 1 second.

    **Abnormal:** Multiple startup events plus first invocation over 5 seconds indicates cold start pressure or host recycling.

## Scaling events timeline

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
| 2026-04-04T11:32:20Z | 1 | Worker process started and initialized. |
| 2026-04-04T11:31:50Z | 1 | Worker process started and initialized. |
| 2026-04-04T11:31:20Z | 1 | Worker process started and initialized. |
| 2026-04-04T11:30:50Z | 1 | Worker process started and initialized. |

**How to interpret:**

| Indicator | Normal | Warning | Critical |
|---|---|---|---|
| Scale events under sustained load | Present | Delayed | Missing |
| New instance allocation after scale out command | < 60s | 60-180s | > 180s |
| Frequent drain/recycle messages | Rare | Intermittent | Continuous |

!!! note "Normal vs abnormal"
    **Normal:** `Scaling out` followed by `New instance allocated` and then stable processing.

    **Abnormal:** Repeated `Drain mode` and recycle logs without sustained capacity growth indicate unstable workers or platform constraints.

## Host startup/shutdown events

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
| 2026-04-04T11:36:20Z | 1 | Host lock lease acquired by instance ID 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' | Healthy |
| 2026-04-04T11:32:30Z | 1 | Host started (64ms) | Healthy |
| 2026-04-04T11:32:30Z | 1 | Job host started | Healthy |
| 2026-04-04T11:32:30Z | 1 | Starting Host (HostId=func-myapp-prod, Version=4.1047.100.26071, InstanceId=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx) | Healthy |

**How to interpret:**

| Indicator | Normal | Warning | Critical |
|---|---|---|---|
| Host start count per hour | 1-2 | 3-5 | > 5 |
| Start-stop cycle interval | N/A | 10-30m | < 10m |
| Shutdown messages with errors nearby | None | Occasional | Repeated |
| Multiple `Host started` entries in short succession on FC1 | Normal scaling behavior | Review only if accompanied by error bursts | Persistent restarts with failures and no successful invocations |

!!! note "Normal vs abnormal"
    **Normal:** One startup event after deployment or planned restart.

    **Abnormal:** Repeated startup/shutdown cycling in short intervals usually indicates crash loops, configuration churn, or failing dependencies.

## Instance count over time

```kusto
let appName = "func-myapp-prod";
traces
| where timestamp > ago(6h)
| where cloud_RoleName =~ appName
| where message has "Host started"
| summarize InstanceCount = dcount(cloud_RoleInstance) by bin(timestamp, 5m)
| order by timestamp asc
```

**How to interpret:**

| Indicator | Normal | Warning | Critical |
|---|---|---|---|
| Instance count under load | Scales proportionally to demand | Flat despite rising backlog | Zero (all instances crashed) |
| Instance count after load subsides | Scales in gradually | Remains over-provisioned | Oscillates rapidly |

## See Also

- [Execution Queries](../execution/index.md)
- [Dependency Queries](../dependencies/index.md)
- [Correlation Queries](../correlation/index.md)
- [KQL Query Library](../index.md)

## Sources

- [Azure Functions scale and hosting](https://learn.microsoft.com/azure/azure-functions/functions-scale)
- [Monitor Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-monitoring)
