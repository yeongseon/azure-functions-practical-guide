---
validation:
  az_cli:
    last_tested: 2026-04-09
    cli_version: 2.83.0
    core_tools_version: 4.8.0
    result: pass
  bicep:
    last_tested: '2026-06-06'
    result: syntax_validated
content_sources:

  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/templates/microsoft.web/serverfarms
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/templates/microsoft.web/sites
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/app-service/overview-vnet-integration
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/app-service/networking/private-endpoint
  diagrams:
    - id: what-you-ll-build
      type: flowchart
      source: self-generated
      justification: Illustrative topology of the optional Dedicated storage-networking example - outbound VNet integration, private endpoint network interfaces in a subnet, and VNet-linked Private DNS zones, not a measured trace or deployment evidence.
      based_on:
        - https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview
        - https://learn.microsoft.com/en-us/azure/dns/private-dns-virtual-network-links
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-infrastructure-as-code
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/supported-languages
        - https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints
        - https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity
        - https://learn.microsoft.com/en-us/azure/app-service/overview-access-restrictions#app-access
        - https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan#always-on
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-deployment-technologies
        - https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/
        - https://learn.microsoft.com/en-us/azure/templates/microsoft.web/serverfarms
        - https://learn.microsoft.com/en-us/azure/templates/microsoft.web/sites
        - https://learn.microsoft.com/en-us/azure/app-service/overview-vnet-integration
        - https://learn.microsoft.com/en-us/azure/app-service/networking/private-endpoint
    - id: what-you-ll-build-2
      type: flowchart
      source: self-generated
      justification: Resource map of the standalone Dedicated Bicep example (B1 plan, storage, Linux Function App), arrows show template resources, not creation order.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-infrastructure-as-code
        - https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/
        - https://learn.microsoft.com/en-us/azure/templates/microsoft.web/serverfarms
        - https://learn.microsoft.com/en-us/azure/templates/microsoft.web/sites
        - https://learn.microsoft.com/en-us/azure/app-service/overview-vnet-integration
        - https://learn.microsoft.com/en-us/azure/app-service/networking/private-endpoint
---
# 05 - Infrastructure as Code (Dedicated)

This tutorial deploys a Dedicated Function App stack using Bicep. It uses a Linux Basic B1 App Service Plan for cost-efficient learning and provisions the core resources needed for a Python Function App.

## Prerequisites

- Completed [04 - Logging & Monitoring](04-logging-monitoring.md)
- Azure CLI with Bicep support
- Variables available:

```bash
export RG="rg-func-dedicated-dev"
export APP_NAME="func-dedi-<unique-suffix>"
export PLAN_NAME="asp-dedi-b1-dev"
export STORAGE_NAME="stdedidev<unique>"
export LOCATION="koreacentral"
```

## What You'll Build

You will define and deploy a Dedicated App Service Plan, storage account, and Linux Python Function App by using `infra/dedicated/main.bicep`, then validate the deployed resources.

!!! info "Infrastructure Context"
    **Plan**: Dedicated (B1) | **Network**: Public internet in this tutorial | **VNet**: Supported by platform, not configured here

    The app runs on a fixed App Service Plan (always on, no scale-to-zero). Basic B1 supports App Service VNet integration and private endpoints, but this guide uses Standard (S1+) for private networking scenarios to provide scale headroom, deployment slots, and a production-oriented validation path.

