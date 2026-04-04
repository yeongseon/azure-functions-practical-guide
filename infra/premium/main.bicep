// Azure Functions Field Guide - Premium Plan (EP1)
//
// Deploys:
// - Linux Function App on Elastic Premium (EP1)
// - VNet integration and private endpoint for the Function App (sites)
// - Storage account with Azure Files content share for file share-based deployment
// - Shared monitoring (Log Analytics + Application Insights)
//
// Key characteristics:
// - Integration subnet delegated to Microsoft.Web/serverFarms
// - Uses classic siteConfig.appSettings (not functionAppConfig)
// - Premium supports VNet integration and private endpoints
//
// Deploy:
// az deployment group create --template-file infra/premium/main.bicep --parameters baseName=myapp

targetScope = 'resourceGroup'

@description('Base name for all resources')
param baseName string

@description('Azure region for deployment')
param location string = resourceGroup().location

@description('Python runtime version')
param pythonVersion string = '3.11'

@description('Premium plan SKU name')
param skuName string = 'EP1'

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
    allowPublicAccess: false
    allowSharedKeyAccess: true
  }
}

module vnetModule '../modules/vnet.bicep' = {
  name: 'vnetModule'
  params: {
    baseName: baseName
    location: location
    integrationSubnetDelegation: 'Microsoft.Web/serverFarms'
    integrationSubnetPrefix: '10.0.1.0/24'
    peSubnetPrefix: '10.0.2.0/24'
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
  kind: 'elastic'
  sku: {
    name: skuName
    tier: 'ElasticPremium'
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
    virtualNetworkSubnetId: vnetModule.outputs.integrationSubnetId
    siteConfig: {
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

resource functionAppPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-11-01' = {
  name: '${baseName}-pe-site'
  location: location
  properties: {
    subnet: {
      id: vnetModule.outputs.peSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: '${baseName}-plsc-site'
        properties: {
          privateLinkServiceId: functionApp.id
          groupIds: [
            'sites'
          ]
        }
      }
    ]
  }
}

resource webPrivateDnsZone 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.azurewebsites.net'
  location: 'global'
}

resource webDnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: webPrivateDnsZone
  name: '${baseName}-web-dns-link'
  location: 'global'
  properties: {
    virtualNetwork: {
      id: vnetModule.outputs.vnetId
    }
    registrationEnabled: false
  }
}

resource webDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-11-01' = {
  parent: functionAppPrivateEndpoint
  name: 'web-dns-zone-group'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'web-config'
        properties: {
          privateDnsZoneId: webPrivateDnsZone.id
        }
      }
    ]
  }
}

output functionAppName string = functionApp.name
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'
output appInsightsName string = appInsightsName
output storageAccountName string = storageModule.outputs.name
