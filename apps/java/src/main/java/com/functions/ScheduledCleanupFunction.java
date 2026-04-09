package com.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;

/**
 * Timer trigger — scheduled cleanup job running at 2:00 AM UTC daily.
 */
public class ScheduledCleanupFunction {

    @FunctionName("scheduledCleanup")
    public void run(
            @TimerTrigger(
                name = "timer",
                schedule = "0 0 2 * * *")
            String timerInfo,
            final ExecutionContext context) {

        context.getLogger().info("Scheduled cleanup executed at: " + java.time.Instant.now());
        context.getLogger().info("Timer info: " + timerInfo);
    }
}
