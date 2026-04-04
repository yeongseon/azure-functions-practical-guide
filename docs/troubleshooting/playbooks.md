# Azure Functions Incident Playbooks

These scenario playbooks are for active incidents.
Use them as evidence-driven workflows: **What you observe → Hypotheses → Checks → Interpretation → Fix**.

## Prerequisites
- Access to Azure CLI, Application Insights, and Log Analytics.
- Subscription and app context prepared.

```bash
RG="rg-myapp-prod"
APP_NAME="func-myapp-prod"
SUBSCRIPTION_ID="<subscription-id>"
WORKSPACE_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

!!! tip "Operations Guide"
    For monitoring setup and alert configuration, see [Monitoring](../operations/monitoring.md) and [Alerts](../operations/alerts.md).

!!! tip "Troubleshooting workflow"
    Start with [First 10 Minutes](first-10-minutes.md), follow [Methodology](methodology.md), pull focused queries from [KQL Query Library](kql.md), and map hands-on practice from [Lab Guides](lab-guides.md).

## Functions not executing

### What you may observe
- Events arrive, but invocation count is near zero.
- App appears running, but trigger output is absent.

### Likely hypotheses
- Function disabled via app setting.
- Trigger connection setting invalid.
- Host listener failed to initialize.

### What to check first
- Confirm the target function is enabled.
- Confirm recent host traces include listener startup for the trigger.
- Correlate queue/event activity with invocation count over the same 30-minute window.

### Check in Portal
- **Function App → Functions → _<FunctionName>_**: verify **Enabled** = `On`.
- **Function App → Monitor**: verify invocation timeline is not flat while events are incoming.
- **Application Insights → Logs**: verify listener startup traces exist after the last restart.

### Check with Azure CLI
```bash
az functionapp function list --name "$APP_NAME" --resource-group "$RG" --output table
az functionapp config appsettings list --name "$APP_NAME" --resource-group "$RG" --output table
az monitor log-analytics query \
  --workspace "$WORKSPACE_ID" \
  --analytics-query "traces | where timestamp > ago(30m) | where cloud_RoleName =~ '$APP_NAME' | where message has_any ('disabled','listener','Host started') | order by timestamp desc" \
  --output table
```

### Example Output
```text
Name             Trigger    IsDisabled
---------------  ---------  ----------
QueueProcessor   queue      true
HttpPing         http       false

Name                                              Value
------------------------------------------------  ----------------------------------------------------------------
AzureWebJobs.QueueProcessor.Disabled              true
AzureWebJobsStorage                               DefaultEndpointsProtocol=https;AccountName=***;AccountKey=***

Timestamp                    Message
---------------------------  ---------------------------------------------------------------------------------
2024-01-15T10:30:05.000000Z  Listener for 'QueueTrigger' was unable to start. Connection refused.
2024-01-15T10:30:00.000000Z  Function 'QueueProcessor' is disabled via app setting 'AzureWebJobs.QueueProcessor.Disabled'.
```

### How to interpret the results
| Signal | Normal | Abnormal | Interpretation |
|---|---|---|---|
| Function enabled state | `IsDisabled=false` | `IsDisabled=true` | Disabled function prevents trigger execution regardless of incoming events. |
| Listener traces | `Listener started for function` appears after restart | `unable to start` or no listener trace | Trigger pipeline is not active. |
| Invocations vs queue activity | Invocations rise with queue activity | 0 invocations in 30 minutes with active queue | Trigger path is broken, not just low traffic. |

### Sample log patterns
```text
# Abnormal: Function disabled
[2024-01-15T10:30:00Z] Function 'QueueProcessor' is disabled via app setting 'AzureWebJobs.QueueProcessor.Disabled'

# Abnormal: Listener startup failure
[2024-01-15T10:30:05Z] Listener for 'QueueTrigger' was unable to start. Microsoft.WindowsAzure.Storage: Connection refused.

