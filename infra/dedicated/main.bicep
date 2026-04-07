// Azure Functions Practical Guide - Dedicated Plan (S1 default)
//
// Deploys:
// - Linux Function App on Dedicated App Service Plan (S1 Standard by default)
// - VNet integration and private endpoint for the Function App (sites)
// - Private endpoints for Storage blob/queue/table services
// - System-assigned managed identity with RBAC for identity-based host storage
// - Shared monitoring (Log Analytics + Application Insights)
//
// Key characteristics:
// - alwaysOn enabled for Dedicated hosting
// - Integration subnet delegated to Microsoft.Web/serverFarms
// - Uses AzureWebJobsStorage__accountName (identity-based, no connection string)
// - Uses classic siteConfig.appSettings (not functionAppConfig)
// - WEBSITE_RUN_FROM_PACKAGE=1 for zip-based deployment (no Azure Files/content share)
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
param skuName string = 'S1'

@description('Dedicated plan SKU tier')
param skuTier string = 'Standard'

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
    allowPublicAccess: false
    allowSharedKeyAccess: false
  }
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: storageAccountName
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

resource blobPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-11-01' = {
  name: '${baseName}-pe-blob'
  location: location
  properties: {
    subnet: {
      id: vnetModule.outputs.peSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: '${baseName}-plsc-blob'
        properties: {
          privateLinkServiceId: storageModule.outputs.id
          groupIds: [
            'blob'
          ]
        }
      }
    ]
  }
}

resource blobPrivateDnsZone 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.blob.${environment().suffixes.storage}'
  location: 'global'
}

resource blobDnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: blobPrivateDnsZone
  name: '${baseName}-blob-dns-link'
  location: 'global'
  properties: {
    virtualNetwork: {
      id: vnetModule.outputs.vnetId
    }
    registrationEnabled: false
  }
}

resource blobDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-11-01' = {
  parent: blobPrivateEndpoint
  name: 'blob-dns-zone-group'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'blob-config'
        properties: {
          privateDnsZoneId: blobPrivateDnsZone.id
        }
      }
    ]
  }
}

resource queuePrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-11-01' = {
  name: '${baseName}-pe-queue'
  location: location
  properties: {
    subnet: {
      id: vnetModule.outputs.peSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: '${baseName}-plsc-queue'
        properties: {
          privateLinkServiceId: storageModule.outputs.id
          groupIds: [
            'queue'
          ]
        }
      }
    ]
  }
}

resource queuePrivateDnsZone 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.queue.${environment().suffixes.storage}'
  location: 'global'
}

resource queueDnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: queuePrivateDnsZone
  name: '${baseName}-queue-dns-link'
  location: 'global'
  properties: {
    virtualNetwork: {
      id: vnetModule.outputs.vnetId
    }
    registrationEnabled: false
  }
}

resource queueDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-11-01' = {
  parent: queuePrivateEndpoint
  name: 'queue-dns-zone-group'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'queue-config'
        properties: {
          privateDnsZoneId: queuePrivateDnsZone.id
        }
      }
    ]
  }
}

resource tablePrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-11-01' = {
  name: '${baseName}-pe-table'
  location: location
  properties: {
    subnet: {
      id: vnetModule.outputs.peSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: '${baseName}-plsc-table'
        properties: {
          privateLinkServiceId: storageModule.outputs.id
          groupIds: [
            'table'
          ]
        }
      }
    ]
  }
}

resource tablePrivateDnsZone 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.table.${environment().suffixes.storage}'
  location: 'global'
}

resource tableDnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: tablePrivateDnsZone
  name: '${baseName}-table-dns-link'
  location: 'global'
  properties: {
    virtualNetwork: {
      id: vnetModule.outputs.vnetId
    }
    registrationEnabled: false
  }
}

resource tableDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-11-01' = {
  parent: tablePrivateEndpoint
  name: 'table-dns-zone-group'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'table-config'
        properties: {
          privateDnsZoneId: tablePrivateDnsZone.id
        }
      }
    ]
  }
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
    virtualNetworkSubnetId: vnetModule.outputs.integrationSubnetId
    vnetRouteAllEnabled: true
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
  dependsOn: [
    blobDnsZoneGroup
    queueDnsZoneGroup
    tableDnsZoneGroup
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
