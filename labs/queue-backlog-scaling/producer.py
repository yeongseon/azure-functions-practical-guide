#!/usr/bin/env python3
"""Queue message producer for queue-backlog-scaling lab.

Sends a burst of messages to the 'work-items' queue to trigger
scaling behavior and backlog accumulation.

Usage:
    export STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;..."
    python producer.py --count 2000 --delay-between-batches 0.05

    # Or use account name with DefaultAzureCredential:
    export STORAGE_ACCOUNT_NAME="labsharedstorage"
    python producer.py --count 2000 --use-identity
"""

import argparse
import json
import os
import time
from datetime import datetime, timezone


def main():
    parser = argparse.ArgumentParser(description="Queue burst producer")
    parser.add_argument("--count", type=int, default=2000, help="Total messages to send")
    parser.add_argument("--batch-size", type=int, default=32, help="Messages per batch")
    parser.add_argument(
        "--delay-between-batches",
        type=float,
        default=0.05,
        help="Seconds between batches",
    )
    parser.add_argument(
        "--use-identity", action="store_true", help="Use DefaultAzureCredential"
    )
    parser.add_argument("--queue-name", default="work-items", help="Queue name")
    args = parser.parse_args()

    if args.use_identity:
        from azure.identity import DefaultAzureCredential
        from azure.storage.queue import QueueClient

        account_name = os.environ["STORAGE_ACCOUNT_NAME"]
        credential = DefaultAzureCredential()
        queue_client = QueueClient(
            account_url=f"https://{account_name}.queue.core.windows.net",
            queue_name=args.queue_name,
            credential=credential,
        )
    else:
        from azure.storage.queue import QueueClient

        conn_str = os.environ["STORAGE_CONNECTION_STRING"]
        queue_client = QueueClient.from_connection_string(
            conn_str, queue_name=args.queue_name
        )

    # Ensure queue exists
    try:
        queue_client.create_queue()
        print(f"Created queue '{args.queue_name}'")
    except Exception:
        print(f"Queue '{args.queue_name}' already exists")

    print(
        f"Sending {args.count} messages in batches of {args.batch_size} "
        f"with {args.delay_between_batches}s delay between batches..."
    )

    sent = 0
    start = time.monotonic()

    while sent < args.count:
        batch_end = min(sent + args.batch_size, args.count)
        for seq in range(sent, batch_end):
            message = json.dumps(
                {
                    "enqueuedUtc": datetime.now(timezone.utc).isoformat(),
                    "sequence": seq,
                    "payload": f"lab-message-{seq:06d}",
                }
            )
            queue_client.send_message(message)

        sent = batch_end
        elapsed = time.monotonic() - start
        rate = sent / elapsed if elapsed > 0 else 0
        print(f"  Sent {sent}/{args.count} ({rate:.0f} msg/s)")

        if sent < args.count:
            time.sleep(args.delay_between_batches)

    elapsed = time.monotonic() - start
    print(f"\nDone. Sent {sent} messages in {elapsed:.1f}s ({sent/elapsed:.0f} msg/s)")


if __name__ == "__main__":
    main()
