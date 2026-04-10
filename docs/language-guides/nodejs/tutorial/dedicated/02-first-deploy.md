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
content_sources:
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-reference-node
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/create-first-function-cli-node
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-scale
---

# 02 - First Deploy (Dedicated)

Provision resources and publish your first Node.js v4 function app to an App Service (Dedicated) plan.

## Prerequisites

- You completed [01 - Run Locally](01-local-run.md).
- You are signed in to Azure CLI and have Contributor access.
- You already exported: `$RG`, `$APP_NAME`, `$PLAN_NAME`, `$STORAGE_NAME`, `$LOCATION` (use `koreacentral` for this guide).

## What You'll Build

- A Linux Node.js Function App on Dedicated B1 with Always On support.
- A first deployment pipeline (`func azure functionapp publish`) and endpoint verification.
- All 20 functions indexed and serving requests on Dedicated infrastructure.

!!! info "Infrastructure Context"
    **Plan**: Dedicated (B1) | **Network**: Public | **Always On**: ✅

    Dedicated deploys on a traditional App Service Plan. Unlike Premium, there are no pre-warmed instances or elastic scaling — you get a fixed compute allocation. Storage uses connection string authentication by default. No content file share is required (`WEBSITE_RUN_FROM_PACKAGE=1`).

    <!-- diagram-id: what-you-ll-build -->
```mermaid
flowchart TD
    INET[Internet] -->|HTTPS| FA[Function App\nDedicated B1\nLinux Node.js 20]

    subgraph PLAN["App Service Plan\nB1 Basic"]
        FA
        ALWAYS["Always On ✅"]
    end

    FA --> ST["Storage Account\nBlob + Queue"]
    FA --> AI[Application Insights]
    FA -.->|System-Assigned MI| ENTRA[Microsoft Entra ID]

    style FA fill:#ff8c00,color:#fff
    style PLAN fill:#E3F2FD,stroke:#1976D2
    style ST fill:#FFF3E0
    style ALWAYS fill:#FFF3E0,stroke:#FF9800
```

## Steps

1. Set environment variables for the deployment.

    ```bash
    export RG="rg-func-node-ded-demo"
    export LOCATION="koreacentral"
    export STORAGE_NAME="stnddedi0410"
    export PLAN_NAME="plan-ndded-04100022"
    export APP_NAME="func-ndded-04100022"
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `export RG="..."` | Sets the resource group name for the deployment. |
    | `export LOCATION="..."` | Chooses the Azure region for the deployment. |
    | `export STORAGE_NAME="..."` | Defines a unique name for the storage account. |
    | `export PLAN_NAME="..."` | Sets the name for the App Service (Dedicated) plan. |
    | `export APP_NAME="..."` | Defines a globally unique name for the Function App. |

    !!! tip "Globally unique names required"
        Both `$APP_NAME` and `$STORAGE_NAME` must be globally unique across all Azure subscriptions. If you get a naming conflict, append a random suffix (e.g., `func-ndded-04091234`).

2. Authenticate and set subscription context.

    ```bash
    az login
    az account set --subscription "<subscription-id>"
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `az login` | Authenticates your CLI session with Azure. |
    | `az account set --subscription` | Targets the specific Azure subscription for resource creation. |

3. Create resource group.

    ```bash
    az group create \
      --name "$RG" \
      --location "$LOCATION"
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `az group create` | Provisions a new Azure resource group container. |
    | `--name "$RG"` | Specifies the resource group name. |
    | `--location "$LOCATION"` | Sets the geographical region for the group. |

    Expected output (abridged):

    ```json
    {
      "name": "rg-func-node-ded-demo",
      "location": "koreacentral",
      "properties": {
        "provisioningState": "Succeeded"
      }
    }
    ```

4. Create storage account.

    ```bash
    az storage account create \
      --name "$STORAGE_NAME" \
      --resource-group "$RG" \
      --location "$LOCATION" \
      --sku "Standard_LRS" \
      --kind "StorageV2" \
      --allow-blob-public-access false
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `az storage account create` | Provisions a new Azure Storage account. |
    | `--sku "Standard_LRS"` | Selects locally-redundant storage for cost-efficiency. |
    | `--kind "StorageV2"` | Uses the general-purpose v2 storage account type. |
    | `--allow-blob-public-access false` | Disables public access to blobs for better security. |

    Expected output (abridged):

    ```json
    {
      "name": "stnddedi0410",
      "location": "koreacentral",
      "kind": "StorageV2",
      "provisioningState": "Succeeded"
    }
    ```

