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
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-premium-plan
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local
---
# 02 - First Deploy (Premium)

Provision a Premium (EP1) function app and deploy the PowerShell project you built in step 01.

## Prerequisites

- Completed [01 - Run Locally](01-local-run.md)
- Signed in with `az login`

## Steps

### Step 1 - Set variables

```bash
RG=rg-functions-demo
APP_NAME=func-ps-demo
STORAGE_NAME=stpsdemo$RANDOM
LOCATION=koreacentral
PLAN_NAME=plan-ps-demo
```

### Step 2 - Create the resource group and storage

```bash
az group create --name $RG --location $LOCATION

az storage account create \
  --name $STORAGE_NAME \
  --resource-group $RG \
  --location $LOCATION \
  --sku Standard_LRS
```
| Command/Parameter | Purpose |
| --- | --- |
| `az group create` | Create the resource group that holds the tutorial resources. |
| `--name` | Name of the resource group. |
| `--location` | Azure region for the resource group. |
| `az storage account create` | Create the storage account the function app requires. |
| `--name` | Name of the storage account. |
| `--resource-group` | Resource group that contains the storage account. |
| `--location` | Azure region for the storage account. |
| `--sku` | Storage replication SKU (`Standard_LRS` = locally redundant). |

### Step 2b - Create the hosting plan

```bash
az functionapp plan create \
  --name $PLAN_NAME \
  --resource-group $RG \
  --location $LOCATION \
  --sku EP1 \
  --is-linux
```
| Command/Parameter | Purpose |
| --- | --- |
| `az functionapp plan create` | Create the Premium (Elastic Premium) plan that hosts the function app. |
| `--name` | Name of the Premium plan. |
| `--resource-group` | Resource group that contains the plan. |
| `--location` | Azure region for the plan. |
| `--sku` | Elastic Premium pricing tier (`EP1`). |
| `--is-linux` | Create the plan on Linux. |

### Step 3 - Create the function app

```bash
az functionapp create \
  --name $APP_NAME \
  --resource-group $RG \
  --storage-account $STORAGE_NAME \
  --plan $PLAN_NAME \
  --runtime powershell \
  --runtime-version 7.4 \
  --functions-version 4
```
| Command/Parameter | Purpose |
| --- | --- |
| `az functionapp create` | Create the function app on the pre-created plan. |
| `--name` | Name of the function app. |
| `--resource-group` | Resource group that contains the function app. |
| `--storage-account` | Storage account backing the function app. |
| `--plan` | Existing plan that hosts the function app. |
| `--runtime` | Language runtime stack (`powershell`). |
| `--runtime-version` | PowerShell runtime version. |
| `--functions-version` | Azure Functions runtime major version. |

### Step 4 - Deploy the code

```bash
func azure functionapp publish $APP_NAME
```

## Verification

```bash
curl "https://$APP_NAME.azurewebsites.net/api/HttpExample?name=Azure"
```

Returns `Hello, Azure.`

## Next Steps

Your app is live. Next, manage its configuration and secrets.

> **Next:** [03 - Configuration](03-configuration.md)


## See Also

- [Tutorial Overview & Plan Chooser](../index.md)
- [PowerShell Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources

- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
- [Azure Functions Premium plan (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-premium-plan)
- [Run Functions locally with Core Tools (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
