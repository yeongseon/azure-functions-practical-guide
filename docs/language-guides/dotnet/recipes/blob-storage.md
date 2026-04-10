---
content_sources:
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/dotnet-isolated-process-guide
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-triggers-bindings
---

# Blob Storage

Implement blob trigger and blob output scenarios for ingestion and transformation pipelines.

<!-- diagram-id: blob-storage -->
```mermaid
flowchart LR
    A[Trigger] --> B[Function]
    B --> C[Binding or SDK]
    C --> D[Azure service]
```

## Topic/Command Groups

### Blob trigger pattern
```csharp
[Function("BlobIngest")]
public void BlobIngest(
    [BlobTrigger("incoming/{name}", Connection = "AzureWebJobsStorage")] byte[] content,
    string name)
{
}
```

### Blob output binding
```csharp
[Function("BlobTransform")]
[BlobOutput("processed/{name}", Connection = "AzureWebJobsStorage")]
public byte[] BlobTransform(
    [BlobTrigger("incoming/{name}", Connection = "AzureWebJobsStorage")] byte[] input,
    string name)
{
    return input;
}
```

## See Also
- [Recipes Index](index.md)
- [.NET Language Guide](../index.md)
- [Troubleshooting](../troubleshooting.md)

## Sources
- [Azure Functions .NET isolated worker guide](https://learn.microsoft.com/azure/azure-functions/dotnet-isolated-process-guide)
- [Azure Functions triggers and bindings](https://learn.microsoft.com/azure/azure-functions/functions-triggers-bindings)
