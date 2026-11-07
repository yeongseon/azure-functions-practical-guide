---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-diagnostics
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-diagnostics
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-host-json
  diagrams:
    - id: main-triage-decision-tree
      type: flowchart
      source: self-generated
      justification: Illustrative symptom-first routing to twelve investigation endpoints for first-response triage; branch points are triage cues drawn from the diagnostics and monitoring references, not confirmed causes.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-diagnostics
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
    - id: trigger-specific-decision-tree
      type: flowchart
      source: self-generated
      justification: Illustrative lookup from trigger type to a symptom question and investigation endpoint; cues such as the HTTP 230-second limit and Blob trigger behavior per plan come from the HTTP and Blob trigger references and are triage cues, not proof of cause.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-hubs-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-diagnostics
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-diagnostics
content_validation:
  status: verified
  last_reviewed: 2026-04-12
  reviewer: agent
  core_claims:
    - claim: "진단 방법론 기반 접근"
      source: self-generated
      verified: true
---

# Troubleshooting Decision Tree

Use this page when you need to triage quickly from symptom to likely failure category and then open the right playbook.

The tree is intentionally symptom-first and optimized for the first 10–15 minutes of incident response.

## Main triage decision tree

<!-- diagram-id: main-triage-decision-tree -->
```mermaid
%%{init: {'flowchart': {'nodeSpacing': 5, 'rankSpacing': 35}}}%%
flowchart TD
    accTitle: Symptom-first incident triage
    accDescr: Illustrative routing to investigations, not confirmed causes. No invocations branches through enablement, listener, host, authentication and connection checks. Slow or failing executions branch through cold start, dependency and execution timeouts, failure type, deployment timing and memory signals. All twelve investigation endpoints remain alternatives; evidence and disproof determine the diagnosis.
    S(["Incident starts:<br/>user-visible impact"]) --> Q1{"Functions<br/>executing?"}

    Q1 -->|"No<br/>invocations"| Q1A{"Function enabled and<br/>listener healthy?"}
    Q1 -->|"Yes but<br/>slow/failing"| Q2{"Is it a<br/>latency issue?"}

    Q1A -->|"Function<br/>disabled"| P1(["P1: Not executing"])
    Q1A -->|"Listener failed<br/>to start"| Q1B{"Auth or<br/>connection error?"}
    Q1A -->|"Host not<br/>starting"| P2(["P2: App settings"])

    Q1B -->|"Auth error<br/>401/403"| P3(["P3: Identity / RBAC"])
    Q1B -->|"Connection<br/>error"| P4(["P4: Not executing"])

    Q2 -->|"Yes, high<br/>latency"| Q2A{"Cold start<br/>or dependency?"}
    Q2 -->|"No,<br/>errors/failures"| Q3{"What type<br/>of failure?"}

    Q2A -->|"Cold start<br/>pattern"| P5(["P5: High latency"])
    Q2A -->|"Dependency<br/>timeout"| P6(["P6: Dependency"])
    Q2A -->|"Execution<br/>timeout"| P7(["P7: Timeout"])

    Q3 -->|5xx errors| Q3A{"After deployment?"}
    Q3 -->|"Exception<br/>storm"| P8(["P8: Failing"])
    Q3 -->|"Queue backlog<br/>growing"| P9(["P9: Queue backlog"])

    Q3A -->|Yes| P10(["P10: Deployment"])
    Q3A -->|No| Q4{"Memory or<br/>OOM signals?"}

    Q4 -->|Yes| P11(["P11: Memory / crash"])
    Q4 -->|No| P12(["P12: Methodology"])
    %% Layout-only links tier alternatives; they add no diagnostic steps or arrows.
    P1 ~~~ Q1B
    P3 ~~~ P4
    P4 ~~~ P2
    P2 ~~~ Q2
    P5 ~~~ P6
    P6 ~~~ P7
    P7 ~~~ Q3
    P8 ~~~ P9
    P9 ~~~ Q3A
    P10 ~~~ Q4
    P11 ~~~ P12
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class S,Q1,Q1A,Q1B,Q2,Q2A,Q3,Q3A,Q4,P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11,P12 baseNeutral;
    linkStyle default stroke-width:2px;
```

