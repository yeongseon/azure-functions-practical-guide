---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-diagnostics
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb-v2-trigger
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-hubs-trigger
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus
  diagrams:
    - id: 1-hosting-plan-architecture-where-startup-and-scale-behavior-change
      type: flowchart
      source: self-generated
      justification: Flow view of hosting plan architecture where startup and scale behavior change, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-premium-plan#prewarmed-instances
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-diagnostics
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb-v2-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-hubs-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus
    - id: 2-trigger-and-binding-architecture-where-invocations-begin-or-stall
      type: flowchart
      source: self-generated
      justification: Flow view of trigger and binding architecture where invocations begin or stall, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-diagnostics
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb-v2-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-hubs-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus
    - id: request-flow-examples-by-trigger-type
      type: flowchart
      source: self-generated
      justification: Illustrative, non-exhaustive comparison of logical stage order for HTTP, Storage Queue and Event Hubs triggers, drawn from the trigger binding references; arrows show stage order, not a guaranteed internal protocol or connection direction.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-hubs-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
    - id: 3-scale-controller-and-instance-management-where-backlog-and-burst-failures-originate
      type: flowchart
      source: self-generated
      justification: Flow view of scale controller and instance management where backlog and burst failures originate, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-diagnostics
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb-v2-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-hubs-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus
    - id: scale-out-decision-flow
      type: flowchart
      source: self-generated
      justification: Conceptual sketch of event-driven scale-out checks and instance readiness, drawn from the scale and hosting references; not a documented internal scale controller protocol and not a root-cause verdict.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
    - id: 4-cold-start-flow-where-first-execution-latency-appears
      type: sequenceDiagram
      source: self-generated
      justification: Interaction sequence for cold start flow where first execution latency appears, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-diagnostics
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb-v2-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-hubs-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus
    - id: 5-durable-functions-orchestration-architecture-where-replay-and-state-coordination-confuse-diagnosis
      type: flowchart
      source: self-generated
      justification: Flow view of durable functions orchestration architecture where replay and state coordination confuse diagnosis, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-azure-storage-provider
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-diagnostics
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb-v2-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-hubs-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus
    - id: durable-state-machine-view
      type: stateDiagram-v2
      source: self-generated
      justification: Durable state machine view, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-error-handling
        - https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-instance-management
        - https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-azure-storage-provider
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-diagnostics
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb-v2-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-hubs-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus
    - id: 6-azure-service-integration-path-where-dependencies-amplify-failure
      type: flowchart
      source: self-generated
      justification: Flow view of azure service integration path where dependencies amplify failure, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-diagnostics
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb-v2-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-hubs-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus
    - id: 7-observability-coverage-and-fast-evidence-commands
      type: flowchart
      source: self-generated
      justification: Flow view of observability coverage and fast evidence commands, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-diagnostics
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb-v2-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-hubs-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus
content_validation:
  status: verified
  last_reviewed: 2026-04-12
  reviewer: agent
  core_claims:
    - claim: "진단 방법론 기반 접근"
      source: self-generated
      verified: true
---

# Architecture Components Reference

This page answers the first practical question during an Azure Functions incident: **which platform segment is failing?**

Before opening a deep playbook, map the symptom to the correct layer: hosting plan behavior, trigger delivery, scale controller decisions, worker startup, Durable Functions state coordination, or downstream service integration. That classification tells you which telemetry to query first and which mitigation is realistic.

!!! info "When to use this page"
    Use this page as a **component-by-component reference** when you need to identify *which platform segment* is failing (hosting plan, trigger/binding delivery, scale controller, cold start, Durable state, service integration).
    For a **request-flow and incident-flow view** that traces symptoms through architecture layers, see [Request flow for incident response](request-flow-for-incident-response.md) instead.

## Why this page exists

Playbooks explain specific scenarios. During active incidents, engineers usually need one faster artifact:

1. A hosting and execution map that explains where invocations actually run
2. A trigger and binding flow that shows where events can be delayed, dropped, or rejected
3. A scale model that explains backlog growth, burst behavior, and instance creation timing
4. A cold start path that explains why the first execution is slow even when application code is healthy
5. A Durable Functions model that explains why orchestrations can appear stuck while storage state is still changing

Use this page to route quickly to the right evidence and the right troubleshooting document.

## 1) Hosting Plan Architecture (where startup and scale behavior change)

Azure Functions does not have one runtime shape. The failure domain changes materially by hosting plan.

