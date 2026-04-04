# CLI Cheatsheet

Quick reference for the most commonly used commands when developing, deploying, and managing Azure Functions Python apps.

## Azure Functions Core Tools (`func`)

The `func` CLI is used for local development, testing, and deploying function apps.

### Local Development

```bash
# Start the local Functions host
func host start

# Start on a custom port
func host start --port 7072

# Start with verbose logging
func host start --verbose

# Create a new function (interactive)
func new

# Create a new function (non-interactive)
func new --name MyFunction --template "HTTP trigger" --authlevel anonymous
```

### Deployment

```bash
# Deploy to Azure (recommended for Python)
func azure functionapp publish your-func --python

# Deploy to a staging slot
func azure functionapp publish your-func --slot staging --python

# Deploy with remote build (ensures Linux-compatible packages)
func azure functionapp publish your-func --python --build remote

# Fetch app settings from Azure to local
func azure functionapp fetch-app-settings your-func
```

### Settings Management

```bash
# Add a local setting
func settings add KEY VALUE

# List local settings
func settings list

# Decrypt local settings
func settings decrypt

# Encrypt local settings
func settings encrypt
```

## Azure CLI: Function App (`az functionapp`)

### Create and Manage

```bash
# Create a function app on Consumption plan
az functionapp create \
  --name your-func \
  --resource-group your-rg \
  --storage-account yourstorage \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type linux

# Show function app details
az functionapp show \
  --name your-func \
  --resource-group your-rg

# Delete a function app
az functionapp delete \
  --name your-func \
  --resource-group your-rg

# Restart the function app
az functionapp restart \
  --name your-func \
  --resource-group your-rg

# Stop the function app
az functionapp stop \
  --name your-func \
  --resource-group your-rg

# Start the function app
az functionapp start \
  --name your-func \
  --resource-group your-rg
```

### App Settings

```bash
# Set app settings
az functionapp config appsettings set \
  --name your-func \
  --resource-group your-rg \
  --settings "KEY1=value1" "KEY2=value2"

# List all app settings
az functionapp config appsettings list \
  --name your-func \
  --resource-group your-rg

# Delete an app setting
az functionapp config appsettings delete \
  --name your-func \
  --resource-group your-rg \
  --setting-names KEY1
```

### Configuration

```bash
# Set scale limit (max instances)
az functionapp config set \
  --name your-func \
  --resource-group your-rg \
  --max-worker-count 50

# Set minimum TLS version
az functionapp config set \
  --name your-func \
  --resource-group your-rg \
  --min-tls-version 1.2

# Enable HTTPS only
az functionapp update \
  --name your-func \
  --resource-group your-rg \
  --set httpsOnly=true

# Show configuration
az functionapp config show \
  --name your-func \
  --resource-group your-rg
```

### Deployment Slots

```bash
# Create a staging slot
az functionapp deployment slot create \
  --name your-func \
  --resource-group your-rg \
  --slot staging

# Swap staging to production
az functionapp deployment slot swap \
  --name your-func \
  --resource-group your-rg \
  --slot staging \
  --target-slot production

# List slots
az functionapp deployment slot list \
  --name your-func \
  --resource-group your-rg

# Delete a slot
az functionapp deployment slot delete \
  --name your-func \
  --resource-group your-rg \
  --slot staging
```

### Identity and Keys

```bash
# Enable system-assigned Managed Identity
az functionapp identity assign \
  --name your-func \
  --resource-group your-rg

# Show identity
az functionapp identity show \
  --name your-func \
  --resource-group your-rg

# List function keys
az functionapp function keys list \
  --name your-func \
  --resource-group your-rg \
  --function-name health

# List host keys
az functionapp keys list \
  --name your-func \
  --resource-group your-rg
```

### Logs

```bash
# Stream live logs
az functionapp log tail \
  --name your-func \
  --resource-group your-rg

# Download logs
az functionapp log download \
  --name your-func \
  --resource-group your-rg \
  --log-file /tmp/func-logs.zip
```

### CORS

```bash
# Add allowed origins
az functionapp cors add \
  --name your-func \
  --resource-group your-rg \
  --allowed-origins "https://example.com" "http://localhost:3000"

# Show CORS settings
az functionapp cors show \
  --name your-func \
  --resource-group your-rg

# Remove an origin
az functionapp cors remove \
  --name your-func \
  --resource-group your-rg \
  --allowed-origins "http://localhost:3000"
```

## Azure CLI: Resource Groups (`az group`)

```bash
# Create a resource group
az group create \
  --name your-rg \
  --location eastus

# List resource groups
az group list --output table

# Delete a resource group (and ALL resources in it)
az group delete \
  --name your-rg \
  --yes --no-wait
```

## Azure CLI: Deployments (`az deployment group`)

```bash
# Deploy Bicep template
az deployment group create \
  --resource-group your-rg \
  --template-file infra/main.bicep \
  --parameters appName=your-func

# Validate a Bicep template (dry run)
az deployment group validate \
  --resource-group your-rg \
  --template-file infra/main.bicep \
  --parameters appName=your-func

# Show deployment status
az deployment group show \
  --resource-group your-rg \
  --name main

# List deployments
az deployment group list \
  --resource-group your-rg \
  --output table
```

## Azure CLI: Monitoring

```bash
# Create a metric alert
az monitor metrics alert create \
  --name "func-errors" \
  --resource-group your-rg \
  --scopes "<function-app-resource-id>" \
  --condition "total Http5xx > 10" \
  --window-size 5m

# Query Application Insights logs
az monitor app-insights query \
  --app your-appinsights \
  --analytics-query "requests | take 10"

# List metrics
az monitor metrics list \
  --resource "<function-app-resource-id>" \
  --metric "FunctionExecutionCount"
```

## Quick Reference Table

| Task | Command |
|------|---------|
| Start locally | `func host start` |
| Deploy to Azure | `func azure functionapp publish your-func --python` |
| Set app setting | `az functionapp config appsettings set --name your-func --resource-group your-rg --settings "KEY=value"` |
| Stream logs | `az functionapp log tail --name your-func --resource-group your-rg` |
| Create slot | `az functionapp deployment slot create --name your-func --resource-group your-rg --slot staging` |
| Swap slot | `az functionapp deployment slot swap --name your-func --resource-group your-rg --slot staging` |
| Enable identity | `az functionapp identity assign --name your-func --resource-group your-rg` |
| Deploy Bicep | `az deployment group create --resource-group your-rg --template-file infra/main.bicep` |

## See Also
- [Deployments](../../operations/deployment.md)

## References
- [Azure Functions Core Tools Reference (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
- [Azure Functions CLI Reference (Microsoft Learn)](https://learn.microsoft.com/cli/azure/functionapp)
- [Develop Azure Functions Locally (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-develop-local)
