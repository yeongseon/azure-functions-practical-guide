# Lab: Cold Start Measurement and Mitigation

## Objective
Measure cold-start latency for an HTTP-triggered Function App and apply practical mitigations.

## Prerequisites
- Azure subscription
- Azure Functions Core Tools
- Python runtime (3.11 or later)
- Azure CLI
- Azurite (local storage emulator)

## Scenario
Your team reports occasional slow first responses after periods of inactivity.
You need a repeatable method to quantify cold starts and compare mitigation strategies.
This lab runs locally first (with Azurite), then validates in Azure.
Capture at least three cold-start samples per variant to avoid one-off outliers.

## Steps
1. Create a new Python Function App.
   ```bash
   func init cold-start-lab --worker-runtime python
   ```
2. Add an HTTP trigger.
   ```bash
   cd cold-start-lab
   func new --template "HTTP trigger" --name HttpProbe
   ```
3. Start Azurite in a separate terminal.
   ```bash
   azurite --location ".azurite" --debug ".azurite/debug.log"
   ```
4. Configure local storage and disable always-on behavior locally.
   Update `local.settings.json` with emulator connection values.
5. Add timing instrumentation in `HttpProbe/__init__.py`.
   Capture process start time and elapsed milliseconds per request.
6. Run the function host.
   ```bash
   func start --verbose
   ```
7. Execute a baseline warm/cold test loop.
   ```bash
   python -c "import time,requests; u='http://localhost:7071/api/HttpProbe'; print(requests.get(u).text); time.sleep(180); print(requests.get(u).text)"
   ```
8. Record first-hit latency and follow-up latency in a table.
9. Apply mitigation A: pre-import heavy modules at startup.
10. Apply mitigation B: defer non-critical initialization until after response.
11. Re-run the exact test loop and compare deltas.
12. Deploy to Azure for real-host validation.
   ```bash
   az group create --name rg-coldstart-lab-krc --location koreacentral
   az storage account create --name stcoldstartlab123 --resource-group rg-coldstart-lab-krc --location koreacentral --sku Standard_LRS
   az functionapp create --name func-coldstart-lab-123 --resource-group rg-coldstart-lab-krc --storage-account stcoldstartlab123 --consumption-plan-location koreacentral --runtime python --runtime-version 3.11 --functions-version 4
   func azure functionapp publish func-coldstart-lab-123
   ```
13. Wait 10+ minutes idle, then call endpoint twice and capture timings.
14. Repeat step 13 three times to build a baseline sample set.
15. Create a summary table:
    - Variant name
    - First-hit latency (ms)
    - Warm latency (ms)
    - Relative improvement (%)
16. Document trade-offs (startup cost, readability, operational risk).

## Expected Behavior
- First request after idle is slower than subsequent warm requests.
- Startup-heavy imports increase first-hit latency.
- Moving optional work off the request path reduces cold-start impact.
- Local and Azure trends are directionally similar, with higher variance in Azure.
- Repeated measurements reduce misleading conclusions from noisy single runs.
- A small code-structure change can produce measurable startup improvements.

## Real Deployment Results (FC1 — Korea Central)

The following results are from an actual Flex Consumption (FC1) deployment on 2026-04-04 in `koreacentral`.
All identifiers are masked per repository policy.

### Deployment CLI output (masked)

```bash
$ az group create --name rg-coldstart-lab-krc --location koreacentral
{
  "id": "/subscriptions/<subscription-id>/resourceGroups/rg-coldstart-lab-krc",
  "location": "koreacentral",
  "name": "rg-coldstart-lab-krc",
  "properties": {
    "provisioningState": "Succeeded"
  }
}

$ az storage account create --name <masked-storage-account> --resource-group rg-coldstart-lab-krc --location koreacentral --sku Standard_LRS
{
  "id": "/subscriptions/<subscription-id>/resourceGroups/rg-coldstart-lab-krc/providers/Microsoft.Storage/storageAccounts/<masked-storage-account>",
  "location": "koreacentral",
  "name": "<masked-storage-account>",
  "provisioningState": "Succeeded"
}

$ az functionapp create --name <masked-function-app> --resource-group rg-coldstart-lab-krc --storage-account <masked-storage-account> --flexconsumption-location koreacentral --runtime python --runtime-version 3.11
{
  "defaultHostName": "<masked-function-app>.azurewebsites.net",
  "id": "/subscriptions/<subscription-id>/resourceGroups/rg-coldstart-lab-krc/providers/Microsoft.Web/sites/<masked-function-app>",
  "location": "koreacentral",
  "name": "<masked-function-app>"
}
```

### Cold Start Measurement Data (FC1 deployment, 2026-04-04)

**Warm baseline (instance already running):**

| Request | HTTP Code | Time Total | Time to First Byte |
|---------|-----------|------------|-------------------|
| Warm 1 | 200 | 0.091s | 0.091s |
| Warm 2 | 200 | 0.067s | 0.067s |
| Warm 3 | 200 | 0.074s | 0.074s |

**Cold start (after ~13 min idle):**

| Request | HTTP Code | Time Total | Time to First Byte |
|---------|-----------|------------|-------------------|
| Cold hit | 200 | 30.485s | 30.485s |

**Post-restart cold start:**

| Request | HTTP Code | Time Total | Time to First Byte |
|---------|-----------|------------|-------------------|
| After restart | 200 | 3.156s | 3.156s |

**Fully warm after rapid-fire:**

| Request | HTTP Code | Time Total |
|---------|-----------|------------|
| Warm 1 | 200 | 0.099s |
| Warm 2 | 200 | 0.084s |
| Warm 3 | 200 | 0.074s |

### KQL Evidence (real telemetry)

**Host startup traces:**

```text
Host started (363ms)
Host started (453ms)
```

**Request duration (server-side):**

```text
health function: 3.63ms - 5.86ms (warm), 1719ms - 1842ms (cold/scale event)
```

### Key Observations

- FC1 cold start from full idle is about 30 seconds client-side; instance provisioning dominates total latency.
- FC1 host startup itself is fast (363-453ms) once an instance is allocated.
- FC1 scale events can add roughly 1.7-3 seconds even during otherwise warm periods when new instances are added.
- Truly warm requests are 67-99ms client-side and 3-6ms server-side.
- After restart, cold-path latency was about 3.1 seconds, much faster than full idle cold start because compute allocation was already in place.

## Cleanup
Remove Azure resources after validation.
```bash
az group delete --name rg-coldstart-lab-krc --yes --no-wait
```
Delete local project and Azurite artifacts when done.
If you created test storage containers manually, remove them as well.

## See Also
- [Hosting options and scaling](../../docs/platform/scaling.md)
- [Monitoring and diagnostics](../../docs/operations/monitoring.md)
- [Python runtime guidance](../../docs/language-guides/python/python-runtime.md)
