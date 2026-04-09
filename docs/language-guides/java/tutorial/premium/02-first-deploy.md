---
hide:
  - toc
validation:
  az_cli:
    last_tested: 2026-04-10
    cli_version: "2.83.0"
    core_tools_version: "4.8.0"
    result: pass
  bicep:
    last_tested: null
    result: not_tested
---

# 02 - First Deploy (Premium)

Provision Azure resources and deploy the Java reference application to the Premium (EP1) plan with repeatable CLI commands.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| JDK | 17+ | Compile and run Java functions locally |
| Maven | 3.6+ | Build and package Java artifacts |
| Azure Functions Core Tools | v4 | Start local host and publish artifacts |
| Azure CLI | 2.61+ | Provision Azure resources and inspect app state |
| Azure subscription | Active | Target for deployment |

!!! info "Premium plan basics"
    Premium (EP) runs on always-warm workers with pre-warmed instances, supports VNet integration, deployment slots, and removes the 10-minute execution timeout. EP1 provides 1 vCPU and 3.5 GB memory per instance.

## What You'll Build

You will provision a Linux Premium (EP1) Function App for Java, deploy with `func azure functionapp publish` from the Maven staging directory, and validate HTTP endpoints.

!!! info "Infrastructure Context"
    **Plan**: Premium EP1 | **Network**: Public internet + VNet integration supported | **Always On**: ✅ Enabled by default

    Premium uses Azure Files content share for deployment artifacts. The plan keeps at least one instance warm at all times, eliminating cold starts for latency-sensitive workloads.

    ```mermaid
    flowchart TD
        INET[Internet] -->|HTTPS| FA[Function App\nPremium EP1\nLinux Java 17]

        FA -->|connection string| ST[Storage Account]
        FA --> AI[Application Insights]

        subgraph STORAGE[Storage Services]
            ST --- FS[Azure Files\ncontent share]
            ST --- QS[Queue Storage]
            ST --- BS[Blob Storage]
        end

        VNET["✅ VNet integration available\n✅ Private endpoints supported"] -. capability .- FA

        style FA fill:#0078d4,color:#fff
        style VNET fill:#E8F5E9,stroke:#4CAF50
        style STORAGE fill:#FFF3E0
    ```

```mermaid
flowchart LR
    A[Set variables + login] --> B[Create RG + storage]
    B --> C[Create Premium plan]
    C --> D[Create function app]
    D --> E[Set placeholder settings]
    E --> F["Build + publish from staging dir"]
    F --> G[Validate endpoints]
```

## Steps

### Step 1 - Set variables and sign in

```bash
export RG="rg-func-java-prem-demo"
export APP_NAME="func-jprem-$(date +%m%d%H%M)"
export STORAGE_NAME="stjprem$(date +%m%d)"
export PLAN_NAME="plan-jprem-$(date +%m%d)"
export LOCATION="koreacentral"

az login
az account set --subscription "<subscription-id>"
```

!!! note "Storage account name limits"
    Storage account names must be 3-24 characters, lowercase letters and digits only. The `$STORAGE_NAME` pattern above keeps names short to stay within limits.

### Step 2 - Create resource group and storage account

```bash
az group create --name "$RG" --location "$LOCATION"

az storage account create \
  --name "$STORAGE_NAME" \
  --resource-group "$RG" \
  --location "$LOCATION" \
  --sku Standard_LRS \
  --kind StorageV2
```

### Step 3 - Create Premium plan

```bash
az functionapp plan create \
  --name "$PLAN_NAME" \
  --resource-group "$RG" \
  --location "$LOCATION" \
  --sku EP1 \
  --is-linux
```

!!! note "Premium plan vs Consumption"
    Unlike Consumption, Premium requires an explicit plan resource. The `--sku EP1` flag selects the smallest Premium tier. The `--is-linux` flag creates a Linux plan required for Java.

### Step 4 - Create function app

```bash
az functionapp create \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --plan "$PLAN_NAME" \
  --storage-account "$STORAGE_NAME" \
  --runtime java \
  --runtime-version 17 \
  --functions-version 4 \
  --os-type Linux
```

!!! note "Auto-created Application Insights"
    `az functionapp create` automatically provisions an Application Insights resource and links it to the function app. You do not need to create one manually unless you want a custom name or configuration.