| Key | Full investigation title / destination |
|---|---|
| P1 | Playbook: [Functions Not Executing](playbooks/functions-not-executing.md) |
| P2 | Playbook: [App Settings Misconfiguration](playbooks/auth-config/app-settings-misconfiguration.md) |
| P3 | Playbook: [Managed Identity / RBAC Failure](playbooks/auth-config/managed-identity-rbac-failure.md) |
| P4 | Playbook: [Functions Not Executing](playbooks/functions-not-executing.md) |
| P5 | Playbook: [High Latency](playbooks/high-latency.md) |
| P6 | Check dependency health |
| P7 | Playbook: [Timeout / Execution Limit Exceeded](playbooks/triggers/timeout-execution-limit.md) |
| P8 | Playbook: [Functions Failing](playbooks/functions-failing.md) |
| P9 | Playbook: [Queue Piling Up](playbooks/queue-piling-up.md) |
| P10 | Playbook: [Deployment Failures](playbooks/deployment-failures.md) |
| P11 | Playbook: [Out of Memory / Worker Crash](playbooks/scaling/out-of-memory-worker-crash.md) |
| P12 | Use Methodology: [build hypotheses from evidence](methodology/troubleshooting-method.md) |

## Trigger-specific decision tree

<!-- diagram-id: trigger-specific-decision-tree -->
```mermaid
%%{init: {'flowchart': {'nodeSpacing': 5, 'rankSpacing': 35}}}%%
flowchart TD
    accTitle: Trigger-specific symptom routing
    accDescr: Illustrative lookup for HTTP, Queue or Service Bus, Blob, Timer, Event Hub and Durable symptoms. Each trigger routes through its pattern question to the named investigation. FC1 and Y1 Blob cases, HTTP timeout at 230 seconds, timer flags and all nine endpoints are retained as triage cues, not proof of cause.
    A(["Trigger type"]) --> B{"Which trigger?"}
    B -->|HTTP| C{"C: Status?"}
    B -->|"Queue/<br/>Service<br/>Bus"| D{"D: Work?"}
    B -->|Blob| E{"E: Delivery?"}
    B -->|Timer| F{"F: Due?"}
    B -->|"Event<br/>Hub"| G{"G: Lag?"}
    B -->|Durable| H{"H: State?"}

    C -->|"5xx<br/>spike"| I(["I: Failing"])
    C -->|"Timeout<br/>230s"| J(["J: Timeout"])
    D -->|"Backlog<br/>growing"| K(["K: Backlog"])
    D -->|"Poison<br/>messages"| L(["L: Failing"])
    E -->|"Not firing<br/>on FC1"| M(["M: Blob trigger"])
    E -->|"Delayed<br/>on Y1"| N(["N: Blob trigger"])
    F -->|"Missed<br/>executions"| O(["O: Timer flags"])
    G -->|"Checkpoint<br/>behind"| P(["P: Lag"])
    H -->|"Stuck in<br/>Running"| Q(["Q: Stuck"])
    %% Layout-only links tier trigger families; they add no diagnostic steps or arrows.
    I ~~~ J
    J ~~~ D
    K ~~~ L
    L ~~~ E
    M ~~~ N
    N ~~~ F
    O ~~~ G
    P ~~~ H
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q baseNeutral;
    linkStyle default stroke-width:2px;
```

| Key | Full pattern question |
|---|---|
| C | Status code pattern |
| D | Processing pattern |
| E | Event delivery |
| F | Schedule pattern |
| G | Lag pattern |
| H | Orchestration state |

