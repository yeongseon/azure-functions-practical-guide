---
validation:
  az_cli:
    last_tested: 2026-04-10
    cli_version: 2.83.0
    core_tools_version: 4.8.0
    result: pass
  bicep:
    last_tested: 2026-04-10
    result: pass
content_sources:

  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-node
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/overview
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
  diagrams:
    - id: what-you-ll-build
      type: flowchart
      source: self-generated
      justification: Flow view of what you ll build, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-infrastructure-as-code
        - https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-how-to#configure-deployment-settings
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-node
        - https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
    - id: what-you-ll-build-2
      type: flowchart
      source: self-generated
      justification: Flow view of what you ll build 2, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-node
        - https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
---
# 05 - Infrastructure as Code (Flex Consumption)

Deploy repeatable infrastructure with Bicep and parameterized environments.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 20+ | Local runtime and package execution |
| Azure Functions Core Tools | v4 | Local host and publishing |
| Azure CLI | 2.61+ | Azure resource provisioning and management |

!!! info "Flex Consumption plan basics"
    Flex Consumption (FC1) supports VNet integration, identity-based storage, per-function scaling, and remote build workflows.

## What You'll Build

You will deploy the complete Flex Consumption infrastructure stack from Bicep, including storage, hosting plan, managed identity, and Linux Function App resources.

!!! info "Infrastructure Context"
    **Plan**: Flex Consumption (FC1) | **Network**: VNet integration with private endpoints

    The production Bicep template at `infra/flex-consumption/main.bicep` includes full VNet integration, private endpoints, and DNS zones.

<!-- diagram-id: what-you-ll-build -->
```mermaid
flowchart TD
    accTitle: Node.js Linux Flex Consumption FC1 infrastructure configuration map
    accDescr: Illustrative provisioning and configuration associations for this Node.js 20 Linux FC1 example, including user-assigned identity, plan, storage and networking. Managed identity and disabled shared keys are this example's configuration; Flex deployment storage can instead use a connection string or managed identity. Arrows are not network hops, app containment in a subnet or serial creation order, and do not certify complete permissions or successful deployment. The runtime label describes the tutorial configuration, not a current support recommendation.
    BICEP["Bicep Template<br/>infra/flex-consumption/<br/>main.bicep"] -->|"az deployment<br/>group create"| RG[Resource Group]
    RG --> MI["User-Assigned<br/>Managed Identity"]
    RG --> PLAN["App Service Plan<br/>FC1<br/>FlexConsumption"]
    RG --> ST["Storage Account<br/>(no shared key)"]
    RG --> FA["Function App<br/>Linux<br/>Node.js 20"]
    RG --> VNET["VNet + Subnets<br/>+ Private<br/>Endpoints"]
    FA --> PLAN
    FA -->|MI auth| ST
    FA --> VNET

    %% Layout-only tiers; add no provisioning dependencies or visible arrows.
    MI ~~~ FA
    PLAN ~~~ ST
    ST ~~~ VNET
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class BICEP,RG,MI,PLAN,ST,FA,VNET baseNeutral;
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az deployment group create"\| RG[Resource` |
| Key flags | None |
| Variables | None |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


<!-- diagram-id: what-you-ll-build-2 -->
```mermaid
flowchart TD
    accTitle: Node.js Flex Consumption infrastructure tutorial task order
    accDescr: Illustrative tutorial stages: review the Bicep template, request a resource-group deployment, then verify provisioning. This is a task order, not serial resource creation or evidence of successful Azure execution.
    A[Review Bicep template] --> B["az deployment group create"]
    B --> C[Verify provisioning]
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az deployment group create"]` |
| Key flags | None |
| Variables | None |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


## Steps

### Step 1 - Set variables (if not already set)

```bash
export RG="rg-func-node-flex-demo"
export LOCATION="koreacentral"
```

### Step 2 - Review the Bicep template

The production template is at `infra/flex-consumption/main.bicep`. Below is a simplified example showing key Flex Consumption resources:

```bicep
param location string = resourceGroup().location
param baseName string

var functionAppName = '${baseName}-func'
var storageAccountName = toLower(replace('${baseName}storage', '-', ''))
var appServicePlanName = '${baseName}-plan'
var managedIdentityName = '${baseName}-identity'
var deploymentContainerName = 'deployment-packages'

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    allowSharedKeyAccess: false
  }
}

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: managedIdentityName
  location: location
}

resource plan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'FC1'
    tier: 'FlexConsumption'
  }
  properties: {
    reserved: true
  }
}

resource functionApp 'Microsoft.Web/sites@2024-04-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    functionAppConfig: {
      runtime: {
        name: 'node'
        version: '20'
      }
      scaleAndConcurrency: {
        maximumInstanceCount: 100
        instanceMemoryMB: 2048
      }
      deployment: {
        storage: {
          type: 'blobContainer'
          value: 'https://${storage.name}.blob.${environment().suffixes.storage}/${deploymentContainerName}'
          authentication: {
            type: 'UserAssignedIdentity'
            userAssignedIdentityResourceId: managedIdentity.id
          }
        }
      }
    }
  }
}
```

!!! note "Flex Consumption vs Consumption Bicep differences"
    - Uses `FC1` / `FlexConsumption` SKU instead of `Y1` / `Dynamic`
    - Uses `functionAppConfig` block (not `siteConfig.appSettings`) for runtime, scaling, and deployment
    - Supports `allowSharedKeyAccess: false` on storage (identity-based auth)
    - Uses blob container for deployment instead of Azure Files

### Step 3 - Deploy template

```bash
az deployment group create \
  --resource-group "$RG" \
  --template-file infra/flex-consumption/main.bicep \
  --parameters baseName=ndflex0410
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az deployment group create` |
| Key flags | `--resource-group`, `--template-file`, `--parameters` |
| Variables | `$RG` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


### Step 4 - Verify deployment state

```bash
az deployment group show \
  --resource-group "$RG" \
  --name main \
  --query "properties.provisioningState" \
  --output tsv
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az deployment group show` |
| Key flags | `--resource-group`, `--name`, `--query`, `--output` |
| Variables | `$RG` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


### Step 5 - Review Flex Consumption-specific notes

- The repository template includes full VNet integration with private endpoints and DNS zones. The simplified snippet above omits networking for clarity.
- Flex Consumption routes all traffic through the integrated VNet by default once `virtualNetworkSubnetId` is configured.
- Use long-form CLI flags for maintainable runbooks.

## Verification

Deployment output shows `Succeeded`:

```json
{
  "name": "main",
  "properties": {
    "provisioningState": "Succeeded",
    "mode": "Incremental",
    "timestamp": "2026-04-10T00:30:36.0000000Z"
  }
}
```

## Next Steps

> **Next:** [06 - CI/CD](06-ci-cd.md)

## See Also

- [Tutorial Overview & Plan Chooser](../index.md)
- [Node.js Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources

- [Azure Functions Node.js developer guide (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-node)
- [Automate resource deployment with Bicep (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/overview)
- [Azure Functions Flex Consumption plan (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan)
