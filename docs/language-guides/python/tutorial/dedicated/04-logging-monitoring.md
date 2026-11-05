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
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring#application-insights
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/app-service/overview-vnet-integration
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/app-service/networking/private-endpoint
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-metric-overview
  diagrams:
    - id: what-you-ll-build
      type: flowchart
      source: self-generated
      justification: Python Linux plan-specific infrastructure context with full adjacent reading key; not deployment evidence.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring#application-insights
        - https://learn.microsoft.com/en-us/azure/app-service/overview-vnet-integration
        - https://learn.microsoft.com/en-us/azure/app-service/networking/private-endpoint
        - https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-metric-overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python
        - https://learn.microsoft.com/en-us/azure/azure-functions/configure-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/streaming-logs
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/azure-functions/storage-considerations
        - https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan
        - https://learn.microsoft.com/en-us/azure/azure-monitor/app/create-workspace-resource
        - https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity
        - https://learn.microsoft.com/en-us/azure/app-service/overview-access-restrictions#app-access
        - https://learn.microsoft.com/en-us/azure/azure-functions/deployment-zip-push
        - https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints
        - https://learn.microsoft.com/en-us/azure/azure-functions/opentelemetry-howto
        - https://learn.microsoft.com/en-us/azure/azure-functions/monitor-functions-reference
    - id: what-you-ll-build-2
      type: flowchart
      source: self-generated
      justification: Python plan-specific monitoring verification relationships; analysis arrows are not network-transit claims.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring#application-insights
        - https://learn.microsoft.com/en-us/azure/app-service/overview-vnet-integration
        - https://learn.microsoft.com/en-us/azure/app-service/networking/private-endpoint
        - https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-metric-overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python
        - https://learn.microsoft.com/en-us/azure/azure-functions/configure-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/streaming-logs
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/azure-functions/storage-considerations
        - https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan
        - https://learn.microsoft.com/en-us/azure/azure-monitor/app/create-workspace-resource
        - https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity
        - https://learn.microsoft.com/en-us/azure/app-service/overview-access-restrictions#app-access
        - https://learn.microsoft.com/en-us/azure/azure-functions/deployment-zip-push
        - https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints
        - https://learn.microsoft.com/en-us/azure/azure-functions/opentelemetry-howto
        - https://learn.microsoft.com/en-us/azure/azure-functions/monitor-functions-reference
---
# 04 - Logging & Monitoring (Dedicated)

This tutorial enables monitoring for a Dedicated Function App with Application Insights and Log Analytics queries. Fixed plan capacity does not guarantee continuous telemetry; enable Always On for reliable non-HTTP triggering.

## Prerequisites

- Completed [03 - Configuration](03-configuration.md)
- Azure CLI logged in and variables set:

```bash
export RG="rg-func-dedicated-dev"
export APP_NAME="func-dedi-<unique-suffix>"
export PLAN_NAME="asp-dedi-b1-dev"
export STORAGE_NAME="stdedidev<unique>"
export LOCATION="koreacentral"
export APPINSIGHTS_NAME="appi-dedi-<unique-suffix>"
export LOG_ANALYTICS_NAME="log-dedi-<unique-suffix>"
```

## What You'll Build

You will connect the Dedicated Function App to workspace-based Application Insights, run request queries, and configure a baseline alert for HTTP failures.

!!! info "Infrastructure Context"
    **Plan**: Dedicated (B1) | **Network**: Public internet in this tutorial | **VNet**: Supported by platform, not configured here

    The app uses fixed App Service plan capacity. Private networking is optional context, not configured by this monitoring page; enable Always On for reliable non-HTTP triggering.

    <!-- diagram-id: what-you-ll-build -->
