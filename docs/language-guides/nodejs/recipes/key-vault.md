---
content_sources:
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/app-service/app-service-key-vault-references
  - type: mslearn-adapted
    url: https://learn.microsoft.com/javascript/api/overview/azure/keyvault-secrets-readme
---

# Key Vault Access

This recipe covers both Key Vault reference app settings and direct SDK access with `DefaultAzureCredential` in Node.js v4 functions.

## Architecture

<!-- diagram-id: architecture -->
```mermaid
flowchart LR
    FUNC[Function App] --> MSI[Managed Identity]
    MSI --> KV[Azure Key Vault]
    KV --> SETTING[App Setting via Key Vault Reference]
    KV --> SDK[SecretClient SDK Call]
    SETTING --> HANDLER[HTTP Trigger Handler]
    SDK --> HANDLER
```

## Prerequisites

Use extension bundle v4 in `host.json`:

```json
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
```

Create Key Vault and a secret:

```bash
az keyvault create \
  --name <key-vault-name> \
  --resource-group $RG \
  --location $LOCATION

az keyvault secret set \
  --vault-name <key-vault-name> \
  --name payment-api-key \
  --value "sample-secret-value"
```

Enable managed identity and grant Key Vault secret permissions:

```bash
az functionapp identity assign --name $APP_NAME --resource-group $RG

az role assignment create \
  --assignee <principal-id> \
  --role "Key Vault Secrets User" \
  --scope $(az keyvault show --name <key-vault-name> --resource-group $RG --query id --output tsv)
```

Configure a version-pinned Key Vault reference in app settings:

```bash
az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG \
  --settings "PaymentApiKey=@Microsoft.KeyVault(SecretUri=https://<key-vault-name>.vault.azure.net/secrets/payment-api-key/<secret-version-guid>)"
```

Install packages for direct SDK access:

```bash
npm install @azure/identity @azure/keyvault-secrets
```

## Working Node.js v4 Code

```javascript
const { app } = require("@azure/functions");
const { DefaultAzureCredential } = require("@azure/identity");
const { SecretClient } = require("@azure/keyvault-secrets");

const vaultUrl = process.env.KEY_VAULT_URI;
const credential = new DefaultAzureCredential();
const secretClient = new SecretClient(vaultUrl, credential);

app.http("secretsHealth", {
  methods: ["GET"],
  route: "secrets/health",
  authLevel: "function",
  handler: async (_request, context) => {
    const fromReference = process.env.PaymentApiKey;
    const fromSdk = await secretClient.getSecret("payment-api-key");

    context.log("Fetched secrets", {
      sdkVersion: fromSdk.properties.version
    });

    return {
      status: 200,
      jsonBody: {
        referenceLoaded: Boolean(fromReference),
        sdkSecretName: fromSdk.name,
        sdkSecretVersion: fromSdk.properties.version
      }
    };
  }
});
```

## Implementation Notes

- Use Key Vault references for simple configuration injection with no SDK code.
- Pin `SecretUri` to a specific version for controlled rollouts and reproducible deployments.
- Use SDK access when you need metadata, dynamic secret names, or explicit version selection at runtime.
- Cache SDK clients across invocations to reduce connection overhead.

## See Also
- [Node.js Recipes Index](index.md)
- [Managed Identity](managed-identity.md)
- [HTTP Authentication](http-auth.md)

## Sources
- [Use Key Vault references for App Service and Azure Functions (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/app-service-key-vault-references)
- [Azure Key Vault Secrets client library for JavaScript (Microsoft Learn)](https://learn.microsoft.com/javascript/api/overview/azure/keyvault-secrets-readme)
