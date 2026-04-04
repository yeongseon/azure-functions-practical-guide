import azure.functions as func
import json
import logging
import time

import requests as http_requests

bp = func.Blueprint()
logger = logging.getLogger(__name__)

EXTERNAL_URL = "https://httpbin.org/get"


@bp.route(route="dependencies/external", methods=["GET"])
def external_dependency(req: func.HttpRequest) -> func.HttpResponse:
    """Call an external HTTP service and return timing information."""
    logger.info("External dependency endpoint requested (url=%s)", EXTERNAL_URL)

    start_time = time.monotonic()
    try:
        response = http_requests.get(EXTERNAL_URL, timeout=10)
        elapsed_ms = round((time.monotonic() - start_time) * 1000)

        logger.info(
            "External call completed (status=%d, time=%dms)",
            response.status_code,
            elapsed_ms,
        )

        body = json.dumps({
            "status": "success",
            "statusCode": response.status_code,
            "responseTime": f"{elapsed_ms}ms",
            "url": EXTERNAL_URL,
        })
        return func.HttpResponse(body, mimetype="application/json", status_code=200)

    except http_requests.RequestException as exc:
        elapsed_ms = round((time.monotonic() - start_time) * 1000)
        logger.error(
            "External call failed (error=%s, time=%dms)", exc, elapsed_ms
        )

        body = json.dumps({
            "status": "error",
            "statusCode": 0,
            "responseTime": f"{elapsed_ms}ms",
            "url": EXTERNAL_URL,
            "error": str(exc),
        })
        return func.HttpResponse(body, mimetype="application/json", status_code=502)
