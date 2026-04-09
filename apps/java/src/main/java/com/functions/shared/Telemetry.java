package com.functions.shared;

import java.util.logging.Logger;

/**
 * Telemetry helper — wraps structured logging conventions.
 */
public class Telemetry {

    private static final Logger LOGGER = Logger.getLogger(Telemetry.class.getName());

    public static void trackEvent(String eventName, String details) {
        LOGGER.info(String.format("[Event] %s: %s", eventName, details));
    }

    public static void trackDependency(String name, String target, long durationMs, boolean success) {
        LOGGER.info(String.format("[Dependency] %s -> %s: %dms (success=%s)",
            name, target, durationMs, success));
    }

    public static void trackException(Exception e, String context) {
        LOGGER.severe(String.format("[Exception] %s in %s: %s",
            e.getClass().getSimpleName(), context, e.getMessage()));
    }
}
