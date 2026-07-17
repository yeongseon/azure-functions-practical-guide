---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-timer
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# Timer Trigger

Run PowerShell functions on a schedule using NCronTab expressions.

## Configuration

`function.json`:

```json
{
  "bindings": [
    {
      "name": "Timer",
      "type": "timerTrigger",
      "direction": "in",
      "schedule": "0 */5 * * * *"
    }
  ]
}
```

`run.ps1`:

```powershell
param($Timer)

if ($Timer.IsPastDue) {
    Write-Warning "Timer is running late"
}

Write-Information "Scheduled job started at $(Get-Date -Format o)"
```

## NCronTab Format

`{second} {minute} {hour} {day} {month} {day-of-week}`

| Expression | Meaning |
|------------|---------|
| `0 */5 * * * *` | Every 5 minutes |
| `0 0 * * * *` | Every hour on the hour |
| `0 0 9 * * 1-5` | 09:00 on weekdays |
| `0 30 3 * * *` | 03:30 daily |

## Idempotent Batch Execution

Timer functions may occasionally run twice (e.g., across a scale event). Guard against duplicate work:

```powershell
param($Timer)

$runId = Get-Date -Format "yyyyMMddHH"
# Use a lease/marker in storage keyed on $runId to ensure single execution.
```

!!! tip "Time zones"
    Timer schedules use UTC by default. Set the `WEBSITE_TIME_ZONE` app setting to change the evaluation time zone.

## See Also

- [Queue Storage](queue.md)
- [Environment Variables](../environment-variables.md)
- [Recipes Index](index.md)

## Sources

- [Timer trigger (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-timer)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
