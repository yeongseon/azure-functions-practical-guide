# Lab: Managed Identity Authentication for Dependencies

## Objective
Configure and validate managed identity authentication from Azure Functions to Azure resources.

## Prerequisites
- Azure subscription
- Azure Functions Core Tools
- Python runtime (3.11 or later)
- Azure CLI
- Azurite (local storage emulator)

## Scenario
Your security baseline disallows connection strings in app settings.
You must move from secret-based access to managed identity for storage and key retrieval,
and prove least-privilege access works end-to-end.
The exercise validates both success and expected authorization failures.

## Steps
1. Initialize a Python Function App and HTTP trigger.
   ```bash
   func init managed-identity-lab --worker-runtime python
   cd managed-identity-lab
   func new --template "HTTP trigger" --name IdentityProbe
   ```
2. Add Azure Identity and SDK dependencies.
   ```bash
   python -m pip install azure-identity azure-storage-blob azure-keyvault-secrets
   ```
3. Implement token-based access in function code using `DefaultAzureCredential`.
4. Verify local development with developer credentials.
   ```bash
   az login
   func start --verbose
   ```
5. Provision Azure resources.
   ```bash
   az group create --name rg-mi-lab --location eastus
   az storage account create --name stmilab123 --resource-group rg-mi-lab --location eastus --sku Standard_LRS
   az keyvault create --name kv-mi-lab-123 --resource-group rg-mi-lab --location eastus --sku standard
   az functionapp create --name func-mi-lab-123 --resource-group rg-mi-lab --storage-account stmilab123 --consumption-plan-location eastus --runtime python --runtime-version 3.11 --functions-version 4
   ```
6. Enable system-assigned identity on the Function App.
   ```bash
   az functionapp identity assign --name func-mi-lab-123 --resource-group rg-mi-lab
   ```
7. Capture principal ID output for role assignments.
8. Grant least-privilege roles.
   ```bash
   az role assignment create --assignee-object-id <function-principal-id> --assignee-principal-type ServicePrincipal --role "Storage Blob Data Reader" --scope "/subscriptions/<subscription-id>/resourceGroups/rg-mi-lab/providers/Microsoft.Storage/storageAccounts/stmilab123"
   az role assignment create --assignee-object-id <function-principal-id> --assignee-principal-type ServicePrincipal --role "Key Vault Secrets User" --scope "/subscriptions/<subscription-id>/resourceGroups/rg-mi-lab/providers/Microsoft.KeyVault/vaults/kv-mi-lab-123"
   ```
9. Configure app settings for endpoint names (not secrets).
   ```bash
   az functionapp config appsettings set --name func-mi-lab-123 --resource-group rg-mi-lab --settings STORAGE_ACCOUNT_NAME=stmilab123 KEY_VAULT_NAME=kv-mi-lab-123
   ```
10. Deploy function and test endpoint.
    ```bash
    func azure functionapp publish func-mi-lab-123
    ```
11. Remove one role temporarily and confirm authorization failure.
12. Restore role and confirm recovery.
13. Document minimum required roles for each dependency.
14. Capture final validation outputs with masked IDs only.

## Expected Behavior
- Local runs authenticate via signed-in developer identity.
- Azure runs authenticate via system-assigned managed identity.
- Missing role assignments return authorization errors.
- Restoring least-privilege roles restores function success.
- Endpoint tests should not require any secret material in app settings.

## Cleanup
```bash
az group delete --name rg-mi-lab --yes --no-wait
```
Delete local project files after lab completion.
Revoke any temporary role assignments that are no longer needed.

## See Also
- [Managed identity recipe](../../docs/language-guides/python/recipes/managed-identity.md)
- [Security operations guidance](../../docs/operations/security.md)
- [Python environment variables](../../docs/language-guides/python/environment-variables.md)
