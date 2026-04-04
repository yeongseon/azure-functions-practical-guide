# Deployment

This guide covers operational deployment execution for Azure Functions.
It focuses on release methods, slot strategy, and rollback safety.

!!! tip "Platform Guide"
    For scaling architecture and plan comparison, see [Scaling](../platform/scaling.md).

!!! tip "Language Guide"
    For Python deployment specifics, see the [Python Tutorial](../language-guides/python/tutorial/index.md).

## Deployment methods

| Method | Best fit | Notes |
|---|---|---|
| `func azure functionapp publish` | Manual and rapid deployments | Works for local operator-driven releases |
| Zip deploy (`az functionapp deployment source config-zip`) | Scripted artifact deployment | Standard on Consumption, Premium, Dedicated |
| GitHub Actions | Continuous deployment | Recommended for repository-native CI/CD |
| Azure DevOps | Governed enterprise release process | Useful for gated stages and approvals |

## Deploy with Core Tools

```bash
func azure functionapp publish <app-name>
```

Use this for operator-driven release or emergency recovery deployment.

!!! note "Production practice"
    Prefer pipeline deployment for repeatability and auditability.

## Deploy with zip artifact

```bash
az functionapp deployment source config-zip \
    --resource-group <resource-group> \
    --name <app-name> \
    --src <path-to-artifact-zip>
```

Enable run-from-package when using immutable artifact patterns:

```bash
az functionapp config appsettings set \
    --resource-group <resource-group> \
    --name <app-name> \
    --settings WEBSITE_RUN_FROM_PACKAGE=1
```

## GitHub Actions pipeline

```yaml
name: deploy-functions

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Azure login with OIDC
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Deploy function app
        uses: azure/functions-action@v1
        with:
          app-name: <app-name>
          package: <artifact-directory-or-zip>
```

Use OIDC where possible to avoid long-lived deployment secrets.

## Azure DevOps pipeline

```yaml
trigger:
  branches:
    include:
      - main

steps:
  - task: AzureFunctionApp@2
    displayName: Deploy Azure Function App
    inputs:
      azureSubscription: <service-connection>
      appType: functionAppLinux
      appName: <app-name>
      package: <artifact-path>
```

## Deployment slots (Consumption, Premium, and Dedicated)

Use slots for safe cutover and fast rollback.

> **Note:** Classic Consumption supports 2 slots total (including production). Flex Consumption does not support deployment slots.

### Create staging slot

```bash
az functionapp deployment slot create \
    --resource-group <resource-group> \
    --name <app-name> \
    --slot staging
```

### Configure slot-specific settings

```bash
az functionapp config appsettings set \
    --resource-group <resource-group> \
    --name <app-name> \
    --slot staging \
    --slot-settings AZURE_FUNCTIONS_ENVIRONMENT=Staging
```

### Swap staging into production

```bash
az functionapp deployment slot swap \
    --resource-group <resource-group> \
    --name <app-name> \
    --slot staging \
    --target-slot production
```

## Rollback runbook

Preferred sequence:

1. Roll back with slot swap-back when slots are in use.
2. Redeploy last-known-good artifact when slots are unavailable.
3. Reapply previous config baseline if release changed settings.

### Slot swap-back

```bash
az functionapp deployment slot swap \
    --resource-group <resource-group> \
    --name <function-app-name> \
    --slot staging \
    --target-slot production
```

### Artifact rollback

```bash
az functionapp deployment source config-zip \
    --resource-group <resource-group> \
    --name <app-name> \
    --src <last-known-good-zip>
```

## Post-deploy checks

- Health endpoint is successful.
- Failure ratio does not regress.
- Duration percentiles stay within expected range.
- Queue backlog does not grow unexpectedly.

## See Also

- [Configuration](configuration.md)
- [Monitoring](monitoring.md)
- [Recovery](recovery.md)

## Sources

- [Deploy Azure Functions from package files](https://learn.microsoft.com/azure/azure-functions/run-functions-from-deployment-package)
- [Deploy Azure Functions with GitHub Actions](https://learn.microsoft.com/azure/azure-functions/functions-how-to-github-actions)
- [Deployment slots in Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-deployment-slots)
- [Functions Core Tools reference](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
