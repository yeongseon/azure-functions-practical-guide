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
# 04 - Logging & Monitoring (Premium)

Configure Application Insights and structured logging for your Premium (EP1) PowerShell app.

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
- [Azure Functions Premium plan (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-premium-plan)
- [Run Functions locally with Core Tools (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
