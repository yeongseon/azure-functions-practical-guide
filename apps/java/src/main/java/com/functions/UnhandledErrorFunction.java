package com.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;
import java.util.Optional;

/**
 * Unhandled error endpoint — simulates unhandled exceptions for diagnostics.
 */
public class UnhandledErrorFunction {

    @FunctionName("unhandledError")
    public HttpResponseMessage run(
            @HttpTrigger(
                name = "req",
                methods = {HttpMethod.GET},
                authLevel = AuthorizationLevel.ANONYMOUS,
                route = "unhandlederror")
            HttpRequestMessage<Optional<String>> request,
            final ExecutionContext context) {

        context.getLogger().warning("About to trigger unhandled error");

        // Simulate an unhandled null pointer exception
        String nullStr = null;
        nullStr.length(); // This will throw NullPointerException

        // Unreachable
        return request.createResponseBuilder(HttpStatus.OK).build();
    }
}
