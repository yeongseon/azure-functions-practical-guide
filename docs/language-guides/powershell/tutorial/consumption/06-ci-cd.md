---
validation:
  az_cli:
    last_tested:
    cli_version:
    core_tools_version:
    result: not_tested
  bicep:
    last_tested:
    result: not_tested
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/consumption-plan
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local
---
# 06 - CI/CD (Consumption)

Automate build and deployment of your Consumption (Y1) PowerShell app with GitHub Actions.

## Workflow

```yaml
name: deploy-powershell-functions

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Bundle PowerShell modules
        shell: pwsh
        run: |
          Save-Module -Name Az.Accounts -Path ./Modules

      - name: Azure login
        uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Deploy to Azure Functions
        uses: Azure/functions-action@v1
        with:
          app-name: func-ps-demo
          package: .
```

## Verification

Push to `main` and confirm the workflow completes green in the Actions tab, then curl the deployed endpoint.

## Next Steps

Extend beyond HTTP with additional trigger types.

> **Next:** [07 - Extending with Triggers](07-extending-triggers.md)


## See Also

- [Tutorial Overview & Plan Chooser](../index.md)
- [PowerShell Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources

- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
- [Azure Functions Consumption plan (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/consumption-plan)
- [Run Functions locally with Core Tools (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)

!!! warning "Legacy hosting path"
    Consumption plan (Y1) content is provided for existing workloads. For most new serverless applications, prefer [Flex Consumption](../flex-consumption/01-local-run.md).
