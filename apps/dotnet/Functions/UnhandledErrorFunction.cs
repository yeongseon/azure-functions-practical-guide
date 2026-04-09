using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace AzureFunctionsGuide.Functions;

/// <summary>
/// Unhandled exception test — generates real 500 errors in Application Insights.
/// Route: GET /api/unhandlederror
/// </summary>
public class UnhandledErrorFunction
{
    private readonly ILogger<UnhandledErrorFunction> _logger;

    public UnhandledErrorFunction(ILogger<UnhandledErrorFunction> logger)
    {
        _logger = logger;
    }

    [Function("unhandledError")]
    public IActionResult Run(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "unhandlederror")] HttpRequest req)
    {
        _logger.LogInformation("Unhandled exception endpoint requested");
        throw new InvalidOperationException("Deliberate unhandled error for KQL data collection");
    }
}
