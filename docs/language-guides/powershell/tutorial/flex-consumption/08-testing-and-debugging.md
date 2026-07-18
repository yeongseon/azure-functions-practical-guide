---
validation:
  az_cli:
    last_tested:
    result: not_tested
  bicep:
    last_tested:
    result: not_tested
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-develop-local
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local
---
# 08 - Testing and Local Debugging (Flex Consumption)

Unit-test your PowerShell function logic with Pester, mock output bindings, run integration tests against Azurite, and step through code with the PowerShell debugger.

## Prerequisites

| Tool | Minimum version | Purpose |
|---|---|---|
| PowerShell | 7.4 | Run function code and tests |
| Azure Functions Core Tools | 4.x | Local host and debugging |
| Pester | 5.x | Test framework |
| Azurite | 3.x | Local Azure Storage emulator |
| Visual Studio Code | Latest | Breakpoint debugging (optional) |

## What You'll Build

You will add Pester tests to the Flex Consumption app that unit-test greeting logic, mock the `Push-OutputBinding` call, run an Azurite integration test, and step through `run.ps1` with the VS Code PowerShell debugger.

## 1. Unit Test the Logic

Extract logic into a module function so Pester can test it without the Functions host.

```powershell
# Modules/Greeting/Greeting.psm1
function Build-Greeting {
    param([string] $Name)
    $value = if ([string]::IsNullOrWhiteSpace($Name)) { 'world' } else { $Name.Trim() }
    "Hello, $value!"
}
Export-ModuleMember -Function Build-Greeting
```

```powershell
# tests/Greeting.Tests.ps1
BeforeAll {
    Import-Module "$PSScriptRoot/../Modules/Greeting/Greeting.psm1" -Force
}

Describe 'Build-Greeting' {
    It 'trims and formats the name' {
        Build-Greeting -Name '  ada ' | Should -Be 'Hello, ada!'
    }
    It 'defaults to world' {
        Build-Greeting -Name '' | Should -Be 'Hello, world!'
    }
}
```

```powershell
Install-Module Pester -Scope CurrentUser -Force
Invoke-Pester ./tests
```

## 2. Mock Output Bindings

`Push-OutputBinding` is provided by the Functions worker. In a Pester test, mock it to assert what your `run.ps1` would send back.

```powershell
# tests/HttpTrigger.Tests.ps1
Describe 'HttpTrigger' {
    It 'pushes an OK response with the greeting' {
        Mock Push-OutputBinding {}

        $Request = [pscustomobject]@{ Query = @{ name = 'grace' } }
        . "$PSScriptRoot/../HttpTrigger/run.ps1"

        Should -Invoke Push-OutputBinding -Times 1 -ParameterFilter {
            $Value.StatusCode -eq [System.Net.HttpStatusCode]::OK
        }
    }
}
```

!!! tip "Make run.ps1 testable"
    Dot-source `run.ps1` inside the test so its `param($Request, $TriggerMetadata)` block executes against your fake `$Request`. Keep heavy logic in a module function that you can test independently.

## 3. Integration Test Against Azurite

```bash
npm install -g azurite
azurite --silent --location ./.azurite &
```

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "powershell",
    "FUNCTIONS_WORKER_RUNTIME_VERSION": "7.4"
  }
}
```

Use the `Az.Storage` module (or the .NET `QueueClient`) with `UseDevelopmentStorage=true` inside a Pester test to create a queue, send a message, read it back, and delete the queue — validating storage behavior without a real account.

## 4. Breakpoint Debugging with Core Tools

Start the host, then attach the VS Code PowerShell debugger:

```bash
func start --verbose
```

Add a breakpoint in `run.ps1`, open the **Run and Debug** panel, and choose **PowerShell: Attach to Host Process** (select the `pwsh` worker process). Invoke `http://localhost:7071/api/HttpTrigger?name=ada` to hit the breakpoint. You can also set `Set-PSBreakpoint` interactively.

!!! info "Flex Consumption note"
    Testing and debugging run entirely on your local machine and are identical across hosting plans. Note that managed dependencies (`requirements.psd1`) are **not** supported on Flex Consumption — bundle modules in a `Modules` folder, which also keeps your local test imports and deployed runtime consistent.

## Verification

- [ ] `Invoke-Pester ./tests` reports all tests passing.
- [ ] The output-binding mock asserts an OK response without a running host.
- [ ] A breakpoint in `run.ps1` is hit when you invoke the local endpoint.

## Next Steps

- Wire `Invoke-Pester` into your pipeline — see [06 - CI/CD](06-ci-cd.md).
- Extend coverage to the triggers you added in [07 - Extending with Triggers](07-extending-triggers.md).

## See Also

- [Testing recipe](../../recipes/index.md) — Recipe index for cross-cutting patterns
- [Run functions locally](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local) — Core Tools reference
- [07 - Extending with Triggers](07-extending-triggers.md)

## Sources

- [Code and test Azure Functions locally (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-develop-local)
- [Azure Functions PowerShell developer guide (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
- [Use Azurite emulator for local Azure Storage development (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite)
</content>
