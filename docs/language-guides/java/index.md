# Java Language Guide

This guide introduces Azure Functions for Java using the annotation-based programming model.

Java functions are declared with `@FunctionName` and trigger/binding annotations such as `@HttpTrigger`, providing explicit metadata in familiar Java class structure.

## Official reference

- [Azure Functions Java developer guide (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-java)

!!! note "Authoritative runtime guidance"
    Validate Java runtime and feature availability with Microsoft Learn before production rollout decisions.

## Java model at a glance

| Topic | Java on Azure Functions |
|-------|--------------------------|
| Registration style | Annotation-based function method declarations |
| Core annotations | `@FunctionName`, `@HttpTrigger`, output/input binding annotations |
| Worker model | Out-of-process Java worker managed by the Functions host |
| Supported runtimes | Java 8, 11, 17, 21 |

## Key concepts

- Function entry methods are grouped in Java classes.
- Trigger and binding behavior is declared via annotations.
- Execution context and logging are provided to handler methods.
- Dependency management follows Maven/Gradle Java ecosystem conventions.

## Java vs Python mental model

| Concern | Python v2 | Java |
|---------|-----------|------|
| Function declaration | Decorators on Python functions | Java annotations on methods |
| App container | `func.FunctionApp()` object | Class-based methods with annotation metadata |
| Dependency management | `requirements.txt` | `pom.xml` or `build.gradle` |
| Common HTTP pattern | `@app.route(...)` | `@FunctionName` + `@HttpTrigger` |

## Quick start: HTTP trigger (Java)

```java
package com.example;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;
import java.util.Optional;

public class HelloFunction {
    @FunctionName("HelloHttp")
    public HttpResponseMessage run(
        @HttpTrigger(
            name = "req",
            methods = {HttpMethod.GET},
            authLevel = AuthorizationLevel.FUNCTION,
            route = "hello/{name?}")
        HttpRequestMessage<Optional<String>> request,
        @BindingName("name") String name,
        final ExecutionContext context) {

        String resolvedName = (name != null && !name.isBlank()) ? name : "world";
        context.getLogger().info("Processed Java request for " + resolvedName);

        return request
            .createResponseBuilder(HttpStatus.OK)
            .body("Hello, " + resolvedName + "! (Azure Functions Java)")
            .build();
    }
}
```

### What this example demonstrates

- Function naming with `@FunctionName`.
- HTTP trigger declaration with `@HttpTrigger`.
- Route parameter extraction with `@BindingName`.
- Logging through `ExecutionContext`.

## Planned content (Coming Soon)

- **Tutorial track**: local run, deployment, configuration, monitoring, IaC, CI/CD.
- **Recipes**: Storage, Cosmos DB, Event Grid, Key Vault, Managed Identity.
- **Reference docs**: runtime/version matrix notes, host settings mapping, troubleshooting patterns.
- **Reference app**: `apps/java/` parity build-out matching hub capability targets.

!!! tip "Use shared hub guidance now"
    While Java-specific sections expand, rely on [Platform](../../platform/index.md), [Operations](../../operations/index.md), and [Troubleshooting](../../troubleshooting/index.md) for architecture and runbook decisions.

## Cross-language links

- [Language Guides overview](../index.md)
- [Python guide](../python/index.md)
- [Node.js guide](../nodejs/index.md)
- [.NET guide](../dotnet/index.md)

## See Also

- [Platform: Triggers and Bindings](../../platform/triggers-and-bindings.md)
- [Platform: Hosting](../../platform/hosting.md)
- [Operations: Deployment](../../operations/deployment.md)
- [Troubleshooting: Methodology](../../troubleshooting/methodology.md)
