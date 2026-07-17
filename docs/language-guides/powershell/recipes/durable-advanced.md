---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# Durable Advanced Patterns

Apply fan-out/fan-in, external events, durable timers, and eternal orchestrations with Durable Functions in PowerShell. These patterns build on the [Durable Orchestration](durable-orchestration.md) basics.

## Fan-Out / Fan-In

Run activities in parallel with `-NoWait`, then join the results:

```powershell
param($Context)

$items = $Context.Input

$parallelTasks = foreach ($item in $items) {
    Invoke-DurableActivity -FunctionName 'ProcessItem' -Input $item -NoWait
}

$results = Wait-ActivityFunction -Task $parallelTasks

return ($results | Measure-Object -Sum).Sum
```

`Wait-ActivityFunction` blocks until all scheduled tasks complete and returns their results in order.

## Durable Timers

Use durable timers for reliable delays and timeouts instead of `Start-Sleep`:

```powershell
$expiry = $Context.CurrentUtcDateTime.AddHours(1)
Start-DurableTimer -Duration (New-TimeSpan -Hours 1)
```

## Waiting for External Events

Suspend an orchestration until an external signal (such as a human approval) arrives:

```powershell
param($Context)

$approval = Start-DurableExternalEventListener -EventName "ApprovalReceived"

if ($approval.approved) {
    Invoke-DurableActivity -FunctionName 'Publish' -Input $Context.Input
}
```

Raise the event from a client function:

```powershell
Send-DurableExternalEvent -InstanceId $instanceId -EventName "ApprovalReceived" -EventData @{ approved = $true }
```

## Timeout with Event Race

Combine a durable timer with an event listener to enforce an approval deadline:

```powershell
$timeoutTask  = Start-DurableTimer -Duration (New-TimeSpan -Days 1) -NoWait
$approvalTask = Start-DurableExternalEventListener -EventName "ApprovalReceived" -NoWait

$winner = Wait-DurableTask -Task @($approvalTask, $timeoutTask) -Any

if ($winner -eq $approvalTask) {
    Write-Information "Approved in time"
} else {
    Write-Information "Approval timed out"
}
```

## Recurring Work (Periodic Orchestrations)

PowerShell does not support the `ContinueAsNew` / continue-as-new pattern used by other Durable Functions SDKs. For recurring cleanup or monitoring, run a **singleton** orchestration (fixed instance ID) that loops with a durable timer:

```powershell
param($Context)

while ($true) {
    Invoke-DurableActivity -FunctionName 'RunHealthCheck'
    Start-DurableTimer -Duration (New-TimeSpan -Minutes 5)
}
```

Start it as a singleton from the client so only one instance runs:

```powershell
$instanceId = Start-DurableOrchestration -FunctionName 'HealthCheckOrchestrator' -InstanceId 'singleton-healthcheck'
```

!!! warning "History growth"
    Because PowerShell cannot reset orchestration history with continue-as-new, a long-running loop accumulates history over time. Keep the per-iteration work small and consider a Timer trigger instead for simple schedules. See [Timer Trigger](timer.md).

!!! warning "Entities not supported"
    Durable **entities** (entity triggers and entity clients) are not supported in the PowerShell model. Model stateful coordination with orchestrations and external storage instead.

## See Also

- [Durable Orchestration](durable-orchestration.md)
- [Retries and Error Handling](retry.md)
- [Recipes Index](index.md)

## Sources

- [Durable Functions overview (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