<!-- diagram-id: what-you-ll-build -->
```mermaid
%%{init: {'flowchart': {'nodeSpacing': 10, 'rankSpacing': 85, 'padding': 8, 'subGraphTitleMargin': {'top': 8, 'bottom': 32}}}}%%
flowchart TD
    accTitle: Python Dedicated app and optional private storage topology
    accDescr: Private endpoints are network interfaces in the PE subnet and Private DNS zones are VNet-linked. Linux Python 3.11 and B1 describe the standalone example; the repository template defaults to S1. Optional outbound integration reaches four storage private endpoints; the app is not inside that subnet. Identity and DNS associations are configuration, not data transit or deployment proof. Public HTTPS is conditional when a site private endpoint exists.
    INET([Internet]) -->|"[Configured]<br/>1"| FA["Function App<br/>Dedicated<br/>B1–P3v3<br/>Linux Python 3.11"]
    FA -.->|"[Configured]<br/>2"| ENTRA{{"Microsoft<br/>Entra ID"}}
    FA -.->|"[Configured]<br/>3"| AI>"Application<br/>Insights"]
    FA -->|"[Configured]<br/>4"| INT
    subgraph VNET["VNet"]
        subgraph INT_SUB["<div style='width:140px;text-align:right'>Integration<br/>subnet</div>"]
            INT[["Outbound<br/>integration"]]
        end
        subgraph PE_SUB["<div style='width:110px;text-align:left'>PE<br/>subnet</div>"]
            PE[["Storage PE NICs<br/>1–4 in table"]]
        end
    end
    INT -->|"[Configured]<br/>5"| PE
    PE -->|"[Configured]<br/>6"| ST[("Storage account")]
    subgraph DNS["<div style='width:150px;text-align:right'>Private DNS<br/>zones<br/>VNet-linked</div>"]
        ZONES{{"Storage zones<br/>1–4 in table"}}
    end
    PE -.->|"[Configured]<br/>7"| ZONES
    FA -.->|"8"| RFP["Local ZIP<br/>Not remote build"]
    FA -.->|"9"| ALWAYS_ON["Always On: true<br/>Fixed capacity"]
    %% Layout-only tiers; add no data hops, operations or visible arrows.
    ENTRA ~~~ AI
    AI ~~~ INT
    ST ~~~ ZONES
    ZONES ~~~ RFP
    RFP ~~~ ALWAYS_ON
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    classDef focusActive fill:#e6f0fd,stroke:#287ce4,stroke-width:2.5px,color:#14202e;
    classDef netBox fill:transparent,stroke:#287ce4,stroke-width:2px,stroke-dasharray:6 3;
    class INET,ENTRA,AI,ST,ZONES,RFP,ALWAYS_ON baseNeutral;
    class FA,INT,PE focusActive;
    class VNET,INT_SUB,PE_SUB,DNS netBox;
```

**Reading key:** Plain numerals 8 and 9 are configured relationships like the other numbered arrows. This retains the optional storage-networking view, not a claim that the standalone B1 snippet provisions it. The B1–P3v3 label identifies the original Dedicated scenario range, not an exhaustive SKU catalogue. The repository template defaults to Linux S1 / Standard; all shown Python 3.11 labels describe example configuration, not a runtime-version recommendation.