| Key | Full outcome / destination |
|---|---|
| I | [Functions Failing](playbooks/functions-failing.md) |
| J | [Timeout / Execution Limit](playbooks/triggers/timeout-execution-limit.md) |
| K | [Queue Piling Up](playbooks/queue-piling-up.md) |
| L | [Functions Failing](playbooks/functions-failing.md) |
| M | [Blob Trigger Not Firing](playbooks/blob-trigger-not-firing.md) |
| N | [Blob Trigger Not Firing](playbooks/blob-trigger-not-firing.md) |
| O | Check isPastDue and RunOnStartup |
| P | [Event Hub / Service Bus Lag](playbooks/triggers/event-hub-service-bus-lag.md) |
| Q | [Durable Orchestration Stuck](playbooks/scaling/durable-orchestration-stuck.md) |

## Playbook leaves (direct links)

### Triggers
- [Timeout / Execution Limit Exceeded](playbooks/triggers/timeout-execution-limit.md)
- [Event Hub / Service Bus Lag](playbooks/triggers/event-hub-service-bus-lag.md)

### Scaling
- [Out of Memory / Worker Crash](playbooks/scaling/out-of-memory-worker-crash.md)
- [Durable Orchestration Stuck](playbooks/scaling/durable-orchestration-stuck.md)

### Auth / Config
- [Managed Identity / RBAC Failure](playbooks/auth-config/managed-identity-rbac-failure.md)
- [App Settings Misconfiguration](playbooks/auth-config/app-settings-misconfiguration.md)

### General
- [Functions Not Executing](playbooks/functions-not-executing.md)
- [High Latency](playbooks/high-latency.md)
- [Functions Failing](playbooks/functions-failing.md)
- [Queue Piling Up](playbooks/queue-piling-up.md)
- [Blob Trigger Not Firing](playbooks/blob-trigger-not-firing.md)
- [Deployment Failures](playbooks/deployment-failures.md)

## Quick reference matrix

| Symptom Pattern | Most Likely Cause Category | Playbook Link |
|---|---|---|
| Zero invocations despite active source | Disabled function, listener failure, or host not starting | [Functions Not Executing](playbooks/functions-not-executing.md) |
| 5xx errors after deployment | Deployment artifact or config regression | [Deployment Failures](playbooks/deployment-failures.md) |
| High P95 latency, normal P50 | Cold start or intermittent dependency | [High Latency](playbooks/high-latency.md) |
| Execution timeout errors | Function exceeds plan timeout limit | [Timeout / Execution Limit](playbooks/triggers/timeout-execution-limit.md) |
| Queue depth rising, executions flat | Trigger stall or scaling bottleneck | [Queue Piling Up](playbooks/queue-piling-up.md) |
| Blob trigger not firing on FC1 | Missing Event Grid subscription | [Blob Trigger Not Firing](playbooks/blob-trigger-not-firing.md) |
| 401/403 on dependency calls | Managed identity or RBAC misconfiguration | [Managed Identity / RBAC Failure](playbooks/auth-config/managed-identity-rbac-failure.md) |
| Host fails to start, no functions found | Missing or wrong app settings | [App Settings Misconfiguration](playbooks/auth-config/app-settings-misconfiguration.md) |
| Worker crashes under load | Memory exhaustion | [Out of Memory / Worker Crash](playbooks/scaling/out-of-memory-worker-crash.md) |
| Durable orchestration stuck in Running | Replay storm or non-deterministic code | [Durable Orchestration Stuck](playbooks/scaling/durable-orchestration-stuck.md) |
| Event Hub/Service Bus processing falling behind | Checkpoint lag or slow processing | [Event Hub / Service Bus Lag](playbooks/triggers/event-hub-service-bus-lag.md) |
| Repeated exceptions dominating failures | Application code error | [Functions Failing](playbooks/functions-failing.md) |

## Triage prompts to ask in order

1. Are functions executing at all? If no, is the function enabled and listener healthy?
2. Was there a recent deployment or configuration change in the incident window?
3. Is it a latency issue (slow) or a failure issue (errors)?
4. Is the issue specific to one trigger type or affecting all functions?
5. Are there memory pressure or OOM signals in the logs?

