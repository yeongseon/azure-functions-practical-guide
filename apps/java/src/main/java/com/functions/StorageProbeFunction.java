package com.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;
import java.util.Optional;

/**
 * Storage probe — checks storage account connectivity.
 */
public class StorageProbeFunction {

    @FunctionName("storageProbe")
    public HttpResponseMessage run(
            @HttpTrigger(
                name = "req",
                methods = {HttpMethod.GET},
                authLevel = AuthorizationLevel.ANONYMOUS,
                route = "storage/probe")
            HttpRequestMessage<Optional<String>> request,
            final ExecutionContext context) {

        String storageConn = System.getenv("AzureWebJobsStorage");
        boolean hasStorage = storageConn != null && !storageConn.isEmpty();

        context.getLogger().info("Storage probe: connection "
            + (hasStorage ? "configured" : "missing"));

        String body = String.format(
            "{\"storageConfigured\":%s,\"connectionType\":\"%s\"}",
            hasStorage,
            hasStorage ? (storageConn.contains("AccountName=") ? "connectionString" : "identity") : "none");

        return request.createResponseBuilder(HttpStatus.OK)
                .header("Content-Type", "application/json")
                .body(body)
                .build();
    }
}
