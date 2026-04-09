# Azure Functions .NET Reference App

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
| `storageProbe` | `GET /api/storage/probe` | Storage connectivity check |
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
│   └── AppConfig.cs
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
