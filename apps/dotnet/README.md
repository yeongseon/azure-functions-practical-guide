# Azure Functions .NET Reference App

> Planned reference implementation for .NET isolated worker model.

## Status

This app is under development. See the [.NET Language Guide](../../docs/language-guides/dotnet/index.md) for current documentation.

## Planned Structure

```
apps/dotnet/
├── Functions/
│   ├── HealthFunction.cs
│   ├── HttpTriggerFunction.cs
│   ├── TimerTriggerFunction.cs
│   └── QueueTriggerFunction.cs
├── Program.cs
├── host.json
├── local.settings.json.example
└── azure-functions-dotnet.csproj
```

## Quick Start (Coming Soon)

```bash
cd apps/dotnet
dotnet restore
func host start
```
