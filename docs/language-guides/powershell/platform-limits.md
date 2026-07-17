---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/language-support-policy
---
# Platform Limits

Key limits and version constraints that affect PowerShell function apps. For the authoritative, always-current numbers, consult the Microsoft Learn sources below.

## PowerShell Version Support

| Functions runtime | PowerShell version | .NET version | Availability |
|---|---|---|---|
| 4.x | PowerShell 7.4 | .NET 8 | GA — all plans (Consumption, Flex Consumption, Premium, Dedicated) |
| 4.x | PowerShell 7.6 (preview) | .NET 10 | Windows-only (Premium, Dedicated, Consumption) |

- Pin an explicit major.minor version. The legacy `~7` value maps to `7.0.x` and is not auto-upgraded.
- Flex Consumption supports PowerShell 7.4 on Linux only.

## Timeout Limits

| Plan | Default | Maximum |
|---|---|---|
| Consumption | 5 min | 10 min |
| Flex Consumption | 30 min | Unbounded (subject to platform constraints) |
| Premium | 30 min | Unbounded |
| Dedicated | 30 min | Unbounded |

Configure with `functionTimeout` in [host.json](host-json.md).

## Scaling Limits

| Plan | Max instances (approx.) | Notes |
|---|---|---|
| Consumption | 200 | Event-driven; scales to zero. |
| Flex Consumption | 1,000 | Per-function scaling; always-ready instances configurable. |
| Premium | 20–100 | Pre-warmed instances eliminate cold start. |
| Dedicated | Bound to App Service Plan | Manual or autoscale rules. |

## Concurrency

- PowerShell processes one invocation per runspace at a time.
- `PSWorkerInProcConcurrencyUpperBound` controls runspaces per process (default 1,000 on 4.x).
- `FUNCTIONS_WORKER_PROCESS_COUNT` controls worker processes per instance.
- Azure PowerShell state is process-scoped; validate concurrency-safety before raising these values.

## Dependency Management

| Plan | Managed dependencies (`requirements.psd1`) | Bundled `Modules` folder |
|---|---|---|
| Consumption | Supported | Supported |
| Premium / Dedicated | Supported | Supported |
| Flex Consumption | **Not supported** | Supported (required) |

## See Also

- [PowerShell Language Guide](index.md)
- [PowerShell Runtime](powershell-runtime.md)
- [host.json Reference](host-json.md)
- [Platform Limits (Reference)](../../reference/platform-limits.md)

## Sources

- [Azure Functions scale and hosting (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
- [Language support policy (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/language-support-policy)
