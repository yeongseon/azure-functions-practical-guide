---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-event-grid-blob-trigger
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-host-json
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference#configure-an-identity-based-connection
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling
  diagrams:
    - id: core-model
      type: flowchart
      source: self-generated
      justification: Logical cardinality view (one trigger, zero or more input and output bindings per function) adapted from the triggers and bindings concepts article; arrows are data flow, not network connection initiators.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
    - id: event-grid-vs-polling-blob-trigger-model
      type: flowchart
      source: self-generated
      justification: Comparison of the event-based and polling-based Blob trigger implementations adapted from the Blob trigger article (Flex Consumption supports only the event-based implementation); groups show availability, not resource containment.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-event-grid-blob-trigger
    - id: input-output-binding-data-flow-multi-service
      type: flowchart
      source: self-generated
      justification: Illustrative logical data flow for one function with an Event Hubs trigger, a Cosmos DB input binding, Service Bus and Blob output bindings, and Application Insights telemetry, adapted from the binding concepts and per-binding reference articles; not an ordered or atomic transaction.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-hubs-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb-v2-input
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus-output
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-output
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
    - id: queue-trigger-output-pattern-architectural
      type: flowchart
      source: self-generated
      justification: Illustrative HTTP-ingest, queue-output and queue-trigger work flow adapted from the binding concepts and Queue trigger articles; the runtime polls the queue, so arrows are logical work flow, not transport initiators.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue-trigger
    - id: durable-functions-triggers
      type: flowchart
      source: self-generated
      justification: Illustrative runtime-mediated relationships among Durable orchestration, activity and entity triggers adapted from the Durable Functions bindings article; not a direct network call or an execution trace.
      based_on:
        - https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-bindings
content_validation:
  status: verified
  last_reviewed: 2026-09-11
  reviewer: agent
  core_claims:
    - claim: "Each Azure Function has exactly one trigger and can also use input and output bindings"
      source: https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
      verified: true
    - claim: "Flex Consumption uses the Event Grid-based blob trigger model instead of polling"
      source: https://learn.microsoft.com/en-us/azure/azure-functions/functions-event-grid-blob-trigger
      verified: true
    - claim: "Bindings can use identity-based connections configured with service URIs and managed identity settings"
      source: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference#configure-an-identity-based-connection
      verified: true
    - claim: "Azure Functions scaling is driven by the trigger type and workload signal"
      source: https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling
      verified: true
---

# Triggers and Bindings
Triggers and bindings are the core integration abstraction in Azure Functions. A trigger starts execution. Bindings connect your function to external data/services with declarative contracts.

## Prerequisites
Before designing trigger and binding architecture, align these baseline decisions:

- Choose the hosting plan first (Consumption, Flex Consumption, Premium, or Dedicated).
- Confirm trigger compatibility for the selected plan, especially Blob and Event Grid behavior.
- Decide connection strategy per binding:
    - identity-based authentication (recommended for production), or
    - connection-string/key-based authentication (legacy or constrained scenarios).
- Define operational constraints:
    - expected throughput,
    - acceptable end-to-end latency,
    - retry tolerance,
    - ordering requirements.
- Prepare app settings with masked placeholders only.
Example placeholder app settings:
```text
AzureWebJobsStorage=<connection-or-identity-reference>
ServiceBusConnection=<connection-string>
Storage__blobServiceUri=https://<storage-account>.blob.core.windows.net
```
If you validate configuration with Azure CLI, keep long flags for readability:
```bash
az functionapp config appsettings list --resource-group $RG --name $APP_NAME
az functionapp config show --resource-group $RG --name $APP_NAME
```
| Command/Parameter | Purpose |
| --- | --- |
| `az functionapp config appsettings list` | List the application settings on the function app. |
| `--resource-group` | Resource group that contains the resource. |
| `--name` | Name of the target resource. |
| `az functionapp config show` | Show the function app's site configuration. |
| `--resource-group` | Resource group that contains the resource. |
| `--name` | Name of the target resource. |

## Portal Walkthrough

This section shows portal blades relevant to trigger and binding configuration for a live Function App (Consumption Y1, Korea Central). PII is masked.

### Function App Overview (Functions List)

[Observed] The **Overview** blade lists deployed functions with their **Trigger** type and **Status**. Two HTTP-triggered functions are shown: `health` and `hello`, both Enabled. The **Monitor** column links to Application Insights invocation data:

![Function App Overview showing functions list with trigger types](../assets/operations/overview/01-function-app-overview.png)

