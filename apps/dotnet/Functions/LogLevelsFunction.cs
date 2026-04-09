using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace AzureFunctionsGuide.Functions;

/// <summary>
/// Log levels demonstration endpoint.
/// Route: GET /api/loglevels
/// </summary>
public class LogLevelsFunction
{
    private readonly ILogger<LogLevelsFunction> _logger;

    public LogLevelsFunction(ILogger<LogLevelsFunction> logger)
    {
        _logger = logger;
    }

    [Function("logLevels")]
    public IActionResult Run(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "loglevels")] HttpRequest req)
    {
        _logger.LogDebug("Debug level log message");
        _logger.LogInformation("Info level log message");
        _logger.LogWarning("Warning level log message");
        _logger.LogError("Error level log message");
        _logger.LogCritical("Critical level log message");

        return new OkObjectResult(new { logged = true });
    }
}
