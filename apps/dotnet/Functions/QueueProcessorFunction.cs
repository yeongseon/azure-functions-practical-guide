using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace AzureFunctionsGuide.Functions;

/// <summary>
/// Queue message processor — processes messages from incoming-orders queue.
/// Binding: Queue trigger on "incoming-orders" with QueueStorage connection.
/// </summary>
public class QueueProcessorFunction
{
    private readonly ILogger<QueueProcessorFunction> _logger;

    public QueueProcessorFunction(ILogger<QueueProcessorFunction> logger)
    {
        _logger = logger;
    }

    [Function("queueProcessor")]
    public void Run(
        [QueueTrigger("incoming-orders", Connection = "QueueStorage")] string message)
    {
        _logger.LogInformation("Queue message received: {Message}", message);
    }
}
