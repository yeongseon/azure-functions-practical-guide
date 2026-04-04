# Python Recipes

The Recipes section provides implementation-focused patterns for common Azure Functions integrations in Python.

Use these documents when you already understand the platform basics and need practical, reusable building blocks.

!!! tip "Pair recipes with platform guidance"
    For architecture and plan behavior that applies across all languages, see [Platform](../../../platform/index.md).

## Recipe categories

### HTTP

| Recipe | Description |
|--------|-------------|
| [HTTP API Patterns](http-api.md) | Route design, request/response patterns, and API-friendly function composition. |
| [HTTP Authentication](http-auth.md) | Function auth levels, app-level auth, and token validation integration patterns. |

### Storage

| Recipe | Description |
|--------|-------------|
| [Cosmos DB](cosmosdb.md) | Input/output patterns for Cosmos DB-backed APIs and event processing workloads. |
| [Blob Storage](blob-storage.md) | Blob trigger and blob binding patterns, including production-oriented processing flow. |
| [Queue Storage](queue.md) | Queue trigger consumer patterns, retries, and output binding usage. |

### Security

| Recipe | Description |
|--------|-------------|
| [Key Vault](key-vault.md) | Secret and configuration retrieval patterns using Key Vault integration. |
| [Managed Identity](managed-identity.md) | Passwordless authentication from Functions to Azure services via Entra identities. |
| [Custom Domains & Certificates](custom-domain-certificates.md) | TLS and custom hostname setup considerations for HTTP-facing workloads. |

### Advanced

| Recipe | Description |
|--------|-------------|
| [Timer Trigger](timer.md) | Scheduled jobs, cron semantics, and idempotent batch execution patterns. |
| [Durable Functions](durable-orchestration.md) | Orchestration, fan-out/fan-in, and stateful workflow coordination. |
| [Event Grid](event-grid.md) | Event-driven designs and event routing patterns for reactive systems. |

## How to consume recipes effectively

1. Start from your trigger pattern (HTTP, timer, queue, blob, Event Grid).
2. Apply security baseline patterns first (Managed Identity and Key Vault).
3. Validate hosting-plan constraints in [Platform: Hosting](../../../platform/hosting.md).
4. Add monitoring/alerts using [Operations](../../../operations/index.md) guidance.

## Official references

- [Python developer guide](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Functions trigger and binding concepts](https://learn.microsoft.com/azure/azure-functions/functions-triggers-bindings)
- [Azure Functions best practices](https://learn.microsoft.com/azure/azure-functions/functions-best-practices)

## See Also

- [Python Language Guide](../index.md)
- [Python Tutorial](../tutorial/index.md)
- [Platform: Triggers and Bindings](../../../platform/triggers-and-bindings.md)
- [Troubleshooting](../troubleshooting.md)
