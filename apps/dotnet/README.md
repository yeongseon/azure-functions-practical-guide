# Azure Functions .NET Reference App

Diagnostics (`dns/*`, `identity`, `storage/probe`, `slow`) and exception-injection routes (`testerror`, `unhandlederror`) require function keys on Azure; health remains anonymous. See [controlled lab endpoint setup and cleanup](../../docs/reference/lab-endpoint-safety.md). Local Core Tools normally skips key authorization. Slow-response `delay` must be 0–25 integer seconds.

Azure Functions .NET 8 isolated worker reference application for the practical guide.

## Trigger and Binding Coverage

- **HTTP** triggers: health, info, helloHttp, log-levels, slow response, external dependency, exception testing, diagnostics (storage probe, DNS resolve, identity probe)
- **Queue** trigger: `queueProcessor` — processes messages from `incoming-orders` queue
- **Timer** triggers: `scheduledCleanup` (daily at 2 AM), `timerLab` (every 5 min)
- **Blob** trigger: `blobProcessor` — blob trigger on `uploads/{name}`
- **Event Hub** trigger: `eventhubLagProcessor` — event stream processor

## Functions (16 total)

### HTTP Triggers
| Function | Route | Description |
|---|---|---|
| `health` | `GET /api/health` | Health check endpoint |
| `helloHttp` | `GET /api/hello/{name}` | Basic greeting with optional name |
| `info` | `GET /api/info` | Runtime environment details |
| `logLevels` | `GET /api/loglevels` | Multi-level logging demo |
| `slowResponse` | `GET /api/slow?delay=N` | Configurable latency endpoint |
| `testError` | `GET /api/testerror` | Intentional error for diagnostics |
| `unhandledError` | `GET /api/unhandlederror` | Unhandled exception simulation |
| `dnsResolve` | `GET /api/dns/{hostname}` | DNS resolution probe |
| `identityProbe` | `GET /api/identity` | Managed identity check |
| `storageProbe` | `GET /api/storage/probe` | Bounded, read-only Blob service connectivity request (not host health) |
| `externalDependency` | `GET /api/dependency` | External URL latency check |

### Non-HTTP Triggers
| Function | Type | Description |
|---|---|---|
| `scheduledCleanup` | Timer (`0 0 2 * * *`) | Daily cleanup job |
| `timerLab` | Timer (`0 */5 * * * *`) | 5-minute interval lab |
| `queueProcessor` | Queue (`incoming-orders`) | Queue message processor |
| `blobProcessor` | Blob (`uploads/{name}`) | Blob upload processor |
| `eventhubLagProcessor` | EventHub (`events`) | Event stream processor |

### Shared Utilities
| Class | Description |
|---|---|
| `AppConfig` | Environment configuration singleton |

## Prerequisites

- .NET SDK 8.0 or later
- Azure Functions Core Tools v4
- Azure CLI (for deployment and validation)
- Azurite (for local storage bindings)

## Quick Start

```bash
cd apps/dotnet
cp local.settings.json.example local.settings.json
dotnet build
func start
```

Test endpoints:

```bash
curl http://localhost:7071/api/health
curl http://localhost:7071/api/hello/World
curl http://localhost:7071/api/info
```

## Storage Probe Contract

`GET /api/storage/probe` performs a real, read-only Blob service request, not just a configuration check. It calls **List Containers** at the configured Blob service root (`GET /?comp=list&maxresults=1`), reads only the first page, and discards container names and continuation tokens. Identity authentication requires **Storage Blob Data Reader** at storage-account scope for this operation. This does not replace the separate roles required by the Functions host or triggers.

- A nonblank `AzureWebJobsStorage` connection string takes precedence, including `UseDevelopmentStorage=true` for Azurite. A malformed value returns `configuration: invalid`; it is never reclassified as identity authentication.
- Without a connection string, `AzureWebJobsStorage__accountName` selects `https://<account-name>.blob.core.windows.net`. `AzureWebJobsStorage__blobServiceUri` supports an explicit HTTPS Blob endpoint. The worker configuration provider maps double underscores to colons.
- `AzureWebJobsStorage__credential=managedidentity` selects managed identity, optionally with `__clientId` or `__managedIdentityResourceId` (not both). Without `__credential`, the SDK default credential chain can use local developer credentials. Setting only `__credential` without an account or Blob endpoint is not sufficient.
- The Blob request has **zero retries**, a **3-second network timeout**, and a **3-second cancellation budget** covering credential acquisition and the service call. A per-invocation transport guard permits only one Blob transport call, including when authentication challenges would otherwise replay the request; the default HTTP transport also disables redirects. A blocked challenge replay reports the original 401 as `authenticationFailed`. Credential discovery may involve identity-provider requests in addition to the single Blob service request. No storage resources are created, changed or deleted.
- Responses and endpoint logs contain only fixed state labels, never connection strings, keys, tokens, account/container names, tenant details, SDK exception messages or raw service errors. The endpoint requires a function key on Azure; also restrict network access to the isolated lab.

