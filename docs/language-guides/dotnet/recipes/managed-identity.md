---
content_sources:

  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/dotnet-isolated-process-guide
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
  diagrams:
    - id: managed-identity
      type: flowchart
      source: self-generated
      justification: Flow view of managed identity, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/dotnet-isolated-process-guide
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
    - id: rbac-structure
      type: flowchart
      source: self-generated
      justification: Flow view of rbac structure, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/dotnet-isolated-process-guide
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
        - https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments
        - https://learn.microsoft.com/en-us/azure/role-based-access-control/troubleshooting
---
# Managed Identity

Use system-assigned managed identity for passwordless access to Azure resources from functions.

<!-- diagram-id: managed-identity -->
```mermaid
flowchart TD
    accTitle: Generic function service access
    accDescr: A trigger invokes a function that uses a binding or SDK to access an Azure service. This conceptual view does not depict managed-identity token acquisition or guarantee authorization success.
    A[Trigger] --> B[Function]
    B --> C[Binding or SDK]
    C --> D[Azure service]
```

## How RBAC Connects Identity to Resources

A managed identity alone does not grant access. Azure RBAC binds three elements into a **role assignment**:

<!-- diagram-id: rbac-structure -->
```mermaid
flowchart TD
    accTitle: Azure RBAC role assignment components
    accDescr: A principal, role definition and scope define a GUID-named role assignment. Access Granted summarizes assigned permissions, not immediate successful service access or completed permission propagation.
    P[Principal<br/>Who] --> RA[Role Assignment<br/>Unique GUID per binding]
    RD[Role Definition<br/>What] --> RA
    S[Scope<br/>Where] --> RA
    RA --> ACCESS[Access Granted]

    style RA fill:#f5c542,stroke:#333,color:#000
```

| Element | Question it answers | Example |
|---|---|---|
| **Principal** | Who needs access? | Function app's managed identity |
| **Role Definition** | What permission? | `Storage Blob Data Owner`, `Key Vault Secrets User` |
| **Scope** | On which resource? | A specific Storage account, Key Vault, or resource group |
| **Role Assignment** | The binding itself | Unique GUID — one per (principal + role + scope) combination |

**Reading key:** Principal = managed identity or service principal; Role Definition =
Storage Blob Data Owner, Key Vault Secrets User, or another role; Scope = subscription,
resource group, or resource. The three incoming arrows identify assignment components,
not network requests. “Access Granted” summarizes assigned permissions: applicable
conditions and permission propagation still matter; it does not promise immediate
successful data access. Managed-identity group or role membership changes can take
several hours to take effect; this is not a fixed wait for every direct role assignment.

Azure RBAC enforces a uniqueness constraint: only one role assignment can exist for the same `(principal, role definition, scope)` triple. Attempting to create a duplicate with a different assignment GUID results in a `RoleAssignmentExists` conflict.

## Topic/Command Groups

### Enable identity
```bash
az functionapp identity assign   --name "$APP_NAME"   --resource-group "$RG"
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp identity assign` |
| Key flags | `--name`, `--resource-group` |
| Variables | `$APP_NAME`, `$RG` |
| Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


### Access Storage SDK with DefaultAzureCredential
```csharp
var credential = new DefaultAzureCredential();
var blobService = new BlobServiceClient(new Uri($"https://{storageName}.blob.core.windows.net"), credential);
```

## See Also
- [Recipes Index](index.md)
- [.NET Language Guide](../index.md)
- [Troubleshooting](../troubleshooting.md)

## Sources
- [Azure Functions .NET isolated worker guide](https://learn.microsoft.com/en-us/azure/azure-functions/dotnet-isolated-process-guide)
- [Azure Functions triggers and bindings](https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings)
- [Understand Azure role assignments](https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments)
- [Troubleshoot Azure RBAC](https://learn.microsoft.com/en-us/azure/role-based-access-control/troubleshooting)
