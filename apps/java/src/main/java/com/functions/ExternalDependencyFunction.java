package com.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Optional;

/**
 * External dependency probe — measures latency to an external URL.
 */
public class ExternalDependencyFunction {

    private static final HttpClient HTTP_CLIENT = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(5))
            .build();

    @FunctionName("externalDependency")
    public HttpResponseMessage run(
            @HttpTrigger(
                name = "req",
                methods = {HttpMethod.GET},
                authLevel = AuthorizationLevel.ANONYMOUS,
                route = "dependency")
            HttpRequestMessage<Optional<String>> request,
            final ExecutionContext context) {

        String url = request.getQueryParameters().getOrDefault("url", "https://httpbin.org/get");
        context.getLogger().info("External dependency check: " + url);

        long start = System.currentTimeMillis();
        try {
            HttpRequest httpReq = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .timeout(Duration.ofSeconds(10))
                    .GET()
                    .build();

            HttpResponse<String> response = HTTP_CLIENT.send(httpReq, HttpResponse.BodyHandlers.ofString());
            long elapsed = System.currentTimeMillis() - start;

            String body = String.format(
                "{\"url\":\"%s\",\"statusCode\":%d,\"latencyMs\":%d,\"success\":true}",
                url, response.statusCode(), elapsed);

            return request.createResponseBuilder(HttpStatus.OK)
                    .header("Content-Type", "application/json")
                    .body(body)
                    .build();
        } catch (Exception e) {
            long elapsed = System.currentTimeMillis() - start;
            String body = String.format(
                "{\"url\":\"%s\",\"error\":\"%s\",\"latencyMs\":%d,\"success\":false}",
                url, e.getMessage(), elapsed);

            return request.createResponseBuilder(HttpStatus.INTERNAL_SERVER_ERROR)
                    .header("Content-Type", "application/json")
                    .body(body)
                    .build();
        }
    }
}