# Normal: Healthy listener
[2024-01-15T10:30:00Z] Listener started for function 'QueueProcessor'
[2024-01-15T10:30:00Z] Host started (234ms)
```

### KQL queries
- Query 1 summarizes invocation volume, failures, and p95 duration by function to quickly spot non-executing triggers.
  For the full query, see [KQL Query Library → 1) Function execution summary (success/failure/duration)](kql.md#1-function-execution-summary-successfailureduration).

- Query 2 inspects host/listener lifecycle traces to validate startup and disabled-listener evidence.
  For the full query, see [KQL Query Library → 8) Host startup/shutdown events](kql.md#8-host-startupshutdown-events).

### Example KQL result
| FunctionName | Invocations | Failures | FailureRate% | P95Ms |
|---|---|---|---|---|
| Functions.QueueProcessor | 0 | 0 | 0 | 0 |
| Functions.HttpPing | 1245 | 2 | 0.16 | 180 |

FailureRate% is derived as `Failures / Invocations * 100`.

### Common misdiagnoses
- Assuming a code bug when the function is simply disabled.
- Scaling out first, even though listener initialization is failing.

### Next steps
- Remove incorrect `AzureWebJobs.<FunctionName>.Disabled` settings.
- Fix trigger connection settings and restart the app.
- If symptoms began after deployment, roll back to the last known good artifact and re-test listener startup.

### Related labs
- [storage-access-failure](lab-guides.md#2-storage-access-failure-lab)

## High latency / slow responses

### What you may observe
- P95 latency spikes and timeout rate increases.
- Failures appear during traffic surges or after idle periods.

### Likely hypotheses
- Cold start delays.
- Slow downstream API or database.
- Concurrency saturation.

### What to check first
- Compare latency spikes with host startup traces.
- Verify dependency p95 by target before tuning function code.
- Confirm whether latency regresses mostly on first invocation after idle.

### Check in Portal
- **Application Insights → Performance → Operations**: inspect p95/p99 by function operation.
- **Application Insights → Dependencies**: check top slow targets and failure rates.
- **Function App → Diagnose and solve problems**: review cold start and performance detectors.

### Check with Azure CLI
```bash
az monitor metrics list \
  --resource "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.Web/sites/$APP_NAME" \
  --metric "AverageResponseTime" "Requests" "Http5xx" \
  --interval PT1M \
  --aggregation Average Total \
  --offset 1h \
  --output table

az monitor log-analytics query \
  --workspace "$WORKSPACE_ID" \
  --analytics-query "dependencies | where timestamp > ago(1h) | where cloud_RoleName =~ '$APP_NAME' | summarize p95=percentile(duration,95), failures=countif(success==false) by target" \
  --output table
```

### Example Output
```text
MetricName            TimeGrain  Average   Total
--------------------  ---------  --------  ------
AverageResponseTime   PT1M       421       0
AverageResponseTime   PT1M       16620     0
Requests              PT1M       0         892
Http5xx               PT1M       0         74

target                          p95      failures
------------------------------  -------  --------
api.partner.internal            28400    116
sql-prod.database.windows.net   9100     12
```

### How to interpret the results
| Signal | Normal | Abnormal | Interpretation |
|---|---|---|---|
| Host start trace | `Host started (200ms)` | `Host started (15000ms)` | Cold start is contributing materially to end-user latency. |
| Dependency p95 | < 500 ms for critical calls | Multi-second p95 on one target | Downstream dependency likely bottleneck. |
| Request latency distribution | Stable p95 with occasional spikes | Sustained p95 spikes with increased 5xx | Latency is systemic, not a one-off transient. |

### Sample log patterns
```text
# Abnormal: severe cold start
[2024-01-15T11:05:10Z] Host started (12543ms)

# Abnormal: dependency timeout
[2024-01-15T11:05:20Z] Executed 'Functions.HttpHandler' (Failed, Duration=30211ms)
[2024-01-15T11:05:20Z] Dependency call failed: target=api.partner.internal, error=TimeoutException

