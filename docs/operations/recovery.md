# Recovery

This guide covers operational recovery for Azure Functions: rollback, backup planning, and regional resilience.
It focuses on practical runbook execution for minimizing downtime and data loss.

!!! tip "Platform Guide"
    For scaling architecture and plan comparison, see [Scaling](../platform/scaling.md).

!!! tip "Language Guide"
    For Python deployment specifics, see the [Python Tutorial](../language-guides/python/tutorial/index.md).

## Recovery objectives

Define service objectives before incidents occur:

- **RTO** (Recovery Time Objective): target time to restore service.
- **RPO** (Recovery Point Objective): acceptable data loss window.

RTO and RPO determine architecture, replication, and operational tooling.

## Fast rollback strategy

For Premium and Dedicated plans, deployment slots are the fastest rollback path.

```bash
az functionapp deployment slot swap \
    --resource-group <resource-group> \
    --name <function-app-name> \
    --slot staging \
    --target-slot production
```

For plans without slot support, redeploy the last known good artifact.

## Artifact and configuration backup

Maintain these backups for every release:

- Immutable build artifact with version metadata.
- Infrastructure templates and parameter sets.
- Exported app settings baseline (with secret values protected).
- Runbook steps for redeploy and validation.

Keep backup assets in secured, versioned storage.

## Data and state resilience

Most Azure Functions apps depend on storage and messaging services for state.
Recovery depends on those services' durability configuration:

- Use geo-redundant options where business continuity requires cross-region resilience.
- Align queue/topic retention and replay capability with RPO targets.
- Protect durable workflow state with storage redundancy and backup policy.

## Regional recovery planning

Region-level recovery usually requires pre-provisioned secondary environment.

Recommended pattern:

1. Provision primary and secondary environments with infrastructure as code.
2. Replicate critical configuration and secrets strategy.
3. Use traffic management or DNS failover process.
4. Exercise failover and failback drills on a schedule.

## Health-based decision gates

Before failover or rollback, validate:

- Current incident scope (app-only or dependency-wide).
- Secondary environment readiness.
- Data consistency and queue lag status.
- Alert suppression or rerouting during controlled switch.

## Post-recovery validation

After recovery action:

- Confirm health endpoint and key user journeys.
- Verify failure rate and latency return to baseline.
- Validate message processing catch-up.
- Re-enable normal alert thresholds and dashboards.

## Recovery drill checklist

- Documented owner and escalation path.
- Tested rollback command set.
- Tested region failover procedure.
- Measured achieved RTO/RPO versus targets.
- Action items tracked for gaps found during drill.

## See Also

- [Deployment](deployment.md)
- [Alerts](alerts.md)
- [Troubleshooting Methodology](../troubleshooting/methodology.md)

## Sources

- [Reliability in Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-best-practices)
- [Business continuity and disaster recovery for Azure applications](https://learn.microsoft.com/azure/architecture/framework/resiliency/disaster-recovery)
- [Azure Storage redundancy options](https://learn.microsoft.com/azure/storage/common/storage-redundancy)
- [Deployment slots in Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-deployment-slots)
