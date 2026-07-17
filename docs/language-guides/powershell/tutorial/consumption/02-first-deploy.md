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
# 02 - First Deploy (Consumption)

Provision a Consumption (Y1) function app and deploy the PowerShell project you built in step 01.

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


### Step 3 - Create the function app

```bash
az functionapp create \
  --name $APP_NAME \
  --resource-group $RG \
  --storage-account $STORAGE_NAME \
  --consumption-plan-location $LOCATION \
  --runtime powershell \
  --runtime-version 7.4 \
  --functions-version 4 \
  --os-type Windows
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
- [Azure Functions Consumption plan (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/consumption-plan)
- [Run Functions locally with Core Tools (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)

!!! warning "Legacy hosting path"
    Consumption plan (Y1) content is provided for existing workloads. For most new serverless applications, prefer [Flex Consumption](../flex-consumption/01-local-run.md).
