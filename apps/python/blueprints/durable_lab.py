"""Durable Functions replay storm lab blueprint.

Demonstrates orchestration replay amplification with large history accumulation.
The orchestrator loops N times calling an activity. Without ContinueAsNew, history
grows continuously and replay duration increases nonlinearly.

Configuration via app settings:
- DurableLab__Iterations: number of activity calls per orchestration (default: 100)
- DurableLab__ContinueAsNewEvery: reset history every N iterations (0 = disabled)
"""

import azure.functions as func
import azure.durable_functions as df
import logging
import os
import time
import json

bp = df.Blueprint()
logger = logging.getLogger(__name__)


@bp.route(route="durable/start-replay-lab", methods=["POST"])
@bp.durable_client_input(client_name="client")
async def start_replay_lab(req: func.HttpRequest, client):
    """HTTP starter for the replay storm lab orchestrator."""
    iterations = int(os.environ.get("DurableLab__Iterations", "100"))
    continue_as_new_every = int(os.environ.get("DurableLab__ContinueAsNewEvery", "0"))

    body = req.get_body().decode("utf-8")
    try:
        payload = json.loads(body) if body else {}
    except json.JSONDecodeError:
        payload = {}

    instances_requested = payload.get("instances", 1)
    override_iterations = payload.get("iterations", iterations)
    override_continue = payload.get("continueAsNewEvery", continue_as_new_every)

    instance_ids = []
    for i in range(instances_requested):
        input_data = {
            "iterations": override_iterations,
            "continueAsNewEvery": override_continue,
            "batchIndex": 0,
            "instanceIndex": i,
        }
        instance_id = await client.start_new("replay_storm_orchestrator", None, input_data)
        instance_ids.append(instance_id)
        logger.info(
            "Started replay_storm_orchestrator instance %s (%d/%d), iterations=%d, continueEvery=%d",
            instance_id, i + 1, instances_requested, override_iterations, override_continue,
        )

    return func.HttpResponse(
        json.dumps({"started": len(instance_ids), "instanceIds": instance_ids}),
        status_code=202,
        mimetype="application/json",
    )


@bp.orchestration_trigger(context_name="context")
def replay_storm_orchestrator(context: df.DurableOrchestrationContext):
    """Orchestrator that calls an activity N times to build history.

    If continueAsNewEvery > 0, resets history periodically to demonstrate
    the recovery pattern.
    """
    input_data = context.get_input()
    total_iterations = input_data.get("iterations", 100)
    continue_every = input_data.get("continueAsNewEvery", 0)
    batch_index = input_data.get("batchIndex", 0)
    instance_index = input_data.get("instanceIndex", 0)

    # Calculate how many iterations to run in this batch
    completed_so_far = batch_index * continue_every if continue_every > 0 else 0
    remaining = total_iterations - completed_so_far

    if continue_every > 0:
        iterations_this_batch = min(continue_every, remaining)
    else:
        iterations_this_batch = remaining

    replay_start = time.monotonic()
    results = []

    for i in range(iterations_this_batch):
        global_index = completed_so_far + i
        result = yield context.call_activity(
            "replay_lab_activity",
            {"index": global_index, "instanceIndex": instance_index},
        )
        results.append(result)

        # Log replay metrics periodically
        if not context.is_replaying and (i + 1) % 50 == 0:
            elapsed = time.monotonic() - replay_start
            logger.info(
                "ReplayIteration instance=%d batch=%d iteration=%d/%d elapsed=%.0fms",
                instance_index,
                batch_index,
                global_index + 1,
                total_iterations,
                elapsed * 1000,
            )

    completed_so_far += iterations_this_batch

    # If continueAsNew is enabled and there are more iterations, reset history
    if continue_every > 0 and completed_so_far < total_iterations:
        new_input = {
            "iterations": total_iterations,
            "continueAsNewEvery": continue_every,
            "batchIndex": batch_index + 1,
            "instanceIndex": instance_index,
        }
        if not context.is_replaying:
            logger.info(
                "ContinueAsNew at iteration %d/%d, batch=%d, resetting history",
                completed_so_far, total_iterations, batch_index,
            )
        context.continue_as_new(new_input)
        return

    if not context.is_replaying:
        logger.info(
            "Orchestration complete: instance=%d total=%d batches=%d",
            instance_index, total_iterations, batch_index + 1,
        )

    return {
        "totalIterations": total_iterations,
        "batches": batch_index + 1,
        "finalBatchResults": len(results),
    }


@bp.activity_trigger(input_name="payload")
def replay_lab_activity(payload: dict) -> dict:
    """Simple activity that simulates work and returns timing info."""
    index = payload.get("index", 0)
    instance_index = payload.get("instanceIndex", 0)

    start = time.monotonic()
    # Simulate light work (5-15ms)
    total = 0
    for j in range(1000):
        total += j * j
    elapsed_ms = (time.monotonic() - start) * 1000

    if (index + 1) % 100 == 0:
        logger.info(
            "Activity completed: instance=%d index=%d elapsed=%.1fms",
            instance_index, index, elapsed_ms,
        )

    return {
        "index": index,
        "instanceIndex": instance_index,
        "elapsedMs": round(elapsed_ms, 1),
    }


@bp.route(route="durable/status/{instanceId}", methods=["GET"])
@bp.durable_client_input(client_name="client")
async def check_replay_status(req: func.HttpRequest, client):
    """Check the status of a replay storm orchestration instance."""
    instance_id = req.route_params.get("instanceId")
    status = await client.get_status(instance_id)

    if status is None:
        return func.HttpResponse(
            json.dumps({"error": "Instance not found"}),
            status_code=404,
            mimetype="application/json",
        )

    return func.HttpResponse(
        json.dumps({
            "instanceId": status.instance_id,
            "runtimeStatus": status.runtime_status.value if status.runtime_status else None,
            "createdTime": str(status.created_time) if status.created_time else None,
            "lastUpdatedTime": str(status.last_updated_time) if status.last_updated_time else None,
            "output": status.output,
        }),
        status_code=200,
        mimetype="application/json",
    )
