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
   az group create --name rg-mi-lab --location koreacentral
   az storage account create --name stmilab123 --resource-group rg-mi-lab --location koreacentral --sku Standard_LRS
   az keyvault create --name kv-mi-lab-123 --resource-group rg-mi-lab --location koreacentral --sku standard
   az functionapp create --name func-mi-lab-123 --resource-group rg-mi-lab --storage-account stmilab123 --flexconsumption-location koreacentral --runtime python --runtime-version 3.11
   ```
6. Enable system-assigned identity on the Function App.
   ```bash
   az functionapp identity assign --name func-mi-lab-123 --resource-group rg-mi-lab
   ```
   For FC1 validation in this lab, use a user-assigned managed identity and configure the storage identity client ID:
   ```bash
   az functionapp identity assign --name func-mi-lab-123 --resource-group rg-mi-lab --identities "<user-assigned-identity-resource-id>"
   az functionapp config appsettings set --name func-mi-lab-123 --resource-group rg-mi-lab --settings AzureWebJobsStorage__accountName=stmilab123 AzureWebJobsStorage__clientId=<user-assigned-client-id>
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

!!! note "User-assigned vs system-assigned identity"
    System-assigned identity is lifecycle-coupled to the Function App and is sufficient for many scenarios.
    User-assigned identity is reusable across apps and requires explicitly setting `AzureWebJobsStorage__clientId` when used for `AzureWebJobsStorage` identity-based connections.
    This lab's real FC1 deployment results use a user-assigned identity.

## Expected Behavior
- Local runs authenticate via signed-in developer identity.
- Azure runs authenticate via managed identity (system-assigned or user-assigned, depending on configuration).
- Missing role assignments return authorization errors.
- Restoring least-privilege roles restores function success.
- Endpoint tests should not require any secret material in app settings.

## Real Deployment Results (FC1 — Korea Central)
The managed identity lab was validated using the same FC1 deployment as the storage-access-failure lab, since both scenarios test RBAC-based access. The `diagnostics/storage-probe` endpoint tests managed identity access to Azure Blob Storage.

**Baseline — identity access working:**
```bash
curl https://<app-name>.azurewebsites.net/api/diagnostics/storage-probe
```
```json
{
    "status": "success",
    "account": "<storage-account>",
    "containers": ["azure-webjobs-hosts", "azure-webjobs-secrets", "deployment-packages", "uploads"],
    "elapsedMs": 293
}
```

**Role assignments before removal:**
```
Role
------------------------------
Storage Blob Data Owner
Storage Queue Data Contributor
Storage Account Contributor
```

**After removing Storage Blob Data Owner + Storage Account Contributor:**
```json
{
    "status": "error",
    "account": "<storage-account>",
    "error": "HttpResponseError",
    "message": "This request is not authorized to perform this operation using this permission.\nErrorCode:AuthorizationPermissionMismatch",
    "elapsedMs": 325
}
```

**KQL: Exception pattern during role removal:**
```
Total exceptions: 10 over 6 minutes
innermostType: Azure.RequestFailedException
innermostMessage: Status: 403 (AuthorizationPermissionMismatch)
```

**KQL: Host health reporting during failure:**
```json
{
  "azure.functions.web_host.lifecycle": {"status": "Healthy"},
  "azure.functions.script_host.lifecycle": {"status": "Healthy"},
  "azure.functions.webjobs.storage": {
    "status": "Unhealthy",
    "description": "Unable to access AzureWebJobsStorage",
    "errorCode": "AuthorizationPermissionMismatch"
  }
}
```

**Cascading listener failures (real):**
```
outerType: Microsoft.Azure.WebJobs.Host.Listeners.FunctionListenerException
outerMessage: The listener for function 'Functions.scheduled_cleanup' was unable to start.
innermostType: Azure.RequestFailedException
innermostMessage: Status: 403 (AuthorizationPermissionMismatch)
```

**Role restoration and recovery:**
```bash
az role assignment create \
  --assignee-object-id "<principal-id>" \
  --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Owner" \
  --scope "<storage-resource-id>"
```
Recovery time: ~120 seconds after role restoration for token cache to refresh

**Post-recovery:**
```json
{
    "status": "success",
    "account": "<storage-account>",
    "containers": ["azure-webjobs-hosts", "azure-webjobs-secrets", "deployment-packages", "uploads"],
    "elapsedMs": 70
}
```

### Key Observations
- User-assigned managed identity was used (not system-assigned), configured via `AzureWebJobsStorage__clientId`.
- RBAC propagation takes 60-120 seconds in both directions (removal and restoration).
- Removing blob data access causes cascading failures: blob triggers, timer triggers (which use blob leases), and any blob-dependent functions all fail.
- The host health check `azure.functions.webjobs.storage` detects the issue within 30 seconds.
- During prolonged RBAC outage, the function app can become completely unresponsive.
- `az functionapp restart` forces new token acquisition and can speed up recovery.
- Minimum roles required for AzureWebJobsStorage: Storage Blob Data Owner + Storage Queue Data Contributor + Storage Account Contributor (for blob, queue, and management operations).

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
