---
validation:
  az_cli:
    last_tested:
    cli_version:
    core_tools_version:
    result: not_tested
  bicep:
    last_tested:
    result: not_tested
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/consumption-plan
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local
---
# 05 - Infrastructure as Code (Consumption)

Define your Consumption (Y1) PowerShell app in Bicep for reproducible deployments.

## Bicep Template

```bicep
param appName string
param location string = resourceGroup().location
param storageName string

resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
}

resource app 'Microsoft.Web/sites@2023-12-01' = {
  name: appName
  location: location
  kind: 'functionapp'
  properties: {
    siteConfig: {
      appSettings: [
        { name: 'FUNCTIONS_EXTENSION_VERSION', value: '~4' }
        { name: 'FUNCTIONS_WORKER_RUNTIME', value: 'powershell' }
        { name: 'FUNCTIONS_WORKER_RUNTIME_VERSION', value: '7.4' }
      ]
    }
  }
}
```

## Deploy

```bash
az deployment group create \
  --resource-group $RG \
  --template-file infra/main.bicep \
  --parameters appName=$APP_NAME storageName=$STORAGE_NAME
```
| Command/Parameter | Purpose |
| --- | --- |
| `az deployment group create` | Deploy the Bicep template to the resource group. |
| `--resource-group` | Target resource group for the deployment. |
| `--template-file` | Path to the Bicep template. |
| `--parameters` | Template parameter values. |

## Verification

```bash
az deployment group show --resource-group $RG --name main --query properties.provisioningState
```
| Command/Parameter | Purpose |
| --- | --- |
| `az deployment group show` | Show the status of a completed deployment. |
| `--resource-group` | Resource group that contains the deployment. |
| `--name` | Name of the deployment. |
| `--query` | JMESPath query selecting the provisioning state. |

Returns `Succeeded`.

## Next Steps

Automate the build and deploy with CI/CD.

> **Next:** [06 - CI/CD](06-ci-cd.md)


## See Also

- [Tutorial Overview & Plan Chooser](../index.md)
- [PowerShell Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources

- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
- [Azure Functions Consumption plan (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/consumption-plan)
- [Run Functions locally with Core Tools (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)

!!! warning "Legacy hosting path"
    Consumption plan (Y1) content is provided for existing workloads. For most new serverless applications, prefer [Flex Consumption](../flex-consumption/01-local-run.md).
