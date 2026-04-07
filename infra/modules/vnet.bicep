@description('Base name for networking resources')
param baseName string

@description('Azure region for deployment')
param location string

@description('Delegation service name for integration subnet')
param integrationSubnetDelegation string

@description('Address prefix for integration subnet')
param integrationSubnetPrefix string

@description('Address prefix for private endpoint subnet')
param peSubnetPrefix string

var vnetName = '${baseName}-vnet'

resource vnet 'Microsoft.Network/virtualNetworks@2023-11-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
  }
}

resource integrationSubnet 'Microsoft.Network/virtualNetworks/subnets@2023-11-01' = {
  parent: vnet
  name: 'subnet-integration'
  properties: {
    addressPrefix: integrationSubnetPrefix
    delegations: [
      {
        name: 'delegation'
        properties: {
          serviceName: integrationSubnetDelegation
        }
      }
    ]
  }
}

resource peSubnet 'Microsoft.Network/virtualNetworks/subnets@2023-11-01' = {
  parent: vnet
  name: 'subnet-private-endpoints'
  properties: {
    addressPrefix: peSubnetPrefix
    privateEndpointNetworkPolicies: 'Disabled'
  }
  dependsOn: [
    integrationSubnet
  ]
}

output vnetId string = vnet.id
output integrationSubnetId string = integrationSubnet.id
output peSubnetId string = peSubnet.id