5. Create the App Service Plan (B1, Linux).

    !!! warning "Dedicated uses `az appservice plan create`"
        Unlike Premium which uses `az functionapp plan create`, Dedicated plans use `az appservice plan create`. This is because Dedicated plans are standard App Service Plans, not elastic function-specific plans.

    ```bash
    az appservice plan create \
      --name "$PLAN_NAME" \
      --resource-group "$RG" \
      --location "$LOCATION" \
      --sku "B1" \
      --is-linux
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `az appservice plan create` | Provisions a standard Azure App Service Plan. |
    | `--sku "B1"` | Selects the Basic B1 pricing tier. |
    | `--is-linux` | Configures the plan for Linux-based workers. |

    Expected output (abridged):

    ```json
    {
      "name": "plan-ndded-04100022",
      "location": "koreacentral",
      "sku": {
        "name": "B1",
        "tier": "Basic"
      },
      "kind": "linux",
      "provisioningState": "Succeeded"
    }
    ```

6. Create the Function App on the Dedicated plan.

    ```bash
    az functionapp create \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --plan "$PLAN_NAME" \
      --storage-account "$STORAGE_NAME" \
      --runtime "node" \
      --runtime-version "20" \
      --functions-version "4" \
      --os-type "Linux"
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `az functionapp create` | Provisions the core Function App resource. |
    | `--plan "$PLAN_NAME"` | Links the app to the Dedicated App Service Plan. |
    | `--runtime "node"` | Selects the Node.js execution environment. |
    | `--runtime-version "20"` | Pins the Node.js version to v20. |
    | `--functions-version "4"` | Uses version 4 of the Azure Functions runtime host. |
    | `--os-type "Linux"` | Deploys the app on a Linux infrastructure. |

    !!! warning "Node.js 20 EOL approaching"
        Azure CLI warns: `Use node version 24 as 20 will reach end-of-life on 2026-04-30`. Consider using `--runtime-version 22` or later for new projects.

    Expected output (abridged):

    ```json
    {
      "name": "func-ndded-04100022",
      "state": "Running",
      "kind": "functionapp,linux",
      "defaultHostName": "func-ndded-04100022.azurewebsites.net"
    }
    ```

    !!! info "Application Insights auto-created"
        `az functionapp create` automatically creates an Application Insights resource with the **same name** as the function app (e.g., `func-ndded-04100022`), not `$APP_NAME-ai`. The `APPLICATIONINSIGHTS_CONNECTION_STRING` app setting is auto-configured.

    !!! tip "No content file share needed"
        Unlike Premium and Consumption plans, Dedicated does **not** require `WEBSITE_CONTENTAZUREFILECONNECTIONSTRING` or `WEBSITE_CONTENTSHARE`. Deployments use `WEBSITE_RUN_FROM_PACKAGE=1` (set automatically) which stores the package in blob storage.

7. Set required app settings for triggers.

    ```bash
    az functionapp config appsettings set \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --settings \
        "EventHubConnection__fullyQualifiedNamespace=placeholder.servicebus.windows.net" \
        "QueueStorage=$(az storage account show-connection-string --name $STORAGE_NAME --resource-group $RG --query connectionString --output tsv)"
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `az functionapp config appsettings set` | Updates the application settings for the Function App. |
    | `az storage account show-connection-string` | Retrieves the connection string for the storage account. |
    | `--settings` | Defines the key-value pairs required by the function triggers. |

    !!! note "EventHub placeholder required"
        If your app includes an Event Hub trigger, the function host may fail to start without a valid `EventHubConnection` setting. Set a placeholder namespace to allow function indexing.

8. Publish the app.

    ```bash
    cd apps/nodejs
    func azure functionapp publish "$APP_NAME"
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `cd apps/nodejs` | Moves the terminal into the source code directory. |
    | `func azure functionapp publish` | Bundles, uploads, and deploys the app source code. |

    Expected output (abridged):

    ```text
    Getting site publishing info...
    Uploading package...
    Uploading 49.36 MB [##############################################################]
    Upload completed successfully.
    Deployment completed successfully.
    ```

