# Azure Functions Node.js Reference App

## Coming Soon — Reference App

This directory is reserved for the Node.js reference implementation using the Azure Functions v4 programming model.
Until the app is published, use the [Node.js Language Guide](../../docs/language-guides/nodejs/index.md) for architecture and runtime guidance.

## Status

Planned implementation. The repository will include production-style trigger and binding patterns, configuration defaults, and operational hooks.

## Planned Trigger and Binding Coverage

- **HTTP** trigger for health, diagnostics, and API patterns
- **Queue** trigger for asynchronous backlog processing
- **Timer** trigger for scheduled maintenance and batch jobs
- **Blob** trigger and blob input/output bindings for file workflows

Each function will demonstrate:

- Input validation and structured error responses
- Dependency initialization at module scope for cold-start control
- Configuration through environment variables and app settings
- Logging patterns compatible with Application Insights queries

## Planned Structure

```
apps/nodejs/
├── src/
│   ├── functions/
│   │   ├── health.js
│   │   ├── http-api.js
│   │   ├── queue-consumer.js
│   │   ├── timer-maintenance.js
│   │   └── blob-processor.js
│   ├── shared/
│   │   ├── config.js
│   │   ├── telemetry.js
│   │   └── clients.js
│   └── index.js
├── host.json
├── local.settings.json.example
├── .funcignore
└── package.json
```

## Prerequisites

- Node.js 20 or later
- Azure Functions Core Tools v4
- Azure CLI (for cloud validation)
- Azurite (for local storage trigger testing)

## Quick Start (Planned)

```bash
cd apps/nodejs
npm install
func host start
```

## Contributing

This app is intentionally staged as a planned implementation.
If you want to help build it, open a PR with a focused capability (for example, one trigger + tests + docs), and include links to related guidance in `docs/language-guides/nodejs/`.
