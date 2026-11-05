---
validation:
  az_cli:
    last_tested:
    cli_version: 2.83.0
    core_tools_version: 4.8.0
    result: not_tested
  bicep:
    last_tested:
    result: not_tested
content_sources:

  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-java
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-premium-plan
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/app-service/configure-vnet-integration-enable
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/app-service/networking/private-endpoint
  diagrams:
    - id: what-you-ll-build
      type: flowchart
      source: self-generated
      justification: Intended Java 17 Linux EP1 Storage, identity, content and capacity relationships, with individual endpoint and DNS mappings in the adjacent key; not deployment evidence.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints
        - https://learn.microsoft.com/en-us/azure/azure-functions/storage-considerations
        - https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-java
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-premium-plan
        - https://learn.microsoft.com/en-us/azure/app-service/configure-vnet-integration-enable
        - https://learn.microsoft.com/en-us/azure/app-service/networking/private-endpoint
        - https://learn.microsoft.com/en-us/azure/app-service/overview-access-restrictions#app-access
    - id: deployment-verification-results
      type: flowchart
      source: self-generated
      justification: Conceptual EP1 private ingress and outbound path with a separate HTTP prewarm association; does not reclassify the historical blocked provisioning result.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-java
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-premium-plan
        - https://learn.microsoft.com/en-us/azure/app-service/configure-vnet-integration-enable
        - https://learn.microsoft.com/en-us/azure/app-service/networking/private-endpoint
---
# 02A - First Deploy (Private Egress)

Deploy a Java Function App to an Elastic Premium plan (`EP1`) with VNet integration and private endpoint support, then publish code and verify the app is live.

## Prerequisites

- You completed [01 - Run Locally](01-local-run.md).
- You are signed in to Azure CLI and have Contributor access.
- You already exported: `$RG`, `$APP_NAME`, `$PLAN_NAME`, `$STORAGE_NAME`, `$LOCATION` (use `koreacentral` for this guide).

| Tool | Minimum version | Purpose |
|---|---|---|
| JDK | 17+ | Compile and run Java functions locally |
| Maven | 3.6+ | Build and package Java artifacts |
| Azure Functions Core Tools | 4.x | Publish function code |
| Azure CLI | 2.60+ | Provision resources |

## What You'll Build

- A Linux Java Function App on Elastic Premium (`EP1`) with runtime settings.
- VNet integration and a site private endpoint for private inbound access.
- A first deployment pipeline (`func azure functionapp publish`) and endpoint verification.

!!! tip "Network Scenario Choices"
    This tutorial deploys with **VNet + Private Endpoints**. For other network configurations:

    | Scenario | Description | Guide |
    |----------|-------------|-------|
    | **Public Only** | No VNet, simplest setup | [Public Only](../../../../platform/networking-scenarios/public-only.md) |
    | **Private Egress** | VNet + Storage PE | [Private Egress](../../../../platform/networking-scenarios/private-egress.md) |
    | **Private Ingress** | + Site Private Endpoint (this tutorial) | Current page |
    | **Fixed Outbound IP** | + NAT Gateway | [Fixed Outbound](../../../../platform/networking-scenarios/fixed-outbound-nat.md) |

!!! info "Infrastructure Context"
    **Plan**: Premium (EP1) | **Network**: VNet + Private Endpoints | **Always warm**: ✅

    This Linux EP1 tutorial combines outbound integration with separate site and Storage private endpoints. Host storage supports connection-string or identity-based authentication; the default Azure Files content share uses its connection string. Prewarmed instances buffer HTTP scale-out, separately from the plan's minimum active capacity.

