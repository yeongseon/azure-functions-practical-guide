package com.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;

/**
 * Timer lab — short-interval timer for observing trigger behavior.
 */
public class TimerLabFunction {

    @FunctionName("timerLab")
    public void run(
            @TimerTrigger(
                name = "timer",
                schedule = "0 */5 * * * *")
            String timerInfo,
            final ExecutionContext context) {

        context.getLogger().info("Timer lab fired at: " + java.time.Instant.now());
    }
}
