---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-bindings
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# Durable Orchestration

Coordinate multi-step, long-running workflows with Durable Functions in PowerShell. A Durable app has three function types: a **client** that starts orchestrations, an **orchestrator** that defines the workflow, and **activities** that do the work.

## Prerequisites

Durable Functions require the extension bundle and the managed dependency to install the PowerShell SDK.

`host.json`:

```json
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  },
  "managedDependency": {
    "enabled": true
  }
}
```

## Client Function

An HTTP-triggered client starts the orchestration and returns status URLs. It uses an `httpTrigger`, an `http` output, and a `durableClient` input binding.

`run.ps1`:

```powershell
param($Request, $TriggerMetadata)

$instanceId = Start-DurableOrchestration -FunctionName 'OrderOrchestrator' -Input $Request.Body
$response = New-DurableOrchestrationCheckStatusResponse -Request $Request -InstanceId $instanceId
Push-OutputBinding -Name Response -Value $response
```

## Orchestrator Function

The orchestrator defines the workflow. It must be deterministic — never call external services or use random values directly; call activities instead. Binding type: `orchestrationTrigger`.

`run.ps1`:

```powershell
param($Context)

$order = $Context.Input

$reserved = Invoke-DurableActivity -FunctionName 'ReserveInventory' -Input $order
$charged  = Invoke-DurableActivity -FunctionName 'ChargePayment' -Input $order
$shipped  = Invoke-DurableActivity -FunctionName 'ShipOrder' -Input $order

return @{ reserved = $reserved; charged = $charged; shipped = $shipped }
```

## Activity Function

Activities do the actual work and may call external services. Binding type: `activityTrigger`.

`run.ps1`:

```powershell
param($order)

Write-Information "Reserving inventory for order $($order.orderId)"
return "reserved"
```

!!! warning "Determinism"
    Orchestrator code replays as the workflow progresses. Avoid `Get-Date`, `Get-Random`, and direct I/O in orchestrators — use `$Context.CurrentUtcDateTime` and delegate side effects to activities.

## See Also

- [Durable Advanced Patterns](durable-advanced.md)
- [Service Bus](service-bus.md)
- [Recipes Index](index.md)

## Sources

- [Durable Functions bindings (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-bindings)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