[Inferred] The trigger type column confirms the binding configuration for each function. After deployment, verify that the expected trigger type appears for each function. Missing or incorrect triggers indicate a binding configuration error in `function.json` or code annotations.

### Environment Variables Blade

[Observed] The **Environment variables** blade shows app settings that provide connection references for bindings: `AzureWebJobsStorage` for host storage, `FUNCTIONS_WORKER_RUNTIME` for the language stack, and `APPINSIGHTS_INSTRUMENTATIONKEY` for monitoring:

![Environment variables blade showing binding-related app settings](../assets/operations/configuration/01-environment-variables.png)

[Inferred] Binding connections resolve from app settings at runtime. For identity-based connections, the setting name pattern changes (e.g., `AzureWebJobsStorage__accountName` instead of a connection string). Missing or misconfigured app settings are the most common cause of binding resolution failures at startup.

## Main Content
### Core model
Every function has:

- exactly **one trigger**,
- zero or more **input bindings**,
- zero or more **output bindings**.
<!-- diagram-id: core-model -->
```mermaid
flowchart TD
    accTitle: Trigger and binding cardinalities
    accDescr: An event source reaches exactly one trigger per function. Zero or more input bindings provide function data; zero or more output bindings connect results to destination services. Arrows describe logical data flow, not network connection initiators.
    S[Event Source] --> T[Trigger\nexactly 1]
    T --> F[Function]
    I[Input Bindings\n0..n] --> F
    F --> O[Output Bindings\n0..n]
    O --> D[Destination Services]
```
### Trigger categories
#### Synchronous triggers
The caller waits for a response.
- HTTP
- Webhook-style integrations
#### Asynchronous triggers
The source posts work and runtime handles completion semantics.
- Storage Queue
- Service Bus
- Event Hubs
- Event Grid
- Blob
- Timer
- Cosmos DB change feed
### Common trigger types
| Trigger | Typical use case | Scaling signal |
|---|---|---|
| HTTP | APIs, webhooks | Concurrent requests and latency |
| Timer | Scheduled jobs | Schedule only (singleton behavior patterns) |
| Queue/Service Bus | Background processing | Backlog length and processing rate |
| Event Hub | Stream ingestion | Partition/event lag |
| Event Grid | Reactive eventing | Event delivery rate |
| Blob | File ingestion | Blob event/polling model by plan |
### Plan-specific trigger considerations
- Flex Consumption supports broad trigger coverage, but **blob trigger uses Event Grid source** instead of polling.
- Classic Consumption supports polling-based blob trigger models.
- Trigger extensions are governed by runtime extension bundle/version support.
!!! warning "Flex Consumption blob trigger"
    Standard polling blob trigger mode is not supported on Flex Consumption. Use the Event Grid-based blob trigger source.
### Event Grid vs polling blob trigger model
Use this comparison when selecting hosting plans for blob-driven workflows.
<!-- diagram-id: event-grid-vs-polling-blob-trigger-model -->
```mermaid
flowchart TD
    accTitle: Event-based and polling-based blob trigger models
    accDescr: Compare two logical detection and invocation paths. Flex Consumption uses Blob Created, Event Grid Event, Functions Runtime and Blob Trigger Function. Classic Consumption, Premium and Dedicated can use Blob Created, Polling Scanner, Functions Runtime and Blob Trigger Function. Groups identify model availability, not physical resource containment; arrows are stage order, not transport direction.
    subgraph FC[Flex Consumption]
        direction TB
        B1[Blob Created] --> EG[Event Grid Event]
        EG --> RT1[Functions Runtime]
        RT1 --> F1[Blob Trigger Function]
    end
    subgraph CL[Classic Consumption, Premium, Dedicated]
        direction TB
        B2[Blob Created] --> POLL[Polling Scanner]
        POLL --> RT2[Functions Runtime]
        RT2 --> F2[Blob Trigger Function]
    end
    %% Layout-only link tiers the two models; it adds no processing step or semantic arrow.
    F1 ~~~ B2
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class B1,EG,RT1,F1,B2,POLL,RT2,F2 baseNeutral;
    linkStyle default stroke-width:2px;
```

