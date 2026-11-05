---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/opentelemetry-howto
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring
  diagrams:
    - id: opentelemetry-export-flow
      type: flowchart
      source: self-generated
      justification: Flow view of OpenTelemetry export paths, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/opentelemetry-howto
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-host-json#telemetrymode
content_validation:
  status: verified
  last_reviewed: 2026-07-17
  reviewer: agent
  core_claims:
    - claim: "OpenTelemetry output is enabled at the function app level by adding telemetryMode set to OpenTelemetry in host.json."
      source: https://learn.microsoft.com/en-us/azure/azure-functions/opentelemetry-howto
      verified: true
    - claim: "When both an Application Insights connection string and an OTLP exporter are configured, OpenTelemetry data is sent to both endpoints."
      source: https://learn.microsoft.com/en-us/azure/azure-functions/opentelemetry-howto
      verified: true
    - claim: "OpenTelemetry is not supported for C# in-process apps."
      source: https://learn.microsoft.com/en-us/azure/azure-functions/opentelemetry-howto
      verified: true
    - claim: "When the host is configured to use OpenTelemetry, the Azure portal does not support log streaming."
      source: https://learn.microsoft.com/en-us/azure/azure-functions/opentelemetry-howto
      verified: true
---
# OpenTelemetry Export

Azure Functions can export logs and traces using OpenTelemetry instead of relying solely on the default Application Insights SDK path. The host can send telemetry to Application Insights, an OTLP-compliant backend, or both; worker export requires language-specific instrumentation and has destination limitations described below. The host.json reference marks `telemetryMode` as **preview**; assess that status before production use.

!!! tip "Related Guide"
    For the day-2 monitoring workflow with Application Insights, see [Monitoring](monitoring.md).

## Prerequisites

