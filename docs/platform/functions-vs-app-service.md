---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/app-service/overview
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/compute-decision-tree
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-compare-logic-apps-ms-flow-webjobs
  diagrams:
    - id: decision-framework
      type: flowchart
      source: self-generated
      justification: Illustrative workload-choice heuristic, not an exhaustive capability or plan-eligibility classifier; all original branches and outcomes retained.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview
        - https://learn.microsoft.com/en-us/azure/app-service/overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/compute-decision-tree
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-compare-logic-apps-ms-flow-webjobs
        - https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan
    - id: architecture-comparison
      type: graph
      source: self-generated
      justification: Conceptual comparison of HTTP routing, worker capacity and runtime roles; bundles retain enumerated roles in the adjacent key, not a physical co-location or wire-protocol claim across hosting plans.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview
        - https://learn.microsoft.com/en-us/azure/app-service/overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/compute-decision-tree
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-compare-logic-apps-ms-flow-webjobs
        - https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling
        - https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan
        - https://learn.microsoft.com/en-us/azure/app-service/overview-hosting-plans
        - https://learn.microsoft.com/en-us/azure/app-service/manage-automatic-scaling
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-hubs-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer
content_validation:
  status: verified
  last_reviewed: 2026-09-11
  reviewer: agent
  core_claims:
    - claim: "Azure Functions and Azure App Service both run on the underlying App Service platform infrastructure"
      source: https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview
      verified: true
    - claim: "Azure Functions supports scale-to-zero on Consumption and Flex Consumption plans, while App Service does not"
      source: https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
      verified: true
    - claim: "Azure Functions provides trigger and binding-based event-driven execution, while App Service is centered on web app hosting"
      source: https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview
      verified: true
    - claim: "App Service supports native WebSocket hosting, unlike Azure Functions"
      source: https://learn.microsoft.com/en-us/azure/app-service/overview
      verified: true
---

# Azure Functions vs Azure App Service

Azure Functions and Azure App Service are both built on the same underlying App Service platform infrastructure. This guide compares the two services, provides a decision framework for choosing between them, and covers migration and coexistence patterns.

## Portal Walkthrough

Key portal blades illustrating Function App characteristics compared to App Service. PII is masked.

![Function App Overview showing serverless runtime, triggers, and plan info](../assets/operations/overview/01-function-app-overview.png)

![App Service plan blade showing Consumption Y1 with scale-to-zero](../assets/operations/hosting/01-app-service-plan.png)

[Observed] Unlike standard App Service, the Function App Overview shows a **Functions** tab with trigger types and the **App Service Plan** shows dynamic scaling (Y1). App Service uses fixed Always On plans without trigger-based execution.

## Main Content
### Why This Comparison Matters

Both services share scale units, networking primitives, and deployment mechanisms. Understanding when each service fits — and when they overlap — prevents architectural misfits that are expensive to reverse after production rollout.

!!! note "Shared platform"
    Azure Functions on the Dedicated (App Service Plan) tier runs on the exact same infrastructure as a standard App Service web app. The difference is the programming model, not the compute substrate.

### Feature Comparison

