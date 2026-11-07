---
content_sources:

  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
  diagrams:
    - id: which-plan-should-i-start-with
      type: flowchart
      source: self-generated
      justification: Flow view of which plan should i start with, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
---
# Tutorial - Choose Your Hosting Plan

This section provides four independent Node.js tutorial tracks. Each track follows the same core steps from local development to production operations, with additional steps on some tracks.

## Which Plan Should I Start With?

<!-- diagram-id: which-plan-should-i-start-with -->
```mermaid
flowchart TD
    accTitle: Choose a Node.js tutorial hosting plan
    accDescr: Illustrative tutorial starting points, not exclusive plan capabilities. Follow the VNet question, then either the execution-billing preference or scale-to-zero question; the separate existing-legacy-app path leads to Consumption. Flex optional always-ready billing is qualified below.
    S["Need Node.js<br/>Azure Functions"] --> Q1{"Need VNet<br/>integration?"}
    Q1 -->|No| Q2{"Pay only<br/>on execution?"}
    Q1 -->|Yes| Q3{"Need scale<br/>to zero?"}
    Q2 -->|Yes| F["Flex<br/>Consumption"]
    S -.->|Existing legacy app| C[Consumption]
    Q2 -->|No| D[Dedicated]
    Q3 -->|Yes| F
    Q3 -->|No| P[Premium]
    %% Layout-only links tier outcomes; they add no decision or semantic arrow.
    C ~~~ Q1
    D ~~~ Q3
    P ~~~ F
    classDef neutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class S,Q1,Q2,Q3,F,C,D,P neutral;
```

**Takeaway:** These are tutorial recommendations, not exclusive capabilities. “Pay only on execution” means Flex **on-demand compute** billing; optional always-ready instances add baseline charges, and storage/monitoring costs are separate ([Flex billing](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan#billing)). Premium and Dedicated do not scale to zero; not needing scale-to-zero does not rule out Flex ([hosting comparison](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)).

## Plan Comparison at a Glance

Use [Platform Limits](../../../reference/platform-limits.md) for plan/OS/region-qualified quotas, slots, runtime support, and timeout qualifications. Flex is Linux-only; this guide's Consumption track uses Linux. For Linux Consumption retirement and target selection, follow the [migration decision path](../../../reference/platform-limits.md#runtime-support-and-linux-consumption-migration). Tutorial runtime pins and configured scale caps are examples, not platform limits.

| Feature | Consumption | Flex Consumption | Premium | Dedicated |
|---|---:|---:|---:|---:|
| Scale to zero | Yes | Yes | No | No |
| VNet integration | No | Yes | Yes | Yes (tier-dependent) |
| Typical fit | Burst workloads | Modern serverless default | Low latency and warm capacity | Existing App Service estates |

## Tutorial Tracks

- [Consumption](consumption/01-local-run.md)
- [Flex Consumption](flex-consumption/01-local-run.md)
- [Premium](premium/01-local-run.md)
- [Dedicated](dedicated/01-local-run.md)

## What Each Step Covers

| Step | Topic |
|---|---|
| 01 | Local run |
| 02 | First deploy |
| 03 | Configuration |
| 04 | Logging and monitoring |
| 05 | Infrastructure as code |
| 06 | CI/CD |
| 07 | Extending triggers |
| 08 | Testing and debugging (Flex track) |
| 09 | Container deployment (Premium track) |

## See Also
- [Node.js Language Guide](../index.md)
- [Node.js v4 Programming Model](../v4-programming-model.md)
- [Platform: Hosting Plans](../../../platform/hosting.md)

## Sources
- [Azure Functions hosting options (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [Flex Consumption plan (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan)
