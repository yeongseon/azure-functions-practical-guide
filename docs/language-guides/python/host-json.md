# host.json Reference

The `host.json` file configures the Azure Functions runtime behaviour. It lives in the root of your function app (same directory as `function_app.py`) and applies to all functions in the app. This reference covers the most important settings for Python function apps.

## Complete Annotated Example

```json
{
  "version": "2.0",

  "logging": {
    "logLevel": {
      "default": "Information",
      "Host.Results": "Error",
      "Function": "Information",
      "Host.Aggregator": "Trace"
    },
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20,
        "excludedTypes": "Request;Exception"
      },
      "enableLiveMetrics": true,
      "httpAutoCollectionOptions": {
        "enableHttpTriggerExtendedInfoCollection": true,
        "enableW3CDistributedTracing": true,
        "enableResponseHeaderInjection": true
      }
    }
  },

  "extensions": {
    "http": {
      "routePrefix": "api",
      "maxOutstandingRequests": 200,
      "maxConcurrentRequests": 100,
      "dynamicThrottlesEnabled": false
    },
    "queues": {
      "maxPollingInterval": "00:00:02",
      "visibilityTimeout": "00:00:30",
      "batchSize": 16,
      "maxDequeueCount": 5,
      "newBatchThreshold": 8
    }
  },

  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  },

  "functionTimeout": "00:05:00",

  "concurrency": {
    "dynamicConcurrencyEnabled": true,
    "snapshotPersistenceEnabled": true
  }
}
```

## Key Settings

### version (Required)

```json
{
  "version": "2.0"
}
```

Always set to `"2.0"` for Azure Functions v4 runtime. This is the only supported version for the v2 Python programming model.

### extensionBundle (Required)

```json
{
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
```

The extension bundle provides pre-compiled binding extensions (Cosmos DB, Storage, Event Grid, etc.) without requiring you to install them individually. The version range `[4.*, 5.0.0)` means any 4.x version but not 5.x.

> **Important:** Without the extension bundle, non-HTTP bindings will not work. HTTP triggers work without it since they are part of the core runtime.

### functionTimeout

```json
{
  "functionTimeout": "00:05:00"
}
```

Maximum execution time for a single function invocation. The format is `hh:mm:ss`.

| Plan | Default | Minimum | Maximum |
|------|---------|---------|---------|
| **Consumption** | 5 minutes | 1 second | 10 minutes |
| **Flex Consumption** | 30 minutes | 1 second | Unlimited (`-1`) |
| **Premium** | 30 minutes | 1 second | Unlimited (set `functionTimeout` to `-1`) |
| **Dedicated** | 30 minutes | 1 second | Unlimited |

For the Consumption plan, if a function exceeds the timeout, the host terminates the process. Flex Consumption defaults to 30 minutes and supports unbounded execution (`-1`); if a bounded timeout is set, the host terminates the process when it is exceeded.

```json
{
  "functionTimeout": "00:10:00"
}
```

> **Tip:** Set the timeout to the maximum your plan allows, then handle timeouts gracefully in your code. For long-running operations, consider Durable Functions instead.

### logging

Control log verbosity and Application Insights behaviour:

```json
{
  "logging": {
    "logLevel": {
      "default": "Information",
      "Host.Results": "Error",
      "Function": "Information",
      "Function.my_func": "Debug"
    }
  }
}
```

| Category | Controls | Recommended Level |
|----------|----------|-------------------|
| `default` | All log sources not explicitly configured | `Information` |
| `Host.Results` | Function execution results (success/failure) | `Error` (reduces noise) |
| `Function` | All function-level logs | `Information` |
| `Function.<function_name>` | Logs for a specific function | `Debug` (only when troubleshooting) |
| `Host.Aggregator` | Aggregated metrics | `Trace` or `Information` |

### logging.applicationInsights.samplingSettings

Control how much telemetry is sent to Application Insights:

```json
{
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20,
        "excludedTypes": "Request;Exception"
      }
    }
  }
}
```

| Setting | Default | Description |
|---------|---------|-------------|
| `isEnabled` | `true` | Enable adaptive sampling |
| `maxTelemetryItemsPerSecond` | `20` | Target telemetry rate per second per instance |
| `excludedTypes` | `""` | Telemetry types to never sample. Options: `Dependency`, `Event`, `Exception`, `PageView`, `Request`, `Trace` |

> **Cost Tip:** Set `excludedTypes` to `"Request;Exception"` to ensure you never lose error data, while allowing traces and dependencies to be sampled. See [Cost Optimization](../../operations/configuration.md).

### extensions.http

Configure HTTP trigger behaviour:

```json
{
  "extensions": {
    "http": {
      "routePrefix": "api",
      "maxOutstandingRequests": 200,
      "maxConcurrentRequests": 100,
      "dynamicThrottlesEnabled": false
    }
  }
}
```

| Setting | Default | Description |
|---------|---------|-------------|
| `routePrefix` | `"api"` | URL prefix for all HTTP functions. Set to `""` to remove the `/api` prefix |
| `maxOutstandingRequests` | `200` | Max pending requests at any given time |
| `maxConcurrentRequests` | `100` | Max HTTP functions executing in parallel per instance |
| `dynamicThrottlesEnabled` | `false` | Check system performance counters and reject requests when thresholds are exceeded |

To remove the `/api` prefix (so routes are `https://your-func.azurewebsites.net/health` instead of `https://your-func.azurewebsites.net/api/health`):

```json
{
  "extensions": {
    "http": {
      "routePrefix": ""
    }
  }
}
```

### extensions.queues

Configure Queue trigger behaviour (see [Queue recipe](recipes/queue.md)):

```json
{
  "extensions": {
    "queues": {
      "maxPollingInterval": "00:00:02",
      "visibilityTimeout": "00:00:30",
      "batchSize": 16,
      "maxDequeueCount": 5,
      "newBatchThreshold": 8
    }
  }
}
```

### concurrency

Enable dynamic concurrency for automatic tuning:

```json
{
  "concurrency": {
    "dynamicConcurrencyEnabled": true,
    "snapshotPersistenceEnabled": true
  }
}
```

When enabled, the runtime automatically adjusts concurrency limits per trigger type based on observed performance. `snapshotPersistenceEnabled` persists the learned concurrency settings across restarts.

## Minimal host.json

The minimum viable `host.json` for an HTTP-only Python function app:

```json
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
```

## Local vs. Production Differences

The `host.json` file is deployed with your code and applies in both local and production environments. For settings that should differ between environments, use app settings (environment variables) and reference them in your code rather than putting environment-specific values in `host.json`.

## See Also
- [Environment Variables](environment-variables.md)
- [Observability](../../operations/monitoring.md)
- [Cost Optimization](../../operations/configuration.md)

## Sources
- [host.json Reference (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-host-json)
