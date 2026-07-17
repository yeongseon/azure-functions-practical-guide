---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-host-json
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# host.json Reference

`host.json` configures runtime behavior for all functions in a PowerShell function app. This page highlights the settings most relevant to PowerShell workers.

## Minimal PowerShell host.json

```json
{
  "version": "2.0",
  "managedDependency": {
    "enabled": true
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  },
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "excludedTypes": "Request"
      }
    }
  }
}
```

## PowerShell-Specific Settings

### managedDependency

Controls whether modules listed in `requirements.psd1` are automatically downloaded from the PowerShell Gallery.

```json
{
  "managedDependency": {
    "enabled": true
  }
}
```

!!! warning "Not supported on Flex Consumption"
    Managed dependencies are unavailable on the Flex Consumption plan. Set `enabled` to `false` and bundle modules in a `Modules` folder instead. See [PowerShell Runtime](powershell-runtime.md#dependency-management).

### Concurrency

PowerShell throughput is controlled by app settings rather than `host.json`, but the host-level `functionTimeout` and HTTP concurrency settings still apply:

| Setting | Location | Effect |
|---|---|---|
| `functionTimeout` | `host.json` | Maximum execution duration per invocation. |
| `PSWorkerInProcConcurrencyUpperBound` | App setting | Number of runspaces per worker process. |
| `FUNCTIONS_WORKER_PROCESS_COUNT` | App setting | Number of worker processes per instance. |

See [Environment Variables](environment-variables.md) for the app settings.

## Common Sections

### functionTimeout

```json
{
  "functionTimeout": "00:10:00"
}
```

Default and maximum values depend on the hosting plan. See [Platform Limits](platform-limits.md).

### extensionBundle

Extension bundles supply trigger and binding extensions without manual package installation. PowerShell apps use the classic `function.json` binding model and rely on the bundle for all non-HTTP bindings.

```json
{
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
```

### logging

```json
{
  "logging": {
    "logLevel": {
      "default": "Information",
      "Host.Aggregator": "Warning"
    },
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20,
        "excludedTypes": "Request"
      }
    }
  }
}
```

## See Also

- [PowerShell Language Guide](index.md)
- [PowerShell Runtime](powershell-runtime.md)
- [Environment Variables](environment-variables.md)
- [Platform Limits](platform-limits.md)

## Sources

- [host.json reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-host-json)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
