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
# 07 - Extending with Triggers (Dedicated)

Add Timer, Queue, and Blob triggers to your Dedicated (App Service Plan) PowerShell app. PowerShell uses the classic `function.json` binding model.

## Timer Trigger

`TimerExample/function.json`:

```json
{
  "bindings": [
    {
      "name": "Timer",
      "type": "timerTrigger",
      "direction": "in",
      "schedule": "0 */5 * * * *"
    }
  ]
}
```

`TimerExample/run.ps1`:

```powershell
param($Timer)
Write-Information "Timer fired at $(Get-Date -Format o)"
```

## Queue Trigger

`QueueExample/function.json`:

```json
{
  "bindings": [
    {
      "name": "QueueItem",
      "type": "queueTrigger",
      "direction": "in",
      "queueName": "work-items",
      "connection": "AzureWebJobsStorage"
    }
  ]
}
```

```powershell
param($QueueItem, $TriggerMetadata)
Write-Information "Dequeued: $QueueItem"
```

## Blob Trigger

`BlobExample/function.json`:

```json
{
  "bindings": [
    {
      "name": "InputBlob",
      "type": "blobTrigger",
      "direction": "in",
      "path": "uploads/{name}",
      "connection": "AzureWebJobsStorage"
    }
  ]
}
```

```powershell
param($InputBlob, $TriggerMetadata)
Write-Information "Blob $($TriggerMetadata.name) is $($InputBlob.Length) bytes"
```

## Verification

Deploy, then drop a message on the `work-items` queue or upload a blob to `uploads/`. Confirm the invocation appears in `az functionapp log tail`.

## Next Steps

Explore the [Recipes Index](../../recipes/index.md) for reusable binding patterns.

> **Next:** [Recipes Index](../../recipes/index.md) — reusable PowerShell trigger and binding patterns.


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
