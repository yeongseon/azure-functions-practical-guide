# Cold Start

This guide explains cold start behavior in Azure Functions and practical mitigation techniques per hosting plan.
Cold start is startup latency after an app has no warm instance available.

!!! tip "Platform Guide"
    For scaling architecture and plan comparison, see [Scaling](../platform/scaling.md).

!!! tip "Language Guide"
    For Python deployment specifics, see the [Python Tutorial](../language-guides/python/tutorial/index.md).

## What causes cold start

Cold start usually combines several phases:

1. Worker instance allocation.
2. Functions host startup.
3. Language worker startup.
4. Application initialization (dependency loading, configuration reads, SDK clients).

Non-HTTP triggers can also experience startup latency when scale controller activates new workers.

## Plan-specific mitigation options

| Hosting plan | Mitigation controls |
|---|---|
| Consumption | Optimize startup path, reduce package size, avoid heavy initialization |
| Flex Consumption | Configure always-ready instances for selected functions or app behavior |
| Premium | Use always-ready and pre-warmed instances |
| Dedicated (App Service Plan) | Enable Always On to keep workers active |

### Flex Consumption (FC1)

Flex Consumption supports always-ready instances to reduce cold-start frequency.
Use this when low-latency response is required without moving to Premium.

### Premium (EP)

Premium supports always-ready instances and pre-warmed capacity for scale-out events.
This is the strongest built-in mitigation for latency-sensitive serverless workloads.

Premium always-ready and pre-warmed settings are configured in the Azure portal or with ARM/Bicep templates (CLI support varies by API version):

```bash
# Premium always-ready/pre-warmed configuration:
# Use Azure portal (Function App > Scale out)
# or ARM/Bicep properties for the plan.
```

### Dedicated plan

Enable Always On so the app remains loaded:

```bash
az functionapp config set \
    --resource-group <resource-group> \
    --name <function-app-name> \
    --always-on true
```

## Startup optimization techniques

Apply these regardless of hosting plan:

- Keep deployment artifact small.
- Remove unused dependencies.
- Delay expensive initialization until first use where safe.
- Reuse SDK clients and HTTP connections.
- Avoid synchronous network calls in module initialization.

## Dependency and package optimization

Operationally, dependency volume and native package loading often dominate startup time.

Recommended practices:

- Audit dependencies quarterly and remove unused packages.
- Prefer lighter libraries for common operations.
- Use run-from-package deployment for immutable and consistent startup files.
- Keep extension bundle and worker runtime versions current and supported.

## Warmup and traffic shaping

For plans without strong always-ready guarantees, use conservative warmup patterns:

- Scheduled health ping to keep app active where appropriate.
- Gradual traffic ramp during deployments.
- Pre-deployment synthetic checks before traffic cutover.

!!! note "Cost tradeoff"
    Warmup strategies can increase baseline cost. Tune against your latency SLO and budget.

## Measuring cold start impact

Track cold-start symptoms with KQL and metrics:

```kql
requests
| where timestamp > ago(24h)
| summarize p95_duration=percentile(duration, 95), p99_duration=percentile(duration, 99) by bin(timestamp, 5m)
| render timechart
```

Correlate duration spikes with scale-out and instance changes to separate code regressions from startup events.

## Operational decision flow

1. If latency SLO is moderate, optimize startup path first.
2. If p95 remains unstable, enable plan-native warm capacity.
3. If strict low-latency is mandatory, use Premium or Dedicated with warm strategy.

## See Also

- [Monitoring](monitoring.md)
- [Deployment](deployment.md)
- [Platform Hosting](../platform/hosting.md)

## Sources

- [Azure Functions hosting options and scaling](https://learn.microsoft.com/azure/azure-functions/functions-scale)
- [Flex Consumption plan for Azure Functions](https://learn.microsoft.com/azure/azure-functions/flex-consumption-plan)
- [Azure Functions Premium plan](https://learn.microsoft.com/azure/azure-functions/functions-premium-plan)
- [Improve performance and reliability of Azure Functions](https://learn.microsoft.com/azure/azure-functions/performance-reliability)