<!-- diagram-id: 1-hosting-plan-architecture-where-startup-and-scale-behavior-change -->
```mermaid
%%{init: {'flowchart': {'nodeSpacing': 10, 'padding': 5}}}%%
flowchart TD
    accTitle: Hosting plan diagnostic routing
    accDescr: Illustrative routing by hosting plan to four candidate failure points, not proof of an incident cause. HTTP front-end routing and non-HTTP trigger sources are alternatives, not a mandatory Azure Front Door deployment.
    A(["Client or<br/>Event Source"]) --> B["Functions HTTP front end<br/>or trigger source"]
    B --> C{Hosting plan}
    C -->|Consumption| D["Shared serverless workers<br/>Scale to zero"]
    C -->|Flex Consumption| E["Serverless workers<br/>Newer scale model<br/>Per-function scaling focus"]
    C -->|Premium| F["Prewarmed and<br/>always-ready workers<br/>No scale-to-zero"]
    C -->|Dedicated| G["App Service Plan instances<br/>Manual or autoscale"]

    D -. FP-PLAN-01 .-> D1("Cold start after<br/>idle or scale-out")
    E -. FP-PLAN-02 .-> E1("Trigger-specific scale<br/>behavior and networking<br/>assumptions")
    F -. FP-PLAN-03 .-> F1("Prewarmed HTTP capacity<br/>insufficient for burst")
    G -. FP-PLAN-04 .-> G1("Too few instances or<br/>noisy-neighbor within plan")
    %% Layout-only links serialize categories; they add no diagnostic steps or arrows.
    D1 ~~~ E
    E1 ~~~ F
    F1 ~~~ G
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class A,B,C,D,E,F,G,D1,E1,F1,G1 baseNeutral;
```

### Hosting plan troubleshooting differences

| Plan | Core behavior | Common incident pattern | First evidence to check | Diagnostic implication |
|---|---|---|---|---|
| Consumption | Event-driven instances, can scale to zero | Slow first execution, backlog during burst, timeout near cold scale-out | `traces`, `requests`, execution count metrics | Always consider cold start and scale latency before blaming app code |
| Flex Consumption | Newer serverless model with better networking and scaling controls | Trigger-specific delivery confusion, cold start reduced but still possible, storage or Event Grid assumptions for some triggers | `traces`, trigger configuration, platform settings | Check trigger transport design, deployment region, and plan-specific trigger support |
| Premium | Prewarmed/always-ready instances, VNet support, no scale-to-zero | Burst exceeds ready capacity, worker recycle, long-running workloads under pressure | instance count metrics, `requests`, `dependencies` | Cold start is less dominant; concurrency and downstream bottlenecks rise in priority |
| Dedicated | Runs on App Service Plan instances | App appears stable but under-provisioned, restarts due to shared plan pressure, scaling requires explicit plan action | App Service metrics, Activity Log, instance health | Treat as fixed-capacity web workload first, serverless elasticity second |

### Failure points and playbooks

| Failure Point | Symptom | First evidence | Playbook |
|---|---|---|---|
| FP-PLAN-01 Consumption cold scale | first request after idle is slow, queue trigger starts late | host startup traces, request duration percentiles | [High Latency](playbooks/high-latency.md) |
| FP-PLAN-02 Flex trigger mismatch | blob or event-driven execution pattern differs from assumption | listener traces, trigger source configuration | [Functions Not Executing](playbooks/functions-not-executing.md) |
| FP-PLAN-03 Premium ready-capacity gap | p95 worsens during bursts even without scale-to-zero | instance count, request volume, dependency latency | [High Latency](playbooks/high-latency.md) |
| FP-PLAN-04 Dedicated capacity ceiling | throughput flattens, queue backlog grows, CPU or memory pressure rises | plan metrics, worker restart correlation | [Queue Piling Up](playbooks/queue-piling-up.md) and [Out of Memory / Worker Crash](playbooks/scaling/out-of-memory-worker-crash.md) |

## 2) Trigger and Binding Architecture (where invocations begin or stall)

Most Azure Functions incidents begin before user code runs. The event must first reach the trigger listener, be accepted by the host, and then complete any binding reads and writes.

<!-- diagram-id: 2-trigger-and-binding-architecture-where-invocations-begin-or-stall -->
```mermaid
%%{init: {'flowchart': {'nodeSpacing': 10, 'padding': 5}}}%%
flowchart TD
    accTitle: Trigger and binding diagnostic routing
    accDescr: Illustrative logical diagnostic map preserving HTTP, Queue and Service Bus, Event Hubs, Blob and Event Grid, and Timer paths. Arrows group responsibilities, not network hops or a universal execution order. Input bindings can supply data before user code executes; output bindings write results. Failure points are candidates to investigate, not confirmed causes.
    A(["Event source<br/>or caller"]) --> B{Trigger type}
    B -->|HTTP| C["C: HTTP routing"]
    B -->|"Queue /<br/>Service Bus"| D["D: Message listener"]
    B -->|"Event Hubs"| E["E: Partitions"]
    B -->|"Blob /<br/>Event Grid"| F["F: Delivery / scan"]
    B -->|Timer| G["Schedule monitor"]
    C --> H[Functions host]
    D --> H
    E --> H
    F --> H
    G --> H
    H --> I[Language worker]
    I --> J[Function code]
    J --> K["Input and<br/>output bindings"]
    K --> L["L: Destinations"]

    C -. FP-TRIG-01 .-> C1("HTTP path issue")
    D -. FP-TRIG-02 .-> D1("Listener issue")
    E -. FP-TRIG-03 .-> E1("E1: Lag / delay")
    F -. FP-TRIG-04 .-> F1("Delivery issue")
    H -. FP-TRIG-05 .-> H1("H1: Listener init")
    K -. FP-TRIG-06 .-> K1("K1: Binding failure")
    %% Layout-only links serialize alternatives; they add no diagnostic steps or arrows.
    C1 ~~~ D
    D1 ~~~ E
    E1 ~~~ F
    F1 ~~~ G
    H1 ~~~ I
    K1 ~~~ L
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class A,B,C,D,E,F,G,H,I,J,K,L,C1,D1,E1,F1,H1,K1 baseNeutral;
```

