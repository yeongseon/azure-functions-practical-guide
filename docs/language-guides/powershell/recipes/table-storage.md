---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-table
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# Table Storage

Persist and query structured NoSQL data with Azure Table storage bindings in PowerShell.

## Input Binding

Read entities filtered by partition key:

`function.json`:

```json
{
  "bindings": [
    {
      "name": "Request",
      "type": "httpTrigger",
      "direction": "in",
      "methods": ["get"]
    },
    {
      "name": "Response",
      "type": "http",
      "direction": "out"
    },
    {
      "name": "Orders",
      "type": "table",
      "direction": "in",
      "tableName": "Orders",
      "partitionKey": "{Query.customerId}",
      "connection": "AzureWebJobsStorage"
    }
  ]
}
```

`run.ps1`:

```powershell
param($Request, $Orders, $TriggerMetadata)

Write-Information "Retrieved $($Orders.Count) order(s)"
Push-OutputBinding -Name Response -Value ([HttpResponseContext]@{
    StatusCode = [System.Net.HttpStatusCode]::OK
    Body       = ($Orders | ConvertTo-Json)
})
```

## Output Binding

Write one or more entities. Each must include `PartitionKey` and `RowKey`:

```json
{
  "name": "OutputOrder",
  "type": "table",
  "direction": "out",
  "tableName": "Orders",
  "connection": "AzureWebJobsStorage"
}
```

```powershell
Push-OutputBinding -Name OutputOrder -Value @{
    PartitionKey = "customer-42"
    RowKey       = [guid]::NewGuid().ToString()
    Total        = 99.5
    Status       = "created"
}
```

!!! tip "Choosing keys"
    Pick a `PartitionKey` that distributes writes evenly and groups the entities you query together. A monotonic `RowKey` (such as a reverse-timestamp) keeps recent items first.

## See Also

- [Cosmos DB](cosmosdb.md)
- [Blob Storage](blob-storage.md)
- [Recipes Index](index.md)

## Sources

- [Table storage bindings (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-table)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