| Capability | Azure Functions | Azure App Service |
|---|---|---|
| **Execution model** | HTTP and non-HTTP triggers on Consumption, Flex Consumption, Premium and Dedicated; enable Always On for reliable non-HTTP triggering on Dedicated | Web/API hosting; background event processing can use WebJobs with the WebJobs SDK; Always On depends on tier/configuration |
| **Programming model** | Functions with bindings | Full web frameworks (ASP.NET, Express, Flask, Spring) |
| **Scale-to-zero** | Yes (Consumption, Flex Consumption) | No (minimum 1 instance) |
| **Auto-scaling** | Event-driven on Consumption/Premium; per-function/group on Flex Consumption; manual/autoscale on Dedicated | Manual (Basic+), rule-based autoscale (Standard+), or HTTP automatic scaling on web-only Premium v2–v4 plans |
| **Max execution time** | Plan-dependent `functionTimeout` (Consumption default 5 min/max 10 min, Flex default 30 min, Premium/Dedicated unbounded) with a 230-second HTTP response limit on all plans | No `functionTimeout`; request duration is governed by app/server behavior and upstream HTTP timeouts, which differ from Functions host timeout semantics |
| **Trigger types** | HTTP, Timer, Queue, Blob, Cosmos DB, Event Hub, Event Grid, Service Bus, SignalR, Durable | HTTP only (plus WebJobs for background) |
| **Bindings (input/output)** | Native support for 20+ services | Manual SDK integration |
| **WebSocket support** | No native WebSocket hosting (use Azure SignalR Service) | Full native support |
| **Session affinity (ARR)** | Not supported (stateless by design) | Supported (Basic and above) |
| **Deployment slots** | Yes (Consumption supports 2 total slots including production; Premium and Dedicated support slots) | Yes (Standard and above) |
| **VNet integration** | Yes (Flex Consumption, Premium, Dedicated) | Yes (Standard and above) |
| **Private endpoints** | Yes (Flex Consumption, Premium, Dedicated) | Yes (Basic and above) |
| **Custom domains** | Yes | Yes |
| **Managed identity** | Yes | Yes |
| **Language support** | C#, JavaScript/TypeScript, Python, Java, PowerShell, Go (custom handler) | C#, Node.js, Python, Java, PHP, Ruby, Go (custom container) |
| **Container support** | Yes (Premium, Dedicated) | Yes (all Linux tiers) |
| **Pricing model** | Per-execution (Consumption), on-demand plus optional always-ready baseline (Flex Consumption), or per-instance (Premium, Dedicated) | Per-instance (always) |
| **Startup class / host** | Function host with triggers | Web server (Kestrel, Express, Gunicorn, Tomcat) |

### Decision Framework

Use this illustrative decision tree to shortlist a service, then check the selected hosting plan and trigger requirements; it is not an exhaustive capability matrix.

<!-- diagram-id: decision-framework -->
```mermaid
%%{init: {'flowchart': {'nodeSpacing': 8, 'rankSpacing': 40}}}%%
flowchart TD
    accTitle: Functions versus App Service workload decisions
    accDescr: Illustrative service-selection heuristic retaining every original question, branch and outcome. Hosting-plan and trigger qualifications immediately below the figure apply to the suggested choices.
    A[New workload] --> B{"Event-driven?<br/>Triggers beyond<br/>HTTP?"}
    B -->|Yes| C{"Scale-to-zero<br/>required?"}
    B -->|No| D{"Long-running<br/>processes?"}
    C -->|Yes| E["Azure Functions<br/>Consumption or Flex"]
    C -->|No| F{"Need warm<br/>baseline?"}
    F -->|Yes| G["Azure Functions<br/>Premium"]
    F -->|No| H["Azure Functions<br/>Dedicated"]
    D -->|Yes| I{"WebSocket or<br/>session affinity?"}
    D -->|No| J{"Simple HTTP<br/>API or complex<br/>web app?"}
    I -->|Yes| K[App Service]
    I -->|No| L{"Background<br/>processing model?"}
    L -->|Event triggers| M["Azure Functions<br/>Dedicated"]
    L -->|"WebJobs or<br/>scheduled"| K
    J -->|"Complex web app<br/>with middleware"| K
    J -->|"Simple<br/>HTTP API"| N{"Existing App<br/>Service Plan?"}
    N -->|"Yes, with<br/>spare capacity"| P["Add Functions<br/>to existing plan"]
    N -->|No| E
    %% Layout-only links tier the original choices; they add no decisions or semantic arrows.
    F ~~~ G
    G ~~~ H
    H ~~~ D
    I ~~~ L
    L ~~~ M
    M ~~~ J
    J ~~~ N
    N ~~~ P
    P ~~~ K
    K ~~~ E
    classDef neutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class A,B,C,D,E,F,G,H,I,J,K,L,M,N,P neutral;
```

**Reading key:** Every labelled branch is a shortlist, not an exclusion of other plans. Flex Consumption also offers always-ready instances; Premium is not the only warm-baseline option. Consumption and Flex Consumption can scale to zero (Flex without an always-ready baseline); Premium keeps at least one plan instance, while Dedicated uses provisioned App Service capacity. Dedicated still supports non-HTTP triggers: enable Always On for reliable non-HTTP triggering. An existing plan must have a supported Dedicated tier and spare capacity. [Hosting comparison](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale), [Dedicated hosting](https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan).

#### When to Choose Azure Functions

