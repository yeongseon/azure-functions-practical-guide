---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/security-concepts
---
# Controlled Lab Endpoints

The reference applications are teaching samples, not hardened public services. Run fault injection only in a disposable Function App and storage account, restrict inbound access to lab operators, and protect Application Insights/log access. These safeguards address a source/configuration risk; local tests do not prove the access policy of any deployed app.

## Enable an Experiment

Python and Node.js register `diagnostics/*`, `durable/start-replay-lab`, `durable/status/{instanceId}`, and `exceptions/*` HTTP routes only when `LAB_ENDPOINTS_ENABLED` is exactly the string `true`. Otherwise those routes are absent. The simple `/api/health` endpoint remains anonymous. Other teaching endpoints and non-HTTP triggers are not gated by this switch.

For local use, set `"LAB_ENDPOINTS_ENABLED": "true"` in `local.settings.json` under `Values`, then restart the host. Core Tools normally skips key authentication locally: bind only to localhost, or use `func start --enableAuth` to exercise host authorization. Handler tests and binding-metadata checks are not HTTP authorization tests.

For an isolated Azure lab, enable the setting after deploying current source:

```bash
az functionapp config appsettings set --resource-group "$RG" --name "$APP_NAME" --settings LAB_ENDPOINTS_ENABLED=true --output none
```

| Command/Parameter | Purpose |
|---|---|
| `az functionapp config appsettings set` | Enable lab HTTP registration on this disposable app. |
| `--resource-group` | Lab resource group. |
| `--name` | Lab Function App. |
| `--settings` | Exact opt-in value; an app-setting change restarts the app. |
| `--output` | Suppress configuration output. |

Enabled Python/Node.js lab routes require a function key on Azure. The .NET `/api/dns/{hostname}`, `/api/identity`, `/api/storage/probe`, `/api/slow`, `/api/testerror`, and `/api/unhandlederror` routes now require function authorization too; .NET does not use the registration switch. Its `/api/health` stays anonymous. Use a function-scoped key where possible, keep it out of source/history, and supply it through `x-functions-key`, not URL query strings. Keys are a minimal shared-secret boundary, not individual-user authorization or a substitute for network isolation.

Read the appropriate function key from the Portal's **Function keys** blade into a protected shell variable without echoing it:

```bash
read -r -s -p 'Function key: ' FUNCTION_KEY
curl --header "x-functions-key: $FUNCTION_KEY" \
  "https://${APP_NAME}.azurewebsites.net/api/diagnostics/slow-response?delay_ms=0"
```

For Azure access verification, separately check that no-key calls are denied, authorized calls work, and `/api/health` remains reachable under the intended network policy. None of these deployed checks was performed for this hardening change.

## Workload Limits

Python and Node.js replay starters accept an empty body or a JSON object up to **4096 UTF-8 bytes**. Malformed JSON/non-object bodies and invalid fields return **400**; oversized bodies return **413**, before any orchestration starts.

| Input | Allowed values |
|---|---|
| `instances` | Integer 1–10; default 1. |
| `iterations` | Integer 1–5000; default `DurableLab__Iterations` or 100. |
| `continueAsNewEvery` | Integer 0–5000; default `DurableLab__ContinueAsNewEvery` or 0. Explicit 0 disables resets even if the setting is nonzero. |
| Total scheduled activity calls | `instances * iterations` must be at most 5000 per request, across all ContinueAsNew batches. |
| `delay_ms` | Decimal integer 0–25000 on Python/Node.js slow-response routes, default 3000. |
| .NET `delay` | Integer 0–25 seconds, default 2. |

Numeric strings, booleans, nulls, non-integral numbers, negatives and nonfinite values are not valid JSON workload integers. Limits are per request, not global throttling: repeated authorized calls still incur cost. The recorded single-instance 50/2000-iteration runs and reset interval 250 remain supported. Container names and identity client IDs are no longer returned by probes; backend failures return a generic message. Retrieve diagnostic error detail from access-controlled operator logs, never paste raw backend errors or keys into public evidence.

## Clean Up

Stop load generators first. Wait for or terminate active Durable instances using operator tooling, then purge completed history if retaining the app. Disabling registration does **not** cancel already-started orchestrations; their workers remain registered to let them drain. Reset artificial delays and restore injected network/RBAC changes using the relevant lab's cleanup instructions.

```bash
az functionapp config appsettings delete --resource-group "$RG" --name "$APP_NAME" --setting-names LAB_ENDPOINTS_ENABLED --output none
unset FUNCTION_KEY
```

| Command/Parameter | Purpose |
|---|---|
| `az functionapp config appsettings delete` | Remove Python/Node.js opt-in and restart without lab HTTP routes. |
| `--resource-group` | Lab resource group. |
| `--name` | Lab Function App. |
| `--setting-names` | Registration switch to remove. |
| `--output` | Suppress configuration output. |

For .NET, stop/delete the disposable deployment when experiments finish. Rotate/delete any experiment keys. Delete the disposable resource group only after confirming it contains no shared resources. The unsafe historical Python ZIP has been removed from the repository; always publish current source rather than reusing an old deployment archive.

## See Also

- [Durable replay storm lab](../troubleshooting/lab-guides/durable-replay-storm.md)
- [DNS/VNet resolution lab](../troubleshooting/lab-guides/dns-vnet-resolution.md)

## Sources

- [HTTP trigger authorization](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger#authorization-level)
- [Run functions locally](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
- [Azure Functions security concepts](https://learn.microsoft.com/en-us/azure/azure-functions/security-concepts)
