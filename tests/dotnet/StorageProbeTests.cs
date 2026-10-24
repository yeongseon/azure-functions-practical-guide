using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;
using Azure.Core;
using Azure.Core.Pipeline;
using Azure.Identity;
using AzureFunctionsGuide.Functions;
using AzureFunctionsGuide.Shared;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging.Abstractions;
using Xunit;

namespace AzureFunctionsGuide.Tests;

public sealed class StorageProbeTests
{
    private static readonly string SharedKey =
        "DefaultEndpointsProtocol=https;AccountName=examplestorage;AccountKey=" +
        Convert.ToBase64String(Encoding.UTF8.GetBytes("local-test-key-not-a-real-credential")) +
        ";EndpointSuffix=core.windows.net";

    [Fact]
    public async Task SharedKeyMakesOneReadOnlyRequestAndDoesNotReturnSecrets()
    {
        using var handler = new StorageHandler();
        var probe = Create(new() { ["AzureWebJobsStorage"] = SharedKey }, handler);
        var function = new StorageProbeFunction(NullLogger<StorageProbeFunction>.Instance, probe);

        var response = Assert.IsType<ObjectResult>(await function.Run(new DefaultHttpContext().Request));
        Assert.Equal(200, response.StatusCode);
        var result = Assert.IsType<StorageProbeResult>(response.Value);
        Assert.Equal(new StorageProbeResult("configured", "connectionString", "succeeded", 200), result);
        Assert.Equal(1, handler.Calls);
        Assert.Equal(HttpMethod.Get, handler.Method);
        Assert.Contains("comp=list", handler.Uri!.Query);
        Assert.Contains("maxresults=1", handler.Uri.Query);
        Assert.Equal("SharedKey", handler.AuthorizationScheme);
        var json = JsonSerializer.Serialize(result);
        Assert.DoesNotContain("examplestorage", json);
        Assert.DoesNotContain("AccountKey", json);
        Assert.DoesNotContain("private-container", json);
        Assert.DoesNotContain("StatusCode", json);
    }

    [Theory]
    [InlineData(null)]
    [InlineData("managedidentity")]
    public async Task IdentityAccountNameIsRecognizedWithoutConnectionString(string? credential)
    {
        using var handler = new StorageHandler();
        var result = await Create(new()
        {
            ["AzureWebJobsStorage:accountName"] = "examplestorage",
            ["AzureWebJobsStorage:credential"] = credential
        }, handler).RunAsync();

        Assert.Equal(new StorageProbeResult("configured", "identity", "succeeded", 200), result);
        Assert.Equal("examplestorage.blob.core.windows.net", handler.Uri!.Host);
        Assert.Equal("Bearer", handler.AuthorizationScheme);
        Assert.Equal(1, handler.Calls);
    }

