# Queue Processing

Queue trigger processing with retries, poison handling, and idempotent writes.

## Main Content

```mermaid
flowchart LR
    A[Client or Event Source] --> B[Node.js v4 handler]
    B --> C[Business logic]
    C --> D[Azure service integration]
```

### Node.js v4 Example

```javascript
const { app } = require('@azure/functions');

app.storageQueue('queueWorker', { queueName: 'work-items', handler: async (queueItem, context) => { context.log(`Work item ${queueItem.id}`); } });
```

### Implementation Notes

- Use `context.log()` for invocation-scoped telemetry.
- Prefer managed identity to avoid secret distribution.
- Return explicit status codes for deterministic client behavior.

## See Also
- [Recipes Index](index.md)
- [Node.js v4 Programming Model](../v4-programming-model.md)
- [Troubleshooting](../troubleshooting.md)

## Sources
- [Azure Functions Node.js developer guide (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-node)
- [Azure Functions trigger and binding concepts (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-triggers-bindings)
