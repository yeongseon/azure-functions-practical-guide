---
validation:
  az_cli:
    last_tested:
    result: not_tested
  bicep:
    last_tested:
    result: not_tested
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-develop-local
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-java
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local
---
# 08 - Testing and Local Debugging (Flex Consumption)

Unit-test your Java function methods with JUnit 5, mock `HttpRequestMessage` and `ExecutionContext` with Mockito, run integration tests against Azurite, and attach a remote debugger to the running host.

## Prerequisites

| Tool | Minimum version | Purpose |
|---|---|---|
| Java | 17 | Run function code and tests |
| Maven | 3.9 | Build and test runner |
| Azure Functions Core Tools | 4.x | Local host and debugging |
| JUnit 5 + Mockito | Latest | Test frameworks |
| Azurite | 3.x | Local Azure Storage emulator |

## What You'll Build

You will add JUnit 5 tests to the Flex Consumption app that unit-test an HTTP function, mock the request and execution context, run an Azurite integration test, and attach IntelliJ or VS Code to a debug-enabled host.

## 1. Unit Test the Function Method

Keep logic in a plain method so it is testable without Azure types.

```java
// src/main/java/com/example/Greeter.java
public final class Greeter {
    public static String build(String name) {
        String value = (name == null || name.isBlank()) ? "world" : name.trim();
        return "Hello, " + value + "!";
    }
}
```

```java
// src/test/java/com/example/GreeterTest.java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

class GreeterTest {
    @Test
    void buildsGreeting() {
        assertEquals("Hello, ada!", Greeter.build("  ada "));
    }
}
```

```bash
mvn test
```

## 2. Mock the Trigger with Mockito

Mock `HttpRequestMessage`, `ExecutionContext`, and the response builder to test the trigger method end to end.

```java
// src/test/java/com/example/HttpFunctionTest.java
import com.microsoft.azure.functions.*;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import java.util.*;
import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.assertEquals;

class HttpFunctionTest {
    @Test
    void returnsGreeting() {
        @SuppressWarnings("unchecked")
        HttpRequestMessage<Optional<String>> req = mock(HttpRequestMessage.class);
        when(req.getQueryParameters()).thenReturn(Map.of("name", "grace"));

        final HttpResponseMessage.Builder builder = mock(HttpResponseMessage.Builder.class);
        when(req.createResponseBuilder(any(HttpStatus.class))).thenReturn(builder);
        when(builder.body(any())).thenReturn(builder);
        when(builder.build()).thenReturn(mock(HttpResponseMessage.class));

        ExecutionContext ctx = mock(ExecutionContext.class);
        when(ctx.getLogger()).thenReturn(java.util.logging.Logger.getGlobal());

        new HttpFunction().run(req, ctx);
        verify(req).createResponseBuilder(HttpStatus.OK);
    }
}
```

## 3. Integration Test Against Azurite

```bash
npm install -g azurite
azurite --silent --location ./.azurite &
```

Use the well-known development connection string (`UseDevelopmentStorage=true`) with the Azure Storage Queue SDK to create, send, and read a message inside a JUnit test, then delete the queue. This validates binding behavior without a real storage account.

## 4. Remote Debugging with Core Tools

Start the host with JVM debug options and attach on port 5005.

```bash
mvn azure-functions:run -DenableDebug
# or export JAVA_OPTS before func start:
export JAVA_OPTS="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005"
func start
```

Attach a **Remote JVM Debug** run configuration to `localhost:5005` in IntelliJ, set a breakpoint in the function method, then invoke `http://localhost:7071/api/hello?name=ada`.

!!! info "Flex Consumption note"
    Testing and debugging run entirely on your local machine and are identical across hosting plans. The Flex Consumption plan changes only how the deployed app scales and networks.

## Verification

- [ ] `mvn test` reports all tests passing.
- [ ] The Azurite integration test round-trips a queue message without a real storage account.
- [ ] A breakpoint in the function method is hit when you invoke the local endpoint over the JDWP attach.

## Next Steps

- Wire `mvn test` into your pipeline — see [06 - CI/CD](06-ci-cd.md).
- Extend coverage to the triggers you added in [07 - Extending with Triggers](07-extending-triggers.md).

## See Also

- [Testing recipe](../../recipes/testing.md) — Framework-agnostic testing patterns
- [Run functions locally](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local) — Core Tools reference
- [07 - Extending with Triggers](07-extending-triggers.md)

## Sources

- [Code and test Azure Functions locally (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-develop-local)
- [Azure Functions Java developer guide (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-java)
- [Use Azurite emulator for local Azure Storage development (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite)
</content>
