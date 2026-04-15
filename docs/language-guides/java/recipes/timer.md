---
content_sources:
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-bindings-timer
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-app-settings
---

# Timer Trigger

This recipe uses Java timer triggers with NCRONTAB schedules, past-due handling, and hosting-plan time-zone behavior.

## Architecture

<!-- diagram-id: architecture -->
```mermaid
flowchart TD
    SCHEDULE[NCRONTAB schedule] --> TIMER[@TimerTrigger]
    TIMER --> WORK[Scheduled work]
    WORK --> LOGS[Execution logs and metrics]
```

## Prerequisites

Define a schedule setting:

```bash
az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG \
  --settings "NightlySchedule=0 0 2 * * *"
```

Time-zone caveat:

- `WEBSITE_TIME_ZONE` is supported on Windows plans and Linux Premium/Dedicated.
- `WEBSITE_TIME_ZONE` is not supported on Linux Consumption or Linux Flex Consumption.

## Java implementation

```java
package com.contoso.functions;

import com.microsoft.azure.functions.ExecutionContext;
import com.microsoft.azure.functions.TimerInfo;
import com.microsoft.azure.functions.annotation.FunctionName;
import com.microsoft.azure.functions.annotation.TimerTrigger;

public class TimerFunctions {

    @FunctionName("nightlyCleanup")
    public void nightlyCleanup(
        @TimerTrigger(name = "timerInfo", schedule = "%NightlySchedule%") TimerInfo timerInfo,
        final ExecutionContext context
    ) {
        if (timerInfo.isPastDue()) {
            context.getLogger().warning("Timer execution is running past due.");
        }

        context.getLogger().info("Timer fired. Running nightly cleanup job.");
        // Cleanup logic here
    }
}
```

## Implementation notes

- Use app settings for schedule strings so ops can change cadence without redeploy.
- Use `isPastDue()` to guard expensive work and detect scheduling delays.
- Keep timer functions idempotent because missed executions can overlap during recovery.
- For business time zones on unsupported Linux plans, convert time in code or use UTC schedules.

## See Also

- [Queue Storage Integration](queue.md)
- [Durable Orchestration](durable-orchestration.md)
- [Operations: Monitoring](../../../operations/monitoring.md)

## Sources

- [Timer trigger for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-bindings-timer)
- [App settings reference for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-app-settings)
