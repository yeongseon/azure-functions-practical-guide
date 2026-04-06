# Java Annotation Programming Model

This deep dive explains how Java functions are declared, discovered, and executed in Azure Functions using annotation metadata instead of external `function.json` files.

## Main Content

```mermaid
flowchart LR
    A[Java class and method] --> B[@FunctionName]
    B --> C[Trigger and binding annotations]
    C --> D[Functions host metadata index]
    D --> E[Invocation and execution]
```

### Core function signature

```java
@FunctionName("OrdersHttp")
public HttpResponseMessage run(
    @HttpTrigger(
        name = "req",
        methods = {HttpMethod.GET, HttpMethod.POST},
        authLevel = AuthorizationLevel.FUNCTION,
        route = "orders/{id}")
    HttpRequestMessage<Optional<String>> request,
    @BindingName("id") String orderId,
    final ExecutionContext context) {

    context.getLogger().info("handling order id=" + orderId);

    return request.createResponseBuilder(HttpStatus.OK)
        .body("order=" + orderId)
        .build();
}
```

### Trigger and binding patterns

| Scenario | Annotation pattern | Input/Output type |
|----------|--------------------|-------------------|
| HTTP API | `@HttpTrigger` | `HttpRequestMessage<Optional<String>>` and `HttpResponseMessage` |
| Queue consumer | `@QueueTrigger` | `String` or POJO |
| Queue publisher | `@QueueOutput` | Return type mapped to queue message |
| Blob ingestion | `@BlobTrigger` | `String`, `byte[]`, or stream |
| Blob write | `@BlobOutput` | Return value mapped to blob body |
| Scheduled job | `@TimerTrigger` | Timer payload string |

### Multiple bindings in one method

```java
@FunctionName("QueueToBlob")
@BlobOutput(name = "outputBlob", path = "archive/{rand-guid}.txt", connection = "AzureWebJobsStorage")
public String queueToBlob(
    @QueueTrigger(name = "message", queueName = "incoming", connection = "AzureWebJobsStorage") String message,
    final ExecutionContext context) {

    context.getLogger().info("queue payload length=" + message.length());
    return "archived:" + message;
}
```

### Request parsing and response building

- For body parsing, use `request.getBody().orElse("")` and validate early.
- Build responses with `request.createResponseBuilder(HttpStatus.OK).body(payload).build()`.
- Use `@BindingName("param")` for route tokens, for example `route = "users/{userId}"`.

### Operational guidance

1. Keep one public function class per domain area (orders, billing, notifications).
2. Minimize cold start overhead by avoiding expensive static initialization.
3. Keep function methods thin and push business logic to reusable services.
4. Emit structured logs through `ExecutionContext` for consistent queries.

## See Also

- [Java Runtime](java-runtime.md)
- [Tutorial Overview & Plan Chooser](tutorial/index.md)
- [Recipes Index](recipes/index.md)
- [Platform: Hosting](../../platform/hosting.md)

## Sources

- [Azure Functions Java developer guide (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-java)
- [Azure Functions triggers and bindings (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-triggers-bindings)
