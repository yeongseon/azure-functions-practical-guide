# 05 - Infrastructure as Code (Dedicated)

Describe your Java Function App platform using Bicep so provisioning is deterministic and easy to review.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| JDK | 17+ | Compile and run Java functions locally |
| Maven | 3.9+ | Build and deploy Java artifacts |
| Azure Functions Core Tools | v4 | Start local host and publish artifacts |
| Azure CLI | 2.61+ | Provision Azure resources and inspect app state |

!!! info "Plan basics"
    Dedicated (App Service Plan) runs Functions on reserved capacity. Choose it when you already operate App Service workloads and prefer fixed-cost hosting.

```mermaid
flowchart TD
    A[Bicep template] --> B[az deployment group create]
    B --> C[Function App + Plan + Storage]
    C --> D[Maven deployment]
```

## What You'll Build

- A Dedicated App Service Plan infrastructure baseline for Java Functions.
- App settings aligned to Dedicated deployment (`WEBSITE_RUN_FROM_PACKAGE`).
- A repeatable deployment command using the `baseName` parameter.

## Steps

### Step 1 - Author Bicep parameters for Java app

```bicep
param location string = resourceGroup().location
param baseName string

var appServicePlanName = '${baseName}-plan'
var functionAppName = '${baseName}-func'
var storageAccountName = toLower(replace('${baseName}storage', '-', ''))
```

### Step 2 - Define Function App runtime settings

```bicep
resource appServicePlan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: appServicePlanName
  location: location
  kind: 'linux'
  sku: {
    name: 'P1V3'
    tier: 'PremiumV3'
  }
  properties: {
    reserved: true
  }
}

resource functionApp 'Microsoft.Web/sites@2023-12-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'JAVA|17'
      alwaysOn: true
      appSettings: [
        { name: 'FUNCTIONS_WORKER_RUNTIME'; value: 'java' }
        { name: 'JAVA_OPTS'; value: '-Xms256m -Xmx512m' }
        { name: 'WEBSITE_RUN_FROM_PACKAGE'; value: '1' }
        { name: 'AzureWebJobsStorage__accountName'; value: storageAccountName }
      ]
    }
  }
}
```

### Step 3 - Deploy infrastructure

```bash
az deployment group create --resource-group $RG --template-file infra/dedicated/main.bicep --parameters baseName=$BASE_NAME
```

### Step 4 - Deploy application artifact

```bash
mvn clean package
mvn azure-functions:deploy
```

## Verification

```text
ProvisioningState  Timestamp
----------------  --------------------------
Succeeded         2026-04-06T10:30:00.000Z
```

## See Also

- [Tutorial Overview & Plan Chooser](../index.md)
- [Java Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources

- [Azure Functions Java developer guide (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-java)
- [Azure Functions hosting options (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-scale)
- [Create a Java function with Azure Functions Core Tools (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/create-first-function-cli-java)
