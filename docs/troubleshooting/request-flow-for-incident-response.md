---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-monitor/app/data-model
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/activity-log
  diagrams:
    - id: request-path-architecture-where-user-facing-failures-surface
      type: flowchart
      source: self-generated
      justification: Illustrative HTTP diagnostic checkpoints and candidate failure associations, not a packet trace or a retained incident result.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-monitor/app/data-model
        - https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/activity-log
    - id: runtime-and-worker-model-where-execution-failures-originate
      type: flowchart
      source: self-generated
      justification: Illustrative out-of-process runtime diagnostic roles and candidate failures; adjacent text retains host roles and language scope.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/dotnet-isolated-process-guide
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-monitor/app/data-model
        - https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/activity-log
    - id: deployment-path-where-release-regressions-appear
      type: flowchart
      source: self-generated
      justification: Illustrative release-stage checks and candidate failures, with slot support qualified by hosting plan.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-deployment-slots
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-monitor/app/data-model
        - https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/activity-log
    - id: network-and-outbound-path-where-external-connectivity-fails
      type: flowchart
      source: self-generated
      justification: Illustrative outbound diagnostic checkpoints, not serial network hops; integration and egress choices depend on plan and configuration.
      based_on:
        - https://learn.microsoft.com/en-us/azure/nat-gateway/nat-overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-monitor/app/data-model
        - https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/activity-log
    - id: observability-map-where-evidence-is-collected
      type: flowchart
      source: self-generated
      justification: Illustrative evidence collection and query map; record availability depends on telemetry and diagnostic configuration.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-monitor/app/data-model
        - https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/activity-log
    - id: suggested-incident-flow-through-architecture-layers
      type: flowchart
      source: self-generated
      justification: Illustrative evidence-routing decisions for incident response, not an exhaustive classifier or proof of root cause.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-monitor/app/data-model
        - https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/activity-log
content_validation:
  status: verified
  last_reviewed: 2026-04-12
  reviewer: agent
  core_claims:
    - claim: "진단 방법론 기반 접근"
      source: self-generated
      verified: true
---

# Request Flow for Incident Response

This guide is a diagnostic architecture reference for incident response.
It is intentionally failure-oriented so you can locate where symptoms originate and what evidence source to check first.
Use it as a fast index from symptom category to architecture layer ownership.

!!! info "When to use this page"
    Use this page when you need a **request-flow and incident-flow view**: trace a symptom top-to-bottom through architecture layers to the evidence source to check.
    For a **component-by-component reference** (hosting, triggers, scale controller, cold start, Durable), see [Architecture components reference](architecture-components-reference.md) instead.

!!! warning "How to use this document"
    This is not a design poster.
    Read each diagram top-to-bottom as a diagnostic map: symptom → candidate layer → evidence to collect, not a confirmed root cause.

!!! tip "Troubleshooting workflow"
Start with [First 10 Minutes](first-10-minutes/index.md), apply [Methodology](methodology.md), run focused queries from [KQL Query Library](kql/index.md), and then execute scenario fixes from [Functions not executing](playbooks/functions-not-executing.md), [High latency / slow responses](playbooks/high-latency.md), [Functions failing with errors](playbooks/functions-failing.md), or [Deployment failures](playbooks/deployment-failures.md).

## Request path architecture (where user-facing failures surface)

The request path is where availability and latency symptoms first appear.
Most `5xx`, timeout, DNS, and auth issues can be mapped to one of these nodes.

<!-- diagram-id: request-path-architecture-where-user-facing-failures-surface -->
```mermaid
flowchart TD
    accTitle: Request-path diagnostic checkpoints
    accDescr: Illustrative HTTP diagnostic order from client and DNS to frontend, worker, code, output binding and downstream, with six candidate failure associations. Arrows are not a packet trace.
    A["Client"] --> B["DNS"]
    B --> C["Load Balancer"]
    C --> D["Frontend"]
    D --> E["Worker Process"]
    E --> F["Function Code"]
    F --> G["Output Binding"]
    G --> H["Downstream"]

    B -. "DNS failure" .-> X1(["Name resolution<br/>error"])
    D -. "401 or 403<br/>auth failure" .-> X2(["Auth or<br/>EasyAuth reject"])
    D -. "5xx gateway<br/>failure" .-> X3(["Frontend-generated<br/>5xx"])
    E -. "timeout" .-> X4(["Execution timeout"])
    G -. "5xx or<br/>retry storm" .-> X5(["Binding write<br/>failure"])
    H -. "timeout or 5xx" .-> X6(["Dependency failure"])
    %% Layout-only links serialize callouts; they add no diagnostic steps or arrows.
    X1 ~~~ C
    X2 ~~~ X3
    X3 ~~~ E
    X4 ~~~ F
    X5 ~~~ H
    classDef neutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class A,B,C,D,E,F,G,H,X1,X2,X3,X4,X5,X6 neutral;
    linkStyle default stroke-width:2px;
```