    [Fact]
    public async Task EnvironmentDoubleUnderscoresMapToIdentityConfiguration()
    {
        const string prefix = "AZF170_TEST_";
        Environment.SetEnvironmentVariable(prefix + "AzureWebJobsStorage__accountName", "examplestorage");
        try
        {
            using var handler = new StorageHandler();
            using var http = new HttpClient(handler);
            var configuration = new ConfigurationBuilder().AddEnvironmentVariables(prefix).Build();
            var result = await new StorageProbe(configuration, new HttpClientTransport(http), new TestCredential())
                .RunAsync();
            Assert.Equal("identity", result.ConnectionType);
            Assert.Equal("succeeded", result.Verification);
        }
        finally
        {
            Environment.SetEnvironmentVariable(prefix + "AzureWebJobsStorage__accountName", null);
        }
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public async Task MissingSettingsDoNotSendRequest(string? connection)
    {
        using var handler = new StorageHandler();
        var result = await Create(new() { ["AzureWebJobsStorage"] = connection }, handler).RunAsync();
        Assert.Equal(new StorageProbeResult("notConfigured", "none", "notRun", 503), result);
        Assert.Equal(0, handler.Calls);
    }

    [Fact]
    public async Task RefusedRequestIsUnavailableNotConnectivitySuccess()
    {
        using var handler = new StorageHandler { Refuse = true };
        var result = await Create(new() { ["AzureWebJobsStorage"] = SharedKey }, handler).RunAsync();
        Assert.Equal(new StorageProbeResult("configured", "connectionString", "endpointUnavailable", 502), result);
        Assert.Equal(1, handler.Calls);
    }

    [Theory]
    [InlineData(401, "authenticationFailed")]
    [InlineData(403, "accessDenied")]
    [InlineData(503, "endpointUnavailable")]
    [InlineData(400, "requestFailed")]
    public async Task ServiceFailuresReportOnlyObservedStatus(int status, string verification)
    {
        using var handler = new StorageHandler { Status = (HttpStatusCode)status };
        var result = await Create(new() { ["AzureWebJobsStorage"] = SharedKey }, handler).RunAsync();
        Assert.Equal(verification, result.Verification);
        Assert.Equal(502, result.StatusCode);
        Assert.Equal(1, handler.Calls);
    }

    [Fact]
    public async Task InvalidConnectionStringDoesNotFallBackToIdentityOrSendRequest()
    {
        using var handler = new StorageHandler();
        var result = await Create(new()
        {
            ["AzureWebJobsStorage"] = "invalid-secret-value",
            ["AzureWebJobsStorage:accountName"] = "examplestorage"
        }, handler).RunAsync();
        Assert.Equal(new StorageProbeResult("invalid", "connectionString", "notRun", 503), result);
        Assert.Equal(0, handler.Calls);
    }

    [Fact]
    public async Task StalledRequestIsBoundedByTimeoutWithoutRetries()
    {
        using var handler = new StorageHandler { Stall = true };
        var result = await Create(new() { ["AzureWebJobsStorage"] = SharedKey }, handler).RunAsync()
            .WaitAsync(StorageProbe.Timeout + TimeSpan.FromSeconds(2));
        Assert.Equal("timedOut", result.Verification);
        Assert.Equal(504, result.StatusCode);
        Assert.Equal(1, handler.Calls);
    }

    [Fact]
    public async Task CredentialFailureDoesNotLeakExceptionDetails()
    {
        using var handler = new StorageHandler();
        var config = new ConfigurationBuilder().AddInMemoryCollection(new Dictionary<string, string?>
            { ["AzureWebJobsStorage:accountName"] = "examplestorage" }).Build();
        using var http = new HttpClient(handler);
        var result = await new StorageProbe(config, new HttpClientTransport(http), new TestCredential(true)).RunAsync();
        Assert.Equal("authenticationFailed", result.Verification);
        Assert.DoesNotContain("secret", JsonSerializer.Serialize(result));
        Assert.Equal(0, handler.Calls);
    }

    private static StorageProbe Create(Dictionary<string, string?> settings, StorageHandler handler) =>
        new(new ConfigurationBuilder().AddInMemoryCollection(settings).Build(),
            new HttpClientTransport(new HttpClient(handler)), new TestCredential());

    private sealed class TestCredential(bool fail = false) : TokenCredential
    {
        public override AccessToken GetToken(TokenRequestContext requestContext, CancellationToken cancellationToken) =>
            fail ? throw new AuthenticationFailedException("secret-tenant-details")
                : new AccessToken("local-test-token", DateTimeOffset.UtcNow.AddHours(1));

        public override ValueTask<AccessToken> GetTokenAsync(TokenRequestContext requestContext,
            CancellationToken cancellationToken) => new(GetToken(requestContext, cancellationToken));
    }

    private sealed class StorageHandler : HttpMessageHandler
    {
        public int Calls { get; private set; }
        public Uri? Uri { get; private set; }
        public HttpMethod? Method { get; private set; }
        public string? AuthorizationScheme { get; private set; }
        public HttpStatusCode Status { get; init; } = HttpStatusCode.OK;
        public bool Refuse { get; init; }
        public bool Stall { get; init; }

        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request,
            CancellationToken cancellationToken)
        {
            Calls++;
            Uri = request.RequestUri;
            Method = request.Method;
            AuthorizationScheme = request.Headers.Authorization?.Scheme;
            if (Refuse)
                throw new HttpRequestException("local simulated refusal", new SocketException((int)SocketError.ConnectionRefused));
            if (Stall)
                await Task.Delay(System.Threading.Timeout.InfiniteTimeSpan, cancellationToken);
            return new HttpResponseMessage(Status)
            {
                Content = new StringContent(Status == HttpStatusCode.OK
                    ? "<EnumerationResults><Containers><Container><Name>private-container</Name><Properties /></Container></Containers><NextMarker>more</NextMarker></EnumerationResults>"
                    : "<Error><Code>LocalTestFailure</Code><Message>secret-details</Message></Error>",
                    Encoding.UTF8, "application/xml")
            };
        }
    }
}
