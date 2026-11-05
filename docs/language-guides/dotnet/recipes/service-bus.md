---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus
  diagrams:
    - id: service-bus
      type: flowchart
      source: self-generated
      justification: Flow view of service-bus, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus-trigger
        - https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-dead-letter-queues
---
# Service Bus

Consume Service Bus queue and topic messages with the trigger and publish messages with the output binding in the .NET isolated worker model.

<!-- diagram-id: service-bus -->
```mermaid
flowchart TD
    accTitle: Service Bus input and outcome relationships for the .NET isolated recipe
    accDescr: Producers publish to a queue or topic; the trigger processes queue or topic-subscription messages. The two downstream paths summarize possible dead-letter and output-binding outcomes, not unconditional actions or direct network hops.
    A[Producers] --> B[(Service Bus Queue/Topic)]
    B --> C[ServiceBusTrigger Function]
    C --> D[(Dead-Letter Queue)]
    C --> E[ServiceBusOutput]
```

**Reading key:** The dead-letter path represents a possible outcome for the source queue or subscription, not a separate queue written by every invocation. The output path represents a configured `ServiceBusOutput` binding; it is not an automatic consequence of receiving a message.

## Topic/Command Groups

### Queue trigger

For this single-message, non-session .NET isolated example with Service Bus extension 5.x and automatic completion enabled, successful execution completes the message; failed processing abandons it. Under PeekLock, abandon or lock expiry increments the delivery count; Service Bus moves the message to the queue's or subscription's dead-letter subqueue when the count exceeds that entity's maximum delivery count. Manual settlement requires separate configuration; session-enabled entities require `IsSessionsEnabled = true`.

```csharp
[Function("ProcessOrder")]
public void ProcessOrder(
    [ServiceBusTrigger("orders", Connection = "ServiceBusConnection")] string message,
    FunctionContext context)
{
    var logger = context.GetLogger("ProcessOrder");
    logger.LogInformation("Processing message: {Message}", message);
}
```

### Topic/subscription trigger

```csharp
[Function("ProcessEvent")]
public void ProcessEvent(
    [ServiceBusTrigger("events", "billing", Connection = "ServiceBusConnection")] string message,
    FunctionContext context)
{
    context.GetLogger("ProcessEvent").LogInformation("Subscription message: {Message}", message);
}
```

### Output binding

```csharp
[Function("Enqueue")]
[ServiceBusOutput("orders", Connection = "ServiceBusConnection")]
public string Enqueue(
    [HttpTrigger(AuthorizationLevel.Function, "post", Route = "servicebus/enqueue")]
    HttpRequestData request)
{
    return new StreamReader(request.Body).ReadToEnd();
}
```

### Identity-based connection

```bash
az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG \
  --settings "ServiceBusConnection__fullyQualifiedNamespace=$NAMESPACE.servicebus.windows.net"
```
| Command/Parameter | Purpose |
| --- | --- |
| `az functionapp config appsettings set` | Add or update application settings on the function app. |
| `--name` | Name of the target resource. |
| `--resource-group` | Resource group that contains the resource. |
| `--settings` | Key=value application settings to apply. |

Grant the managed identity the **Azure Service Bus Data Receiver** (and **Data Sender** for output) role.

### Host settings

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

## Review Matrix

| Review area | Page-specific check |
|---|---|
| Scope | Confirm the guidance applies to Service Bus trigger and output bindings. |
| Source basis | Validate the recommendation against the Microsoft Learn sources in this page. |
| Evidence | Capture command output, portal state, metrics, logs, or screenshots before treating the result as proven. |

## See Also
- [Recipes Index](index.md)
- [.NET Language Guide](../index.md)
- [Troubleshooting](../troubleshooting.md)

## Sources
- [Azure Service Bus bindings for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus)
- [Azure Service Bus trigger for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus-trigger)
- [Azure Service Bus output binding for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-service-bus-output)
- [Service Bus dead-letter queues (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-dead-letter-queues)