**Reading key:** Solid arrows order diagnostic checkpoints, not network connections through DNS. Dotted arrows associate symptoms with candidate failure locations; confirm them using the table below. The output-binding checkpoint applies when the function uses an output binding; code can also call dependencies directly.

### Request-path failure map

| Hop | Typical Symptom | Common Failure | Primary Evidence | First Action |
|---|---|---|---|---|
| Client → DNS | Immediate failure before app code runs | DNS record mismatch, private DNS zone missing | Client logs, Azure Front Door/Application Gateway logs, Azure DNS analytics | Validate DNS resolution path and private zone link |
| DNS → Load Balancer | Intermittent connect failures | Edge routing issue or transient platform fault | `requests` + Azure status | Check Azure Service Health and region incidents |
| Load Balancer → Frontend | `502`/`503` spikes | Frontend cannot route to healthy worker | `requests` resultCode + platform logs | Correlate failure spike with restarts |
| Frontend → Worker Process | Long tail latency, timed-out requests | Worker warm-up delay, instance recycle | `traces` host lifecycle, request duration | Check host start and recycle timeline |
| Worker Process → Function Code | `500` with exception | Runtime crash, unhandled exception | `exceptions`, `traces` | Identify dominant exception family |
| Function Code → Output Binding | Retry storms, partial success | Binding auth/config mismatch | `traces` binding errors, dependency failures | Validate binding connection settings |
| Output Binding → Downstream | High p95 and downstream `5xx` | API/database slowness or throttling | `dependencies` p95/failure rate | Isolate failing target and apply backoff |

### High-signal KQL for request-path triage

```kusto
requests
| where timestamp > ago(30m)
| summarize
    Total=count(),
    Failed=countif(success == false),
    P95=percentile(duration, 95)
  by resultCode, bin(timestamp, 5m)
| order by timestamp desc
```

## Runtime and worker model (where execution failures originate)

Azure Functions execution is split across host and language worker boundaries.
Symptoms often appear in requests, but root causes are frequently in process lifecycle and resource pressure.

<!-- diagram-id: runtime-and-worker-model-where-execution-failures-originate -->
```mermaid
flowchart TD
    accTitle: Host and worker failure checkpoints
    accDescr: Illustrative out-of-process model separating host, language worker and user code, with startup, crash, Python contention, memory and blocking-call hypotheses. This is not a measured execution.
    A["A: Functions Host<br/>Process"] --> B["B: Language Worker<br/>Process"]
    B --> C["User Function<br/>Code"]

    A -. "startup failure" .-> X1(["Host startup<br/>failed"])
    B -. "process crash" .-> X2(["Worker terminated"])
    B -. "GIL contention" .-> X3(["Python throughput<br/>collapse"])
    A -. "memory pressure" .-> X4(["Recycle or<br/>OOM risk"])
    C -. "blocking call" .-> X5(["Execution timeout"])
    %% Layout-only links serialize callouts; they add no diagnostic steps or arrows.
    X1 ~~~ X4
    X4 ~~~ B
    X2 ~~~ X3
    X3 ~~~ C
    classDef neutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class A,B,C,X1,X2,X3,X4,X5 neutral;
    linkStyle default stroke-width:2px;
```

**Reading key:** A retains the host roles: trigger listeners, bindings and scale hooks. B covers Python, Node.js, Java and .NET isolated. This is a logical out-of-process view; .NET in-process code runs in the host instead. Dotted associations suggest hypotheses, not proof that memory pressure, GIL contention or a blocking call caused an incident.

### Runtime diagnostic table

| Layer | Component | Common Failure | Evidence Source |
|---|---|---|---|
| Host | JobHost startup | Host cannot initialize listeners or storage lock | `traces` messages containing `Initializing Host`, `Host lock`, `Host started` |
| Host | Trigger listener | Listener disabled, misconfigured, or auth denied | `traces` listener warnings + trigger silence in `requests`/metrics |
| Worker | Language worker process | Crash loop, startup timeout, incompatible runtime | platform logs + `traces` worker startup lines |
| Worker | Python execution runtime | GIL contention under CPU-bound concurrency | high duration variance, low CPU parallelism, `dependencies` idle while requests queue |
| Runtime | Memory management | Memory pressure and instance recycle | Activity Log events, `traces` host shutdown/startup cycle |
| Code | Function entrypoint | Unhandled exceptions and blocking operations | `exceptions`, slow request traces, timeout messages |

