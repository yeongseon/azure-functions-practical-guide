---
hide:
  - toc
validation:
  az_cli:
    last_tested: 2026-04-12
    cli_version: "2.70.0"
    core_tools_version: "4.6.0"
    result: pass
  bicep:
    last_tested: null
    result: not_tested
content_sources:
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-reference-node
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/create-first-function-cli-node
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-scale
---

# 02 - First Deploy (Consumption)

Deploy the app to Azure Functions Consumption (Y1) using long-form CLI commands only. This tutorial uses Linux examples and notes Windows support where relevant.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 20+ | Local runtime and package execution |
| Azure Functions Core Tools | v4 | Local host and publishing |
| Azure CLI | 2.61+ | Azure resource provisioning and management |
| Azure subscription | Active | Target for deployment |

!!! info "Consumption plan basics"
    Consumption (Y1) is serverless with scale-to-zero, up to 200 instances, 1.5 GB memory per instance, and a default 5-minute timeout (max 10 minutes).

## What You'll Build

You will provision a Linux Function App on the Consumption plan, publish your Node.js v4 app, and validate trigger discovery.

!!! info "Infrastructure Context"
    **Plan**: Consumption (Y1) | **Network**: Public internet only | **VNet**: ❌ Not supported

    Consumption has no VNet integration or private endpoint support. All traffic flows over the public internet. Storage uses connection string authentication.

    <!-- diagram-id: what-you-ll-build -->
```mermaid
flowchart TD
    INET[Internet] -->|HTTPS| FA[Function App\nConsumption Y1\nLinux Node.js 20]

    FA -->|connection string| ST[Storage Account\npublic access]
    FA --> AI[Application Insights]

    subgraph STORAGE[Storage Services]
        ST --- FS[Azure Files\ncontent share]
    end

    NO_VNET["⚠️ No VNet integration\nNo private endpoints"] -. limitation .- FA

    style FA fill:#0078d4,color:#fff
    style NO_VNET fill:#FFF3E0,stroke:#FF9800
    style STORAGE fill:#FFF3E0
```

<!-- diagram-id: what-you-ll-build-2 -->
```mermaid
flowchart LR
    A[Set variables + login] --> B[Create RG + storage]
    B --> C[Create function app]
    C --> D[Set placeholder settings]
    D --> E["func azure functionapp publish"]
    E --> F[Validate endpoints]
```

## Steps

### Step 1 - Set variables and sign in

```bash
export RG="rg-func-node-consumption-demo"
export APP_NAME="func-ndcons-$(date +%m%d%H%M)"
export STORAGE_NAME="stndconsdev$(date +%m%d)"
export LOCATION="koreacentral"

az login
az account set --subscription "<subscription-id>"
```

| Command/Parameter | Purpose |
|-------------------|---------|
| `export RG="..."` | Sets the resource group name for the deployment. |
| `export APP_NAME="..."` | Defines a unique name for the Function App using a timestamp. |
| `export STORAGE_NAME="..."` | Sets a valid, unique name for the storage account. |
| `export LOCATION="koreacentral"` | Chooses the Azure region for the deployment. |
| `az login` | Authenticates your CLI session with Azure. |
| `az account set --subscription` | Targets the specific Azure subscription for resource creation. |

!!! note "Storage account name limits"
    Storage account names must be 3-24 characters, lowercase letters and digits only. The `$STORAGE_NAME` pattern above keeps names short to stay within limits.

### Step 2 - Create resource group and storage account

```bash
az group create --name "$RG" --location "$LOCATION"

az storage account create \
  --name "$STORAGE_NAME" \
  --resource-group "$RG" \
  --location "$LOCATION" \
  --sku Standard_LRS \
  --kind StorageV2
```

| Command/Parameter | Purpose |
|-------------------|---------|
| `az group create` | Provisions a new Azure resource group container. |
| `--name "$RG"` | Specifies the resource group name. |
| `--location "$LOCATION"` | Sets the geographical region for the group. |
| `az storage account create` | Provisions a new Azure Storage account. |
| `--sku Standard_LRS` | Selects locally-redundant storage for cost-efficiency. |
| `--kind StorageV2` | Uses the general-purpose v2 storage account type. |

### Step 3 - Create function app

