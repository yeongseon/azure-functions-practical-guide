---
validation:
  az_cli:
    last_tested: 2026-04-10
    cli_version: "2.83.0"
    core_tools_version: "4.8.0"
    result: pass
  bicep:
    last_tested: null
    result: not_tested
content_sources:
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-reference-node
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-triggers-bindings
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/flex-consumption-plan
---

# 07 - Extending Triggers (Flex Consumption)

Add queue, timer, and blob triggers with the Node.js v4 APIs and verify the Functions host indexes each binding.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 20+ | Local runtime and package execution |
| Azure Functions Core Tools | v4 | Local host and publishing |
| Azure CLI | 2.61+ | Azure resource provisioning and management |

!!! info "Flex Consumption plan basics"
    Flex Consumption (FC1) supports VNet integration, identity-based storage, per-function scaling, and remote build workflows.

## What You'll Build

You will add timer, queue, and blob triggers to a Node.js v4 app and verify that the Functions host indexes each binding both locally and in Azure.

!!! info "Infrastructure Context"
    **Plan**: Flex Consumption (FC1) | **Network**: VNet integration supported

    This tutorial adds non-HTTP triggers that require storage queues and blob containers.

    <!-- diagram-id: what-you-ll-build -->
```mermaid
flowchart TD
    TIMER["Timer\n(CRON schedule)"] --> FA[Function App\nFlex Consumption FC1]
    QUEUE["Storage Queue\nwork-items"] --> FA
    BLOB["Blob Container\nuploads/{name}"] --> FA
    FA --> PROCESSED["Blob Container\nprocessed/{name}"]

    style FA fill:#0078d4,color:#fff
    style TIMER fill:#E8F5E9
    style QUEUE fill:#FFF3E0
    style BLOB fill:#E3F2FD
```

<!-- diagram-id: what-you-ll-build-2 -->
```mermaid
flowchart TD
    A[Add timer trigger] --> B[Add queue trigger]
    B --> C[Add blob trigger]
    C --> D[Create storage resources]
    D --> E[Deploy + verify indexing]
```

## Steps

### Step 1 - Set variables (if not already set)

```bash
export RG="rg-func-node-flex-demo"
export APP_NAME="<your-function-app-name>"
export STORAGE_NAME="<your-storage-account-name>"
```

### Step 2 - Add a timer trigger

Save the following as `src/functions/nightlySummary.js`:

```javascript
const { app } = require('@azure/functions');

app.timer('nightlySummary', {
    schedule: '0 0 2 * * *',
    handler: async (_timer, context) => {
        context.log('Nightly summary job fired');
    }
});
```

### Step 3 - Add a queue trigger

Save the following as `src/functions/orderProcessor.js`:

```javascript
const { app } = require('@azure/functions');

app.storageQueue('orderProcessor', {
    queueName: 'work-items',
    connection: 'QueueStorage',
    handler: async (queueItem, context) => {
        context.log(`Order received: ${JSON.stringify(queueItem)}`);
    }
});
```

### Step 4 - Add a blob trigger

Save the following as `src/functions/blobIngest.js`:

```javascript
const { app } = require('@azure/functions');

app.storageBlob('blobIngest', {
    path: 'uploads/{name}',
    connection: 'AzureWebJobsStorage',
    handler: async (blob, context) => {
        context.log(`Blob received, size: ${blob.length} bytes`);
    }
});
```

### Step 5 - Create storage resources

```bash
# Create the queue
az storage queue create \
  --name "work-items" \
  --account-name "$STORAGE_NAME" \
  --auth-mode login

# Create blob containers
az storage container create \
  --name "uploads" \
  --account-name "$STORAGE_NAME" \
  --auth-mode login

az storage container create \
  --name "processed" \
  --account-name "$STORAGE_NAME" \
  --auth-mode login
```

### Step 6 - Verify local trigger indexing

```bash
cd apps/nodejs && func host start
```

### Step 7 - Deploy and verify in Azure

```bash
func azure functionapp publish "$APP_NAME"
```

### Step 8 - Test the queue trigger

```bash
az storage message put \
  --queue-name "work-items" \
  --content '{"orderId":"test-flex-001","item":"widget"}' \
  --account-name "$STORAGE_NAME"
```

!!! note "Queue auth mode"
    If `--auth-mode login` fails with a permissions error, use `--auth-mode key` or pass `--account-key` explicitly. The Storage Queue Data Contributor role is required for login-based queue writes.

### Step 9 - Review Flex Consumption-specific notes

- Flex Consumption supports per-function scaling for queue and blob triggers.
- Use long-form CLI flags for maintainable runbooks.
- Queue triggers on Flex Consumption benefit from per-function scaling — each function can scale independently.

## Verification

Local `func host start` output shows all triggers indexed:

```text
Functions:

    helloHttp: [GET] http://localhost:7071/api/hello/{name?}
    health: [GET] http://localhost:7071/api/health
    nightlySummary: timerTrigger
    orderProcessor: queueTrigger
    blobIngest: blobTrigger
```

Deployed function list:

```bash
az functionapp function list \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --output table
```

## Clean Up

If you are finished with the Flex Consumption tutorials, delete the resource group:

```bash
az group delete --name "$RG" --yes --no-wait
```

## See Also

- [Tutorial Overview & Plan Chooser](../index.md)
- [Node.js Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources

- [Azure Functions Node.js developer guide (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-node)
- [Azure Functions triggers and bindings (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-triggers-bindings)
- [Azure Functions Flex Consumption plan (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/flex-consumption-plan)
