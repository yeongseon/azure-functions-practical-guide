using System.Runtime.InteropServices;
using AzureFunctionsGuide.Shared;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace AzureFunctionsGuide.Functions;

/// <summary>
/// Application info endpoint returning runtime and configuration details.
/// Route: GET /api/info
/// </summary>
public class InfoFunction
{
    private readonly ILogger<InfoFunction> _logger;

    public InfoFunction(ILogger<InfoFunction> logger)
    {
        _logger = logger;
    }

    [Function("info")]
    public IActionResult Run(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "info")] HttpRequest req)
    {
        _logger.LogInformation("Info endpoint requested");

        var result = new
        {
            name = AppConfig.AppName,
            version = AppConfig.Version,
            dotnet = RuntimeInformation.FrameworkDescription,
            os = RuntimeInformation.IsOSPlatform(OSPlatform.Linux) ? "Linux" :
                 RuntimeInformation.IsOSPlatform(OSPlatform.Windows) ? "Windows" : "Other",
            environment = AppConfig.FunctionsEnvironment,
            functionApp = AppConfig.FunctionAppName
        };

        return new OkObjectResult(result);
    }
}
