---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-signalr-service
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# SignalR Service

Add real-time messaging to clients with Azure SignalR Service bindings in PowerShell.

## Negotiate Function

Clients first call a negotiate endpoint to obtain connection info. Use the `signalRConnectionInfo` input binding:

`function.json`:

```json
{
  "bindings": [
    {
      "name": "Request",
      "type": "httpTrigger",
      "direction": "in",
      "methods": ["post"]
    },
    {
      "name": "Response",
      "type": "http",
      "direction": "out"
    },
    {
      "name": "ConnectionInfo",
      "type": "signalRConnectionInfo",
      "direction": "in",
      "hubName": "notifications",
      "connectionStringSetting": "AzureSignalRConnectionString"
    }
  ]
}
```

`run.ps1`:

```powershell
param($Request, $ConnectionInfo, $TriggerMetadata)

Push-OutputBinding -Name Response -Value ([HttpResponseContext]@{
    StatusCode = [System.Net.HttpStatusCode]::OK
    Body       = ($ConnectionInfo | ConvertTo-Json)
})
```

## Broadcasting Messages

Use the `signalR` output binding to push messages to connected clients:

```json
{
  "name": "SignalRMessages",
  "type": "signalR",
  "direction": "out",
  "hubName": "notifications",
  "connectionStringSetting": "AzureSignalRConnectionString"
}
```

```powershell
Push-OutputBinding -Name SignalRMessages -Value @{
    target    = "newMessage"
    arguments = @( @{ text = "Order shipped"; timestamp = (Get-Date).ToString("o") } )
}
```

Set `userId` on the message to target a single user, or `groupName` to target a group.

!!! tip "Serverless mode"
    Configure the SignalR Service instance in **Serverless** mode so it works with Azure Functions rather than a self-hosted hub.

## See Also

- [HTTP API Patterns](http-api.md)
- [Event Grid](event-grid.md)
- [Recipes Index](index.md)

## Sources

- [SignalR Service bindings (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-signalr-service)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
