import os


class Settings:
    """Application settings loaded from environment variables."""

    app_name: str = os.environ.get("APP_NAME", "azure-functions-field-guide")
    environment: str = os.environ.get("AZURE_FUNCTIONS_ENVIRONMENT", "production")
    telemetry_mode: str = os.environ.get("TELEMETRY_MODE", "basic")
    function_app_name: str = os.environ.get("WEBSITE_SITE_NAME", "local")
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")


settings = Settings()
