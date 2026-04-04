import azure.functions as func
import json
import logging
from datetime import datetime, timezone

bp = func.Blueprint()
logger = logging.getLogger(__name__)


@bp.route(route="health", methods=["GET"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint returning application status."""
    logger.info("Health check requested")
    body = json.dumps({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
    })
    return func.HttpResponse(body, mimetype="application/json", status_code=200)
