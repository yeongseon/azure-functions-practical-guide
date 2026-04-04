@description('Storage account name')
param name string

@description('Azure region for deployment')
param location string

@description('Allow public network access to storage account')
param allowPublicAccess bool = true

@description('Allow shared key access for storage account')
param allowSharedKeyAccess bool = true

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: name
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: allowSharedKeyAccess
    publicNetworkAccess: allowPublicAccess ? 'Enabled' : 'Disabled'
    networkAcls: {
      defaultAction: allowPublicAccess ? 'Allow' : 'Deny'
      bypass: 'AzureServices'
    }
  }
}

output id string = storageAccount.id
output name string = storageAccount.name
output primaryEndpoints object = storageAccount.properties.primaryEndpoints

@description('Primary access key for the storage account')
output accessKey string = storageAccount.listKeys().keys[0].value
