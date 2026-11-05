---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus
  diagrams:
    - id: architecture
      type: flowchart
      source: self-generated
      justification: Flow view of architecture, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus-trigger
        - https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-dead-letter-queues
---
# Service Bus

This recipe covers integrating Azure Service Bus with Azure Functions Node.js v4 — consuming queue and topic/subscription messages, handling dead-lettering, and publishing messages with the output binding.

## Architecture

<!-- diagram-id: architecture -->
```mermaid
flowchart TD
    accTitle: Node.js Service Bus input and possible outcome relationships
    accDescr: Producers publish to a queue or topic; the Node.js v4 app.serviceBusQueue or app.serviceBusTopic registration processes queue or topic-subscription messages. Dead-lettering and a configured output binding are possible outcomes, not unconditional actions or direct network hops from the function app.
    PROD[Producers] --> SBQ[(Service Bus Queue/Topic)]
    SBQ --> TRIG[Service Bus Trigger]
    TRIG --> FA[Function App]
    FA --> DLQ[(Dead-Letter Queue)]
    FA --> OUT[Service Bus Output]
```

**Reading key:** The dead-letter path refers to the source queue's or subscription's dead-letter subqueue, not a separate queue written by every invocation. The output path represents a configured `output.serviceBusQueue` binding, not an automatic consequence of receiving a message.

## Prerequisites

Provide the connection in app settings. A connection-string setting or an identity-based connection is supported. Identity-based connections use a setting prefix with `__fullyQualifiedNamespace`:

```bash
az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG \
  --settings "ServiceBusConnection__fullyQualifiedNamespace=$NAMESPACE.servicebus.windows.net"
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp config appsettings set` |
| Key flags | `--name`, `--resource-group`, `--settings` |
| Variables | `$APP_NAME`, `$RG`, `$NAMESPACE` |
| Expected result | Azure CLI returns the updated app settings as JSON; confirm the setting is present before continuing. |

When using an identity-based connection, grant the function app's managed identity the **Azure Service Bus Data Receiver** (and **Data Sender** for output) role on the namespace.

## Queue Trigger

For this single-message, non-session Node.js v4 example using ordinary bindings with automatic completion, successful execution completes the message and failed processing abandons it. Under PeekLock, abandon or lock expiry increments the delivery count; exceeding the source queue's or subscription's `maxDeliveryCount` moves the message to that entity's dead-letter subqueue. This is not the SDK-type/manual-settlement mode.

```javascript
const { app, output } = require("@azure/functions");

const ordersOutput = output.serviceBusQueue({
  queueName: "orders",
  connection: "ServiceBusConnection"
});

app.serviceBusQueue("processOrder", {
  queueName: "orders",
  connection: "ServiceBusConnection",
  handler: (message, context) => {
    context.log("Message ID:", context.triggerMetadata.messageId);
    context.log("Delivery count:", context.triggerMetadata.deliveryCount);
    context.log("Payload:", message);
    // Throwing here abandons the message; after maxDeliveryCount it is
    // moved to the dead-letter subqueue automatically.
  }
});
```

## Topic/Subscription Trigger

```javascript
app.serviceBusTopic("processEvent", {
  topicName: "events",
  subscriptionName: "billing",
  connection: "ServiceBusConnection",
  handler: (message, context) => {
    context.log("Subscription message:", message);
  }
});
```

## Output Binding: Publish Messages

```javascript
app.http("enqueue", {
  methods: ["POST"],
  authLevel: "function",
  extraOutputs: [ordersOutput],
  handler: async (request, context) => {
    const body = await request.json();
    context.extraOutputs.set(ordersOutput, body);
    return { status: 202, jsonBody: { status: "enqueued" } };
  }
});
```

## Host Configuration

```json
{
  "version": "2.0",
  "extensions": {
    "serviceBus": {
      "maxConcurrentCalls": 16,
      "prefetchCount": 0,
      "maxAutoLockRenewalDuration": "00:05:00"
    }
  }
}
```

| Setting | Description |
|---------|-------------|
| `maxConcurrentCalls` | Maximum concurrent message handlers per instance |
| `prefetchCount` | Number of messages the client prefetches to reduce latency |
| `maxAutoLockRenewalDuration` | How long the runtime keeps renewing the message lock during processing |

!!! note "Sessions and ordering"
    Enable `isSessionsEnabled: true` on the trigger to process session-enabled queues/subscriptions, which guarantees ordered, single-consumer processing per session ID.

## See Also

- [Queue](queue.md)
- [Event Hubs](event-hub.md)

## Sources

- [Azure Service Bus bindings for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus)
- [Azure Service Bus trigger for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus-trigger)
- [Azure Service Bus output binding for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus-output)
- [Service Bus dead-letter queues (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-dead-letter-queues)
