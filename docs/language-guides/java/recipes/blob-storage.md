# Blob Storage Integration

This recipe covers Java blob processing using trigger, input, and output bindings for ingestion and transformed output patterns.

## Architecture

```mermaid
flowchart LR
    BLOBIN[(incoming container)] --> TRIGGER[@BlobTrigger]
    TRIGGER --> TRANSFORM[Transform content]
    TRANSFORM --> BLOBOUT[@BlobOutput processed container]
    API[HTTP Trigger] --> BLOBREAD[@BlobInput]
```

## Prerequisites

Create a storage account and containers:

```bash
az storage account create \
  --name $STORAGE_NAME \
  --resource-group $RG \
  --location $LOCATION \
  --sku Standard_LRS

az storage container create --name incoming --account-name $STORAGE_NAME --auth-mode login
az storage container create --name processed --account-name $STORAGE_NAME --auth-mode login
```

Configure storage connection:

```bash
az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG \
  --settings "AzureWebJobsStorage=<storage-connection-string>"
```

## Java implementation

```java
package com.contoso.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;

import java.nio.charset.StandardCharsets;
import java.util.Optional;

public class BlobFunctions {

    @FunctionName("processBlob")
    @BlobOutput(
        name = "outputBlob",
        path = "processed/{name}",
        connection = "AzureWebJobsStorage"
    )
    public byte[] processBlob(
        @BlobTrigger(
            name = "inputBlob",
            path = "incoming/{name}",
            connection = "AzureWebJobsStorage"
        ) byte[] content,
        @BindingName("name") String name,
        final ExecutionContext context
    ) {
        String transformed = "processed:" + name + ":" + new String(content, StandardCharsets.UTF_8).toUpperCase();
        context.getLogger().info("Blob processed: " + name);
        return transformed.getBytes(StandardCharsets.UTF_8);
    }

    @FunctionName("readBlobByApi")
    public HttpResponseMessage readBlobByApi(
        @HttpTrigger(
            name = "request",
            methods = {HttpMethod.GET},
            authLevel = AuthorizationLevel.FUNCTION,
            route = "blobs/{name}"
        ) HttpRequestMessage<Optional<String>> request,
        @BlobInput(
            name = "blobContent",
            path = "processed/{name}",
            connection = "AzureWebJobsStorage"
        ) String blobContent
    ) {
        if (blobContent == null) {
            return request.createResponseBuilder(HttpStatus.NOT_FOUND).body("Blob not found").build();
        }
        return request.createResponseBuilder(HttpStatus.OK).body(blobContent).build();
    }
}
```

## Implementation notes

- Keep blob trigger handlers idempotent because retries can happen.
- Use `byte[]` for binary-safe processing and convert text explicitly with UTF-8.
- Prefer separate containers for raw and processed data.
- For cross-service workflows, emit queue messages after blob processing.

## See Also

- [Queue Storage Integration](queue.md)
- [Managed Identity](managed-identity.md)
- [HTTP API Patterns](http-api.md)

## Sources

- [Azure Blob storage bindings for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-bindings-storage-blob)
- [Azure Functions Java developer guide (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-java)