- **Event-driven workloads** — processing queue messages, blob uploads, database change feeds, scheduled tasks, or webhook handlers.
- **Microservice glue** — lightweight functions that connect services without maintaining a full web application.
- **Scale-to-zero** — workloads with idle periods where paying for zero compute matters.
- **Rapid development** — bindings eliminate boilerplate for common Azure service integrations.
- **Fan-out / fan-in** — Durable Functions orchestrations that coordinate parallel work.

#### When to Choose App Service

- **Traditional web applications** — server-rendered pages, SPAs with API backends, REST APIs with complex middleware.
- **Long-running HTTP connections** — WebSocket-based applications (chat, real-time dashboards).
- **Session affinity** — workloads requiring sticky sessions (ARR affinity).
- **Full framework control** — applications needing complete control over the HTTP pipeline, middleware, and startup configuration.
- **Existing App Service estate** — organizations with existing App Service Plans and operational investment.

### Architecture Comparison

Compare runtime roles separately from plan-specific capacity management. The infrastructure boundary below is conceptual: Dedicated Functions can share an App Service plan with web apps; it does not assert that Consumption, Flex Consumption and Premium apps share that same worker pool.

<!-- diagram-id: architecture-comparison -->
```mermaid
%%{init: {'flowchart': {'nodeSpacing': 8, 'rankSpacing': 40}}}%%
graph TB
    accTitle: Functions and App Service runtime comparison
    accDescr: Conceptual hosting comparison, not physical co-location across all plans. HTTP front ends route to worker capacity; separate Functions and web runtime roles retain Queue, Event Hubs and timer examples. The adjacent key scopes scaling by plan and distinguishes listener reads from HTTP ingress.
    subgraph HTTP["HTTP traffic"]
        client(["Client requests"])
    end
    subgraph STAMP["App Service<br/>infrastructure"]
        ingress["HTTP front ends<br/>LB + FE"]
        subgraph WORKERS["Worker capacity"]
            workers["Instances 1, 2, N"]
        end
    end
    subgraph FUNCTIONS["Functions<br/>runtime"]
        app_runtime["Function host"]
        trigger_listener["Trigger listeners"]
    end
    subgraph WEB["Web app runtime"]
        web_runtime["Web server"]
        middleware["Middleware pipeline"]
    end
    subgraph TRIGGERS["Trigger examples"]
        event_source[("Queue +<br/>Event Hubs")]
        schedule["Timer schedule"]
    end
    scale_controller["Scale controller<br/>Dynamic plans<br/>only"]
    client -->|"[Illustrative]<br/>HTTP"| ingress
    ingress -->|"[Illustrative]<br/>Route"| workers
    workers -.->|"[Illustrative]<br/>Functions"| app_runtime
    app_runtime -.->|"[Illustrative]<br/>Owns"| trigger_listener
    trigger_listener -->|"[Configured]<br/>Read"| event_source
    trigger_listener -.->|"[Configured]<br/>Schedule"| schedule
    workers -.->|"[Illustrative]<br/>Web app"| web_runtime
    web_runtime -->|"[Illustrative]<br/>Pipeline"| middleware
    scale_controller -.->|"[Configured]<br/>Demand"| event_source
    scale_controller -.->|"[Configured]<br/>Capacity"| app_runtime
    %% Layout-only tiers add no components, runtime steps or semantic arrows.
    scale_controller ~~~ client
    event_source ~~~ schedule
    schedule ~~~ web_runtime
    classDef neutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    classDef control fill:#ffffff,stroke:#707e93,stroke-width:1.5px,stroke-dasharray:4 3,color:#14202e;
    class client,ingress,workers,app_runtime,trigger_listener,event_source,schedule,web_runtime,middleware neutral;
    class scale_controller control;
    linkStyle default stroke-width:2px;
```