<!-- diagram-id: what-you-ll-build -->
```mermaid
%%{init: {'flowchart': {'nodeSpacing': 10, 'rankSpacing': 70, 'padding': 8, 'subGraphTitleMargin': {'top': 8, 'bottom': 32}}}}%%
flowchart TD
    accTitle: Java 17 Linux EP1 private Storage topology
    accDescr: Private Storage relationships for this Premium tutorial; public HTTPS after the site endpoint is added requires publicNetworkAccess explicitly Enabled (H). Outbound integration does not deploy app compute into the integration subnet. Four distinct Storage endpoints and DNS zones are expanded in the key; identity, telemetry and HTTP prewarm capacity are not data-transit hops. The separate site endpoint appears in the later path map.
    client(["Internet"])
    app_runtime["Function App<br/>EP1 · Linux<br/>Java 17"]
    identity{{"System MI<br/>Microsoft Entra ID"}}
    telemetry>"Application<br/>Insights"]
    warm_capacity["HTTP prewarm<br/>Capacity: W"]
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
    subgraph STORAGE["<div style='width:200px;text-align:left'>Content<br/>backend</div>"]
        SHARE[("Azure Files<br/>content share")]
    end
    client -->|"[Configured]<br/>HTTPS if H"| app_runtime
    app_runtime -.->|"[Configured]<br/>Identity"| identity
    app_runtime -.->|"[Configured]<br/>Telemetry"| telemetry
    app_runtime -.->|"[Configured]<br/>HTTP buffer"| warm_capacity
    dns_fn -.->|"[Configured]<br/>VNet link"| vnet_fn
    app_runtime -->|"[Configured]<br/>Outbound"| vnet_integration
    vnet_integration -->|"[Configured]<br/>Each PE"| pe_storage
    pe_storage -->|"[Configured]<br/>Each service"| storage_db
    %% Membership targets the content boundary, not a path through its title to SHARE.
    storage_db -.->|"[Configured]<br/>Contains"| STORAGE
    %% Layout-only tiers; add no requests, diagnostic steps or visible arrows.
    identity ~~~ telemetry
    telemetry ~~~ warm_capacity
    warm_capacity ~~~ dns_fn
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    classDef focusActive fill:#e6f0fd,stroke:#287ce4,stroke-width:2.5px,color:#14202e;
    classDef bandMuted fill:#ffffff,stroke:#707e93,stroke-width:1.5px,stroke-dasharray:4 3,color:#14202e;
    class client,storage_db,SHARE baseNeutral;
    class app_runtime,vnet_integration,pe_storage focusActive;
    class identity,telemetry,warm_capacity,dns_fn bandMuted;
    linkStyle default stroke-width:2px;
    linkStyle 2 stroke-width:1.5px;
```

**Reading key (Linux EP1):** Solid arrows show intended request/data access; dotted arrows show identity, telemetry, capacity, DNS-link association or membership. VNet integration is outbound-only and does not deploy the app into the integration subnet. DNS zones sit outside the VNet; their link targets the VNet boundary, not the integration role. Token acquisition summarizes the app's local identity endpoint, not a direct app-to-Entra network hop ([networking](https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options), [identity](https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity)).

| Key | Tutorial configuration / meaning |
|---|---|
| H | Public HTTPS after Step 8 requires `publicNetworkAccess: Enabled`, subject to site access restrictions; this tutorial does not explicitly enable it |
| VNet / integration / PE subnet | `10.20.0.0/16` / `10.20.1.0/24` / `10.20.2.0/24`; delegation `Microsoft.Web/serverFarms` |
| S | `allowBlobPublicAccess: false`, shared-key access allowed; anonymous-Blob blocking does not disable public networking |
| W | Premium minimum active billed instance: 1; default prewarmed HTTP buffer: 1; Linux regional maximum scale-out: 20–100, Korea Central: 20. These are different settings, not prewarm minimum/maximum |
| Content / identity | Default Azure Files content-share connection string is distinct from optional identity-based host storage; RBAC is not transport |

The bundled `pe_storage` node represents **four distinct endpoints**. Each row expands integration → endpoint → matching Storage service and endpoint → DNS zone-group association; these are separate service paths, not serial hops, and a workload can use several of them.

| Endpoint → Storage service | Linked private DNS zone |
|---|---|
| `PE_BLOB` → Blob | `privatelink.blob.core.windows.net` |
| `PE_QUEUE` → Queue | `privatelink.queue.core.windows.net` |
| `PE_TABLE` → Table | `privatelink.table.core.windows.net` |
| `PE_FILE` → File | `privatelink.file.core.windows.net` |

