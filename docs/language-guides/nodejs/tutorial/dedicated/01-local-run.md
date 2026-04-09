---
hide:
  - toc
validation:
  az_cli:
    last_tested: 2026-04-10
    cli_version: "2.83.0"
    core_tools_version: "4.8.0"
    result: pass
  bicep:
    last_tested: null
    result: not_tested
---

# 01 - Run Locally (Dedicated)

Initialize, run, and verify a Node.js v4 app on your machine before cloud deployment.

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Node.js | 20+ | Local runtime and package execution |
| Azure Functions Core Tools | v4 | Local host and publishing |
| Azure CLI | 2.61+ | Azure resource provisioning and management |

!!! info "Plan basics"
    Dedicated runs on App Service plans (B1/S1/P1v3), supports Always On, and behaves like traditional web app hosting. Unlike Consumption and Premium, you pay for the plan whether or not functions are running.

## What You'll Build

- A Node.js v4 HTTP-triggered function named `helloHttp` running locally with Azure Functions Core Tools.
- Local route validation at `/api/hello/{name?}` confirming a JSON payload response.

!!! info "Infrastructure Context"
    **Plan**: Dedicated (B1) | **Environment**: Local development | **Always On**: ✅ (when deployed)

    Dedicated plans use traditional App Service infrastructure. Locally, the function host behaves identically regardless of target plan.

    ```mermaid
    flowchart TD
        DEV[Developer Machine] -->|func start| HOST[Local Functions Host\nPort 7071]

        subgraph LOCAL["Local Development"]
            HOST
            FUNC[helloHttp\nGET /api/hello]
        end

        HOST --> FUNC
        DEV -->|curl| FUNC

        style HOST fill:#ff8c00,color:#fff
        style LOCAL fill:#E8F5E9,stroke:#4CAF50
        style FUNC fill:#FFF3E0
    ```

## Steps

1. Initialize project.

    ```bash
    func init node-guide-dedicated --worker-runtime node --language javascript
    cd node-guide-dedicated
    npm install @azure/functions
    ```

2. Create the v4 handler.

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

3. Run host and test.

    ```bash
    func start
    ```

    Expected output:

    ```text
    Functions:
        helloHttp: [GET] http://localhost:7071/api/hello/{name?}
    ```

    In a second terminal, test the endpoint:

    ```bash
    curl --request GET "http://localhost:7071/api/hello"
    ```

    Expected output:

    ```json
    {"message":"Hello, world"}
    ```

    ```bash
    curl --request GET "http://localhost:7071/api/hello/Dedicated"
    ```

    Expected output:

    ```json
    {"message":"Hello, Dedicated"}
    ```

4. Review Dedicated-specific notes.

    - Dedicated does not require Azure Files content share settings for zip-based deployments (`WEBSITE_RUN_FROM_PACKAGE=1`).
    - Enable Always On for non-HTTP triggers so timer, queue, and blob workloads stay active.
    - Use long-form CLI flags (for example, `--resource-group`) for maintainable runbooks.
    - Dedicated plans use `az appservice plan create` (not `az functionapp plan create` used by Premium).

## Verification

Confirm that the host lists `helloHttp`, then run `curl --request GET "http://localhost:7071/api/hello"` and verify a `200 OK` response with a JSON body `{"message":"Hello, world"}`.

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