| Key | Relationship or configuration |
|---|---|
| 1 | Public HTTPS for the standalone baseline. If adding a site private endpoint, public ingress requires `publicNetworkAccess: Enabled` and applicable access rules; with that property unset, a site private endpoint disables the public endpoint by default ([app access](https://learn.microsoft.com/en-us/azure/app-service/overview-access-restrictions#app-access)). The repository template includes that site endpoint; this optional CLI storage extension does not. |
| 2 | System-assigned managed identity in Microsoft Entra ID; a logical identity association via the app's managed-identity endpoint, not a direct Entra network hop. |
| 3 | Telemetry to configured Application Insights, off the storage data path. |
| 4 | Optional outbound VNet integration; it does not deploy the app into the subnet. Original example addresses: VNet `10.0.0.0/16`, integration `10.0.1.0/24`, private endpoints `10.0.2.0/24`; integration delegation `Microsoft.Web/serverFarms`. |
| 5–6 | Outbound storage access through the four private endpoints below to their matching services in the same Storage account; the bundle is four parallel service paths, not four serial hops. |
| 7 | Each endpoint's DNS zone-group association maps to its matching numbered zone below; these dotted links are configuration, not queries initiated by a private endpoint. Private zones are linked to the VNet, not contained in its subnets. Each private endpoint is a network interface that uses a private IP address from the PE subnet; zones are shown VNet-linked ([private endpoint overview](https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview), [virtual network links](https://learn.microsoft.com/en-us/azure/dns/private-dns-virtual-network-links)). |
| 8 | Local ready-to-run ZIP alternative: `WEBSITE_RUN_FROM_PACKAGE=1`; do not preconfigure it for Python remote build ([deployment technologies](https://learn.microsoft.com/en-us/azure/azure-functions/functions-deployment-technologies)). |
| 9 | `alwaysOn: true` for reliable non-HTTP triggering on Dedicated hosting; fixed plan capacity is distinct from this setting ([Always On](https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan#always-on)). |

| Endpoint / zone key | Storage private endpoint | Matching private DNS zone |
|---|---|---|
| 1 | `blob` | `privatelink.blob.core.windows.net` |
| 2 | `queue` | `privatelink.queue.core.windows.net` |
| 3 | `table` | `privatelink.table.core.windows.net` |
| 4 | `file` | `privatelink.file.core.windows.net` |

The four-service endpoint/zone set is this page's optional CLI example; the repository Dedicated template has blob, queue and table endpoints, plus a site endpoint, and no default Azure Files content share. See [Storage private endpoints](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints) for the service-to-zone mappings.

<!-- diagram-id: what-you-ll-build-2 -->
```mermaid
flowchart TD
    accTitle: Python Dedicated standalone Bicep resource map
    accDescr: The standalone example defines a Basic B1 App Service Plan, Storage account and Linux Python Function App. These arrows identify template resources, not serial creation; ARM resolves dependencies and can deploy independent resources in parallel. The repository template defaults to S1 instead; no successful deployment is asserted.
    A[Bicep template] --> B["App Service Plan<br/>B1"]
    A --> C[Storage Account]
    A --> D["Function App<br/>Linux Python"]
    %% Layout-only tiers; add no provisioning dependency or visible arrow.
    B ~~~ C
    C ~~~ D
```

## Steps

### Step 1 - Create and review the Bicep entry point

Use `infra/dedicated/main.bicep` as the Dedicated template root.

```bash
mkdir --parents infra/dedicated
touch infra/dedicated/main.bicep
ls infra/dedicated/main.bicep
```

### Step 2 - Define Dedicated plan and Function App resources

Your template should include these Dedicated-specific values:

```bicep
param location string = resourceGroup().location
param planName string
param appName string
param storageName string

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  kind: 'linux'
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  properties: {
    reserved: true
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}

resource functionApp 'Microsoft.Web/sites@2023-12-01' = {
  name: appName
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: plan.id
    siteConfig: {
      alwaysOn: true
      linuxFxVersion: 'Python|3.11'
      appSettings: [
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'AzureWebJobsStorage'
          value: '<connection-string-or-identity-based-setting>'
        }
      ]
    }
  }
}
```

This is the classic `siteConfig.appSettings` model for Dedicated (not `functionAppConfig`).

### Step 3 - Configure Function App settings for Dedicated

Dedicated does not require Azure Files content share settings such as `WEBSITE_CONTENTAZUREFILECONNECTIONSTRING` as a general rule.

```bicep
resource functionApp 'Microsoft.Web/sites@2023-12-01' = {
  name: appName
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: plan.id
    siteConfig: {
      alwaysOn: true
      linuxFxVersion: 'Python|3.11'
      appSettings: [
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'AzureWebJobsStorage'
          value: '<connection-string-or-identity-based-setting>'
        }
      ]
    }
  }
}
```

### Step 4 - Deploy the Bicep template

```bash
az group create \
  --name $RG \
  --location $LOCATION

az deployment group create \
  --resource-group $RG \
  --template-file infra/dedicated/main.bicep \
  --parameters \
    location=$LOCATION \
    planName=$PLAN_NAME \
    appName=$APP_NAME \
    storageName=$STORAGE_NAME
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az group create`, `az deployment group create` |
| Key flags | `--name`, `--location`, `--resource-group`, `--template-file`, `--parameters` |
| Variables | `$RG`, `$LOCATION`, `$PLAN_NAME`, `$APP_NAME`, `$STORAGE_NAME` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


### Step 5 - Validate deployed resources

```bash
az appservice plan show \
  --name $PLAN_NAME \
  --resource-group $RG \
  --query "{name:name,sku:sku.name,tier:sku.tier,kind:kind}" \
  --output json

az functionapp show \
  --name $APP_NAME \
  --resource-group $RG \
  --query "{name:name,kind:kind,defaultHostName:defaultHostName}" \
  --output json
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az appservice plan show`, `az functionapp show` |
| Key flags | `--name`, `--resource-group`, `--query`, `--output` |
| Variables | `$PLAN_NAME`, `$RG`, `$APP_NAME` |
| Expected result | Azure CLI returns the requested resource data; verify names, IDs, status fields, or metric values match the scenario. |


### Option B: Deploy with Azure CLI (No Bicep)

Use this full CLI sequence when you want to provision the same Dedicated baseline without Bicep.

#### B-1: Resource Group

```bash
az group create \
  --name "$RG" \
  --location "$LOCATION"
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az group create` |
| Key flags | `--name`, `--location` |
| Variables | `$RG`, `$LOCATION` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


#### B-2: Storage Account

```bash
az storage account create \
  --name "$STORAGE_NAME" \
  --resource-group "$RG" \
  --location "$LOCATION" \
  --sku "Standard_LRS" \
  --kind "StorageV2"
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az storage account create` |
| Key flags | `--name`, `--resource-group`, `--location`, `--sku`, `--kind` |
| Variables | `$STORAGE_NAME`, `$RG`, `$LOCATION` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


#### B-3: App Service Plan (B1)

```bash
az appservice plan create \
  --name "$PLAN_NAME" \
  --resource-group "$RG" \
  --location "$LOCATION" \
  --sku "B1" \
  --is-linux
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az appservice plan create` |
| Key flags | `--name`, `--resource-group`, `--location`, `--sku`, `--is-linux` |
| Variables | `$PLAN_NAME`, `$RG`, `$LOCATION` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


#### B-4: Function App (with Always On)

```bash
az functionapp create \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --plan "$PLAN_NAME" \
  --storage-account "$STORAGE_NAME" \
  --runtime "python" \
  --runtime-version "3.11" \
  --functions-version "4" \
  --os-type "Linux"

az functionapp config set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --always-on true
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp create`, `az functionapp config set` |
| Key flags | `--name`, `--resource-group`, `--plan`, `--storage-account`, `--runtime`, `--runtime-version`, `--functions-version`, `--os-type`, `--always-on` |
| Variables | `$APP_NAME`, `$RG`, `$PLAN_NAME`, `$STORAGE_NAME` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


#### B-5: App Settings (connection string or identity-based)

This Python track uses remote build: do not preconfigure `WEBSITE_RUN_FROM_PACKAGE=1`. The template's local-package option applies only to a separately built ready-to-run ZIP; reconcile that setting before remote publish. See the [package matrix](../../../../operations/deployment.md#package-configuration-by-plan-and-os).

```bash
az functionapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --settings "FUNCTIONS_WORKER_RUNTIME=python"
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp config appsettings set` |
| Key flags | `--name`, `--resource-group`, `--settings` |
| Variables | `$APP_NAME`, `$RG` |
| Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


Connection string mode:

```bash
export STORAGE_CONN_STRING=$(az storage account show-connection-string \
  --name "$STORAGE_NAME" \
  --resource-group "$RG" \
  --query "connectionString" \
  --output tsv)

az functionapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --settings "AzureWebJobsStorage=$STORAGE_CONN_STRING"
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az storage account show-connection-string`, `az functionapp config appsettings set` |
| Key flags | `--name`, `--resource-group`, `--query`, `--output`, `--settings` |
| Variables | `$STORAGE_NAME`, `$RG`, `$APP_NAME`, `$STORAGE_CONN_STRING` |
| Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


Identity-based mode:

```bash
az functionapp identity assign \
  --name "$APP_NAME" \
  --resource-group "$RG"

az functionapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --settings \
    "AzureWebJobsStorage__accountName=$STORAGE_NAME" \
    "AzureWebJobsStorage__credential=managedidentity"
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp identity assign`, `az functionapp config appsettings set` |
| Key flags | `--name`, `--resource-group`, `--settings` |
| Variables | `$APP_NAME`, `$RG`, `$STORAGE_NAME` |
| Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


#### B-6: Application Insights

```bash
export APPINSIGHTS_NAME="appi-$APP_NAME"

az monitor app-insights component create \
  --app "$APPINSIGHTS_NAME" \
  --resource-group "$RG" \
  --location "$LOCATION" \
  --application-type "web"

export APPINSIGHTS_CONNECTION_STRING=$(az monitor app-insights component show \
  --app "$APPINSIGHTS_NAME" \
  --resource-group "$RG" \
  --query "connectionString" \
  --output tsv)

az functionapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --settings "APPLICATIONINSIGHTS_CONNECTION_STRING=$APPINSIGHTS_CONNECTION_STRING"
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az monitor app-insights component create`, `az monitor app-insights component show`, `az functionapp config appsettings set` |
| Key flags | `--app`, `--resource-group`, `--location`, `--application-type`, `--query`, `--output`, `--name`, `--settings` |
| Variables | `$APP_NAME`, `$APPINSIGHTS_NAME`, `$RG`, `$LOCATION`, `$APPINSIGHTS_CONNECTION_STRING` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


??? example "Optional: VNet and Private Endpoints"
    Basic (B1) can use App Service VNet integration and private endpoints. This optional path upgrades to `S1` so the tutorial matches the guide-tested private networking scenario and provides more production headroom.

    !!! info "B1 network support and guide scope"
        B1 supports these platform networking features, but this guide validates private networking on Standard (S1+) for production-oriented examples.

        If you add optional VNet integration in this template, document subnet delegation to `Microsoft.Web/serverFarms` and use S1 or higher when you want to match this guide exactly.

    #### B-7: Upgrade to Standard (if needed)

    ```bash
    az appservice plan update \
      --name "$PLAN_NAME" \
      --resource-group "$RG" \
      --sku S1
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az appservice plan update` |
    | Key flags | `--name`, `--resource-group`, `--sku` |
    | Variables | `$PLAN_NAME`, `$RG` |
    | Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


    #### B-8: VNet and Subnets

    ```bash
    export VNET_NAME="vnet-dedicated-demo"

    az network vnet create \
      --name "$VNET_NAME" \
      --resource-group "$RG" \
      --location "$LOCATION" \
      --address-prefixes "10.0.0.0/16" \
      --subnet-name "snet-integration" \
      --subnet-prefixes "10.0.1.0/24"

    az network vnet subnet create \
      --name "snet-private-endpoints" \
      --resource-group "$RG" \
      --vnet-name "$VNET_NAME" \
      --address-prefixes "10.0.2.0/24"

    az network vnet subnet update \
      --name "snet-integration" \
      --resource-group "$RG" \
      --vnet-name "$VNET_NAME" \
      --delegations "Microsoft.Web/serverFarms"
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az network vnet create`, `az network vnet subnet create`, `az network vnet subnet update` |
    | Key flags | `--name`, `--resource-group`, `--location`, `--address-prefixes`, `--subnet-name`, `--subnet-prefixes`, `--vnet-name`, `--delegations` |
    | Variables | `$VNET_NAME`, `$RG`, `$LOCATION` |
    | Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


    #### B-9: VNet Integration

    ```bash
    az functionapp vnet-integration add \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --vnet "$VNET_NAME" \
      --subnet "snet-integration"
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az functionapp vnet-integration add` |
    | Key flags | `--name`, `--resource-group`, `--vnet`, `--subnet` |
    | Variables | `$APP_NAME`, `$RG`, `$VNET_NAME` |
    | Expected result | Azure CLI completes successfully and returns JSON, table, or no output depending on the command; verify the next documented check before continuing. |


    #### B-10: Managed Identity and RBAC

    ```bash
    az functionapp identity assign \
      --name "$APP_NAME" \
      --resource-group "$RG"

    export MI_PRINCIPAL_ID=$(az functionapp identity show \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --query "principalId" \
      --output tsv)

    export STORAGE_ID=$(az storage account show \
      --name "$STORAGE_NAME" \
      --resource-group "$RG" \
      --query "id" \
      --output tsv)

    az role assignment create \
      --assignee "$MI_PRINCIPAL_ID" \
      --role "Storage Blob Data Owner" \
      --scope "$STORAGE_ID"

    az role assignment create \
      --assignee "$MI_PRINCIPAL_ID" \
      --role "Storage Account Contributor" \
      --scope "$STORAGE_ID"

    az role assignment create \
      --assignee "$MI_PRINCIPAL_ID" \
      --role "Storage Queue Data Contributor" \
      --scope "$STORAGE_ID"
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az functionapp identity assign`, `az functionapp identity show`, `az storage account show`, `az role assignment create` |
    | Key flags | `--name`, `--resource-group`, `--query`, `--output`, `--assignee`, `--role`, `--scope` |
    | Variables | `$APP_NAME`, `$RG`, `$STORAGE_NAME`, `$MI_PRINCIPAL_ID`, `$STORAGE_ID` |
    | Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


    #### B-11: Lock Down Storage

    ```bash
    az storage account update \
      --name "$STORAGE_NAME" \
      --resource-group "$RG" \
      --allow-blob-public-access false
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az storage account update` |
    | Key flags | `--name`, `--resource-group`, `--allow-blob-public-access` |
    | Variables | `$STORAGE_NAME`, `$RG` |
    | Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


    #### B-12: Storage Private Endpoints (x4)

    ```bash
    for SVC in blob queue table file; do
      az network private-endpoint create \
        --name "pe-st-$SVC" \
        --resource-group "$RG" \
        --location "$LOCATION" \
        --vnet-name "$VNET_NAME" \
        --subnet "snet-private-endpoints" \
        --private-connection-resource-id "$STORAGE_ID" \
        --group-ids "$SVC" \
        --connection-name "conn-st-$SVC"
    done
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az network private-endpoint create` |
    | Key flags | `--name`, `--resource-group`, `--location`, `--vnet-name`, `--subnet`, `--private-connection-resource-id`, `--group-ids`, `--connection-name` |
    | Variables | `$SVC`, `$RG`, `$LOCATION`, `$VNET_NAME`, `$STORAGE_ID` |
    | Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


    #### B-13: Private DNS Zones and VNet Links (x4)

    ```bash
    for SVC in blob queue table file; do
      az network private-dns zone create \
        --resource-group "$RG" \
        --name "privatelink.$SVC.core.windows.net"

      az network private-dns link vnet create \
        --resource-group "$RG" \
        --zone-name "privatelink.$SVC.core.windows.net" \
        --name "link-$SVC" \
        --virtual-network "$VNET_NAME" \
        --registration-enabled false

      az network private-endpoint dns-zone-group create \
        --resource-group "$RG" \
        --endpoint-name "pe-st-$SVC" \
        --name "$SVC-dns-zone-group" \
        --private-dns-zone "privatelink.$SVC.core.windows.net" \
        --zone-name "$SVC"
    done
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az network private-dns zone create`, `az network private-dns link vnet`, `az network private-endpoint dns-zone-group create` |
    | Key flags | `--resource-group`, `--name`, `--zone-name`, `--virtual-network`, `--registration-enabled`, `--endpoint-name`, `--private-dns-zone` |
    | Variables | `$RG`, `$SVC`, `$VNET_NAME` |
    | Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


    #### B-14: Identity-Based Storage Config

    ```bash
    az functionapp config appsettings set \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --settings \
        "AzureWebJobsStorage__accountName=$STORAGE_NAME" \
        "AzureWebJobsStorage__credential=managedidentity"
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az functionapp config appsettings set` |
    | Key flags | `--name`, `--resource-group`, `--settings` |
    | Variables | `$APP_NAME`, `$RG`, `$STORAGE_NAME` |
    | Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


## Verification

`az deployment group create ...`:

```json
{
  "id": "/subscriptions/<subscription-id>/resourceGroups/rg-func-dedicated-dev/providers/Microsoft.Resources/deployments/<auto-generated-deployment-name>",
  "name": "<auto-generated-deployment-name>",
  "properties": {
    "provisioningState": "Succeeded",
    "timestamp": "2026-04-03T10:45:12.000000+00:00"
  },
  "resourceGroup": "rg-func-dedicated-dev"
}
```

`az appservice plan show ... --query ...`:

```json
{
  "kind": "linux",
  "name": "asp-dedi-b1-dev",
  "sku": "B1",
  "tier": "Basic"
}
```

## Next Steps

You now have reproducible Dedicated infrastructure in Bicep. Next you will automate deployment through CI/CD.

> **Next:** [06 - CI/CD](06-ci-cd.md)

## See Also

- [Tutorial Overview & Plan Chooser](../index.md)
- [Python Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources

- [Bicep documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [Microsoft.Web/serverfarms resource reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.web/serverfarms)
- [Microsoft.Web/sites resource reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.web/sites)
- [Functions infrastructure as code](https://learn.microsoft.com/en-us/azure/azure-functions/functions-infrastructure-as-code)
- [Python version and operating-system support](https://learn.microsoft.com/en-us/azure/azure-functions/supported-languages)
- [Storage private endpoints and DNS](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints)
- [Managed identities](https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity)
- [App access](https://learn.microsoft.com/en-us/azure/app-service/overview-access-restrictions#app-access)
- [Dedicated Always On](https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan#always-on)
- [Deployment technologies](https://learn.microsoft.com/en-us/azure/azure-functions/functions-deployment-technologies)
- [Functions monitoring](https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring)
- [Private endpoint overview](https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview)
- [Virtual network links for private DNS zones](https://learn.microsoft.com/en-us/azure/dns/private-dns-virtual-network-links)