**Reading key:** Solid arrows associate logical roles, not universal transport or binding-resolution order; dotted FP arrows identify candidates, not proven causes. FP-TRIG-01 covers HTTP authentication, routing or host availability; FP-TRIG-02 covers Queue or Service Bus listener authentication/backlog; FP-TRIG-04 covers the Blob delivery path or Event Grid subscription. Input bindings can read before function code runs; output bindings write results.

| Display key | Complete label |
|---|---|
| C | Functions front end and host routing |
| D | Listener polls or receives messages |
| E | Partition processor and checkpoint store |
| F | Event delivery or storage scan path |
| L | Storage, Service Bus, Event Hubs, Cosmos DB, HTTP APIs |
| E1 / FP-TRIG-03 | Partition lag or checkpoint delay |
| H1 / FP-TRIG-05 | Host cannot initialize listener |
| K1 / FP-TRIG-06 | Binding write/read failure |

### Request flow examples by trigger type

<!-- diagram-id: request-flow-examples-by-trigger-type -->
```mermaid
flowchart TD
    accTitle: Logical processing stages by trigger type
    accDescr: Three separate illustrative stage paths compare HTTP routing and response, Storage Queue listener and visibility-based processing with delete, retry or poison handling, and Event Hubs processing with partition ownership and checkpoints. Arrows show logical stage order, not connection initiators or a guaranteed internal protocol; the paths are not connected to one another.
    A(["HTTP client"]) --> B["Functions endpoint"]
    B --> C["Host route table"]
    C --> D["Function invocation"]
    D --> E(["Output binding or<br/>HTTP response"])

    F(["Storage Queue<br/>message"]) --> G["Queue trigger listener"]
    G --> H["Dequeue and<br/>set invisibility"]
    H --> I["Function invocation"]
    I --> J(["Delete on success;<br/>retry or poison handling"])

    K(["Event Hub event"]) --> L["Event processor"]
    L --> M["Partition ownership"]
    M --> N["Function invocation"]
    N --> O(["Checkpoint write"])
    %% Layout-only links stack independent paths; they add no processing steps or arrows.
    E ~~~ F
    J ~~~ K
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class A,B,C,D,E,F,G,H,I,J,K,L,M,N,O baseNeutral;
    linkStyle default stroke-width:2px;
```

### Trigger and binding diagnostic routing

| Failure Point | Typical symptom | Why it fails | First evidence | Primary next step |
|---|---|---|---|---|
| FP-TRIG-01 HTTP path | `404`, `401`, `403`, or `5xx` before expected handler path | route mismatch, auth policy, host unavailable | `requests` + `traces` | verify route config, auth settings, and host startup |
| FP-TRIG-02 Queue / Service Bus listener | backlog rises while executions stay flat | listener start failed, connection broken, RBAC mismatch | `traces`, queue metrics, dead-letter growth | validate connection settings and listener startup |
| FP-TRIG-03 Event Hubs lag | partitions fall behind, checkpoint delay grows | slow handler, checkpoint failure, too few instances | consumer lag metrics, `traces`, dependencies | correlate backlog with execution time and checkpoint success |
| FP-TRIG-04 Blob / Event Grid path | blob created but no invocation | Event Grid subscription missing, storage events delayed, trigger configuration mismatch | Event Grid subscription state, `traces` | validate storage event path and listener configuration |
| FP-TRIG-05 Host listener init | app is running but trigger never becomes active | storage auth, extension init, host startup failure | startup traces and exceptions | open trigger-focused playbook |
| FP-TRIG-06 Binding output | function logs success but downstream artifact missing | output binding auth/config failure, retries exhausted | `dependencies`, traces, target service metrics | validate binding identity and downstream permissions |

### Integration map for common Azure services

| Service | Typical role in Functions architecture | Common failure mode | First evidence source |
|---|---|---|---|
| Azure Storage | required host storage, queue/blob triggers, Durable state | auth failure, lease/checkpoint problems, trigger silence | `traces`, storage metrics, Activity Log |
| Event Hubs | high-volume event ingestion | checkpoint lag, partition imbalance, consumer auth | Event Hubs metrics, `traces`, dependency errors |
| Service Bus | queue/topic processing and dead-letter patterns | listener auth failure, lock loss, backlog growth | queue depth metrics, `traces`, exceptions |
| Cosmos DB | trigger source, output binding target, app dependency | lease container issues, throttling, auth failure | `dependencies`, traces, Cosmos metrics |
| Event Grid | delivery path for blob and event-based workflows | subscription misconfiguration or delivery failure | Event Grid subscription health, traces |

