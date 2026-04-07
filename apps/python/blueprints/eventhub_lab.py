"""Event Hub checkpoint lag lab blueprint.

Demonstrates checkpoint lag accumulation when processing throughput
drops below ingestion throughput due to artificial processing delay.

Configuration via app settings:
- EventHubLab__ArtificialDelayMs: artificial delay per batch (default: 0)
- EventHubLab__LogCheckpointDelta: log per-batch checkpoint info (default: true)
"""

import azure.functions as func
from typing import List
import logging
import os
import time
import json

bp = func.Blueprint()
logger = logging.getLogger(__name__)


@bp.event_hub_message_trigger(
    arg_name="events",
    event_hub_name="eh-lab-stream",
    connection="EventHubConnection",
    consumer_group="cg-lab",
    cardinality="many",
    data_type="string",
)
def eventhub_lag_processor(events: List[func.EventHubEvent]):
    """Process Event Hub events with configurable artificial delay.

    Logs checkpoint delta metrics for observability.
    """
    delay_ms = int(os.environ.get("EventHubLab__ArtificialDelayMs", "0"))
    log_checkpoint = os.environ.get("EventHubLab__LogCheckpointDelta", "true").lower() == "true"

    batch_start = time.monotonic()
    batch_size = len(events)
    partition_ids = set()
    sequence_numbers = []
    enqueue_times = []

    for event in events:
        partition_ids.add(event.metadata.get("PartitionId", "unknown") if event.metadata else "unknown")
        if event.sequence_number is not None:
            sequence_numbers.append(event.sequence_number)
        if event.enqueued_time:
            enqueue_times.append(event.enqueued_time)

        # Process the event (minimal work)
        body = event.get_body().decode("utf-8", errors="replace")

    # Apply artificial delay
    if delay_ms > 0:
        time.sleep(delay_ms / 1000.0)

    elapsed_ms = (time.monotonic() - batch_start) * 1000
    partition_id = partition_ids.pop() if len(partition_ids) == 1 else ",".join(sorted(partition_ids))

    if log_checkpoint and sequence_numbers:
        min_seq = min(sequence_numbers)
        max_seq = max(sequence_numbers)

        # Calculate backlog age from oldest event in batch
        backlog_age_seconds = 0
        if enqueue_times:
            import datetime
            now = datetime.datetime.now(datetime.timezone.utc)
            oldest_enqueue = min(enqueue_times)
            if oldest_enqueue.tzinfo is None:
                oldest_enqueue = oldest_enqueue.replace(tzinfo=datetime.timezone.utc)
            backlog_age_seconds = max(0, (now - oldest_enqueue).total_seconds())

        logger.info(
            "CheckpointDelta partition=%s batchSize=%d seqRange=[%d-%d] "
            "backlogAgeSec=%.1f processingMs=%.1f delayMs=%d",
            partition_id,
            batch_size,
            min_seq,
            max_seq,
            backlog_age_seconds,
            elapsed_ms,
            delay_ms,
            extra={
                "custom_dimensions": {
                    "PartitionId": partition_id,
                    "BatchSize": batch_size,
                    "MinSequenceNumber": min_seq,
                    "MaxSequenceNumber": max_seq,
                    "CheckpointLagEvents": 0,  # Will be populated by actual lag signal
                    "BacklogAgeSeconds": round(backlog_age_seconds, 1),
                    "ProcessingMs": round(elapsed_ms, 1),
                    "ArtificialDelayMs": delay_ms,
                }
            },
        )

    if batch_size > 0 and (batch_size >= 50 or elapsed_ms > 1000):
        logger.info(
            "Batch completed: partition=%s size=%d elapsed=%.0fms delay=%dms",
            partition_id, batch_size, elapsed_ms, delay_ms,
        )
