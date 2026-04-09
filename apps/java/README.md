# Azure Functions Java Reference App

Reference application demonstrating Azure Functions with the Java annotation-based programming model.

## Functions (14 total)

### HTTP Triggers
| Function | Route | Description |
|---|---|---|
| `helloHttp` | `GET /api/hello/{name}` | Basic greeting with optional name |
| `health` | `GET /api/health` | Health check endpoint |
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
| `scheduledCleanup` | Timer (`0 0 2 * * *`) | Nightly cleanup job |
| `timerLab` | Timer (`0 */5 * * * *`) | 5-minute interval lab |
| `queueProcessor` | Queue (`incoming-orders`) | Queue message processor |
| `blobProcessor` | Blob (`uploads/{name}`) | Blob upload processor |
| `eventhubLagProcessor` | EventHub (`telemetry-events`) | Event stream processor |

### Shared Utilities
| Class | Description |
|---|---|
| `AppConfig` | Environment configuration singleton |
| `Telemetry` | Structured logging helper |

## Prerequisites

- Java 17 or later
- Maven 3.6 or later
- Azure Functions Core Tools v4
- Azure CLI 2.61+

## Quick Start

```bash
cd apps/java
mvn clean package
mvn azure-functions:run
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
mvn clean package
mvn azure-functions:deploy
```

## Project Structure

```
apps/java/
├── src/main/java/com/functions/
│   ├── BlobProcessorFunction.java
│   ├── DnsResolveFunction.java
│   ├── EventHubLagProcessorFunction.java
│   ├── ExternalDependencyFunction.java
│   ├── HealthFunction.java
│   ├── HelloHttpFunction.java
│   ├── IdentityProbeFunction.java
│   ├── InfoFunction.java
│   ├── LogLevelsFunction.java
│   ├── QueueProcessorFunction.java
│   ├── ScheduledCleanupFunction.java
│   ├── SlowResponseFunction.java
│   ├── StorageProbeFunction.java
│   ├── TestErrorFunction.java
│   ├── TimerLabFunction.java
│   ├── UnhandledErrorFunction.java
│   └── shared/
│       ├── AppConfig.java
│       └── Telemetry.java
├── src/test/java/com/functions/
├── host.json
├── local.settings.json.example
└── pom.xml
```
