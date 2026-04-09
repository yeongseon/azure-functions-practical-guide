using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace AzureFunctionsGuide.Functions;

/// <summary>
/// Timer lab — 5-minute interval timer for schedule testing.
/// Binding: Timer trigger with CRON expression "0 */5 * * * *".
/// </summary>
public class TimerLabFunction
{
    private readonly ILogger<TimerLabFunction> _logger;

    public TimerLabFunction(ILogger<TimerLabFunction> logger)
    {
        _logger = logger;
    }

    [Function("timerLab")]
    public void Run(
        [TimerTrigger("0 */5 * * * *")] TimerInfo timer)
    {
        var instanceId = (System.Environment.GetEnvironmentVariable("WEBSITE_INSTANCE_ID") ?? "unknown")[..Math.Min(8, (System.Environment.GetEnvironmentVariable("WEBSITE_INSTANCE_ID") ?? "unknown").Length)];

        _logger.LogInformation("TimerFired isPastDue={IsPastDue} actualUtc={Timestamp} instanceId={InstanceId}",
            timer.IsPastDue, DateTime.UtcNow.ToString("o"), instanceId);

        if (timer.IsPastDue)
        {
            _logger.LogWarning("TimerPastDue actualUtc={Timestamp} instanceId={InstanceId}",
                DateTime.UtcNow.ToString("o"), instanceId);
        }
    }
}
