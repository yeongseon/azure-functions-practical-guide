---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/app-service/app-service-key-vault-references
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# Key Vault

Retrieve secrets securely in PowerShell functions using Key Vault references or the Az module.

## Key Vault References (Recommended)

Reference a secret directly from an app setting — no code changes required:

```bash
az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG \
  --settings "DbPassword=@Microsoft.KeyVault(SecretUri=https://my-vault.vault.azure.net/secrets/db-password/)"
```
| Command/Parameter | Purpose |
| --- | --- |
| `az functionapp config appsettings set` | Add or update application settings on the function app. |
| `--name` | Name of the target resource. |
| `--resource-group` | Resource group that contains the resource. |
| `--settings` | Key=value application settings to apply. |

The function reads it as a normal environment variable:

```powershell
$password = $env:DbPassword
```

The function app's managed identity must have the **Key Vault Secrets User** role on the vault.

## Retrieving Secrets at Runtime

For dynamic secret names, use the `Az.KeyVault` module with a managed identity:

```powershell
# profile.ps1
if ($env:MSI_SECRET) {
    Connect-AzAccount -Identity
}
```

```powershell
# run.ps1
param($Request, $TriggerMetadata)

$secret = Get-AzKeyVaultSecret -VaultName "my-vault" -Name "db-password" -AsPlainText
```

Bundle `Az.KeyVault` (and `Az.Accounts`) in the `Modules` folder, or declare them in `requirements.psd1` on plans that support managed dependencies.

## Grant Access

```bash
az role assignment create \
  --assignee <function-app-identity-object-id> \
  --role "Key Vault Secrets User" \
  --scope <key-vault-resource-id>
```
| Command/Parameter | Purpose |
| --- | --- |
| `az role assignment create` | Assign an Azure RBAC role to an identity. |
| `--assignee` | Identity (object ID) receiving the role. |
| `--role` | Azure RBAC role to assign. |
| `--scope` | Scope at which the role applies. |

!!! warning "Never log secrets"
    Do not pass secret values to `Write-Information`/`Write-Host` — they flow to Application Insights.

## See Also

- [Managed Identity](managed-identity.md)
- [Environment Variables](../environment-variables.md)
- [Recipes Index](index.md)

## Sources

- [Key Vault references (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/app-service/app-service-key-vault-references)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
