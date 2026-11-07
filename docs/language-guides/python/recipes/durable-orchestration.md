---
content_sources:

  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-eternal-orchestrations
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-http-features
  diagrams:
    - id: overview
      type: flowchart
      source: self-generated
      justification: Illustrative logical view of client, orchestrator and activity roles plus the HTTP 202 management-URL and runtime-owned status-query paths; shows logical relationships only, not hosting topology or a measured trace.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-http-features
        - https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-http-features#async-operation-tracking
        - https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-instance-management#query-instances
        - https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-azure-storage-provider#instances-table-for-orchestration-and-entity-status
        - https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-code-constraints
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python
    - id: fan-out-fan-in-pattern
      type: sequenceDiagram
      source: self-generated
      justification: Illustrative sequence of an orchestrator scheduling several activities, waiting for all results and aggregating them; completion order and activity count are examples, not a measured trace.
      based_on:
        - https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-fan-in-fan-out
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python
    - id: monitor-pattern
      type: flowchart
      source: self-generated
      justification: Illustrative polling-loop flow in which an orchestrator checks job status, then waits on a durable timer until the job is done or a deadline passes; the polling interval and deadline are examples, not measurements.
      based_on:
        - https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-timers
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-eternal-orchestrations
    - id: human-interaction-pattern
      type: sequenceDiagram
      source: self-generated
      justification: Illustrative sequence of an orchestrator waiting on an external event and a durable timeout timer, applying the decision if the event arrives first or escalating if the timer wins; not a measured trace.
      based_on:
        - https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-external-events
        - https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-timers
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-http-features
---
# Durable Functions

> **Note:** This recipe covers Durable Functions patterns with Azure Functions Python v2. HTTP triggers are used as the entry point to start orchestrations, making this a natural extension of HTTP-based function apps.

## Overview

Durable Functions enable stateful workflows in serverless Azure Functions. They are ideal for long-running operations, fan-out/fan-in patterns, human interaction workflows, and function chaining that would be impractical with standard stateless functions.

Durable Functions use three function types:

| Function Type | Purpose | Example |
|--------------|---------|---------|
| **Client** (Starter) | Starts an orchestration (often HTTP-triggered) | REST API receives a request, starts a workflow |
| **Orchestrator** | Defines the workflow logic, coordinates activities | Chain activity calls, fan-out/fan-in, wait for events |
| **Activity** | Performs the actual work (a single unit of work) | Send an email, process a file, call an API |

<!-- diagram-id: overview -->
```mermaid
flowchart TD
    accTitle: Durable workflow roles and runtime-owned status queries
    accDescr: Client functions start a deterministic orchestrator and return HTTP 202 with management URLs without waiting for completion. The orchestrator calls activities and receives results. Status queries use the Durable runtime management API to read persisted orchestration metadata without invoking orchestrator code.
    HTTP["HTTP caller"] --> CL["Client functions<br/>Start / status"]
    CL -->|"start"| ORC["Orchestrator<br/>Deterministic workflow"]
    ORC -->|"call"| A1["Activity 1"]
    ORC -->|"call"| A2["Activity 2"]
    ORC -->|"call"| A3["Activity 3"]
    A1 --> ORC
    A2 --> ORC
    A3 --> ORC
    RT["Durable runtime<br/>Management API"] -->|"status result"| CL
    CL -->|"202 + URLs"| HTTP
    CL -->|"query status"| RT
    %% Layout-only tiers; add no activity calls or execution-order arrows.
    RT ~~~ ORC
    A1 ~~~ A2
    A2 ~~~ A3
    classDef neutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class HTTP,CL,ORC,A1,A2,A3,RT neutral;
```

