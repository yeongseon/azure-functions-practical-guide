import azure.functions as func
import logging
import os
from datetime import datetime, timezone

bp = func.Blueprint()
logger = logging.getLogger(__name__)


@bp.timer_trigger(
    schedule="%TIMER_LAB_SCHEDULE%",
    arg_name="timer",
    run_on_startup=False,
)
def timer_lab(timer: func.TimerRequest) -> None:
    """Timer trigger for missed-schedules lab.

    Schedule is controlled by TIMER_LAB_SCHEDULE app setting.
    Default should be set to '0 */2 * * * *' (every 2 minutes).

    Logs isPastDue, schedule status, and instance ID for KQL evidence.
    """
    utc_now = datetime.now(timezone.utc)
    instance_id = os.environ.get("WEBSITE_INSTANCE_ID", "unknown")[:8]

    is_past_due = timer.past_due

    # Extract schedule status if available
    schedule_last = ""
    schedule_next = ""
    schedule_last_updated = ""
    if hasattr(timer, "schedule_status") and timer.schedule_status:
        schedule_last = str(timer.schedule_status.get("Last", ""))
        schedule_next = str(timer.schedule_status.get("Next", ""))
        schedule_last_updated = str(timer.schedule_status.get("LastUpdated", ""))

    logger.info(
        "TimerFired isPastDue=%s actualUtc=%s scheduleLast=%s "
        "scheduleNext=%s lastUpdated=%s instanceId=%s",
        is_past_due,
        utc_now.isoformat(),
        schedule_last,
        schedule_next,
        schedule_last_updated,
        instance_id,
    )

    if is_past_due:
        logger.warning(
            "TimerPastDue actualUtc=%s scheduleLast=%s instanceId=%s",
            utc_now.isoformat(),
            schedule_last,
            instance_id,
        )
