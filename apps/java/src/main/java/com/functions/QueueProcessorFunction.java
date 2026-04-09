package com.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;

/**
 * Queue trigger — processes messages from incoming-orders queue.
 */
public class QueueProcessorFunction {

    @FunctionName("queueProcessor")
    public void run(
            @QueueTrigger(
                name = "message",
                queueName = "incoming-orders",
                connection = "QueueStorage")
            String message,
            final ExecutionContext context) {

        context.getLogger().info("Queue message received: " + message);
    }
}