# Normal: warm startup and stable dependency
[2024-01-15T11:20:00Z] Host started (200ms)
[2024-01-15T11:20:01Z] Dependency call success: target=api.partner.internal, duration=84ms
```

### KQL queries
- Query 1 trends request latency and failure counts over time by function to isolate sustained response slowness.
  For the full query, see [KQL Query Library → 1) Function execution summary (success/failure/duration)](kql.md#1-function-execution-summary-successfailureduration).

- Query 2 summarizes dependency failure/latency by target to identify downstream bottlenecks.
  For the full query, see [KQL Query Library → 4) Dependency call failures](kql.md#4-dependency-call-failures).

### Example KQL result
| target | Calls | Failed | FailureRate% | P95Ms |
|---|---|---|---|---|
| api.partner.internal | 612 | 116 | 18.95 | 28400 |
| sql-prod.database.windows.net | 1890 | 12 | 0.63 | 9100 |
| cache.redis.cache.windows.net | 4310 | 0 | 0.00 | 120 |

FailureRate% is derived as `Failed / Calls * 100`.

### Common misdiagnoses
- Blaming function code when dependency latency is dominating total duration.
- Treating every latency spike as cold start without checking dependency p95.

### Next steps
- Reduce cold-start cost (always-ready, dependency trimming, startup optimization).
- Tune dependency timeouts/retries and add circuit-breaking where appropriate.
- Adjust concurrency and processing model to avoid blocking work on hot paths.

### Related labs
- [cold-start](lab-guides.md#1-cold-start-lab)

## Functions failing with errors

### What you may observe
- Exception count and `5xx` increase quickly.
- Retries and poison-message rates rise.

### Likely hypotheses
- Auth failures to downstream resources.
- Function timeout reached.
- Memory pressure or runtime mismatch.

### What to check first
- Identify top exception type by count and trend.
- Separate transient errors from deterministic authorization/configuration failures.
- Confirm whether failures started after a configuration or deployment change.

### Check in Portal
- **Application Insights → Failures → Exception types**: identify dominant exception and affected operations.
- **Application Insights → Failures → Samples**: inspect `outerMessage`, call stack, and correlation IDs.
- **Function App → Configuration**: verify identity and app setting drift.

### Check with Azure CLI
```bash
az monitor log-analytics query \
  --workspace "$WORKSPACE_ID" \
  --analytics-query "exceptions | where timestamp > ago(1h) | where cloud_RoleName =~ '$APP_NAME' | summarize count() by type, outerMessage" \
  --output table

az functionapp config show --name "$APP_NAME" --resource-group "$RG" --output json
```

### Example Output
```text
type                                 outerMessage                                         count_
-----------------------------------  ---------------------------------------------------  ------
System.UnauthorizedAccessException   The client does not have authorization               932
System.Net.Sockets.SocketException   Connection refused                                   188
Microsoft.WindowsAzure.Storage...    Storage operation failed: (403) Forbidden            174

{
  "id": "/subscriptions/<subscription-id>/resourceGroups/rg-myapp-prod/providers/Microsoft.Web/sites/func-myapp-prod/config/web",
  "linuxFxVersion": "PYTHON|3.11",
  "alwaysOn": false
}
```

### How to interpret the results
| Pattern | Normal | Abnormal | Interpretation |
|---|---|---|---|
| Exception cadence | Sporadic, diverse, quickly self-recovering | Sustained high-volume same exception type | Usually permanent config/auth/runtime issue. |
| Auth-related exception share | Low and intermittent | Dominant (`403`, `UnauthorizedAccessException`) | Retrying will not heal missing role/scope/secret. |
| Failure onset | No clear deployment correlation | Sharp increase right after config/deploy | Strong signal of regression in rollout. |

### Sample log patterns
```text
# Abnormal: authorization failure
[2024-01-15T12:10:00Z] System.UnauthorizedAccessException: The client does not have authorization to perform action.
[2024-01-15T12:10:00Z] Storage operation failed: (403) Forbidden.

# Abnormal: network connectivity
[2024-01-15T12:12:11Z] System.Net.Sockets.SocketException: Connection refused.

