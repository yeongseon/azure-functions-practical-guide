---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# HTTP API Patterns

Build HTTP APIs in PowerShell using the `HttpRequestContext` input and `HttpResponseContext` output binding.

## Route and Method Configuration

`function.json`:

```json
{
  "bindings": [
    {
      "authLevel": "function",
      "type": "httpTrigger",
      "direction": "in",
      "name": "Request",
      "methods": ["get", "post"],
      "route": "orders/{id?}"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "Response"
    }
  ]
}
```

## Parsing the Request

```powershell
param($Request, $TriggerMetadata)

# Route parameter
$id = $Request.Params.id

# Query string
$status = $Request.Query.Status

# JSON body (already deserialized into a Hashtable/PSObject)
$payload = $Request.Body
```

## Returning Structured Responses

```powershell
Push-OutputBinding -Name Response -Value ([HttpResponseContext]@{
    StatusCode  = [System.Net.HttpStatusCode]::OK
    Headers     = @{ "Content-Type" = "application/json" }
    Body        = @{ id = $id; status = "processed" } | ConvertTo-Json
})
```

## Error Handling

```powershell
if (-not $id) {
    Push-OutputBinding -Name Response -Value ([HttpResponseContext]@{
        StatusCode = [System.Net.HttpStatusCode]::BadRequest
        Body       = "Missing order id"
    })
    return
}
```

!!! tip "Always return early"
    After pushing an error response, `return` immediately to avoid pushing a second value to the same output binding.

## See Also

- [HTTP Authentication](http-auth.md)
- [PowerShell Programming Model](../powershell-programming-model.md)
- [Recipes Index](index.md)

## Sources

- [HTTP trigger and bindings (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