```mermaid
%%{init: {'flowchart': {'nodeSpacing': 10, 'rankSpacing': 70, 'padding': 8, 'subGraphTitleMargin': {'top': 8, 'bottom': 32}}}}%%
flowchart TD
    accTitle: Python 3.11 Linux Dedicated optional Storage topology
    accDescr: Dedicated B1 through P3v3 context, not networking configured by this monitoring page. App compute is outside outbound integration; four Storage endpoints and DNS zones are expanded in the key. Identity, telemetry, package mode and Always On are associations, not data-transit hops. Public ingress depends on app access configuration.
    client(["Internet"])
    app_runtime["Function App<br/>Dedicated D<br/>Linux · Python 3.11"]
    identity{{"System MI<br/>Entra ID"}}
    telemetry>"Application<br/>Insights"]
    RFP["ZIP option R"]
    ALWAYS_ON["Always On A"]
    subgraph DNS["Private DNS zones"]
        dns_fn{{"Blob · Queue<br/>Table · File"}}
    end
    subgraph vnet_fn["VNet"]
        subgraph INT_SUB["<div style='width:130px;text-align:right'>Integration<br/>subnet</div>"]
            vnet_integration[["Outbound<br/>integration"]]
        end
        subgraph PE_SUB["<div style='width:100px;text-align:left'>PE<br/>subnet</div>"]
            pe_storage[["Storage PEs<br/>blob · queue<br/>table · file"]]
        end
    end
    storage_db[("Storage account")]
    client -->|"[Illustrative]<br/>HTTPS if H"| app_runtime
    app_runtime -.->|"[Illustrative]<br/>Identity"| identity
    app_runtime -.->|"[Configured]<br/>Telemetry"| telemetry
    app_runtime -.->|"[Illustrative]<br/>ZIP R"| RFP
    app_runtime -.->|"[Illustrative]<br/>Setting A"| ALWAYS_ON
    dns_fn -.->|"[Illustrative]<br/>VNet link"| vnet_fn
    app_runtime -->|"[Illustrative]<br/>Outbound"| vnet_integration
    vnet_integration -->|"[Illustrative]<br/>Each PE"| pe_storage
    pe_storage -->|"[Illustrative]<br/>Each service"| storage_db
    %% Layout-only tiers; add no requests, diagnostic steps or visible arrows.
    identity ~~~ telemetry
    telemetry ~~~ RFP
    RFP ~~~ ALWAYS_ON
    ALWAYS_ON ~~~ dns_fn
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class client,app_runtime,identity,telemetry,RFP,ALWAYS_ON,dns_fn,vnet_integration,pe_storage,storage_db baseNeutral;
```

