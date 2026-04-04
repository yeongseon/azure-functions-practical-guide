# Troubleshooting

This reference covers the most common issues encountered when developing and deploying Azure Functions Python v2 apps, organised as **Problem → Cause → Solution**.

## 1. Functions Not Found After Deploy

**Problem:** After deploying to Azure, navigating to the function app shows no functions. The Functions list in the Azure Portal is empty, and hitting endpoints returns 404.

**Cause:** On current runtimes (4.x+), worker indexing is enabled by default. An empty function list is more commonly caused by startup/import failures during app load.

**Solution:**

```bash
# Check startup errors first
az functionapp log tail \
  --name $APP_NAME \
  --resource-group $RG
```

Verify in `local.settings.json` for local development:

```json
{
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

> **Note:** Older runtimes (< 4.x) may need `AzureWebJobsFeatureFlags=EnableWorkerIndexing` as a legacy workaround.

---

## 2. 500 Error on All Requests

**Problem:** Every HTTP request to the function app returns a 500 Internal Server Error, regardless of which endpoint you hit.

**Cause:** There is likely an import error or syntax error in `function_app.py` or one of the blueprint files. When the Python worker fails to load the function module, all functions become unavailable.

**Solution:**

1. Check the application logs:
   ```bash
   az functionapp log tail \
      --name $APP_NAME \
      --resource-group $RG
   ```

2. Look for `ImportError`, `SyntaxError`, or `ModuleNotFoundError` in the output.

3. If the error is a missing module, check that `requirements.txt` is complete and that remote build is enabled (see issue #3 below).

4. If the error is a syntax error, fix the Python code and redeploy.

5. For local debugging, run `func host start` and check the terminal output for the exact error.

---

## 3. ModuleNotFoundError

**Problem:** The function app crashes with `ModuleNotFoundError: No module named 'some_package'` even though the package is listed in `requirements.txt`.

**Cause:** The deployment did not install Python packages. This typically happens when:

- Remote build was not triggered during deployment
- The `SCM_DO_BUILD_DURING_DEPLOYMENT` setting is not enabled
- Packages with native extensions were built on a different OS (e.g., macOS → Linux)

**Solution:**

For Consumption/Premium/Dedicated plans, ensure remote build is enabled:

```bash
az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG \
  --settings "SCM_DO_BUILD_DURING_DEPLOYMENT=true" "ENABLE_ORYX_BUILD=true"
```

Deploy with remote build flag:

```bash
# Using func CLI
func azure functionapp publish $APP_NAME --python --build remote

# Using az CLI
az functionapp deployment source config-zip \
  --name $APP_NAME \
  --resource-group $RG \
  --src deploy.zip \
  --build-remote true
```

For Flex Consumption apps, prefer the standard `func azure functionapp publish --python` workflow and avoid relying on legacy Kudu-specific app settings.

Verify `requirements.txt` is in the correct location (same directory as `function_app.py`, typically the app root).

---

## 4. Cold Start Timeout

**Problem:** The first request after a period of inactivity takes 10+ seconds or times out entirely.

**Cause:** On the Consumption plan, the function app scales to zero when idle. The first request triggers a cold start, which involves provisioning an instance, starting the Python worker, and loading all dependencies. Python apps with many dependencies can take 3–8 seconds (or longer with heavy packages like `numpy`, `pandas`, or `scikit-learn`).

**Solution:**

| Approach | Details |
|----------|---------|
| Reduce dependencies | Remove unused packages from `requirements.txt` |
| Lazy imports | Move heavy imports inside function bodies |
| Premium plan | Use always-ready instances to eliminate cold starts |
| Keep-warm timer | Add a timer trigger that fires every few minutes |
| Increase timeout | Set `functionTimeout` in `host.json` to allow more time |

```json
{
  "functionTimeout": "00:10:00"
}
```

See the [Scaling guide](../../platform/scaling.md) for detailed cold start mitigation strategies.

---

## 5. local.settings.json Not Found

**Problem:** Running `func host start` locally fails with an error about missing `local.settings.json`.

**Cause:** The `local.settings.json` file does not exist in the current directory. This file is excluded from source control via `.gitignore`, so it is not present after a fresh clone.

**Solution:**

Copy the example file:

```bash
cp local.settings.json.example local.settings.json
```

If no example file exists, create one manually:

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true"
  }
}
```

