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
      url: https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local
---
# 02 - First Deploy (Dedicated)

Provision a Dedicated (App Service Plan) function app and deploy the PowerShell project you built in step 01.

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

### Step 2b - Create the hosting plan

```bash
az appservice plan create \
  --name $PLAN_NAME \
  --resource-group $RG \
  --location $LOCATION \
  --sku B1 \
  --is-linux
```

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
- [Azure Functions Dedicated (App Service) plan (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan)
- [Run Functions locally with Core Tools (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
