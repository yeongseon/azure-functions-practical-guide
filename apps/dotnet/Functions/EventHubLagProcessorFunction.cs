using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace AzureFunctionsGuide.Functions;

/// <summary>
/// Event Hub message processor — processes events from the events hub.
/// Binding: EventHub trigger on "events" with EventHubConnection connection.
/// </summary>
public class EventHubLagProcessorFunction
{
    private readonly ILogger<EventHubLagProcessorFunction> _logger;

    public EventHubLagProcessorFunction(ILogger<EventHubLagProcessorFunction> logger)
    {
        _logger = logger;
    }

    [Function("eventhubLagProcessor")]
    public void Run(
        [EventHubTrigger("events", Connection = "EventHubConnection")] string[] messages)
    {
        _logger.LogInformation("EventHub batch received: {Count} messages", messages.Length);

        foreach (var message in messages)
        {
            _logger.LogInformation("EventHub message: {Message}", message);
        }
    }
}