**Reading key:** Solid arrows show intended request/data access; dotted arrows are associations. The private network is **optional illustrative context**, not an assertion that these steps configure it. Outbound VNet integration does not deploy compute into its subnet. The DNS link targets the VNet boundary; the table retains endpoint-to-zone-group associations, not endpoint-originated DNS queries ([integration](https://learn.microsoft.com/en-us/azure/app-service/overview-vnet-integration), [Storage endpoints](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints)).

| Key | Context / qualification |
|---|---|
| D | Dedicated B1–P3v3 plan range retained from the original context; this page uses B1 |
| H | Public HTTPS is available only when app public-network access and access restrictions permit it; a prerequisite deployment with a site private endpoint can change that default |
| VNet / integration / PE subnet | `10.0.0.0/16` / `10.0.1.0/24` / `10.0.2.0/24`; delegation `Microsoft.Web/serverFarms` |
| R | Local ready-to-run ZIP alternative: `WEBSITE_RUN_FROM_PACKAGE=1`; do not force this setting for remote build |
| A | Enable `Always On: true` for reliable non-HTTP triggering on Dedicated; fixed plan capacity alone does not prevent app idling |
| Identity | Optional system-assigned identity in Microsoft Entra ID; token acquisition uses the app-local identity endpoint, not direct app-to-Entra transit |

The bundled endpoints and zones expand into four independent service associations, not serial hops:

| Endpoint → Storage service | Associated private DNS zone |
|---|---|
| `PE_BLOB` → Blob | `privatelink.blob.core.windows.net` |
| `PE_QUEUE` → Queue | `privatelink.queue.core.windows.net` |
| `PE_TABLE` → Table | `privatelink.table.core.windows.net` |
| `PE_FILE` → File | `privatelink.file.core.windows.net` |

These are contextual choices, not a universal four-endpoint requirement. See [Dedicated Always On](https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan#always-on), [package configuration](https://learn.microsoft.com/en-us/azure/azure-functions/deployment-zip-push), [identity](https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity) and [app access defaults](https://learn.microsoft.com/en-us/azure/app-service/overview-access-restrictions#app-access).

<!-- diagram-id: what-you-ll-build-2 -->
```mermaid
flowchart TD
    accTitle: Python Dedicated monitoring verification
    accDescr: Configured Application Insights supports telemetry analysis. The metric alert is associated with the Function App because Step 6 scopes Http5xx to that resource, not Application Insights. These are monitoring associations, not network transit.
    A[Function App telemetry] --> B[Application Insights]
    B --> C[Log Analytics queries]
    A --> D[Metric alert rule]
```

**Monitoring distinction:** The small map groups telemetry analysis and the Function App's platform-metric alert; it does not route `Http5xx` through Application Insights. Default Python `logging` uses worker → Functions host → configured Application Insights with filtering/sampling, while the reference app's separate distro setup is not depicted as a mandatory host bypass ([Python logging](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python#logging-and-monitoring), [configuration](https://learn.microsoft.com/en-us/azure/azure-functions/configure-monitoring)). Workspace-based telemetry is stored in the linked workspace; diagnostic-settings `FunctionAppLogs` is a different collection route ([workspace](https://learn.microsoft.com/en-us/azure/azure-monitor/app/create-workspace-resource), [resource logs](https://learn.microsoft.com/en-us/azure/azure-functions/monitor-functions#azure-monitor-resource-logs)). Built-in streaming is single-instance where supported and enabled; Live Metrics is separate ([streaming](https://learn.microsoft.com/en-us/azure/azure-functions/streaming-logs)).

## Steps

### Step 1 - Create Log Analytics workspace

```bash
az monitor log-analytics workspace create \
  --resource-group $RG \
  --workspace-name $LOG_ANALYTICS_NAME \
  --location $LOCATION
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az monitor log-analytics workspace create` |
| Key flags | `--resource-group`, `--workspace-name`, `--location` |
| Variables | `$RG`, `$LOG_ANALYTICS_NAME`, `$LOCATION` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


### Step 2 - Create Application Insights (workspace-based)

```bash
WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group $RG \
  --workspace-name $LOG_ANALYTICS_NAME \
  --query id \
  --output tsv)

az monitor app-insights component create \
  --app $APPINSIGHTS_NAME \
  --location $LOCATION \
  --resource-group $RG \
  --workspace $WORKSPACE_ID \
  --application-type web
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az monitor log-analytics workspace show`, `az monitor app-insights component create` |
| Key flags | `--resource-group`, `--workspace-name`, `--query`, `--output`, `--app`, `--location`, `--workspace`, `--application-type` |
| Variables | `$RG`, `$LOG_ANALYTICS_NAME`, `$APPINSIGHTS_NAME`, `$LOCATION`, `$WORKSPACE_ID` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


### Step 3 - Connect Function App to Application Insights

```bash
APPINSIGHTS_CONNECTION_STRING=$(az monitor app-insights component show \
  --app $APPINSIGHTS_NAME \
  --resource-group $RG \
  --query connectionString \
  --output tsv)

az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG \
  --settings \
    APPLICATIONINSIGHTS_CONNECTION_STRING="$APPINSIGHTS_CONNECTION_STRING"
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az monitor app-insights component show`, `az functionapp config appsettings set` |
| Key flags | `--app`, `--resource-group`, `--query`, `--output`, `--name`, `--settings` |
| Variables | `$APPINSIGHTS_NAME`, `$RG`, `$APP_NAME`, `$APPINSIGHTS_CONNECTION_STRING` |
| Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


### Step 4 - Stream platform logs

```bash
az webapp log config \
  --name $APP_NAME \
  --resource-group $RG \
  --application-logging filesystem \
  --level information

az webapp log tail \
  --name $APP_NAME \
  --resource-group $RG
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az webapp log config`, `az webapp log tail` |
| Key flags | `--name`, `--resource-group`, `--application-logging`, `--level` |
| Variables | `$APP_NAME`, `$RG` |
| Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


Kudu/SCM is available on Dedicated, so you can also inspect diagnostics through `https://$APP_NAME.scm.azurewebsites.net`.

### Step 5 - Run a basic query for requests

```bash
APPINSIGHTS_APP_ID=$(az monitor app-insights component show \
  --app $APPINSIGHTS_NAME \
  --resource-group $RG \
  --query appId \
  --output tsv)

az monitor app-insights query \
  --app $APPINSIGHTS_APP_ID \
  --analytics-query "requests | take 5" \
  --output json
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az monitor app-insights component show`, `az monitor app-insights query` |
| Key flags | `--app`, `--resource-group`, `--query`, `--output`, `--analytics-query` |
| Variables | `$APPINSIGHTS_NAME`, `$RG`, `$APPINSIGHTS_APP_ID` |
| Expected result | Azure CLI returns the requested resource data; verify names, IDs, status fields, or metric values match the scenario. |


!!! tip "Use `--output json` for App Insights queries"
    The `--output table` format for `az monitor app-insights query` may return empty results even when data exists. Use `--output json` to reliably retrieve query results.

### Step 6 - Add an alert rule for failures

```bash
APP_ID=$(az functionapp show \
  --name $APP_NAME \
  --resource-group $RG \
  --query id \
  --output tsv)

ACTION_GROUP_ID=$(az monitor action-group create \
  --name "ag-dedi-alerts" \
  --resource-group $RG \
  --short-name "dediag" \
  --action webhook alertHook "https://example.com/webhook" \
  --query id \
  --output tsv)

az monitor metrics alert create \
  --name "alert-func-http5xx" \
  --resource-group $RG \
  --scopes $APP_ID \
  --condition "total Http5xx > 5" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action $ACTION_GROUP_ID
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp show`, `az monitor action-group create`, `az monitor metrics alert create` |
| Key flags | `--name`, `--resource-group`, `--query`, `--output`, `--short-name`, `--action`, `--scopes`, `--condition`, `--window-size`, `--evaluation-frequency` |
| Variables | `$APP_NAME`, `$RG`, `$APP_ID`, `$ACTION_GROUP_ID` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


## Verification

`az monitor app-insights component create ...`:

```json
{
  "appId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "applicationType": "web",
  "connectionString": "InstrumentationKey=<masked>;IngestionEndpoint=https://<region>.in.applicationinsights.azure.com/;LiveEndpoint=https://<region>.livediagnostics.monitor.azure.com/",
  "id": "/subscriptions/<subscription-id>/resourceGroups/rg-func-dedicated-dev/providers/microsoft.insights/components/appi-dedi-<unique-suffix>",
  "name": "appi-dedi-<unique-suffix>"
}
```

`az monitor app-insights query --analytics-query "requests | take 5" --output json`:

```text
TimeGenerated                 name     resultCode    duration
----------------------------  -------  ------------  --------
2026-04-03T10:22:41.132000Z  GET /api/health  200   00:00:00.018
2026-04-03T10:22:35.917000Z  GET /api/info    200   00:00:00.025
```

`az monitor metrics alert create ...`:

```json
{
  "id": "/subscriptions/<subscription-id>/resourceGroups/rg-func-dedicated-dev/providers/microsoft.insights/metricAlerts/alert-func-http5xx",
  "name": "alert-func-http5xx",
  "enabled": true,
  "severity": 3
}
```

## Next Steps

Monitoring is now in place with logs, queries, and alerts. Next you will codify Dedicated infrastructure using Bicep.

> **Next:** [05 - Infrastructure as Code](05-infrastructure-as-code.md)

## See Also

- [Tutorial Overview & Plan Chooser](../index.md)
- [Python Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources

- [Functions OpenTelemetry configuration](https://learn.microsoft.com/en-us/azure/azure-functions/opentelemetry-howto)
- [Functions monitoring data reference](https://learn.microsoft.com/en-us/azure/azure-functions/monitor-functions-reference)

- [functions-reference-python](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [configure-monitoring](https://learn.microsoft.com/en-us/azure/azure-functions/configure-monitoring)
- [streaming-logs](https://learn.microsoft.com/en-us/azure/azure-functions/streaming-logs)
- [functions-networking-options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options)
- [storage-considerations](https://learn.microsoft.com/en-us/azure/azure-functions/storage-considerations)
- [dedicated-plan](https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan)
- [create-workspace-resource](https://learn.microsoft.com/en-us/azure/azure-monitor/app/create-workspace-resource)
- [overview-managed-identity](https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity)
- [overview-access-restrictions](https://learn.microsoft.com/en-us/azure/app-service/overview-access-restrictions#app-access)
- [deployment-zip-push](https://learn.microsoft.com/en-us/azure/azure-functions/deployment-zip-push)
- [storage-private-endpoints](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints)

- [Monitor Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring)
- [Application Insights for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring#application-insights)
- [Azure Monitor metrics alerts](https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-metric-overview)
