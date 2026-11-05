---
validation:
  az_cli:
    last_tested: 2026-04-10
    cli_version: 2.83.0
    core_tools_version: 4.8.0
    result: pass
  bicep:
    last_tested:
    result: not_tested
content_sources:

  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-node
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-node
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
  diagrams:
    - id: what-you-ll-build
      type: flowchart
      source: self-generated
      justification: Flow view of what you ll build, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-node
        - https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-node
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
        - https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan#always-on
---
# 07 - Extending Triggers (Dedicated)

Add queue, timer, and blob triggers with the Node.js v4 APIs and deploy to Dedicated.

## Prerequisites

- You completed [06 - CI/CD](06-ci-cd.md).
- Your function app `$APP_NAME` is deployed and running on the Dedicated plan.

## What You'll Build

- Extend your app with timer, queue, and blob triggers using the Node.js v4 programming model.
- Deploy all triggers to Dedicated and verify they index correctly.
- Understand Always On requirements for non-HTTP triggers on Dedicated plans.

!!! info "Infrastructure Context"
    **Plan**: Dedicated (B1) | **Triggers**: HTTP + Timer + Queue + Blob + EventHub | **Always On**: Enable for reliable non-HTTP triggering

    Enable [Always On](https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan#always-on) for reliable non-HTTP triggering on Dedicated hosting. Without it, the app may idle; an HTTP request or portal access can wake it. The reference app includes 20 functions across all trigger types.

<!-- diagram-id: what-you-ll-build -->
```mermaid
%%{init: {'flowchart': {'nodeSpacing': 10}}}%%
flowchart TD
    accTitle: Node.js Dedicated trigger overview and Always On
    accDescr: Conceptual timer, queue, blob, HTTP and Event Hub trigger paths to the Node.js v4 Dedicated B1 app and its Always On setting. Enable Always On for reliable non-HTTP triggering; an idled app without it can wake on an HTTP request or portal access. Source arrows associate independent triggers with the app, not a network topology or sequential execution; the Always On arrow identifies configuration, not app output.
    TIMER["Timer Trigger<br/>scheduledCleanup<br/>timerLab"] -->|"CRON<br/>schedule"| FA["Function App<br/>Dedicated B1"]
    QUEUE["Queue Trigger<br/>queueProcessor"] -->|"Queue<br/>message"| FA
    BLOB["Blob Trigger<br/>blobProcessor"] -->|"Blob<br/>event"| FA
    HTTP["HTTP Triggers<br/>helloHttp, health<br/>info, logLevels"] -->|HTTPS| FA
    EH["EventHub Trigger<br/>eventhubLagProcessor"] -->|"Event<br/>stream"| FA

    FA --> ALWAYS["Always On<br/>Keeps app warm<br/>Enable for reliable<br/>non-HTTP triggering"]
    %% Layout-only links tier independent sources; no execution steps or arrows added.
    TIMER ~~~ QUEUE
    QUEUE ~~~ BLOB
    BLOB ~~~ HTTP
    HTTP ~~~ EH

    classDef default fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
```

**Reading key:** These are independent trigger-to-app associations, not network initiator paths or an execution sequence. The final arrow identifies the app's Always On setting, not a downstream service.

## Steps

1. Add timer trigger.

    The reference app includes `src/functions/scheduledCleanup.js`:

    ```javascript
    const { app } = require('@azure/functions');

    app.timer('scheduledCleanup', {
        schedule: '0 0 2 * * *',
        handler: async (_timer, context) => {
            context.log('Nightly cleanup job fired');
        }
    });
    ```

    !!! tip "Always On for reliable timers"
        Enable Always On for reliable timer triggering on Dedicated hosting. Without it, an idle app can miss scheduled executions until an HTTP request or portal access wakes it.

2. Add queue trigger.

    The reference app includes `src/functions/queueProcessor.js`:

    ```javascript
    const { app } = require('@azure/functions');

    app.storageQueue('queueProcessor', {
        queueName: 'incoming-orders',
        connection: 'QueueStorage',
        handler: async (queueItem, context) => {
            context.log(`Order received: ${JSON.stringify(queueItem)}`);
        }
    });
    ```

    !!! note "Queue connection setting"
        The `connection` property (`QueueStorage`) must match an app setting containing the storage connection string. Set it during deployment:

        ```bash
        az functionapp config appsettings set \
          --name "$APP_NAME" \
          --resource-group "$RG" \
          --settings "QueueStorage=$(az storage account show-connection-string --name $STORAGE_NAME --resource-group $RG --query connectionString --output tsv)"
        ```

        | CLI element | Explanation |
        |---|---|
        | Command(s) | `az functionapp config appsettings set` |
        | Key flags | `--name`, `--resource-group`, `--settings`, `--query`, `--output` |
        | Variables | `$APP_NAME`, `$RG`, `$STORAGE_NAME` |
        | Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


3. Add blob trigger.

    The reference app includes `src/functions/blobProcessor.js`:

    ```javascript
    const { app } = require('@azure/functions');

    app.storageBlob('blobProcessor', {
        path: 'uploads/{name}',
        connection: 'AzureWebJobsStorage',
        source: 'EventGrid',
        handler: async (blob, context) => {
            context.log(`Processing blob: ${context.triggerMetadata.name}, size: ${blob.length} bytes`);
        }
    });
    ```

4. Deploy and verify trigger indexing.

    ```bash
    cd apps/nodejs
    func azure functionapp publish "$APP_NAME"
    ```

    Wait 30–60 seconds for indexing, then verify:

    ```bash
    az functionapp function list \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --output table
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az functionapp function list` |
    | Key flags | `--name`, `--resource-group`, `--output` |
    | Variables | `$APP_NAME`, `$RG` |
    | Expected result | Azure CLI returns the requested resource data; verify names, IDs, status fields, or metric values match the scenario. |


    Expected output (all 20 functions):

    ```text
    Name                                          Language
    --------------------------------------------  ----------
    func-ndded-04100022/blobProcessor             node
    func-ndded-04100022/checkReplayStatus         node
    func-ndded-04100022/dnsResolve                node
    func-ndded-04100022/eventhubLagProcessor      node
    func-ndded-04100022/externalDependency        node
    func-ndded-04100022/health                    node
    func-ndded-04100022/helloHttp                 node
    func-ndded-04100022/identityProbe             node
    func-ndded-04100022/info                      node
    func-ndded-04100022/logLevels                 node
    func-ndded-04100022/queueProcessor            node
    func-ndded-04100022/replayLabActivity         node
    func-ndded-04100022/replayStormOrchestrator   node
    func-ndded-04100022/scheduledCleanup          node
    func-ndded-04100022/slowResponse              node
    func-ndded-04100022/startReplayLab            node
    func-ndded-04100022/storageProbe              node
    func-ndded-04100022/testError                 node
    func-ndded-04100022/timerLab                  node
    func-ndded-04100022/unhandledError            node
    ```

5. Test HTTP endpoints after deployment.

    ```bash
    curl --request GET "https://$APP_NAME.azurewebsites.net/api/health"
    ```

    Expected output:

    ```json
    {"status":"healthy","timestamp":"2026-04-09T16:05:04.222Z","version":"1.0.0"}
    ```

    ```bash
    curl --request GET "https://$APP_NAME.azurewebsites.net/api/hello/Triggers"
    ```

    Expected output:

    ```json
    {"message":"Hello, Triggers"}
    ```

6. Review Dedicated trigger-specific notes.

    - **Always On**: Enable for reliable timer, queue, blob, and EventHub triggering on Dedicated hosting; otherwise the app may idle until an HTTP request or portal access wakes it.
    - **EventHub placeholder**: Set `EventHubConnection__fullyQualifiedNamespace=placeholder.servicebus.windows.net` to allow indexing without a real EventHub.
    - **Queue connection**: `QueueStorage` app setting must contain a valid storage connection string for `queueProcessor` to index.
    - **No auto-scale**: Dedicated plans do not scale automatically based on queue depth or event backlog. For auto-scaling workloads, use Premium or Consumption.

## Verification

The host output confirms all triggers are indexed and available. Verify:

- `az functionapp function list` shows all 20 functions with language `node`
- HTTP endpoints return expected responses
- Timer triggers (`scheduledCleanup`, `timerLab`) are listed — enable Always On for reliable scheduled triggering on Dedicated hosting

## See Also
- [Tutorial Overview & Plan Chooser](../index.md)
- [Node.js Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources
- [Azure Functions Node.js developer guide (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-node)
- [Create your first Azure Function with Core Tools (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-node)
- [Azure Functions hosting options (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [Dedicated hosting and Always On (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan#always-on)
- [Azure Functions triggers and bindings (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings)
