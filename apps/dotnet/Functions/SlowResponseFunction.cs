using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace AzureFunctionsGuide.Functions;

/// <summary>
/// Slow response endpoint — delays response by configurable duration for latency testing.
/// Route: GET /api/slow?delay=N
/// </summary>
public class SlowResponseFunction
{
    private readonly ILogger<SlowResponseFunction> _logger;

    public SlowResponseFunction(ILogger<SlowResponseFunction> logger)
    {
        _logger = logger;
    }

    [Function("slowResponse")]
    public async Task<IActionResult> Run(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "slow")] HttpRequest req)
    {
        var delayStr = req.Query["delay"].FirstOrDefault() ?? "2";
        if (!int.TryParse(delayStr, out var delaySec))
            delaySec = 2;

        _logger.LogInformation("Slow response: delaying {Seconds}s", delaySec);

        await Task.Delay(delaySec * 1000);

        var result = new
        {
            delayed = delaySec,
            message = $"Response after {delaySec} second(s)"
        };

        return new OkObjectResult(result);
    }
}