```bash
az functionapp create \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --storage-account "$STORAGE_NAME" \
  --consumption-plan-location "$LOCATION" \
  --runtime node \
  --runtime-version 20 \
  --functions-version 4 \
  --os-type Linux
```

| Command/Parameter | Purpose |
|-------------------|---------|
| `az functionapp create` | Provisions the core Function App resource. |
| `--consumption-plan-location` | Specifies the region for the serverless Consumption plan. |
| `--runtime node` | Selects the Node.js execution environment. |
| `--runtime-version 20` | Pins the Node.js version to v20. |
| `--functions-version 4` | Uses version 4 of the Azure Functions runtime host. |
| `--os-type Linux` | Deploys the app on a Linux infrastructure. |

!!! note "Auto-created Application Insights"
    `az functionapp create` automatically provisions an Application Insights resource and links it to the function app. You do not need to create one manually unless you want a custom name or configuration.

### Step 4 - Set placeholder trigger settings

```bash
STORAGE_CONN=$(az storage account show-connection-string \
  --name "$STORAGE_NAME" \
  --resource-group "$RG" \
  --output tsv)

az functionapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --settings \
    "QueueStorage=$STORAGE_CONN" \
    "EventHubConnection=Endpoint=sb://placeholder.servicebus.windows.net/;SharedAccessKeyName=placeholder;SharedAccessKey=placeholder;EntityPath=placeholder" \
    "TIMER_LAB_SCHEDULE=0 */5 * * * *"
```

| Command/Parameter | Purpose |
|-------------------|---------|
| `az storage account show-connection-string` | Retrieves the full connection string for the storage account. |
| `az functionapp config appsettings set` | Updates the application settings for the Function App. |
| `--settings` | Defines the key-value pairs required by the function triggers. |

!!! warning "Placeholder settings prevent host errors"
    The Node.js v4 reference app includes triggers for Queue, EventHub, and Timer. If these connection settings are missing, the Functions host enters an `Error` state and cannot index any functions. Use placeholder values until real resources are provisioned.

### Step 5 - Publish app

```bash
cd apps/nodejs && func azure functionapp publish "$APP_NAME"
```

| Command/Parameter | Purpose |
|-------------------|---------|
| `cd apps/nodejs` | Moves the terminal into the source code directory. |
| `func azure functionapp publish` | Bundles, uploads, and deploys the app source code. |

!!! note "Upload size"
    Node.js function apps include `node_modules` in the deployment package, resulting in ~49 MB uploads. This is significantly larger than Python (~2 MB). The upload may take a few minutes on slower connections.

### Step 6 - Validate deployment

```bash
# List deployed functions
az functionapp function list \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --output table

# Test the health endpoint
curl --request GET "https://$APP_NAME.azurewebsites.net/api/health"

# Test the hello endpoint
curl --request GET "https://$APP_NAME.azurewebsites.net/api/hello/Azure"
```

| Command/Parameter | Purpose |
|-------------------|---------|
| `az functionapp function list` | Queries ARM to retrieve the list of indexed functions. |
| `--output table` | Formats the function list as a readable text table. |
| `curl --request GET` | Sends an HTTP GET request to verify the live endpoints. |


### Step 7 - Review Consumption-specific notes

- Use `--consumption-plan-location` for app creation and expect cold starts under idle periods.
- Use long-form CLI flags for maintainable runbooks.
- Keep `FUNCTIONS_WORKER_RUNTIME=node` across all environments.

## Verification

Function list output (showing key fields):

```json
[
  {
    "name": "helloHttp",
    "type": "Microsoft.Web/sites/functions",
    "invokeUrlTemplate": "https://<app-name>.azurewebsites.net/api/hello/{name?}",
    "language": "node",
    "isDisabled": false
  }
]
```

!!! warning "Language field is `node`, not `Javascript`"
    The `language` field in the function list output returns `"node"` for Node.js v4 apps deployed to Linux Consumption. Earlier documentation may show `"Javascript"` — this is incorrect for current deployments.

Health endpoint response:

```json
{"status":"healthy","timestamp":"2026-04-10T00:15:00.000Z","version":"1.0.0"}
```

Hello endpoint response:

```json
{"message":"Hello, Azure"}
```

## Next Steps

> **Next:** [03 - Configuration](03-configuration.md)

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
