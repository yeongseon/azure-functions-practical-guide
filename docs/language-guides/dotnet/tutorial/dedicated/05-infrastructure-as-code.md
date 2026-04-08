# 05 - Infrastructure as Code (Dedicated)

Define the Dedicated environment in Bicep and deploy the same architecture repeatedly across environments.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| .NET SDK | 8.0 (LTS) | Build and run isolated worker functions |
| Azure Functions Core Tools | v4 | Local host and deployment commands |
| Azure CLI | 2.61+ | Provision and configure Azure resources |

!!! info "Plan basics"
    Dedicated (App Service Plan) runs on pre-provisioned compute with predictable cost. Enable Always On for non-HTTP triggers.
    Supports VNet integration and slots on eligible SKUs.

## What You'll Build

- A Dedicated plan Bicep template with Linux .NET isolated worker configuration
- Required host storage settings plus `alwaysOn` for non-HTTP triggers
- Repeatable infrastructure deployment and validation commands

## Steps
### Step 1 - Create a Bicep template for Dedicated
```bicep
param location string = resourceGroup().location
param appName string
param storageName string
param planName string
param storageConnectionString string

resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}

resource appPlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  sku: {
    name: 'B1'
  }
  kind: 'functionapp'
  properties: {
    reserved: true
  }
}

resource app 'Microsoft.Web/sites@2023-12-01' = {
  name: appName
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: appPlan.id
    siteConfig: {
      linuxFxVersion: 'DOTNET-ISOLATED|8.0'
      alwaysOn: true
      appSettings: [
        { name: 'FUNCTIONS_WORKER_RUNTIME'; value: 'dotnet-isolated' }
        { name: 'FUNCTIONS_EXTENSION_VERSION'; value: '~4' }
        { name: 'AzureWebJobsStorage'; value: storageConnectionString }
      ]
    }
  }
}
```

### Step 2 - Deploy the template
```bash
az deployment group create \
  --resource-group "$RG" \
  --template-file "infra/dedicated/main.bicep" \
  --parameters \
    appName="$APP_NAME" \
    storageName="$STORAGE_NAME" \
    planName="$PLAN_NAME" \
    storageConnectionString="$(az storage account show-connection-string --name "$STORAGE_NAME" --resource-group "$RG" --query "connectionString" --output tsv)"
```

### Step 3 - Validate created resources
```bash
az functionapp show \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --query "{kind:kind,state:state,defaultHostName:defaultHostName}" \
  --output json
```

```mermaid
flowchart LR
    A[Bicep template] --> B[Resource Group deployment]
    B --> C[Storage + Plan + Function App]
    C --> D[Runtime dotnet-isolated]
```
### Step X - Validate isolated worker conventions
```bash
grep "FUNCTIONS_WORKER_RUNTIME" "local.settings.json"
grep "ConfigureFunctionsWebApplication" "Program.cs"
```

Confirm that HTTP functions use `HttpRequestData` and `HttpResponseData`, and that logging is constructor-injected with `ILogger<T>`.

## Verification
```json
{
  "kind": "functionapp,linux",
  "state": "Running",
  "defaultHostName": "func-dotnet-dedicated-demo.azurewebsites.net"
}
```

## See Also
- [Tutorial Overview & Plan Chooser](../index.md)
- [.NET Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources
- [Azure Functions .NET isolated worker guide](https://learn.microsoft.com/azure/azure-functions/dotnet-isolated-process-guide)
- [Develop Azure Functions locally with Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-develop-local)
- [Azure Functions hosting options](https://learn.microsoft.com/azure/azure-functions/functions-scale)