**Takeaway:** Read each group as detection → runtime → invocation, not as a hosting or network boundary. The polling scanner detects blob changes; a blob does not initiate a connection to it. Flex requires the Event Grid source; [event-based Blob triggers are also an option on other supported plans](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger#choose-a-blob-storage-trigger-implementation), so the second group is not a polling-only mandate.

### Binding behavior
Bindings reduce plumbing code but still require you to model:

- idempotency,
- retries and duplicate delivery,
- payload schema evolution,
- destination latency and throttling.
Bindings are not a replacement for domain-level error handling.
Recommended behavior guardrails:

- **Message contract**: include `schemaVersion` and enforce required fields.
- **Idempotency key**: upsert by deterministic business key.
- **Poison strategy**: route repeated failures to dead-letter destination.
- **Timeout boundary**: align function timeout with downstream SLA.
### Binding connection configuration
Bindings resolve connection values from app settings. You can use identity-based configuration or connection-string configuration.
| Approach | When to use | Configuration shape | Security posture |
|---|---|---|---|
| Identity-based | Default for production | URI-based settings + managed identity + RBAC | No shared secret in app settings |
| Connection-string based | Legacy migration or unsupported identity path | Single secret setting | Secret rotation and leakage risk |
#### Identity-based example (Storage Queue output)
Binding metadata:
```json
{
  "bindings": [
    {
      "name": "outputQueue",
      "type": "queue",
      "direction": "out",
      "queueName": "orders",
      "connection": "OrdersStorage"
    }
  ]
}
```
App settings:
```text
OrdersStorage__queueServiceUri=https://<storage-account>.queue.core.windows.net
OrdersStorage__credential=managedidentity
```
#### Connection-string example (Storage Queue output)
Binding metadata stays the same:
```json
{
  "bindings": [
    {
      "name": "outputQueue",
      "type": "queue",
      "direction": "out",
      "queueName": "orders",
      "connection": "OrdersStorage"
    }
  ]
}
```
App settings store a secret:
```text
OrdersStorage=DefaultEndpointsProtocol=https;AccountName=<storage-account>;AccountKey=<masked-key>;EndpointSuffix=core.windows.net
```
Decision guidance:

- Prefer identity-based config when supported by the binding extension.
- Use connection strings only when identity is blocked or unavailable.
- Avoid mixing identity and key-based access for the same service unless you are in controlled migration.
### Input/output binding data flow (multi-service)
One trigger can coordinate multiple bindings in one function boundary.
<!-- diagram-id: input-output-binding-data-flow-multi-service -->
```mermaid
flowchart TD
    accTitle: Multi-service input and output binding data flow
    accDescr: An Event Hub trigger and Cosmos DB input binding provide data to one function, which has Service Bus and Blob output bindings and Application Insights telemetry. This illustrative logical data flow does not specify connection initiators, output ordering or atomic fan-out; telemetry is not an output binding.
    EH["Event Hub Trigger"] --> FN[Function]
    COS[("Cosmos DB<br/>Input Binding")] --> FN
    FN --> SB[("Service Bus<br/>Output Binding")]
    FN --> BL[("Blob<br/>Output Binding")]
    FN --> AI>"Application Insights<br/>Telemetry"]
    %% Layout-only links tier outputs; they add no data dependency or semantic arrow.
    SB ~~~ BL
    BL ~~~ AI
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class EH,FN,COS,SB,BL,AI baseNeutral;
    linkStyle default stroke-width:2px;
```

**Takeaway:** The output branches are independent logical destinations, not an ordered transaction. Application Insights is a telemetry sink, not an output binding; [telemetry export depends on monitoring configuration](https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring#collecting-telemetry-data).

Design notes:

- Keep one business responsibility per function.
- If partial fan-out failure is unacceptable, use an outbox pattern.
- Validate downstream idempotency before increasing parallelism.
### Cross-language HTTP trigger examples
=== "Python"
    ```python
    import azure.functions as func

    app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

    @app.route(route="health", methods=["GET"])
    def health(req: func.HttpRequest) -> func.HttpResponse:
        return func.HttpResponse('{"status":"ok"}', mimetype="application/json")
    ```
=== "Node.js"
    ```javascript
    const { app } = require('@azure/functions');

    app.http('health', {
      methods: ['GET'],
      authLevel: 'function',
      handler: async (request, context) => {
        return { jsonBody: { status: 'ok' } };
      }
    });
    ```
=== ".NET (Isolated)"
    ```csharp
    using Microsoft.Azure.Functions.Worker;
    using Microsoft.Azure.Functions.Worker.Http;
    using System.Net;

    public class HealthFunction
    {
        [Function("Health")]
        public HttpResponseData Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", Route = "health")] HttpRequestData req)
        {
            var response = req.CreateResponse(HttpStatusCode.OK);
            response.WriteString("{\"status\":\"ok\"}");
            return response;
        }
    }
    ```
=== "Java"
    ```java
    @FunctionName("health")
    public HttpResponseMessage execute(
        @HttpTrigger(
            name = "req",
            methods = {HttpMethod.GET},
            authLevel = AuthorizationLevel.FUNCTION,
            route = "health")
        HttpRequestMessage<Optional<String>> request,
        final ExecutionContext context) {
        return request.createResponseBuilder(HttpStatus.OK)
            .body("{\"status\":\"ok\"}")
            .build();
    }
    ```
### Queue-trigger + output pattern (architectural)
A common pattern is HTTP ingest + queue output + queue-trigger processor.
<!-- diagram-id: queue-trigger-output-pattern-architectural -->
```mermaid
flowchart TD
    accTitle: HTTP ingestion and queue-triggered processing
    accDescr: Client work reaches an HTTP trigger, then a queue output binding, queue-trigger processor and storage or database. Arrows show logical work flow, not transport initiators: the runtime polls the queue. Backend processing is decoupled from the HTTP response.
    C[Client] --> H[HTTP Trigger]
    H --> Q[(Queue Output Binding)]
    Q --> P[Queue Trigger Processor]
    P --> S["Storage/Database"]
```
This decouples response latency from backend processing.
### Configuration at host level
Bindings and trigger extensions are controlled in `host.json`.
#### Extension bundle version range example
```json
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
```
#### Alternate bundle range for controlled validation
```json
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[3.15.0, 4.0.0)"
  }
}
```
#### Per-trigger concurrency settings example
```json
{
  "version": "2.0",
  "extensions": {
    "queues": {
      "batchSize": 32,
      "newBatchThreshold": 16,
      "maxDequeueCount": 5,
      "visibilityTimeout": "00:00:30"
    },
    "eventHubs": {
      "maxEventBatchSize": 256,
      "prefetchCount": 512,
      "batchCheckpointFrequency": 1
    }
  }
}
```
Tuning guidance:

- Increase `queues.batchSize` only after confirming downstream write capacity.
- Tune `eventHubs.maxEventBatchSize` with partition count and memory limits.
- Change one concurrency lever at a time and compare telemetry windows.
### Authentication levels for HTTP triggers
| Level | Meaning |
|---|---|
| anonymous | No function key required |
| function | Function or host key required |
| admin | Master key required |
Use platform auth (App Service Authentication/Authorization) for user identity scenarios, and keep function keys for service-to-service endpoint control.
### Trigger design checklist
- Use HTTP only when immediate response is required.
- Use async triggers for throughput and resiliency.
- Model retries and poison behavior from day one.
- Validate trigger support against selected hosting plan.
- Keep function boundaries small and idempotent.
### Troubleshooting matrix
| Symptom | Likely Cause | Validation Path |
|---|---|---|
| Trigger not firing | Missing or incorrect connection setting | Verify app setting key, binding `connection` value, and slot-scoped settings |
| Blob trigger delay is high | Polling model used when event-based behavior expected | Confirm plan type and blob trigger source mode |
| Queue backlog keeps growing | Low batch/concurrency or downstream saturation | Compare enqueue/dequeue rates and inspect poison queue |
| Event Hub trigger stalls intermittently | Checkpointing or partition hot-spot issue | Check partition lag and consumer-group ownership |
| HTTP trigger returns 401/403 | Authorization level mismatch or platform auth policy conflict | Validate trigger auth level and App Service auth settings |
| Output binding write fails | Missing RBAC assignment or stale secret | Validate identity role assignment or rotated connection string |
Suggested validation command set:
```bash
az functionapp config appsettings list --resource-group $RG --name $APP_NAME
az functionapp function show --resource-group $RG --name $APP_NAME --function-name $FUNCTION_NAME
az monitor app-insights query --app <application-insights-name> --analytics-query "traces | take 20"
```
| Command/Parameter | Purpose |
| --- | --- |
| `az functionapp config appsettings list` | List the application settings on the function app. |
| `--resource-group` | Resource group that contains the resource. |
| `--name` | Name of the target resource. |
| `az functionapp function show` | Show details of a function. |
| `--resource-group` | Resource group that contains the resource. |
| `--name` | Name of the target resource. |
| `--function-name` | Name of the function. |
| `az monitor app-insights query` | Run a KQL query against Application Insights. |
| `--app` | Application Insights component name. |
| `--analytics-query` | KQL query to run. |

!!! tip "Reliability Guide"
    For retry and poison-message design, see [Reliability](reliability.md).
!!! tip "Language Guide"
    For Python decorator syntax and advanced trigger examples, see [v2 Programming Model](../language-guides/python/v2-programming-model.md).
## Advanced Topics
### Custom bindings
Custom bindings are useful when no first-class extension exists and repeated SDK plumbing creates operational inconsistency.
- Start with native SDK integration first.
- Introduce custom bindings only for stable, repeated integration contracts.
- Version custom binding contracts and publish migration notes.
### Durable Functions triggers
Durable Functions adds orchestration-centric triggers:

- **Orchestration trigger**: coordinates deterministic workflows.
- **Activity trigger**: executes side-effecting units of work.
- **Entity trigger**: provides serialized stateful operations.
<!-- diagram-id: durable-functions-triggers -->
```mermaid
flowchart TD
    accTitle: Durable orchestration, activity and entity trigger relationships
    accDescr: A client or starter reaches orchestration, which schedules Validate and Enrich activities, calls an Aggregate State entity and produces final output. The entity can pass a value back to orchestration. These are illustrative runtime-mediated logical relationships, not direct network calls or a guaranteed ordering of activities.
    C["Client/Starter"] --> O[Orchestration Trigger]
    O --> A1["Activity Trigger:<br/>Validate"]
    O --> A2["Activity Trigger:<br/>Enrich"]
    O --> E["Entity Trigger:<br/>Aggregate State"]
    E --> O
    O --> R[Final Output]
    %% Layout-only links tier destinations; they add no workflow steps or semantic arrows.
    A1 ~~~ A2
    A2 ~~~ E
    E ~~~ R
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class C,O,A1,A2,E,R baseNeutral;
    linkStyle default stroke-width:2px;
```

**Takeaway:** Arrows summarize [Durable runtime-mediated scheduling and value exchange](https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-bindings), not a direct transport or execution trace. Validate and Enrich are distinct activity examples, not a prescribed sequence; the entity-to-orchestration edge represents passing a value through the entity APIs, and Final Output is an orchestration result, not an ordinary output binding.

Keep orchestrator code deterministic and move all I/O into activities.
### Extension bundle versioning strategy
Treat extension bundle upgrades like dependency upgrades with staged rollout:

1. Validate bundle range changes in lower environments with representative load.
2. Compare failure rates, cold start behavior, and throughput.
3. Promote gradually with rollback criteria.
Recommended pattern:

- Pin a compatible major range (for example, `[4.*, 5.0.0)`).
- Avoid unbounded version ranges.
- Revalidate trigger defaults when changing bundle ranges.
### Trigger-specific scaling signals deep dive
Each trigger family scales from different pressure signals:

- **Queue/Service Bus**: backlog, lock renewal pressure, dequeue latency.
- **Event Hubs**: partition lag and ingest velocity.
- **HTTP**: concurrent request pressure and latency percentiles.
- **Timer**: schedule-driven execution, not demand-driven scale.
Design implication:

- Keep trigger-to-workload mapping explicit to preserve useful scale signals.
- Avoid mixing unrelated high-variance workloads behind one trigger unless isolation is not required.
## Language-Specific Details
Use language guides for runtime-specific syntax, decorators/attributes, and package setup:

- [Python v2 Programming Model](../language-guides/python/v2-programming-model.md)
- [Python Recipes: Queue](../language-guides/python/recipes/queue.md)
- [Python Recipes: Blob Storage](../language-guides/python/recipes/blob-storage.md)
- [Python Recipes: Event Grid](../language-guides/python/recipes/event-grid.md)
- [Node.js Guide](../language-guides/nodejs/index.md)
- [Java Guide](../language-guides/java/index.md)
- [.NET Guide](../language-guides/dotnet/index.md)
## See Also
- [Architecture](architecture/index.md)
- [Scaling](scaling.md)
- [Reliability](reliability.md)
- [Hosting Plans](hosting.md)
- [Networking](networking.md)
## Sources
- [Microsoft Learn: Azure Functions triggers and bindings concepts](https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings)
- [Microsoft Learn: Azure Functions Blob storage trigger](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger)
- [Microsoft Learn: Azure Functions Event Grid Blob trigger](https://learn.microsoft.com/en-us/azure/azure-functions/functions-event-grid-blob-trigger)
- [Microsoft Learn: host.json reference for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-host-json)
- [Microsoft Learn: Azure Functions identity-based connections](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference#configure-an-identity-based-connection)
- [Microsoft Learn: Azure Functions scale and hosting behavior](https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling)
- [Microsoft Learn: Durable Functions triggers and bindings](https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-bindings)
- [Microsoft Learn: Queue storage trigger](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue-trigger)
- [Microsoft Learn: Monitor function executions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring)
