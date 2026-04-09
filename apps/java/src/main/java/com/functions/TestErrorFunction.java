package com.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;
import java.util.Optional;

/**
 * Test error endpoint — throws intentional exception for error handling validation.
 */
public class TestErrorFunction {

    @FunctionName("testError")
    public HttpResponseMessage run(
            @HttpTrigger(
                name = "req",
                methods = {HttpMethod.GET},
                authLevel = AuthorizationLevel.ANONYMOUS,
                route = "testerror")
            HttpRequestMessage<Optional<String>> request,
            final ExecutionContext context) {

        context.getLogger().severe("Intentional error for testing");
        throw new RuntimeException("Intentional test error from Java function");
    }
}
