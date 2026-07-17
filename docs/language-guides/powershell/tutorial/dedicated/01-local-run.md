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
# 01 - Run Locally (Dedicated)

Scaffold and run a PowerShell Azure Functions app locally before deploying to the Dedicated (App Service Plan) plan.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| PowerShell | 7.4+ | Local runtime matching the worker |
| Azure Functions Core Tools | v4 | Start the local host and publish |
| Azure CLI | 2.61+ | Provision and configure Azure resources |
| Azurite (optional) | latest | Local Storage emulator for triggers |

!!! info "Dedicated (App Service Plan) basics"
    Dedicated (App Service Plan) is fixed-capacity App Service hosting with predictable pricing. PowerShell runs on version 7.4 on this plan.

## What You'll Build

You will scaffold a PowerShell function app with an anonymous HTTP trigger, run it on the local Functions host, and verify the endpoint responds.

## Steps

### Step 1 - Scaffold the project

```bash
func init MyPsApp --powershell
cd MyPsApp
func new --name HttpExample --template "HTTP trigger" --authlevel anonymous
```

### Step 2 - Configure local settings

`local.settings.json`:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "powershell",
    "FUNCTIONS_WORKER_RUNTIME_VERSION": "7.4"
  }
}
```

### Step 3 - Review the function

`HttpExample/run.ps1`:

```powershell
param($Request, $TriggerMetadata)

$name = $Request.Query.Name
if (-not $name) { $name = $Request.Body.Name }

$body = if ($name) { "Hello, $name." } else { "Pass a name in the query string or body." }

Push-OutputBinding -Name Response -Value ([HttpResponseContext]@{
    StatusCode = [System.Net.HttpStatusCode]::OK
    Body       = $body
})
```

### Step 4 - Start the host

```bash
func host start
```

### Step 5 - Call the endpoint

```bash
curl "http://localhost:7071/api/HttpExample?name=Azure"
```

## Verification

```text
Functions:
    HttpExample: [GET,POST] http://localhost:7071/api/HttpExample
```

The curl call returns `Hello, Azure.`

## Next Steps

You now have local parity and can deploy to Dedicated (App Service Plan).

> **Next:** [02 - First Deploy](02-first-deploy.md)


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
