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
10. Create Azure resources for remote validation.
   ```bash
   az group create --name rg-storage-failure-lab --location eastus
   az storage account create --name stfailurelab123 --resource-group rg-storage-failure-lab --location eastus --sku Standard_LRS
   az functionapp create --name func-storage-failure-123 --resource-group rg-storage-failure-lab --storage-account stfailurelab123 --consumption-plan-location eastus --runtime python --runtime-version 3.11 --functions-version 4
   ```
11. Publish app.
   ```bash
   func azure functionapp publish func-storage-failure-123
   ```
12. Introduce failure C in Azure: set invalid `AzureWebJobsStorage` app setting.
   ```bash
   az functionapp config appsettings set --name func-storage-failure-123 --resource-group rg-storage-failure-lab --settings AzureWebJobsStorage="DefaultEndpointsProtocol=https;AccountName=invalid;AccountKey=invalid;EndpointSuffix=core.windows.net"
   ```
13. Check logs for authentication/network errors.
   ```bash
   az webapp log tail --name func-storage-failure-123 --resource-group rg-storage-failure-lab
   ```
14. Restore correct setting from storage connection string and verify recovery.
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
