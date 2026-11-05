---
validation:
  az_cli:
    last_tested: 2026-04-09
    cli_version: 2.83.0
    core_tools_version: 4.8.0
    result: pass
  bicep:
    last_tested:
    result: not_tested
content_sources:

  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-event-grid-blob-trigger
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue
  diagrams:
    - id: what-you-ll-build
      type: flowchart
      source: self-generated
      justification: Flow view of what you ll build, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints
        - https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity
        - https://learn.microsoft.com/en-us/azure/azure-functions/manage-connections
        - https://learn.microsoft.com/en-us/azure/azure-functions/storage-considerations
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-event-grid-blob-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue
    - id: what-you-ll-build-2
      type: flowchart
      source: self-generated
      justification: Flow view of what you ll build 2, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer
        - https://learn.microsoft.com/en-us/azure/azure-functions/manage-connections
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-event-grid-blob-trigger
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue
---
# 07 - Extending Triggers (Flex Consumption)

Add non-HTTP triggers to your Flex Consumption app with the correct trigger model for FC1 scaling and networking behavior.

## Prerequisites

| Tool | Minimum version | Purpose |
|---|---|---|
| Python | 3.11 | Update function code |
| Azure Functions Core Tools | 4.x | Run and publish triggers |
| Azure Storage Account | Existing | Queue and blob event source |
| Event Grid integration | Enabled | Blob event delivery for Flex |

## What You'll Build

You will extend the Python Flex app with timer, queue, and Event Grid-based blob triggers, then validate end-to-end event processing.

!!! info "Infrastructure Context"
    **Plan**: Flex Consumption (FC1) | **Network**: Full private network | **VNet**: ✅

    This FC1 scenario retains outbound VNet integration, four Storage private endpoints and DNS zones, and user-assigned identity for host/deployment access. These are configuration choices, not requirements for every Flex app; HTTP ingress and Event Grid delivery remain separate from private Storage access.

<!-- diagram-id: what-you-ll-build -->
```mermaid
%%{init: {'flowchart': {'nodeSpacing': 10, 'rankSpacing': 70, 'padding': 8, 'subGraphTitleMargin': {'top': 8, 'bottom': 32}}}}%%
flowchart TD
    accTitle: Python Flex Consumption private Storage context
    accDescr: Linux Python 3.11 FC1 app outside its outbound integration subnet, with four distinct Storage endpoints and DNS zones expanded in the key. User-assigned identity and RBAC are authorization associations, not data transit. Deployment uses the retained Blob container; this is intended configuration, not a deployment result.
    client(["Internet"])
    app_runtime["Function App<br/>Flex Consumption FC1<br/>Linux Python 3.11"]
    identity{{"User-assigned MI<br/>Storage RBAC"}}
    telemetry>"Application<br/>Insights"]
    subgraph DNS["Private DNS zones"]
        dns_fn{{"Blob · Queue<br/>Table · File"}}
    end
    subgraph vnet_fn["VNet"]
        subgraph subnet_int_fn["<div style='width:170px;text-align:right'>Integration<br/>subnet</div>"]
            vnet_integration[["Outbound<br/>integration"]]
        end
        subgraph subnet_pe_fn["<div style='width:130px;text-align:left'>PE<br/>subnet</div>"]
            pe_storage[["Storage PEs<br/>blob · queue<br/>table · file"]]
        end
    end
    storage_db[("Storage account<br/>Settings: S")]
    subgraph DEPLOY["<div style='width:200px;text-align:left'>Deployment</div>"]
        BLOB_CTR[("Blob container<br/>deployment-packages")]
    end
    client -->|"[Configured]<br/>HTTPS"| app_runtime
    app_runtime -.->|"[Configured]<br/>Identity"| identity
    app_runtime -.->|"[Configured]<br/>Telemetry"| telemetry
    dns_fn -.->|"[Configured]<br/>VNet link"| vnet_fn
    app_runtime -->|"[Configured]<br/>Outbound"| vnet_integration
    vnet_integration -->|"[Configured]<br/>Each PE"| pe_storage
    pe_storage -->|"[Configured]<br/>Each service"| storage_db
    storage_db -.->|"[Configured]<br/>Contains"| BLOB_CTR
    %% Layout-only tiers; add no requests, diagnostic steps or visible arrows.
    identity ~~~ telemetry
    telemetry ~~~ dns_fn
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    classDef focusActive fill:#e6f0fd,stroke:#287ce4,stroke-width:2.5px,color:#14202e;
    classDef bandMuted fill:#ffffff,stroke:#707e93,stroke-width:1.5px,stroke-dasharray:4 3,color:#14202e;
    class client,storage_db,BLOB_CTR baseNeutral;
    class app_runtime,vnet_integration,pe_storage focusActive;
    class identity,telemetry,dns_fn bandMuted;
```

