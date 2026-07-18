---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/migrate-dotnet-to-isolated-model
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/migrate-version-3-version-4
content_validation:
  status: verified
  last_reviewed: 2026-07-18
  reviewer: agent
  core_claims:
    - claim: "Migrating from Consumption (Y1) to Flex Consumption (FC1) requires creating a new function app; an in-place plan SKU change is not supported"
      source: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
      verified: true
    - claim: "The .NET in-process model is retired and .NET functions must run on the isolated worker model"
      source: https://learn.microsoft.com/en-us/azure/azure-functions/migrate-dotnet-to-isolated-model
      verified: true
    - claim: "The Python v2 programming model uses decorators instead of function.json for defining triggers and bindings"
      source: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python
      verified: true
    - claim: "The Dedicated (App Service) plan runs functions on fixed-capacity instances and does not provide event-driven dynamic scaling"
      source: https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan
      verified: true
    - claim: "Flex Consumption provides always-ready instances and per-function scaling as alternatives to Premium pre-warmed instances"
      source: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
      verified: true
---

# Migration Guide

Migrating an Azure Functions workload — whether across hosting plans or across programming models — is a day-2 operation performed against a running app. This guide provides the decision matrix, breaking-change tables, verification steps, and rollback procedures for each supported path, and links to the language-specific recipes for step-by-step code changes.

## Prerequisites

- An existing function app on the source plan or programming model.
- Azure CLI 2.60 or later with the current `functionapp` commands available.
- A staging slot or a secondary function app to enable a safe cutover (blue-green) rather than an in-place change.
- Application Insights enabled on both source and target so migration can be verified with telemetry.
- Source control access to the app code, so a redeploy of the previous version is always possible.

## When to Use

| Migration path | Typical trigger |
|---|---|
| Consumption (Y1) → Flex Consumption (FC1) | Need VNet integration, per-function scaling, or reduced cold start |
| .NET in-process → isolated worker | In-process model retirement; move to current .NET versions |
| Python v1 → v2 | Decorator model, blueprints, cleaner project layout |
| Premium ↔ Dedicated | Cost optimization, or adding/removing dynamic event-driven scale |

## Procedure

### Migration Decision Matrix

| Source → Target | New app required? | Expected downtime | Reversibility |
|---|---|---|---|
| Y1 → FC1 | Yes (create new FC1 app) | Cutover only (DNS/slot swap) | High — keep old app until validated |
| In-process → isolated | No (same app, code change) | Deploy window | Medium — redeploy previous package |
| Python v1 → v2 | No (same app, code change) | Deploy window | Medium — redeploy previous package |
| Premium ↔ Dedicated | No (change plan SKU) | Brief restart | High — change SKU back |

### Path 1: Consumption (Y1) → Flex Consumption (FC1)

- **Motivation.** Flex Consumption adds VNet integration, per-function scaling groups, always-ready instances, and faster cold start compared to the legacy Consumption plan.
- **What changes.** There is no in-place SKU conversion from Y1 to FC1 — you create a new Flex Consumption app and deploy your code to it, then cut traffic over. Deployment uses a storage container for the app package rather than the legacy content share.
- **App settings delta.**

    | Setting | Y1 | FC1 |
    |---|---|---|
    | `WEBSITE_CONTENTAZUREFILECONNECTIONSTRING` | Required | Not used (no content share) |
    | `WEBSITE_CONTENTSHARE` | Required | Not used |
    | Deployment | Zip to content share / `RUN_FROM_PACKAGE` | Zip to deployment storage container |
    | Scaling | Automatic, per-app | Per-function scaling groups, configurable maximum instances |

- **Steps (high level).** Create the FC1 app and its deployment storage container, deploy the code package, validate on the new hostname, then cut over DNS or swap slots.
- **Breaking changes.** In-portal `function.json` editing is not part of the Flex workflow; the scaling model differs, so revisit any assumptions baked into per-instance concurrency.

### Path 2: .NET In-Process → Isolated Worker

