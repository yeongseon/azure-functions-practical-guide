# Lab: Storage Access Failure Troubleshooting

## Objective
Reproduce common Azure Storage connectivity failures and verify systematic troubleshooting steps.

## Prerequisites
- Azure subscription
- Azure Functions Core Tools
- Python runtime (3.11 or later)
- Azure CLI
- Azurite (local storage emulator)

## Scenario
A queue-triggered function intermittently fails with storage-related startup and binding errors.
You need to determine whether the issue is configuration, credentials, DNS, or network access.
This lab starts with local emulation, then repeats in Azure with controlled misconfigurations.
Record each failure mode with timestamp, error category, and corrective action.

## Steps
1. Initialize a Python Functions project.
   ```bash
   func init storage-failure-lab --worker-runtime python
   ```
2. Add a Queue trigger and a Queue output binding.
   ```bash
   cd storage-failure-lab
   func new --template "Azure Queue Storage trigger" --name QueueWorker
   ```
3. Launch Azurite.
   ```bash
   azurite --location ".azurite" --debug ".azurite/debug.log"
   ```
4. Set `AzureWebJobsStorage` in `local.settings.json` to the Azurite connection string.
5. Start host and confirm success.
   ```bash
   func start --verbose
   ```
6. Introduce failure A: typo in account key.
   Observe host startup errors and retry behavior.
7. Restore key, confirm recovery.
8. Introduce failure B: wrong queue name binding.
   Observe binding initialization error.
9. Restore queue name, confirm trigger resumes.
10. Create Azure resources for remote validation in Korea Central using identity-based storage.
   ```bash
   az group create --name rg-storage-failure-lab --location koreacentral
   az storage account create --name <storage-account> --resource-group rg-storage-failure-lab --location koreacentral --sku Standard_LRS --allow-shared-key-access false
   az functionapp create --name <app-name> --resource-group rg-storage-failure-lab --storage-account <storage-account> --flexconsumption-location koreacentral --runtime python --runtime-version 3.11 --functions-version 4
   az functionapp identity assign --name <app-name> --resource-group rg-storage-failure-lab
   az functionapp config appsettings set --name <app-name> --resource-group rg-storage-failure-lab --settings AzureWebJobsStorage__accountName=<storage-account>
   ```
    !!! note "Modern storage configuration"
        Identity-based storage (`AzureWebJobsStorage__accountName`) is the modern approach and recommended over connection strings.
11. Publish app.
   ```bash
   func azure functionapp publish <app-name>
   ```
12. Introduce failure C in Azure: remove storage RBAC roles from the Function App managed identity.
   ```bash
   az role assignment delete --assignee "<principal-id>" --role "Storage Blob Data Owner" --scope "<storage-resource-id>" --yes
   az role assignment delete --assignee "<principal-id>" --role "Storage Account Contributor" --scope "<storage-resource-id>" --yes
   ```
13. Check logs for authentication/network errors.
   ```bash
   az webapp log tail --name <app-name> --resource-group rg-storage-failure-lab
   ```
14. Restore required RBAC roles and verify recovery.
15. Build a troubleshooting matrix with columns:
    - Symptom
    - Representative error text
    - Likely cause
    - Verification command
    - Remediation

## Expected Behavior
- Invalid keys produce authentication failures.
- Wrong binding names fail during listener startup.
- Correcting settings restores host health without code changes.
- Logs reveal whether failures are credential, endpoint, or binding related.
- A structured symptom-to-cause matrix shortens mean time to recovery.

## Real Deployment Results (FC1 — Korea Central)

### Storage Access Failure Data (2026-04-04)