9. Validate deployment.

    ```bash
    az functionapp function list \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --output table
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `az functionapp function list` | Queries ARM to retrieve the list of indexed functions. |
    | `--output table` | Formats the function list as a readable text table. |

    !!! tip "Function indexing delay"
        After the first publish, it may take 30–60 seconds for all functions to appear in the ARM API. If the list is empty, wait and retry.

    Expected output (abridged — showing key functions):

    ```text
    Name                                          Language
    --------------------------------------------  ----------
    func-ndded-04100022/helloHttp                 node
    func-ndded-04100022/health                    node
    func-ndded-04100022/info                      node
    func-ndded-04100022/queueProcessor            node
    func-ndded-04100022/blobProcessor             node
    func-ndded-04100022/scheduledCleanup          node
    ```

    !!! note "Language field"
        The `Language` column shows `node`, not `Javascript`. This is the actual value returned by the ARM API for Node.js v4 apps.

10. Test the deployed endpoints.

    ```bash
    curl --request GET "https://$APP_NAME.azurewebsites.net/api/health"
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `curl --request GET` | Sends an HTTP GET request to verify the health endpoint. |

    Expected output:

    ```json
    {"status":"healthy","timestamp":"2026-04-09T16:05:04.222Z","version":"1.0.0"}
    ```

    ```bash
    curl --request GET "https://$APP_NAME.azurewebsites.net/api/hello/Dedicated"
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `curl --request GET` | Sends an HTTP GET request to verify the hello endpoint. |

    Expected output:

    ```json
    {"message":"Hello, Dedicated"}
    ```

    ```bash
    curl --request GET "https://$APP_NAME.azurewebsites.net/api/info"
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `curl --request GET` | Sends an HTTP GET request to verify the info endpoint. |


    !!! tip "Globally unique names required"
        Both `$APP_NAME` and `$STORAGE_NAME` must be globally unique across all Azure subscriptions. If you get a naming conflict, append a random suffix (e.g., `func-ndded-04091234`).

2. Authenticate and set subscription context.

    ```bash
    az login
    az account set --subscription "<subscription-id>"
    ```

3. Create resource group.

    ```bash
    az group create \
      --name "$RG" \
      --location "$LOCATION"
    ```

    Expected output (abridged):

    ```json
    {
      "name": "rg-func-node-ded-demo",
      "location": "koreacentral",
      "properties": {
        "provisioningState": "Succeeded"
      }
    }
    ```

4. Create storage account.

    ```bash
    az storage account create \
      --name "$STORAGE_NAME" \
      --resource-group "$RG" \
      --location "$LOCATION" \
      --sku "Standard_LRS" \
      --kind "StorageV2" \
      --allow-blob-public-access false
    ```

    Expected output (abridged):

    ```json
    {
      "name": "stnddedi0410",
      "location": "koreacentral",
      "kind": "StorageV2",
      "provisioningState": "Succeeded"
    }
    ```

5. Create the App Service Plan (B1, Linux).

    !!! warning "Dedicated uses `az appservice plan create`"
        Unlike Premium which uses `az functionapp plan create`, Dedicated plans use `az appservice plan create`. This is because Dedicated plans are standard App Service Plans, not elastic function-specific plans.

    ```bash
    az appservice plan create \
      --name "$PLAN_NAME" \
      --resource-group "$RG" \
      --location "$LOCATION" \
      --sku "B1" \
      --is-linux
    ```

    Expected output (abridged):

    ```json
    {
      "name": "plan-ndded-04100022",
      "location": "koreacentral",
      "sku": {
        "name": "B1",
        "tier": "Basic"
      },
      "kind": "linux",
      "provisioningState": "Succeeded"
    }
    ```

