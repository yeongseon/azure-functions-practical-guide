#!/bin/bash
set -euo pipefail

echo "============================================"
echo "Azure Functions Field Guide — Python Reference App Deploy"
echo "Flex Consumption + VNet + Private Endpoint"
echo "============================================"
echo ""

# Load environment variables
if [ -f .env ]; then
  echo "Loading configuration from .env file..."
  set -a
  source .env
  set +a
else
  echo "  .env file not found. Using default values..."
fi

RESOURCE_GROUP_NAME=${RESOURCE_GROUP_NAME:-"rg-functions-python"}
LOCATION=${LOCATION:-"koreacentral"}
BASE_NAME=${BASE_NAME:-"pyfunc"}

echo "Configuration:"
echo "  Resource Group: $RESOURCE_GROUP_NAME"
echo "  Location: $LOCATION"
echo "  Base Name: $BASE_NAME"
echo ""

read -p "Continue with deployment? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Deployment cancelled."
  exit 1
fi

echo ""
echo "Step 1/5: Checking Azure CLI login status..."
if ! az account show > /dev/null 2>&1; then
  echo "Not logged in to Azure. Please run 'az login' first."
  exit 1
fi
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
echo "Logged in to Azure subscription: $SUBSCRIPTION_NAME"

echo ""
echo "Step 2/5: Creating resource group..."
az group create --name "$RESOURCE_GROUP_NAME" --location "$LOCATION" --output none
echo "Resource group ready: $RESOURCE_GROUP_NAME"

echo ""
echo "Step 3/5: Deploying infrastructure (Bicep)..."
echo "  This deploys: VNet, Storage (Private Endpoint - Blob), Flex Consumption Function App"
echo "  Estimated time: 5-10 minutes..."
DEPLOYMENT_OUTPUT=$(az deployment group create \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --template-file main.bicep \
  --parameters \
    baseName="$BASE_NAME" \
    location="$LOCATION" \
  --output json)

FUNCTION_APP_NAME=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.properties.outputs.functionAppName.value')
FUNCTION_APP_URL=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.properties.outputs.functionAppUrl.value')
APP_INSIGHTS_NAME=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.properties.outputs.appInsightsName.value')
STORAGE_ACCOUNT_NAME=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.properties.outputs.storageAccountName.value')
VNET_NAME=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.properties.outputs.vnetName.value')
MANAGED_IDENTITY_NAME=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.properties.outputs.managedIdentityName.value')

echo "Infrastructure deployed!"

# Save deployment output
cat > .deploy-output.env << EOF
# Deployment Output - Generated at $(date -u +"%Y-%m-%dT%H:%M:%SZ")
RESOURCE_GROUP_NAME=$RESOURCE_GROUP_NAME
FUNCTION_APP_NAME=$FUNCTION_APP_NAME
FUNCTION_APP_URL=$FUNCTION_APP_URL
APP_INSIGHTS_NAME=$APP_INSIGHTS_NAME
STORAGE_ACCOUNT_NAME=$STORAGE_ACCOUNT_NAME
VNET_NAME=$VNET_NAME
MANAGED_IDENTITY_NAME=$MANAGED_IDENTITY_NAME
EOF
echo "Deployment outputs saved to .deploy-output.env"

echo ""
echo "Step 4/5: Deploying function app code..."
echo "  Publishing with Azure Functions Core Tools..."
pushd ../apps/python > /dev/null

func azure functionapp publish "$FUNCTION_APP_NAME" --python

popd > /dev/null
echo "Function app code deployed!"

echo ""
echo "Step 5/5: Verifying deployment..."
echo "  Waiting 60 seconds for function app to start (Flex Consumption cold start)..."
sleep 60

echo "Testing health endpoint..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FUNCTION_APP_URL/api/health" --max-time 30 || echo "000")

if [ "$HTTP_STATUS" = "200" ]; then
  echo "Application is healthy!"
else
  echo "Application returned HTTP $HTTP_STATUS. It may still be starting up."
  echo "   This is normal for Flex Consumption with VNet integration (cold start can take longer)."
  echo "   Check logs: az functionapp log tail --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP_NAME"
fi

echo ""
echo "============================================"
echo "Deployment Completed!"
echo "============================================"
echo ""
echo "Architecture:"
echo "  Plan:              Flex Consumption (FC1)"
echo "  VNet:              $VNET_NAME"
echo "  VNet Integration:  subnet-integration (10.0.1.0/24)"
echo "  Private Endpoint:  ${BASE_NAME}-pe-blob (Blob only)"
echo "  Storage Account:   $STORAGE_ACCOUNT_NAME (public access disabled)"
echo "  Managed Identity:  $MANAGED_IDENTITY_NAME"
echo ""
echo "Application URL: $FUNCTION_APP_URL"
echo ""
echo "Endpoints:"
echo "  Health:        $FUNCTION_APP_URL/api/health"
echo "  Info:          $FUNCTION_APP_URL/api/info"
echo "  Log Levels:    $FUNCTION_APP_URL/api/requests/log-levels"
echo "  External Dep:  $FUNCTION_APP_URL/api/dependencies/external"
echo "  Test Error:    $FUNCTION_APP_URL/api/exceptions/test-error"
echo ""
echo "Useful commands:"
echo "  az functionapp log tail --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP_NAME"
echo "  az functionapp show --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP_NAME"
echo "  az network private-endpoint show --name ${BASE_NAME}-pe-blob --resource-group $RESOURCE_GROUP_NAME"
echo ""
echo "Verify Private Endpoint:"
echo "  az network private-endpoint show --name ${BASE_NAME}-pe-blob --resource-group $RESOURCE_GROUP_NAME --query 'customDnsConfigs[0].ipAddresses[0]' -o tsv"
echo ""
echo "Cleanup:"
echo "  az group delete --name $RESOURCE_GROUP_NAME --yes --no-wait"
echo ""
