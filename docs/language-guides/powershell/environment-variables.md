---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# Environment Variables

Application settings are exposed to PowerShell functions as environment variables. Read them with `$env:SETTING_NAME`.

## Reading Settings in PowerShell

```powershell
# Access an app setting
$connectionString = $env:MyStorageConnection

# Provide a default when unset
$batchSize = if ($env:BatchSize) { [int]$env:BatchSize } else { 100 }
```

Set values locally in `local.settings.json` under `Values`, and in Azure via `az functionapp config appsettings set`.

## Runtime Settings

| Setting | Purpose |
|---|---|
| `FUNCTIONS_WORKER_RUNTIME` | Must be `powershell`. |
| `FUNCTIONS_WORKER_RUNTIME_VERSION` | PowerShell major.minor version (`7.4` or `7.6`). Pin explicitly. |
| `FUNCTIONS_EXTENSION_VERSION` | Functions host version (`~4`). |
| `AzureWebJobsStorage` | Storage account connection used by the runtime. |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Application Insights connection string for telemetry. |

## Concurrency Settings

| Setting | Purpose |
|---|---|
| `FUNCTIONS_WORKER_PROCESS_COUNT` | Number of language worker processes per instance. |
| `PSWorkerInProcConcurrencyUpperBound` | Number of runspaces per worker process. Defaults to 1,000 on the 4.x runtime. |

!!! warning "Concurrency and Azure PowerShell"
    Azure PowerShell holds process-level context. Enabling in-process concurrency with state-changing operations can cause race conditions. Set `PSWorkerInProcConcurrencyUpperBound` to `1` if you observe cross-invocation interference.

## Identity and Secrets

| Setting | Purpose |
|---|---|
| `MSI_SECRET` / `IDENTITY_HEADER` | Present when a managed identity is assigned; used by `Connect-AzAccount -Identity`. |
| `WEBSITE_LOAD_USER_PROFILE` | Loads the user profile on Windows plans (needed by some certificate operations). |

```powershell
# profile.ps1 — authenticate once per worker using managed identity
if ($env:MSI_SECRET) {
    Disable-AzContextAutosave -Scope Process | Out-Null
    Connect-AzAccount -Identity
}
```

!!! tip "Never hard-code secrets"
    Store secrets in Azure Key Vault and reference them with Key Vault references in app settings, or retrieve them at runtime using a managed identity. See [Managed Identity recipe](recipes/managed-identity.md).

## See Also

- [PowerShell Language Guide](index.md)
- [PowerShell Runtime](powershell-runtime.md)
- [host.json Reference](host-json.md)
- [Managed Identity recipe](recipes/managed-identity.md)

## Sources

- [App settings reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
