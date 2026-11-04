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
# Service Bus Integration

This recipe demonstrates Java Service Bus queue and topic triggers with output bindings, dead-letter behavior, and host tuning.

## Architecture

<!-- diagram-id: architecture -->
```mermaid
flowchart TD
    accTitle: Java Service Bus input and possible processing outcomes
    accDescr: Producers publish to a queue or topic; functions consume queue or topic-subscription messages. The QueueTrigger label identifies the queue example; the topic example uses ServiceBusTopicTrigger. Function App to dead-letter and output paths summarize possible outcomes, not unconditional writes or a network-call sequence.
    PROD[Producers] --> SBQ[(Service Bus Queue/Topic)]
    SBQ --> TRIG[ServiceBusQueueTrigger worker]
    TRIG --> FA[Function App]
    FA --> DLQ[(Dead-Letter Queue)]
    FA --> OUT[ServiceBusQueueOutput]
```

**Reading key:** The Java single-message trigger examples use automatic settlement: successful processing completes the message and failed processing abandons it. Under PeekLock, abandon or lock expiry increments delivery count; exceeding the source queue's or subscription's maximum delivery count moves the message to that entity's dead-letter subqueue. The output path represents a configured `@ServiceBusQueueOutput`, not an automatic consequence of receiving a message. The examples below do not configure session processing; session support must be checked against the installed extension and Java annotation version.

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

## Java Implementation

```java
package com.contoso.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;

public class ServiceBusFunctions {

    @FunctionName("processOrder")
    public void processOrder(
        @ServiceBusQueueTrigger(
            name = "message",
            queueName = "orders",
            connection = "ServiceBusConnection"
        ) String message,
        final ExecutionContext context
    ) {
        context.getLogger().info("Processing Service Bus message: " + message);
        // Throwing abandons the message; after maxDeliveryCount it is
        // moved to the dead-letter queue automatically.
    }

    @FunctionName("processEvent")
    public void processEvent(
        @ServiceBusTopicTrigger(
            name = "message",
            topicName = "events",
            subscriptionName = "billing",
            connection = "ServiceBusConnection"
        ) String message,
        final ExecutionContext context
    ) {
        context.getLogger().info("Subscription message: " + message);
    }

    @FunctionName("enqueue")
    @ServiceBusQueueOutput(name = "output", queueName = "orders", connection = "ServiceBusConnection")
    public String enqueue(
        @HttpTrigger(
            name = "request",
            methods = {HttpMethod.POST},
            authLevel = AuthorizationLevel.FUNCTION,
            route = "servicebus/enqueue"
        ) HttpRequestMessage<String> request
    ) {
        return request.getBody();
    }
}
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
    Set `isSessionsEnabled = true` on the trigger to process session-enabled queues/subscriptions, which guarantees ordered, single-consumer processing per session ID.

## See Also

- [Queue Storage Integration](queue.md)
- [Event Hubs Integration](event-hub.md)

## Sources

- [Azure Service Bus bindings for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus)
- [Azure Service Bus trigger for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus-trigger)
- [Azure Service Bus output binding for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus-output)
- [Service Bus dead-letter queues (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-dead-letter-queues)