## 3) Scale Controller and Instance Management (where backlog and burst failures originate)

Azure Functions scaling is a control loop, not instant elasticity. Backlog, target-based heuristics, and instance readiness all matter.

<!-- diagram-id: 3-scale-controller-and-instance-management-where-backlog-and-burst-failures-originate -->
```mermaid
flowchart TD
    accTitle: Event-driven scale diagnostic flow
    accDescr: Illustrative scale-out stages for Consumption, Flex Consumption and Premium, not Dedicated App Service autoscale or a documented internal protocol. Preserve the Yes additional-instance path and No current-count outcome. Five failure points identify candidate observation, cap, allocation, startup and downstream bottlenecks, not measured failures.
    A(["Incoming load or<br/>event backlog"]) --> B["Scale controller observes<br/>trigger metrics"]
    B --> C{Need more workers?}
    C -->|No| D(["Keep current<br/>instance count"])
    C -->|Yes| E["Request additional instances"]
    E --> F["Allocate workers<br/>for hosting plan"]
    F --> G["Start host and listeners<br/>on new instances"]
    G --> H["Instances begin processing"]

    B -. FP-SCALE-01 .-> B1("Metrics do not reflect<br/>actual bottleneck yet")
    E -. FP-SCALE-02 .-> E1("Scale request<br/>delayed or capped")
    F -. FP-SCALE-03 .-> F1("Instance allocation<br/>slow in burst")
    G -. FP-SCALE-04 .-> G1("Host startup or<br/>specialization delay")
    H -. FP-SCALE-05 .-> H1("More instances exist but<br/>downstream still throttles")
    %% Layout-only links serialize candidates; they add no diagnostic steps or arrows.
    B1 ~~~ C
    D ~~~ E
    E1 ~~~ F
    F1 ~~~ G
    G1 ~~~ H
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class A,B,C,D,E,F,G,H,B1,E1,F1,G1,H1 baseNeutral;
```

### Scale-out decision flow

<!-- diagram-id: scale-out-decision-flow -->
```mermaid
flowchart TD
    accTitle: Scale-out checks and instance readiness
    accDescr: Illustrative event-driven scale-out sketch for Flex Consumption, Premium and legacy Consumption, not Dedicated App Service scaling. Demand, trigger-specific thresholds and available capacity lead to keeping size, a delay or cap, or instance startup. After invocations begin, falling backlog leads to stabilization; otherwise investigate further scale or dependencies. The stages are conceptual, not a documented internal protocol or a root-cause verdict.
    A(["Queue depth, partition lag,<br/>HTTP demand,<br/>concurrency pressure"]) --> B{"Trigger-specific<br/>thresholds crossed?"}
    B -->|No| C(["Remain at<br/>current size"])
    B -->|Yes| D{"Hosting plan can add<br/>instances now?"}
    D -->|No| E(["Delay, throttle,<br/>or stay capped"])
    D -->|Yes| F["Provision instance"]
    F --> G["Load Functions host"]
    G --> H["Replay config and<br/>start listeners"]
    H --> I["Begin invocations"]
    I --> J{"Backlog falling?"}
    J -->|Yes| K(["Stabilize"])
    J -->|No| L(["Need more scale<br/>or dependency fix"])
    %% Layout-only links tier alternatives; they add no decisions, steps or arrows.
    C ~~~ D
    E ~~~ F
    K ~~~ L
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class A,B,C,D,E,F,G,H,I,J,K,L baseNeutral;
    linkStyle default stroke-width:2px;
```

### Scale troubleshooting matrix

| Failure Point | Symptom pattern | First evidence | Interpretation |
|---|---|---|---|
| FP-SCALE-01 Observation gap | backlog grows before instance count rises | trigger-specific metrics, queue depth, partition lag | scale loop has not reacted yet or trigger metrics are delayed |
| FP-SCALE-02 Scale cap | load rises but instance count plateaus | plan limits, app settings, autoscale config | not all scale problems are runtime bugs |
| FP-SCALE-03 Allocation delay | new instances appear too slowly during spike | platform metrics and burst timeline | provisioning latency can dominate burst recovery |
| FP-SCALE-04 Startup delay on new worker | instance count rises but executions lag | startup traces on new instances | this is scale success followed by cold initialization cost |
| FP-SCALE-05 Downstream bottleneck | more workers increase dependency failures instead of throughput | `dependencies` failure rate, target throttling metrics | scale-out can amplify pressure on Service Bus, Cosmos DB, SQL, or APIs |

### Diagnostic commands for scale and instance state

