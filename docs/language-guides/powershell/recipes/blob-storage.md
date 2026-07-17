---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# Blob Storage

Process files with blob triggers and read/write blobs using bindings in PowerShell.

## Blob Trigger

`function.json`:

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

`run.ps1`:

```powershell
param($InputBlob, $TriggerMetadata)

$name = $TriggerMetadata.name
Write-Information "Processing blob '$name' ($($InputBlob.Length) bytes)"
```

The blob binding delivers content as a `byte[]` by default. For text, convert:

```powershell
$text = [System.Text.Encoding]::UTF8.GetString($InputBlob)
```

## Output Blob Binding

Add an output binding to write a derived file:

```json
{
  "name": "OutputBlob",
  "type": "blob",
  "direction": "out",
  "path": "processed/{name}",
  "connection": "AzureWebJobsStorage"
}
```

```powershell
Push-OutputBinding -Name OutputBlob -Value $processedContent
```

## Using the Az.Storage Module

For dynamic paths or listing operations, use the module with a managed identity:

```powershell
Connect-AzAccount -Identity
$ctx = New-AzStorageContext -StorageAccountName $env:StorageAccountName -UseConnectedAccount
Get-AzStorageBlob -Container "uploads" -Context $ctx
```

!!! warning "Blob trigger scaling"
    Blob triggers on Consumption can lag under high volume. For latency-sensitive processing, prefer an Event Grid-based blob trigger or a queue.

## See Also

- [Queue Storage](queue.md)
- [Managed Identity](managed-identity.md)
- [Recipes Index](index.md)

## Sources

- [Blob storage bindings (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
