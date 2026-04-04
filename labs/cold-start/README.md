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
   az group create --name rg-coldstart-lab --location eastus
   az storage account create --name stcoldstartlab123 --resource-group rg-coldstart-lab --location eastus --sku Standard_LRS
   az functionapp create --name func-coldstart-lab-123 --resource-group rg-coldstart-lab --storage-account stcoldstartlab123 --consumption-plan-location eastus --runtime python --runtime-version 3.11 --functions-version 4
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

## Cleanup
Remove Azure resources after validation.
```bash
az group delete --name rg-coldstart-lab --yes --no-wait
```
Delete local project and Azurite artifacts when done.
If you created test storage containers manually, remove them as well.

## See Also
- [Hosting options and scaling](../../docs/platform/scaling-and-plans.md)
- [Monitoring and diagnostics](../../docs/operations/monitoring.md)
- [Python runtime guidance](../../docs/language-guides/python/python-runtime.md)
