import azure.functions as func
import json
import logging
import os
import sys

bp = func.Blueprint()
logger = logging.getLogger(__name__)


@bp.route(route="info", methods=["GET"])
def info(req: func.HttpRequest) -> func.HttpResponse:
    """Application info endpoint returning runtime and configuration details."""
    logger.info("Info endpoint requested")
    body = json.dumps({
        "name": "azure-functions-python-guide",
        "version": "1.0.0",
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "environment": os.environ.get("AZURE_FUNCTIONS_ENVIRONMENT", "development"),
        "telemetryMode": os.environ.get("TELEMETRY_MODE", "basic"),
        "functionApp": os.environ.get("WEBSITE_SITE_NAME", "local"),
        "invocationId": req.headers.get("x-ms-request-id", "local"),
    })
    return func.HttpResponse(body, mimetype="application/json", status_code=200)
