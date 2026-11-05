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

This recipe covers integrating Azure Service Bus with Azure Functions Python v2 — consuming queue and topic/subscription messages with the trigger, handling sessions and dead-lettering, and publishing messages with the output binding. Service Bus is the standard choice for enterprise messaging that needs ordering, sessions, transactions, or duplicate detection.

## Architecture

<!-- diagram-id: architecture -->
```mermaid
flowchart TD
    accTitle: Service Bus processing and dead-letter outcome
    accDescr: Producers send to Service Bus; a queue or topic subscription supplies the trigger for function processing and application output. Service Bus moves messages to the entity's dead-letter queue when the delivery limit is exceeded, not through the output binding.
    PROD[Producers] --> SBQ[("Service Bus<br/>Queue/Topic")]
    SBQ --> TRIG[Service Bus Trigger]
    TRIG --> FA[Function App]
    SBQ --> DLQ[(Dead-Letter Queue)]
    FA --> OUT[Service Bus Output]
```

**Reading key:** Arrows show logical message-processing stages, not network
connection initiators. For topics, the trigger receives from a subscription;
its DLQ belongs to that subscription. The DLQ arrow shows the broker's
[maximum-delivery-count outcome](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-dead-letter-queues#maximum-delivery-count),
not an application send or a dead-letter action on every exception.

## Prerequisites

Service Bus bindings are included in the default extension bundle. Provide the connection in app settings. A connection-string setting or an identity-based connection is supported. Identity-based connections use a setting prefix with `__fullyQualifiedNamespace`:

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

For the Python v2 `func.ServiceBusMessage` trigger shown here, with automatic
completion enabled, the runtime completes a message on successful execution and
abandons it on an exception. Abandonment or lock expiry permits redelivery;
Service Bus moves the message to the queue's or subscription's DLQ when its
delivery count exceeds `maxDeliveryCount`.

```python
import azure.functions as func
import logging
import json

bp = func.Blueprint()

@bp.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="orders",
    connection="ServiceBusConnection",
)
def process_order(msg: func.ServiceBusMessage) -> None:
    """Process a single Service Bus queue message."""
    body = msg.get_body().decode("utf-8")
    data = json.loads(body)

    logging.info("Message ID: %s, delivery count: %s",
                 msg.message_id, msg.delivery_count)
    logging.info("Payload: %s", data)
    # Raising an exception abandons the message; after maxDeliveryCount
    # it is moved to the dead-letter queue automatically.
```

## Topic/Subscription Trigger

```python
@bp.service_bus_topic_trigger(
    arg_name="msg",
    topic_name="events",
    subscription_name="billing",
    connection="ServiceBusConnection",
)
def process_event(msg: func.ServiceBusMessage) -> None:
    """Process a message from a topic subscription."""
    logging.info("Subscription message: %s", msg.get_body().decode("utf-8"))
```

## Output Binding: Publish Messages

```python
@bp.route(route="enqueue", methods=["POST"])
@bp.service_bus_queue_output(
    arg_name="out_msg",
    queue_name="orders",
    connection="ServiceBusConnection",
)
def enqueue(req: func.HttpRequest, out_msg: func.Out[str]) -> func.HttpResponse:
    """Publish a message to a Service Bus queue."""
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON body"}),
            mimetype="application/json",
            status_code=400,
        )

    out_msg.set(json.dumps(body))
    return func.HttpResponse(
        json.dumps({"status": "enqueued"}),
        mimetype="application/json",
        status_code=202,
    )
```

## Host Configuration

Tune concurrency and prefetch in `host.json`:

```json
{
  "version": "2.0",
  "extensions": {
    "serviceBus": {
      "maxConcurrentCalls": 16,
      "prefetchCount": 0,
      "maxAutoLockRenewalDuration": "00:05:00",
      "sessionHandlerOptions": {
        "maxConcurrentSessions": 8
      }
    }
  }
}
```

| Setting | Description |
|---------|-------------|
| `maxConcurrentCalls` | Maximum concurrent message handlers per instance (non-session) |
| `prefetchCount` | Number of messages the client prefetches to reduce latency |
| `maxAutoLockRenewalDuration` | How long the runtime keeps renewing the message lock during processing |
| `maxConcurrentSessions` | Maximum concurrent sessions processed per instance |

!!! note "Sessions and ordering"
    Enable `isSessionsEnabled=True` on the trigger to process session-enabled queues/subscriptions, which guarantees ordered, single-consumer processing per session ID.

## See Also

- [Queue Storage](queue.md)
- [Event Hubs](event-hub.md)

## Sources

- [Azure Service Bus bindings for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus)
- [Azure Service Bus trigger for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus-trigger)
- [Azure Service Bus output binding for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus-output)
- [Service Bus dead-letter queues (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-dead-letter-queues)
