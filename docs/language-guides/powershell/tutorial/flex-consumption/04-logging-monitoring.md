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
# 04 - Logging & Monitoring (Flex Consumption)

Configure Application Insights and structured logging for your Flex Consumption (FC1) PowerShell app.

## Enable Application Insights

```bash
az monitor app-insights component create \
  --app func-ps-demo-ai \
  --location $LOCATION \
  --resource-group $RG

az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG \
  --settings "APPLICATIONINSIGHTS_CONNECTION_STRING=<connection-string>"
```
| Command/Parameter | Purpose |
| --- | --- |
| `az monitor app-insights component create` | Create the Application Insights component for telemetry. |
| `--app` | Name of the Application Insights component. |
| `--location` | Azure region for the component. |
| `--resource-group` | Resource group that contains the component. |
| `az functionapp config appsettings set` | Point the function app at Application Insights. |
| `--name` | Name of the function app. |
| `--resource-group` | Resource group that contains the function app. |
| `--settings` | Set the Application Insights connection string setting. |

## Logging in PowerShell

Use the standard streams — they flow to Application Insights automatically:

```powershell
param($Request, $TriggerMetadata)

Write-Information "Processing request for $($Request.Query.Name)"
Write-Warning "Name was empty; using default"
Write-Error "Downstream call failed"
```

| Cmdlet | Severity |
|--------|----------|
| `Write-Information` / `Write-Host` | Information |
| `Write-Warning` | Warning |
| `Write-Error` | Error |

## Stream Live Logs

```bash
az functionapp log tail --name $APP_NAME --resource-group $RG
```
| Command/Parameter | Purpose |
| --- | --- |
| `az functionapp log tail` | Stream live log output from the function app. |
| `--name` | Name of the function app. |
| `--resource-group` | Resource group that contains the function app. |

## Verification

Invoke the function, then query Application Insights:

```kusto
traces
| where timestamp > ago(15m)
| order by timestamp desc
```

You should see your `Write-Information` messages.

## Next Steps

Codify the whole environment as Infrastructure as Code.

> **Next:** [05 - Infrastructure as Code](05-infrastructure-as-code.md)


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
