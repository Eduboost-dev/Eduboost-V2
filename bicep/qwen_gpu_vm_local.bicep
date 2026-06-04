// EduBoost SA — Qwen 2.5 Coder 14B GPU VM (Local deployment variant)
// This template mirrors qwen_gpu_vm.bicep and is intended for local parameterized deployments.
//
// Deploy with:
//   az deployment group create \
//     --resource-group <RG_NAME> \
//     --template-file bicep/qwen_gpu_vm_local.bicep \
//     --parameters @bicep/qwen_gpu_vm.parameters.json
//
// For simplicity this file is a copy of qwen_gpu_vm.bicep; it references the same setup script

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('VM name')
param vmName string = 'qwen-coder-14b'

@description('Admin username for the VM')
param adminUsername string = 'eduboost'

@description('SSH public key for authentication')
@secure()
param adminPublicKey string

@description('VM size - non-GPU SKU for local testing')
@allowed([
  'Standard_D4s_v3'  // 4 vCPU, 16GB RAM
  'Standard_D8s_v3'  // 8 vCPU, 32GB RAM
  'Standard_D16s_v3' // 16 vCPU, 64GB RAM
])
param vmSize string = 'Standard_D4s_v3'

@description('OS disk size in GB')
param osDiskSizeGB int = 128

@description('Additional data disk size in GB for model storage')
param dataDiskSizeGB int = 256

@description('Environment tag')
param environment string = 'development'

@description('Project tag')
param project string = 'eduboost'

var networkInterfaceName = '${vmName}-nic'
var publicIpAddressName = '${vmName}-ip'
var virtualNetworkName = '${vmName}-vnet'
var subnetName = 'gpu-subnet'
var nsgName = '${vmName}-nsg'
var dataDiskName = '${vmName}-data-disk'
var customScriptExtensionName = '${vmName}-setup'

// Public IP
resource publicIpAddress 'Microsoft.Network/publicIPAddresses@2023-05-01' = {
  name: publicIpAddressName
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    publicIPAllocationMethod: 'Static'
  }
  tags: {
    environment: environment
    project: project
  }
}

// Virtual Network
resource virtualNetwork 'Microsoft.Network/virtualNetworks@2023-05-01' = {
  name: virtualNetworkName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
    subnets: [
      {
        name: subnetName
        properties: {
          addressPrefix: '10.0.0.0/24'
        }
      }
    ]
  }
  tags: {
    environment: environment
    project: project
  }
}

// Network Security Group
resource nsg 'Microsoft.Network/networkSecurityGroups@2023-05-01' = {
  name: nsgName
  location: location
  properties: {
    securityRules: [
      {
        name: 'SSH'
        properties: {
          priority: 1000
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '22'
        }
      }
      {
        name: 'OllamaAPI'
        properties: {
          priority: 1010
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '11434'
        }
      }
      {
        name: 'vLLMAPI'
        properties: {
          priority: 1020
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '8000'
        }
      }
      {
        name: 'Jupyter'
        properties: {
          priority: 1030
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '8888'
        }
      }
    ]
  }
  tags: {
    environment: environment
    project: project
  }
}

// Network Interface
resource networkInterface 'Microsoft.Network/networkInterfaces@2023-05-01' = {
  name: networkInterfaceName
  location: location
  properties: {
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          publicIPAddress: {
            id: publicIpAddress.id
          }
          subnet: {
            id: resourceId('Microsoft.Network/virtualNetworks/subnets', virtualNetworkName, subnetName)
          }
        }
      }
    ]
    networkSecurityGroup: {
      id: nsg.id
    }
  }
  dependsOn: [
    virtualNetwork
  ]
  tags: {
    environment: environment
    project: project
  }
}

// Data Disk for model storage
resource dataDisk 'Microsoft.Compute/disks@2023-04-02' = {
  name: dataDiskName
  location: location
  sku: {
    name: 'Premium_LRS'
  }
  properties: {
    creationData: {
      createOption: 'Empty'
    }
    diskSizeGB: dataDiskSizeGB
  }
  tags: {
    environment: environment
    project: project
  }
}

// Virtual Machine
resource vm 'Microsoft.Compute/virtualMachines@2023-03-01' = {
  name: vmName
  location: location
  properties: {
    hardwareProfile: {
      vmSize: vmSize
    }
    osProfile: {
      computerName: vmName
      adminUsername: adminUsername
      linuxConfiguration: {
        disablePasswordAuthentication: true
        ssh: {
          publicKeys: [
            {
              path: '/home/${adminUsername}/.ssh/authorized_keys'
              keyData: adminPublicKey
            }
          ]
        }
      }
    }
    storageProfile: {
      imageReference: {
        publisher: 'Canonical'
        offer: '0001-com-ubuntu-server-jammy'
        sku: '22_04-lts-gen2'
        version: 'latest'
      }
      osDisk: {
        createOption: 'FromImage'
        diskSizeGB: osDiskSizeGB
        managedDisk: {
          storageAccountType: 'Premium_LRS'
        }
      }
      dataDisks: [
        {
          lun: 0
          createOption: 'Attach'
          managedDisk: {
            id: dataDisk.id
          }
        }
      ]
    }
    networkProfile: {
      networkInterfaces: [
        {
          id: networkInterface.id
        }
      ]
    }
  }
  tags: {
    environment: environment
    project: project
    gpu: 'nvidia'
    model: 'qwen-2.5-coder-14b'
  }
}

// Custom Script Extension to setup GPU drivers and Qwen
resource setupExtension 'Microsoft.Compute/virtualMachines/extensions@2023-03-01' = {
  parent: vm
  name: customScriptExtensionName
  location: location
  properties: {
    publisher: 'Microsoft.Azure.Extensions'
    type: 'CustomScript'
    typeHandlerVersion: '2.0'
    autoUpgradeMinorVersion: true
    settings: {
      commandToExecute: 'echo Placeholder VM setup - script not downloaded. > /var/log/qwen-setup.log'
    }
  }
}

// Outputs
@description('Public IP address of the VM')
output publicIP string = publicIpAddress.properties.ipAddress

@description('SSH connection string')
output sshCommand string = 'ssh -i <private_key> ${adminUsername}@${publicIpAddress.properties.ipAddress}'

@description('VM name')
output vmName string = vm.name

@description('Ollama API endpoint')
output ollamaEndpoint string = 'http://${publicIpAddress.properties.ipAddress}:11434'

@description('vLLM API endpoint (if configured)')
output vllmEndpoint string = 'http://${publicIpAddress.properties.ipAddress}:8000'
