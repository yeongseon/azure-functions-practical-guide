package com.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;
import java.util.Optional;

/**
 * HTTP hello endpoint — basic greeting with optional name parameter.
 */
public class HelloHttpFunction {

    @FunctionName("helloHttp")
    public HttpResponseMessage run(
            @HttpTrigger(
                name = "req",
                methods = {HttpMethod.GET},
                authLevel = AuthorizationLevel.ANONYMOUS,
                route = "hello/{name=world}")
            HttpRequestMessage<Optional<String>> request,
            @BindingName("name") String name,
            final ExecutionContext context) {

        String greeting = (name != null && !name.isEmpty()) ? name : "world";
        context.getLogger().info("Handled hello for " + greeting);

        return request.createResponseBuilder(HttpStatus.OK)
                .header("Content-Type", "application/json")
                .body("{\"message\":\"Hello, " + greeting + "\"}")
                .build();
    }
}
