package com.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;
import java.net.InetAddress;
import java.util.Optional;

/**
 * DNS resolution probe — resolves hostname for network troubleshooting.
 */
public class DnsResolveFunction {

    @FunctionName("dnsResolve")
    public HttpResponseMessage run(
            @HttpTrigger(
                name = "req",
                methods = {HttpMethod.GET},
                authLevel = AuthorizationLevel.ANONYMOUS,
                route = "dns/{hostname=google.com}")
            HttpRequestMessage<Optional<String>> request,
            @BindingName("hostname") String hostname,
            final ExecutionContext context) {

        context.getLogger().info("DNS resolve request for: " + hostname);

        try {
            InetAddress[] addresses = InetAddress.getAllByName(hostname);
            StringBuilder ips = new StringBuilder("[");
            for (int i = 0; i < addresses.length; i++) {
                if (i > 0) ips.append(",");
                ips.append("\"").append(addresses[i].getHostAddress()).append("\"");
            }
            ips.append("]");

            String body = String.format(
                "{\"hostname\":\"%s\",\"addresses\":%s,\"resolved\":true}",
                hostname, ips.toString());

            return request.createResponseBuilder(HttpStatus.OK)
                    .header("Content-Type", "application/json")
                    .body(body)
                    .build();
        } catch (Exception e) {
            String body = String.format(
                "{\"hostname\":\"%s\",\"error\":\"%s\",\"resolved\":false}",
                hostname, e.getMessage());

            return request.createResponseBuilder(HttpStatus.OK)
                    .header("Content-Type", "application/json")
                    .body(body)
                    .build();
        }
    }
}
