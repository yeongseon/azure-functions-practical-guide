---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb-v2
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# Azure Cosmos DB

React to document changes and read/write items with Azure Cosmos DB bindings in PowerShell.

## Change Feed Trigger

`function.json`:

```json
{
  "bindings": [
    {
      "name": "Documents",
      "type": "cosmosDBTrigger",
      "direction": "in",
      "databaseName": "catalog",
      "containerName": "products",
      "connection": "CosmosDbConnection",
      "leaseContainerName": "leases",
      "createLeaseContainerIfNotExists": true
    }
  ]
}
```

`run.ps1`:

```powershell
param($Documents, $TriggerMetadata)

Write-Information "Change feed delivered $($Documents.Count) document(s)"
foreach ($doc in $Documents) {
    Write-Information "Changed document id: $($doc.id)"
}
```

The trigger uses a lease container to track its position in the change feed. Keep the lease container in the same account as the monitored container.

## Input Binding

Read a single item by id and partition key:

```json
{
  "name": "Product",
  "type": "cosmosDB",
  "direction": "in",
  "databaseName": "catalog",
  "containerName": "products",
  "connection": "CosmosDbConnection",
  "id": "{Query.id}",
  "partitionKey": "{Query.category}"
}
```

## Output Binding

```json
{
  "name": "OutputDocument",
  "type": "cosmosDB",
  "direction": "out",
  "databaseName": "catalog",
  "containerName": "products",
  "connection": "CosmosDbConnection"
}
```

```powershell
Push-OutputBinding -Name OutputDocument -Value @{ id = [guid]::NewGuid().ToString(); category = "books"; name = "Sample" }
```

!!! tip "Identity-based connections"
    Configure `CosmosDbConnection__accountEndpoint` with a managed identity instead of an account key. See [Managed Identity](managed-identity.md).

## See Also

- [Table Storage](table-storage.md)
- [Managed Identity](managed-identity.md)
- [Recipes Index](index.md)

## Sources

- [Azure Cosmos DB bindings (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb-v2)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
