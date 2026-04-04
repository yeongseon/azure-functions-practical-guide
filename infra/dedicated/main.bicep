// Azure Functions Field Guide - Dedicated Plan (B1 default)
//
// Deploys:
// - Linux Function App on Dedicated App Service Plan (B1 Basic by default)
// - Shared monitoring (Log Analytics + Application Insights)
// - Storage account with Azure Files content share for file share-based deployment
//
// Key characteristics:
// - alwaysOn enabled for Dedicated hosting
// - Uses classic siteConfig.appSettings (not functionAppConfig)
// - No VNet integration on B1; upgrade to S1+ for VNet features
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
var contentShareName = toLower(replace('${baseName}-content', '-', ''))

var storageConnectionString = 'DefaultEndpointsProtocol=https;AccountName=${storageModule.outputs.name};AccountKey=${storageModule.outputs.accessKey};EndpointSuffix=${environment().suffixes.storage}'

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
    allowSharedKeyAccess: true
  }
}

resource fileService 'Microsoft.Storage/storageAccounts/fileServices@2023-05-01' = {
  name: '${storageAccountName}/default'
  dependsOn: [
    storageModule
  ]
}

resource contentShare 'Microsoft.Storage/storageAccounts/fileServices/shares@2023-05-01' = {
  name: '${storageAccountName}/default/${contentShareName}'
  properties: {
    accessTier: 'TransactionOptimized'
  }
  dependsOn: [
    fileService
  ]
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
          name: 'WEBSITE_CONTENTSHARE'
          value: contentShareName
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: storageConnectionString
        }
        {
          name: 'AzureWebJobsStorage'
          value: storageConnectionString
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
  dependsOn: [
    contentShare
  ]
}

output functionAppName string = functionApp.name
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'
output appInsightsName string = appInsightsName
output storageAccountName string = storageModule.outputs.name
