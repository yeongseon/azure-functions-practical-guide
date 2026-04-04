# Azure Functions Java Reference App

## Coming Soon — Reference App

This directory is reserved for the Java reference implementation using the annotation-based Azure Functions model.
Until the implementation is available, use the [Java Language Guide](../../docs/language-guides/java/index.md) for current recommendations.

## Status

Planned implementation. The app will focus on practical trigger coverage, operational readiness, and maintainable project organization.

## Planned Trigger and Binding Coverage

- **HTTP** trigger for API and health endpoints
- **Queue** trigger for asynchronous work-item processing
- **Timer** trigger for scheduled tasks and cleanup jobs
- **Blob** trigger/binding for file-driven processing flows

Reference scenarios will highlight:

- Shared service wiring and reuse across function classes
- Runtime-safe configuration loading via environment variables
- Consistent telemetry and error handling conventions
- Cloud-ready defaults that match repository operations guidance

## Planned Structure

```
apps/java/
├── src/main/java/com/functions/
│   ├── HealthFunction.java
│   ├── HttpApiFunction.java
│   ├── QueueConsumerFunction.java
│   ├── TimerMaintenanceFunction.java
│   └── BlobProcessorFunction.java
├── src/main/java/com/functions/shared/
│   ├── AppConfig.java
│   ├── Telemetry.java
│   └── Clients.java
├── src/test/java/com/functions/
│   └── FunctionTests.java
├── host.json
├── local.settings.json.example
└── pom.xml
```

## Prerequisites

- Java 17 or later
- Maven 3.9 or later
- Azure Functions Core Tools v4
- Azure CLI and Azurite for end-to-end validation

## Quick Start (Planned)

```bash
cd apps/java
mvn clean package
func host start
```

## Contributing

This is currently a planned reference app.
If you contribute, prefer small vertical slices (one trigger path with docs/tests) and link implementation decisions back to `docs/language-guides/java/` to keep guidance and code synchronized.
