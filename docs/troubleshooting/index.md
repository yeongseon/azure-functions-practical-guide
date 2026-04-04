# Troubleshooting

Use this section when Azure Functions workloads are degraded, failing, or behaving unexpectedly.
It is designed for incident response first, then root-cause analysis and prevention.

!!! tip "Operations Guide"
    For monitoring setup and alert configuration, see [Monitoring](../operations/monitoring.md) and [Alerts](../operations/alerts.md).

## What this section covers

- [First 10 Minutes](first-10-minutes.md): incident triage checklist for rapid stabilization.
- [Playbooks](playbooks.md): scenario runbooks with symptoms, diagnosis, and fixes.
- [Methodology](methodology.md): repeatable troubleshooting workflow for complex incidents.
- [KQL Query Library](kql.md): ready-to-use Application Insights and Log Analytics queries.
- [Lab Guides](lab-guides.md): hands-on failure simulations to practice response.

## Suggested incident flow

1. Start with [First 10 Minutes](first-10-minutes.md) to verify platform health and blast radius.
2. Move to [Playbooks](playbooks.md) for scenario-specific diagnosis paths.
3. Use [KQL Query Library](kql.md) to validate hypotheses with telemetry.
4. Apply [Methodology](methodology.md) to avoid guesswork and reduce MTTR.
5. Rehearse with [Lab Guides](lab-guides.md) to improve operational readiness.

## Scope and source policy

- Guidance in this section follows Microsoft Learn documentation for Azure Functions, App Service, Application Insights, and Azure Monitor.
- Product behavior, limits, and trigger specifics should always be validated against the linked Learn references.
- Examples use masked identifiers (`<subscription-id>`, `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`) to avoid exposing PII.

## See Also

- [Azure Functions documentation](https://learn.microsoft.com/azure/azure-functions/)
- [Azure Functions diagnostics](https://learn.microsoft.com/azure/azure-functions/functions-monitoring)
- [Application Insights for Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-monitoring#application-insights)
- [Scale and hosting options](https://learn.microsoft.com/azure/azure-functions/functions-scale)