```bash
az functionapp show --resource-group "<resource-group>" --name "<app-name>" --output json
az functionapp plan show --resource-group "<resource-group>" --name "<plan-name>" --output json
az monitor metrics list --resource "/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.Web/sites/<app-name>" --metric "FunctionExecutionCount,FunctionExecutionUnits,Http5xx,Requests" --interval PT1M --aggregation "Total,Average,Maximum" --offset 1h --output table
az monitor metrics list --resource "/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.Storage/storageAccounts/<storage-name>" --metric "QueueMessageCount" --interval PT1M --aggregation "Average,Maximum" --offset 1h --output table
az monitor activity-log list --resource-group "<resource-group>" --offset 2h --max-events 100 --output table
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp show`, `az functionapp plan show`, `az monitor metrics list`, `az monitor activity-log list` |
| Key flags | `--resource-group`, `--name`, `--output`, `--resource`, `--metric`, `--interval`, `--aggregation`, `--offset`, `--max-events` |
| Variables | None |
| Expected result | Azure CLI returns the requested resource data; verify names, IDs, status fields, or metric values match the scenario. |


## 4) Cold Start Flow (where first-execution latency appears)

Cold start is not one step. It is a chain: instance allocation, host specialization, runtime loading, extension startup, application import, and first dependency initialization.

<!-- diagram-id: 4-cold-start-flow-where-first-execution-latency-appears -->
```mermaid
%%{init: {'sequence': {'actorMargin': 0, 'width': 20, 'diagramMarginX': 0, 'messageMargin': 25}}}%%
sequenceDiagram
    accTitle: Cold start logical startup sequence
    accDescr: Illustrative out-of-process startup with six roles and nine ordered exchanges, not a measured timeline or a universal hosting protocol. Allocation, site specialization, host configuration, worker startup, code import and first dependency initialization remain distinct.
    participant S as S
    participant I as I
    participant H as H
    participant W as W
    participant F as F
    participant D as D

    S->>I: 1
    I->>H: 2
    H->>H: 3
    H->>W: 4
    W->>F: 5
    F->>D: 6
    D-->>F: 7
    F-->>H: 8
    H-->>I: 9
```

**Roles:** S = Scale Controller; I = New Instance; H = Functions Host; W = Language Worker; F = Function Code; D = Dependency. This is an illustrative out-of-process startup sequence, not a measured timeline or wire protocol.

| Exchange | Full meaning |
|---|---|
| 1. S → I | Allocate worker for load or first request |
| 2. I → H | Specialize site and mount app content |
| 3. H → H | Load host.json and extensions |
| 4. H → W | Start language worker process |
| 5. W → F | Import user code and initialize globals |
| 6. F → D | Open first dependency connection |
| 7. D → F | Return authentication/session/metadata |
| 8. F → H | Ready for invocation |
| 9. H → I | Execute first invocation |

### Cold start interpretation

- Slow first invocation can come from platform work before your handler begins.
- A healthy steady-state p95 does not disprove cold start.
- Cold-start impact is workload-dependent and should be treated as a range (often sub-second to several seconds), not a fixed single value.
- Premium reduces but does not eliminate initialization cost; tune always-ready and prewarmed instance capacity for burst scenarios.
- Queue or Event Hub workloads can show cold-start symptoms as delayed event pickup instead of slow HTTP response.

### Cold-start failure points

| Failure Point | Symptom | What it usually means | First evidence |
|---|---|---|---|
| FP-COLD-01 allocation delay | no worker available immediately | scale-to-zero or burst allocation latency | request timeline, instance count trend |
| FP-COLD-02 specialization delay | app files or site config take time to load | worker still preparing environment | startup traces |
| FP-COLD-03 extension startup | trigger listeners load slowly or fail | binding extension init problem | `traces` around host initialization |
| FP-COLD-04 language worker init | Python/Node/.NET isolated process starts slowly | package size, imports, runtime mismatch | worker startup traces |
| FP-COLD-05 dependency warm-up | first call to Key Vault, Cosmos DB, Storage, SQL is slow | network/auth/token/cache initialization | `dependencies` first-call duration |

### Cold-start diagnostic commands

```bash
az monitor log-analytics query --workspace "$WORKSPACE_ID" --analytics-query "AppTraces | where TimeGenerated > ago(2h) | where Message has_any ('Initializing Host','Host started','Generating 0 job function','Starting JobHost') | project TimeGenerated, AppRoleInstance, Message | order by TimeGenerated desc" --output table
az monitor log-analytics query --workspace "$WORKSPACE_ID" --analytics-query "AppRequests | where TimeGenerated > ago(2h) | summarize p50=percentile(DurationMs,50), p95=percentile(DurationMs,95), maxDuration=max(DurationMs) by bin(TimeGenerated, 5m) | order by TimeGenerated desc" --output table
az functionapp config appsettings list --resource-group "<resource-group>" --name "<app-name>" --output table
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az monitor log-analytics query`, `az functionapp config appsettings list` |
| Key flags | `--workspace`, `--analytics-query`, `--output`, `--resource-group`, `--name` |
| Variables | `$WORKSPACE_ID` |
| Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


## 5) Durable Functions Orchestration Architecture (where replay and state coordination confuse diagnosis)

Durable Functions is not a single long-running process. It is a state-driven workflow pattern backed by storage. The orchestrator replays history, the runtime persists checkpoints, and activity functions run as separate executions.