| Figure key | Preserved roles and scope |
|---|---|
| LB + FE | Azure Load Balancer and front-end server roles bundled as a conceptual HTTP routing layer, not a documented packet-by-packet path. Client requests reach worker-hosted HTTP handlers; Queue/Event Hubs traffic does not traverse this HTTP path. |
| Instances 1, 2, N | Original three worker examples retained as an enumerated pool. Functions and web runtimes are logical worker-hosted alternatives, not extra network hops. Dedicated apps can share a plan; other plans have their own capacity/scaling rules. |
| Functions runtime | Function host coordinates trigger listeners. Queue listeners poll Queue Storage; Event Hubs listeners read the event stream; the timer listener follows its schedule rather than receiving an external HTTP event. These are trigger-model distinctions, not language-specific process boundaries. |
| Web app runtime | Web server (original examples: Kestrel, Express, Gunicorn) and middleware pipeline remain separate roles. The pipeline is application-specific, not a mandatory transport component. |
| Scale controller | Dotted demand/capacity paths summarize Consumption/Premium app-level and Flex Consumption per-function/group event-driven scaling, not event forwarding or ARM transport. HTTP, Blob (Event Grid) and Durable triggers each share their respective Flex groups. The timer example does not imply one timer invocation per worker. |

!!! info "Key architectural difference"
    Trigger listeners belong to the Functions programming model on Consumption, Flex Consumption, Premium and Dedicated. Functions event-driven capacity management applies to Consumption, Flex Consumption and Premium, **not Dedicated**. Dedicated uses App Service manual scaling or supported rule-based autoscale. Web-only App Service plans on Premium v2–v4 can alternatively enable HTTP-traffic automatic scaling; that feature does not support a plan containing function apps. [Event-driven scaling](https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling), [App Service scaling](https://learn.microsoft.com/en-us/azure/app-service/manage-automatic-scaling).

### Migration Guidance

#### App Service to Azure Functions

**When to migrate:**

- Your web app evolved into mostly API endpoints and background processors.
- You want event-driven scaling instead of always-on instances.
- You are paying for idle capacity during off-peak hours.
- You need native trigger support for queues, blobs, or timers.

**Key changes:**

| App Service Pattern | Azure Functions Equivalent |
|---|---|
| Web routes / controllers | HTTP-triggered functions |
| Hosted background jobs | Timer-triggered or queue-triggered functions |
| In-process startup/configuration | Function host configuration for the chosen language model |
| `appsettings.json` | Application settings + `local.settings.json` for local development |
| WebJobs | Native Azure Functions triggers |

**Step-by-step approach:**

1. **Inventory endpoints** — catalog all routes, background jobs, and scheduled tasks.
2. **Map to triggers** — assign each endpoint to an HTTP trigger, timer trigger, or event trigger.
3. **Extract shared logic** — move business logic into shared libraries that both the app and functions can reference during the transition.
4. **Create function project** — initialize with the current Azure Functions programming model for your language (for example, Node.js v4, Java annotations, Python v2, or .NET isolated worker).
5. **Migrate incrementally** — move one endpoint or job at a time, verifying behavior with integration tests.
6. **Update routing** — use Azure API Management or Azure Front Door to gradually shift traffic.
7. **Decommission** — remove the App Service app after all traffic is migrated.

!!! warning "Common pitfalls"
    - **Execution timeout**: Consumption plan has a 5-minute default timeout. Move long-running logic to Premium or Dedicated, or redesign with Durable Functions.
    - **Cold starts**: If the App Service app had always-on enabled, users may notice latency regression on Consumption or Flex Consumption.
    - **State management**: Functions are stateless by default. Externalize any in-memory session or cache state to Redis or Cosmos DB.
    - **WebSocket loss**: Azure Functions does not support WebSocket connections. Keep WebSocket endpoints on App Service or migrate to Azure SignalR Service.

#### Azure Functions to App Service

**When to migrate:**

- The function app grew into a complex API with 50+ endpoints and shared middleware.
- You need WebSocket support or session affinity.
- Execution time requirements exceed Consumption plan limits and Durable Functions is not a fit.
- You want full control over the HTTP pipeline and startup sequence.

**Key changes:**

| Azure Functions Pattern | App Service Equivalent |
|---|---|
| HTTP-triggered functions | Controllers or route handlers |
| Input/output bindings | Direct SDK or service client calls |
| Timer-triggered functions | Hosted services or WebJobs |
| Queue-triggered functions | Hosted services, WebJobs, or a retained function app |
| Durable orchestrations | Custom workflow/orchestration implementation or Logic Apps |
| `local.settings.json` | `appsettings.json` + environment variables |

**Step-by-step approach:**

1. **Audit function triggers** — list all functions and their trigger types.
2. **Identify non-HTTP triggers** — these need replacement strategies (WebJobs, hosted services, or separate function apps).
3. **Create web app project** — scaffold with your preferred framework.
4. **Migrate HTTP functions** — convert to controllers or minimal API endpoints.
5. **Replace bindings** — swap input/output bindings for direct SDK calls.
6. **Handle background work** — move timer and queue triggers to WebJobs or keep them in a small function app.
7. **Deploy and validate** — use deployment slots for safe rollout.

!!! warning "Common pitfalls"
    - **Binding replacement**: Input and output bindings handle retries, serialization, and connection management automatically. Direct SDK usage requires implementing this logic yourself.
    - **Scale model change**: You lose event-driven auto-scaling. Plan instance counts based on load testing.
    - **Cost model shift**: App Service charges per instance (always running), not per execution.

### Coexistence Patterns

In most real-world architectures, Functions and App Service coexist rather than replace each other.

#### Pattern 1: Functions for Events, App Service for Web

The most common pattern: a web application on App Service handles user-facing HTTP traffic while Azure Functions processes background events.

```
User → App Service (Web UI / API) → Queue Storage → Azure Functions (Processor)
                                   → Blob Storage → Azure Functions (Thumbnail Generator)
```

!!! tip "When to use"
    This is the default recommendation for applications that have both a web frontend and event-driven processing requirements.

#### Pattern 2: Shared App Service Plan

When using the Dedicated (App Service Plan) tier, you can run both web apps and function apps on the same plan to maximize instance utilization.

```bash
# Create an App Service Plan
az appservice plan create \
    --resource-group $RG \
    --name $PLAN_NAME \
    --sku P1V3 \
    --is-linux

# Deploy a web app on the plan
az webapp create \
    --resource-group $RG \
    --plan $PLAN_NAME \
    --name $APP_NAME \
    --runtime "DOTNET|8.0"

# Deploy a function app on the same plan
az functionapp create \
    --resource-group $RG \
    --plan $PLAN_NAME \
    --name $FUNC_NAME \
    --runtime dotnet-isolated \
    --functions-version 4 \
    --storage-account $STORAGE_NAME
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az appservice plan create`, `az webapp create`, `az functionapp create` |
| Key flags | `--resource-group`, `--name`, `--sku`, `--is-linux`, `--plan`, `--runtime`, `--functions-version`, `--storage-account` |
| Variables | `$RG`, `$PLAN_NAME`, `$APP_NAME`, `$FUNC_NAME`, `$STORAGE_NAME` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


!!! warning "Resource contention"
    Web apps and function apps on the same plan share CPU and memory. A spike in function app executions can starve the web app. Monitor both apps and consider separate plans for production workloads with strict SLAs.

#### Pattern 3: API Management as Unified Gateway

Use Azure API Management to expose both App Service and Functions endpoints behind a single API gateway, providing a unified URL namespace, authentication, rate limiting, and monitoring.

```
Client → API Management Gateway → /api/users/* → App Service
                                → /api/events/* → Azure Functions
                                → /api/reports/* → Azure Functions
```

#### Pattern 4: Gradual Migration Bridge

During migration from one service to the other, run both side by side with traffic splitting. Use Azure Front Door or API Management to route a percentage of traffic to the new service while monitoring error rates and latency.

## See Also

- [Hosting Plans](hosting.md) — detailed comparison of Azure Functions hosting plans
- [Architecture](architecture/index.md) — Azure Functions runtime architecture and execution model
- [Scaling](scaling.md) — event-driven scaling behavior across hosting plans
- [Hosting Plan Selection](../best-practices/hosting-plan-selection.md) — best practices for choosing a hosting plan
- [Hosting Options Overview](../start-here/hosting-options.md) — quick start guide for hosting options

## Sources

- [Azure Functions overview — Microsoft Learn](https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview)
- [Azure App Service overview — Microsoft Learn](https://learn.microsoft.com/en-us/azure/app-service/overview)
- [Azure Functions hosting options — Microsoft Learn](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [Choose an Azure compute service — Microsoft Learn](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/compute-decision-tree)
- [App Service, Functions, and Logic Apps comparison — Microsoft Learn](https://learn.microsoft.com/en-us/azure/azure-functions/functions-compare-logic-apps-ms-flow-webjobs)
