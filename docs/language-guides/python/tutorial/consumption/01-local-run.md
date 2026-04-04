# 01 - Run Locally (Consumption)

Run the sample Azure Functions Python app on your machine before deploying to the Consumption (Y1) plan. This track uses Linux shell examples; the same workflow works on Windows with equivalent commands.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Local runtime for the function code |
| Azure Functions Core Tools | v4 | Start the local host and publish later |
| Azure CLI | 2.61+ | Provision and configure Azure resources |
| Azurite (optional) | latest | Local Storage emulator for triggers and bindings |

!!! info "Consumption plan basics"
    Consumption (Y1) is serverless with scale-to-zero, up to 200 instances, 1.5 GB memory per instance, and a default 5-minute timeout (max 10 minutes).

## Steps

### Step 1 - Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --requirement app/requirements.txt
```

### Step 2 - Create local settings

```bash
cp app/local.settings.json.example app/local.settings.json
```

Update `app/local.settings.json` with these baseline values:

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true"
  }
}
```

`AzureWebJobsStorage` can be a connection string (common for Consumption) or identity-based settings in Azure; both are supported.

### Step 3 - Start Azurite (optional but recommended)

```bash
azurite --silent --location /tmp/azurite --debug /tmp/azurite/debug.log
```

### Step 4 - Start the Functions host

```bash
func start --script-root app
```

### Step 5 - Call an endpoint from another terminal

```bash
curl --request GET "http://localhost:7071/api/health"
```

## Expected Output

Host start output:

```text
Azure Functions Core Tools
Core Tools Version:       4.x.x
Function Runtime Version: 4.x.x.x

Functions:

    health: [GET] http://localhost:7071/api/health
    info: [GET] http://localhost:7071/api/info
```

HTTP response example:

```json
{"status":"healthy","timestamp":"2026-04-03T09:00:00Z","version":"1.0.0"}
```

## Next Steps

You now have local parity and can deploy to Azure Consumption (Y1).

> **Next:** [02 - First Deploy](02-first-deploy.md)

## References

- [Run Functions locally with Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
- [Azure Functions Consumption plan](https://learn.microsoft.com/azure/azure-functions/consumption-plan)
- [Python developer guide for Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
