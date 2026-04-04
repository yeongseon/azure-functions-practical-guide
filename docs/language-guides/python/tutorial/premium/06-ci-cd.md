# 06 - CI/CD (Premium)

Build a GitHub Actions pipeline for Azure Functions Premium, then add safe production rollout with deployment slots.

## Prerequisites

- You completed [05 - Infrastructure as Code](05-infrastructure-as-code.md).
- You exported `$RG`, `$APP_NAME`, `$PLAN_NAME`, `$STORAGE_NAME`, `$LOCATION`.
- GitHub repository admin access for Actions variables and environments.

## Steps

1. Configure OIDC service principal for GitHub Actions.

    ```bash
    az ad app create \
      --display-name "github-$APP_NAME"

    az ad sp create \
      --id "<app-id-from-previous-command>"

    az ad app federated-credential create \
      --id "<app-id-from-previous-command>" \
      --parameters '{
        "name": "github-main",
        "issuer": "https://token.actions.githubusercontent.com",
        "subject": "repo:<org>/<repo>:ref:refs/heads/main",
        "audiences": ["api://AzureADTokenExchange"]
      }'

    az role assignment create \
      --assignee "<app-id-from-previous-command>" \
      --role "Contributor" \
      --scope "/subscriptions/<subscription-id>/resourceGroups/$RG"
    ```

2. Create deployment slots for Premium staging and warm-up.

    ```bash
    az functionapp deployment slot create \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --slot "staging"

    az functionapp deployment slot list \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --output table
    ```

3. Mark slot-specific app settings.

    ```bash
    az functionapp config appsettings set \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --slot "staging" \
      --slot-settings \
        "AZURE_FUNCTIONS_ENVIRONMENT=Staging"
    ```

4. Create a GitHub Actions workflow for deploy-to-slot then swap.

    ```yaml
    name: Deploy Premium Function App

    on:
      push:
        branches:
          - main
      workflow_dispatch:

    permissions:
      id-token: write
      contents: read

    jobs:
      deploy:
        runs-on: ubuntu-latest
        steps:
          - name: Checkout
            uses: actions/checkout@v4

          - name: Setup Python
            uses: actions/setup-python@v5
            with:
              python-version: '3.11'

          - name: Install dependencies
            run: |
              python -m pip install --upgrade pip
              pip install --requirement requirements.txt
            working-directory: app

          - name: Azure login
            uses: azure/login@v2
            with:
              client-id: ${{ vars.AZURE_CLIENT_ID }}
              tenant-id: ${{ vars.AZURE_TENANT_ID }}
              subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}

          - name: Deploy to staging slot
            uses: azure/functions-action@v1
            with:
              app-name: ${{ vars.AZURE_FUNCTIONAPP_NAME }}
              slot-name: staging
              package: app

          - name: Smoke test staging
            run: |
              curl --request GET "https://${{ vars.AZURE_FUNCTIONAPP_NAME }}-staging.azurewebsites.net/api/health"

          - name: Swap staging to production
            run: |
              az functionapp deployment slot swap \
                --name "${{ vars.AZURE_FUNCTIONAPP_NAME }}" \
                --resource-group "${{ vars.AZURE_RESOURCE_GROUP }}" \
                --slot "staging" \
                --target-slot "production"
    ```

5. Deploy from local terminal to staging slot (manual fallback).

    ```bash
    cd app
    func azure functionapp publish "$APP_NAME" --python --slot "staging"
    ```

6. Validate staging and swap to production with Azure CLI.

    ```bash
    curl --request GET "https://$APP_NAME-staging.azurewebsites.net/api/health"

    az functionapp deployment slot swap \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --slot "staging" \
      --target-slot "production"

    curl --request GET "https://$APP_NAME.azurewebsites.net/api/health"
    ```

7. Verify deployment history and SCM endpoints.

    ```bash
    az functionapp deployment slot list \
      --name "$APP_NAME" \
      --resource-group "$RG" \
      --output table
    ```

    Premium includes SCM/Kudu endpoints per slot:
    - Production: `https://$APP_NAME.scm.azurewebsites.net`
    - Staging: `https://$APP_NAME-staging.scm.azurewebsites.net`

## Expected Output

```text
Name       Status
---------  ---------
production Running
staging    Running
```

```text
Deploying to function app slot...
Deployment completed successfully.
Syncing triggers...
```

```json
{"status":"healthy","timestamp":"2026-01-01T00:00:00Z","version":"1.0.0"}
```

## Next Steps

> **Next:** [07 - Extending Triggers](07-extending-triggers.md)

## Sources

- [Deploy to Azure Functions using GitHub Actions](https://learn.microsoft.com/azure/azure-functions/functions-how-to-github-actions)
- [Deployment slots for Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-deployment-slots)
- [Swap deployment slots](https://learn.microsoft.com/azure/azure-functions/functions-deployment-slots#swap-slots)
