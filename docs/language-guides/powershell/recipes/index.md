---
content_sources:
  diagrams:
    - id: powershell-recipes
      type: graph
      source: self-generated
      justification: Category view of the PowerShell recipes, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices
---
# PowerShell Recipes

The Recipes section provides implementation-focused patterns for common Azure Functions integrations in PowerShell.

Use these documents when you already understand the platform basics and need practical, reusable building blocks. PowerShell functions use the classic `function.json` binding model with `param` inputs and `Push-OutputBinding` outputs.

<!-- diagram-id: powershell-recipes -->
```mermaid
graph TD
    A[PowerShell Recipes] --> B[HTTP]
    A --> C[Storage & Messaging]
    A --> D[Security]
    A --> E[Scheduling]
    A --> F[Orchestration]
    A --> G[API & Quality]
```

!!! tip "Pair recipes with platform guidance"
    For architecture and plan behavior that applies across all languages, see [Platform](../../../platform/index.md).

## Recipe categories

### HTTP

| Recipe | Description |
|--------|-------------|
| [HTTP API Patterns](http-api.md) | Route design, request parsing, and structured responses with `HttpResponseContext`. |
| [HTTP Authentication](http-auth.md) | Function auth levels, function keys, and token validation patterns. |

### Storage & Messaging

| Recipe | Description |
|--------|-------------|
| [Blob Storage](blob-storage.md) | Blob trigger and blob binding patterns for file processing. |
| [Queue Storage](queue.md) | Queue trigger consumer patterns and output bindings. |
| [Service Bus](service-bus.md) | Enterprise messaging with queue/topic triggers and dead-lettering. |
| [Event Hubs](event-hub.md) | High-throughput stream ingestion with batch triggers. |
| [Event Grid](event-grid.md) | Reactive handling of discrete events and custom topics. |
| [Cosmos DB](cosmosdb.md) | Change feed trigger and item input/output bindings. |
| [Table Storage](table-storage.md) | Structured NoSQL entity read/write bindings. |
| [SignalR Service](signalr.md) | Real-time messaging with negotiate and broadcast bindings. |

### Security

| Recipe | Description |
|--------|-------------|
| [Key Vault](key-vault.md) | Secret retrieval using Key Vault references and the Az module. |
| [Managed Identity](managed-identity.md) | Passwordless authentication via `Connect-AzAccount -Identity`. |

### Scheduling

| Recipe | Description |
|--------|-------------|
| [Timer Trigger](timer.md) | Scheduled jobs, cron semantics, and idempotent batch execution. |

### Orchestration

| Recipe | Description |
|--------|-------------|
| [Durable Orchestration](durable-orchestration.md) | Client, orchestrator, and activity functions for long-running workflows. |
| [Durable Advanced Patterns](durable-advanced.md) | Fan-out/fan-in, external events, durable timers, and eternal orchestrations. |

### API & Quality

| Recipe | Description |
|--------|-------------|
| [Retries and Error Handling](retry.md) | Retry policies, defensive error handling, and idempotency. |
| [OpenAPI Documentation](openapi.md) | Serve an API contract from a dedicated HTTP endpoint. |
| [Testing](testing.md) | Unit-test function logic with Pester. |
| [Custom Domain and Certificates](custom-domain-certificates.md) | HTTPS custom domains and TLS certificate binding. |

!!! note "Not applicable in the PowerShell model"
    Some recipes available for other languages have no idiomatic PowerShell equivalent:

    - **Dependency injection** — PowerShell has no DI container. Share initialized state (clients, config) through `profile.ps1` and module-scoped variables instead.
    - **Middleware** — PowerShell has no invocation pipeline. Put cross-cutting logic (logging, auth checks) in `profile.ps1` or shared helper modules imported by each function.
    - **Durable entities** — Entity triggers and clients are not supported for PowerShell. Use orchestrations with external storage for stateful coordination. See [Durable Advanced Patterns](durable-advanced.md).

## How to consume recipes effectively

1. Start from your trigger pattern (HTTP, timer, queue, blob, Service Bus).
2. Apply security baseline patterns first (Managed Identity and Key Vault).
3. Validate hosting-plan constraints in [Platform: Hosting](../../../platform/hosting.md).
4. Add monitoring/alerts using [Operations](../../../operations/index.md) guidance.

## See Also

- [PowerShell Language Guide](../index.md)
- [PowerShell Tutorial](../tutorial/index.md)
- [Platform: Triggers and Bindings](../../../platform/triggers-and-bindings.md)
- [Troubleshooting](../troubleshooting.md)

## Sources

- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
- [Azure Functions trigger and binding concepts (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings)
- [Azure Functions best practices (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices)