# Normal: occasional transient with successful retry
[2024-01-15T12:20:07Z] Dependency timeout on attempt 1.
[2024-01-15T12:20:09Z] Retry succeeded on attempt 2.
```

### KQL queries
- Query 1 clusters exceptions by type/message to identify dominant failure modes.
  For the full query, see [KQL Query Library → 6) Exception trends](kql.md#6-exception-trends).

- Query 2 trends invocation failures by function to confirm sustained error regressions.
  For the full query, see [KQL Query Library → 1) Function execution summary (success/failure/duration)](kql.md#1-function-execution-summary-successfailureduration).

### Example KQL result
| ExceptionType | Message | Count |
|---|---|---|
| System.UnauthorizedAccessException | The client does not have authorization | 932 |
| Microsoft.WindowsAzure.Storage.StorageException | Storage operation failed: (403) Forbidden | 174 |
| System.Net.Sockets.SocketException | Connection refused | 188 |

### Common misdiagnoses
- Retrying aggressively when the root cause is permanent auth failure.
- Treating all failures as transient dependency issues without exception clustering.

### Next steps
- Repair identity/RBAC or secrets configuration.
- Correct timeout and runtime alignment issues.
- Roll back to the last known good artifact if regression is confirmed.

### Related labs
- [managed-identity-auth](lab-guides.md#5-managed-identity-authentication-lab)

## Queue messages piling up

### What you may observe
- Queue depth and message age rise steadily.
- Processing throughput stays below enqueue rate.

### Likely hypotheses
- Scale-out not keeping up.
- Poison-message loop.
- Per-message processing regression.

### What to check first
- Verify dequeue count patterns for repeated retries.
- Compare queue message age trend vs invocation trend.
- Identify whether processing time per message increased after a recent change.

### Check in Portal
- **Storage Account → Queues → _<queue-name>_**: review message count trend.
- **Storage Account → Queues → _<queue-name>-poison_**: check poison growth.
- **Function App → Monitor**: compare invocation throughput with enqueue rate.

### Check with Azure CLI
```bash
az storage message peek \
  --account-name "<storage-account-name>" \
  --queue-name "<queue-name>" \
  --num-messages 5 \
  --auth-mode login

az monitor metrics list \
  --resource "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.Storage/storageAccounts/<storage-account-name>" \
  --metric "QueueMessageCount" \
  --interval PT1M \
  --aggregation Average \
  --offset 1h \
  --output table
```

### Example Output
```text
[
  {
    "messageId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "insertionTime": "2024-01-15T12:00:00+00:00",
    "expirationTime": "2024-01-22T12:00:00+00:00",
    "dequeueCount": "5",
    "messageText": "{\"orderId\":\"ORD-***\"}"
  }
]

TimeStamp                    Average
---------------------------  -------
2024-01-15T12:00:00.000000Z  1211
2024-01-15T12:30:00.000000Z  3988
2024-01-15T13:00:00.000000Z  7420
```

### How to interpret the results
| Signal | Normal | Abnormal | Interpretation |
|---|---|---|---|
| Queue drain behavior | Queue drains within 5 minutes during normal load | Queue age > 30 minutes and growing | Throughput deficit exists; backlog will continue to expand. |
| Dequeue count | Most messages dequeued 1-2 times | Repeated `dequeueCount >= 5` | Poison/retry loop or deterministic processing failure. |
| Scale response | Invocation throughput rises with enqueue rate | Throughput flat while queue grows | Bottleneck likely per-message execution duration or downstream dependency. |

### Sample log patterns
```text
# Abnormal: repeated retries
[2024-01-15T12:22:00Z] Message has been dequeued '5' time(s).
[2024-01-15T12:22:01Z] Moving message to poison queue.

# Abnormal: long processing path
[2024-01-15T12:25:10Z] Executed 'Functions.QueueProcessor' (Succeeded, Duration=48211ms)

# Normal: stable queue processing
[2024-01-15T12:30:05Z] Executed 'Functions.QueueProcessor' (Succeeded, Duration=412ms)
```

### KQL queries
!!! warning "Custom instrumentation required"
    Queue processing metrics (`QueueMessageAgeMs`, `QueueProcessingLatencyMs`) are not emitted by the Azure Functions runtime by default. These queries require your application to explicitly emit custom metrics. For built-in queue monitoring, use Azure Storage metrics via Azure Monitor.

- Query 1 tracks queue age/processing latency custom metrics over time to confirm backlog growth and processing lag.
  For the full query, see [KQL Query Library → 5) Queue processing latency](kql.md#5-queue-processing-latency).

- Query 2 trends queue processor invocation/failure latency to correlate function throughput with backlog behavior.
  For the full query, see [KQL Query Library → 1) Function execution summary (success/failure/duration)](kql.md#1-function-execution-summary-successfailureduration).

### Example KQL result
| timestamp | MetricName | AvgMs | P95Ms | MaxMs |
|---|---|---|---|---|
| 2024-01-15T13:00:00Z | QueueMessageAgeMs | 1522000 | 1940000 | 2210000 |
| 2024-01-15T13:00:00Z | QueueProcessingLatencyMs | 35800 | 49100 | 72200 |
| 2024-01-15T13:00:00Z | QueueDequeueDelayMs | 890000 | 1210000 | 1550000 |

### Common misdiagnoses
- Adding more instances immediately when the true bottleneck is long per-message duration.
- Ignoring poison queue growth and assuming pure scale insufficiency.

### Next steps
- Isolate poison messages and validate retry policy.
- Reduce processing time per message.
- Reassess scale limits and hosting plan fit.

### Related labs
- [queue-backlog-scaling](lab-guides.md#3-queue-backlog-scaling-lab)

## Blob trigger not firing

### What you may observe
- Blob uploads succeed, but invocations never appear.
- Issue starts after Flex Consumption migration.

### Likely hypotheses
- Event Grid subscription missing.
- Storage networking or RBAC blocks notifications.
- Trigger binding misconfiguration.

### What to check first
- Confirm Event Grid subscription exists for the storage account.
- Confirm listener startup traces for blob trigger.
- Confirm hosting plan behavior (FC1 requires Event Grid-based blob trigger).

### Check in Portal
- **Storage Account → Events → Event Subscriptions**: verify subscription exists and endpoint health is successful.
- **Function App → Functions → _Blob trigger function_**: verify enabled state.
- **Application Insights → Logs**: check for `BlobTrigger` listener startup traces.

### Check with Azure CLI
```bash
az eventgrid event-subscription list \
  --source-resource-id "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.Storage/storageAccounts/<storage-account-name>" \
  --output table