### Runtime evidence shortcuts

| Signal | Why it matters | Quick check |
|---|---|---|
| `Host started` missing | App state may be Running but host not healthy | Query `traces` over last 15 minutes |
| Repeated host start/shutdown | Crash loop or platform recycle | Compare `traces` timeline with Activity Log |
| Fast failure with no dependency call | Fails before downstream access | Inspect startup/config/identity exceptions first |
| Latency rises while dependency latency stable | Worker-side bottleneck | Check CPU/memory pressure and concurrency model |

## Deployment path (where release regressions appear)

Many incidents begin at deployment transitions.
Map failures by stage so rollback and forward-fix decisions are evidence-based.

<!-- diagram-id: deployment-path-where-release-regressions-appear -->
```mermaid
flowchart TD
    accTitle: Deployment-stage failure checkpoints
    accDescr: Illustrative code, build, artifact, deploy target, slot and production stages with five candidate release-failure associations. The slot stage applies to slot-supported hosting plans, not Flex Consumption.
    A[Code] --> B[Build]
    B --> C[Artifact]
    C --> D[Deploy Target]
    D --> E[Slot]
    E --> F[Production]

    B -. "dependency restore<br/>failure" .-> X1(["Build failed"])
    C -. "runtime mismatch" .-> X2(["Invalid artifact"])
    D -. "deploy auth<br/>failure" .-> X3(["Deploy rejected"])
    E -. "slot config<br/>drift" .-> X4(["Swap risk"])
    F -. "post-release 5xx" .-> X5(["Production<br/>regression"])
    %% Layout-only links serialize callouts; they add no diagnostic steps or arrows.
    X1 ~~~ C
    X2 ~~~ D
    X3 ~~~ E
    X4 ~~~ F
    classDef neutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class A,B,C,D,E,F,X1,X2,X3,X4,X5 neutral;
    linkStyle default stroke-width:2px;
```

**Takeaway:** Match the failed stage to its evidence before choosing rollback or forward-fix. The slot/swap stage applies to Consumption, Premium and supported Dedicated tiers; Flex Consumption does not support deployment slots.

### Deployment stage troubleshooting table

| Stage | Failure Mode | Detection Method | Recovery Action |
|---|---|---|---|
| Code | Missing config contract, breaking change | PR checks, config schema validation | Revert change or patch config compatibility |
| Build | Dependency resolution or compile failure | CI logs and build summary | Pin package versions, fix pipeline cache and restore |
| Artifact | Runtime/version mismatch with app settings | Compare artifact metadata to function runtime | Rebuild artifact with aligned runtime |
| Deploy Target | Access denied or failed deployment operation | Activity Log and deployment task output | Fix RBAC/service principal scope and redeploy |
| Slot | Slot-specific app settings missing | Slot config diff and smoke tests | Sync required settings and mark sticky config |
| Production | Immediate `5xx`/timeouts after release | `requests` and `exceptions` spike post-deploy | Swap back or roll back to last known good artifact |

### Minimal CLI checks for deployment path

```bash
az monitor activity-log list \
  --subscription "<subscription-id>" \
  --resource-group "rg-myapp-prod" \
  --offset 2h \
  --max-events 50 \
  --output table

az functionapp deployment slot list \
  --resource-group "rg-myapp-prod" \
  --name "func-myapp-prod" \
  --output table
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az monitor activity-log list`, `az functionapp deployment slot list` |
| Key flags | `--subscription`, `--resource-group`, `--offset`, `--max-events`, `--output`, `--name` |
| Variables | None |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


## Network and outbound path (where external connectivity fails)

Outbound failures often look like app bugs but originate in network controls.
Use this path to separate DNS, routing, NSG, and SNAT issues.

