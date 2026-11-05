---
validation:
  az_cli:
    last_tested: 2026-04-10
    cli_version: 2.83.0
    core_tools_version: 4.8.0
    result: pass
  bicep:
    last_tested:
    result: not_tested
content_sources:

  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-node
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-node
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
  diagrams:
    - id: what-you-ll-build
      type: flowchart
      source: self-generated
      justification: Flow view of what you ll build, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-node
        - https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-node
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-host-json
        - https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan
---
# 03 - Configuration (Dedicated)

Manage environment settings, runtime options, and host behavior per environment.

## Prerequisites

- You completed [02 - First Deploy](02-first-deploy.md).
- Your function app `$APP_NAME` is deployed and running on the Dedicated plan.

## What You'll Build

- Apply required app settings for the Node.js worker and runtime extension.
- Tune host-level timeout behavior appropriate for Dedicated plan characteristics.
- Validate effective settings in Azure.

!!! info "Infrastructure Context"
    **Plan**: Dedicated (B1) | **Timeout**: Unlimited (`-1`) | **Always On**: ✅

    Dedicated plans support unlimited function timeout (`functionTimeout: -1`), unlike Consumption (5/10 min) and Premium (30/60 min defaults). This makes Dedicated ideal for long-running workloads.

    <!-- diagram-id: what-you-ll-build -->
```mermaid
flowchart TD
    accTitle: Node.js Dedicated B1 configuration categories
    accDescr: Azure CLI updates app settings on the Dedicated B1 app. The configuration group also lists Node.js heap tuning and the separate host.json timeout; R, E, M and T refer to the adjacent key.
    CLI[Azure CLI] -->|appsettings set| FA[Function App\nDedicated B1]

    subgraph CONFIG["Configuration"]
        RT["R: Worker runtime<br/>node"]
        EXT["E: Functions runtime<br/>~4"]
        MEM["M: Node.js heap<br/>4096 MB example"]
        TIMEOUT["T: host.json timeout<br/>-1 (unbounded)"]
        %% Layout-only links tier categories; they add no configuration steps or semantic arrows.
        RT ~~~ EXT
        EXT ~~~ MEM
        MEM ~~~ TIMEOUT
    end

    FA --> CONFIG

    style FA fill:#ff8c00,color:#fff
```

| Key | Configuration shown |
|---|---|
| R | App setting `FUNCTIONS_WORKER_RUNTIME=node` selects the Node.js worker. |
| E | App setting `FUNCTIONS_EXTENSION_VERSION=~4` selects Functions runtime 4.x, not the Node.js programming-model version. |
| M | `node --max-old-space-size=4096`, passed through `languageWorkers__node__arguments`, is the tutorial's heap-limit example, not a recommendation for B1's available memory. |
| T | The tutorial sets `functionTimeout: -1` (unbounded) in `host.json`; an environment-specific override can instead use the app setting `AzureFunctionsJobHost__functionTimeout`. Unbounded execution on Dedicated requires Always On and remains subject to platform shutdowns and the separate HTTP response limit. |

**Reading key:** The group classifies configuration, not physical containment or execution order. Enable Always On for reliable non-HTTP triggering on Dedicated hosting; an HTTP request or Portal access can wake an idled app without it.

## Steps

1. Configure app settings.

    ```bash
    az functionapp config appsettings set \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --settings \
        "FUNCTIONS_WORKER_RUNTIME=node" \
        "FUNCTIONS_EXTENSION_VERSION=~4" \
        "languageWorkers__node__arguments=--max-old-space-size=4096"
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az functionapp config appsettings set` |
    | Key flags | `--name`, `--resource-group`, `--settings`, `--max-old-space-size` |
    | Variables | `$APP_NAME`, `$RG` |
    | Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


    Expected output (abridged):

    ```text
    Name                                    SlotSetting    Value
    --------------------------------------  -------------  -------------------------
    FUNCTIONS_WORKER_RUNTIME                False          node
    FUNCTIONS_EXTENSION_VERSION             False          ~4
    languageWorkers__node__arguments        False          --max-old-space-size=4096
    ```

    !!! tip "FUNCTIONS_WORKER_RUNTIME on Dedicated"
        On Dedicated plans, `FUNCTIONS_WORKER_RUNTIME` can be set via `az functionapp config appsettings set` without issues. On Flex Consumption, this setting is platform-managed and cannot be changed via CLI.

2. Configure host timeout.

    The `host.json` file in your project root controls timeout behavior. For Dedicated plans, set `functionTimeout` to `-1` for unlimited execution:

    ```json
    {
      "version": "2.0",
      "functionTimeout": "-1"
    }
    ```

    !!! warning "Timeout values by plan"
        | Plan | Default Timeout | Maximum |
        |---|---|---|
        | Consumption | 5 min | 10 min |
        | Premium | 30 min | 60 min (unlimited with `host.json`) |
        | Dedicated | 30 min | Unlimited (`-1`) |

3. Validate effective config.

    ```bash
    az functionapp config appsettings list \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --output table
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az functionapp config appsettings list` |
    | Key flags | `--name`, `--resource-group`, `--output` |
    | Variables | `$APP_NAME`, `$RG` |
    | Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


    Expected output (abridged):

    ```text
    Name                                         Value
    -------------------------------------------  -----------------------------------
    FUNCTIONS_WORKER_RUNTIME                     node
    FUNCTIONS_EXTENSION_VERSION                  ~4
    AzureWebJobsStorage                          DefaultEndpointsProtocol=https;...
    APPLICATIONINSIGHTS_CONNECTION_STRING        InstrumentationKey=...
    EventHubConnection__fullyQualifiedNamespace  placeholder.servicebus.windows.net
    QueueStorage                                 DefaultEndpointsProtocol=https;...
    WEBSITE_RUN_FROM_PACKAGE                     1
    languageWorkers__node__arguments             --max-old-space-size=4096
    ```

    !!! note "WEBSITE_RUN_FROM_PACKAGE"
        For a ready-to-run local ZIP on Dedicated, configure `WEBSITE_RUN_FROM_PACKAGE=1`; it is not an automatic plan-wide default. Do not manually force this setting when requesting remote build. Windows Consumption also supports `1`, Linux Consumption uses a package URL, and Flex must not receive the setting. See the [package matrix](../../../../operations/deployment.md#package-configuration-by-plan-and-os).

4. Review Dedicated-specific configuration notes.

    - **Always On**: Enable via portal or Bicep (`alwaysOn: true`) for non-HTTP triggers (timer, queue, blob). Without Always On, the app may idle and miss timer/queue events.
    - **No content share**: Unlike Premium and Consumption, Dedicated does not use `WEBSITE_CONTENTAZUREFILECONNECTIONSTRING` or `WEBSITE_CONTENTSHARE`.
    - **Memory tuning**: `--max-old-space-size=4096` sets Node.js heap to 4 GB. Adjust based on your B1 (1.75 GB RAM) or S1/P1v3 tier.

## Verification

The table confirms required Node.js worker settings are applied to the deployed app. Verify:

- `FUNCTIONS_WORKER_RUNTIME` is `node`
- `FUNCTIONS_EXTENSION_VERSION` is `~4`
- `languageWorkers__node__arguments` includes `--max-old-space-size`
- `WEBSITE_RUN_FROM_PACKAGE` is `1`

## See Also
- [Tutorial Overview & Plan Chooser](../index.md)
- [Node.js Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources
- [Azure Functions Node.js developer guide (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-node)
- [Create your first Azure Function with Core Tools (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-node)
- [Azure Functions hosting options (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [App settings reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings)
- [host.json reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-host-json)
- [Dedicated hosting and Always On (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan)
