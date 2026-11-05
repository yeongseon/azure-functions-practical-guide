---
content_sources:

  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-identity-based-connections-tutorial
  diagrams:
    - id: architecture
      type: flowchart
      source: self-generated
      justification: Flow view of architecture, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-identity-based-connections-tutorial
        - https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity
        - https://learn.microsoft.com/en-us/azure/azure-functions/manage-connections
    - id: rbac-structure
      type: flowchart
      source: self-generated
      justification: Flow view of rbac structure, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-identity-based-connections-tutorial
        - https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments
---
# Managed Identity

Managed Identity lets your Azure Functions app authenticate to other Azure services without storing credentials in code or configuration. This recipe covers enabling Managed Identity, assigning roles, and using `DefaultAzureCredential` for a seamless local-to-cloud development experience.

## Architecture

<!-- diagram-id: architecture -->
```mermaid
flowchart TD
    accTitle: Configured app identity and resource relationships
    accDescr: The function app has a configured managed identity represented in Entra ID and separate application data paths to Blob, Queue, Cosmos DB and Key Vault. Dotted links denote identity and resource-permission associations, not data transit or automatic connections.
    FA[Function App] -.-> MI[Managed Identity]
    MI -.-> ENTRA[Microsoft Entra ID]
    FA --> BLOB[Blob Storage]
    FA --> QUEUE[Queue Storage]
    FA --> COSMOS[Cosmos DB]
    FA --> KV[Key Vault]
    MI -.-> BLOB
    MI -.-> QUEUE
    MI -.-> COSMOS
    MI -.-> KV
    %% Layout-only links tier the existing resources; they add no service calls or authorization steps.
    ENTRA ~~~ BLOB
    BLOB ~~~ QUEUE
    QUEUE ~~~ COSMOS
    COSMOS ~~~ KV
```