- **Motivation.** The in-process model is retired; the isolated worker model is the supported path and unlocks current .NET versions, full control of the middleware pipeline, and standard `Program.cs` startup.
- **Breaking-change summary.**

    | Area | In-process | Isolated worker |
    |---|---|---|
    | Host coupling | Shares the host runtime | Separate worker process |
    | Startup | `Startup.cs` (`FunctionsStartup`) | `Program.cs` with `HostBuilder` |
    | HTTP types | `HttpRequest` / `IActionResult` | `HttpRequestData` / `HttpResponseData` |
    | Middleware | Limited | First-class middleware pipeline |
    | DI lifetimes | Host-managed | Worker-managed |

- **Step-by-step.** Follow [Migrate .NET In-Process to Isolated Worker](../language-guides/dotnet/recipes/migrate-to-isolated.md) for the project file, `Program.cs`, function signature, and configuration changes.

### Path 3: Python v1 → v2

- **Motivation.** The v2 programming model replaces per-function `function.json` files with decorators, supports blueprints for modular apps, and gives a cleaner, type-hinted project layout.
- **Breaking-change summary.**

    | Area | v1 | v2 |
    |---|---|---|
    | Trigger/binding definition | `function.json` per function | Python decorators in code |
    | App entry point | Folder-per-function | Single app object (`func.FunctionApp()`) with blueprints |
    | Project layout | One folder per function | Consolidated modules |

- **Step-by-step.** Follow the [Python v2 Programming Model](../language-guides/python/v2-programming-model.md) page for the decorator syntax and project restructuring.

### Path 4: Premium ↔ Dedicated

- **When to move.** Choose Dedicated to reuse an existing App Service estate or to run on fixed, predictable capacity; choose Premium to keep event-driven dynamic scale with pre-warmed instances and enterprise networking.
- **Configuration deltas.** Moving to Dedicated changes the plan SKU and removes event-driven dynamic scaling — you manage instance count and rely on "Always On" instead of pre-warmed instances. Moving to Premium restores dynamic scale-out and always-ready instances. Re-validate VNet integration and cold-start expectations after the change, as they differ between the two plans.

## Verification

- Confirm the plan and SKU with `az functionapp show --resource-group $RG --name $APP_NAME --query "sku" --output tsv` (and the plan resource for dedicated/premium).
- In Application Insights, run a `requests` query to confirm executions are succeeding on the target with expected `resultCode` values.
- Smoke-test each critical trigger (HTTP, queue, timer) against the migrated app.
- Compare latency and error rate before and after migration in Application Insights to catch regressions early.

## Rollback / Troubleshooting

- **Plan/app migrations (Y1→FC1, Premium↔Dedicated).** Keep the source app or previous SKU until the target is validated; roll back by cutting DNS/slot traffic to the source app or changing the SKU back.
- **Model migrations (in-process→isolated, v1→v2).** Roll back by redeploying the previous package from source control.
- **Common failure: missing app settings after migration.** Diff the source and target app settings; settings such as connection strings and feature flags are not copied automatically to a new app.
- **Common failure: binding extension version mismatch.** After a model change, confirm the extension bundle or NuGet extension versions match what the new model expects.

## See Also

- [Hosting Plan Selection](../best-practices/hosting-plan-selection.md)
- [Deployment Scenarios](../platform/deployment-scenarios.md)
- [.NET Migrate to Isolated Worker](../language-guides/dotnet/recipes/migrate-to-isolated.md)
- [Python v2 Programming Model](../language-guides/python/v2-programming-model.md)
- [Operations: Deployment](deployment.md)

## Sources

- [Azure Functions Flex Consumption plan (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan)
- [Migrate .NET apps to the isolated worker model (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/migrate-dotnet-to-isolated-model)
- [Azure Functions Python developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Dedicated (App Service) plan for Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan)
- [Migrate apps to Azure Functions runtime version 4.x (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/migrate-version-3-version-4)
