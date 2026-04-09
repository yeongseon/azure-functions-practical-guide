using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace AzureFunctionsGuide.Functions;

/// <summary>
/// Storage connectivity check — verifies storage account configuration.
/// Route: GET /api/storage/probe
/// </summary>
public class StorageProbeFunction
{
    private readonly ILogger<StorageProbeFunction> _logger;

    public StorageProbeFunction(ILogger<StorageProbeFunction> logger)
    {
        _logger = logger;
    }

    [Function("storageProbe")]
    public IActionResult Run(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "storage/probe")] HttpRequest req)
    {
        var storageConn = System.Environment.GetEnvironmentVariable("AzureWebJobsStorage");
        var hasStorage = !string.IsNullOrEmpty(storageConn);

        _logger.LogInformation("Storage probe: connection {Status}",
            hasStorage ? "configured" : "missing");

        string connectionType;
        if (!hasStorage)
            connectionType = "none";
        else if (storageConn!.Contains("AccountName="))
            connectionType = "connectionString";
        else
            connectionType = "identity";

        return new OkObjectResult(new
        {
            storageConfigured = hasStorage,
            connectionType
        });
    }
}
