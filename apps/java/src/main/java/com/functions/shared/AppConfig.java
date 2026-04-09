package com.functions.shared;

/**
 * Centralized application configuration loaded from environment variables.
 */
public class AppConfig {

    private static final AppConfig INSTANCE = new AppConfig();

    private final String environment;
    private final String appName;
    private final String telemetryMode;

    private AppConfig() {
        String siteName = System.getenv("WEBSITE_SITE_NAME");
        this.appName = siteName != null ? siteName : "local";
        this.environment = siteName != null ? "production" : "development";
        String mode = System.getenv("TELEMETRY_MODE");
        this.telemetryMode = mode != null ? mode : "basic";
    }

    public static AppConfig getInstance() {
        return INSTANCE;
    }

    public String getEnvironment() {
        return environment;
    }

    public String getAppName() {
        return appName;
    }

    public String getTelemetryMode() {
        return telemetryMode;
    }

    public boolean isProduction() {
        return "production".equals(environment);
    }
}
