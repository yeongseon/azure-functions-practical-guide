# 01 - Run Locally (Consumption)

Set up a Java Azure Functions app on your workstation and validate the first HTTP endpoint before touching Azure resources.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| JDK | 17+ | Compile and run Java functions locally |
| Maven | 3.9+ | Build and deploy Java artifacts |
| Azure Functions Core Tools | v4 | Start local host and publish artifacts |
| Azure CLI | 2.61+ | Provision Azure resources and inspect app state |

!!! info "Plan basics"
    Consumption (Y1) is fully serverless with scale-to-zero and pay-per-execution billing. It is ideal for bursty workloads that do not require VNet integration.

## What You'll Build

A Java HTTP-triggered Azure Function scaffolded from the Azure Functions Maven archetype, built with Maven, and validated locally at `/api/hello/{name?}`.

## Steps

```mermaid
flowchart LR
    A[Initialize Maven project] --> B[Add Java function class]
    B --> C[Start Functions host]
    C --> D[Test local endpoint]
```


### Step 1 - Create the Java project

The recommended approach uses the Maven archetype:

```bash
mvn archetype:generate \
    -DarchetypeGroupId=com.microsoft.azure \
    -DarchetypeArtifactId=azure-functions-archetype \
    -DgroupId=com.example \
    -DartifactId=my-java-functions \
    -Dversion=1.0-SNAPSHOT \
    -DappName=my-java-functions \
    -DjavaVersion=17 \
    -DinteractiveMode=false
cd my-java-functions
```

### Step 2 - Confirm Maven project structure

```text
project-root/
├── src/
│   └── main/
│       └── java/
│           └── com/example/
│               ├── Function.java
│               └── ...
├── host.json
├── local.settings.json
└── pom.xml
```

### Step 3 - Add a minimal HTTP trigger

```java
package com.example;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;
import java.util.Optional;

public class Function {
    @FunctionName("HelloJava")
    public HttpResponseMessage run(
        @HttpTrigger(
            name = "req",
            methods = {HttpMethod.GET, HttpMethod.POST},
            authLevel = AuthorizationLevel.FUNCTION,
            route = "hello/{name?}")
        HttpRequestMessage<Optional<String>> request,
        @BindingName("name") String name,
        final ExecutionContext context) {

        String input = request.getBody().orElse(name != null ? name : "world");
        context.getLogger().info("Processing local Java request for: " + input);

        return request.createResponseBuilder(HttpStatus.OK)
            .body("Hello, " + input + " from Java!")
            .build();
    }
}
```

### Step 4 - Start the local runtime

```bash
mvn clean package
mvn azure-functions:run
```

### Step 5 - Call the endpoint

In a second terminal, call the endpoint:

```bash
curl --request GET "http://localhost:7071/api/hello/local"
```

## Verification

```text
[INFO] Azure Functions Java Worker started
Functions:
    HelloJava: [GET,POST] http://localhost:7071/api/hello/{name?}
```

```text
Hello, local from Java!
```

Confirm that Maven starts the Functions host, that `HelloJava` is listed in the local endpoint table, and that `curl --request GET "http://localhost:7071/api/hello/local"` returns `Hello, local from Java!`.

## See Also

- [Tutorial Overview & Plan Chooser](../index.md)
- [Java Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources

- [Azure Functions Java developer guide (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-java)
- [Azure Functions hosting options (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-scale)
- [Create a Java function with Azure Functions Core Tools (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/create-first-function-cli-java)