- A function app on a supported runtime (OpenTelemetry is **not** supported for C# in-process apps).
- Access to update `host.json` and application settings.
- A destination: an Application Insights resource, an OTLP endpoint, or both.

## When to Use

- You need to send Functions telemetry to a non-Azure observability backend.
- You want standards-based, correlated traces and logs across the host and worker processes.
- You are standardizing telemetry across a multi-service estate on OpenTelemetry semantics.

Stay with the default Application Insights SDK path if you only need Azure Monitor and portal features such as live log streaming.

## Export Paths

<!-- diagram-id: opentelemetry-export-flow -->
```mermaid
flowchart TD
    accTitle: OpenTelemetry export destination choices
    accDescr: Logical configuration view of host telemetry and separately instrumented worker telemetry. With telemetryMode set to OpenTelemetry, the host sends to Application Insights with its connection string, an OTLP backend with its endpoint, or both when both are set. Worker destinations depend on language-specific setup; see the reading key. This is not a shared exporter pipeline or a complete Yes/No decision tree.
    HOST["Functions host<br/>telemetry"] --> MODE{"telemetryMode =<br/>OpenTelemetry?"}
    WORKER["Worker process<br/>telemetry"] --> MODE
    MODE -->|AI only| AI["Application<br/>Insights"]
    MODE -->|OTLP only| OTLP["OTLP-compliant<br/>backend"]
    MODE -->|Both set| BOTH["Both endpoints"]
    %% Layout-only links tier destinations; they add no export paths or decisions.
    AI ~~~ OTLP
    OTLP ~~~ BOTH
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class HOST,WORKER,MODE,AI,OTLP,BOTH baseNeutral;
```

**Reading key:** With `telemetryMode` enabled, **AI only** means
`APPLICATIONINSIGHTS_CONNECTION_STRING` is set without an OTLP endpoint;
**OTLP only** means `OTEL_EXPORTER_OTLP_ENDPOINT` is set and the Application
Insights connection string is removed; **Both set** means both settings are
present. Configure provider-required authentication as well. The arrows summarize
configuration choices, not telemetry passing through a common exporter.

Worker setup is separate: follow the [language-specific instructions](https://learn.microsoft.com/en-us/azure/azure-functions/opentelemetry-howto#enable-opentelemetry-in-your-app)
for .NET isolated, Java, JavaScript/TypeScript, Python, PowerShell or Go.
C# in-process is unsupported. PowerShell worker OpenTelemetry output to
Application Insights is unsupported (worker logs are still forwarded by the host,
but distributed tracing is not supported there); Go worker middleware exports
through OTLP, requiring a forwarding pipeline to reach Azure Monitor.
The host setting alone does not establish worker instrumentation or support for
every runtime/hosting-plan combination; check the selected language and deployment
requirements rather than inferring them from this destination view.

## Procedure

### Step 1: Enable OpenTelemetry in the Host

Add `telemetryMode` to the root of `host.json`. This makes the host export OpenTelemetry regardless of language stack.

```json
{
    "version": "2.0",
    "telemetryMode": "OpenTelemetry"
}
```

### Step 2: Configure the Destination via App Settings

The app's environment variables determine where data is sent.

| App setting | Purpose |
|---|---|
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Sends OpenTelemetry data to an Application Insights workspace. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | The OTLP endpoint URL from your observability provider. |
| `OTEL_EXPORTER_OTLP_HEADERS` | Authentication headers (for example API keys) for the OTLP endpoint. |

When both an Application Insights connection string and an OTLP exporter are configured, data is sent to **both** endpoints. To export only to OTLP, remove `APPLICATIONINSIGHTS_CONNECTION_STRING`.

```bash
az functionapp config appsettings set --resource-group $RG --name $APP_NAME --settings OTEL_EXPORTER_OTLP_ENDPOINT="https://otlp.example-provider.com" OTEL_EXPORTER_OTLP_HEADERS="api-key=<redacted>"
```

| CLI element | Explanation |
|---|---|
| Command | `az functionapp config appsettings set` |
| Key flags | `--resource-group`, `--name`, `--settings` |
| Variables | `$RG`, `$APP_NAME`, provider endpoint and headers |
| Expected result | Settings applied; confirm they appear in the app configuration before validating export. |

### Step 3: Instrument the Worker Process

Enabling OpenTelemetry in both the host and the app code gives better trace/log correlation. Worker-side setup is language-specific — install the OpenTelemetry packages and register the exporter in your app's entry point (`Program.cs`, `function_app.py`, `src/index.js`, or Maven dependencies). See the language-specific instructions in the Microsoft Learn source below.

## Verification

- Confirm telemetry arrives at the configured backend (Application Insights or OTLP destination).
- In Application Insights, verify traces and logs correlate across the host and worker (shared operation IDs).
- Query for `instrumentation.provider == 'opentelemetry'` to confirm OpenTelemetry-sourced records.

## Rollback / Troubleshooting

- **Revert**: remove `telemetryMode` from `host.json` (or set it back to the default) to return to the Application Insights SDK path.
- **No log streaming**: when the host uses OpenTelemetry, the Azure portal does not support live log streaming — this is expected.
- **`logging.applicationInsights` ignored**: when `telemetryMode` is `OpenTelemetry`, the `logging.applicationInsights` section of `host.json` no longer applies.
- **Duplicate telemetry**: avoid adding a console exporter or the Azure Monitor distro in the worker when the host already emits equivalent telemetry.
- **Missing request telemetry**: with parent-based sampling, requests whose incoming `traceparent` is not sampled will not generate request telemetry.
- **Recent invocations view**: the portal's *Recent function invocation* traces appear only when telemetry is sent to Azure Monitor.

## See Also

- [Monitoring](monitoring.md)
- [Alerts](alerts.md)
- [Configuration](configuration.md)

## Sources

- [Use OpenTelemetry with Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/opentelemetry-howto)
- [host.json telemetryMode reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-host-json#telemetrymode)
- [Monitor Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring)
