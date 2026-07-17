---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/storage-considerations
---
# Glossary

Definitions of core Azure Functions terms used throughout this guide. Terms are grouped by domain; within each group they are ordered alphabetically.

## Runtime and Hosting

| Term | Definition |
|------|------------|
| **Function** | A single, independently triggered unit of code deployed within a function app. |
| **Function app** | The deployment and management unit that hosts one or more functions sharing the same configuration, runtime, and hosting plan. |
| **Functions host** | The runtime process that loads the function app, manages the language worker, and dispatches trigger events to functions. |
| **Language worker** | A separate process (Python, Node.js, Java, or .NET isolated) that runs your function code and communicates with the Functions host over gRPC. |
| **In-process model** | Legacy .NET model where function code runs inside the Functions host process. Superseded by the isolated worker model. |
| **Isolated worker model** | The current .NET model where function code runs in a separate worker process, decoupled from the host runtime version. |
| **Consumption plan (Y1)** | Serverless, event-driven hosting that scales to zero and bills per execution. Legacy default for new workloads. |
| **Flex Consumption plan (FC1)** | Serverless plan with fast/large scale-out, VNet integration, and per-instance concurrency control. Recommended default for most new workloads. |
| **Premium plan (EP)** | Plan with always-ready (pre-warmed) instances, VNet integration, and no cold start for warm instances. |
| **Dedicated plan (App Service plan)** | Fixed-capacity hosting on an App Service plan, suitable for reusing an existing App Service estate. |

## Triggers and Bindings

| Term | Definition |
|------|------------|
| **Trigger** | The event that causes a function to run (for example an HTTP request, a queue message, or a timer schedule). Each function has exactly one trigger. |
| **Binding** | A declarative connection to data or a service. Input bindings supply data to a function; output bindings send data from a function. |
| **Binding extension** | A NuGet/npm/pip package that provides a specific trigger or binding type (for example the Service Bus or Event Hubs extension). |
| **Extension bundle** | A versioned set of binding extensions declared in `host.json` so non-.NET apps do not manage individual extension packages. |
| **Poison message** | A message that repeatedly fails processing and is moved to a poison/dead-letter location after the maximum dequeue/delivery count is reached. |

## Scaling

| Term | Definition |
|------|------------|
| **Scale controller** | The Azure component that monitors trigger activity and decides when to add or remove function app instances. |
| **Target-based scaling** | A scaling model that computes desired instance count from queue/stream backlog and per-instance target, allowing faster scale-out than incremental scaling. |
| **Always-ready instance** | A pre-provisioned Premium/Flex instance kept warm to eliminate cold start for a baseline of concurrent executions. |
| **Per-instance concurrency** | The number of concurrent invocations a single instance handles before the platform scales out (configurable on Flex Consumption). |
| **Cold start** | The added latency when a request is served by a newly allocated instance that must initialize the host, worker, and dependencies. |
| **Scale to zero** | The behavior of serverless plans that remove all instances when there is no work, eliminating idle cost. |

## Storage

| Term | Definition |
|------|------------|
| **AzureWebJobsStorage** | The storage account connection setting the Functions runtime uses for internal state such as triggers, leases, and logs. |
| **Content share** | The Azure Files share that stores the deployed application content for Consumption and Premium plans. |
| **Deployment package** | The zipped application artifact. On Flex Consumption it is stored in a blob container and mounted at runtime. |
| **Lease** | A storage-based lock used to coordinate singleton behavior and trigger ownership across instances. |

## Networking

| Term | Definition |
|------|------------|
| **VNet integration** | A feature that lets a function app make outbound calls into an Azure virtual network. |
| **Private endpoint** | A network interface that exposes an Azure service (including a function app or its storage) with a private IP inside a VNet. |
| **Service endpoint** | A VNet feature that secures an Azure service to specific subnets over the Azure backbone without a private IP. |
| **Fixed outbound IP** | A predictable egress IP for a function app, typically achieved with VNet integration and a NAT gateway. |
| **Private DNS zone** | A DNS zone that resolves a service's hostname to its private endpoint IP inside a VNet. |

## Security

| Term | Definition |
|------|------------|
| **Managed identity** | An Azure-managed Microsoft Entra identity assigned to a function app for passwordless authentication to other Azure services. |
| **System-assigned identity** | A managed identity whose lifecycle is tied to a single function app. |
| **User-assigned identity** | A standalone managed identity that can be shared across multiple resources. |
| **Function access key** | A shared secret that authorizes calls to an HTTP-triggered function or the app's admin endpoints. |
| **Authorization level** | The access requirement for an HTTP trigger: `anonymous`, `function`, or `admin`. |

## Deployment and Operations

| Term | Definition |
|------|------------|
| **Deployment slot** | A separate, addressable instance of a function app used for staging and zero-downtime swaps. |
| **Zip deploy / run-from-package** | Deployment mechanisms that publish the app as a package, with run-from-package mounting it read-only. |
| **Kudu / SCM** | The advanced deployment and diagnostics site for App Service and Functions apps (not available on Flex Consumption). |
| **Application setting** | A key/value configuration entry exposed to the app as an environment variable. |

## Observability

| Term | Definition |
|------|------------|
| **Application Insights** | The Azure Monitor telemetry service that collects requests, dependencies, traces, exceptions, and metrics from a function app. |
| **Live Metrics** | A near-real-time stream of request, dependency, and performance metrics in Application Insights. |
| **Distributed tracing** | Correlation of a single logical operation across functions, bindings, and downstream dependencies using trace context. |
| **Sampling** | A telemetry-volume control that records a representative subset of events to manage cost. |

## See Also

- [Platform Limits](platform-limits.md)
- [host.json Reference](host-json.md)
- [Environment Variables](environment-variables.md)
- [Platform: Triggers and Bindings](../platform/triggers-and-bindings.md)

## Sources

- [Azure Functions overview (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview)
- [Azure Functions triggers and bindings (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings)
- [Azure Functions event-driven scaling (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [Azure Functions storage considerations (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/storage-considerations)
</content>
</invoke>
