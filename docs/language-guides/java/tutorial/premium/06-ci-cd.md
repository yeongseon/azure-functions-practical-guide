---
validation:
  az_cli:
    last_tested: 2026-04-10
    cli_version: "2.83.0"
    core_tools_version: "4.8.0"
    result: pass
  bicep:
    last_tested: null
    result: not_tested
content_sources:
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-reference-java
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-scale
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/create-first-function-cli-java
---

# 06 - CI/CD (Premium)

Automate build, test, and deployment using GitHub Actions and Maven so every change ships through the same pipeline.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| JDK | 17+ | Compile and run Java functions locally |
| Maven | 3.6+ | Build and package Java artifacts |
| Azure Functions Core Tools | v4 | Start local host and publish artifacts |
| Azure CLI | 2.61+ | Provision Azure resources and inspect app state |

!!! info "Premium plan basics"
    Premium (EP) runs on always-warm workers with pre-warmed instances, supports VNet integration, deployment slots, and removes the 10-minute execution timeout. EP1 provides 1 vCPU and 3.5 GB memory per instance.

## What You'll Build

You will create a GitHub Actions workflow that builds the Java project with Maven, publishes to the Premium function app from the staging directory, and runs a post-deployment smoke test.

<!-- diagram-id: what-you-ll-build -->
```mermaid
flowchart LR
    A[Push to main] --> B[GitHub Actions]
    B --> C[Maven build + test]
    C --> D["Publish from staging dir"]
    D --> E[Smoke test]
```

## Steps

### Step 1 - Store deployment secrets in GitHub

Add repository secrets in **Settings → Secrets and variables → Actions**:

- `AZURE_CREDENTIALS` — Service principal JSON from `az ad sp create-for-rbac`
- `AZURE_FUNCTIONAPP_NAME` — e.g. `func-jprem-04100200`
- `AZURE_RESOURCE_GROUP` — e.g. `rg-func-java-prem-demo`

```bash
az ad sp create-for-rbac \
  --name "sp-func-java-deploy" \
  --role contributor \
  --scopes "/subscriptions/<subscription-id>/resourceGroups/$RG" \
  --sdk-auth
```

### Step 2 - Create workflow file

```yaml
# .github/workflows/deploy-java-premium.yml
name: Deploy Java Function (Premium)

on:
  push:
    branches: [main]
    paths:
      - 'apps/java/**'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: apps/java

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'

      - name: Build with Maven
        run: mvn --batch-mode clean package

      - name: Azure login
        uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Install Azure Functions Core Tools
        run: npm install -g azure-functions-core-tools@4

      - name: Deploy from staging directory
        run: |
          cd target/azure-functions/azure-functions-java-guide
          func azure functionapp publish ${{ secrets.AZURE_FUNCTIONAPP_NAME }}

      - name: Smoke test
        run: |
          sleep 30
          HTTP_STATUS=$(curl --silent --output /dev/null --write-out "%{http_code}" \
            "https://${{ secrets.AZURE_FUNCTIONAPP_NAME }}.azurewebsites.net/api/health")
          if [ "$HTTP_STATUS" != "200" ]; then
            echo "Smoke test failed with HTTP $HTTP_STATUS"
            exit 1
          fi
          echo "Smoke test passed (HTTP 200)"
```

!!! danger "Must publish from staging directory in CI/CD"
    The workflow must `cd target/azure-functions/azure-functions-java-guide` before running `func azure functionapp publish`. Publishing from the project root uploads the package but functions will not be indexed.

### Step 3 - Add post-deployment verification

```bash
# Verify app state
az functionapp show \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --query "{state:state, defaultHostName:defaultHostName, kind:kind, sku:sku}" \
  --output table

# Test health endpoint
curl --request GET "https://$APP_NAME.azurewebsites.net/api/health"
```

### Step 4 - Track release history

```bash
az functionapp show \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --query "{state:state, defaultHostName:defaultHostName, kind:kind, sku:sku}" \
  --output table
```

Expected output:

```text
State    DefaultHostName                        Kind               Sku
-------  -------------------------------------  -----------------  --------------
Running  func-jprem-04100200.azurewebsites.net  functionapp,linux  ElasticPremium
```

!!! note "Premium deployment slots"
    Premium supports deployment slots for zero-downtime deployments. You can extend the workflow to deploy to a staging slot first, run validation, then swap to production:

    ```bash
    func azure functionapp publish "$APP_NAME" --slot staging
    az functionapp deployment slot swap \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --slot staging \
      --target-slot production
    ```

## Verification

Successful workflow output:

```text
[INFO] BUILD SUCCESS
Getting site publishing info...
Uploading 326.23 KB [--------------------]
Upload completed successfully.
Deployment completed successfully.
Syncing triggers...
Smoke test passed (HTTP 200)
```

## Next Steps

> **Next:** [07 - Extending with Triggers](07-extending-triggers.md)

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
