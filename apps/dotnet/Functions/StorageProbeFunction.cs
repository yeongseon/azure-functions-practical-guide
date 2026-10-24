using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using AzureFunctionsGuide.Shared;

namespace AzureFunctionsGuide.Functions;

/// <summary>
/// Bounded, read-only Blob service request; does not verify host lock health.
/// Route: GET /api/storage/probe
/// </summary>
public class StorageProbeFunction
{
    private readonly ILogger<StorageProbeFunction> _logger;
    private readonly StorageProbe _probe;

    public StorageProbeFunction(ILogger<StorageProbeFunction> logger, StorageProbe probe)
    {
        _logger = logger;
        _probe = probe;
    }

    [Function("storageProbe")]
    public async Task<IActionResult> Run(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "storage/probe")] HttpRequest req)
    {
        var result = await _probe.RunAsync(req.HttpContext.RequestAborted);
        // Never log SDK exceptions, endpoints, account names or credentials.
        _logger.LogInformation("Storage probe: configuration={Configuration}, verification={Verification}",
            result.Configuration, result.Verification);
        return new ObjectResult(result) { StatusCode = result.StatusCode };
    }
}
