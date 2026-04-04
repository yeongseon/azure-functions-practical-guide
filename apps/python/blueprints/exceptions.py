import azure.functions as func
import json
import logging

bp = func.Blueprint()
logger = logging.getLogger(__name__)


@bp.route(route="exceptions/test-error", methods=["GET"])
def test_error(req: func.HttpRequest) -> func.HttpResponse:
    """Raise and catch a ValueError to demonstrate exception handling."""
    logger.info("Exception test endpoint requested")

    try:
        raise ValueError("Simulated error for testing")
    except ValueError as exc:
        logger.exception("Caught simulated error: %s", exc)

        body = json.dumps(
            {
                "error": "Handled exception",
                "type": type(exc).__name__,
                "message": str(exc),
            }
        )
        return func.HttpResponse(body, mimetype="application/json", status_code=200)


@bp.route(route="exceptions/unhandled", methods=["GET"])
def unhandled_error(req: func.HttpRequest) -> func.HttpResponse:
    """Raise an unhandled exception to generate real 500 errors in Application Insights."""
    logger.info("Unhandled exception endpoint requested")
    raise RuntimeError("Deliberate unhandled error for KQL data collection")
