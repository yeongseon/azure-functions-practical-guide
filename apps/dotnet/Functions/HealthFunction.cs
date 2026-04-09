using System.Text.Json;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace AzureFunctionsGuide.Functions;

/// <summary>
/// Health check endpoint — returns app liveness status.
/// Route: GET /api/health
/// </summary>
public class HealthFunction
{
    private readonly ILogger<HealthFunction> _logger;

    public HealthFunction(ILogger<HealthFunction> logger)
    {
        _logger = logger;
    }

    [Function("health")]
    public IActionResult Run(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "health")] HttpRequest req)
    {
        _logger.LogInformation("Health check invoked");

        var result = new
        {
            status = "healthy",
            timestamp = DateTime.UtcNow.ToString("o"),
            version = "1.0.0"
        };

        return new OkObjectResult(result);
    }
}
