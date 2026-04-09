package com.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;
import java.time.Instant;
import java.util.Optional;

/**
 * Health check endpoint — returns app liveness status.
 */
public class HealthFunction {

    @FunctionName("health")
    public HttpResponseMessage run(
            @HttpTrigger(
                name = "req",
                methods = {HttpMethod.GET},
                authLevel = AuthorizationLevel.ANONYMOUS,
                route = "health")
            HttpRequestMessage<Optional<String>> request,
            final ExecutionContext context) {

        context.getLogger().info("Health check invoked");

        String body = String.format(
            "{\"status\":\"healthy\",\"timestamp\":\"%s\",\"version\":\"1.0.0\"}",
            Instant.now().toString());

        return request.createResponseBuilder(HttpStatus.OK)
                .header("Content-Type", "application/json")
                .body(body)
                .build();
    }
}
