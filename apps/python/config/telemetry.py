import logging
import os

from config.settings import settings


def configure_telemetry() -> None:
    """Configure telemetry and logging for the Azure Functions application.

    Sets up structured logging and optionally configures Azure Monitor
    OpenTelemetry when APPLICATIONINSIGHTS_CONNECTION_STRING is available.
    """
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    logger = logging.getLogger(__name__)

    connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")

    if connection_string:
        try:
            from azure.monitor.opentelemetry import configure_azure_monitor

            configure_azure_monitor(
                connection_string=connection_string,
                logger_name="azure-functions-python-guide",
            )
            logger.info(
                "Azure Monitor OpenTelemetry configured (mode=%s)",
                settings.telemetry_mode,
            )
        except ImportError:
            logger.warning(
                "azure-monitor-opentelemetry not installed; "
                "skipping Azure Monitor configuration"
            )
        except Exception as exc:
            logger.warning(
                "Failed to configure Azure Monitor: %s", exc
            )
    else:
        logger.info(
            "APPLICATIONINSIGHTS_CONNECTION_STRING not set; "
            "using basic logging (mode=%s)",
            settings.telemetry_mode,
        )