!!! note "Premium uses `--plan` not `--consumption-plan-location`"
    Consumption uses `--consumption-plan-location` to create an implicit plan. Premium requires a pre-created plan specified with `--plan`.

### Step 5 - Set placeholder trigger settings

```bash
STORAGE_CONN=$(az storage account show-connection-string \
  --name "$STORAGE_NAME" \
  --resource-group "$RG" \
  --output tsv)

az functionapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --settings \
    "QueueStorage=$STORAGE_CONN" \
    "EventHubConnection=Endpoint=sb://placeholder.servicebus.windows.net/;SharedAccessKeyName=placeholder;SharedAccessKey=cGxhY2Vob2xkZXI=;EntityPath=placeholder"
```

!!! warning "Placeholder settings prevent host crashes"
    The Java reference app includes triggers for Queue, EventHub, Blob, and Timer. If connection settings are missing or use an invalid format, the Functions host enters an error state and cannot index any functions.

    **For QueueStorage**: Use a real storage connection string, not a placeholder. A fake AccountKey causes 403 errors when the queue listener starts, crashing the entire host and returning 502 on all HTTP requests.

### Step 6 - Create trigger resources

```bash
az storage queue create \
  --name "incoming-orders" \
  --account-name "$STORAGE_NAME"

az storage container create \
  --name "uploads" \
  --account-name "$STORAGE_NAME"
```

### Step 7 - Build and publish

```bash
cd apps/java
mvn clean package
```

!!! danger "Must publish from Maven staging directory"
    Java function apps **must** be published from the Maven staging directory, NOT from the project root. The `azure-functions-maven-plugin` generates `function.json` files in `target/azure-functions/<appName>/`. Publishing from the project root uploads the package but functions will not be indexed (0 functions found).

```bash
cd target/azure-functions/azure-functions-java-guide
func azure functionapp publish "$APP_NAME"
```

Expected output:

```text
Getting site publishing info...
Uploading package...
Uploading 326.23 KB [--------------------]
Upload completed successfully.
Deployment completed successfully.
Syncing triggers...
```

### Step 8 - Validate deployment

```bash
# Check app state
az functionapp show \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --query "{state:state, defaultHostName:defaultHostName, kind:kind, sku:sku}" \
  --output table

# Test the health endpoint
curl --request GET "https://$APP_NAME.azurewebsites.net/api/health"

# Test the hello endpoint
curl --request GET "https://$APP_NAME.azurewebsites.net/api/hello/Premium"

# Test the info endpoint
curl --request GET "https://$APP_NAME.azurewebsites.net/api/info"
```

### Step 9 - Review Premium-specific notes

- Premium uses `--plan` with a pre-created EP1 plan, unlike Consumption's `--consumption-plan-location`.
- Always On is enabled by default — no cold starts.
- Premium supports VNet integration, private endpoints, and deployment slots.
- Premium has no execution timeout limit (Consumption has 5-minute default, 10-minute max).
- Use long-form CLI flags for maintainable runbooks.
- Keep `FUNCTIONS_WORKER_RUNTIME=java` across all environments.

## Verification

App state output:

```text
State    DefaultHostName                        Kind               Sku
-------  -------------------------------------  -----------------  --------------
Running  func-jprem-04100200.azurewebsites.net  functionapp,linux  ElasticPremium
```

Health endpoint response:

```json
{"status":"healthy","timestamp":"2026-04-09T17:09:47.112Z","version":"1.0.0"}
```

Hello endpoint response:

```json
{"message":"Hello, Premium"}
```

Info endpoint response:

```json
{"name":"azure-functions-java-guide","version":"1.0.0","java":"17.0.14","os":"Linux","environment":"production","functionApp":"func-jprem-04100200"}
```

!!! note "Function list indexing delay on Premium"
    `az functionapp function list` may return empty results for several minutes after deployment, even though all HTTP endpoints respond correctly. This is a known Azure management API indexing delay — not a deployment failure.

## Next Steps

> **Next:** [03 - Configuration](03-configuration.md)

## See Also

- [Tutorial Overview & Plan Chooser](../index.md)
- [Java Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources

- [Azure Functions Java developer guide (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-java)
- [Azure Functions hosting options (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-scale)
- [Create a Java function with Azure Functions Core Tools (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/create-first-function-cli-java)
