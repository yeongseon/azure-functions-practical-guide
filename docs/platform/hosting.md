# Hosting Plans

Choosing a hosting plan is the most important Azure Functions platform decision. It controls scale behavior, cold start profile, networking options, limits, and baseline cost.

## Hosting plans at a glance

Azure Functions supports four main hosting models:

| Plan | Best for | Scale profile | Cold start profile |
|---|---|---|---|
| Consumption | Bursty, lower-cost serverless workloads | 0 to platform limit | Present after idle |
| Flex Consumption | New serverless apps needing VNet + high scale | 0 to high scale ceiling, per-function scaling | Reduced with always-ready |
| Premium | Low-latency, enterprise integration | Elastic with warm baseline | Eliminated for warm baseline |
| Dedicated (App Service Plan) | Predictable, fixed-capacity workloads | Manual/autoscale by plan rules | None (always on) |

!!! tip "Decision rule"
    Start with Flex Consumption for most new serverless workloads, then choose Premium when you need permanently warm behavior and App Service premium features such as deployment slots.

## Consumption plan (classic)

Consumption is the original serverless model.

### Key characteristics

- Scale to zero when idle.
- Billed per execution and execution resources.
- No VNet integration.
- Typical default function timeout: **5 minutes**, maximum **10 minutes**.

### Design trade-offs

Use Consumption when:

- traffic is sporadic,
- private networking is not required,
- and occasional cold starts are acceptable.

Avoid Consumption when you require private-only backend access or strict latency SLOs.

## Flex Consumption plan

Flex Consumption combines serverless economics with modern networking and scaling controls.

### Key characteristics

- Scale to zero when idle.
- Per-function (or function-group) scaling model.
- Supports VNet integration and private endpoints.
- One Function App per plan.
- Linux-based runtime model.

### Critical platform facts

- **No Kudu/SCM site** is available.
- **Identity-based storage is required** for host storage configuration.
- Blob trigger must use **Event Grid source** on Flex; standard polling blob trigger is not supported.
- Default function timeout is **30 minutes**; maximum is **unbounded**.

### Flex memory profiles

At creation time, you choose an instance memory size profile (for example 512 MB, 2048 MB, 4096 MB). This choice affects throughput density and cost.

### Always-ready behavior

Flex supports always-ready instances per function group to reduce startup latency while retaining scale-to-zero for non-baseline traffic.

## Premium plan

Premium (Elastic Premium) is designed for consistently low latency and enterprise workloads.

### Key characteristics

- Instances are **permanently warm** at configured minimum count.
- Elastic scale beyond baseline.
- Supports VNet integration, private endpoints, and advanced App Service capabilities.
- No practical execution timeout ceiling for most long-running patterns (host settings still apply).

### Premium is a fit when

- cold start must be eliminated,
- private networking is mandatory,
- long-running executions are expected,
- and you need features like deployment slots.

## Dedicated plan (App Service Plan)

Dedicated runs Functions on pre-provisioned App Service compute.

### Key characteristics

- Fixed VM allocation (you pay regardless of invocation volume).
- Full App Service plan capabilities.
- Manual/autoscale rules at App Service layer.
- Suitable for shared hosting with existing web workloads.

### Dedicated is a fit when

- you already operate App Service capacity,
- predictable fixed spend is preferred,
- and always-on behavior is required.

## Capability matrix

| Capability | Consumption | Flex Consumption | Premium | Dedicated |
|---|---|---|---|---|
| Scale to zero | Yes | Yes | No | No |
| VNet integration | No | Yes | Yes | Yes |
| Inbound private endpoint | No | Yes | Yes | Yes |
| Deployment slots | No | No | Yes | Yes |
| Kudu/SCM | Yes | No | Yes | Yes |
| Apps per plan | Multiple | One | Multiple | Multiple |

## Timeout reference (design-time)

| Plan | Default timeout | Maximum timeout |
|---|---:|---:|
| Consumption (classic) | 5 minutes | 10 minutes |
| Flex Consumption | 30 minutes | Unbounded |
| Premium | 30 minutes (common default) | Unbounded |
| Dedicated | 30 minutes (common default) | Unbounded |

!!! note
    HTTP responses still have platform front-end constraints independent of background function timeout. Design long-running HTTP operations using async patterns.

## CLI examples (plan creation/selection)

Use long-form flags only.

```bash
# Consumption Function App
az functionapp create \
  --resource-group "$RG" \
  --name "$APP_NAME" \
  --storage-account "$STORAGE_NAME" \
  --consumption-plan-location "$LOCATION" \
  --runtime node \
  --functions-version 4
```

```bash
# Flex Consumption Function App
az functionapp create \
  --resource-group "$RG" \
  --name "$APP_NAME" \
  --storage-account "$STORAGE_NAME" \
  --flexconsumption-location "$LOCATION" \
  --runtime python \
  --runtime-version 3.12
```

```bash
# Premium plan + Function App
az functionapp plan create \
  --resource-group "$RG" \
  --name "$PLAN_NAME" \
  --location "$LOCATION" \
  --sku EP1 \
  --is-linux

az functionapp create \
  --resource-group "$RG" \
  --name "$APP_NAME" \
  --plan "$PLAN_NAME" \
  --storage-account "$STORAGE_NAME" \
  --runtime dotnet-isolated \
  --functions-version 4
```

## Hosting decision workflow

1. Decide if scale-to-zero is required.
2. Decide if private networking is required.
3. Decide if cold-start elimination is required.
4. Decide if one-app-per-plan (Flex) is acceptable.
5. Validate timeout requirements against plan limits.

If you need both serverless cost behavior and private networking, Flex is usually the first candidate.

## Anti-patterns

- Choosing Consumption, then requiring private-only data paths later.
- Choosing Dedicated for highly sporadic workloads.
- Ignoring Flex one-app-per-plan constraint in multi-app tenancy designs.
- Assuming Kudu is available on Flex.

!!! tip "Language Guide"
    For Python-specific deployment nuances on each plan, see [Python Runtime](../language-guides/python/python-runtime.md).

## See also

- [Architecture](architecture.md)
- [Scaling](scaling.md)
- [Networking](networking.md)
- [Microsoft Learn: Scale and hosting](https://learn.microsoft.com/azure/azure-functions/functions-scale)
- [Microsoft Learn: Flex Consumption plan](https://learn.microsoft.com/azure/azure-functions/flex-consumption-plan)
- [Microsoft Learn: Premium plan](https://learn.microsoft.com/azure/azure-functions/functions-premium-plan)
