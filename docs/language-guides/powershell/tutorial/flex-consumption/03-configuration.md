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
      url: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local
---
# 03 - Configuration (Flex Consumption)

Manage app settings, connection strings, and PowerShell module dependencies for your Flex Consumption (FC1) app.

## App Settings

```bash
az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG \
  --settings "GreetingPrefix=Hello" "FUNCTIONS_WORKER_RUNTIME_VERSION=7.4"
```

Read settings in PowerShell with `$env:GreetingPrefix`.

## Module Dependencies

Managed dependencies are **not** supported on Flex Consumption. Bundle modules into a `Modules` folder before publishing:

```bash
pwsh -c "Save-Module -Name Az.Accounts -Path ./Modules"
```

The `Modules` folder is added to `$env:PSModulePath` for autoloading.

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
- [Flex Consumption plan (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan)
- [Run Functions locally with Core Tools (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
