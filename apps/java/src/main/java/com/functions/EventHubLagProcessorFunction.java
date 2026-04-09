package com.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;

/**
 * EventHub trigger — processes events from telemetry-events hub.
 */
public class EventHubLagProcessorFunction {

    @FunctionName("eventhubLagProcessor")
    public void run(
            @EventHubTrigger(
                name = "event",
                eventHubName = "telemetry-events",
                connection = "EventHubConnection",
                consumerGroup = "$Default",
                cardinality = Cardinality.ONE)
            String event,
            final ExecutionContext context) {

        context.getLogger().info("EventHub event received: " + event);
    }
}
