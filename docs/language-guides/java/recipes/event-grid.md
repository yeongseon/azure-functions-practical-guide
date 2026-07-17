---
content_sources:

  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-grid-trigger
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/cli/azure/eventgrid/event-subscription?view=azure-cli-latest
  diagrams:
    - id: architecture
      type: flowchart
      source: self-generated
      justification: Flow view of architecture, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-grid-trigger
        - https://learn.microsoft.com/en-us/cli/azure/eventgrid/event-subscription?view=azure-cli-latest
---
# Event Grid Trigger

This recipe uses native Event Grid bindings in Java with `@EventGridTrigger` to process cloud events without HTTP trigger shims.

## Architecture

<!-- diagram-id: architecture -->
```mermaid
flowchart TD
    SOURCE[Storage account events] --> TOPIC["Event Grid topic/system topic"]
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

| CLI element | Explanation |
|---|---|
| Command(s) | `az storage account show`, `az eventgrid event-subscription create` |
| Key flags | `--name`, `--resource-group`, `--query`, `--output`, `--source-resource-id`, `--endpoint-type`, `--endpoint` |
| Variables | `$STORAGE_NAME`, `$RG`, `$STORAGE_ID`, `$SUBSCRIPTION_ID`, `$APP_NAME` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


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

## Event Grid Output: Publish to a Custom Topic

Use the `@EventGridOutput` annotation to publish events to a custom topic. The annotation reads the topic endpoint and access key from app settings, so never hard-code the topic URI in the annotation properties. You can output a JSON string or a POJO.

```java
public class PublishFunction {
    @FunctionName("publishEvent")
    public void run(
            @TimerTrigger(name = "timer", schedule = "0 */5 * * * *") String timerInfo,
            @EventGridOutput(
                name = "outputEvent",
                topicEndpointUri = "MyEventGridTopicUriSetting",
                topicKeySetting = "MyEventGridTopicKeySetting")
                OutputBinding<EventGridEvent> outputEvent,
            final ExecutionContext context) {
        EventGridEvent event = new EventGridEvent();
        event.setId("1807");
        event.setEventType("Contoso.Order.Created");
        event.setSubject("orders/created");
        event.setEventTime("2026-01-01T00:00:00+00:00");
        event.setDataVersion("1.0");
        event.setData("{ orderId: 12345 }");
        outputEvent.setValue(event);
    }
}
```

Here `EventGridEvent` is a plain POJO with `id`, `eventType`, `subject`, `eventTime`, `dataVersion`, and `data` fields and their getters/setters.

Configure the two app settings the annotation references:

```bash
az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG \
  --settings "MyEventGridTopicUriSetting=$TOPIC_ENDPOINT" "MyEventGridTopicKeySetting=$TOPIC_KEY"
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp config appsettings set` |
| Key flags | `--name`, `--resource-group`, `--settings` |
| Variables | `$APP_NAME`, `$RG`, `$TOPIC_ENDPOINT`, `$TOPIC_KEY` |
| Expected result | Azure CLI returns the updated app settings as JSON; confirm both settings are present before continuing. |

!!! note "CloudEvents schema"
    The output binding emits the Event Grid schema. To publish in the **CloudEvents 1.0** schema, create the custom topic with `--input-schema cloudeventschemav1.0` and produce the payload in CloudEvents shape (`specversion`, `type`, `source`, `id`, `data`).

## See Also

- [Queue Storage Integration](queue.md)
- [Blob Storage Integration](blob-storage.md)
- [Durable Orchestration](durable-orchestration.md)

## Sources

- [Event Grid trigger for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-grid-trigger)
- [Event Grid output binding for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-grid-output)
- [Create event subscriptions with Azure CLI (Microsoft Learn)](https://learn.microsoft.com/en-us/cli/azure/eventgrid/event-subscription?view=azure-cli-latest)
