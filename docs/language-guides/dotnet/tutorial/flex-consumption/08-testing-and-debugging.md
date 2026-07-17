---
validation:
  az_cli:
    last_tested:
    result: not_tested
  bicep:
    last_tested:
    result: not_tested
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-develop-local
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/dotnet-isolated-process-guide
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local
---
# 08 - Testing and Local Debugging (Flex Consumption)

Unit-test your .NET isolated-worker functions with xUnit, mock `HttpRequestData` and `FunctionContext`, run integration tests against Azurite, and attach the Visual Studio debugger to a running host.

## Prerequisites

| Tool | Minimum version | Purpose |
|---|---|---|
| .NET SDK | 8.0 | Build and run functions and tests |
| Azure Functions Core Tools | 4.x | Local host and debugging |
| xUnit + Moq | Latest | Test frameworks |
| Azurite | 3.x | Local Azure Storage emulator |
| Visual Studio / VS Code | Latest | Breakpoint debugging |

## What You'll Build

You will add an xUnit test project that unit-tests business logic, mocks the isolated-worker HTTP types, runs an Azurite integration test, and attaches the debugger to a running host.

## 1. Unit Test the Logic

Keep logic out of the trigger so it tests without Functions types.

```csharp
// Greeter.cs
public static class Greeter
{
    public static string Build(string? name) =>
        $"Hello, {(string.IsNullOrWhiteSpace(name) ? "world" : name.Trim())}!";
}
```

```csharp
// tests/GreeterTests.cs
using Xunit;

public class GreeterTests
{
    [Theory]
    [InlineData("  ada ", "Hello, ada!")]
    [InlineData(null, "Hello, world!")]
    public void Build_FormatsGreeting(string? input, string expected) =>
        Assert.Equal(expected, Greeter.Build(input));
}
```

```bash
dotnet test
```

## 2. Mock the Isolated-Worker HTTP Types

`HttpRequestData` and `HttpResponseData` are abstract, so mock a minimal `FunctionContext` with a service provider that supplies them.

```csharp
// tests/HttpFunctionTests.cs
using System.Net;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Http;
using Microsoft.Extensions.DependencyInjection;
using Moq;
using Xunit;

public class HttpFunctionTests
{
    private static FunctionContext Context()
    {
        var services = new ServiceCollection().BuildServiceProvider();
        var ctx = new Mock<FunctionContext>();
        ctx.SetupProperty(c => c.InstanceServices, services);
        return ctx.Object;
    }

    [Fact]
    public async Task Hello_Returns_Ok()
    {
        var context = Context();
        var request = new FakeHttpRequestData(context, query: "name=grace");
        var response = new HttpFunction().Run(request);
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
    }
}
```

!!! tip "Reuse a test double"
    Rather than mocking `HttpRequestData` repeatedly, write a small `FakeHttpRequestData : HttpRequestData` test double that exposes a settable query string and body stream, and reuse it across tests.

## 3. Integration Test Against Azurite

```bash
npm install -g azurite
azurite --silent --location ./.azurite &
```

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "dotnet-isolated"
  }
}
```

Use `Azure.Storage.Queues.QueueClient` with the `UseDevelopmentStorage=true` connection string inside an xUnit test to create a queue, send a message, receive it, and delete the queue — validating binding behavior without a real account.

## 4. Breakpoint Debugging with Core Tools

Start the host and attach the debugger:

```bash
func start
```

In Visual Studio choose **Debug > Attach to Process** and select the `func.exe` (or the isolated worker `dotnet` process). In VS Code use a `coreclr` attach configuration. Set a breakpoint in the function, then call `http://localhost:7071/api/hello?name=ada`.

!!! info "Flex Consumption note"
    Testing and debugging run entirely on your local machine and are identical across hosting plans. The Flex Consumption plan changes only how the deployed app scales and networks.

## Verification

- [ ] `dotnet test` reports all tests passing.
- [ ] The Azurite integration test round-trips a queue message without a real storage account.
- [ ] A breakpoint in the function is hit when you invoke the local endpoint.

## Next Steps

- Wire `dotnet test` into your pipeline — see [06 - CI/CD](06-ci-cd.md).
- Extend coverage to the triggers you added in [07 - Extending with Triggers](07-extending-triggers.md).

## See Also

- [Testing recipe](../../recipes/testing.md) — Framework-agnostic testing patterns
- [Run functions locally](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local) — Core Tools reference
- [07 - Extending with Triggers](07-extending-triggers.md)

## Sources

- [Code and test Azure Functions locally (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-develop-local)
- [Guide for running C# Azure Functions in an isolated worker process (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/dotnet-isolated-process-guide)
- [Use Azurite emulator for local Azure Storage development (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite)
</content>
