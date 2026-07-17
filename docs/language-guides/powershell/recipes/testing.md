---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-test-a-function
---
# Testing

Unit-test PowerShell function logic with Pester.

## Structuring for Testability

Keep `run.ps1` thin and move business logic into a shared module (for example under a `Modules/` folder or a `.psm1` next to your functions). Pure functions with explicit inputs and outputs are far easier to test than binding-coupled handlers.

`Modules/OrderLogic.psm1`:

```powershell
function Get-OrderTotal {
    param([object[]] $Items)
    ($Items | Measure-Object -Property Price -Sum).Sum
}

Export-ModuleMember -Function Get-OrderTotal
```

`run.ps1` calls the module:

```powershell
param($Request, $TriggerMetadata)

Import-Module "$PSScriptRoot/../Modules/OrderLogic.psm1"
$total = Get-OrderTotal -Items $Request.Body.items
```

## Writing Pester Tests

`OrderLogic.Tests.ps1`:

```powershell
BeforeAll {
    Import-Module "$PSScriptRoot/Modules/OrderLogic.psm1" -Force
}

Describe "Get-OrderTotal" {
    It "sums item prices" {
        $items = @(
            @{ Price = 10 },
            @{ Price = 5.5 }
        )
        Get-OrderTotal -Items $items | Should -Be 15.5
    }

    It "returns null for an empty cart" {
        Get-OrderTotal -Items @() | Should -BeNullOrEmpty
    }
}
```

## Running Tests

```powershell
Invoke-Pester -Path . -Output Detailed
```

In CI, fail the build on any failing test and publish the results:

```powershell
Invoke-Pester -Configuration (New-PesterConfiguration -Hashtable @{
    Run    = @{ Path = "." }
    Output = @{ Verbosity = "Detailed" }
    Run    = @{ Exit = $true }
})
```

!!! tip "Mock external calls"
    Use Pester's `Mock` to stub `Invoke-RestMethod`, `Connect-AzAccount`, and other cmdlets so unit tests never touch live Azure resources.

## See Also

- [HTTP API Patterns](http-api.md)
- [Retries and Error Handling](retry.md)
- [Recipes Index](index.md)

## Sources

- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
- [Testing Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-test-a-function)
