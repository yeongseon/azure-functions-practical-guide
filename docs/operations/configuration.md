# Configuration

This guide covers operational runtime configuration for Azure Functions.
It focuses on app settings, `host.json`, and secret management patterns.

!!! tip "Platform Guide"
    For scaling architecture and plan comparison, see [Scaling](../platform/scaling.md).

!!! tip "Language Guide"
    For Python deployment specifics, see the [Python Tutorial](../language-guides/python/tutorial/index.md).

## Configuration layers

Use a layered model:

1. App settings for environment values.
2. `host.json` for runtime host behavior.
3. Local development settings for workstation execution.

## App settings

Common settings:

| Setting | Purpose |
|---|---|
| `AzureWebJobsStorage` or identity-based equivalent | Host storage dependency |
| `FUNCTIONS_WORKER_RUNTIME` | Worker runtime selection |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Monitoring destination |
| `WEBSITE_RUN_FROM_PACKAGE` | Immutable package deployment behavior |
| Custom settings | Feature flags and endpoints |

Set values:

```bash
az functionapp config appsettings set \
    --resource-group <resource-group> \
    --name <app-name> \
    --settings FUNCTIONS_WORKER_RUNTIME=<worker-runtime>
```

List values (redact secrets before sharing):

```bash
az functionapp config appsettings list \
    --resource-group <resource-group> \
    --name <app-name>
```

## `host.json` essentials

`host.json` controls host-level behavior such as logging, sampling, and extension configuration.

```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "excludedTypes": "Request;Exception"
      }
    },
    "logLevel": {
      "default": "Information"
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
```

!!! note "Sampling"
    Sampling can reduce telemetry costs, but keep critical request and exception visibility.

## `local.settings.json`

Use local settings only for local runtime execution.

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "<worker-runtime>",
    "APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=<masked>"
  }
}
```

Operational rules:

- Do not commit production secrets.
- Keep a sanitized `local.settings.json.example` in source control.
- Inject secrets at deployment time via secure pipeline mechanisms.

## Key Vault references

Use Key Vault references to resolve secrets in app settings without storing plaintext secret values.

Format:

```text
@Microsoft.KeyVault(SecretUri=https://<key-vault-name>.vault.azure.net/secrets/<secret-name>/)
```

Set a Key Vault-backed app setting:

```bash
az functionapp config appsettings set \
    --resource-group <resource-group> \
    --name <app-name> \
    --settings "MySecretSetting=@Microsoft.KeyVault(SecretUri=https://<key-vault-name>.vault.azure.net/secrets/<secret-name>/)"
```

## Managed identity for secret access

Enable system-assigned identity:

```bash
az functionapp identity assign \
    --resource-group <resource-group> \
    --name <app-name>
```

Grant the identity least-privilege access to Key Vault and dependent services.
Prefer identity-based connection patterns over connection strings when bindings support it.

## Slot-specific settings

When using slots, mark environment-specific values as slot settings.

```bash
az functionapp config appsettings set \
    --resource-group <resource-group> \
    --name <app-name> \
    --slot staging \
    --slot-settings AZURE_FUNCTIONS_ENVIRONMENT=Staging
```

## Configuration checklist

- Configuration updates are versioned and reviewed.
- Secrets come from Key Vault references.
- `host.json` changes are validated before production rollout.

## References

- [App settings reference for Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-app-settings)
- [host.json reference for Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-host-json)
- [Use Key Vault references in App Service and Functions](https://learn.microsoft.com/azure/app-service/app-service-key-vault-references)
- [Azure Functions identity-based connections](https://learn.microsoft.com/azure/azure-functions/functions-reference#configure-an-identity-based-connection)

## See Also

- [Deployment](deployment.md)
- [Monitoring](monitoring.md)
- [Platform Security](../platform/security.md)
