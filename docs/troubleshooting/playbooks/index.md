---
content_sources:

  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-diagnostics
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-diagnostics
  diagrams:
    - id: incident-playbooks
      type: graph
      source: self-generated
      justification: Guide-authored navigation from symptom areas to the playbooks linked below; Learn diagnostics and monitoring provide troubleshooting context, not this guide's category taxonomy or a root-cause classifier.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-diagnostics
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-diagnostics
---
# Incident Playbooks

Symptom-oriented troubleshooting guides for Azure Functions.

Each playbook follows a hypothesis-driven structure: start from the symptom, list competing hypotheses, collect evidence, validate or disprove, and identify the root cause.

<!-- diagram-id: incident-playbooks -->
```mermaid
%%{init: {'flowchart': {'nodeSpacing': 12, 'rankSpacing': 35}}}%%
graph TD
    accTitle: Which incident playbook should I open?
    accDescr: Navigation from a reported symptom through seven primary symptom areas to twelve playbooks. Execution, Performance, Queue / Event Processing, Deployment, Triggers, Scaling and Auth / Config match the linked sections below. Arrows group destinations, not diagnostic evidence or confirmed causes.
    A([Reported symptom]) --> B{Primary<br/>symptom area}
    B --> C[Execution]
    C --> C1["Functions not<br/>executing"]
    C --> C2["Functions failing<br/>with errors"]
    B --> D[Performance]
    D --> D1["High latency /<br/>slow responses"]
    B --> E["Queue /<br/>Event Processing"]
    E --> E1["Queue messages<br/>piling up"]
    E --> E2["Blob trigger<br/>not firing"]
    B --> F[Deployment]
    F --> F1["Deployment failures"]
    B --> G[Triggers]
    G --> G1["Timeout /<br/>Execution Limit"]
    G --> G2["Event Hub /<br/>Service Bus Lag"]
    B --> H[Scaling]
    H --> H1["Out of Memory /<br/>Worker Crash"]
    H --> H2["Durable Orchestration<br/>Stuck"]
    B --> I["Auth / Config"]
    I --> I1["Managed Identity /<br/>RBAC Failure"]
    I --> I2["App Settings<br/>Misconfiguration"]
    %% Layout-only links tier the categories; they add no navigation or diagnostic arrows.
    C1 ~~~ C2
    C2 ~~~ D
    D1 ~~~ E
    E1 ~~~ E2
    E2 ~~~ F
    F1 ~~~ G
    G1 ~~~ G2
    G2 ~~~ H
    H1 ~~~ H2
    H2 ~~~ I
    I1 ~~~ I2
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class A,B,C,D,E,F,G,H,I,C1,C2,D1,E1,E2,F1,G1,G2,H1,H2,I1,I2 baseNeutral;
    linkStyle default stroke-width:2px;
```

**Takeaway:** Choose a symptom area, then open its playbook in the linked tables below. These are navigation categories, not confirmed causes; the playbook supplies the evidence and hypothesis checks.

---

## Execution

| Playbook | Symptom |
|----------|---------|
| [Functions Not Executing](functions-not-executing.md) | Events arrive but invocation count is near zero |
| [Functions Failing with Errors](functions-failing.md) | Exception count and 5xx increase quickly |

## Performance

| Playbook | Symptom |
|----------|---------|
| [High Latency / Slow Responses](high-latency.md) | P95 latency spikes and timeout rate increases |

## Queue / Event Processing

| Playbook | Symptom |
|----------|---------|
| [Queue Messages Piling Up](queue-piling-up.md) | Queue depth and message age rise steadily |
| [Blob Trigger Not Firing](blob-trigger-not-firing.md) | Blob uploads succeed but invocations never appear |

## Deployment

| Playbook | Symptom |
|----------|---------|
| [Deployment Failures](deployment-failures.md) | Deployment fails or app degrades immediately after release |

## Triggers

| Playbook | Symptom |
|----------|---------|
| [Timeout / Execution Limit](triggers/timeout-execution-limit.md) | Functions terminate early or hit maximum execution duration |
| [Event Hub / Service Bus Lag](triggers/event-hub-service-bus-lag.md) | Event-driven processing falls behind and checkpoint lag grows |

## Scaling

| Playbook | Symptom |
|----------|---------|
| [Out of Memory / Worker Crash](scaling/out-of-memory-worker-crash.md) | Workers restart or fail under memory pressure |
| [Durable Orchestration Stuck](scaling/durable-orchestration-stuck.md) | Durable orchestrations hang or replay excessively |

## Auth / Config

| Playbook | Symptom |
|----------|---------|
| [Managed Identity / RBAC Failure](auth-config/managed-identity-rbac-failure.md) | Identity-based access fails after RBAC or scope changes |
| [App Settings Misconfiguration](auth-config/app-settings-misconfiguration.md) | Functions fail due to missing, wrong, or stale application settings |
---

## How to Use These Playbooks

1. Identify the primary symptom your incident matches.
2. Open the corresponding playbook.
3. Follow the hypothesis-driven workflow: **What you observe → Hypotheses → Checks → Interpretation → Fix**.
4. Use inline KQL queries directly in the playbook — no need to switch to a separate query library.

!!! tip "Troubleshooting Workflow"
    Start with [First 10 Minutes](../first-10-minutes/index.md), follow [Methodology](../methodology.md), use playbook-embedded KQL queries, and map hands-on practice from [Lab Guides](../lab-guides/index.md).

## See Also

- [First 10 Minutes](../first-10-minutes/index.md)
- [Methodology](../methodology.md)
- [KQL Query Library](../kql/index.md)
- [Lab Guides](../lab-guides/index.md)
- [Evidence Map](../evidence-map.md)

## Sources

- [Microsoft Learn source 1](https://learn.microsoft.com/en-us/azure/azure-functions/functions-diagnostics)
- [Microsoft Learn source 2](https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring)
- [Microsoft Learn source 3](https://learn.microsoft.com/en-us/azure/azure-functions/functions-diagnostics)
