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
# 03 - Configuration (Dedicated)

Manage app settings, connection strings, and PowerShell module dependencies for your Dedicated (App Service Plan) app.

## App Settings

```bash
az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG \
  --settings "GreetingPrefix=Hello" "FUNCTIONS_WORKER_RUNTIME_VERSION=7.4"
```

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
- [Azure Functions Dedicated (App Service) plan (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan)
- [Run Functions locally with Core Tools (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
