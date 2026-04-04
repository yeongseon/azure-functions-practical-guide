# Azure Functions .NET Reference App

## Coming Soon — Reference App

This directory is reserved for the .NET isolated worker reference implementation.
Until the app is published, use the [.NET Language Guide](../../docs/language-guides/dotnet/index.md) for current platform, runtime, and design guidance.

## Status

Planned implementation. The final app will provide production-oriented patterns that mirror platform and operations guidance in this repository.

## Planned Trigger and Binding Coverage

- **HTTP** trigger for API endpoints, auth boundaries, and health probes
- **Queue** trigger for burst processing and retry behavior
- **Timer** trigger for scheduled workflows and housekeeping tasks
- **Blob** trigger and blob bindings for file ingestion pipelines

Coverage goals include:

- Isolated worker middleware and dependency injection composition
- Configuration layering for local and Azure environments
- Structured logging conventions for incident troubleshooting
- Example error handling paths with actionable diagnostics

## Planned Structure

```
apps/dotnet/
├── Functions/
│   ├── HealthFunction.cs
│   ├── HttpApiFunction.cs
│   ├── QueueConsumerFunction.cs
│   ├── TimerMaintenanceFunction.cs
│   └── BlobProcessorFunction.cs
├── Infrastructure/
│   ├── ServiceRegistration.cs
│   └── Options/
│       └── StorageOptions.cs
├── Program.cs
├── host.json
├── local.settings.json.example
├── .funcignore
└── azure-functions-dotnet.csproj
```

## Prerequisites

- .NET SDK 8.0 or later
- Azure Functions Core Tools v4
- Azure CLI (for deployment and validation)
- Azurite (for local storage bindings)

## Quick Start (Planned)

```bash
cd apps/dotnet
dotnet restore
func host start
```

## Contributing

This is a planned reference implementation, not a completed sample.
Contributions are welcome as incremental slices (single trigger path + tests + docs), with links back to `docs/language-guides/dotnet/` so guidance and implementation stay aligned.
