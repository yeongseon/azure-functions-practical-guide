# Node.js Language Guide

This guide introduces Azure Functions for Node.js using the **v4 programming model**.

In v4, functions are registered directly in code with APIs such as `app.http()` and `app.timer()`, which is a major shift from older folder-based patterns.

## Current scope in this hub

This page is a roadmap-backed starter for Node.js. It includes:

- Worker/programming model overview
- Runtime support baseline
- Python-to-Node.js mental model mapping
- A minimal HTTP trigger quick start
- Planned content tracks for full parity

## Official reference

- [Azure Functions Node.js developer guide (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-node)

!!! note "Source of truth"
    Runtime/version support and binding capabilities should be validated against Microsoft Learn for production decisions.

## Node.js model at a glance

| Topic | Node.js v4 |
|------|-------------|
| Registration style | Code-first function registration |
| HTTP trigger API | `app.http()` |
| Timer trigger API | `app.timer()` |
| Queue trigger API | `app.storageQueue()` |
| Worker model | Out-of-process language worker via Azure Functions host |
| Supported runtimes | Node.js 18, 20, 22 |

## Key differences from Python v2 model

| Concern | Python | Node.js |
|--------|--------|---------|
| App object | `func.FunctionApp()` | `app` from `@azure/functions` |
| HTTP declaration | `@app.route(...)` decorator | `app.http(name, { ... })` |
| Timer declaration | `@app.timer_trigger(...)` decorator | `app.timer(name, { ... })` |
| Handler signature | Python function with typed params | JavaScript/TypeScript handler with request/context |
| Package management | `requirements.txt` | `package.json` |

## Quick start: HTTP trigger (Node.js v4 model)

```javascript
const { app } = require('@azure/functions');

app.http('helloHttp', {
    methods: ['GET'],
    authLevel: 'function',
    route: 'hello/{name?}',
    handler: async (request, context) => {
        const name = request.params.name || request.query.get('name') || 'world';
        context.log(`Processed request for ${name}`);
        return {
            status: 200,
            jsonBody: {
                message: `Hello, ${name}!`,
                runtime: 'Azure Functions Node.js v4'
            }
        };
    }
});
```

### What this example demonstrates

- Code-first registration with `app.http()`.
- Optional route parameter + query fallback.
- Structured response object with status and JSON body.
- Logging through function execution context.

## Planned content (Coming Soon)

- **Tutorial track**: local run, first deploy, configuration, monitoring, IaC, CI/CD, trigger expansion.
- **Recipes**: HTTP auth, Storage patterns, Cosmos DB, Key Vault, Managed Identity, Event Grid.
- **Reference docs**: runtime/version guide, host configuration mapping, troubleshooting baseline.
- **Reference app**: `apps/nodejs/` parity implementation with the Python app capabilities.

!!! tip "Use platform docs now"
    Until full Node.js tracks are published, pair this page with [Platform](../../platform/index.md) and [Operations](../../operations/index.md) to make architecture and production decisions.

## Cross-language links

- [Language Guides overview](../index.md)
- [Python guide (reference implementation)](../python/index.md)
- [.NET guide](../dotnet/index.md)
- [Java guide](../java/index.md)

## See Also

- [Platform: Architecture](../../platform/architecture.md)
- [Platform: Hosting](../../platform/hosting.md)
- [Operations: Deployment](../../operations/deployment.md)
- [Operations: Monitoring](../../operations/monitoring.md)