**Reading key:** “start” is `start_new()`, which returns an `instance_id`.
“call” is `call_activity()`; activities 1–3 retain the illustrative names
`validate_order`, `charge_payment` and `send_notification`. Unlabelled return
arrows carry activity results. The HTTP-triggered client starts the workflow and
returns HTTP 202 with management URLs (including status and terminate), not a
completion callback. Status queries use the Durable client API or the returned runtime management URL; they read orchestration status without invoking orchestrator code. The starter returns 202 without waiting for completion. These are logical
roles, not network hops or a chronological sequence
([HTTP management](https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-http-features#async-operation-tracking),
[client status query](https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-instance-management#query-instances),
[persisted status metadata](https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-azure-storage-provider#instances-table-for-orchestration-and-entity-status)).

## Prerequisites

Add the Durable Functions package to `requirements.txt`:

```
azure-functions-durable>=1.2.0
```

Ensure your `host.json` has the extension bundle:

```json
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
```

Durable Functions also require Azure Storage (`AzureWebJobsStorage`) for storing orchestration state, history, and messages. On Flex Consumption, configure host storage with identity-based settings (e.g. `AzureWebJobsStorage__accountName`) rather than a connection string. Durable Functions are supported on Flex Consumption; for lower orchestration startup latency, use the `durable` always-ready instance group.

## HTTP Starter: Kick Off an Orchestration

The client function is an HTTP trigger that starts a new orchestration instance:

```python
import azure.functions as func
import azure.durable_functions as df
import json

bp = df.Blueprint()

@bp.route(route="orchestrations/{function_name}", methods=["POST"])
@bp.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client: df.DurableOrchestrationClient) -> func.HttpResponse:
    """HTTP endpoint that starts a durable orchestration."""
    function_name = req.route_params.get("function_name")

    # Optional: pass input from the HTTP request body
    try:
        payload = req.get_json()
    except ValueError:
        payload = None

    # Start the orchestration
    instance_id = await client.start_new(function_name, client_input=payload)

    # Return management URLs for checking status, terminating, etc.
    return client.create_check_status_response(req, instance_id)
```

When you call this endpoint, the response includes management URLs:

```bash
curl --request POST http://localhost:7071/api/orchestrations/order_processing \
  --header "Content-Type: application/json" \
  --data '{"order_id": "12345", "items": ["widget-a", "widget-b"]}'
```

Response:

```json
{
  "id": "abc123...",
  "statusQueryGetUri": "http://localhost:7071/runtime/webhooks/durabletask/instances/abc123...",
  "sendEventPostUri": "http://localhost:7071/runtime/webhooks/durabletask/instances/abc123.../raiseEvent/{eventName}",
  "terminatePostUri": "http://localhost:7071/runtime/webhooks/durabletask/instances/abc123.../terminate",
  "purgeHistoryDeleteUri": "http://localhost:7071/runtime/webhooks/durabletask/instances/abc123..."
}
```

## Orchestrator: Define the Workflow

The orchestrator function defines the sequence of operations. It must be **deterministic** — no random values, no current time, no direct I/O. All work happens through activity calls.

```python
@bp.orchestration_trigger(context_name="context")
def order_processing(context: df.DurableOrchestrationContext):
    """Orchestrate order processing: validate → charge → fulfill → notify."""
    order = context.get_input()

    # Step 1: Validate the order
    validation = yield context.call_activity("validate_order", order)
    if not validation["valid"]:
        return {"status": "rejected", "reason": validation["reason"]}

    # Step 2: Charge the customer
    charge_result = yield context.call_activity("charge_customer", {
        "order_id": order["order_id"],
        "amount": validation["total"]
    })

    # Step 3: Fulfill the order
    fulfillment = yield context.call_activity("fulfill_order", order)

    # Step 4: Notify the customer
    yield context.call_activity("send_notification", {
        "order_id": order["order_id"],
        "email": order.get("email"),
        "status": "completed"
    })

    return {
        "status": "completed",
        "order_id": order["order_id"],
        "charge_id": charge_result["charge_id"],
        "tracking_number": fulfillment["tracking_number"]
    }
```

## Activity Functions: Do the Work

Activity functions are the building blocks that perform actual work:

```python
@bp.activity_trigger(input_name="order")
def validate_order(order: dict) -> dict:
    """Validate the order and calculate total."""
    items = order.get("items", [])
    if not items:
        return {"valid": False, "reason": "No items in order"}

    # Simulate price lookup
    price_per_item = 29.99
    total = len(items) * price_per_item

    return {"valid": True, "total": total, "item_count": len(items)}


@bp.activity_trigger(input_name="charge_input")
def charge_customer(charge_input: dict) -> dict:
    """Charge the customer (simulated)."""
    import uuid
    return {
        "charge_id": str(uuid.uuid4()),
        "amount": charge_input["amount"],
        "status": "charged"
    }


@bp.activity_trigger(input_name="order")
def fulfill_order(order: dict) -> dict:
    """Fulfill the order (simulated)."""
    import uuid
    return {
        "tracking_number": f"TRK-{uuid.uuid4().hex[:8].upper()}",
        "status": "shipped"
    }


@bp.activity_trigger(input_name="notification")
def send_notification(notification: dict) -> dict:
    """Send a notification to the customer (simulated)."""
    import logging
    logging.info(f"Notification sent to {notification.get('email')} for order {notification['order_id']}")
    return {"sent": True}
```

## Fan-Out / Fan-In Pattern

<!-- diagram-id: fan-out-fan-in-pattern -->
```mermaid
%%{init: {"sequence": {"width": 40, "actorMargin": 10, "diagramMarginX": 5, "noteMargin": 5}}}%%
sequenceDiagram
    accTitle: Fan-out, join and aggregate
    accDescr: The orchestrator schedules three activity tasks before waiting, receives each result, waits for all results with task_all, and aggregates them. Activity completion order is illustrative.
    participant O as O
    participant A1 as A1
    participant A2 as A2
    participant A3 as A3

    O->>A1: call 1
    O->>A2: call 2
    O->>A3: call 3
    A1-->>O: result_1
    A2-->>O: result_2
    A3-->>O: result_3
    Note over O: Join all<br/>three results
    O->>O: aggregate
```

**Reading key:** O = orchestrator; A1/A2/A3 = activity functions
`process_item_1`, `process_item_2`, `process_item_3`. “call 1–3” means
`call_activity()` scheduled in parallel (tasks t1–t3); `result_1`–`result_3`
are r1–r3. “Join all” is `task_all([t1, t2, t3])`; “aggregate” is
`aggregate_results([r1, r2, r3])`. Return order is illustrative, not guaranteed
([fan-out/fan-in](https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-fan-in-fan-out)).

Process multiple items in parallel, then aggregate results:

```python
@bp.orchestration_trigger(context_name="context")
def parallel_processing(context: df.DurableOrchestrationContext):
    """Process multiple items in parallel."""
    items = context.get_input().get("items", [])

    # Fan-out: start all activities in parallel
    parallel_tasks = [
        context.call_activity("process_item", item)
        for item in items
    ]

    # Fan-in: wait for all to complete
    results = yield context.task_all(parallel_tasks)

    # Aggregate
    successful = sum(1 for r in results if r["status"] == "success")
    return {
        "total": len(items),
        "successful": successful,
        "failed": len(items) - successful,
        "results": results
    }


@bp.activity_trigger(input_name="item")
def process_item(item: dict) -> dict:
    """Process a single item."""
    import logging
    logging.info(f"Processing item: {item}")
    return {"item": item, "status": "success"}
```

## Monitor Pattern

Poll a long-running job on a durable timer until it finishes or a deadline passes. `create_timer` is a durable sleep — no compute is billed while the orchestration waits, and the timer survives host restarts.

<!-- diagram-id: monitor-pattern -->
```mermaid
flowchart TD
    accTitle: Durable monitor loop
    accDescr: Start with a job ID and deadline, check job status, and return when done or expired. While still running, wait on a durable timer before checking again.
    START["Start\nget job_id + deadline"] --> CHECK["call_activity\ncheck_job_status"]
    CHECK --> COND{"Done or expired?"}
    COND -->|"still running"| TIMER["create_timer\nsleep interval"]
    TIMER --> CHECK
    COND -->|"done / timeout"| RET["Return final status"]
    style CHECK fill:#0078d4,color:#fff
    style RET fill:#107c10,color:#fff
```

```python
from datetime import timedelta


@bp.orchestration_trigger(context_name="context")
def monitor_job(context: df.DurableOrchestrationContext):
    """Poll a job until it completes or the deadline passes."""
    job = context.get_input()
    job_id = job["job_id"]
    polling_seconds = job.get("polling_seconds", 30)

    # Use the deterministic orchestration clock, never datetime.now().
    deadline = context.current_utc_datetime + timedelta(hours=2)

    while context.current_utc_datetime < deadline:
        status = yield context.call_activity("check_job_status", job_id)
        if status["state"] in ("completed", "failed"):
            return {"job_id": job_id, "state": status["state"], "result": status.get("result")}

        # Durable sleep: schedule the next check, then yield until the timer fires.
        next_check = context.current_utc_datetime + timedelta(seconds=polling_seconds)
        yield context.create_timer(next_check)

    return {"job_id": job_id, "state": "timeout"}
```

Key points:

- Use `context.current_utc_datetime` for all time math — `datetime.now()` breaks determinism.
- `create_timer` schedules a durable timer; the orchestration is unloaded while it waits and costs no compute.
- For an open-ended monitor, call `context.continue_as_new(...)` instead of a `while` loop so the history stays small.

## Human Interaction Pattern

Pause a workflow until an external decision arrives — an approval, a signature, a callback — with a timeout so the workflow never blocks forever. The orchestrator waits on an external event and a durable timer at the same time and acts on whichever resolves first.

<!-- diagram-id: human-interaction-pattern -->
```mermaid
%%{init: {"sequence": {"width": 50, "actorMargin": 10, "diagramMarginX": 5, "noteMargin": 5}}}%%
sequenceDiagram
    accTitle: Approval event versus durable timeout
    accDescr: An orchestrator requests approval through an activity and waits for an external decision or a timer. If the event arrives first it applies the decision, approved or rejected; if the timer wins it escalates.
    participant Cli as C
    participant Orc as O
    participant Act as A
    Orc->>Act: request<br/>approval
    Note over Orc: Event wait +<br/>timeout timer
    alt event first
        Cli->>Orc: raise event
        Orc->>Act: apply decision
    else timer first
        Orc->>Orc: escalate
    end
```

**Reading key:** C = HTTP client, O = orchestrator, A = activity.
“request approval” is `request_approval`; the wait is
`wait_for_external_event` plus `create_timer` (timeout). “raise event” is
`raise_event` for `ApprovalEvent`; “apply decision” retains the approved/rejected
outcomes; “escalate” is the default timeout action. The activity action is
illustrative, not a required platform callback
([external events](https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-external-events),
[timers](https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-timers)).

```python
from datetime import timedelta


@bp.orchestration_trigger(context_name="context")
def approval_workflow(context: df.DurableOrchestrationContext):
    """Wait up to 72 hours for an approval decision, then act or escalate."""
    request = context.get_input()
    yield context.call_activity("request_approval", request)

    # Race the external event against a durable timeout.
    deadline = context.current_utc_datetime + timedelta(hours=72)
    approval_task = context.wait_for_external_event("ApprovalEvent")
    timeout_task = context.create_timer(deadline)

    winner = yield context.task_any([approval_task, timeout_task])

    if winner == approval_task:
        if not timeout_task.is_completed:
            timeout_task.cancel()  # release the pending durable timer
        decision = approval_task.result
        if decision.get("approved"):
            yield context.call_activity("apply_approval", request)
            return {"status": "approved", "approver": decision.get("approver")}
        return {"status": "rejected", "approver": decision.get("approver")}

    return {"status": "escalated", "reason": "approval timed out"}
```

Deliver the decision from any client function with `raise_event`, using the same event name the orchestrator waits on:

```python
@bp.route(route="orchestrations/{instance_id}/approve", methods=["POST"])
@bp.durable_client_input(client_name="client")
async def approve(req: func.HttpRequest, client: df.DurableOrchestrationClient) -> func.HttpResponse:
    """Deliver an approval decision to a waiting orchestration."""
    instance_id = req.route_params.get("instance_id")
    decision = req.get_json()  # e.g. {"approved": true, "approver": "alice"}

    await client.raise_event(instance_id, "ApprovalEvent", decision)
    return func.HttpResponse(status_code=202)
```

The `sendEventPostUri` from the starter response points at this same raise-event webhook, so external systems can resume the workflow without a custom endpoint.

## Check Orchestration Status

Use the status query URL from the starter response, or query programmatically:

```python
@bp.route(route="orchestrations/{instance_id}/status", methods=["GET"])
@bp.durable_client_input(client_name="client")
async def get_status(req: func.HttpRequest, client: df.DurableOrchestrationClient) -> func.HttpResponse:
    """Check the status of an orchestration instance."""
    instance_id = req.route_params.get("instance_id")
    status = await client.get_status(instance_id)

    if status is None:
        return func.HttpResponse(
            json.dumps({"error": "Instance not found"}),
            mimetype="application/json",
            status_code=404
        )

    return func.HttpResponse(
        json.dumps({
            "instance_id": status.instance_id,
            "runtime_status": status.runtime_status.name,
            "output": status.output,
            "created_time": status.created_time.isoformat() if status.created_time else None,
            "last_updated_time": status.last_updated_time.isoformat() if status.last_updated_time else None
        }),
        mimetype="application/json",
        status_code=200
    )
```

## See Also
- [HTTP API Patterns](http-api.md)
- [Queue Recipe](queue.md)
- [Durable Entities](durable-entities.md)
- [Platform: Durable Functions](../../../platform/durable-functions.md)

## Sources
- [Asynchronous HTTP operation tracking](https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-http-features#async-operation-tracking)
- [Query orchestration instances](https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-instance-management#query-instances)
- [Instances table for orchestration and entity status](https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-azure-storage-provider#instances-table-for-orchestration-and-entity-status)
- [Fan-out/fan-in](https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-fan-in-fan-out)
- [External events](https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-external-events)
- [Durable timers](https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-timers)
- [Orchestrator code constraints](https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-code-constraints)
- [Durable Functions Overview (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview)
- [Python v2 Programming Model (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [HTTP features: raise event webhooks (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-http-features)
- [Eternal orchestrations (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-eternal-orchestrations)
