using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace AzureFunctionsGuide.Functions;

/// <summary>
/// Hello HTTP handler — primary endpoint used across all tutorials.
/// Route: GET /api/hello/{name?}
/// </summary>
public class HelloHttpFunction
{
    private readonly ILogger<HelloHttpFunction> _logger;

    public HelloHttpFunction(ILogger<HelloHttpFunction> logger)
    {
        _logger = logger;
    }

    [Function("helloHttp")]
    public IActionResult Run(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "hello/{name?}")] HttpRequest req,
        string? name)
    {
        name ??= req.Query["name"].FirstOrDefault() ?? "world";
        _logger.LogInformation("Handled hello for {Name}", name);

        return new OkObjectResult(new { message = $"Hello, {name}" });
    }
}
