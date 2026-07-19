---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-identity-based-connections-tutorial
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# Managed Identity

Authenticate to Azure services without secrets using a managed identity and `Connect-AzAccount -Identity`.

## Enable the Identity

```bash
az functionapp identity assign \
  --name $APP_NAME \
  --resource-group $RG
```
| Command/Parameter | Purpose |
| --- | --- |
| `az functionapp identity assign` | Enable a managed identity on the function app. |
| `--name` | Name of the target resource. |
| `--resource-group` | Resource group that contains the resource. |

This injects `MSI_SECRET` and `IDENTITY_HEADER` into the app environment.

## Authenticate Once per Worker

Put the connection in `profile.ps1` so it runs once on cold start rather than per invocation:

```powershell
# profile.ps1
if ($env:MSI_SECRET) {
    Disable-AzContextAutosave -Scope Process | Out-Null
    Connect-AzAccount -Identity
}
```

## Use the Connection

```powershell
# run.ps1
param($Request, $TriggerMetadata)

$ctx = New-AzStorageContext -StorageAccountName $env:StorageAccountName -UseConnectedAccount
$blobs = Get-AzStorageBlob -Container "data" -Context $ctx
```

## Identity-Based Trigger Connections

Bindings can use the identity instead of a connection string. Replace the connection string setting with a namespace/endpoint setting:

```bash
az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG \
  --settings "AzureWebJobsStorage__accountName=$STORAGE_NAME"
```
| Command/Parameter | Purpose |
| --- | --- |
| `az functionapp config appsettings set` | Add or update application settings on the function app. |
| `--name` | Name of the target resource. |
| `--resource-group` | Resource group that contains the resource. |
| `--settings` | Key=value application settings to apply. |

## Grant RBAC

```bash
az role assignment create \
  --assignee <function-app-identity-object-id> \
  --role "Storage Blob Data Contributor" \
  --scope <storage-account-resource-id>
```
| Command/Parameter | Purpose |
| --- | --- |
| `az role assignment create` | Assign an Azure RBAC role to an identity. |
| `--assignee` | Identity (object ID) receiving the role. |
| `--role` | Azure RBAC role to assign. |
| `--scope` | Scope at which the role applies. |

!!! warning "Concurrency and Az context"
    Azure PowerShell context is process-scoped. When in-process concurrency is enabled, call `Disable-AzContextAutosave -Scope Process` and validate for race conditions. See [PowerShell Runtime](../powershell-runtime.md#concurrency).

## See Also

- [Key Vault](key-vault.md)
- [Environment Variables](../environment-variables.md)
- [Recipes Index](index.md)

## Sources

- [Identity-based connections tutorial (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-identity-based-connections-tutorial)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