<!-- diagram-id: 5-durable-functions-orchestration-architecture-where-replay-and-state-coordination-confuse-diagnosis -->
```mermaid
%%{init: {'flowchart': {'nodeSpacing': 10}}}%%
flowchart TD
    accTitle: Durable orchestration diagnostic flow
    accDescr: Illustrative Azure Storage task-hub model; the runtime mediates history reads, persistence and activity scheduling. Replay is the normal reconstruction path; supported caching can avoid a full replay. Activity results, durable timers and external client signals resume processing; waiting itself does not send an event. Sub-orchestrations are also supported, although this figure branches only to activities, timers and external-event waits. Failure points are diagnostic candidates.
    A(["Client starts<br/>orchestration"]) --> B["Durable client binding"]
    B --> C[Orchestration trigger]
    C --> D["Read history"]
    D --> E["Replay orchestrator"]
    E --> F{"Schedule work<br/>or wait?"}
    F -->|Activity| G[Queue work item]
    F -->|Timer| H["Persist wake-up"]
    F -->|External event| I["Wait for event"]
    G --> J["Activity function executes"]
    J --> K["Write result"]
    H --> D
    I --> D
    K --> D

    C -. FP-DUR-01 .-> C1("Trigger stalled")
    D -. FP-DUR-02 .-> D1("History/store issue")
    E -. FP-DUR-03 .-> E1("Replay issue")
    G -. FP-DUR-04 .-> G1("Activity backlog")
    K -. FP-DUR-05 .-> K1("Write failure")
    %% Layout-only links tier candidates; they add no diagnostic steps or arrows.
    C1 ~~~ D
    D1 ~~~ E
    E1 ~~~ F
    G1 ~~~ J
    %% Layout-only links tier the three alternatives; they add no diagnostic steps or arrows.
    K1 ~~~ H
    H ~~~ I
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class A,B,C,D,E,F,G,H,I,J,K,C1,D1,E1,G1,K1 baseNeutral;
```

**Reading key:** This illustrates the Azure Storage task-hub model. The runtime reads execution history from the durable store, normally replays orchestrator code deterministically, queues activity work, persists timer wake-up messages and activity results, and resumes processing when results, timers or external client signals arrive. Supported caching can avoid a full replay. “Schedule work or wait?” retains activities, timers and sub-orchestrations as scheduling options; the three drawn branches remain Activity, Timer and External event (waiting does not send its own signal).

| Candidate | Full diagnostic meaning |
|---|---|
| FP-DUR-01 | Orchestrator trigger not advancing |
| FP-DUR-02 | History or storage access issue |
| FP-DUR-03 | Replay storm or non-deterministic code |
| FP-DUR-04 | Activity backlog or queue saturation |
| FP-DUR-05 | Checkpoint/state write failure |

### Durable state-machine view

<!-- diagram-id: durable-state-machine-view -->
```mermaid
%%{init: {'state': {'nodeSpacing': 10, 'rankSpacing': 30}}}%%
stateDiagram-v2
    accTitle: Durable conceptual waiting and outcome states
    accDescr: Illustrative diagnostic state model retaining activity, timer and external-event waits, completion, failure and termination. WaitingFor states are conceptual, not runtimeStatus values. Failure arrows identify possible diagnostic paths, not a guarantee that storage outages, poison messages or repeated activity failures set orchestration status to Failed; recovery and exception handling affect the outcome.
    state "WA" as WaitingForActivity
    state "WT" as WaitingForTimer
    state "WE" as WaitingForExternalEvent
    [*] --> Pending
    Pending --> Running: 1
    Running --> WaitingForActivity: 2
    WaitingForActivity --> Running: 3
    Running --> WaitingForTimer: 4
    WaitingForTimer --> Running: 5
    Running --> WaitingForExternalEvent: 6
    WaitingForExternalEvent --> Running: 7
    Running --> Completed: 8
    Running --> Failed: F1
    WaitingForActivity --> Failed: F2
    WaitingForExternalEvent --> Terminated: 9
```

**Reading key:** WaitingForActivity, WaitingForTimer and WaitingForExternalEvent are conceptual waiting states, not `runtimeStatus` values. F1 represents an unhandled orchestrator exception; F2 represents an activity failure propagated to and left unhandled by the orchestrator after any configured retries. Storage failures or problematic messages can instead stall progress and do not by themselves establish `Failed`. The diagram is not an exhaustive runtime state machine.

| Display key | Complete label |
|---|---|
| WA | WaitingForActivity — Waiting for activity |
| WT | WaitingForTimer — Waiting for timer |
| WE | WaitingForExternalEvent — Waiting for external event |
| 1 | Pending → Running: orchestration starts |
| 2 | Running → WaitingForActivity: schedule activity |
| 3 | WaitingForActivity → Running: activity result written |
| 4 | Running → WaitingForTimer: durable timer created |
| 5 | WaitingForTimer → Running: timer fires |
| 6 | Running → WaitingForExternalEvent: external event expected |
| 7 | WaitingForExternalEvent → Running: event received |
| 8 | Running → Completed: final output stored |
| 9 | WaitingForExternalEvent → Terminated: manual terminate |

### Durable troubleshooting matrix