az monitor log-analytics query \
  --workspace "$WORKSPACE_ID" \
  --analytics-query "traces | where timestamp > ago(1h) | where cloud_RoleName =~ '$APP_NAME' | where message has_any ('BlobTrigger','EventGrid','listener') | order by timestamp desc" \
  --output table
```

### Example Output
```text
# Abnormal: no Event Grid subscriptions returned
[]

# Normal: subscription exists
Name                                ProvisioningState  DestinationEndpointType
----------------------------------  -----------------  -----------------------
func-myapp-prod-blob-created-sub    Succeeded          WebHook
```

### How to interpret the results
| Signal | Normal | Abnormal | Interpretation |
|---|---|---|---|
| Event Grid subscription | At least one active subscription for blob created events | Empty list or failed provisioning | Trigger source cannot notify Function endpoint. |
| Blob listener traces | `BlobTrigger listener started` appears after startup | No listener trace, or explicit trigger-not-fired messages | Host is not wired to blob events. |
| Hosting model compatibility | Event Grid configuration present on FC1 | Polling assumptions carried from older model | Architecture mismatch, not app code defect. |

### Sample log patterns
```text
# Abnormal: trigger not firing
[2024-01-15T13:40:00Z] BlobTrigger - function was not triggered for container 'incoming'.

# Abnormal: missing subscription
[2024-01-15T13:40:03Z] Event Grid subscription not found for storage account '<storage-account-name>'.

# Normal: listener healthy
[2024-01-15T13:45:00Z] BlobTrigger listener started for function 'BlobIngestor'.
```

### KQL queries
- Query 1 inspects blob trigger and Event Grid listener traces to validate trigger wiring failures.
  For the full query, see [KQL Query Library → 8) Host startup/shutdown events](kql.md#8-host-startupshutdown-events).

- Query 2 summarizes blob handler invocation/failure latency for quick trigger health validation.
  For the full query, see [KQL Query Library → 1) Function execution summary (success/failure/duration)](kql.md#1-function-execution-summary-successfailureduration).

### Example KQL result
| timestamp | severityLevel | message |
|---|---|---|
| 2024-01-15T13:40:03Z | 3 | Event Grid subscription not found for storage account '<storage-account-name>'. |
| 2024-01-15T13:40:00Z | 2 | BlobTrigger - function was not triggered for container 'incoming'. |

### Common misdiagnoses
- Blaming blob trigger code when the real issue is missing Event Grid wiring on FC1.
- Assuming storage upload success implies trigger notification path is healthy.

### Next steps
- Use Event Grid-based blob trigger on Flex Consumption.
- Recreate missing subscription and verify endpoint delivery.
- Confirm storage access permissions for managed identity.

### Related labs
- Closest network/event-path lab: [dns-vnet-resolution](lab-guides.md#4-dns-and-vnet-resolution-lab)

## Deployment failures

### What you may observe
- Deployment fails or app degrades immediately after release.
- Functions disappear or host startup fails.

### Likely hypotheses
- Runtime mismatch.
- Missing required app settings.
- Deployment method not suited to hosting model.

### What to check first
- Confirm deployment event status and timestamp in activity logs.
- Confirm host startup traces after deployment.
- Confirm `FUNCTIONS_WORKER_RUNTIME`, extension/runtime versions, and critical settings.

### Check in Portal
- **Function App → Deployment Center → Logs**: inspect latest deployment operation status and step failures.
- **Function App → Log stream**: inspect startup and trigger sync traces.
- **Application Insights → Logs**: verify host startup completion after deployment.

### Check with Azure CLI
```bash
az functionapp show --name "$APP_NAME" --resource-group "$RG" --output json
az functionapp config appsettings list --name "$APP_NAME" --resource-group "$RG" --output table
az monitor activity-log list --resource-group "$RG" --offset 2h --output table
```

### Example Output
```text
eventTimestamp                operationName                                status      subStatus
---------------------------  -------------------------------------------  ----------  --------------------------
2024-01-15T14:05:10.000000Z  Microsoft.Web/sites/publish/action          Failed      BadRequest
2024-01-15T14:05:12.000000Z  Microsoft.Web/sites/config/write             Succeeded   OK

