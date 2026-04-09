package com.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;
import java.util.Optional;

/**
 * Slow response endpoint — delays response by configurable duration for latency testing.
 */
public class SlowResponseFunction {

    @FunctionName("slowResponse")
    public HttpResponseMessage run(
            @HttpTrigger(
                name = "req",
                methods = {HttpMethod.GET},
                authLevel = AuthorizationLevel.ANONYMOUS,
                route = "slow")
            HttpRequestMessage<Optional<String>> request,
            final ExecutionContext context) {

        String delayParam = request.getQueryParameters().getOrDefault("delay", "2");
        int delaySec;
        try {
            delaySec = Integer.parseInt(delayParam);
        } catch (NumberFormatException e) {
            delaySec = 2;
        }

        context.getLogger().info("Slow response: delaying " + delaySec + "s");

        try {
            Thread.sleep(delaySec * 1000L);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        String body = String.format(
            "{\"delayed\":%d,\"message\":\"Response after %d second(s)\"}",
            delaySec, delaySec);

        return request.createResponseBuilder(HttpStatus.OK)
                .header("Content-Type", "application/json")
                .body(body)
                .build();
    }
}
