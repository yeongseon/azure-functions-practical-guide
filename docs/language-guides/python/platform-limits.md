---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/supported-languages
---
# Platform Limits for Python

Use the shared [Platform Limits](../../reference/platform-limits.md) as the authoritative reference for plan/OS instance ceilings, deployment slots, execution timeouts, HTTP boundaries, connections, and storage. This page adds Python sizing guidance instead of maintaining a second quota table.

## Python Hosting Constraints

Python function apps run on **Linux only** in Azure. A Windows Consumption quota is not applicable to Python, even though Windows and Linux Consumption both use Y1. Use the Linux column in the shared reference and the current [supported-language policy](https://learn.microsoft.com/en-us/azure/azure-functions/supported-languages).

Python 3.12 is the last Python version added to Linux Consumption. For a new serverless app, start with [Flex Consumption](tutorial/flex-consumption/01-local-run.md); for an existing Consumption app, use the shared [retirement and migration decision path](../../reference/platform-limits.md#runtime-support-and-linux-consumption-migration). Check target-region runtime availability rather than treating the version pinned in a tutorial as a support matrix.

## Sizing Considerations

- Budget memory for the Functions host, imported packages, worker processes, and concurrent invocations together. Idle-worker figures vary by dependencies and runtime; the former fixed estimates were illustrative, not measured evidence or an official allowance.
- Tune worker processes and concurrency with workload profiling; increasing workers does not increase instance memory or the hosting-plan scale ceiling. See [Scaling](../../platform/scaling.md).
- Reuse HTTP and database clients across invocations, with bounded pools. “Unbounded” in a hosting connection table does not remove socket, port, memory, or downstream limits.
- Keep temporary files disposable. Distinguish scratch space from host storage, deployment packages, and application data; use the shared reference's storage qualifications and the [deployment plan/OS matrix](../../operations/deployment.md#package-configuration-by-plan-and-os).

## See Also

- [Platform Limits — shared reference](../../reference/platform-limits.md)
- [Python Runtime](python-runtime.md)
- [Scaling](../../platform/scaling.md)
- [Tutorial Plan Selector](tutorial/index.md)
- [Hosting Plans](../../platform/hosting.md)

## Sources

- [Functions scale and service limits](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [Supported languages](https://learn.microsoft.com/en-us/azure/azure-functions/supported-languages)
- [Python scale and performance](https://learn.microsoft.com/en-us/azure/azure-functions/python-scale-performance-reference)
- [Connection management](https://learn.microsoft.com/en-us/azure/azure-functions/manage-connections)
