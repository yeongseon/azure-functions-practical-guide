using System.Reflection;
using AzureFunctionsGuide.Functions;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging.Abstractions;
using Xunit;

namespace AzureFunctionsGuide.Tests;

public sealed class DiagnosticSecurityTests
{
    [Theory]
    [InlineData(typeof(DnsResolveFunction))]
    [InlineData(typeof(IdentityProbeFunction))]
    [InlineData(typeof(StorageProbeFunction))]
    [InlineData(typeof(SlowResponseFunction))]
    [InlineData(typeof(TestErrorFunction))]
    [InlineData(typeof(UnhandledErrorFunction))]
    public void DiagnosticHttpBindingsRequireFunctionKey(Type function)
    {
        var trigger = function.GetMethod("Run")!.GetParameters()[0]
            .GetCustomAttribute<HttpTriggerAttribute>();
        Assert.NotNull(trigger);
        Assert.Equal(AuthorizationLevel.Function, trigger.AuthLevel);
    }

    [Fact]
    public void HealthBindingRemainsAnonymous()
    {
        var trigger = typeof(HealthFunction).GetMethod("Run")!.GetParameters()[0]
            .GetCustomAttribute<HttpTriggerAttribute>();
        Assert.Equal(AuthorizationLevel.Anonymous, trigger!.AuthLevel);
    }

    [Theory]
    [InlineData("-1")]
    [InlineData("26")]
    [InlineData("2147483647")]
    [InlineData("1.5")]
    [InlineData("NaN")]
    public async Task InvalidDelayReturnsBadRequest(string delay)
    {
        var request = new DefaultHttpContext().Request;
        request.QueryString = new QueryString("?delay=" + delay);
        var function = new SlowResponseFunction(NullLogger<SlowResponseFunction>.Instance);
        Assert.IsType<BadRequestObjectResult>(await function.Run(request));
    }
}
