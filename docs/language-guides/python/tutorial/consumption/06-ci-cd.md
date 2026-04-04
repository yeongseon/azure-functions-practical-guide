# 06 - CI/CD (Consumption)

Set up GitHub Actions deployment for Consumption (Y1) using `azure/functions-action@v1`, which deploys through SCM/Kudu Zip Deploy.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| GitHub repository | Actions enabled | Host CI/CD workflow |
| Function App | Consumption (Y1) | Deployment target |
| Azure CLI | 2.61+ | Generate publish profile |

## Steps

### Step 1 - Set variables

```bash
export RG="rg-func-consumption-demo"
export APP_NAME="func-consumption-demo-001"
export STORAGE_NAME="stconsumptiondemo001"
export LOCATION="eastus"
```

### Step 2 - Download publish profile

```bash
az functionapp deployment list-publishing-profiles \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --xml \
  --output tsv
```

Copy the XML output into GitHub secret `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`.

### Step 3 - Create workflow file

Create `.github/workflows/consumption-deploy.yml`:

```yaml
name: Deploy Function App (Consumption)

on:
  push:
    branches:
      - main

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install --requirement app/requirements.txt

      - name: Deploy with Azure Functions Action (SCM/ZipDeploy)
        uses: azure/functions-action@v1
        with:
          app-name: func-consumption-demo-001
          package: app
          publish-profile: ${{ secrets.AZURE_FUNCTIONAPP_PUBLISH_PROFILE }}
```

### Step 4 - Commit and push

```bash
git add ".github/workflows/consumption-deploy.yml"
git commit --message "docs: add consumption CI/CD workflow"
git push --set-upstream origin main
```

### Step 5 - Verify deployment from Actions

```bash
curl --request GET "https://$APP_NAME.azurewebsites.net/api/health"
```

Consumption supports Kudu/SCM, so this action path works well for standard zipdeploy workflows.

## Expected Output

GitHub Actions log excerpt:

```text
Run azure/functions-action@v1
Successfully parsed publish profile
Using SCM credential for deployment
Uploading package to function app...
Deployment completed successfully.
```

Health response:

```json
{"status":"healthy","timestamp":"2026-04-03T10:10:00Z","version":"1.0.0"}
```

## Next Steps

Add non-HTTP triggers and verify scaling behavior for Consumption.

> **Next:** [07 - Extending Triggers](07-extending-triggers.md)

## References

- [Azure Functions GitHub Action](https://github.com/Azure/functions-action)
- [Deploy Azure Functions with Zip Deploy](https://learn.microsoft.com/azure/azure-functions/deployment-zip-push)
- [GitHub Actions secrets](https://docs.github.com/actions/security-guides/encrypted-secrets)
