---
content_sources:
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-reference-node
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-diagnostics
---

# Troubleshooting

This runbook-style reference captures common Node.js v4 issues with practical checks and resolutions.

## Topic/Command Groups

<!-- diagram-id: topic-command-groups -->
```mermaid
flowchart TD
    A[Issue] --> B[Evidence]
    B --> C[Diagnosis]
    C --> D[Fix]
```

### Functions not discovered

- Confirm `FUNCTIONS_WORKER_RUNTIME=node`.
- Check startup logs for module resolution errors.

```bash
az functionapp log tail --name $APP_NAME --resource-group $RG
```

### Runtime version mismatch

- Validate runtime and Node settings.
- For Linux apps, validate `siteConfig.linuxFxVersion` in addition to app settings.

```bash
az functionapp config appsettings list --name $APP_NAME --resource-group $RG --query "[?name=='WEBSITE_NODE_DEFAULT_VERSION' || name=='FUNCTIONS_EXTENSION_VERSION']"
az functionapp config show --name $APP_NAME --resource-group $RG --query "linuxFxVersion"
```

### Out-of-memory under load

- Set `languageWorkers__node__arguments=--max-old-space-size=4096`.
- Reduce dependency footprint and stream large payloads.

### Trigger binding failures

- Check `AzureWebJobsStorage` and related connection settings.
- Validate queue or blob names and identity permissions.

## See Also
- [Environment Variables](environment-variables.md)
- [host.json Reference](host-json.md)
- [Operations: Monitoring](../../operations/monitoring.md)

## Sources
- [Azure Functions Node.js developer guide (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-node)
- [Azure Functions diagnostics (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-diagnostics)
