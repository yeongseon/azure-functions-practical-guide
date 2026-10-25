---
content_sources:

  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
  diagrams:
    - id: python-language-guide
      type: flowchart
      source: self-generated
      justification: Flow view of python language guide, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
---
# Python Language Guide

Python is the **reference implementation** in this guide and currently contains the most complete end-to-end content set.

If you are new to Azure Functions, this track is the fastest way to understand hosting plans, deployment workflows, and production operations with concrete examples.

<!-- diagram-id: python-language-guide -->
```mermaid
flowchart TD
    A[Tutorial Overview]
    A --> B[Consumption Track]
    A --> C[Flex Consumption Track]
    A --> D[Premium Track]
    A --> E[Dedicated Track]
    A --> F[Recipes]
    A --> G[Runtime and Reference]
```

!!! tip "Architecture first"
    Before diving into Python-specific details, review [Platform](../../platform/index.md) for language-agnostic guidance on hosting, scaling, networking, reliability, and security.

## Why Python is the reference track

- Full tutorial coverage across **all four hosting plans**.
- Complete recipe set for common Azure integrations.
- Dedicated runtime/reference docs for operational concerns.
- Backed by a populated reference app in `apps/python/`.

## Start here

1. Choose your hosting plan in [Tutorial Overview & Plan Chooser](tutorial/index.md).
2. Follow one full tutorial track from local run through CI/CD.
3. Use recipes to add integrations (Storage, Cosmos DB, Key Vault, Event Grid, and more).
4. Keep runtime/reference docs open during production hardening.

## What's Covered

| Area | Document | Scope |
|------|----------|-------|
| Tutorial | [Overview & Plan Chooser](tutorial/index.md) | Select Consumption, Flex Consumption, Premium, or Dedicated |
| Tutorial track | [Consumption (Y1)](tutorial/consumption/01-local-run.md) | 7-step flow for classic serverless |
| Tutorial track | [Flex Consumption (FC1)](tutorial/flex-consumption/01-local-run.md) | 7-step flow for modern default serverless |
| Tutorial track | [Premium (EP)](tutorial/premium/01-local-run.md) | 7-step flow for always-warm/VNet scenarios |
| Tutorial track | [Dedicated (App Service)](tutorial/dedicated/01-local-run.md) | 7-step flow for fixed-capacity hosting |
| Recipes | [Recipes Index](recipes/index.md) | 11 practical implementation recipes |
| Runtime model | [v2 Programming Model](v2-programming-model.md) | Decorators, function app structure, binding patterns |
| Runtime internals | [Python Runtime](python-runtime.md) | Python worker behavior and version/runtime specifics |
| CLI | [CLI Cheatsheet](cli-cheatsheet.md) | `az` and `func` operational commands |
| Host settings | [host.json Reference](host-json.md) | Concurrency, retry, logging, and extension settings |
| Configuration | [Environment Variables](environment-variables.md) | Key app and platform environment settings |
| Limits | [Platform Limits](platform-limits.md) | Timeouts, payloads, scaling, and service constraints |
| Diagnostics | [Troubleshooting](troubleshooting.md) | Common failures and troubleshooting flow |

## Tutorial structure at a glance

The tutorial library provides **4 plans × 7 tutorials = 28 tutorials**.

Each plan follows the same sequence:

1. Run locally
2. First deploy
3. Configuration
4. Logging and monitoring
5. Infrastructure as code
6. CI/CD
7. Extending with triggers

This consistent sequence helps teams compare plan behavior without relearning the workflow.

## Recipes coverage

The Python recipes section contains production-oriented patterns for:

- HTTP API design and authentication
- Storage integrations (Blob, Queue)
- Data integrations (Cosmos DB)
- Security patterns (Managed Identity, Key Vault)
- Event and workflow patterns (Timer, Event Grid, Durable Functions)
- Edge/network concerns (custom domains and certificates)

See [Recipes Index](recipes/index.md) for full links and category grouping.

## Reference application

The Python guide is backed by a working reference app:

- [`apps/python/`](https://github.com/yeongseon/azure-functions-practical-guide/tree/main/apps/python)

Use it to validate tutorial steps, copy implementation patterns, and test hosting-plan-specific behavior.

### Default functions and optional trigger registration

The reference entrypoint indexes `health`, `info`, `log_levels`, `external_dependency`,
`replay_storm_orchestrator`, `replay_lab_activity`, and `eventhub_lag_processor` by
default. The existing Durable and Event Hubs listeners still require their storage
and Event Hubs configuration; this is not an HTTP-only app. Diagnostic, exception,
and Durable starter/status HTTP routes remain separately gated by
`LAB_ENDPOINTS_ENABLED=true` and require function keys in Azure.

The following listeners are **not registered by default**. Select only the variant
you need by setting its switch to the exact string `true` in local
`local.settings.json` under `Values` and separately in the Azure app settings before
publishing. Local settings are not automatically published. Restart the host after
changing a switch; merely copying a blueprint file does not register it.

| Variant | Registration switch | Expected indexed name | Required setup before listener startup |
|---|---|---|---|
| Queue backlog lab | `QUEUE_LAB_ENABLED=true` | `queue_processor` (`queueTrigger`) | `QueueStorage` connection or identity-based connection settings with queue access; queue `work-items` |
| Missed-schedules lab | `TIMER_LAB_ENABLED=true` | `timer_lab` (`timerTrigger`) | Host storage access and `TIMER_LAB_SCHEDULE=0 */2 * * * *` |
| General Timer tutorial/recipe | `SCHEDULED_TRIGGER_ENABLED=true` | `scheduled_cleanup` (`timerTrigger`) | Host storage access; fixed five-minute schedule |
| Blob tutorial/recipe | `BLOB_TRIGGER_ENABLED=true` | `process_blob` (`blobTrigger`) | `AzureWebJobsStorage` Blob access, `uploads`/`processed` containers, and an Event Grid subscription in Azure |

These switches perform explicit blueprint registration in `function_app.py`; no
module discovery is involved. When using the checked-in app, use the switch
**instead of** adding a second manual `register_blueprint` call for the same
blueprint. Tutorials that define their own functions/blueprints still need their
documented registration step; their function names may differ from this table.

From the repository root, run the focused SDK smoke checks:

```bash
uv run --python 3.11 --with-requirements apps/python/requirements.txt --with pytest \
    python -m pytest tests/test_trigger_registration.py -q
```

The tests index the real entrypoint with each selection and check names and binding
metadata. This is local/static registration evidence, **not** proof of storage
permissions, Event Grid delivery, a healthy listener, or an Azure lab execution.
With dependencies installed, Core Tools and local storage configured, run
`func start --verbose` from `apps/python/`. Require the selected name/type in the
`Functions:` list and resolve indexing/listener errors before generating work.
For a registration-only check, other already-registered listeners can be disabled
locally with `AzureWebJobs.<function-name>.Disabled=true`; do not disable the
selected function when checking its actual execution.

After publishing, verify the deployed function list and startup logs separately,
then collect new execution evidence before drawing scaling or scheduling
conclusions. Local indexing does not revalidate the historical lab runs. After the
experiment, remove/set the selected switch to `false` in Azure and locally, restart
the host, and clean up the lab resources.

## Microsoft Learn alignment

This guide aligns to the official Python developer documentation.

!!! note "Runtime and feature truth source"
    If you find any mismatch between this guide and official service behavior, treat Microsoft Learn as authoritative and open a docs issue in this repository.

## Cross-language context

If your team supports multiple stacks, compare Python with:

- [Node.js guide](../nodejs/index.md)
- [.NET guide](../dotnet/index.md)
- [Java guide](../java/index.md)

Use [Language Guides Overview](../index.md) for a side-by-side worker/programming model matrix.

## See Also

- [Language Guides Overview](../index.md)
- [Platform: Architecture](../../platform/architecture/index.md)
- [Platform: Hosting](../../platform/hosting.md)
- [Operations: Deployment](../../operations/deployment.md)
- [Operations: Monitoring](../../operations/monitoring.md)

## Sources

- [Python reference application (`apps/python/`)](https://github.com/yeongseon/azure-functions-practical-guide/tree/main/apps/python)
- [Azure Functions Python developer guide (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Azure Functions hosting options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [Flex Consumption plan](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan)
