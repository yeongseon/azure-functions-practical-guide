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

        body = json.dumps({
            "error": "Handled exception",
            "type": type(exc).__name__,
            "message": str(exc),
        })
        return func.HttpResponse(body, mimetype="application/json", status_code=200)