**Reading key:** Solid arrows are illustrative app-to-service data access; dotted arrows associate the configured app identity with Entra ID and target permissions, not data routed through an identity. [Token retrieval uses the app's managed-identity endpoint](https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity#connect-to-azure-services-in-app-code). Configure the SDK credential or [supported binding's identity-based connection](https://learn.microsoft.com/en-us/azure/azure-functions/manage-connections), plus target permissions; enabling identity alone establishes neither connection nor access. Blob/Queue and Key Vault can use Azure RBAC (Key Vault also supports access policies); Cosmos DB for NoSQL uses its own data-plane RBAC, not Azure RBAC data roles.

## How RBAC Connects Identity to Resources

A managed identity alone does not grant access. Azure RBAC binds three elements into a **role assignment**:

<!-- diagram-id: rbac-structure -->
```mermaid
flowchart TD
    accTitle: Azure RBAC role assignment components
    accDescr: Principal, role definition and scope define a role assignment and the permissions it grants. These are configuration relationships, not a runtime data path; access granted means the assigned permissions at scope, not guaranteed success of a request.
    P[Principal<br/>Who: Managed Identity<br/>or Service Principal] --> RA[Role Assignment<br/>Unique GUID per binding]
    RD[Role Definition<br/>What: Storage Blob Data Owner,<br/>Key Vault Secrets User, etc.] --> RA
    S[Scope<br/>Where: Subscription,<br/>Resource Group, or Resource] --> RA
    RA --> ACCESS[Access Granted]

    %% Layout-only links tier the three inputs; they add no permission dependency or data hop.
    P ~~~ RD
    RD ~~~ S
    style RA fill:#f5c542,stroke:#333,color:#000
```

**Reading key:** The three inputs describe a [role assignment](https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments), which authorizes a principal's role permissions at a scope; it is not a data-transit hop. “Access Granted” does not guarantee network reachability or that the role permits a particular operation, and applicable conditions still matter.

| Element | Question it answers | Example |
|---|---|---|
| **Principal** | Who needs access? | Function app's managed identity |
| **Role Definition** | What permission? | `Storage Blob Data Owner`, `Key Vault Secrets User` |
| **Scope** | On which resource? | A specific Storage account, Key Vault, or resource group |
| **Role Assignment** | The binding itself | Unique GUID — one per (principal + role + scope) combination |

Azure RBAC enforces a uniqueness constraint: only one role assignment can exist for the same `(principal, role definition, scope)` triple. Attempting to create a duplicate with a different assignment GUID results in a `RoleAssignmentExists` conflict.

## What Is Managed Identity?

A Managed Identity is an Azure AD identity automatically managed by Azure. Your function app can use this identity to obtain tokens for Azure services (Storage, Cosmos DB, Key Vault, SQL, etc.) without managing secrets, certificates, or connection strings.

There are two types:

| Type | Lifecycle | Use Case |
|------|-----------|----------|
| **System-assigned** | Tied to the function app (deleted when app is deleted) | Single app, simple scenarios |
| **User-assigned** | Independent resource (survives app deletion) | Shared across multiple apps, blue-green deployments |

This guide uses system-assigned identity for simplicity.

## Step 1: Enable System-Assigned Identity

```bash
az functionapp identity assign \
  --name your-func \
  --resource-group your-rg
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp identity assign` |
| Key flags | `--name`, `--resource-group` |
| Variables | None |
| Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


Output:

```json
{
  "principalId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "<tenant-id>",
  "type": "SystemAssigned"
}
```

Save the `principalId` — you need it for role assignments.

## Step 2: Assign Roles

Grant the identity access to specific Azure resources using role-based access control (RBAC). Only assign the minimum permissions needed.

### Common Role Assignments

| Resource | Role | Permission |
|----------|------|------------|
| Storage Account (blobs) | `Storage Blob Data Contributor` | Read, write, delete blobs |
| Storage Account (queues) | `Storage Queue Data Contributor` | Read, write, delete queue messages |
| Storage Account (tables) | `Storage Table Data Contributor` | Read, write, delete table entities |
| Key Vault | `Key Vault Secrets User` | Read secrets |
| Cosmos DB | `Cosmos DB Built-in Data Contributor` | Read, write documents |
| Service Bus | `Azure Service Bus Data Sender` | Send messages |

```bash
# Storage Blob Data Contributor
az role assignment create \
  --assignee "<object-id>" \
  --role "Storage Blob Data Contributor" \
  --scope "/subscriptions/<subscription-id>/resourceGroups/your-rg/providers/Microsoft.Storage/storageAccounts/yourstorage"

# Key Vault Secrets User
az role assignment create \
  --assignee "<object-id>" \
  --role "Key Vault Secrets User" \
  --scope "/subscriptions/<subscription-id>/resourceGroups/your-rg/providers/Microsoft.KeyVault/vaults/your-kv"
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az role assignment create` |
| Key flags | `--assignee`, `--role`, `--scope` |
| Variables | None |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


> **Tip:** Scope role assignments to the specific resource (storage account, Key Vault) rather than the resource group or subscription. This follows the principle of least privilege.

## Step 3: Replace Connection Strings with Identity-Based Connections

For Azure Functions bindings, replace the traditional connection string with identity-based settings. The runtime detects the `__accountName` or `__serviceUri` suffix pattern and uses Managed Identity automatically.

### AzureWebJobsStorage (Internal Host Storage)

```bash
# Remove the connection string
az functionapp config appsettings delete \
  --name your-func \
  --resource-group your-rg \
  --setting-names AzureWebJobsStorage

# Set identity-based connection
az functionapp config appsettings set \
  --name your-func \
  --resource-group your-rg \
  --settings "AzureWebJobsStorage__accountName=yourstorage"
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp config appsettings delete`, `az functionapp config appsettings set` |
| Key flags | `--name`, `--resource-group`, `--setting-names`, `--settings` |
| Variables | None |
| Expected result | Azure CLI completes the removal request; verify the target no longer appears in follow-up `show` or `list` output. |


### Custom Binding Connections

For bindings that use a custom connection name (e.g., `CosmosDBConnection`), use the `__accountEndpoint` suffix:

```bash
az functionapp config appsettings set \
  --name your-func \
  --resource-group your-rg \
  --settings "CosmosDBConnection__accountEndpoint=https://your-cosmos-db.documents.azure.com:443/"
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp config appsettings set` |
| Key flags | `--name`, `--resource-group`, `--settings` |
| Variables | None |
| Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


## Step 4: Use DefaultAzureCredential in Code

The `DefaultAzureCredential` class from the Azure Identity library provides a unified authentication experience. It tries multiple credential sources in order:

1. **Environment variables** — service principal credentials (CI/CD)
2. **Managed Identity** — when running in Azure
3. **Azure CLI** — `az login` credentials (local development)
4. **VS Code** — Azure extension credentials

This means the same code works locally (using your `az login` session) and in Azure (using Managed Identity).

Add to `requirements.txt`:

```
azure-identity>=1.15.0
azure-storage-blob>=12.19.0
```

### Example: Access Blob Storage with Managed Identity

**Runnable example:** save the entire block as `function_app.py` in a Python v2 project with `azure-functions` and the SDK dependencies above. It includes app/blueprint registration. Set `STORAGE_ACCOUNT_NAME`, sign in locally with `az login`, and grant your developer identity Blob data access to an existing `uploads` container. Use `host.json` with `extensions.http.routePrefix` set to `"api"` and run `func start`; request `GET /api/blobs`. In Azure, configure the app identity and its RBAC separately. Local unit checks below substitute the credential/client constructors; they do not authenticate or prove RBAC.

```python
import azure.functions as func
import json
import os
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

app = func.FunctionApp()
bp = func.Blueprint()

# Initialize once at module level
_blob_client = None

def get_blob_service_client() -> BlobServiceClient:
    global _blob_client
    if _blob_client is None:
        account_name = os.environ.get("STORAGE_ACCOUNT_NAME", "yourstorage")
        credential = DefaultAzureCredential()
        _blob_client = BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=credential
        )
    return _blob_client


@bp.route(route="blobs", methods=["GET"])
def list_blobs(req: func.HttpRequest) -> func.HttpResponse:
    """List blobs using Managed Identity — no connection string needed."""
    client = get_blob_service_client()
    container = client.get_container_client("uploads")

    blobs = [{"name": b.name, "size": b.size} for b in container.list_blobs()]

    return func.HttpResponse(
        json.dumps({"blobs": blobs}),
        mimetype="application/json",
        status_code=200
    )


app.register_blueprint(bp)
```

**Local verification:** `tests/test_python_doc_examples.py` checks undefined names and real SDK registration, then verifies account URL construction, credential forwarding, client reuse across two invocations, container selection, and response serialization using SDK-constrained doubles. No storage requests or token acquisition occur.

### Example: Access Key Vault with Managed Identity

**Intentionally abbreviated helper fragment:** not a standalone Functions app. It requires `import os` from the preceding example, `azure-keyvault-secrets` installed, `KEY_VAULT_URL`, and an authorized identity. It is not part of the focused executable checks.

```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def get_secret(secret_name: str) -> str:
    vault_url = os.environ.get("KEY_VAULT_URL", "https://your-kv.vault.azure.net/")
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    return client.get_secret(secret_name).value
```

## Local Development with Managed Identity

`DefaultAzureCredential` works locally by using your Azure CLI login:

```bash
# Login to Azure CLI
az login

# Set your subscription
az account set --subscription "<subscription-id>"

# Your code now uses your az login credentials automatically
func host start
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az login`, `az account set` |
| Key flags | `--subscription` |
| Variables | None |
| Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


Ensure your personal Azure AD account has the same role assignments as the Managed Identity (e.g., `Storage Blob Data Contributor`).

## Bicep: Managed Identity in Infrastructure

Enable Managed Identity and assign roles in your Bicep template:

```bicep
resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: functionAppName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  // ...
}

resource storageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, functionApp.id, 'Storage Blob Data Contributor')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'ba92f5b4-2d11-453d-a403-e96b0029c9fe'  // Storage Blob Data Contributor
    )
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}
```

## See Also
- [Key Vault Integration Recipe](key-vault.md)
- [Platform Security Design](../../../platform/security.md) — authentication architecture, Easy Auth, key management design
- [Security Operations](../../../operations/security.md) — key rotation, RBAC audit, CORS, TLS enforcement
- [Blob Storage Recipe](blob-storage.md)

## Sources
- [Managed Identity Tutorial (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-identity-based-connections-tutorial)
