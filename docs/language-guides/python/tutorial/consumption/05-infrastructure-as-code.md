# 05 - Infrastructure as Code (Consumption)

Define and deploy a complete Consumption (Y1) environment with Bicep. This plan is simpler than Flex: no VNet integration requirement, no private endpoints, and no mandatory managed identity (recommended for app access patterns).

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Azure CLI | 2.61+ | Run Bicep deployments |
| Bicep | latest | Author ARM resources as code |
| Target path | `infra/consumption/main.bicep` | Consumption IaC template location |

## Steps

### Step 1 - Set variables

```bash
export RG="rg-func-consumption-demo"
export APP_NAME="func-consumption-demo-001"
export STORAGE_NAME="stconsumptiondemo001"
export LOCATION="eastus"
```

### Step 2 - Create the resource group

```bash
az group create --name "$RG" --location "$LOCATION"
```

### Step 3 - Author `infra/consumption/main.bicep`

Use a Consumption plan resource with Y1/Dynamic SKU and classic app settings on the Function App:

```bicep
param location string = resourceGroup().location
param appName string
param storageName string

resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: 'asp-${appName}'
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  kind: 'functionapp'
}

resource app 'Microsoft.Web/sites@2023-12-01' = {
  name: appName
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: plan.id
    siteConfig: {
      linuxFxVersion: 'Python|3.11'
      appSettings: [
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storage.name};AccountKey=${listKeys(storage.id, storage.apiVersion).keys[0].value};EndpointSuffix=${environment().suffixes.storage}'
        }
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '1'
        }
      ]
    }
    httpsOnly: true
  }
}
```

### Step 4 - Deploy the Bicep template

```bash
az deployment group create \
  --resource-group "$RG" \
  --template-file "infra/consumption/main.bicep" \
  --parameters baseName="consumpdemo"

### Step 5 - Validate resulting host plan

```

```bash
az functionapp show \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --query "{kind:kind,state:state,defaultHostName:defaultHostName}" \
  --output json
```

!!! info "Not available on Consumption"
    VNet integration requires Flex Consumption, Premium, or Dedicated plan.

!!! info "Not available on Consumption"
    Private endpoints require Flex Consumption, Premium, or Dedicated plan.

!!! info "Consumption slot support"
    Consumption (Y1) supports deployment slots (2 total, including production).

## Expected Output

Deployment output excerpt:

```

```json
{
  "id": "/subscriptions/<subscription-id>/resourceGroups/rg-func-consumption-demo/providers/Microsoft.Resources/deployments/main",
  "name": "main",
  "properties": {
    "provisioningState": "Succeeded"
  }
}
```

Function app validation output:

```

```json
{
  "defaultHostName": "func-consumption-demo-001.azurewebsites.net",
  "kind": "functionapp,linux",
  "state": "Running"
}
```

## Next Steps

Automate deployments in CI/CD with GitHub Actions.

> **Next:** [06 - CI/CD](06-ci-cd.md)

## References

- [Bicep for Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-infrastructure-as-code)
- [Bicep language reference](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [Azure Functions Consumption plan](https://learn.microsoft.com/azure/azure-functions/consumption-plan)
