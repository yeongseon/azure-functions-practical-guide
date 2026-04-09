package com.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;
import java.util.Optional;

/**
 * Info endpoint — returns runtime environment details.
 */
public class InfoFunction {

    @FunctionName("info")
    public HttpResponseMessage run(
            @HttpTrigger(
                name = "req",
                methods = {HttpMethod.GET},
                authLevel = AuthorizationLevel.ANONYMOUS,
                route = "info")
            HttpRequestMessage<Optional<String>> request,
            final ExecutionContext context) {

        String appName = System.getenv("WEBSITE_SITE_NAME") != null
                ? System.getenv("WEBSITE_SITE_NAME") : "local";
        String javaVersion = System.getProperty("java.version");
        String osName = System.getProperty("os.name");

        context.getLogger().info("Info endpoint called");

        String body = String.format(
            "{\"name\":\"azure-functions-java-guide\",\"version\":\"1.0.0\","
            + "\"java\":\"%s\",\"os\":\"%s\","
            + "\"environment\":\"%s\",\"functionApp\":\"%s\","
            + "\"invocationId\":\"%s\"}",
            javaVersion, osName,
            appName.equals("local") ? "development" : "production",
            appName,
            context.getInvocationId());

        return request.createResponseBuilder(HttpStatus.OK)
                .header("Content-Type", "application/json")
                .body(body)
                .build();
    }
}
