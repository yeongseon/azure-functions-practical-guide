---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-recover-storage-account
---
# Troubleshooting PowerShell Functions

Symptom-based guidance for common PowerShell-specific problems. For platform-wide diagnosis, see the [Troubleshooting hub](../../troubleshooting/index.md).

## Module Not Found at Runtime

**Symptom**: `The term '<cmdlet>' is not recognized` or `Could not load module`.

**Checks**:

- On Flex Consumption, confirm the module is bundled in the `Modules` folder — managed dependencies are not supported there.
- Confirm `managedDependency.enabled` is `true` in [host.json](host-json.md) when using `requirements.psd1`.
- Verify outbound access to `https://www.powershellgallery.com` for managed dependencies.
- Check the module version directory exists under `Modules/<Name>/<Version>/`.

```powershell
# Verify a module is discoverable inside a function
Get-Module -ListAvailable -Name Az.Accounts
```

## Slow Cold Start

**Symptom**: First invocation after idle takes many seconds.

**Checks**:

- Large module sets (e.g., the full `Az` module) inflate load time. Import only the sub-modules you need (`Az.Accounts`, `Az.Storage`).
- Move one-time setup into `profile.ps1` rather than repeating it per invocation.
- Consider Premium plan pre-warmed instances or Flex Consumption always-ready instances for latency-sensitive workloads.

```powershell
# requirements.psd1 — pin narrow modules instead of the full Az
@{
    'Az.Accounts' = '2.*'
    'Az.Storage'  = '5.*'
}
```

## Output Binding Not Written

**Symptom**: HTTP response is empty or a queue/blob output is missing.

**Checks**:

- Ensure you call `Push-OutputBinding -Name <bindingName> -Value <value>` with a `Name` that matches the binding `name` in `function.json`.
- For HTTP, the output binding name is typically `Response` and expects an `HttpResponseContext`.

```powershell
Push-OutputBinding -Name Response -Value ([HttpResponseContext]@{
    StatusCode = [System.Net.HttpStatusCode]::OK
    Body       = "ok"
})
```

## Concurrency Race Conditions

**Symptom**: Intermittent wrong results, cross-request data bleed, or Azure context errors under load.

**Checks**:

- Azure PowerShell context is process-scoped. Set `PSWorkerInProcConcurrencyUpperBound` to `1` to isolate invocations.
- Use `FUNCTIONS_WORKER_PROCESS_COUNT` for parallelism instead of in-process runspaces when using stateful modules.
- Call `Disable-AzContextAutosave -Scope Process` in `profile.ps1`.

## Managed Identity Authentication Fails

**Symptom**: `Connect-AzAccount -Identity` throws or returns no context.

**Checks**:

- Confirm a system- or user-assigned identity is assigned to the function app.
- Verify `MSI_SECRET`/`IDENTITY_HEADER` are present (they are injected only when an identity exists).
- Ensure the identity has the required RBAC role on the target resource.

See the [Managed Identity recipe](recipes/managed-identity.md).

## See Also

- [PowerShell Language Guide](index.md)
- [PowerShell Runtime](powershell-runtime.md)
- [Troubleshooting hub](../../troubleshooting/index.md)

## Sources

- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
- [Recover a deleted storage account (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-recover-storage-account)