<!-- diagram-id: network-and-outbound-path-where-external-connectivity-fails -->
```mermaid
flowchart TD
    accTitle: Outbound diagnostic checkpoints
    accDescr: Illustrative checklist from function app and VNet integration to subnet policies, egress configuration and destination, with five failure associations. These are checks, not serial network appliances.
    A[Function App] --> B["VNet Integration"]
    B --> C[Subnet]
    C --> D[NSG]
    D --> E[UDR]
    E --> F[NAT or Firewall]
    F --> G["Internet or<br/>Private Endpoint"]

    C -. "SNAT exhaustion" .-> X1(["Ephemeral port<br/>depletion"])
    D -. "NSG block" .-> X2(["Outbound denied"])
    E -. "UDR<br/>misconfiguration" .-> X3(["Blackhole route"])
    F -. "firewall deny" .-> X4(["Egress blocked"])
    G -. "DNS resolution<br/>failure" .-> X5(["Name lookup<br/>failed"])
    %% Layout-only links serialize callouts; they add no diagnostic steps or arrows.
    X1 ~~~ D
    X2 ~~~ E
    X3 ~~~ F
    X4 ~~~ G
    classDef neutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class A,B,C,D,E,F,G,X1,X2,X3,X4,X5 neutral;
    linkStyle default stroke-width:2px;
```

**Reading key:** This orders checks, not packet hops: NSGs and UDRs are subnet policies, and NAT is not a UDR next hop. The integration checks apply to Flex Consumption, Premium and supported Dedicated configurations, not Consumption. NAT, firewall routing and private endpoints are configuration-dependent alternatives; SNAT and DNS callouts are hypotheses to test, not faults proved at a subnet or destination.

### Outbound failure evidence table

| Failure Point | Symptom | CLI Check | KQL Query |
|---|---|---|---|
| SNAT exhaustion | Intermittent connect timeout to many external targets | Diagnose and Solve Problems → SNAT Port Exhaustion; `az monitor metrics list --resource "/subscriptions/<subscription-id>/resourceGroups/rg-myapp-prod/providers/Microsoft.Web/sites/func-myapp-prod" --metric "TcpSynSent" --interval PT1M --aggregation Total --offset 30m --output table` | `dependencies | where timestamp > ago(30m) | where success == false | summarize failures=count() by type, target` |
| DNS resolution (outbound) | `ENOTFOUND`, `Name or service not known` | `az network private-dns zone list --resource-group "rg-network" --output table` | `exceptions | where timestamp > ago(30m) | where type has "SocketException" or outerMessage has "DNS" or outerMessage has "NameResolution"` |
| NSG block | Hard timeout after SYN attempts | `az network nsg rule list --resource-group "rg-network" --nsg-name "nsg-functions" --output table` | `dependencies | where timestamp > ago(30m) | summarize timeoutCount=countif(tostring(resultCode) in ("", "0")) by target` |
| UDR misconfiguration | All traffic to one range fails after route change | `az network route-table route list --resource-group "rg-network" --route-table-name "rt-functions" --output table` | `dependencies | where timestamp > ago(30m) | where success == false | summarize count() by target` |
| Firewall or NAT | Region-wide external egress failures | `az network firewall show --resource-group "rg-network" --name "fw-hub" --output table` | `dependencies | where timestamp > ago(30m) | summarize failed=countif(success == false), p95=percentile(duration,95) by target` |

## Observability map (where evidence is collected)

This map shows the primary data paths for troubleshooting.
During incidents, choose evidence source by hypothesis rather than querying everything.

<!-- diagram-id: observability-map-where-evidence-is-collected -->
```mermaid
flowchart TD
    accTitle: Incident evidence collection map
    accDescr: Illustrative configured collection and query relationships among the function app, Application Insights, platform logs, Log Analytics and dashboards. Evidence categories are listed in the adjacent B and C key.
    A[Function App] --> B["B: Application<br/>Insights"]
    A --> C["C: Platform Logs"]
    B --> D["Log Analytics<br/>Workspace"]
    C --> D
    D --> E["Queries and<br/>Dashboards"]
    B -. "B categories" .-> E
    C -. "C categories" .-> E
    %% Layout-only links serialize sources; they add no diagnostic steps or arrows.
    B ~~~ C
    classDef neutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class A,B,C,D,E neutral;
    linkStyle default stroke-width:2px;
```

**Reading key:** B categories are `requests`, `traces`, `dependencies` and `exceptions`; C categories are startup, recycle and platform events. Arrows summarize configured collection/query relationships, not a mandatory export pipeline: Application Insights integration, diagnostic settings, instrumentation, log levels and sampling determine available records.

### Observability source matrix

