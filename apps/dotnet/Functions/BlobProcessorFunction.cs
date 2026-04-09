using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace AzureFunctionsGuide.Functions;

/// <summary>
/// Blob upload processor — triggered when a blob is uploaded to the uploads container.
/// Binding: Blob trigger on "uploads/{name}" with AzureWebJobsStorage connection.
/// </summary>
public class BlobProcessorFunction
{
    private readonly ILogger<BlobProcessorFunction> _logger;

    public BlobProcessorFunction(ILogger<BlobProcessorFunction> logger)
    {
        _logger = logger;
    }

    [Function("blobProcessor")]
    public void Run(
        [BlobTrigger("uploads/{name}", Connection = "AzureWebJobsStorage")] string content,
        string name)
    {
        _logger.LogInformation("Blob processed: {Name}, size: {Size} chars", name, content.Length);
    }
}
