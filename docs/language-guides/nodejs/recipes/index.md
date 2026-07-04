---
content_sources:

  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
  diagrams:
    - id: recipe-categories
      type: flowchart
      source: self-generated
      justification: Flow view of recipe categories, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
---
# Node.js Recipes

The recipes section provides implementation-focused patterns for common integration scenarios in Azure Functions Node.js v4 apps.

## Recipe Categories

<!-- diagram-id: recipe-categories -->
```mermaid
flowchart TD
    A[Recipes] --> B[HTTP]
    A --> C[Data]
    A --> D[Security]
    A --> E[Eventing]
```

| Category | Recipes |
|---|---|
| HTTP | [HTTP API](http-api.md), [HTTP Auth](http-auth.md) |
| Data | [Cosmos DB](cosmosdb.md), [Blob Storage](blob-storage.md), [Queue](queue.md) |
| Security | [Key Vault](key-vault.md), [Managed Identity](managed-identity.md), [Custom Domains and Certificates](custom-domain-certificates.md) |
| Eventing | [Timer](timer.md), [Durable Orchestration](durable-orchestration.md), [Event Grid](event-grid.md) |

## See Also
- [Node.js Language Guide](../index.md)
- [Node.js Tutorials](../tutorial/index.md)
- [Troubleshooting](../troubleshooting.md)

## Sources
- [Azure Functions trigger and binding concepts (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings)
