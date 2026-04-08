# Blob Storage Patterns

This recipe covers Blob trigger processing plus blob input/output bindings in Node.js v4 for ingestion and transformed output flows.

## Architecture

```mermaid
flowchart LR
    UPLOAD[Blob Upload to incoming container] --> TRIGGER[storageBlob Trigger]
    TRIGGER --> TRANSFORM[Parse and Transform Content]
    TRANSFORM --> OUTPUT[Blob Output Binding to processed container]
    API[HTTP Trigger] --> INPUT[Blob Input Binding]
    INPUT --> APIRESP[Return Blob Metadata]
```

## Prerequisites

Set up extension bundle:

```json
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
```

Create storage and required containers:

```bash
az storage account create \
  --name $STORAGE_NAME \
  --resource-group $RG \
  --location $LOCATION \
  --sku Standard_LRS

az storage container create \
  --name incoming \
  --account-name $STORAGE_NAME

az storage container create \
  --name processed \
  --account-name $STORAGE_NAME
```

## Working Node.js v4 Code

```javascript
const { app, input, output } = require("@azure/functions");

const sourceBlobInput = input.storageBlob({
  path: "incoming/{name}",
  connection: "AzureWebJobsStorage"
});

const processedBlobOutput = output.storageBlob({
  path: "processed/{name}.json",
  connection: "AzureWebJobsStorage"
});

app.storageBlob("ingestBlob", {
  path: "incoming/{name}",
  connection: "AzureWebJobsStorage",
  extraOutputs: [processedBlobOutput],
  handler: async (blob, context) => {
    const fileName = context.triggerMetadata.name;
    const text = blob.toString("utf8");

    const transformed = {
      fileName,
      receivedUtc: new Date().toISOString(),
      size: blob.length,
      lineCount: text.split(/\r?\n/).length
    };

    context.extraOutputs.set(processedBlobOutput, Buffer.from(JSON.stringify(transformed)));
    context.log("Processed blob", { fileName, bytes: blob.length });
  }
});

app.http("getIncomingBlobMetadata", {
  methods: ["GET"],
  route: "blobs/{name}",
  extraInputs: [sourceBlobInput],
  handler: async (_request, context) => {
    const blob = context.extraInputs.get(sourceBlobInput);
    if (!blob) {
      return { status: 404, jsonBody: { error: "Blob not found." } };
    }

    return {
      status: 200,
      jsonBody: {
        bytes: blob.length,
        preview: blob.toString("utf8").slice(0, 120)
      }
    };
  }
});
```

## Implementation Notes

- `app.storageBlob()` is the event-driven path for new blob arrivals and is preferred over polling patterns.
- Use blob output binding for deterministic write targets (`processed/{name}.json`) without manual SDK upload code.
- Use blob input binding in HTTP functions when you need quick metadata/content lookup by path.
- Store large payload handling and retry behavior in `host.json` when throughput increases.

## See Also
- [Node.js Recipes Index](index.md)
- [Queue Processing](queue.md)
- [Node.js v4 Programming Model](../v4-programming-model.md)

## Sources
- [Azure Blob Storage bindings for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-bindings-storage-blob)
- [Azure Functions Node.js developer guide (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-node)
