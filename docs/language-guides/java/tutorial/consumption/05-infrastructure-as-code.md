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
---

# 05 - Infrastructure as Code (Consumption)

Describe your Java Function App platform using Bicep so provisioning is deterministic and easy to review.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| JDK | 17+ | Compile and run Java functions locally |
| Maven | 3.6+ | Build and package Java artifacts |
| Azure Functions Core Tools | v4 | Start local host and publish artifacts |
| Azure CLI | 2.61+ | Provision Azure resources and inspect app state |

!!! info "Consumption plan basics"
    Consumption (Y1) is serverless with scale-to-zero, up to 200 instances, 1.5 GB memory per instance, and a default 5-minute timeout (max 10 minutes).

## What You'll Build

You will define a complete Consumption environment in Bicep (storage account, Y1 plan, and Linux Function App for Java 17), apply required host storage settings, and deploy from your own template.

```mermaid
flowchart TD
    A[Bicep template] --> B[az deployment group create]
    B --> C[Function App + Plan + Storage]
    C --> D["Build + publish from staging dir"]
```

## Steps

### Step 1 - Create a Bicep template for your Java Function App

```bicep
param location string = resourceGroup().location
param baseName string

var storageName = toLower(replace('${baseName}storage', '-', ''))
var planName = '${baseName}-plan'
var appName = '${baseName}-func'
var contentShareName = toLower(replace('${baseName}-content', '-', ''))
```

### Step 2 - Define Function App runtime settings

```bicep
resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  kind: 'linux'
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  properties: {
    reserved: true
  }
}

resource functionApp 'Microsoft.Web/sites@2023-12-01' = {
  name: appName
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'Java|17'
      appSettings: [
        { name: 'FUNCTIONS_EXTENSION_VERSION'; value: '~4' }
        { name: 'FUNCTIONS_WORKER_RUNTIME'; value: 'java' }
        { name: 'AzureWebJobsStorage'; value: 'DefaultEndpointsProtocol=https;AccountName=${storage.name};AccountKey=${listKeys(storage.id, storage.apiVersion).keys[0].value};EndpointSuffix=${environment().suffixes.storage}' }
        { name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'; value: 'DefaultEndpointsProtocol=https;AccountName=${storage.name};AccountKey=${listKeys(storage.id, storage.apiVersion).keys[0].value};EndpointSuffix=${environment().suffixes.storage}' }
        { name: 'WEBSITE_CONTENTSHARE'; value: contentShareName }
        { name: 'JAVA_OPTS'; value: '-Xmx512m' }
      ]
    }
  }
}
```

!!! note "Java-specific Bicep settings"
    - `linuxFxVersion: 'Java|17'` sets the Java runtime version.
    - `FUNCTIONS_WORKER_RUNTIME: 'java'` tells the host to use the Java worker.
    - `WEBSITE_CONTENTAZUREFILECONNECTIONSTRING` and `WEBSITE_CONTENTSHARE` are required for Consumption plan.

### Step 3 - Deploy infrastructure

```bash
az deployment group create \
  --resource-group "$RG" \
  --template-file main.bicep \
  --parameters baseName="$BASE_NAME"
```

### Step 4 - Deploy application artifact

After infrastructure is provisioned, build and publish from the Maven staging directory:

```bash
cd apps/java
mvn clean package
cd target/azure-functions/azure-functions-java-guide
func azure functionapp publish "$APP_NAME"
```

!!! danger "Must publish from Maven staging directory"
    Do NOT run `func azure functionapp publish` from the project root. The `function.json` files are generated in `target/azure-functions/<appName>/` by Maven. Publishing from the root uploads the package but functions will not be indexed.

### Step 5 - Validate infrastructure deployment

```bash
az deployment group show \
  --resource-group "$RG" \
  --name main \
  --query "properties.provisioningState" \
  --output tsv

az functionapp show \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --output table
```

## Verification

Infrastructure deployment output:

```text
ProvisioningState    Timestamp
-----------------    --------------------------
Succeeded            2026-04-09T16:00:00.000Z
```

Function app status:

```text
Name                    State    ResourceGroup            DefaultHostName
----------------------  -------  -----------------------  ------------------------------------------
func-jcon-04100022      Running  rg-func-java-con-demo    func-jcon-04100022.azurewebsites.net
```

## Next Steps

> **Next:** [06 - CI/CD](06-ci-cd.md)

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
