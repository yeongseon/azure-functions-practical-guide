import azure.functions as func
import logging
import json
import os
import time
from datetime import datetime, timezone

bp = func.Blueprint()
logger = logging.getLogger(__name__)


@bp.queue_trigger(
    arg_name="msg",
    queue_name="work-items",
    connection="QueueStorage",
)
def queue_processor(msg: func.QueueMessage) -> None:
    """Process queue messages with configurable delay for backlog lab.

    Logs enqueue age, dequeue count, processing duration, and instance ID
    for KQL evidence collection.

    Set PROCESSING_DELAY_MS environment variable to inject artificial delay.
    """
    receive_utc = datetime.now(timezone.utc)
    instance_id = os.environ.get("WEBSITE_INSTANCE_ID", "unknown")[:8]

    # Parse message
    try:
        body = json.loads(msg.get_body().decode("utf-8"))
        enqueued_utc_str = body.get("enqueuedUtc", "")
        sequence = body.get("sequence", -1)
    except (json.JSONDecodeError, UnicodeDecodeError):
        body = {}
        enqueued_utc_str = ""
        sequence = -1

    # Compute message age
    age_ms = -1
    if enqueued_utc_str:
        try:
            enqueued_utc = datetime.fromisoformat(enqueued_utc_str.replace("Z", "+00:00"))
            age_ms = int((receive_utc - enqueued_utc).total_seconds() * 1000)
        except (ValueError, TypeError):
            age_ms = -1

    # Inject configurable processing delay
    delay_ms = int(os.environ.get("PROCESSING_DELAY_MS", "0"))
    start = time.monotonic()
    if delay_ms > 0:
        time.sleep(delay_ms / 1000.0)
    processing_ms = int((time.monotonic() - start) * 1000)

    dequeue_count = msg.dequeue_count

    logger.info(
        "QueueProcessed sequence=%d ageMs=%d dequeueCount=%d "
        "processingMs=%d instanceId=%s delayMs=%d",
        sequence,
        age_ms,
        dequeue_count,
        processing_ms,
        instance_id,
        delay_ms,
    )