> **Note:** If you set `AzureWebJobsStorage` to `UseDevelopmentStorage=true`, you need Azurite running locally for non-HTTP triggers. For HTTP-only functions, you can use an empty string or the development storage setting.

---

## 6. Azurite Not Running

**Problem:** Functions that use Storage bindings (queue output, blob trigger, timer trigger, Durable Functions) fail locally with a connection error. HTTP triggers may also fail if `AzureWebJobsStorage` is set to `UseDevelopmentStorage=true`.

**Cause:** The local storage emulator (Azurite) is not running, but `AzureWebJobsStorage` is set to `UseDevelopmentStorage=true`.

**Solution:**

Option A — Start Azurite:

```bash
# Install Azurite
npm install -g azurite

# Start Azurite
azurite --silent --location /tmp/azurite --debug /tmp/azurite/debug.log
```

Option B — Use a real Azure Storage connection string:

```json
{
  "Values": {
    "AzureWebJobsStorage": "DefaultEndpointsProtocol=https;AccountName=$STORAGE_NAME;AccountKey=..."
  }
}
```

Option C — For HTTP-only functions, set an empty connection string:

```json
{
  "Values": {
    "AzureWebJobsStorage": ""
  }
}
```

> **Warning:** An empty `AzureWebJobsStorage` only works for HTTP triggers. Timer triggers, queue triggers, Durable Functions, and any function using storage bindings require a valid storage connection.

---

## 7. Route Not Found (404)

**Problem:** A specific endpoint returns 404 even though the function is defined.

**Cause:** Common causes include:

- The route prefix is misconfigured in `host.json`
- The blueprint is not registered in `function_app.py`
- The route is misspelled in the decorator

**Solution:**

1. Check that the blueprint is registered:
   ```python
   # function_app.py
   app = func.FunctionApp()
   app.register_functions(my_bp)  # Is this present?
   ```

2. Check the route prefix in `host.json`:
   ```json
   {
     "extensions": {
       "http": {
         "routePrefix": "api"  // URL will be /api/<route>
       }
     }
   }
   ```

3. Run `func host start` locally — the terminal lists all discovered functions and their URLs.

---

## 8. Permission Denied on Managed Identity

**Problem:** Functions using Managed Identity to access Azure resources fail with `403 Forbidden` or `AuthorizationFailed`.

**Cause:** The Managed Identity does not have the required RBAC role assignment on the target resource.

**Solution:**

```bash
# Check current role assignments
az role assignment list \
  --assignee "<object-id>" \
  --all \
  --output table

# Assign the needed role
az role assignment create \
  --assignee "<object-id>" \
  --role "<role-name>" \
  --scope "<resource-id>"
```

> **Note:** Role assignments can take up to 5 minutes to propagate. Wait and retry before further troubleshooting.

---

## 9. Deployment Succeeds but Old Code Runs

**Problem:** A deployment completes successfully, but the function app still serves old code.

**Cause:** The deployment slot was not swapped, or the function app is running from a cached package.

**Solution:**

```bash
# Restart the function app to clear any caches
az functionapp restart \
  --name $APP_NAME \
  --resource-group $RG

# If using deployment slots, verify you deployed to the correct slot
az functionapp deployment slot list \
  --name $APP_NAME \
  --resource-group $RG
```

---

## 10. Application Insights Shows No Data

**Problem:** Application Insights is configured but no telemetry appears.

**Cause:** The `APPLICATIONINSIGHTS_CONNECTION_STRING` is missing, incorrect, or the sampling settings are too aggressive.

**Solution:**

