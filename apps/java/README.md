# Azure Functions Java Reference App

> Planned reference implementation for Java annotation-based model.

## Status

This app is under development. See the [Java Language Guide](../../docs/language-guides/java/index.md) for current documentation.

## Planned Structure

```
apps/java/
├── src/main/java/com/functions/
│   ├── HealthFunction.java
│   ├── HttpTriggerFunction.java
│   ├── TimerTriggerFunction.java
│   └── QueueTriggerFunction.java
├── host.json
├── local.settings.json.example
└── pom.xml
```

## Quick Start (Coming Soon)

```bash
cd apps/java
mvn clean package
func host start
```
