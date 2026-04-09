package com.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;
import java.util.Optional;

/**
 * Emits logs at multiple severity levels for telemetry validation.
 */
public class LogLevelsFunction {

    @FunctionName("logLevels")
    public HttpResponseMessage run(
            @HttpTrigger(
                name = "req",
                methods = {HttpMethod.GET},
                authLevel = AuthorizationLevel.ANONYMOUS,
                route = "loglevels")
            HttpRequestMessage<Optional<String>> request,
            final ExecutionContext context) {

        context.getLogger().info("Info-level message from logLevels");
        context.getLogger().warning("Warning-level message from logLevels");
        context.getLogger().severe("Error-level message from logLevels");

        return request.createResponseBuilder(HttpStatus.OK)
                .header("Content-Type", "application/json")
                .body("{\"logged\":true}")
                .build();
    }
}
