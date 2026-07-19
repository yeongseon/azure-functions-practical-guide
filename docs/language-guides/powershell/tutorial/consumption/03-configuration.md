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
# 03 - Configuration (Consumption)

Manage app settings, connection strings, and PowerShell module dependencies for your Consumption (Y1) app.

## App Settings

```bash
az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG \
  --settings "GreetingPrefix=Hello" "FUNCTIONS_WORKER_RUNTIME_VERSION=7.4"
```
| Command/Parameter | Purpose |
| --- | --- |
| `az functionapp config appsettings set` | Add or update application settings on the function app. |
| `--name` | Name of the function app. |
| `--resource-group` | Resource group that contains the function app. |
| `--settings` | Key=value application settings to apply. |

Read settings in PowerShell with `$env:GreetingPrefix`.

## Module Dependencies

Use managed dependencies. Declare modules in `requirements.psd1` and enable `managedDependency` in `host.json`:

```powershell
@{
    'Az.Accounts' = '2.*'
}
```

The runtime downloads them from the PowerShell Gallery on startup.

## Verification

```bash
az functionapp config appsettings list \
  --name $APP_NAME \
  --resource-group $RG \
  --output table
```
| Command/Parameter | Purpose |
| --- | --- |
| `az functionapp config appsettings list` | List the application settings on the function app. |
| `--name` | Name of the function app. |
| `--resource-group` | Resource group that contains the function app. |
| `--output` | Output format (`table`). |

Confirm `GreetingPrefix` appears with the expected value.

## Next Steps

With configuration in place, wire up observability.

> **Next:** [04 - Logging & Monitoring](04-logging-monitoring.md)


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
