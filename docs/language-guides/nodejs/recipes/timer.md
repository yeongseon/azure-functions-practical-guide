# Timer Jobs

Deterministic schedules, idempotency keys, and batch maintenance jobs.

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

app.timer('nightlyCleanup', { schedule: '0 0 1 * * *', handler: async (_timer, context) => { context.log('cleanup started'); } });
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
