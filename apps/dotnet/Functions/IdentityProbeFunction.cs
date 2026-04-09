using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace AzureFunctionsGuide.Functions;

/// <summary>
/// Managed identity status probe.
/// Route: GET /api/identity
/// </summary>
public class IdentityProbeFunction
{
    private readonly ILogger<IdentityProbeFunction> _logger;

    public IdentityProbeFunction(ILogger<IdentityProbeFunction> logger)
    {
        _logger = logger;
    }

    [Function("identityProbe")]
    public IActionResult Run(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "identity")] HttpRequest req)
    {
        _logger.LogInformation("Identity probe requested");

        var identityEndpoint = System.Environment.GetEnvironmentVariable("IDENTITY_ENDPOINT");
        var hasManagedIdentity = !string.IsNullOrEmpty(identityEndpoint);

        return new OkObjectResult(new
        {
            managedIdentity = hasManagedIdentity,
            identityEndpoint = hasManagedIdentity ? "configured" : "not configured"
        });
    }
}
