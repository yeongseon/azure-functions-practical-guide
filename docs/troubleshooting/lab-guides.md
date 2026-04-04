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

## 2) Storage access failure lab

- **Scenario:** Triggers stop processing due to storage authentication or connectivity issues.
- **What you practice:** Identifying storage-related host errors, validating identity-based access, and restoring trigger listeners safely.
- **Signals to watch:** host listener errors, authorization failures, trigger execution drop.
- **Lab guide:** [storage-access-failure](https://github.com/yeongseon/azure-functions/tree/main/labs/storage-access-failure)

## 3) Queue backlog scaling lab

- **Scenario:** Queue depth grows faster than processing throughput.
- **What you practice:** Backlog triage, poison-message identification, scale bottleneck analysis, and throughput recovery.
- **Signals to watch:** queue length, queue message age, invocation rate, retry patterns.
- **Lab guide:** [queue-backlog-scaling](https://github.com/yeongseon/azure-functions/tree/main/labs/queue-backlog-scaling)

## 4) DNS and VNet resolution lab

- **Scenario:** Function app cannot resolve or reach private dependencies after network changes.
- **What you practice:** Diagnosing DNS path issues, VNet integration checks, and dependency-call verification.
- **Signals to watch:** dependency timeout spikes, name resolution errors, network-related exceptions.
- **Lab guide:** [dns-vnet-resolution](https://github.com/yeongseon/azure-functions/tree/main/labs/dns-vnet-resolution)

## 5) Managed identity authentication lab

- **Scenario:** Managed identity calls fail after RBAC or scope changes.
- **What you practice:** Verifying principal identity, role assignments, propagation delays, and least-privilege correction.
- **Signals to watch:** `403`/`AuthorizationFailed`, dependency failures, exception trends.
- **Lab guide:** [managed-identity-auth](https://github.com/yeongseon/azure-functions/tree/main/labs/managed-identity-auth)

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

## See Also

- [First 10 Minutes](first-10-minutes.md)
- [Playbooks](playbooks.md)
- [Methodology](methodology.md)
- [KQL Query Library](kql.md)
- [Azure Functions reliability guidance](https://learn.microsoft.com/azure/azure-functions/functions-best-practices)