Sample host traces after deploy:
[2024-01-15T14:05:30Z] Site not started yet.
[2024-01-15T14:05:45Z] Container didn't respond to HTTP pings on port 8080.
[2024-01-15T14:06:02Z] Health check failure.
[2024-01-15T14:06:15Z] Syncing triggers...
[2024-01-15T14:06:45Z] Function host is not running.
```

### How to interpret the results
| Signal | Normal | Abnormal | Interpretation |
|---|---|---|---|
| Deployment operation | `Succeeded` | `Failed` with `BadRequest`/`Conflict` | Artifact or deployment method mismatch likely. |
| Post-deploy host startup | `Host started` and trigger sync complete | Startup timeout, repeated health check failure | App cannot initialize with current artifact/config. |
| Trigger availability | Functions listed and invokable | Functions missing/unavailable | Host bootstrapping failed before trigger registration. |

### Sample log patterns
```text
# Abnormal: container startup issue
[2024-01-15T14:05:45Z] Container didn't respond to HTTP pings on port 8080.
[2024-01-15T14:06:02Z] Health check failure.

# Abnormal: host did not come up
[2024-01-15T14:06:15Z] Syncing triggers...
[2024-01-15T14:06:45Z] Function host is not running.

# Normal: deployment complete
[2024-01-15T14:08:00Z] Deployment successful.
[2024-01-15T14:08:05Z] Host started (410ms)
```

### KQL queries
- Query 1 surfaces deployment/startup lifecycle traces to pinpoint host boot failures after release.
  For the full query, see [KQL Query Library → 8) Host startup/shutdown events](kql.md#8-host-startupshutdown-events).

- Query 2 trends post-deployment invocation/failure latency to verify runtime recovery.
  For the full query, see [KQL Query Library → 1) Function execution summary (success/failure/duration)](kql.md#1-function-execution-summary-successfailureduration).

### Example KQL result
| timestamp | severityLevel | message |
|---|---|---|
| 2024-01-15T14:06:45Z | 3 | Function host is not running. |
| 2024-01-15T14:06:02Z | 3 | Health check failure. |
| 2024-01-15T14:05:45Z | 3 | Container didn't respond to HTTP pings on port 8080. |

### Common misdiagnoses
- Re-deploying the same broken artifact repeatedly instead of rolling back.
- Treating startup failure as transient before validating runtime/config compatibility.

### Next steps
- Align artifact runtime and app runtime settings.
- Restore required configuration before activation.
- Roll back quickly, then apply a controlled forward fix.

### Related labs
- Closest startup analysis lab: [cold-start](lab-guides.md#1-cold-start-lab)

## See Also
- [First 10 Minutes](first-10-minutes.md)
- [Methodology](methodology.md)
- [KQL Query Library](kql.md)
- [Troubleshooting Lab Guides](lab-guides.md)

## References
- [Azure Functions best practices](https://learn.microsoft.com/azure/azure-functions/functions-best-practices)
- [Monitor Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-monitoring)
- [Analyze telemetry in Application Insights](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- [Azure Functions triggers and bindings concepts](https://learn.microsoft.com/azure/azure-functions/functions-triggers-bindings)
- [Azure Functions Event Grid blob trigger](https://learn.microsoft.com/azure/azure-functions/functions-event-grid-blob-trigger)
- [Deploy Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-deployment-technologies)