| Data Source | What It Captures | Best For | Latency |
|---|---|---|---|
| Application Insights `requests` | Invocation success/failure, latency, result codes | User-facing `5xx`, timeout trends, p95 analysis | Near real-time |
| Application Insights `traces` | Host lifecycle, listener state, runtime diagnostics | Startup failures, trigger initialization issues | Near real-time |
| Application Insights `exceptions` | Exception type, message, stack traces | Root-cause clustering by error family | Near real-time |
| Application Insights `dependencies` | Outbound call target, duration, success | Downstream slowness, DNS/network symptoms | Near real-time |
| Platform logs | Host/container/platform lifecycle events | Recycle loops and platform-generated restarts | Minutes |
| Activity Log | Configuration, deployment, RBAC change history | Change correlation and blast-window audit | Near real-time |

## Where problems happen (summary)

Use this as the first routing table when symptom ownership is unclear.

| Symptom Category | Architecture Layer | Evidence Source | First Check |
|---|---|---|---|
| 5xx responses | Frontend / Worker | `requests` table, `Http5xx` metric | KQL: failed requests by resultCode |
| Startup failure | Host process | `traces` table, platform logs | KQL: host startup events |
| DNS or SNAT failure | Network / outbound | `dependencies` + `exceptions`, app logs | Run [High latency / slow responses](playbooks/high-latency.md) checks and SNAT detector + `TcpSynSent` metric |
| Trigger silence | Listener / storage | `traces` table, queue metrics | CLI: function list + storage peek |
| Slow responses | Worker / dependency | `dependencies` table | KQL: dependency p95 |
| Recycle or restart | Platform events | Activity Log, `traces` | KQL: host shutdown/startup timeline |

## Suggested incident flow through architecture layers

<!-- diagram-id: suggested-incident-flow-through-architecture-layers -->
```mermaid
flowchart TD
    accTitle: Incident evidence routing decisions
    accDescr: Illustrative routing through three Yes or No checks. User-facing failures route to requests and exceptions, other symptoms to trigger activity and traces; all four investigation outcomes converge on the smallest safe mitigation.
    A(["Symptom detected"]) --> B{"User-facing 5xx<br/>or timeout?"}
    B -->|Yes| C["Check requests<br/>and exceptions"]
    B -->|No| D["Check trigger activity<br/>and traces"]
    C --> E{"Downstream<br/>latency high?"}
    E -->|Yes| F["F: Dependencies<br/>and outbound"]
    E -->|No| G["G: Worker and<br/>host lifecycle"]
    D --> H{"No listener<br/>startup events?"}
    H -->|Yes| I["I: Host startup<br/>and config"]
    H -->|No| J["J: Trigger source<br/>and backlog"]
    F --> K(["Apply smallest<br/>safe mitigation"])
    G --> K
    I --> K
    J --> K
    %% Layout-only links serialize branches; they add no diagnostic steps or arrows.
    F ~~~ G
    G ~~~ D
    J ~~~ K
    I ~~~ J
    classDef neutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class A,B,C,D,E,F,G,H,I,J,K neutral;
    linkStyle default stroke-width:2px;
```

**Reading key:** F: inspect dependencies and outbound network path; G: inspect worker and host lifecycle; I: investigate host startup and config; J: inspect trigger source and backlog. Preserve both answers at each diamond; these are investigation routes, not confirmed causes. Missing listener events can also reflect telemetry configuration, so verify collection before treating silence as host failure.

## See Also

- [First 10 Minutes](first-10-minutes/index.md)
- [Architecture components reference](architecture-components-reference.md)
- [Systematic Troubleshooting Methodology](methodology.md)
- [KQL Query Library](kql/index.md)
- [Functions not executing playbook](playbooks/functions-not-executing.md)
- [High latency / slow responses playbook](playbooks/high-latency.md)
- [Functions failing with errors playbook](playbooks/functions-failing.md)
- [Deployment failures playbook](playbooks/deployment-failures.md)
- [Monitoring](../operations/monitoring.md)

## Sources

- [Azure Functions monitoring](https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring)
- [Azure Functions networking options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options)
- [Azure Functions scale and hosting](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [Application Insights data model](https://learn.microsoft.com/en-us/azure/azure-monitor/app/data-model)
- [Azure Monitor Activity Log](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/activity-log)
- [Isolated worker and in-process models](https://learn.microsoft.com/en-us/azure/azure-functions/dotnet-isolated-process-guide)
- [Functions deployment slots](https://learn.microsoft.com/en-us/azure/azure-functions/functions-deployment-slots)
- [Functions triggers and bindings](https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings)
- [Azure NAT Gateway overview](https://learn.microsoft.com/en-us/azure/nat-gateway/nat-overview)
