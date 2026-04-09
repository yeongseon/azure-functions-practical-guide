using System.Diagnostics;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace AzureFunctionsGuide.Functions;

/// <summary>
/// External HTTP dependency call — measures latency to httpbin.org.
/// Route: GET /api/dependency
/// </summary>
public class ExternalDependencyFunction
{
    private readonly ILogger<ExternalDependencyFunction> _logger;
    private static readonly HttpClient _httpClient = new();
    private const string ExternalUrl = "https://httpbin.org/get";

    public ExternalDependencyFunction(ILogger<ExternalDependencyFunction> logger)
    {
        _logger = logger;
    }

    [Function("externalDependency")]
    public async Task<IActionResult> Run(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "dependency")] HttpRequest req)
    {
        _logger.LogInformation("External dependency endpoint requested (url={Url})", ExternalUrl);

        var sw = Stopwatch.StartNew();
        try
        {
            var response = await _httpClient.GetAsync(ExternalUrl);
            sw.Stop();

            _logger.LogInformation("External call completed (status={Status}, time={Elapsed}ms)",
                (int)response.StatusCode, sw.ElapsedMilliseconds);

            return new OkObjectResult(new
            {
                url = ExternalUrl,
                statusCode = (int)response.StatusCode,
                latencyMs = sw.ElapsedMilliseconds,
                success = response.IsSuccessStatusCode
            });
        }
        catch (Exception ex)
        {
            sw.Stop();
            _logger.LogError(ex, "External call failed (time={Elapsed}ms)", sw.ElapsedMilliseconds);

            return new ObjectResult(new
            {
                url = ExternalUrl,
                statusCode = 0,
                latencyMs = sw.ElapsedMilliseconds,
                success = false,
                error = ex.Message
            })
            { StatusCode = 502 };
        }
    }
}
