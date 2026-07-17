---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/cli/azure/functionapp
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# CLI Cheatsheet

Quick reference for the most commonly used commands when developing, deploying, and managing Azure Functions PowerShell apps.

## Azure Functions Core Tools (`func`)

The `func` CLI is used for local development, testing, and deploying function apps.

### Local Development

```bash
# Initialize a new PowerShell function app project
func init MyFunctionApp --powershell

# Create a new function (interactive)
func new

# Create an HTTP-triggered function (non-interactive)
func new --name HttpExample --template "HTTP trigger" --authlevel anonymous

# Start the local Functions host
func host start

# Start on a custom port with verbose logging
func host start --port 7072 --verbose
```

### Deployment

```bash
# Deploy to Azure
func azure functionapp publish $APP_NAME

# Deploy to a staging slot
func azure functionapp publish $APP_NAME --slot staging

# Fetch app settings from Azure to local
func azure functionapp fetch-app-settings $APP_NAME
```

| CLI element | Explanation |
|---|---|
| Command(s) | `func init`, `func new`, `func host start`, `func azure functionapp publish` |
| Key flags | `--powershell`, `--name`, `--template`, `--authlevel`, `--port`, `--verbose`, `--slot` |
| Variables | `$APP_NAME` |
| Expected result | Core Tools scaffolds, runs, or publishes the app; verify the local host prints the function URLs or the publish output lists uploaded functions. |

## Azure CLI: Function App (`az functionapp`)

### Create a PowerShell Function App

```bash
# Flex Consumption (recommended, Linux, PowerShell 7.4)
az functionapp create \
  --name $APP_NAME \
  --resource-group $RG \
  --storage-account $STORAGE_NAME \
  --flexconsumption-location $LOCATION \
  --runtime powershell \
  --runtime-version 7.4 \
  --functions-version 4

# Consumption (legacy)
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

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp create` |
| Key flags | `--runtime powershell`, `--runtime-version`, `--functions-version`, `--flexconsumption-location`, `--consumption-plan-location`, `--os-type` |
| Variables | `$APP_NAME`, `$RG`, `$STORAGE_NAME`, `$LOCATION` |
| Expected result | Azure CLI returns provisioning details; confirm the app name and successful provisioning state before continuing. |

### App Settings

```bash
# Set app settings
az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG \
  --settings "FUNCTIONS_WORKER_RUNTIME=powershell" "FUNCTIONS_WORKER_RUNTIME_VERSION=7.4"

# List all app settings
az functionapp config appsettings list \
  --name $APP_NAME \
  --resource-group $RG
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp config appsettings set`, `az functionapp config appsettings list` |
| Key flags | `--name`, `--resource-group`, `--settings` |
| Variables | `$APP_NAME`, `$RG` |
| Expected result | Azure CLI applies the configuration change; confirm the returned JSON shows the expected value. |

### Logs

```bash
# Stream live logs
az functionapp log tail \
  --name $APP_NAME \
  --resource-group $RG
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp log tail` |
| Key flags | `--name`, `--resource-group` |
| Variables | `$APP_NAME`, `$RG` |
| Expected result | Azure CLI streams log output; verify function invocations appear as you exercise triggers. |

## PowerShell Module Management

```powershell
# Save a module into the app's Modules folder for bundled deployment
Save-Module -Name Az.Accounts -Path ./Modules

# Modern equivalent using the PSResourceGet cmdlet
Save-PSResource -Name Az.Accounts -Path ./Modules
```

| CLI element | Explanation |
|---|---|
| Command(s) | `Save-Module`, `Save-PSResource` |
| Key flags | `-Name`, `-Path` |
| Variables | None |
| Expected result | The module and its dependencies are written to `./Modules`; verify the folder contains the module version directories before publishing. |

## Quick Reference Table

| Task | Command |
|------|---------|
| Init project | `func init MyFunctionApp --powershell` |
| Start locally | `func host start` |
| Deploy to Azure | `func azure functionapp publish $APP_NAME` |
| Create Flex app | `az functionapp create --runtime powershell --runtime-version 7.4 ...` |
| Set app setting | `az functionapp config appsettings set --name $APP_NAME --resource-group $RG --settings "KEY=value"` |
| Stream logs | `az functionapp log tail --name $APP_NAME --resource-group $RG` |
| Bundle module | `Save-Module -Name Az.Accounts -Path ./Modules` |

## See Also

- [PowerShell Language Guide](index.md)
- [PowerShell Programming Model](powershell-programming-model.md)
- [host.json Reference](host-json.md)
- [Deployments](../../operations/deployment.md)

## Sources

- [Azure Functions Core Tools reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
- [az functionapp CLI reference (Microsoft Learn)](https://learn.microsoft.com/en-us/cli/azure/functionapp)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
