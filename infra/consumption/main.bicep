// Azure Functions Practical Guide - Consumption Plan (Y1)
//
// Deploys:
// - Linux Function App on classic Consumption plan (Y1 / Dynamic)
// - System-assigned managed identity with RBAC for identity-based host storage
// - Shared monitoring (Log Analytics + Application Insights)
//
// Key characteristics:
// - Equivalent to CLI --consumption-plan-location behavior
// - No VNet integration, no private endpoints
// - Uses AzureWebJobsStorage__accountName (identity-based, no connection string)
// - Runtime/content settings at site creation; complete appsettings reapplied after RBAC
// - Identity-based host storage is activated only by the post-RBAC appsettings resource
// - No package setting until supported publishing establishes a real artifact URL.
//   Linux Y1 does not support the local-package value 1. Remote build manages its output.
//   Reapplying appsettings replaces deployment-managed keys; coordinate a compatible republish.
//   https://learn.microsoft.com/en-us/azure/azure-functions/deployment-zip-push
//
// Deploy:
// az deployment group create --template-file infra/consumption/main.bicep --parameters baseName=myapp

targetScope = 'resourceGroup'

@description('Base name for all resources')
param baseName string

@description('Azure region for deployment')
param location string = resourceGroup().location

@description('Python runtime version')
param pythonVersion string = '3.11'

var appInsightsName = '${baseName}-insights'
var storageAccountName = toLower(replace('${baseName}storage', '-', ''))
var appServicePlanName = '${baseName}-plan'
var functionAppName = '${baseName}-func'
var contentShareName = toLower(replace('${baseName}-content', '-', ''))

// RBAC role definition IDs
var storageBlobDataOwnerRoleId = 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b'
var storageAccountContributorRoleId = '17d1049b-9a84-46fb-8f53-869881c3d3ab'
var storageQueueDataContributorRoleId = '974c5e8b-45b9-4653-ba55-5f855dd0fb88'
var storageTableDataContributorRoleId = '0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3'
var storageFileDataPrivilegedContributorRoleId = '69566ab7-960f-475b-8e7c-b3118f30c6bd'

// Connection string for WEBSITE_CONTENTAZUREFILECONNECTIONSTRING (required by platform for provisioning)
var storageAccountKey = listKeys(resourceId('Microsoft.Storage/storageAccounts', storageAccountName), '2023-05-01').keys[0].value
var storageConnectionString = 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${storageAccountKey};EndpointSuffix=${environment().suffixes.storage}'

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

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: storageAccountName
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
  kind: 'functionapp'
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
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
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: storageConnectionString
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: contentShareName
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

// Activate identity-based storage after RBAC; appsettings replaces, rather than merges, all settings.
resource functionAppSettings 'Microsoft.Web/sites/config@2024-04-01' = {
  parent: functionApp
  name: 'appsettings'
  properties: {
    FUNCTIONS_EXTENSION_VERSION: '~4'
    FUNCTIONS_WORKER_RUNTIME: 'python'
    AzureWebJobsStorage__accountName: storageAccountName
    AzureWebJobsStorage__credential: 'managedidentity'
    WEBSITE_CONTENTAZUREFILECONNECTIONSTRING: storageConnectionString
    WEBSITE_CONTENTSHARE: contentShareName
    APPLICATIONINSIGHTS_CONNECTION_STRING: appInsightsModule.outputs.connectionString
    APPINSIGHTS_INSTRUMENTATIONKEY: appInsightsModule.outputs.instrumentationKey
  }
  dependsOn: [
    blobDataOwnerAssignment
    storageAccountContributorAssignment
    queueDataContributorAssignment
    tableDataContributorAssignment
    fileDataContributorAssignment
  ]
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

// RBAC: Durable Azure Storage task hub state and history.
resource tableDataContributorAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, functionApp.id, storageTableDataContributorRoleId)
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageTableDataContributorRoleId)
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
  dependsOn: [storageModule]
}

// RBAC: Storage File Data Privileged Contributor (for content share access)
resource fileDataContributorAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, functionApp.id, storageFileDataPrivilegedContributorRoleId)
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageFileDataPrivilegedContributorRoleId)
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
  dependsOn: [storageModule]
}

output functionAppName string = functionApp.name
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'
output appInsightsName string = appInsightsName
output storageAccountName string = storageModule.outputs.name
