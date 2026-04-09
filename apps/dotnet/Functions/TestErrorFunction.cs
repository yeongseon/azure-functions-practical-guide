using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace AzureFunctionsGuide.Functions;

/// <summary>
/// Controlled error test — catches and returns error details.
/// Route: GET /api/testerror
/// </summary>
public class TestErrorFunction
{
    private readonly ILogger<TestErrorFunction> _logger;

    public TestErrorFunction(ILogger<TestErrorFunction> logger)
    {
        _logger = logger;
    }

    [Function("testError")]
    public IActionResult Run(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "testerror")] HttpRequest req)
    {
        _logger.LogInformation("Test error endpoint requested");

        try
        {
            throw new InvalidOperationException("Simulated error for testing");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Caught simulated error: {Message}", ex.Message);

            return new OkObjectResult(new
            {
                error = "Handled exception",
                type = ex.GetType().Name,
                message = ex.Message
            });
        }
    }
}
