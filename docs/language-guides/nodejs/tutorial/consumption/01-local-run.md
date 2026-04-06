# 01 - Run Locally (Consumption)

Initialize, run, and verify a Node.js v4 app on your machine before cloud deployment.

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Node.js | 20+ | Local runtime and package execution |
| Azure Functions Core Tools | v4 | Local host and publishing |
| Azure CLI | 2.61+ | Azure resource provisioning and management |

!!! info "Plan basics"
    Consumption scales to zero automatically, does not support VNet integration, and defaults to a 5-minute timeout with a 10-minute maximum.

## What You'll Build

A single Node.js v4 HTTP-triggered function named `helloHttp` that runs locally on the Consumption track and returns a JSON response from `/api/hello/{name?}`.

## Steps

```mermaid
flowchart LR
    A[func init project] --> B[Create v4 handler]
    B --> C[func start]
    C --> D[Test with curl]
```


### Step 1 - Initialize project

```bash
func init node-guide-consumption --worker-runtime node --language javascript
cd node-guide-consumption
npm install @azure/functions
```

### Step 2 - Create the v4 handler

Save the following as `src/functions/helloHttp.js`:
```javascript
const { app } = require('@azure/functions');

app.http('helloHttp', {
    methods: ['GET'],
    route: 'hello/{name?}',
    handler: async (request, context) => {
        const name = request.params.name || request.query.get('name') || 'world';
        context.log(`Handled hello for ${name}`);
        return { status: 200, jsonBody: { message: `Hello, ${name}` } };
    }
});
```

### Step 3 - Run host and test

```bash
func start
```

In a second terminal, test the endpoint:

```bash
curl --request GET "http://localhost:7071/api/hello"
```

### Step 4 - Review Consumption-specific notes

- Consumption defaults to a 5-minute timeout (10-minute maximum). Design functions accordingly.
- Use long-form CLI flags (`--resource-group`, not `-g`) for maintainable runbooks.
- Keep `FUNCTIONS_WORKER_RUNTIME=node` aligned between `local.settings.json` for local development and Azure application settings in deployed environments.

## Verification

```text
Functions:
    helloHttp: [GET] http://localhost:7071/api/hello/{name?}
```

Confirm that the host lists `helloHttp`, then run `curl --request GET "http://localhost:7071/api/hello"` and verify a `200 OK` response with a JSON body such as `{"message":"Hello, world"}`.

## Next Steps

> **Next:** [02 - First Deploy](02-first-deploy.md)



## See Also
- [Tutorial Overview & Plan Chooser](../index.md)
- [Node.js Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources
- [Azure Functions Node.js developer guide (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-node)
- [Create your first Azure Function with Core Tools (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/create-first-function-cli-node)
- [Azure Functions hosting options (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-scale)
