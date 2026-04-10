---
content_sources:
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-bindings-storage-queue
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-host-json
---

# Queue Storage Integration

This recipe demonstrates Java queue trigger and queue output bindings with retry behavior, host settings, and poison queue handling.

## Architecture

<!-- diagram-id: architecture -->
```mermaid
flowchart LR
    API[HTTP enqueue] --> QUEUE[(work-items queue)]
    QUEUE --> TRIGGER[@QueueTrigger worker]
    TRIGGER --> RESULT[@QueueOutput results queue]
    QUEUE --> POISON[(work-items-poison queue)]
```

## Prerequisites

Create queues:

```bash
az storage queue create --name work-items --account-name $STORAGE_NAME --auth-mode login
az storage queue create --name work-results --account-name $STORAGE_NAME --auth-mode login
```

Queue runtime defaults in `host.json`:

```json
{
  "version": "2.0",
  "extensions": {
    "queues": {
      "maxPollingInterval": "00:01:00",
      "visibilityTimeout": "00:00:00",
      "maxDequeueCount": 5
    }
  }
}
```

## Java implementation

```java
package com.contoso.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;

import java.util.Optional;

public class QueueFunctions {

    @FunctionName("enqueueWork")
    @QueueOutput(name = "output", queueName = "work-items", connection = "AzureWebJobsStorage")
    public String enqueueWork(
        @HttpTrigger(
            name = "request",
            methods = {HttpMethod.POST},
            authLevel = AuthorizationLevel.FUNCTION,
            route = "queue/work"
        ) HttpRequestMessage<Optional<String>> request
    ) {
        return request.getBody().orElse("{\"job\":\"default\"}");
    }

    @FunctionName("processWork")
    @QueueOutput(name = "result", queueName = "work-results", connection = "AzureWebJobsStorage")
    public String processWork(
        @QueueTrigger(
            name = "message",
            queueName = "work-items",
            connection = "AzureWebJobsStorage"
        ) String message,
        final ExecutionContext context
    ) {
        context.getLogger().info("Processing queue message: " + message);

        if (message.contains("force-error")) {
            throw new RuntimeException("Simulated failure to demonstrate poison queue behavior");
        }

        return "processed:" + message;
    }
}
```

## Poison queue handling

- Messages that exceed `maxDequeueCount` are moved to `<queue-name>-poison`.
- Investigate poison messages with:

```bash
az storage message peek \
  --queue-name work-items-poison \
  --account-name $STORAGE_NAME \
  --auth-mode login
```

## Implementation notes

- Keep workers idempotent and safe for retries.
- Tune `batchSize` and `newBatchThreshold` only after observing throughput.
- Use dead-letter/poison analysis as part of incident runbooks.

## See Also

- [Blob Storage Integration](blob-storage.md)
- [Timer Trigger](timer.md)
- [Managed Identity](managed-identity.md)

## Sources

- [Azure Queue storage bindings for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-bindings-storage-queue)
- [Azure Functions host.json reference (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-host-json)
