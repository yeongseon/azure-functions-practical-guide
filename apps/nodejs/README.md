# Azure Functions Node.js Reference App

> Planned reference implementation for Node.js v4 programming model.

## Status

This app is under development. See the [Node.js Language Guide](../../docs/language-guides/nodejs/index.md) for current documentation.

## Planned Structure

```
apps/nodejs/
├── src/
│   ├── functions/
│   │   ├── health.js
│   │   ├── httpTrigger.js
│   │   ├── timerTrigger.js
│   │   └── queueTrigger.js
│   └── index.js
├── host.json
├── local.settings.json.example
└── package.json
```

## Quick Start (Coming Soon)

```bash
cd apps/nodejs
npm install
func host start
```