## Minimal evidence before choosing a branch

- 15-minute function execution trend (`requests` table)
- Host lifecycle events for restarts/startups (`traces` table)
- Recent Activity Log operations

```kusto
let appName = "func-myapp-prod";
requests
| where timestamp > ago(2h)
| where cloud_RoleName =~ appName
| where operation_Name startswith "Functions."
| summarize total=count(), err=countif(success == false), p95=percentile(duration, 95) by bin(timestamp, 5m)
| order by timestamp asc
```

```kusto
let appName = "func-myapp-prod";
traces
| where timestamp > ago(24h)
| where cloud_RoleName =~ appName
| where message has_any ("Host started", "Host shutdown", "restart", "listener", "unable to start", "timeout")
| project timestamp, message
| order by timestamp desc
```

```bash
az monitor activity-log list \
  --resource-group "$RG" \
  --offset 24h \
  --max-events 20 \
  --output table
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az monitor activity-log list` |
| Key flags | `--resource-group`, `--offset`, `--max-events`, `--output` |
| Variables | `$RG` |
| Expected result | Azure CLI returns the requested resource data; verify names, IDs, status fields, or metric values match the scenario. |


!!! warning "Avoid branch bias"
    Do not choose a branch only because it matches a familiar past issue.
    If the first branch is disproven by timestamps, return to the top and re-classify.
    Decision trees accelerate triage, but evidence still decides root cause.

## Decision Tree Limits

- This tree is optimized for Azure Functions serverless workloads.
- Multi-cause incidents can map to more than one branch.
- If no branch matches cleanly, use [Troubleshooting Method](methodology/troubleshooting-method.md) and build explicit competing hypotheses.

## Branch-specific first checks

### If you choose the trigger branch

- Confirm function is enabled and listener started.
- Check trigger-specific connection strings and auth.
- For blob triggers on FC1, verify Event Grid subscription exists.

### If you choose the latency branch

- Compare cold start frequency against latency pattern.
- Check dependency P95 for single-target bottleneck.
- Verify `functionTimeout` in host.json matches plan limits.

### If you choose the failure branch

- Correlate error onset with deployment timestamps.
- Check for dominant exception type in `exceptions` table.
- Verify app settings (especially `FUNCTIONS_WORKER_RUNTIME`, `AzureWebJobsStorage`).

## Practical triage examples

1. **Zero invocations + listener unable to start + 403 error**
    - Decision tree branch: not executing → listener failed → auth error.
    - Start with [Managed Identity / RBAC Failure](playbooks/auth-config/managed-identity-rbac-failure.md).

2. **Deployment succeeded + immediate 500 errors + no functions found**
    - Decision tree branch: errors → after deployment → config issue.
    - Start with [App Settings Misconfiguration](playbooks/auth-config/app-settings-misconfiguration.md).

3. **Queue depth growing over hours + worker restarts + OOM exceptions**
    - Decision tree branch: queue backlog → memory signals.
    - Start with [Out of Memory / Worker Crash](playbooks/scaling/out-of-memory-worker-crash.md).

## See Also

- [Troubleshooting Method](methodology/troubleshooting-method.md)
- [Detector Map](methodology/detector-map.md)
- [Request flow for incident response](request-flow-for-incident-response.md)
- [Evidence Map](evidence-map.md)
- [Mental Model](mental-model.md)
- [First 10 Minutes: Triggers Not Firing](first-10-minutes/triggers-not-firing.md)
- [First 10 Minutes: High Latency](first-10-minutes/high-latency.md)
- [First 10 Minutes: Scaling Issues](first-10-minutes/scaling-issues.md)

## Sources

- [Azure Functions diagnostics overview](https://learn.microsoft.com/en-us/azure/azure-functions/functions-diagnostics)
- [Monitor Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring)
- [Troubleshoot Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-diagnostics)
- [Azure Functions host.json reference](https://learn.microsoft.com/en-us/azure/azure-functions/functions-host-json)
