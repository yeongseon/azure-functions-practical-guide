---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/function-keys-how-to
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/security-concepts
---
# HTTP Authentication

Control access to PowerShell HTTP functions with authorization levels, function keys, and token validation.

## Authorization Levels

Set `authLevel` in `function.json`:

| Level | Behavior |
|-------|----------|
| `anonymous` | No key required. |
| `function` | Requires a function or host key (default). |
| `admin` | Requires the host master key. |

```json
{
  "authLevel": "function",
  "type": "httpTrigger",
  "direction": "in",
  "name": "Request",
  "methods": ["post"]
}
```

## Calling with a Function Key

```bash
curl "https://$APP_NAME.azurewebsites.net/api/secure?code=<function-key>"
```

Retrieve keys with:

```bash
az functionapp function keys list \
  --name $APP_NAME \
  --resource-group $RG \
  --function-name secure
```

## Validating a Bearer Token

For Entra ID-issued tokens, validate the JWT inside the function. Prefer fronting the app with API Management or App Service Easy Auth for production, but a lightweight in-function check looks like:

```powershell
param($Request, $TriggerMetadata)

$authHeader = $Request.Headers.Authorization
if (-not $authHeader -or -not $authHeader.StartsWith("Bearer ")) {
    Push-OutputBinding -Name Response -Value ([HttpResponseContext]@{
        StatusCode = [System.Net.HttpStatusCode]::Unauthorized
        Body       = "Missing bearer token"
    })
    return
}

$token = $authHeader.Substring(7)
# Validate $token signature/claims against your identity provider here.
```

!!! warning "Do not hand-roll crypto"
    For real token validation, use a vetted library or delegate to App Service Authentication / API Management rather than manually verifying signatures.

## See Also

- [HTTP API Patterns](http-api.md)
- [Managed Identity](managed-identity.md)
- [Recipes Index](index.md)

## Sources

- [Work with function keys (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/function-keys-how-to)
- [Azure Functions security concepts (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/security-concepts)