| Failure Point | Typical symptom | First evidence | Why it is misleading |
|---|---|---|---|
| FP-DUR-01 trigger not advancing | orchestration remains `Running` with no visible progress | orchestration status, traces, queue activity | app may be healthy while durable control queue is stuck |
| FP-DUR-02 history/store issue | replay cannot reconstruct state cleanly | storage auth failures, table/queue access traces | looks like code bug but may be storage availability or RBAC |
| FP-DUR-03 replay storm | high CPU/log volume with little forward progress | repeated replay traces, same history events | replays are expected, but excessive replays indicate design or storage pressure |
| FP-DUR-04 activity backlog | orchestration scheduled work but activities lag | queue depth, execution counts, activity failures | orchestrator status alone hides downstream queue saturation |
| FP-DUR-05 state write failure | orchestration appears to retry or stall after activity success | storage exceptions, durable backend errors | activity succeeded but checkpoint did not persist |

### Durable diagnostic commands

```bash
az functionapp function list --resource-group "<resource-group>" --name "<app-name>" --output table
az monitor log-analytics query --workspace "$WORKSPACE_ID" --analytics-query "AppTraces | where TimeGenerated > ago(2h) | where Message has_any ('DurableTask','orchestration','replay','activity') | project TimeGenerated, SeverityLevel, Message | order by TimeGenerated desc" --output table
az storage queue list --account-name "<storage-name>" --auth-mode login --output table
az storage table list --account-name "<storage-name>" --auth-mode login --output table
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp function list`, `az monitor log-analytics query`, `az storage queue list`, `az storage table list` |
| Key flags | `--resource-group`, `--name`, `--output`, `--workspace`, `--analytics-query`, `--account-name`, `--auth-mode` |
| Variables | `$WORKSPACE_ID` |
| Expected result | Azure CLI returns the requested resource data; verify names, IDs, status fields, or metric values match the scenario. |


## 6) Azure Service Integration Path (where dependencies amplify failure)

Azure Functions usually sits in the middle of other services rather than at the edge alone. That means incidents often reflect integration failure, not runtime failure.

<!-- diagram-id: 6-azure-service-integration-path-where-dependencies-amplify-failure -->
```mermaid
%%{init: {'flowchart': {'nodeSpacing': 10}}}%%
flowchart TD
    accTitle: Azure service integration diagnostic routing
    accDescr: Illustrative routing from five integration categories to candidate failure points. Host storage, streaming input, messaging, document data and output events remain separate; this is a diagnostic association map, not a network transport diagram or observed deployment.
    A(["Function invocation"]) --> B{Integration type}
    B -->|"Host<br/>storage"| C["Azure Storage<br/>account"]
    B -->|"Streaming<br/>input"| D[Event Hubs]
    B -->|Messaging| E[Service Bus]
    B -->|"Document<br/>data"| F[Cosmos DB]
    B -->|"Output<br/>events"| G["Event Grid or<br/>HTTP API"]

    C -. FP-INT-01 .-> C1("C1: Storage issue")
    D -. FP-INT-02 .-> D1("D1: Consumer issue")
    E -. FP-INT-03 .-> E1("E1: Message issue")
    F -. FP-INT-04 .-> F1("F1: Data issue")
    G -. FP-INT-05 .-> G1("G1: Output issue")
    %% Layout-only links serialize categories; they add no diagnostic steps or arrows.
    C1 ~~~ D
    D1 ~~~ E
    E1 ~~~ F
    F1 ~~~ G
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class A,B,C,D,E,F,G,C1,D1,E1,F1,G1 baseNeutral;
```

| Display key / candidate | Complete diagnostic label |
|---|---|
| C1 / FP-INT-01 | Host lease, checkpoint, or auth failure |
| D1 / FP-INT-02 | Checkpoint lag or consumer auth failure |
| E1 / FP-INT-03 | Lock loss, dead-letter growth, auth failure |
| F1 / FP-INT-04 | 429 throttling, lease issue, auth failure |
| G1 / FP-INT-05 | Delivery or downstream API failure |

### Integration failure mapping

| Integration | What breaks first | Fastest evidence | Common misread |
|---|---|---|---|
| Azure Storage | host startup, trigger checkpoints, Durable state | storage auth exceptions, queue/table/blob metrics | assuming storage is just an app dependency rather than a platform dependency |
| Event Hubs | lag and uneven partition progress | consumer group lag, checkpoint traces | blaming Functions scale before checking partition ownership |
| Service Bus | backlog, retries, dead-letter growth | queue depth, lock-lost exceptions, trace warnings | treating poison messages as scaling problem only |
| Cosmos DB | throttling or trigger lease contention | `dependencies`, 429 trend, lease container health | blaming handler latency without checking RU limits |
| Event Grid / APIs | delivery failures after successful execution | dependency failures, delivery metrics | concluding the function failed when only the output path failed |

## 7) Observability Coverage and Fast Evidence Commands