6. Create the Function App on the Dedicated plan.

    ```bash
    az functionapp create \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --plan "$PLAN_NAME" \
      --storage-account "$STORAGE_NAME" \
      --runtime "node" \
      --runtime-version "20" \
      --functions-version "4" \
      --os-type "Linux"
    ```

    !!! warning "Node.js 20 EOL approaching"
        Azure CLI warns: `Use node version 24 as 20 will reach end-of-life on 2026-04-30`. Consider using `--runtime-version 22` or later for new projects.

    Expected output (abridged):

    ```json
    {
      "name": "func-ndded-04100022",
      "state": "Running",
      "kind": "functionapp,linux",
      "defaultHostName": "func-ndded-04100022.azurewebsites.net"
    }
    ```

    !!! info "Application Insights auto-created"
        `az functionapp create` automatically creates an Application Insights resource with the **same name** as the function app (e.g., `func-ndded-04100022`), not `$APP_NAME-ai`. The `APPLICATIONINSIGHTS_CONNECTION_STRING` app setting is auto-configured.

    !!! tip "No content file share needed"
        Unlike Premium and Consumption plans, Dedicated does **not** require `WEBSITE_CONTENTAZUREFILECONNECTIONSTRING` or `WEBSITE_CONTENTSHARE`. Deployments use `WEBSITE_RUN_FROM_PACKAGE=1` (set automatically) which stores the package in blob storage.

7. Set required app settings for triggers.

    ```bash
    az functionapp config appsettings set \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --settings \
        "EventHubConnection__fullyQualifiedNamespace=placeholder.servicebus.windows.net" \
        "QueueStorage=$(az storage account show-connection-string --name $STORAGE_NAME --resource-group $RG --query connectionString --output tsv)"
    ```

    !!! note "EventHub placeholder required"
        If your app includes an Event Hub trigger, the function host may fail to start without a valid `EventHubConnection` setting. Set a placeholder namespace to allow function indexing.

8. Publish the app.

    ```bash
    cd apps/nodejs
    func azure functionapp publish "$APP_NAME"
    ```

    Expected output (abridged):

    ```text
    Getting site publishing info...
    Uploading package...
    Uploading 49.36 MB [##############################################################]
    Upload completed successfully.
    Deployment completed successfully.
    ```

9. Validate deployment.

    ```bash
    az functionapp function list \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --output table
    ```

    !!! tip "Function indexing delay"
        After the first publish, it may take 30–60 seconds for all functions to appear in the ARM API. If the list is empty, wait and retry.

    Expected output (abridged — showing key functions):

    ```text
    Name                                          Language
    --------------------------------------------  ----------
    func-ndded-04100022/helloHttp                 node
    func-ndded-04100022/health                    node
    func-ndded-04100022/info                      node
    func-ndded-04100022/queueProcessor            node
    func-ndded-04100022/blobProcessor             node
    func-ndded-04100022/scheduledCleanup          node
    ```

    !!! note "Language field"
        The `Language` column shows `node`, not `Javascript`. This is the actual value returned by the ARM API for Node.js v4 apps.

10. Test the deployed endpoints.

    ```bash
    curl --request GET "https://$APP_NAME.azurewebsites.net/api/health"
    ```

    Expected output:

    ```json
    {"status":"healthy","timestamp":"2026-04-09T16:05:04.222Z","version":"1.0.0"}
    ```

    ```bash
    curl --request GET "https://$APP_NAME.azurewebsites.net/api/hello/Dedicated"
    ```

    Expected output:

    ```json
    {"message":"Hello, Dedicated"}
    ```

    ```bash
    curl --request GET "https://$APP_NAME.azurewebsites.net/api/info"
    ```

    Expected output:

    ```json
    {
      "name": "azure-functions-nodejs-guide",
      "version": "1.0.0",
      "node": "v20.20.0",
      "environment": "production",
      "functionApp": "func-ndded-04100022"
    }
    ```

## Verification

The output confirms that Azure indexed your function definitions and the app serves requests. Verify:

- `az functionapp function list` shows functions with language `node`
- `curl` to the health endpoint returns `200 OK` with `{"status":"healthy",...}`
- `curl` to `/api/hello/Dedicated` returns `{"message":"Hello, Dedicated"}`

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
