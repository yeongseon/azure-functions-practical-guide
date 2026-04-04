import azure.functions as func
import json
import logging

bp = func.Blueprint()
logger = logging.getLogger(__name__)


@bp.route(route="requests/log-levels", methods=["GET"])
def log_levels(req: func.HttpRequest) -> func.HttpResponse:
    """Demonstrate logging at all severity levels."""
    logger.info("Log levels endpoint requested")

    levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    logger.debug("Debug level log message")
    logger.info("Info level log message")
    logger.warning("Warning level log message")
    logger.error("Error level log message")
    logger.critical("Critical level log message")

    body = json.dumps({
        "message": "Logged at all levels",
        "levels": levels,
    })
    return func.HttpResponse(body, mimetype="application/json", status_code=200)
