---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger
---
# OpenAPI Documentation

Publish a discoverable HTTP API contract for PowerShell functions.

## Approach for PowerShell

The Azure Functions OpenAPI extension provides first-class attribute-based generation for C#, but PowerShell functions do not have those attributes. Instead, serve a hand-authored or generated OpenAPI document from a dedicated HTTP function.

## Serving the OpenAPI Document

Place an `openapi.json` (or `openapi.yaml`) spec alongside your function and return it from an HTTP endpoint:

`function.json`:

```json
{
  "bindings": [
    {
      "name": "Request",
      "type": "httpTrigger",
      "direction": "in",
      "authLevel": "anonymous",
      "methods": ["get"],
      "route": "openapi.json"
    },
    {
      "name": "Response",
      "type": "http",
      "direction": "out"
    }
  ]
}
```

`run.ps1`:

```powershell
param($Request, $TriggerMetadata)

$specPath = Join-Path $PSScriptRoot "openapi.json"
$spec = Get-Content -Path $specPath -Raw

Push-OutputBinding -Name Response -Value ([HttpResponseContext]@{
    StatusCode  = [System.Net.HttpStatusCode]::OK
    Headers     = @{ "Content-Type" = "application/json" }
    Body        = $spec
})
```

## Keeping the Spec Accurate

Treat the OpenAPI document as source-controlled API contract. Validate it in CI with a linter such as `spectral`, and review it whenever routes, parameters, or response shapes change.

!!! tip "Serve a UI"
    Host Swagger UI or Redoc as static content (for example on the same Function App via a static route or on Azure Static Web Apps) and point it at your `openapi.json` endpoint.

## See Also

- [HTTP API Patterns](http-api.md)
- [HTTP Authentication](http-auth.md)
- [Recipes Index](index.md)

## Sources

- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
- [HTTP trigger (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger)
