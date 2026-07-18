---
content_sources:
  references:
    - type: self-generated
      justification: Auto-generated dashboard tracking content validation status
---

# Content Validation Status

This page tracks `content_validation` metadata for **in-scope factual-claim documents** under `docs/best-practices/`, `docs/operations/`, `docs/platform/`, `docs/troubleshooting/`. Pages outside this scope — navigation indexes (`docs/best-practices/index.md`, `docs/operations/index.md`, `docs/platform/index.md`, `docs/troubleshooting/first-10-minutes/index.md`, `docs/troubleshooting/index.md`, `docs/troubleshooting/playbooks/index.md`), reference-lookup KQL packs and lab guides (`docs/troubleshooting/kql/`, `docs/troubleshooting/lab-guides/`), tutorials, language guides, and start-here landing pages — are not counted here, even when legacy `content_validation` blocks exist on them (the cleanup tool removes those blocks; see `scripts/remove_out_of_scope_validation.py`). See `AGENTS.md` §Text Content Validation for the full policy and `scripts/lib/content_scope.py` for the executable scope definition.

## Summary

*Generated: 2026-07-18*

| Content Type | Total | Verified | Pending | Unverified | No Metadata |
|---|---:|---:|---:|---:|---:|
| Mermaid Diagrams | 566 | 566 | 0 | 0 | 0 |
| In-Scope Factual-Claim Documents | 64 | 64 | 0 | 0 | 0 |

!!! success "All In-Scope Documents Verified"
    Every in-scope factual-claim document has verified Microsoft Learn sources for its core claims.

<!-- diagram-id: content-validation-status-pie -->
```mermaid
pie title In-Scope Document Validation Status
    "Verified" : 64
```

## By Section

### Platform

