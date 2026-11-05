---
content_sources:

  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-identity-based-connections-tutorial
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/java/api/overview/azure/identity-readme
  diagrams:
    - id: architecture
      type: flowchart
      source: self-generated
      justification: Flow view of architecture, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-identity-based-connections-tutorial
        - https://learn.microsoft.com/en-us/java/api/overview/azure/identity-readme
        - https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity
    - id: rbac-structure
      type: flowchart
      source: self-generated
      justification: Flow view of rbac structure, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-identity-based-connections-tutorial
        - https://learn.microsoft.com/en-us/java/api/overview/azure/identity-readme
        - https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments
        - https://learn.microsoft.com/en-us/azure/role-based-access-control/troubleshooting
---
# Managed Identity

This recipe configures a system-assigned managed identity and uses `DefaultAzureCredential` from Java to call downstream Azure services without secrets.

## Architecture

<!-- diagram-id: architecture -->
```mermaid
flowchart TD
    accTitle: Java managed identity and service access
    accDescr: The function app's system-assigned identity is associated with Microsoft Entra token issuance, while its Java SDK uses DefaultAzureCredential to access Storage, Key Vault or Cosmos DB. This is a logical relationship map, not a direct app-to-Entra network trace or a guarantee of credential selection and authorization.
    FUNC[Function App] --> MSI[System-assigned<br/>managed identity]
    MSI --> ENTRA[Microsoft Entra<br/>token endpoint]
    FUNC --> SDK[Azure SDK with<br/>DefaultAzureCredential]
    SDK --> SERVICE[("Storage / Key Vault /<br/>Cosmos DB")]
    %% Layout-only link tiers the branches; it adds no token or service request.
    ENTRA ~~~ SDK
```

**Reading key:** The identity/Entra branch summarizes identity association and token
issuance; in App Service-hosted Functions, Azure Identity obtains managed-identity
tokens through the platform's internal identity endpoint. `DefaultAzureCredential`
can use managed identity when configured and selected by its credential chain; it
does not unconditionally select that identity in Azure. The SDK/service branch
still requires the target service's authorization configuration.

## How RBAC Connects Identity to Resources

A managed identity alone does not grant access. Azure RBAC binds three elements into a **role assignment**:

<!-- diagram-id: rbac-structure -->
```mermaid
flowchart TD
    accTitle: Azure RBAC role assignment components
    accDescr: Principal, role definition and scope define a GUID-named role assignment. Access Granted summarizes assigned permissions, not immediate successful service access or completed permission propagation.
    P[Principal<br/>Who] --> RA[Role Assignment<br/>Unique GUID per binding]
    RD[Role Definition<br/>What] --> RA
    S[Scope<br/>Where] --> RA
    RA --> ACCESS[Access Granted]

    style RA fill:#f5c542,stroke:#333,color:#000
```

**Reading key:** Principal = Who: Managed Identity or Service Principal; Role Definition =
What: Storage Blob Data Owner, Key Vault Secrets User, etc.; Scope = Where:
Subscription, Resource Group, or Resource. Incoming arrows identify assignment
components, not requests. “Access Granted” denotes assigned permissions, not immediate
successful data access: applicable conditions and propagation still matter.
Changes to a managed identity's group or role membership can take several hours;
this is not a fixed wait for every direct role assignment.

| Element | Question it answers | Example |
|---|---|---|
| **Principal** | Who needs access? | Function app's managed identity |
| **Role Definition** | What permission? | `Storage Blob Data Owner`, `Key Vault Secrets User` |
| **Scope** | On which resource? | A specific Storage account, Key Vault, or resource group |
| **Role Assignment** | The binding itself | Unique GUID — one per (principal + role + scope) combination |

Azure RBAC enforces a uniqueness constraint: only one role assignment can exist for the same `(principal, role definition, scope)` triple. Attempting to create a duplicate with a different assignment GUID results in a `RoleAssignmentExists` conflict.

## Prerequisites

Enable identity and capture principal ID:

```bash
az functionapp identity assign --name $APP_NAME --resource-group $RG

PRINCIPAL_ID=$(az functionapp identity show --name $APP_NAME --resource-group $RG --query principalId --output tsv)
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp identity assign`, `az functionapp identity show` |
| Key flags | `--name`, `--resource-group`, `--query`, `--output` |
| Variables | `$APP_NAME`, `$RG` |
| Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


Grant RBAC access to a storage account:

```bash
STORAGE_SCOPE=$(az storage account show --name $STORAGE_NAME --resource-group $RG --query id --output tsv)

az role assignment create \
  --assignee-object-id $PRINCIPAL_ID \
  --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Reader" \
  --scope $STORAGE_SCOPE
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az storage account show`, `az role assignment create` |
| Key flags | `--name`, `--resource-group`, `--query`, `--output`, `--assignee-object-id`, `--assignee-principal-type`, `--role`, `--scope` |
| Variables | `$STORAGE_NAME`, `$RG`, `$PRINCIPAL_ID`, `$STORAGE_SCOPE` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


Maven dependencies:

```xml
<dependencies>
    <dependency>
        <groupId>com.azure</groupId>
        <artifactId>azure-identity</artifactId>
        <version>1.14.2</version>
    </dependency>
    <dependency>
        <groupId>com.azure</groupId>
        <artifactId>azure-storage-blob</artifactId>
        <version>12.27.0</version>
    </dependency>
</dependencies>
```

## Java implementation

```java
package com.contoso.functions;

import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.BlobContainerClientBuilder;
import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;

import java.util.Optional;

public class ManagedIdentityFunctions {

    @FunctionName("listBlobsWithIdentity")
    public HttpResponseMessage listBlobsWithIdentity(
        @HttpTrigger(
            name = "request",
            methods = {HttpMethod.GET},
            authLevel = AuthorizationLevel.FUNCTION,
            route = "identity/blobs"
        ) HttpRequestMessage<Optional<String>> request
    ) {
        String endpoint = System.getenv("STORAGE_BLOB_ENDPOINT");
        String container = System.getenv("STORAGE_CONTAINER_NAME");

        BlobContainerClient containerClient = new BlobContainerClientBuilder()
            .endpoint(endpoint)
            .containerName(container)
            .credential(new DefaultAzureCredentialBuilder().build())
            .buildClient();

        long count = containerClient.listBlobs().stream().count();
        return request.createResponseBuilder(HttpStatus.OK)
            .body("Blob count: " + count)
            .build();
    }
}
```

## Implementation notes

- `DefaultAzureCredential` uses local developer identity during development and managed identity in Azure.
- RBAC propagation can take a few minutes after assignment.
- Scope role assignments narrowly to least privilege.
- Prefer identity-based connection settings for supported bindings.

## See Also

- [Key Vault Integration](key-vault.md)
- [Cosmos DB Integration](cosmosdb.md)
- [Blob Storage Integration](blob-storage.md)

## Sources

- [Use managed identities in Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-identity-based-connections-tutorial)
- [Azure Identity client library for Java (Microsoft Learn)](https://learn.microsoft.com/en-us/java/api/overview/azure/identity-readme)
- [Managed identities in App Service and Azure Functions](https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity)
- [Understand Azure role assignments](https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments)
- [Troubleshoot Azure RBAC](https://learn.microsoft.com/en-us/azure/role-based-access-control/troubleshooting)