Clients retain normal Storage hostnames; with appropriate private DNS resolution configured for their network, these resolve to PE IPs. Private content-share routing must also be configured for secured Premium content storage. With `publicNetworkAccess` unset (`null`), adding the site endpoint in Step 8 disables public ingress by default. The Internet → app HTTPS arrow is conditional on explicitly setting `publicNetworkAccess: Enabled` (H), which this tutorial does not do; use the private-client → site endpoint → app path shown below for private ingress ([app access](https://learn.microsoft.com/en-us/azure/app-service/overview-access-restrictions#app-access), [Storage endpoints/DNS](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints), [storage](https://learn.microsoft.com/en-us/azure/azure-functions/storage-considerations), [Premium capacity](https://learn.microsoft.com/en-us/azure/azure-functions/functions-premium-plan), [site endpoint](https://learn.microsoft.com/en-us/azure/app-service/networking/private-endpoint)).

## Steps

1. Authenticate and set subscription context.

    ```bash
    az login
    az account set --subscription "<subscription-id>"
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `az login` | Authenticates your Azure CLI session. |
    | `az account set --subscription "<subscription-id>"` | Sets the active subscription for the current session. |
    | `--subscription "<subscription-id>"` | Specifies the target subscription ID. |

    Expected output (abridged):

    ```json
    [
      {
        "name": "<account-name>",
        "tenantId": "<tenant-id>",
        "id": "<subscription-id>",
        "isDefault": true
      }
    ]
    ```

    ```json
    {
      "id": "<subscription-id>",
      "name": "<subscription-name>",
      "state": "Enabled"
    }
    ```

2. Create resource group and storage account.

    ```bash
    export RG="rg-func-java-prem-demo"
    export STORAGE_NAME="stjprem$(openssl rand -hex 4)"
    export APP_NAME="func-jprem-$(openssl rand -hex 4)"
    export PLAN_NAME="plan-jprem-$(openssl rand -hex 4)"
    export LOCATION="koreacentral"

    az group create \
      --name "$RG" \
      --location "$LOCATION"

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
    | `az group create` | Provisions a new resource group. |
    | `--name "$RG"` | Sets the resource group name. |
    | `--location "$LOCATION"` | Places the resource group in the target region. |
    | `az storage account create` | Creates a storage account for function app use. |
    | `--sku "Standard_LRS"` | Uses Standard Locally Redundant Storage. |
    | `--kind "StorageV2"` | Selects General Purpose v2 storage account type. |
    | `--allow-blob-public-access false` | Disables public anonymous access to blobs. |

    Expected output (abridged):

    ```json
    {
      "name": "<resource-group-name>",
      "location": "koreacentral",
      "properties": {
        "provisioningState": "Succeeded"
      }
    }
    ```

    ```json
    {
      "name": "<storage-account-name>",
      "location": "koreacentral",
      "kind": "StorageV2",
      "sku": {
        "name": "Standard_LRS"
      },
      "allowBlobPublicAccess": false,
      "provisioningState": "Succeeded"
    }
    ```

3. Create the Premium plan and Function App (Linux example).

    ```bash
    az functionapp plan create \
      --name "$PLAN_NAME" \
      --resource-group "$RG" \
      --location "$LOCATION" \
      --sku "EP1" \
      --is-linux

    az functionapp create \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --plan "$PLAN_NAME" \
      --storage-account "$STORAGE_NAME" \
      --runtime "java" \
      --runtime-version "17" \
      --functions-version "4" \
      --os-type "Linux"
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `az functionapp plan create` | Provisions an Elastic Premium hosting plan. |
    | `--sku "EP1"` | Selects the initial Premium tier size. |
    | `--is-linux` | Configures the plan for Linux hosting. |
    | `az functionapp create` | Provisions the function app within the Premium plan. |
    | `--plan "$PLAN_NAME"` | Links the app to the newly created plan. |
    | `--runtime "java"` | Sets the language runtime to Java. |
    | `--runtime-version "17"` | Specifies the Java version. |
    | `--functions-version "4"` | Selects version 4.x of the runtime. |
    | `--os-type "Linux"` | Deploys the app on a Linux host. |

!!! tip "Globally unique names required"
    Both `$APP_NAME` and `$STORAGE_NAME` must be globally unique across all Azure subscriptions. If you get a naming conflict, append a random suffix (e.g., `func-jprem-04091234`).

    Expected output (abridged):

    ```json
    {
      "name": "<plan-name>",
      "location": "koreacentral",
      "sku": {
        "name": "EP1",
        "tier": "ElasticPremium"
      },
      "provisioningState": "Succeeded"
    }
    ```

    ```json
    {
      "name": "<function-app-name>",
      "state": "Running",
      "kind": "functionapp,linux",
      "defaultHostName": "<function-app-name>.azurewebsites.net"
    }
    ```

!!! warning "Enterprise policy: Shared key access"
    Some enterprise subscriptions enforce Azure Policy that sets `allowSharedKeyAccess: false` on all storage accounts. Premium (EP1) requires `WEBSITE_CONTENTAZUREFILECONNECTIONSTRING` with a connection string that uses shared key access to create the content file share during provisioning. If your subscription has this policy, the Function App creation will fail with a 403 error. Solutions:

    - Request a policy exemption from your Azure administrator
    - Use Flex Consumption (FC1) which supports identity-based blob storage without shared keys
    - Use Dedicated (B1) which uses `WEBSITE_RUN_FROM_PACKAGE` without a content file share

4. Configure app settings using classic `siteConfig.appSettings` model values.

    ```bash
    az functionapp config appsettings set \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --settings \
        "FUNCTIONS_WORKER_RUNTIME=java" \
        "AzureWebJobsStorage__accountName=$STORAGE_NAME" \
        "AzureWebJobsStorage__credential=managedidentity"
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `az functionapp config appsettings set` | Configures environment variables for the function app. |
    | `"FUNCTIONS_WORKER_RUNTIME=java"` | Sets the runtime worker to Java. |
    | `"AzureWebJobsStorage__accountName=$STORAGE_NAME"` | Sets the storage account name for host storage. |
    | `"AzureWebJobsStorage__credential=managedidentity"` | Configures the host to use managed identity for storage access. |

    Expected output (abridged):

    ```json
    [
      {
        "name": "FUNCTIONS_WORKER_RUNTIME",
        "value": "java"
      },
      {
        "name": "AzureWebJobsStorage__accountName",
        "value": "<storage-account-name>"
      },
      {
        "name": "AzureWebJobsStorage__credential",
        "value": "managedidentity"
      }
    ]
    ```

    For Premium, both host-storage models are valid:
    - Connection string: `AzureWebJobsStorage=<connection-string>`
    - Identity-based: `AzureWebJobsStorage__accountName=<storage-account-name>` plus `AzureWebJobsStorage__credential=managedidentity`

5. Enable a system-assigned managed identity for the Function App.

    ```bash
    az functionapp identity assign \
      --name "$APP_NAME" \
      --resource-group "$RG"

    export MI_PRINCIPAL_ID=$(az functionapp identity show \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --query "principalId" \
      --output tsv)
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `az functionapp identity assign` | Enables system-assigned managed identity for the app. |
    | `az functionapp identity show` | Retrieves properties of the app's identity. |
    | `--query "principalId"` | Extracts the principal ID for RBAC role assignments. |
    | `--output tsv` | Formats output for variable capture. |

    Expected output (abridged):

    ```json
    {
      "type": "SystemAssigned",
      "principalId": "<object-id>",
      "tenantId": "<tenant-id>"
    }
    ```

    ```text
    <object-id>
    ```

6. Assign storage RBAC roles to the managed identity.

    ```bash
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

    az role assignment create \
      --assignee "$MI_PRINCIPAL_ID" \
      --role "Storage File Data Privileged Contributor" \
      --scope "$STORAGE_ID"
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `az storage account show` | Retrieves the storage account resource ID. |
    | `az role assignment create` | Grants a specific RBAC role to the managed identity. |
    | `--assignee "$MI_PRINCIPAL_ID"` | Targets the function app's system-assigned identity. |
    | `--role "Storage Blob Data Owner"` | Grants full blob access for host data. |
    | `--role "Storage Account Contributor"` | Allows platform-level management of the storage account. |
    | `--role "Storage Queue Data Contributor"` | Grants access to storage queues for runtime operations. |
    | `--role "Storage File Data Privileged Contributor"` | Grants access to file shares for Premium content storage. |

    Expected output (abridged):

    ```text
    /subscriptions/<subscription-id>/resourceGroups/<resource-group-name>/providers/Microsoft.Storage/storageAccounts/<storage-account-name>
    ```

    ```json
    {
      "principalId": "<object-id>",
      "roleDefinitionName": "Storage Blob Data Owner",
      "scope": "/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>/providers/Microsoft.Storage/storageAccounts/<storage-account-name>"
    }
    ```

    ```json
    {
      "principalId": "<object-id>",
      "roleDefinitionName": "Storage Account Contributor",
      "scope": "/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>/providers/Microsoft.Storage/storageAccounts/<storage-account-name>"
    }
    ```

    ```json
    {
      "principalId": "<object-id>",
      "roleDefinitionName": "Storage Queue Data Contributor",
      "scope": "/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>/providers/Microsoft.Storage/storageAccounts/<storage-account-name>"
    }
    ```

    ```json
    {
      "principalId": "<object-id>",
      "roleDefinitionName": "Storage File Data Privileged Contributor",
      "scope": "/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>/providers/Microsoft.Storage/storageAccounts/<storage-account-name>"
    }
    ```

    !!! tip "Why these four roles are required on Premium"
        Premium Function Apps need host storage and Azure Files content share access during provisioning and runtime:

        - `Storage Blob Data Owner` for host blobs, leases, and trigger state.
        - `Storage Account Contributor` for storage account-level management operations used by the platform.
        - `Storage Queue Data Contributor` for queue-backed host coordination and trigger operations.
        - `Storage File Data Privileged Contributor` for the Azure Files content share (`WEBSITE_CONTENTAZUREFILECONNECTIONSTRING`) used by Premium.

7. Create a VNet with separate subnets for integration and private endpoints.

    ```bash
    az network vnet create \
      --name "vnet-premium-demo" \
      --resource-group "$RG" \
      --location "$LOCATION" \
      --address-prefixes "10.20.0.0/16" \
      --subnet-name "snet-integration" \
      --subnet-prefixes "10.20.1.0/24"

    az network vnet subnet create \
      --name "snet-private-endpoints" \
      --resource-group "$RG" \
      --vnet-name "vnet-premium-demo" \
      --address-prefixes "10.20.2.0/24"

    az network vnet subnet update \
      --name "snet-integration" \
      --resource-group "$RG" \
      --vnet-name "vnet-premium-demo" \
      --delegations "Microsoft.Web/serverFarms"

    az functionapp vnet-integration add \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --vnet "vnet-premium-demo" \
      --subnet "snet-integration"

    for SVC in blob queue table file; do
      az network private-endpoint create \
        --name "pe-st-$SVC" \
        --resource-group "$RG" \
        --location "$LOCATION" \
        --vnet-name "vnet-premium-demo" \
        --subnet "snet-private-endpoints" \
        --private-connection-resource-id "$STORAGE_ID" \
        --group-ids "$SVC" \
        --connection-name "conn-st-$SVC"
    done
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `az network vnet create` | Provisions a new Virtual Network. |
    | `--address-prefixes "10.20.0.0/16"` | Defines the CIDR range for the VNet. |
    | `az network vnet subnet create` | Adds a subnet for private endpoints. |
    | `az network vnet subnet update` | Modifies the integration subnet. |
    | `--delegations "Microsoft.Web/serverFarms"` | Delegating the subnet to Premium hosting plans. |
    | `az functionapp vnet-integration add` | Configures outbound traffic to flow through the VNet. |
    | `az network private-endpoint create` | Provisions private endpoints for storage services. |
    | `--group-ids "$SVC"` | Specifies the storage sub-resource (blob, queue, etc). |

    Expected output (abridged):

    ```json
    {
      "newVNetName": "vnet-premium-demo",
      "newSubnetName": "snet-integration",
      "newRouteAllEnabled": false
    }
    ```

    ```text
    {
      "name": "pe-st-blob",
      "provisioningState": "Succeeded"
    }
    {
      "name": "pe-st-queue",
      "provisioningState": "Succeeded"
    }
    {
      "name": "pe-st-table",
      "provisioningState": "Succeeded"
    }
    {
      "name": "pe-st-file",
      "provisioningState": "Succeeded"
    }
    ```

8. Create a private endpoint for inbound private access.

    ```bash
    APP_ID=$(az functionapp show \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --query "id" \
      --output tsv)

    az network private-endpoint create \
      --name "pe-$APP_NAME" \
      --resource-group "$RG" \
      --location "$LOCATION" \
      --vnet-name "vnet-premium-demo" \
      --subnet "snet-private-endpoints" \
      --private-connection-resource-id "$APP_ID" \
      --group-ids "sites" \
      --connection-name "conn-$APP_NAME"
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `az functionapp show` | Retrieves the function app resource ID. |
    | `az network private-endpoint create` | Provisions an inbound private endpoint for the function app. |
    | `--group-ids "sites"` | Targets the primary web app (site) resource. |
    | `--connection-name "conn-$APP_NAME"` | Sets the private link connection name. |

    Expected output (abridged):

    ```text
    /subscriptions/<subscription-id>/resourceGroups/<resource-group-name>/providers/Microsoft.Web/sites/<function-app-name>
    ```

    ```json
    {
      "name": "pe-<function-app-name>",
      "provisioningState": "Succeeded",
      "privateLinkServiceConnections": [
        {
          "groupIds": [
            "sites"
          ]
        }
      ]
    }
    ```

    Private endpoint name resolution requires private DNS configuration. At minimum, create and link `privatelink.azurewebsites.net` to the VNet, then attach the zone to the private endpoint:

    ```bash
    az network private-dns zone create \
      --resource-group "$RG" \
      --name "privatelink.azurewebsites.net"

    az network private-dns link vnet create \
      --resource-group "$RG" \
      --zone-name "privatelink.azurewebsites.net" \
      --name "link-vnet-premium-demo" \
      --virtual-network "vnet-premium-demo" \
      --registration-enabled false

    az network private-endpoint dns-zone-group create \
      --resource-group "$RG" \
      --endpoint-name "pe-$APP_NAME" \
      --name "web-dns-zone-group" \
      --private-dns-zone "privatelink.azurewebsites.net" \
      --zone-name "web-config"

    for SVC in blob queue table file; do
      az network private-dns zone create \
        --resource-group "$RG" \
        --name "privatelink.$SVC.core.windows.net"

      az network private-dns link vnet create \
        --resource-group "$RG" \
        --zone-name "privatelink.$SVC.core.windows.net" \
        --name "link-$SVC" \
        --virtual-network "vnet-premium-demo" \
        --registration-enabled false

      az network private-endpoint dns-zone-group create \
        --resource-group "$RG" \
        --endpoint-name "pe-st-$SVC" \
        --name "$SVC-dns-zone-group" \
        --private-dns-zone "privatelink.$SVC.core.windows.net" \
        --zone-name "$SVC"
    done
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `az network private-dns zone create` | Provisions private DNS zones for name resolution. |
    | `az network private-dns link vnet create` | Links the DNS zone to the VNet for resolution. |
    | `az network private-endpoint dns-zone-group create` | Connects the private endpoint to its DNS zone for automatic IP registration. |

    Expected output (abridged):

    ```json
    {
      "name": "privatelink.azurewebsites.net",
      "numberOfRecordSets": 0
    }
    ```

    ```json
    {
      "name": "web-dns-zone-group",
      "provisioningState": "Succeeded"
    }
    ```

    ```text
    {
      "name": "privatelink.blob.core.windows.net",
      "provisioningState": "Succeeded"
    }
    {
      "name": "privatelink.queue.core.windows.net",
      "provisioningState": "Succeeded"
    }
    {
      "name": "privatelink.table.core.windows.net",
      "provisioningState": "Succeeded"
    }
    {
      "name": "privatelink.file.core.windows.net",
      "provisioningState": "Succeeded"
    }
    ```

9. Build and publish function code (Premium supports file share-based deployment and SCM/Kudu).

    ```bash
    cd apps/java
    mvn clean package
    cd target/azure-functions/azure-functions-java-guide
    func azure functionapp publish "$APP_NAME"
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `cd apps/java` | Navigates to the Java project directory. |
    | `mvn clean package` | Compiles the Java source and packages it into the Maven staging directory. |
    | `cd target/azure-functions/azure-functions-java-guide` | Navigates to the Maven staging directory containing deployment artifacts. |
    | `func azure functionapp publish "$APP_NAME"` | Deploys the local project to the Azure Function App. |

    Expected output (abridged):

    ```text
    [INFO] BUILD SUCCESS
    ...
    Getting site publishing info...
    Creating archive for current directory...
    Upload completed successfully.
    Deployment completed successfully.
    Syncing triggers...
    ```

10. Verify app status and endpoint.

    ```bash
    az functionapp show \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --output table

    curl --request GET "https://$APP_NAME.azurewebsites.net/api/health"
    ```

    | Command/Parameter | Purpose |
    |-------------------|---------|
    | `az functionapp show` | Displays function app status. |
    | `--output table` | Formats output as a table. |
    | `curl --request GET` | Tests the public HTTP endpoint. |

    Expected output (abridged):

    ```text
    Name               State    DefaultHostName
    -----------------  -------  ----------------------------------------
    <function-app-name> Running  <function-app-name>.azurewebsites.net
    ```

    ```json
    {"status":"healthy","timestamp":"2026-01-01T00:00:00Z","version":"1.0.0"}
    ```

!!! warning "Auto-created Application Insights"
    `az functionapp create` automatically creates an Application Insights resource and links it via `APPINSIGHTS_INSTRUMENTATIONKEY` and `APPLICATIONINSIGHTS_CONNECTION_STRING`. Tutorial 04 creates a second, explicit Application Insights resource. You may see duplicate resources — this is expected.

## Verification

### Expected output when policy allows shared key access

```json
{
  "id": "/subscriptions/<subscription-id>/resourceGroups/rg-func-java-prem-demo/providers/Microsoft.Web/sites/<app-name>",
  "location": "koreacentral",
  "name": "<app-name>",
  "state": "Running",
  "defaultHostName": "<app-name>.azurewebsites.net"
}
```

```text
[INFO] BUILD SUCCESS
...
Getting site publishing info...
Creating archive for current directory...
Uploading 326.47 KB [########################################]
Upload completed successfully.
Deployment completed successfully.
Syncing triggers...
Functions in <app-name>:
    health - [httpTrigger]
    info - [httpTrigger]
```

```json
{"status":"healthy","timestamp":"2026-01-01T00:00:00Z","version":"1.0.0"}
```

### Deployment Verification Results

!!! warning "Blocked by enterprise policy"
    In our Korea Central deployment, EP1 Premium was blocked during provisioning by the same `allowSharedKeyAccess: false` policy as Consumption. Premium plans also require `WEBSITE_CONTENTAZUREFILECONNECTIONSTRING` with shared key access for the content file share.

    **Observed error:**

    ```text
    ERROR: Creation of storage file share failed with: 'The remote server returned an error: (403) Forbidden.'.
    Please check if the storage account is accessible.
    ```

    **Workarounds:**

    - Request a policy exemption from your Azure administrator
    - Use Flex Consumption (FC1) which supports identity-based blob storage
    - Use Dedicated (B1) which uses `WEBSITE_RUN_FROM_PACKAGE` without a content file share

<!-- diagram-id: deployment-verification-results -->
```mermaid
flowchart TD
    accTitle: Linux EP1 private ingress and outbound path
    accDescr: Conceptual private-reachable client through the site endpoint to the Premium app, then outbound integration to a private backend. HTTP prewarm capacity is a separate association, not a request hop or evidence that the historical blocked deployment succeeded.
    client(["Internet-origin client<br/>Private reachability"]) -->|"[Configured]<br/>HTTPS"| pe_site[["Site private endpoint"]]
    pe_site -->|"[Configured]<br/>Private Link"| app_runtime["Function App<br/>Premium EP1"]
    app_runtime -->|"[Configured]<br/>Outbound"| vnet_integration[["VNet integration subnet"]]
    vnet_integration -->|"[Configured]<br/>Private access"| storage_db[("Private backend")]
    app_runtime -.->|"[Configured]<br/>HTTP buffer"| warm_capacity["Prewarmed instances"]
    %% Layout-only tier; adds no request or diagnostic step.
    warm_capacity ~~~ vnet_integration
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class client,pe_site,app_runtime,vnet_integration,storage_db,warm_capacity baseNeutral;
```

**Takeaway:** This is a conceptual network/capacity map, not a successful verification trace; the historical provisioning result above is unchanged. Private ingress needs network reachability (for example VPN or ExpressRoute) and DNS resolving the app hostname to the site PE IP. Keep that hostname for TLS. Outbound integration and the HTTP prewarm buffer have separate roles ([site endpoints](https://learn.microsoft.com/en-us/azure/app-service/networking/private-endpoint), [Premium](https://learn.microsoft.com/en-us/azure/azure-functions/functions-premium-plan)).

## Next Steps

> **Next:** [03 - Configuration](03-configuration.md)

## See Also

- [Tutorial Overview & Plan Chooser](../index.md)
- [Java Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources

- [Azure Functions Premium plan](https://learn.microsoft.com/en-us/azure/azure-functions/functions-premium-plan)
- [Integrate your app with an Azure virtual network](https://learn.microsoft.com/en-us/azure/app-service/configure-vnet-integration-enable)
- [Use private endpoints for Azure App Service apps](https://learn.microsoft.com/en-us/azure/app-service/networking/private-endpoint)
- [App Service app access and public-network defaults](https://learn.microsoft.com/en-us/azure/app-service/overview-access-restrictions#app-access)