| Document | Has Sources | Status | Claims | Last Reviewed |
|---|---|---|---|---|
| [Custom Handlers](../platform/custom-handlers.md) | ✅ | ✅ Verified | 4/4 | 2026-07-17 |
| [Deployment Scenarios](../platform/deployment-scenarios.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Durable Functions](../platform/durable-functions.md) | ✅ | ✅ Verified | 5/5 | 2026-07-05 |
| [Fixed Outbound Nat](../platform/networking-scenarios/fixed-outbound-nat.md) | ✅ | ✅ Verified | 3/3 | 2026-04-12 |
| [Functions Vs App Service](../platform/functions-vs-app-service.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Hosting](../platform/hosting.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Index](../platform/architecture/index.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Index](../platform/networking-scenarios/index.md) | ✅ | ✅ Verified | 3/3 | 2026-05-21 |
| [Networking](../platform/networking.md) | ✅ | ✅ Verified | 3/3 | 2026-04-12 |
| [Private Egress](../platform/networking-scenarios/private-egress.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Private Ingress](../platform/networking-scenarios/private-ingress.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Public Only](../platform/networking-scenarios/public-only.md) | ✅ | ✅ Verified | 3/3 | 2026-04-12 |
| [Reliability](../platform/reliability.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Scaling](../platform/scaling.md) | ✅ | ✅ Verified | 3/3 | 2026-04-12 |
| [Security](../platform/security.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Storage Connectivity](../platform/storage-connectivity.md) | ✅ | ✅ Verified | 5/5 | 2026-07-16 |
| [Storage Service Endpoint](../platform/networking-scenarios/storage-service-endpoint.md) | ✅ | ✅ Verified | 4/4 | 2026-07-16 |
| [Triggers And Bindings](../platform/triggers-and-bindings.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |

### Best Practices

| Document | Has Sources | Status | Claims | Last Reviewed |
|---|---|---|---|---|
| [Common Anti Patterns](../best-practices/common-anti-patterns.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Cost Optimization](../best-practices/cost-optimization.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Deployment](../best-practices/deployment.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Hosting Plan Selection](../best-practices/hosting-plan-selection.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Networking](../best-practices/networking.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Reliability](../best-practices/reliability.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Scaling](../best-practices/scaling.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Security](../best-practices/security.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Testing](../best-practices/testing.md) | ✅ | ✅ Verified | 4/4 | 2026-07-18 |
| [Trigger And Binding](../best-practices/trigger-and-binding.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |

### Operations

| Document | Has Sources | Status | Claims | Last Reviewed |
|---|---|---|---|---|
| [Alerts](../operations/alerts.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Cold Start](../operations/cold-start.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Configuration](../operations/configuration.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Cost Optimization](../operations/cost-optimization.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Deployment](../operations/deployment.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Migration](../operations/migration.md) | ✅ | ✅ Verified | 5/5 | 2026-07-18 |
| [Monitoring](../operations/monitoring.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Opentelemetry](../operations/opentelemetry.md) | ✅ | ✅ Verified | 4/4 | 2026-07-17 |
| [Recovery](../operations/recovery.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Retries And Poison Handling](../operations/retries-and-poison-handling.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |
| [Security](../operations/security.md) | ✅ | ✅ Verified | 4/4 | 2026-04-12 |

### Troubleshooting

| Document | Has Sources | Status | Claims | Last Reviewed |
|---|---|---|---|---|
| [App Settings Misconfiguration](../troubleshooting/playbooks/auth-config/app-settings-misconfiguration.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Architecture](../troubleshooting/architecture.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Architecture Overview](../troubleshooting/architecture-overview.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Blob Trigger Not Firing](../troubleshooting/playbooks/blob-trigger-not-firing.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Decision Tree](../troubleshooting/decision-tree.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Deployment Failures](../troubleshooting/playbooks/deployment-failures.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Detector Map](../troubleshooting/methodology/detector-map.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Durable Orchestration Stuck](../troubleshooting/playbooks/scaling/durable-orchestration-stuck.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Event Hub Service Bus Lag](../troubleshooting/playbooks/triggers/event-hub-service-bus-lag.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Evidence Map](../troubleshooting/evidence-map.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Flex Consumption Deployment](../troubleshooting/playbooks/flex-consumption-deployment.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Functions Failing](../troubleshooting/playbooks/functions-failing.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Functions Not Executing](../troubleshooting/playbooks/functions-not-executing.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [High Latency](../troubleshooting/first-10-minutes/high-latency.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [High Latency](../troubleshooting/playbooks/high-latency.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Managed Identity Rbac Failure](../troubleshooting/playbooks/auth-config/managed-identity-rbac-failure.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Mental Model](../troubleshooting/mental-model.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Methodology](../troubleshooting/methodology.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Out Of Memory Worker Crash](../troubleshooting/playbooks/scaling/out-of-memory-worker-crash.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Queue Piling Up](../troubleshooting/playbooks/queue-piling-up.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Quick Diagnosis Cards](../troubleshooting/quick-diagnosis-cards.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Scaling Issues](../troubleshooting/first-10-minutes/scaling-issues.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Timeout Execution Limit](../troubleshooting/playbooks/triggers/timeout-execution-limit.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Triggers Not Firing](../troubleshooting/first-10-minutes/triggers-not-firing.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |
| [Troubleshooting Method](../troubleshooting/methodology/troubleshooting-method.md) | ✅ | ✅ Verified | 1/1 | 2026-04-12 |

## Validation Categories

### Source Types

| Type | Description | Allowed? |
|---|---|---|
| `mslearn` | Content directly from or based on Microsoft Learn | Yes |
| `mslearn-adapted` | Microsoft Learn content adapted for this guide | Yes, with source URL |
| `self-generated` | Original content created for this guide | Requires justification |
| `community` | From community sources | Not for core content |
| `unknown` | Source not documented | Must be validated |

### Validation Status

| Status | Description |
|---|---|
| `verified` | All core claims traced to Microsoft Learn sources |
| `pending_review` | Document exists but claims need source verification |
| `unverified` | New document, no validation performed |

## How to Add Validation

Before adding metadata, confirm the page is in scope. The block is required ONLY for factual-claim pages under `docs/platform/`, `docs/best-practices/`, `docs/operations/`, and `docs/troubleshooting/` (excluding `troubleshooting/kql/`, `troubleshooting/lab-guides/`, and navigation landing pages listed in `scripts/lib/content_scope.NAVIGATION_INDEXES`).

For an in-scope page, add a `content_validation` block to its frontmatter:

```yaml
---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/...
content_validation:
  status: verified
  last_reviewed: 2026-04-12
  reviewer: agent
  core_claims:
    - claim: "Flex Consumption supports VNet integration with regional VNet."
      source: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
      verified: true
---
```

Each `core_claim` MUST be a verifiable factual assertion about Azure Functions behavior (a documented limit, default, or feature). Meta-statements such as "this page uses Microsoft Learn as the primary source basis" are tautological and rejected — the marker text `primary source basis` triggers a fail-fast in this generator.

Then regenerate this page:

```bash
python3 scripts/generate_content_validation_status.py
```

## See Also

- [Tutorial Validation Status](validation-status.md)
- [CLI Cheatsheet](cli-cheatsheet.md)