```bash
# Verify the setting exists
az functionapp config appsettings list \
  --name $APP_NAME \
  --resource-group $RG \
  --query "[?name=='APPLICATIONINSIGHTS_CONNECTION_STRING']"
```

Check `host.json` sampling settings — if `maxTelemetryItemsPerSecond` is set very low, telemetry may appear to be missing:

```json
{
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20
      }
    }
  }
}
```

Data can take 2–5 minutes to appear in Application Insights. Check the **Live Metrics** view for real-time data.

---

## 11. Outbound Requests Fail (VNet Integration)

**Problem:** Functions time out or receive connection errors when calling services that are only accessible inside a VNet (for example, a Private Endpoint database or an internal API).

**Cause:** The function app is not integrated with a VNet, or the VNet integration is not routing the required traffic through the VNet.

**Solution:**

Confirm VNet integration is active:

```bash
az functionapp vnet-integration list \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --output table
```

Expected output: one row showing the subnet resource ID. An empty table means VNet integration is not configured — see the [Networking operations guide](../../platform/networking.md) to set it up.

For traffic to private resources, ensure `WEBSITE_VNET_ROUTE_ALL` is set to `1`:

```bash
az functionapp config appsettings list \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --query "[?name=='WEBSITE_VNET_ROUTE_ALL']"
```

If the setting is missing or `0`, add it:

```bash
az functionapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --settings "WEBSITE_VNET_ROUTE_ALL=1"
```

Verify DNS resolution from the app (via Kudu console or SSH where available):

```bash
nslookup <private-resource-hostname>
```

Expected result: the hostname resolves to a private IP (for example `10.x.x.x`). If it resolves to a public IP, check the Private DNS Zone link for the VNet.

---

## 12. Function App IP Blocked by Firewall

**Problem:** Functions calling an external service receive `Connection refused` or `403 Forbidden` from the target service. The same call works locally.

**Cause:** The target service has an IP allowlist, and the function app's egress IP is not on it. Function app outbound IPs can change when the app scales or the plan is modified.

**Solution:**

Retrieve the current set of outbound IPs:

```bash
az functionapp show \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --query "{outboundIpAddresses: properties.outboundIpAddresses, possibleOutboundIpAddresses: properties.possibleOutboundIpAddresses}" \
  --output json
```

Add **all** IPs in `possibleOutboundIpAddresses` to the target service's allowlist — not just the currently active ones, as the active set can rotate.

!!! warning "NAT Gateway for stable egress"
    If you need a single, stable egress IP that does not change as the app scales, attach a NAT Gateway to the VNet integration subnet. See [Networking operations](../../platform/networking.md) for the setup steps.

---

## 13. Private Endpoint DNS Not Resolving

**Problem:** Functions receive `Name or service not known` when calling a resource (for example Cosmos DB or Key Vault) that is configured with a Private Endpoint.

**Cause:** The Private DNS Zone for the resource type is not linked to the VNet used by the function app's VNet integration subnet.

**Solution:**

List Private DNS Zones linked to the VNet:

```bash
az network private-dns link vnet list \
  --resource-group "$RG" \
  --zone-name "privatelink.documents.azure.com" \
  --output table
```

If no link exists, create one:

```bash
az network private-dns link vnet create \
  --resource-group "$RG" \
  --zone-name "privatelink.documents.azure.com" \
  --name "link-cosmos-vnet" \
  --virtual-network "vnet-prod" \
  --registration-enabled false
```

After linking, verify resolution from the app (Kudu console where available):

```bash
nslookup <account-name>.documents.azure.com
```

Expected result: resolves to a `10.x.x.x` address, not a public IP.

See also: [Networking operations](../../platform/networking.md) for the full Private Endpoint setup walkthrough.

## See Also
- [Environment Variables](environment-variables.md)
- [host.json Reference](host-json.md)
- [Observability](../../operations/monitoring.md)
- [Networking Operations](../../platform/networking.md)

## Sources
- [Python v2 Programming Model (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Develop Azure Functions Locally (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-develop-local)