<!-- diagram-id: 7-observability-coverage-and-fast-evidence-commands -->
```mermaid
flowchart TD
    accTitle: Architecture segment to first evidence source
    accDescr: Six independent source-to-evidence associations, not sequential incident steps. Suggested telemetry depends on instrumentation and collection settings; absence of telemetry does not establish absence of failures. Durable storage artifacts apply to the configured backend.
    A["Architecture segment"] --> B["Best first<br/>evidence source"]
    C["Hosting plan and scale"] --> D["Metrics + Activity Log"]
    E["Trigger startup<br/>and listener health"] --> F["Application Insights<br/>traces"]
    G["User-facing failures"] --> H["requests + exceptions"]
    I["Dependency issues"] --> J["dependencies +<br/>service metrics"]
    K["Durable state progression"] --> L["traces +<br/>storage artifacts"]
    %% Layout-only links stack independent pairs; they add no diagnostic steps or arrows.
    B ~~~ C
    D ~~~ E
    F ~~~ G
    H ~~~ I
    J ~~~ K
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class A,B,C,D,E,F,G,H,I,J,K,L baseNeutral;
```

### Quick evidence commands by component

```bash
az functionapp show --resource-group "<resource-group>" --name "<app-name>" --output json
az functionapp config appsettings list --resource-group "<resource-group>" --name "<app-name>" --output table
az functionapp function list --resource-group "<resource-group>" --name "<app-name>" --output table
az monitor activity-log list --resource-group "<resource-group>" --offset 24h --max-events 100 --output table
az monitor metrics list --resource "/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.Web/sites/<app-name>" --metric "Requests,Http5xx,FunctionExecutionCount,FunctionExecutionUnits" --interval PT1M --aggregation "Total,Average,Maximum" --offset 2h --output table
az monitor log-analytics query --workspace "$WORKSPACE_ID" --analytics-query "AppRequests | where TimeGenerated > ago(2h) | summarize total=count(), failed=countif(Success == false), p95=percentile(DurationMs,95) by bin(TimeGenerated, 5m) | order by TimeGenerated asc" --output table
az monitor log-analytics query --workspace "$WORKSPACE_ID" --analytics-query "AppDependencies | where TimeGenerated > ago(2h) | summarize failed=countif(Success == false), p95=percentile(DurationMs,95) by Target | order by failed desc" --output table
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp show`, `az functionapp config appsettings list`, `az functionapp function list`, `az monitor activity-log list`, plus 2 more |
| Key flags | `--resource-group`, `--name`, `--output`, `--offset`, `--max-events`, `--resource`, `--metric`, `--interval`, `--aggregation`, `--workspace`, plus 1 more |
| Variables | `$WORKSPACE_ID` |
| Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


## 8) Fast routing examples

- **Example A**: HTTP requests fail only after idle periods.
    - Start with hosting plan architecture and cold start flow.
- Open: [High Latency](playbooks/high-latency.md), [Quick Diagnosis Cards](quick-diagnosis-cards.md), and [First 10 Minutes](first-10-minutes/index.md).
- **Example B**: Queue depth rises while the app shows healthy in the portal.
    - Start with trigger and binding architecture, then scale controller behavior.
    - Open: [Functions Not Executing](playbooks/functions-not-executing.md) and [Queue Piling Up](playbooks/queue-piling-up.md).
- **Example C**: Durable orchestration stays `Running` for a long time with repeated logs.
    - Start with Durable Functions orchestration architecture.
    - Open: [Durable Orchestration Stuck](playbooks/scaling/durable-orchestration-stuck.md) and [Methodology](methodology.md).
- **Example D**: More instances appear during load, but errors shift to Service Bus or Cosmos DB.
    - Start with scale controller and integration path.
    - Open: [High Latency](playbooks/high-latency.md) and [Evidence Map](evidence-map.md).

!!! note "How to use this page during incidents"
    Do not treat scale-out, cold start, or replay behavior as proof of root cause by themselves.
    Use this page to identify the most likely failure layer, then confirm with time-correlated telemetry from Application Insights, Activity Log, and the integrated Azure service.

## See Also

- [Troubleshooting](index.md)
- [Request flow for incident response](request-flow-for-incident-response.md)
- [Evidence Map](evidence-map.md)
- [Decision Tree](decision-tree.md)
- [Troubleshooting Mental Model](mental-model.md)
- [Quick Diagnosis Cards](quick-diagnosis-cards.md)
- [First 10 Minutes](first-10-minutes/index.md)
- [Troubleshooting Method](methodology/troubleshooting-method.md)
- [Detector Map](methodology/detector-map.md)
- [Playbooks Index](playbooks/index.md)
- [KQL Query Library](kql/index.md)

## Sources

- [Azure Functions hosting options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [Azure Functions scale and hosting concepts](https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling)
- [Azure Functions triggers and bindings concepts](https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings)
- [Azure Functions best practices for performance and reliability](https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices)
- [Monitor Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring)
- [Azure Functions networking options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options)
- [Durable Functions application patterns](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview)
- [Durable Functions diagnostics](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-diagnostics)
- [Azure Blob storage trigger for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger)
- [Azure Cosmos DB trigger for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb-v2-trigger)
- [Azure Event Hubs trigger for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-hubs-trigger)
- [Azure Service Bus bindings for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus)
