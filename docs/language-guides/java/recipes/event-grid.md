# Event Grid Trigger

This recipe uses native Event Grid bindings in Java with `@EventGridTrigger` to process cloud events without HTTP trigger shims.

## Architecture

```mermaid
flowchart LR
    SOURCE[Storage account events] --> TOPIC[Event Grid topic/system topic]
    TOPIC --> SUB[Event subscription]
    SUB --> FUNC[@EventGridTrigger handler]
    FUNC --> ACTION[Business action]
```

## Prerequisites

Create subscription from a Storage account to a Function endpoint:

```bash
STORAGE_ID=$(az storage account show --name $STORAGE_NAME --resource-group $RG --query id --output tsv)

az eventgrid event-subscription create \
  --name storage-to-function \
  --source-resource-id $STORAGE_ID \
  --endpoint-type azurefunction \
  --endpoint "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.Web/sites/$APP_NAME/functions/handleEventGrid"
```

## Java implementation

```java
package com.contoso.functions;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.microsoft.azure.functions.ExecutionContext;
import com.microsoft.azure.functions.annotation.EventGridTrigger;
import com.microsoft.azure.functions.annotation.FunctionName;

public class EventGridFunctions {
    private static final ObjectMapper MAPPER = new ObjectMapper();

    @FunctionName("handleEventGrid")
    public void handleEventGrid(
        @EventGridTrigger(name = "event") String event,
        final ExecutionContext context
    ) throws Exception {
        JsonNode eventJson = MAPPER.readTree(event);
        String eventType = eventJson.path("eventType").asText();
        String subject = eventJson.path("subject").asText();
        String dataVersion = eventJson.path("dataVersion").asText();

        context.getLogger().info(
            "Event Grid event received: eventType=" + eventType +
            ", subject=" + subject +
            ", dataVersion=" + dataVersion
        );
    }
}
```

## Implementation notes

- Use `@EventGridTrigger`, not `@HttpTrigger`, for Event Grid function handlers.
- Handle both `Microsoft.EventGrid.SubscriptionValidationEvent` and business events.
- Keep handlers idempotent because duplicate event delivery can occur.
- Route by `eventType` and `subject` to isolate processing paths.

## See Also

- [Queue Storage Integration](queue.md)
- [Blob Storage Integration](blob-storage.md)
- [Durable Orchestration](durable-orchestration.md)

## Sources

- [Event Grid trigger for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-bindings-event-grid-trigger)
- [Create event subscriptions with Azure CLI (Microsoft Learn)](https://learn.microsoft.com/azure/event-grid/create-view-manage-event-subscriptions-cli)
