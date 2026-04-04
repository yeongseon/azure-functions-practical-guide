# Hands-on Labs

These labs let you practice incident response on reproducible Azure Functions failure scenarios.
Run labs in a non-production environment and treat them like live incidents: detect, triage, diagnose, fix, and verify.

```mermaid
graph TD
    A[Hands-on Labs] --> B[Performance]
    A --> C[Storage / Identity]
    A --> D[Network]
    B --> E[Cold Start]
    B --> F[Queue Backlog Scaling]
    C --> G[Storage Access Failure]
    C --> H[Managed Identity Auth]
    D --> I[DNS / VNet Resolution]
```

## How Labs Work

Each lab includes:

1. **Lab infrastructure** — Bicep templates and app source in `labs/` directory
2. **Documentation page** — Step-by-step walkthrough with KQL queries and expected observations
3. **Expected evidence** — Baseline, during-incident, and after-recovery evidence to validate your investigation

## Available Labs

### Performance

| Lab | Symptom | Related Playbook |
|-----|---------|-----------------|
| [Cold Start](cold-start.md) | Elevated first-request latency after idle periods | [High Latency / Slow Responses](../playbooks/high-latency.md) |
| [Queue Backlog Scaling](queue-backlog-scaling.md) | Queue depth grows faster than processing throughput | [Queue Messages Piling Up](../playbooks/queue-piling-up.md) |

### Storage / Identity

| Lab | Symptom | Related Playbook |
|-----|---------|-----------------|
| [Storage Access Failure](storage-access-failure.md) | Triggers stop processing due to storage auth or connectivity issues | [Functions Not Executing](../playbooks/functions-not-executing.md) |
| [Managed Identity Auth](managed-identity-auth.md) | Managed identity calls fail after RBAC or scope changes | [Functions Failing with Errors](../playbooks/functions-failing.md) |

### Network

| Lab | Symptom | Related Playbook |
|-----|---------|-----------------|
| [DNS / VNet Resolution](dns-vnet-resolution.md) | Function app cannot resolve or reach private dependencies | [Blob Trigger Not Firing](../playbooks/blob-trigger-not-firing.md) |

## Prerequisites

All labs require:

- Azure subscription with Contributor access
- Azure CLI installed and logged in (`az login`)
- Bash shell (Linux, macOS, or WSL)

## General Workflow

```bash
# 1. Create resource group
az group create --name rg-lab-<name> --location koreacentral

# 2. Deploy infrastructure
az deployment group create \
  --resource-group rg-lab-<name> \
  --template-file labs/<name>/main.bicep \
  --parameters baseName=lab<short>

# 3. Deploy app code (zip deploy)
# 4. Trigger the failure scenario
# 5. Wait 2-5 minutes for logs to appear
# 6. Investigate using playbooks and KQL queries

# 7. Clean up
az group delete --name rg-lab-<name> --yes --no-wait
```

!!! warning "Cost"
    Each lab deploys Azure Functions resources. Delete the resource group after completing the lab to avoid ongoing charges.

## Recommended Learning Sequence

Start with broad reliability issues, then move into specialized scenarios:

1. [Cold Start](cold-start.md) — Understand cold start vs dependency latency
2. [Queue Backlog Scaling](queue-backlog-scaling.md) — Backlog triage and throughput analysis
3. [Storage Access Failure](storage-access-failure.md) — Storage auth and host errors
4. [Managed Identity Auth](managed-identity-auth.md) — RBAC and identity troubleshooting
5. [DNS / VNet Resolution](dns-vnet-resolution.md) — Network path and DNS diagnosis

## Practice Checklist

For each lab, confirm your team can do all of the following without guesswork:

- Detect the issue from alerts or dashboard anomalies.
- Execute the [First 10 Minutes](../first-10-minutes.md) checklist.
- Select the right [Playbook](../playbooks/index.md) and isolate likely causes.
- Run 2-3 focused KQL queries from [KQL Library](../kql.md).
- Apply a minimal fix and verify recovery in telemetry.
- Document root cause and prevention tasks.

## Evidence Collection Skills

Each lab trains specific diagnostic skills:

| Lab | Primary Skill | Secondary Skill |
|---|---|---|
| Cold Start | Correlating host startup with request latency | Reading trace timeline |
| Storage Access Failure | Identifying auth errors in host logs | Verifying RBAC with CLI |
| Queue Backlog Scaling | Reading queue metrics vs execution metrics | Identifying poison message loops |
| DNS / VNet Resolution | Diagnosing DNS errors in dependency calls | Verifying private DNS zone configuration |
| Managed Identity Auth | Tracing RBAC changes in activity log | Correlating exceptions with config changes |

## Mapping Labs to Common Production Incidents

| Incident type | Best lab |
|---|---|
| Latency regression after idle periods | [Cold Start](cold-start.md) |
| Trigger pipeline stalls | [Storage Access Failure](storage-access-failure.md) |
| Event ingestion cannot keep up | [Queue Backlog Scaling](queue-backlog-scaling.md) |
| Private endpoint dependency outages | [DNS / VNet Resolution](dns-vnet-resolution.md) |
| RBAC / identity breakages | [Managed Identity Auth](managed-identity-auth.md) |

## See Also

- [First 10 Minutes](../first-10-minutes.md)
- [Playbooks](../playbooks/index.md)
- [Methodology](../methodology.md)
- [KQL Query Library](../kql.md)

## Sources

- [Azure Functions monitoring](https://learn.microsoft.com/azure/azure-functions/functions-monitoring)
- [Application Insights for Azure Functions](https://learn.microsoft.com/azure/azure-functions/configure-monitoring)
- [Troubleshoot Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-recover-from-failed-host)
