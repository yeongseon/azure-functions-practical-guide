using System.Net;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace AzureFunctionsGuide.Functions;

/// <summary>
/// DNS resolution probe — resolves a hostname and returns addresses.
/// Route: GET /api/dns/{hostname}
/// </summary>
public class DnsResolveFunction
{
    private readonly ILogger<DnsResolveFunction> _logger;

    public DnsResolveFunction(ILogger<DnsResolveFunction> logger)
    {
        _logger = logger;
    }

    [Function("dnsResolve")]
    public async Task<IActionResult> Run(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "dns/{hostname}")] HttpRequest req,
        string hostname)
    {
        _logger.LogInformation("DNS resolve requested for {Hostname}", hostname);

        try
        {
            var addresses = await Dns.GetHostAddressesAsync(hostname);
            var addressList = addresses.Select(a => a.ToString()).ToArray();

            _logger.LogInformation("DNS resolved {Hostname} to {Addresses}", hostname, string.Join(", ", addressList));

            return new OkObjectResult(new
            {
                hostname,
                addresses = addressList
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "DNS resolution failed for {Hostname}", hostname);

            return new ObjectResult(new
            {
                hostname,
                error = ex.Message
            })
            { StatusCode = 502 };
        }
    }
}
