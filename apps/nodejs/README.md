# Azure Functions Node.js Reference App

Azure Functions v4 programming model reference application for the practical guide.

## Trigger and Binding Coverage

- **HTTP** triggers: health, info, helloHttp, log-levels, external dependency, exception testing, diagnostics (slow response, storage probe, DNS resolve, identity probe)
- **Queue** trigger: `queueProcessor` — processes messages from `work-items` queue with configurable delay
- **Timer** triggers: `scheduledCleanup` (every 5 min), `timerLab` (configurable via `TIMER_LAB_SCHEDULE`)
- **Blob** trigger: `blobProcessor` — Event Grid-based blob trigger on `uploads/{name}`
- **Event Hub** trigger: `eventhubLagProcessor` — checkpoint lag lab with artificial delay
- **Durable Functions**: `replayStormOrchestrator` — replay storm lab with configurable iterations

## Structure

```text
apps/nodejs/
├── src/
│   ├── functions/
│   │   ├── health.js           # Health check endpoint
│   │   ├── helloHttp.js        # Primary tutorial endpoint
│   │   ├── info.js             # Runtime info endpoint
│   │   ├── requests.js         # Log levels demonstration
│   │   ├── dependencies.js     # External HTTP dependency
│   │   ├── exceptions.js       # Exception handling demo
│   │   ├── diagnostics.js      # Slow response, storage/DNS/identity probes
│   │   ├── scheduled.js        # Timer trigger (every 5 min)
│   │   ├── queueProcessor.js   # Queue trigger with delay
│   │   ├── blobProcessor.js    # Blob trigger (Event Grid)
│   │   ├── timerLab.js         # Timer lab (configurable schedule)
│   │   ├── eventhubLab.js      # Event Hub checkpoint lag lab
│   │   └── durableLab.js       # Durable Functions replay storm lab
│   └── shared/
│       ├── config.js           # Environment variable settings
│       └── telemetry.js        # Azure Monitor OpenTelemetry setup
├── host.json
├── local.settings.json.example
├── .funcignore
├── .gitignore
└── package.json
```

## Prerequisites

- Node.js 20 or later
- Azure Functions Core Tools v4
- Azure CLI (for cloud validation)
- Azurite (for local storage trigger testing)

## Quick Start

```bash
cd apps/nodejs
npm install
cp local.settings.json.example local.settings.json
func host start
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `AZURE_FUNCTIONS_ENVIRONMENT` | `production` | Runtime environment |
| `TELEMETRY_MODE` | `basic` | Telemetry configuration mode |
| `LOG_LEVEL` | `info` | Application log level |
| `PROCESSING_DELAY_MS` | `0` | Artificial delay for queue processor (ms) |
| `TIMER_LAB_SCHEDULE` | `0 */2 * * * *` | Cron expression for timer lab |
| `EventHubLab__ArtificialDelayMs` | `0` | Artificial delay for Event Hub lab (ms) |
| `EventHubLab__LogCheckpointDelta` | `true` | Log checkpoint delta metrics |
| `DurableLab__Iterations` | `100` | Replay storm iterations |
| `DurableLab__ContinueAsNewEvery` | `0` | History reset frequency (0 = disabled) |

## Notes

- The `eventhubLab` function requires a valid `EventHubConnection` app setting. Without it, the host enters an error state. Set a placeholder or disable the function.
- The `blobProcessor` uses `source: 'EventGrid'` — it requires an Event Grid subscription to fire from blob uploads.
- The `scheduled.js` and `blobProcessor.js` are NOT registered in the main tutorials until Tutorial 07 (extending triggers). They are included here for reference.
