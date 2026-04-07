#!/usr/bin/env python3
"""Event Hub event producer for the checkpoint lag lab.

Sends events at a configurable rate to an Event Hub to create
sustained ingestion pressure for the checkpoint lag experiment.

Usage:
    python producer.py --namespace <namespace> --eventhub <hub-name> \
        --events-per-second 500 --duration-seconds 300

Requires: pip install azure-eventhub azure-identity
"""

import argparse
import json
import time
import uuid
import sys
from datetime import datetime, timezone

from azure.eventhub import EventHubProducerClient, EventData
from azure.identity import DefaultAzureCredential


def create_event(index: int, batch_id: str) -> EventData:
    """Create a single event with metadata."""
    payload = {
        "eventId": str(uuid.uuid4()),
        "index": index,
        "batchId": batch_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": f"lab-event-{index:08d}",
    }
    return EventData(json.dumps(payload))


def main():
    parser = argparse.ArgumentParser(description="Event Hub producer for checkpoint lag lab")
    parser.add_argument("--namespace", required=True, help="Event Hub namespace (FQDN without .servicebus.windows.net)")
    parser.add_argument("--eventhub", required=True, help="Event Hub name")
    parser.add_argument("--events-per-second", type=int, default=500, help="Target events per second")
    parser.add_argument("--duration-seconds", type=int, default=300, help="Duration to produce events")
    parser.add_argument("--batch-size", type=int, default=100, help="Events per batch send")
    parser.add_argument("--connection-string", default=None, help="Connection string (optional, uses DefaultAzureCredential if not provided)")
    args = parser.parse_args()

    batch_id = str(uuid.uuid4())[:8]
    fqdn = f"{args.namespace}.servicebus.windows.net"

    if args.connection_string:
        producer = EventHubProducerClient.from_connection_string(
            conn_str=args.connection_string,
            eventhub_name=args.eventhub,
        )
    else:
        credential = DefaultAzureCredential()
        producer = EventHubProducerClient(
            fully_qualified_namespace=fqdn,
            eventhub_name=args.eventhub,
            credential=credential,
        )

    total_sent = 0
    start_time = time.monotonic()
    interval = args.batch_size / args.events_per_second

    print(f"Producing {args.events_per_second} events/sec to {fqdn}/{args.eventhub}")
    print(f"Duration: {args.duration_seconds}s, Batch size: {args.batch_size}")
    print(f"Batch ID: {batch_id}")
    print()

    try:
        with producer:
            while (time.monotonic() - start_time) < args.duration_seconds:
                batch_start = time.monotonic()

                event_data_batch = producer.create_batch()
                for i in range(args.batch_size):
                    event = create_event(total_sent + i, batch_id)
                    try:
                        event_data_batch.add(event)
                    except ValueError:
                        # Batch is full, send what we have
                        break

                producer.send_batch(event_data_batch)
                sent_count = len(event_data_batch)
                total_sent += sent_count

                elapsed = time.monotonic() - start_time
                rate = total_sent / elapsed if elapsed > 0 else 0

                if total_sent % (args.events_per_second * 10) < args.batch_size:
                    print(
                        f"  [{elapsed:6.1f}s] Sent {total_sent:>8,} events "
                        f"({rate:,.0f} events/sec avg)",
                        flush=True,
                    )

                # Rate limit
                batch_elapsed = time.monotonic() - batch_start
                sleep_time = interval - batch_elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    total_elapsed = time.monotonic() - start_time
    avg_rate = total_sent / total_elapsed if total_elapsed > 0 else 0

    print(f"\nDone. Sent {total_sent:,} events in {total_elapsed:.1f}s ({avg_rate:,.0f} events/sec)")

    result = {
        "batchId": batch_id,
        "totalEventsSent": total_sent,
        "durationSeconds": round(total_elapsed, 1),
        "averageEventsPerSecond": round(avg_rate, 1),
        "namespace": fqdn,
        "eventhub": args.eventhub,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
