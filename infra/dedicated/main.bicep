// Azure Functions Field Guide - Dedicated Plan (B1 default)
//
// Deploys:
// - Linux Function App on Dedicated App Service Plan (B1 Basic by default)
// - System-assigned managed identity with RBAC for identity-based host storage
// - Shared monitoring (Log Analytics + Application Insights)
//
// Key characteristics:
// - alwaysOn enabled for Dedicated hosting
// - Uses AzureWebJobsStorage__accountName (identity-based, no connection string)
// - Uses classic siteConfig.appSettings (not functionAppConfig)
// - No VNet integration on B1; upgrade to S1+ for VNet features
// - WEBSITE_RUN_FROM_PACKAGE=1 for zip-based deployment (no content share needed)
//
// Deploy:
// az deployment group create --template-file infra/dedicated/main.bicep --parameters baseName=myapp

targetScope = 'resourceGroup'

@description('Base name for all resources')
param baseName string

@description('Azure region for deployment')
param location string = resourceGroup().location

@description('Python runtime version')
param pythonVersion string = '3.11'

@description('Dedicated plan SKU name')
param skuName string = 'B1'

@description('Dedicated plan SKU tier')
param skuTier string = 'Basic'

var appInsightsName = '${baseName}-insights'
var storageAccountName = toLower(replace('${baseName}storage', '-', ''))
var appServicePlanName = '${baseName}-plan'
var functionAppName = '${baseName}-func'

// RBAC role definition IDs
var storageBlobDataOwnerRoleId = 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b'
var storageAccountContributorRoleId = '17d1049b-9a84-46fb-8f53-869881c3d3ab'
var storageQueueDataContributorRoleId = '974c5e8b-45b9-4653-ba55-5f855dd0fb88'

module appInsightsModule '../modules/app-insights.bicep' = {
  name: 'appInsightsModule'
  params: {
    baseName: baseName
    location: location
  }
}

module storageModule '../modules/storage-account.bicep' = {
  name: 'storageModule'
  params: {
    name: storageAccountName
    location: location
    allowPublicAccess: true
    allowSharedKeyAccess: false
  }
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: storageAccountName
}

resource appServicePlan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: appServicePlanName
  location: location
  kind: 'linux'
  sku: {
    name: skuName
    tier: skuTier
  }
  properties: {
    reserved: true
  }
}

resource functionApp 'Microsoft.Web/sites@2024-04-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      alwaysOn: true
      linuxFxVersion: 'Python|${pythonVersion}'
      minTlsVersion: '1.2'
      ftpsState: 'Disabled'
      appSettings: [
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'AzureWebJobsStorage__accountName'
          value: storageAccountName
        }
        {
          name: 'AzureWebJobsStorage__credential'
          value: 'managedidentity'
        }
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '1'
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsightsModule.outputs.connectionString
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsightsModule.outputs.instrumentationKey
        }
      ]
    }
  }
}

// RBAC: Storage Blob Data Owner
resource blobDataOwnerAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, functionApp.id, storageBlobDataOwnerRoleId)
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataOwnerRoleId)
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
  dependsOn: [storageModule]
}

// RBAC: Storage Account Contributor
resource storageAccountContributorAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, functionApp.id, storageAccountContributorRoleId)
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageAccountContributorRoleId)
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
  dependsOn: [storageModule]
}

// RBAC: Storage Queue Data Contributor
resource queueDataContributorAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, functionApp.id, storageQueueDataContributorRoleId)
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageQueueDataContributorRoleId)
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
  dependsOn: [storageModule]
}

output functionAppName string = functionApp.name
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'
output appInsightsName string = appInsightsName
output storageAccountName string = storageModule.outputs.name
