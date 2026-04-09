package com.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;
import java.util.Optional;

/**
 * Identity probe — checks managed identity availability.
 */
public class IdentityProbeFunction {

    @FunctionName("identityProbe")
    public HttpResponseMessage run(
            @HttpTrigger(
                name = "req",
                methods = {HttpMethod.GET},
                authLevel = AuthorizationLevel.ANONYMOUS,
                route = "identity")
            HttpRequestMessage<Optional<String>> request,
            final ExecutionContext context) {

        String identityEndpoint = System.getenv("IDENTITY_ENDPOINT");
        String identityHeader = System.getenv("IDENTITY_HEADER");

        boolean hasManagedIdentity = identityEndpoint != null && identityHeader != null;

        context.getLogger().info("Identity probe: managed identity "
            + (hasManagedIdentity ? "available" : "not available"));

        String body = String.format(
            "{\"managedIdentity\":%s,\"identityEndpoint\":\"%s\"}",
            hasManagedIdentity,
            hasManagedIdentity ? "configured" : "not configured");

        return request.createResponseBuilder(HttpStatus.OK)
                .header("Content-Type", "application/json")
                .body(body)
                .build();
    }
}
