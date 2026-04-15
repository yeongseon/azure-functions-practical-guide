---
content_sources:
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-bindings-cosmosdb-v2
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-reference#configure-an-identity-based-connection
---

# Cosmos DB Integration

This recipe shows Java bindings for Azure Cosmos DB trigger, input, and output patterns, plus identity-based configuration for production.

## Architecture

<!-- diagram-id: architecture -->
```mermaid
flowchart TD
    API[HTTP Trigger] --> OUT[@CosmosDBOutput]
    OUT --> COSMOS[(Cosmos DB Container)]
    COSMOS --> TRIGGER[@CosmosDBTrigger]
    API --> IN[@CosmosDBInput]
    MI[Managed Identity] -.-> COSMOS
```

## Prerequisites

Add Cosmos DB Java binding library and Functions plugin in `pom.xml`:

```xml
<dependencies>
    <dependency>
        <groupId>com.microsoft.azure.functions</groupId>
        <artifactId>azure-functions-java-library</artifactId>
        <version>3.1.0</version>
    </dependency>
</dependencies>

<build>
    <plugins>
        <plugin>
            <groupId>com.microsoft.azure</groupId>
            <artifactId>azure-functions-maven-plugin</artifactId>
            <version>1.36.0</version>
        </plugin>
    </plugins>
</build>
```

Provision account, database, and container:

```bash
az cosmosdb create --name $COSMOS_ACCOUNT --resource-group $RG --kind GlobalDocumentDB

az cosmosdb sql database create \
  --account-name $COSMOS_ACCOUNT \
  --resource-group $RG \
  --name appdb

az cosmosdb sql container create \
  --account-name $COSMOS_ACCOUNT \
  --resource-group $RG \
  --database-name appdb \
  --name items \
  --partition-key-path "/category"
```

Connection string setting:

```bash
az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG \
  --settings "CosmosDBConnection=<cosmos-connection-string>"
```

Managed identity alternative:

```bash
az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG \
  --settings "CosmosDBConnection__accountEndpoint=https://$COSMOS_ACCOUNT.documents.azure.com:443/"
```

## Java implementation

```java
package com.contoso.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;

import java.util.*;

public class CosmosFunctions {

    @FunctionName("createItem")
    @CosmosDBOutput(
        name = "outputDocument",
        databaseName = "appdb",
        containerName = "items",
        connection = "CosmosDBConnection"
    )
    public String createItem(
        @HttpTrigger(
            name = "request",
            methods = {HttpMethod.POST},
            authLevel = AuthorizationLevel.FUNCTION,
            route = "items"
        ) HttpRequestMessage<Optional<String>> request
    ) {
        return request.getBody().orElse("{\"id\":\"missing\",\"category\":\"general\"}");
    }

    @FunctionName("getItem")
    public HttpResponseMessage getItem(
        @HttpTrigger(
            name = "request",
            methods = {HttpMethod.GET},
            authLevel = AuthorizationLevel.FUNCTION,
            route = "items/{category}/{id}"
        ) HttpRequestMessage<Optional<String>> request,
        @BindingName("id") String id,
        @BindingName("category") String category,
        @CosmosDBInput(
            name = "document",
            databaseName = "appdb",
            containerName = "items",
            id = "{id}",
            partitionKey = "{category}",
            connection = "CosmosDBConnection"
        ) String document
    ) {
        if (document == null) {
            return request.createResponseBuilder(HttpStatus.NOT_FOUND).body("Item not found").build();
        }
        return request.createResponseBuilder(HttpStatus.OK).body(document).build();
    }

    @FunctionName("onItemChanged")
    public void onItemChanged(
        @CosmosDBTrigger(
            name = "documents",
            databaseName = "appdb",
            containerName = "items",
            connection = "CosmosDBConnection",
            leaseContainerName = "leases",
            createLeaseContainerIfNotExists = true
        ) String documents,
        final ExecutionContext context
    ) {
        context.getLogger().info("Cosmos DB change feed batch: " + documents);
    }
}
```

## Implementation notes

- Use `@CosmosDBOutput` for simple write paths from HTTP or queue events.
- Use `@CosmosDBInput` for key-based reads where route values map to partition key and id.
- Use `@CosmosDBTrigger` for change feed processing and keep the handler idempotent.
- For production, prefer managed identity configuration over raw connection strings.

## See Also

- [Managed Identity](managed-identity.md)
- [Queue Storage Integration](queue.md)
- [Blob Storage Integration](blob-storage.md)

## Sources

- [Azure Functions Cosmos DB bindings (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-bindings-cosmosdb-v2)
- [Identity-based connections in Azure Functions (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference#configure-an-identity-based-connection)
