# Reference

Quick lookup documentation for Azure Functions platform operations and diagnostics.

## Documents

| Document | Description |
|----------|-------------|
| [CLI Cheatsheet](cli-cheatsheet.md) | Common `az functionapp`, `func`, and Azure CLI commands |
| [host.json Reference](host-json.md) | Host configuration options for the Functions runtime |
| [Environment Variables](environment-variables.md) | System and application environment variables |
| [Platform Limits](platform-limits.md) | Timeouts, payload sizes, concurrency limits per hosting plan |
| [Troubleshooting](troubleshooting.md) | Common issues and debugging for Python function apps |

## Quick Links

| URL | Purpose |
|-----|---------|
| `https://$APP_NAME.azurewebsites.net` | Function App endpoint |
| `https://$APP_NAME.scm.azurewebsites.net` | Kudu/SCM endpoint (not available on Flex Consumption) |

## Common Variables

| Variable | Description |
|----------|-------------|
| `$RG` | Resource group name |
| `$APP_NAME` | Function app name |
| `$PLAN_NAME` | Hosting plan name |
| `$STORAGE_NAME` | Storage account name |
| `$LOCATION` | Azure region |

## Language-Specific Details

Reference documents currently cover Python-specific content. As additional language guides are added, language-agnostic content will be promoted to this section.

- [Python Language Guide](../language-guides/python/index.md)

## References

- [Azure Functions Documentation (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/)
- [Azure Functions host.json Reference (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-host-json)
- [Azure Functions CLI Reference (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-core-tools-reference)
- [Azure Functions Scale and Hosting (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-scale)