**Baseline (before RBAC removal):**
```bash
# Storage probe endpoint with managed identity — working
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

**RBAC removal:**
```bash
# Removed Storage Blob Data Owner and Storage Account Contributor roles
az role assignment delete --assignee "<principal-id>" --role "Storage Blob Data Owner" --scope "<storage-resource-id>" --yes
az role assignment delete --assignee "<principal-id>" --role "Storage Account Contributor" --scope "<storage-resource-id>" --yes
```

**After RBAC removal (120s propagation):**
```json
{
    "status": "error",
    "account": "<storage-account>",
    "error": "HttpResponseError",
    "message": "This request is not authorized to perform this operation using this permission.\nRequestId:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx\nTime:2026-04-04T12:17:54.9058630Z\nErrorCode:AuthorizationPermissionMismatch",
    "elapsedMs": 325
}
```
HTTP Status: 502

**KQL: Exceptions during RBAC removal (excerpt — 7 of 10 total):**
```
Total exceptions: 10
timestamp                    innermostType                       message
2026-04-04T12:15:42Z         Azure.RequestFailedException        Status: 403 AuthorizationPermissionMismatch
2026-04-04T12:16:06Z         Azure.RequestFailedException        Status: 403 AuthorizationPermissionMismatch
2026-04-04T12:16:26Z         Azure.RequestFailedException        Status: 403 AuthorizationPermissionMismatch
2026-04-04T12:17:00Z         Azure.RequestFailedException        Status: 403 AuthorizationPermissionMismatch
2026-04-04T12:17:57Z         Azure.RequestFailedException        Status: 403 AuthorizationPermissionMismatch
2026-04-04T12:19:57Z         Azure.RequestFailedException        Status: 403 AuthorizationPermissionMismatch
2026-04-04T12:21:57Z         Azure.RequestFailedException        Status: 403 AuthorizationPermissionMismatch
```

**KQL: Host health check traces (real data):**
```
Process reporting unhealthy: Unhealthy. Health check entries are {
  "azure.functions.web_host.lifecycle": {"status":"Healthy"},
  "azure.functions.script_host.lifecycle": {"status":"Healthy"},
  "azure.functions.webjobs.storage": {
    "status":"Unhealthy",
    "description":"Unable to access AzureWebJobsStorage",
    "errorCode":"AuthorizationPermissionMismatch"
  }
}
```

**KQL: Request table showing failure pattern (real data):**
```
timestamp                    name            duration_ms  resultCode
2026-04-04T12:15:31Z         storage_probe      58.41     200   (before removal)
2026-04-04T12:15:34Z         storage_probe      64.86     200   (before removal)
2026-04-04T12:17:54Z         storage_probe     330.28     502   (after removal)
2026-04-04T12:18:55Z         storage_probe      68.32     502   (after removal)
2026-04-04T12:21:28Z         storage_probe      87.64     502   (after removal)
2026-04-04T12:24:31Z         storage_probe      75.57     200   (after restore)
```

**After RBAC restoration (~120s propagation):**
```json
{
    "status": "success",
    "account": "<storage-account>",
    "containers": ["azure-webjobs-hosts", "azure-webjobs-secrets", "deployment-packages", "uploads"],
    "elapsedMs": 70
}
```

**Host exceptions during removal — listener failures:**
```
outerType: Microsoft.Azure.WebJobs.Host.Listeners.FunctionListenerException
outerMessage: The listener for function 'Functions.scheduled_cleanup' was unable to start.
innermostType: Azure.RequestFailedException
innermostMessage: Status: 403 (AuthorizationPermissionMismatch)
```

### Key Observations
- RBAC propagation delay: 60-120 seconds for token cache expiry.
- Host health check detects storage access failure within ~30s (checks every ~10-20s).
- Listener startup failures cascade — timer trigger and blob trigger both fail.
- The `azure.functions.webjobs.storage` health check is the most reliable early indicator.
- Recovery also has propagation delay — ~120s after role restoration.
- App became completely unresponsive during prolonged RBAC outage (HTTP 000 timeouts).
- Restart via `az functionapp restart` can force new token acquisition.

## Cleanup
```bash
az group delete --name rg-storage-failure-lab --yes --no-wait
```
Remove local test files and Azurite artifacts.
Delete temporary queues created for test scenarios.

## See Also
- [Storage and connection settings](../../docs/language-guides/python/environment-variables.md)
- [Monitoring and logs](../../docs/operations/monitoring.md)
- [Troubleshooting guide](../../docs/language-guides/python/troubleshooting.md)
