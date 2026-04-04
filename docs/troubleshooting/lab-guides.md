# Troubleshooting Lab Guides

These labs let you practice incident response on reproducible Azure Functions failure scenarios.
Run labs in a non-production environment and treat them like live incidents: detect, triage, diagnose, fix, and verify.

## How to use this page

1. Pick a scenario that matches your current operational risk.
2. Run the lab using its README instructions.
3. Use [First 10 Minutes](first-10-minutes.md), [Playbooks](playbooks.md), and [KQL](kql.md) while troubleshooting.
4. Record findings as team runbook updates.

!!! tip "Operations Guide"
    For monitoring setup and alert configuration, see [Monitoring](../operations/monitoring.md) and [Alerts](../operations/alerts.md).

## Lab catalog

## 1) Cold start lab

- **Scenario:** Function app shows elevated first-request latency after idle periods.
- **What you practice:** Distinguishing cold start from dependency latency, validating startup traces, and choosing mitigation paths by hosting plan.
- **Signals to watch:** startup traces, p95 latency, first-invocation duration.
- **Lab guide:** [cold-start](https://github.com/yeongseon/azure-functions/tree/main/labs/cold-start)

### Expected evidence timeline

| Phase | What Happens | Evidence to Collect | Where to Look |
|---|---|---|---|
| Before trigger | Healthy baseline after warm period | Stable `requests` latency (p95 < 500ms), no startup churn | `requests`, `traces` |
| During incident | App receives first request after idle; cold initialization occurs | `Host started (Xms)` appears, first invocation duration spikes in same window | `traces`, `requests` |
| After recovery | Host is warm and responses normalize | Next invocations return to low latency; startup event frequency drops | `requests`, `traces` |

### Key log patterns to recognize

**During incident you should see:**

```text
[2026-04-04T09:00:12Z] Host started (6842ms)
[2026-04-04T09:00:24Z] Executing 'Functions.HttpTrigger' (Reason='This function was programmatically called via the host APIs.')
```

**After recovery you should see:**

```text
[2026-04-04T09:05:03Z] Executed 'Functions.HttpTrigger' (Succeeded, Duration=312ms)
[2026-04-04T09:05:09Z] Executed 'Functions.HttpTrigger' (Succeeded, Duration=287ms)
```

### Why this proves the hypothesis

If `Host started` exceeds 5000ms and aligns with first-invocation latency spikes in the same time bin, cold start is confirmed. If host start time is low while latency remains high, investigate dependencies instead.

**Related playbook**: [Playbook: High latency / slow responses](playbooks.md#high-latency--slow-responses)

**Related playbook**: [Playbook: Deployment failures](playbooks.md#deployment-failures)

## 2) Storage access failure lab

- **Scenario:** Triggers stop processing due to storage authentication or connectivity issues.
- **What you practice:** Identifying storage-related host errors, validating identity-based access, and restoring trigger listeners safely.
- **Signals to watch:** host listener errors, authorization failures, trigger execution drop.
- **Lab guide:** [storage-access-failure](https://github.com/yeongseon/azure-functions/tree/main/labs/storage-access-failure)

### Expected evidence timeline

| Phase | What Happens | Evidence to Collect | Where to Look |
|---|---|---|---|
| Before trigger | Listeners initialize normally | Host startup succeeds, queue/blob listeners report started | `traces` |
| During incident | Storage access denied | `(403) Forbidden`, listener startup failures, invocation count drops | `traces`, `requests`, `exceptions` |
| After recovery | Access restored and trigger pipeline resumes | Listener starts cleanly, function executions return, error rate returns to zero | `traces`, `requests` |

### Key log patterns to recognize

**During incident you should see:**

```text
[2026-04-04T09:10:41Z] Storage operation failed: (403) Forbidden
[2026-04-04T09:10:42Z] Listener for 'QueueTrigger' was unable to start
```

**After recovery you should see:**

```text
[2026-04-04T09:16:08Z] Host started (234ms)
[2026-04-04T09:16:09Z] Listener started for function 'QueueProcessor'
```

### Why this proves the hypothesis

If storage `403` appears immediately after an RBAC change in the activity log and listeners fail in the same window, identity or permission drift is the direct cause.

**Related playbook**: [Playbook: Functions not executing](playbooks.md#functions-not-executing)

**Related playbook**: [Playbook: Functions failing with errors](playbooks.md#functions-failing-with-errors)

## 3) Queue backlog scaling lab

- **Scenario:** Queue depth grows faster than processing throughput.
- **What you practice:** Backlog triage, poison-message identification, scale bottleneck analysis, and throughput recovery.
- **Signals to watch:** queue length, queue message age, invocation rate, retry patterns.
- **Lab guide:** [queue-backlog-scaling](https://github.com/yeongseon/azure-functions/tree/main/labs/queue-backlog-scaling)

!!! warning "Custom instrumentation required"
    Queue processing metrics (`QueueMessageAgeMs`, `QueueProcessingLatencyMs`) are not emitted by the Azure Functions runtime by default. These queries require your application to explicitly emit custom metrics. For built-in queue monitoring, use Azure Storage metrics via Azure Monitor.

### Expected evidence timeline

| Phase | What Happens | Evidence to Collect | Where to Look |
|---|---|---|---|
| Before trigger | Throughput matches ingest rate | Queue depth stable, low message age, steady execution count | `Azure Monitor metrics`, `requests` |
| During incident | Backlog grows faster than processing | `QueueMessageCount` rises while `FunctionExecutionCount` stays flat/low | `Azure Monitor metrics`, `traces` |
| After recovery | Scaling or optimization catches up | Queue depth and message age trend down, execution count increases | `Azure Monitor metrics`, `requests` |

### Key log patterns to recognize

**During incident you should see:**

```text
[2026-04-04T09:21:10Z] QueueMessageCount=18240, QueueMessageAgeMsP95=74200
[2026-04-04T09:21:11Z] FunctionExecutionCount=42 (unchanged over last 5m)
```

**After recovery you should see:**

```text
[2026-04-04T09:34:02Z] Scaling out worker count from 2 to 6
[2026-04-04T09:39:11Z] QueueMessageCount=3200, QueueMessageAgeMsP95=8900
```

### Why this proves the hypothesis

If queue depth grows while execution count is capped, either scale limits are reached or per-message work became slow. The metric divergence is the evidence chain for throughput bottlenecks.

**Related playbook**: [Playbook: Queue messages piling up](playbooks.md#queue-messages-piling-up)

## 4) DNS and VNet resolution lab

- **Scenario:** Function app cannot resolve or reach private dependencies after network changes.
- **What you practice:** Diagnosing DNS path issues, VNet integration checks, and dependency-call verification.
- **Signals to watch:** dependency timeout spikes, name resolution errors, network-related exceptions.
- **Lab guide:** [dns-vnet-resolution](https://github.com/yeongseon/azure-functions/tree/main/labs/dns-vnet-resolution)

### Expected evidence timeline

| Phase | What Happens | Evidence to Collect | Where to Look |
|---|---|---|---|
| Before trigger | Dependency resolution works from function subnet | Successful dependency calls, low DNS latency | `dependencies`, `requests` |
| During incident | Name resolution breaks after network change | `getaddrinfo ENOTFOUND`, DNS timeout errors, dependency failures | `dependencies`, `exceptions`, `traces` |
| After recovery | DNS zone/link fixed and resolution restored | Dependency success returns, timeout and ENOTFOUND disappear | `dependencies`, `requests` |

### Key log patterns to recognize

**During incident you should see:**

```text
[2026-04-04T09:08:52Z] getaddrinfo ENOTFOUND api.internal.contoso
[2026-04-04T09:08:53Z] DNS resolution timeout for api.internal.contoso:53
```

**After recovery you should see:**

```text
[2026-04-04T09:18:14Z] DNS resolution succeeded for api.internal.contoso -> 10.20.1.14
[2026-04-04T09:18:15Z] Dependency call succeeded: api.internal.contoso (200)
```

### Why this proves the hypothesis

If failures occur only from the function subnet and a private DNS zone link is missing or misconfigured, DNS resolution failure is confirmed as the root cause instead of application code defects.

**Related playbook**: [Playbook: Functions failing with errors](playbooks.md#functions-failing-with-errors)

**Related playbook**: [Playbook: Blob trigger not firing](playbooks.md#blob-trigger-not-firing)

## 5) Managed identity authentication lab

- **Scenario:** Managed identity calls fail after RBAC or scope changes.
- **What you practice:** Verifying principal identity, role assignments, propagation delays, and least-privilege correction.
- **Signals to watch:** `403`/`AuthorizationFailed`, dependency failures, exception trends.
- **Lab guide:** [managed-identity-auth](https://github.com/yeongseon/azure-functions/tree/main/labs/managed-identity-auth)

### Expected evidence timeline

| Phase | What Happens | Evidence to Collect | Where to Look |
|---|---|---|---|
| Before trigger | Managed identity has valid role assignments | Dependency calls succeed; no auth exceptions | `dependencies`, `exceptions` |
| During incident | RBAC scope/role changes break authorization | `AuthorizationFailed`, dependency `403`, failures surge | `exceptions`, `dependencies`, activity log |
| After recovery | Correct role restored and propagation completes | `403` drops to zero, success rate recovers | `dependencies`, `requests`, `exceptions` |

### Key log patterns to recognize

**During incident you should see:**

```text
[2026-04-04T09:12:10Z] AuthorizationFailed: The client '<object-id>' does not have authorization to perform action
[2026-04-04T09:12:11Z] Dependency response: 403 Forbidden from https://storage.azure.com/
```

**After recovery you should see:**

```text
[2026-04-04T09:20:42Z] Role assignment update detected for principal <object-id>
[2026-04-04T09:21:03Z] Dependency response: 200 OK from https://storage.azure.com/
```

### Why this proves the hypothesis

If role assignment removal or scope change aligns with onset of `AuthorizationFailed` and dependency `403`, the outage is RBAC-driven. Recovery after role restoration confirms identity path correctness.

**Related playbook**: [Playbook: Functions failing with errors](playbooks.md#functions-failing-with-errors)

## Recommended learning sequence

Start with broad reliability issues, then move into specialized scenarios:

1. [cold-start](https://github.com/yeongseon/azure-functions/tree/main/labs/cold-start)
2. [queue-backlog-scaling](https://github.com/yeongseon/azure-functions/tree/main/labs/queue-backlog-scaling)
3. [storage-access-failure](https://github.com/yeongseon/azure-functions/tree/main/labs/storage-access-failure)
4. [managed-identity-auth](https://github.com/yeongseon/azure-functions/tree/main/labs/managed-identity-auth)
5. [dns-vnet-resolution](https://github.com/yeongseon/azure-functions/tree/main/labs/dns-vnet-resolution)

## Practice checklist

For each lab, confirm your team can do all of the following without guesswork:

- Detect the issue from alerts or dashboard anomalies.
- Execute the [First 10 Minutes](first-10-minutes.md) checklist.
- Select the right [Playbook](playbooks.md) and isolate likely causes.
- Run 2-3 focused KQL queries from [KQL Library](kql.md).
- Apply a minimal fix and verify recovery in telemetry.
- Document root cause and prevention tasks.

## Mapping labs to common production incidents

| Incident type | Best lab |
|---|---|
| Latency regression after idle periods | [cold-start](https://github.com/yeongseon/azure-functions/tree/main/labs/cold-start) |
| Trigger pipeline stalls | [storage-access-failure](https://github.com/yeongseon/azure-functions/tree/main/labs/storage-access-failure) |
| Event ingestion cannot keep up | [queue-backlog-scaling](https://github.com/yeongseon/azure-functions/tree/main/labs/queue-backlog-scaling) |
| Private endpoint dependency outages | [dns-vnet-resolution](https://github.com/yeongseon/azure-functions/tree/main/labs/dns-vnet-resolution) |
| RBAC/identity breakages | [managed-identity-auth](https://github.com/yeongseon/azure-functions/tree/main/labs/managed-identity-auth) |

## Evidence collection skills

Each lab trains specific diagnostic skills:

| Lab | Primary Skill | Secondary Skill |
|---|---|---|
| Cold start | Correlating host startup with request latency | Reading trace timeline |
| Storage access failure | Identifying auth errors in host logs | Verifying RBAC with CLI |
| Queue backlog scaling | Reading queue metrics vs execution metrics | Identifying poison message loops |
| DNS/VNet resolution | Diagnosing DNS errors in dependency calls | Verifying private DNS zone configuration |
| Managed identity auth | Tracing RBAC changes in activity log | Correlating exceptions with config changes |

## See Also

- [First 10 Minutes](first-10-minutes.md)
- [Playbooks](playbooks.md)
- [Methodology](methodology.md)
- [KQL Query Library](kql.md)
- [Azure Functions reliability guidance](https://learn.microsoft.com/azure/azure-functions/functions-best-practices)

## References

- [Azure Functions monitoring](https://learn.microsoft.com/azure/azure-functions/functions-monitoring)
- [Application Insights for Azure Functions](https://learn.microsoft.com/azure/azure-functions/configure-monitoring)
- [Troubleshoot Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-recover-from-failed-host)