| HTTP status | `configuration` | `verification` | Interpretation |
|---|---|---|---|
| 200 | `configured` | `succeeded` | The single Blob list request succeeded; not a claim about all storage services, host locks, triggers or write permissions |
| 503 | `notConfigured` | `notRun` | Neither a connection string nor an identity account/Blob endpoint was supplied |
| 503 | `invalid` | `notRun` | Client configuration could not be constructed; no Blob request was made |
| 502 | `configured` | `authenticationFailed` | Credential acquisition failed or the service returned HTTP 401 |
| 502 | `configured` | `credentialUnavailable` | No usable credential was available |
| 502 | `configured` | `accessDenied` | Service returned HTTP 403; RBAC, firewall or another access policy is not distinguished |
| 502 | `configured` | `endpointUnavailable` | Transport failure or HTTP 408/5xx; the underlying network/DNS/service cause is not established |
| 502 | `configured` | `requestFailed` | Another unsuccessful service response was received |
| 502 | `configured` | `invalidResponse` | A response could not be parsed/deserialized; response content and exception text are not returned or logged |
| 504 | `configured` | `timedOut` / `cancelled` | The probe budget expired or the caller cancelled; no success is claimed |

`connectionType` is `connectionString`, `identity`, or `none`. `configured` means settings were present and the client was constructed, not that authentication or connectivity succeeded. Use `verification` and the HTTP status together.

### Local Tests

From the repository root:

```bash
dotnet build tests/dotnet/AzureFunctionsGuide.Tests.csproj
dotnet test tests/dotnet/AzureFunctionsGuide.Tests.csproj --no-build
```

The tests use an in-memory HTTP transport and synthetic credentials for shared-key, identity, refused requests, missing settings, service failures, secret-safe responses and timeout behavior. Regression cases assert a 401 challenge makes exactly one transport call and malformed XML/typed values return sanitized failures with captured endpoint logs containing no sensitive sentinel or exception. The targeted `.NET Tests` workflow builds and runs these tests on PR changes to the .NET app, tests or workflow. They do not contact Azure or prove deployed managed identity, Storage RBAC, network paths or host lock health. This change has source/local-test verification only; no live Azure validation is claimed and no tutorial validation dates are updated.

## Deploy to Azure

```bash
export APP_NAME="your-function-app-name"
export RG="your-resource-group"
dotnet publish --configuration Release --output ./publish
cd publish
func azure functionapp publish "$APP_NAME"
```

## Project Structure

```
apps/dotnet/
├── Functions/
│   ├── BlobProcessorFunction.cs
│   ├── DnsResolveFunction.cs
│   ├── EventHubLagProcessorFunction.cs
│   ├── ExternalDependencyFunction.cs
│   ├── HealthFunction.cs
│   ├── HelloHttpFunction.cs
│   ├── IdentityProbeFunction.cs
│   ├── InfoFunction.cs
│   ├── LogLevelsFunction.cs
│   ├── QueueProcessorFunction.cs
│   ├── ScheduledCleanupFunction.cs
│   ├── SlowResponseFunction.cs
│   ├── StorageProbeFunction.cs
│   ├── TestErrorFunction.cs
│   ├── TimerLabFunction.cs
│   └── UnhandledErrorFunction.cs
├── Shared/
│   ├── AppConfig.cs
│   └── StorageProbe.cs
├── Program.cs
├── host.json
├── local.settings.json.example
├── .funcignore
├── .gitignore
└── AzureFunctionsGuide.csproj
```

## Notes

- The `eventhubLagProcessor` function requires a valid `EventHubConnection` app setting. Without it, the host enters an error state. Set a placeholder connection string.
- The `blobProcessor` uses the standard polling blob trigger — for Flex Consumption plans, consider using Event Grid-based blob triggers.
- The .NET isolated worker model uses `HttpRequest` / `IActionResult` from ASP.NET Core via `ConfigureFunctionsWebApplication()`.

## See Also

- [Storage connectivity and host permissions](../../docs/platform/storage-connectivity.md)
- [Focused local storage probe tests](../../tests/dotnet/StorageProbeTests.cs)

## Sources

- [Functions connection management and identity settings](https://learn.microsoft.com/en-us/azure/azure-functions/manage-connections)
- [List Containers: request and authorization requirements](https://learn.microsoft.com/en-us/rest/api/storageservices/list-containers2)
- [Azure Storage .NET retry configuration](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-retry-policy)
