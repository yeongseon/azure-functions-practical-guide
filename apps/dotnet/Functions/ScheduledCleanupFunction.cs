using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace AzureFunctionsGuide.Functions;

/// <summary>
/// Scheduled cleanup — runs daily at 2:00 AM UTC.
/// Binding: Timer trigger with CRON expression "0 0 2 * * *".
/// </summary>
public class ScheduledCleanupFunction
{
    private readonly ILogger<ScheduledCleanupFunction> _logger;

    public ScheduledCleanupFunction(ILogger<ScheduledCleanupFunction> logger)
    {
        _logger = logger;
    }

    [Function("scheduledCleanup")]
    public void Run(
        [TimerTrigger("0 0 2 * * *")] TimerInfo timer)
    {
        _logger.LogInformation("Scheduled cleanup fired at {Timestamp}", DateTime.UtcNow.ToString("o"));

        if (timer.IsPastDue)
        {
            _logger.LogWarning("Timer trigger is past due");
        }
    }
}
