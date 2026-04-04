import azure.functions as func
import logging
from datetime import datetime, timezone

bp = func.Blueprint()
logger = logging.getLogger(__name__)


@bp.timer_trigger(
    schedule="0 */5 * * * *",
    arg_name="timer",
    run_on_startup=False,
)
def scheduled_cleanup(timer: func.TimerRequest) -> None:
    """Runs every 5 minutes to perform scheduled maintenance tasks.

    Common use cases:
    - Clean up expired cache entries
    - Generate periodic reports
    - Ping downstream health endpoints

    Set run_on_startup=True temporarily for local testing, but always
    revert to False before deploying to production on the Consumption plan.
    """
    utc_timestamp = datetime.now(timezone.utc).isoformat()

    if timer.past_due:
        logger.warning("Timer trigger is past due: %s", utc_timestamp)

    logger.info("Scheduled cleanup fired at %s", utc_timestamp)
