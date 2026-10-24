using System.Text.Json.Serialization;
using Azure;
using Azure.Core;
using Azure.Core.Pipeline;
using Azure.Identity;
using Azure.Storage.Blobs;
using Microsoft.Extensions.Configuration;

namespace AzureFunctionsGuide.Shared;

public sealed record StorageProbeResult(
    string Configuration, string ConnectionType, string Verification,
    [property: JsonIgnore] int StatusCode);

/// <summary>
/// Lists at most one container page (one item requested), without returning names.
/// Identity requires account-scoped Storage Blob Data Reader, not host write permissions.
/// </summary>
public sealed class StorageProbe
{
    public static readonly TimeSpan Timeout = TimeSpan.FromSeconds(3);
    private readonly IConfiguration _configuration;
    private readonly HttpPipelineTransport? _transport;
    private readonly TokenCredential? _credential;

    public StorageProbe(IConfiguration configuration, HttpPipelineTransport? transport = null,
        TokenCredential? credential = null)
    {
        _configuration = configuration;
        _transport = transport;
        _credential = credential;
    }

    public async Task<StorageProbeResult> RunAsync(CancellationToken cancellationToken = default)
    {
        var connectionString = _configuration["AzureWebJobsStorage"];
        var accountName = _configuration["AzureWebJobsStorage:accountName"];
        var blobUri = _configuration["AzureWebJobsStorage:blobServiceUri"];
        var connectionType = !string.IsNullOrWhiteSpace(connectionString) ? "connectionString"
            : !string.IsNullOrWhiteSpace(accountName) || !string.IsNullOrWhiteSpace(blobUri) ? "identity" : "none";
        if (connectionType == "none")
            return new("notConfigured", connectionType, "notRun", 503);

        var options = new BlobClientOptions();
        options.Retry.MaxRetries = 0;
        options.Retry.NetworkTimeout = Timeout;
        options.Diagnostics.IsLoggingEnabled = false;
        if (_transport is not null)
            options.Transport = _transport;

        BlobServiceClient client;
        try
        {
            if (connectionType == "connectionString")
                client = new BlobServiceClient(connectionString, options);
            else
            {
                if (string.IsNullOrWhiteSpace(blobUri) &&
                    (accountName is null || accountName.Length is < 3 or > 24 ||
                     accountName.Any(c => c is not (>= 'a' and <= 'z') and not (>= '0' and <= '9'))))
                    return new("invalid", connectionType, "notRun", 503);

                var endpoint = new Uri(blobUri ?? $"https://{accountName}.blob.core.windows.net");
                if (endpoint.Scheme != Uri.UriSchemeHttps || !string.IsNullOrEmpty(endpoint.UserInfo) ||
                    !string.IsNullOrEmpty(endpoint.Query) || !string.IsNullOrEmpty(endpoint.Fragment))
                    return new("invalid", connectionType, "notRun", 503);

                var credential = _configuration["AzureWebJobsStorage:credential"];
                var clientId = _configuration["AzureWebJobsStorage:clientId"];
                var resourceId = _configuration["AzureWebJobsStorage:managedIdentityResourceId"];
                if ((!string.IsNullOrWhiteSpace(credential) && credential != "managedidentity") ||
                    (!string.IsNullOrWhiteSpace(clientId) && !string.IsNullOrWhiteSpace(resourceId)))
                    return new("invalid", connectionType, "notRun", 503);

                TokenCredential tokenCredential;
                if (credential == "managedidentity")
                {
                    var identity = !string.IsNullOrWhiteSpace(clientId)
                        ? ManagedIdentityId.FromUserAssignedClientId(clientId)
                        : !string.IsNullOrWhiteSpace(resourceId)
                            ? ManagedIdentityId.FromUserAssignedResourceId(new ResourceIdentifier(resourceId))
                            : ManagedIdentityId.SystemAssigned;
                    tokenCredential = new ManagedIdentityCredential(identity);
                }
                else
                    tokenCredential = new DefaultAzureCredential(new DefaultAzureCredentialOptions
                    {
                        ManagedIdentityClientId = clientId,
                        ManagedIdentityResourceId = string.IsNullOrWhiteSpace(resourceId)
                            ? null : new ResourceIdentifier(resourceId)
                    });
                client = new BlobServiceClient(endpoint, _credential ?? tokenCredential, options);
            }
        }
        catch (Exception ex) when (ex is ArgumentException or FormatException or InvalidOperationException)
        {
            return new("invalid", connectionType, "notRun", 503);
        }

        using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        timeout.CancelAfter(Timeout);
        try
        {
            // MoveNextAsync only once: never enumerate further pages or mutate storage.
            await using var pages = client.GetBlobContainersAsync(cancellationToken: timeout.Token)
                .AsPages(pageSizeHint: 1).GetAsyncEnumerator(timeout.Token);
            await pages.MoveNextAsync();
            return new("configured", connectionType, "succeeded", 200);
        }
        catch (CredentialUnavailableException)
        {
            return new("configured", connectionType, "credentialUnavailable", 502);
        }
        catch (AuthenticationFailedException)
        {
            return new("configured", connectionType, "authenticationFailed", 502);
        }
        catch (RequestFailedException ex)
        {
            // A generic 403 can also be caused by a firewall: do not label it RBAC failure.
            var verification = ex.Status switch
            {
                401 => "authenticationFailed",
                403 => "accessDenied",
                0 or 408 or >= 500 => "endpointUnavailable",
                _ => "requestFailed"
            };
            return new("configured", connectionType, verification, 502);
        }
        catch (OperationCanceledException)
        {
            return new("configured", connectionType,
                cancellationToken.IsCancellationRequested ? "cancelled" : "timedOut", 504);
        }
        catch (HttpRequestException)
        {
            return new("configured", connectionType, "endpointUnavailable", 502);
        }
    }
}