**Reading key (Linux FC1):** Solid arrows show intended request/data access; dotted arrows show identity, telemetry, VNet-link or membership associations, not transport. Outbound integration does not deploy app compute into the integration subnet; Flex uses shared gateways dedicated to that subnet ([networking](https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options)).

| Key | Configuration / meaning |
|---|---|
| VNet / integration / PE subnet | `10.0.0.0/16` / `10.0.1.0/24` / `10.0.2.0/24`; delegation `Microsoft.App/environments` |
| S | Intended private template configuration: `publicNetworkAccess: Disabled`, `allowSharedKeyAccess: false`; `allowPublicAccess` was the Bicep module parameter, not a Storage ARM property |
| Identity / RBAC | User-assigned identity with Storage permissions; RBAC authorizes access, not a hop through the identity. Tokens use the app's local identity endpoint ([identity](https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity)) |
| Deployment | Blob container `deployment-packages`; Flex does not depend on an Azure Files content share ([storage](https://learn.microsoft.com/en-us/azure/azure-functions/storage-considerations)) |

The bundled nodes retain **four distinct endpoints**, with integration → endpoint → matching Storage service and each endpoint's DNS zone-group association. DNS zones are outside and linked to the VNet; clients keep the normal Storage hostname, resolving to the endpoint's private IP when private DNS is configured ([Storage endpoints/DNS](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints)). The File endpoint is retained scenario context, not a Flex content-share requirement.

| Endpoint → Storage service | Private DNS zone |
|---|---|
| `PE_BLOB` → Blob | `privatelink.blob.core.windows.net` |
| `PE_QUEUE` → Queue | `privatelink.queue.core.windows.net` |
| `PE_TABLE` → Table | `privatelink.table.core.windows.net` |
| `PE_FILE` → File | `privatelink.file.core.windows.net` |

<!-- diagram-id: what-you-ll-build-2 -->
```mermaid
flowchart TD
    accTitle: Python Flex Consumption independent trigger paths
    accDescr: The tasks queue associates with its queue trigger, uploads Blob events pass through an Event Grid subscription to the EventGrid-source Blob trigger, and the cron schedule associates with the timer trigger. These are logical trigger relationships, not HTTP ingress or sequential execution across trigger types.
    Queue["Storage Queue:<br/>tasks"] --> QueueFn[Queue trigger]
    Blob["Blob uploads<br/>container"] --> EG["Event Grid<br/>subscription"]
    EG --> BlobFn["Blob trigger<br/>source=EventGrid"]
    Timer[Cron schedule] --> TimerFn[Timer trigger]
    %% Layout-only tiers; add no trigger dependencies or visible arrows.
    QueueFn ~~~ Blob
    BlobFn ~~~ Timer
```

**Takeaway:** These Python v2 samples use `@bp.queue_trigger`, `@bp.blob_trigger(source="EventGrid")` and `@bp.timer_trigger`. Flex requires the event-based Blob source **and** the subscription setup in Step 5; setting the decorator alone does not create that subscription. `connection="AzureWebJobsStorage"` selects the app setting or identity-setting prefix, not a literal connection string in source; identity connections also need appropriate settings and permissions. The timer expression `0 */5 * * * *` means every fifth minute, not every five seconds ([Blob setup](https://learn.microsoft.com/en-us/azure/azure-functions/functions-event-grid-blob-trigger), [queue connection](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue-trigger), [timer](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer), [connections](https://learn.microsoft.com/en-us/azure/azure-functions/manage-connections)).

## Steps

### Step 1: Set Variables

```bash
export BASE_NAME="flexdemo"
export RG="rg-flexdemo"
export APP_NAME="flexdemo-func"
export PLAN_NAME="flexdemo-plan"
export STORAGE_NAME="flexdemostorage"
export APPINSIGHTS_NAME="flexdemo-insights"
export LOCATION="koreacentral"
```

Expected output:


```text
```

### Step 2: Add a Timer Trigger Blueprint

Create `apps/python/blueprints/scheduled.py` and register it in `apps/python/function_app.py`.


```python
import azure.functions as func
import logging
from datetime import datetime, timezone

bp = func.Blueprint()

@bp.timer_trigger(schedule="0 */5 * * * *", arg_name="timer", run_on_startup=False)
def scheduled_cleanup(timer: func.TimerRequest) -> None:
    logging.info("Timer fired at %s", datetime.now(timezone.utc).isoformat())
```

Expected output:


```text
```

### Step 3: Add Queue Trigger (Per-Function Scaling)

Queue-triggered functions on Flex scale independently from other functions in the same app.


```python
import azure.functions as func
import logging

bp = func.Blueprint()

@bp.queue_trigger(arg_name="msg", queue_name="tasks", connection="AzureWebJobsStorage")
def process_queue_message(msg: func.QueueMessage) -> None:
    logging.info("Queue message: %s", msg.get_body().decode("utf-8"))
```

Expected output:


```text
```

### Step 4: Add Blob Trigger with Event Grid Path

For Flex Consumption, production blob triggers **must** use the Event Grid-based blob trigger. The standard polling blob trigger is not supported on Flex Consumption. Use the `source="EventGrid"` parameter on `@bp.blob_trigger()` to enable Event Grid delivery.


```python
import azure.functions as func
import logging

bp = func.Blueprint()

@bp.blob_trigger(
    arg_name="input_blob",
    path="uploads/{name}",
    connection="AzureWebJobsStorage",
    source="EventGrid",
)
def process_blob_event(input_blob: func.InputStream) -> None:
    logging.info(
        "Blob trigger (Event Grid): name=%s, size=%d bytes",
        input_blob.name,
        input_blob.length,
    )
    content = input_blob.read()
    logging.info("Read %d bytes from blob", len(content))
```

!!! warning "source parameter is required on Flex"
    Without `source="EventGrid"`, the trigger defaults to the polling model, which is **not supported** on Flex Consumption. Your function will fail to process blobs.

Expected output:


```text
```

### Step 5: Create Event Subscription for Blob Events

The Event Grid-based blob trigger uses a **webhook endpoint** exposed by the Functions runtime. The URL pattern is:

```text
https://<APP_NAME>.azurewebsites.net/runtime/webhooks/blobs?functionName=Host.Functions.process_blob_event&code=<system-key>
```

Retrieve the system key and create the subscription:


```bash
# Get the blob extension system key
BLOB_KEY=$(az functionapp keys list \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --query "systemKeys.blobs_extension" \
  --output tsv)

# Create the Event Grid subscription pointing to the blob webhook endpoint
az eventgrid event-subscription create \
  --name "blob-created-subscription" \
  --source-resource-id "/subscriptions/<subscription-id>/resourceGroups/$RG/providers/Microsoft.Storage/storageAccounts/$STORAGE_NAME" \
  --endpoint "https://$APP_NAME.azurewebsites.net/runtime/webhooks/blobs?functionName=Host.Functions.process_blob_event&code=$BLOB_KEY" \
  --endpoint-type webhook \
  --included-event-types "Microsoft.Storage.BlobCreated" \
  --output json
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp keys list`, `az eventgrid event-subscription create` |
| Key flags | `--name`, `--resource-group`, `--query`, `--output`, `--source-resource-id`, `--endpoint`, `--endpoint-type`, `--included-event-types` |
| Variables | `$APP_NAME`, `$RG`, `$STORAGE_NAME`, `$BLOB_KEY` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


Expected output:


```json
{
  "id": "/subscriptions/<subscription-id>/resourceGroups/rg-flexdemo/providers/Microsoft.Storage/storageAccounts/flexdemostorage/providers/Microsoft.EventGrid/eventSubscriptions/blob-created-subscription",
  "name": "blob-created-subscription",
  "provisioningState": "Succeeded"
}
```

### Step 6: Publish and Validate Trigger Registration


```bash
cd apps/python
func azure functionapp publish "$APP_NAME" --python
az functionapp function list --name "$APP_NAME" --resource-group "$RG" --output table
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp function list` |
| Key flags | `--python`, `--name`, `--resource-group`, `--output` |
| Variables | `$APP_NAME`, `$RG` |
| Expected result | Azure CLI returns the requested resource data; verify names, IDs, status fields, or metric values match the scenario. |


Expected output:


```text
Name                         Trigger
---------------------------  -----------------
health                       httpTrigger
scheduled_cleanup            timerTrigger
process_queue_message        queueTrigger
process_blob_event           blobTrigger
```

### Step 7: Trigger Tests

!!! warning "Storage is network-locked"
    If the storage account has `defaultAction: Deny` (set in Tutorial 02 Step 10), you cannot run data-plane operations from your local machine. Either temporarily allow public access or run these commands from within the VNet:

    ```bash
    az storage account update \
      --name "$STORAGE_NAME" \
      --resource-group "$RG" \
      --default-action Allow
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az storage account update` |
    | Key flags | `--name`, `--resource-group`, `--default-action` |
    | Variables | `$STORAGE_NAME`, `$RG` |
    | Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


    Remember to lock it down again after testing.

```bash
az storage queue create --name "tasks" --account-name "$STORAGE_NAME" --auth-mode login --output json
az storage message put --queue-name "tasks" --content '{"task":"reindex"}' --account-name "$STORAGE_NAME" --auth-mode login --output json
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az storage queue create`, `az storage message put` |
| Key flags | `--name`, `--account-name`, `--auth-mode`, `--output`, `--queue-name`, `--content` |
| Variables | `$STORAGE_NAME` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


Upload a blob to emit Event Grid event:


```bash
az storage container create --name "uploads" --account-name "$STORAGE_NAME" --auth-mode login --output json
az storage blob upload --container-name "uploads" --name "sample.txt" --file "/tmp/sample.txt" --account-name "$STORAGE_NAME" --auth-mode login --output json
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az storage container create`, `az storage blob upload` |
| Key flags | `--name`, `--account-name`, `--auth-mode`, `--output`, `--container-name`, `--file` |
| Variables | `$STORAGE_NAME` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


Expected output:


```json
{
  "messageId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "insertionTime": "2026-01-01T00:00:00Z"
}
```


```json
{
  "etag": "\"0x8DXXXXXXXXXXXX\"",
  "lastModified": "2026-01-01T00:00:00+00:00"
}
```

## Verification

- `az functionapp function list` includes timer, queue, and blob triggers after publish.
- Queue test succeeds after creating the `tasks` queue.
- Blob upload succeeds after creating the `uploads` container and emits `BlobCreated` events to the subscription.
- Blob trigger production path remains Event Grid-based (`source="EventGrid"`) for Flex compliance.

## Next Steps

> **Next:** [How Azure Functions Works](../../../../platform/architecture/index.md)

## See Also

- [Tutorial Overview & Plan Chooser](../index.md)
- [Python Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources

- [Functions networking options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options)
- [Storage private endpoints and DNS](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints)
- [App Service and Functions managed identity](https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity)
- [Functions storage considerations](https://learn.microsoft.com/en-us/azure/azure-functions/storage-considerations)
- [Functions connection settings](https://learn.microsoft.com/en-us/azure/azure-functions/manage-connections)
- [Python Queue trigger](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue-trigger)
- [Python Timer trigger](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer)
- [Azure Functions trigger and binding concepts](https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings)
- [Event Grid blob trigger for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-event-grid-blob-trigger)
- [Queue storage trigger for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue)
