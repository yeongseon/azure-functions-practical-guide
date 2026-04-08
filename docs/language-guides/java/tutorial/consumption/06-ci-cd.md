# 06 - CI/CD (Consumption)

Automate build, test, and deployment using GitHub Actions and Maven so every change ships through the same pipeline.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| JDK | 17+ | Compile and run Java functions locally |
| Maven | 3.9+ | Build and deploy Java artifacts |
| Azure Functions Core Tools | v4 | Start local host and publish artifacts |
| Azure CLI | 2.61+ | Provision Azure resources and inspect app state |

## What You'll Build

You will configure a GitHub Actions pipeline that builds and deploys a Java Function App with Maven, then verify the release with a function-key-based smoke test and workflow run evidence.

!!! info "Plan basics"
    Consumption (Y1) is fully serverless with scale-to-zero and pay-per-execution billing. It is ideal for bursty workloads that do not require VNet integration.

```mermaid
flowchart LR
    A[Push to main] --> B[GitHub Actions]
    B --> C[Maven build and test]
    C --> D[Deploy to Function App]
    D --> E[Smoke test]
```

## Steps

### Step 1 - Store deployment secrets in GitHub

Add repository secrets:

- `AZURE_CREDENTIALS`
- `AZURE_FUNCTIONAPP_NAME`
- `AZURE_RESOURCE_GROUP`

### Step 2 - Create workflow file

```yaml
name: deploy-java-function
on:
  push:
    branches: [ main ]
env:
  AZURE_FUNCTIONAPP_NAME: ${{ secrets.AZURE_FUNCTIONAPP_NAME }}
  AZURE_RESOURCE_GROUP: ${{ secrets.AZURE_RESOURCE_GROUP }}
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'
      - name: Build
        run: mvn --batch-mode clean verify
      - name: Azure login
        uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      - name: Deploy
        run: |
          mvn --batch-mode azure-functions:deploy \
            -DfunctionAppName=${{ env.AZURE_FUNCTIONAPP_NAME }} \
            -DresourceGroup=${{ env.AZURE_RESOURCE_GROUP }}
```

### Step 3 - Add post-deployment smoke test

```bash
curl --request GET https://$APP_NAME.azurewebsites.net/api/health?code=$(az functionapp keys list --resource-group $RG --name $APP_NAME --query "functionKeys.default" --output tsv)
```

### Step 4 - Validate the release

```bash
FUNC_KEY=$(az functionapp keys list --resource-group $RG --name $APP_NAME --query "functionKeys.default" --output tsv)
curl --header "x-functions-key: $FUNC_KEY" "https://$APP_NAME.azurewebsites.net/api/health"
az functionapp show --name $APP_NAME --resource-group $RG --query "lastModifiedTimeUtc" --output tsv
```

Use GitHub Actions run history as the deployment timeline of record (`Actions` tab -> workflow runs -> latest commit SHA), and compare it with `lastModifiedTimeUtc` to confirm release timing.

## Verification

```text
[INFO] BUILD SUCCESS
[INFO] Successfully deployed package to Azure Functions.
```

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
