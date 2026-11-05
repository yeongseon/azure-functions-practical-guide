---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-how-to
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-deployment-technologies
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings
  diagrams:
    - id: 1-summary
      type: flowchart
      source: self-generated
      justification: Flow view of summary, synthesized from Microsoft Learn documentation cited on this page.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
        - https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-how-to
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-deployment-technologies
        - https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings
        - https://learn.microsoft.com/en-us/azure/storage/common/shared-key-authorization-prevent
        - https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security-set-default-access
content_validation:
  status: verified
  last_reviewed: 2026-04-12
  reviewer: agent
  core_claims:
    - claim: "Flex Consumption Deployment Gotchas 관련 핵심 진단 절차와 운영 판단 기준"
      source: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
      verified: true
---

# Flex Consumption Deployment Gotchas

## Portal Walkthrough

Key portal blades for Flex Consumption deployment investigation. Captures from a Consumption (Y1) Function App with PII masked.

![Deployment Center blade](../../assets/operations/deployment/01-deployment-center.png)

![Environment variables blade](../../assets/operations/configuration/01-environment-variables.png)

![Log stream for deployment traces](../../assets/operations/monitoring/02-log-stream.png)

## 1. Summary

Flex Consumption (FC1) introduces a fundamentally different provisioning and deployment model compared to Consumption (Y1), Premium (EP), and Dedicated plans. Operators who carry over assumptions from those plans routinely encounter provisioning failures, deployment auth errors, and incomplete network lockdown — even when following documentation that appears correct for other plan types.

This playbook covers five specific issues discovered during hands-on deployment validation (2026-04-09, Azure CLI 2.83.0). Each maps to a competing hypothesis and includes evidence collection, validation, and mitigation steps.

<!-- diagram-id: 1-summary -->
```mermaid
flowchart TD
    accTitle: Flex Consumption deployment diagnostic decision flow
    accDescr: Illustrative triage, not a confirmed diagnosis. From failed or degraded deployment, check plan creation, publish storage authentication, public storage access, host 503 or Error state, then unexpected environment value. Each Yes branch selects H1, H2, H3, H4a or H4b respectively and its proposed mitigation; each No continues to the next check, ending at the general deployment playbook. Validate each candidate against the evidence and disproof sections below; the adjacent key retains command and setting details.
    A(["Symptom: Flex Consumption<br/>deployment failed<br/>or degraded"]) --> B{"Plan creation<br/>failed?"}
    B -->|Yes| C("H1 candidate:<br/>FC1 plan command")
    C --> C1(["Use Flex app<br/>creation command"])
    B -->|No| D{"Publish failed with<br/>storage auth error?"}
    %% Layout-only links serialize branches; they add no diagnostic steps or arrows.
    C1 ~~~ D
    D -->|Yes| E("H2 candidate:<br/>Shared Key disabled")
    E --> E1(["Set deployment storage<br/>to user-assigned identity"])
    D -->|No| F{"Storage accessible<br/>from public internet?"}
    E1 ~~~ F
    F -->|Yes| G("H3 candidate:<br/>Default Deny not set")
    G --> G1(["Set storage default<br/>network rule to Deny"])
    F -->|No| H{"Host returns 503<br/>or Error state?"}
    G1 ~~~ H
    H -->|Yes| I("H4a candidate:<br/>Missing trigger<br/>connection setting")
    I --> I1(["Add missing trigger<br/>binding app setting"])
    H -->|No| J{"Environment value<br/>unexpected?"}
    I1 ~~~ J
    J -->|Yes| K("H4b candidate:<br/>ENVIRONMENT not<br/>explicitly set")
    K --> K1(["Set ENVIRONMENT<br/>app setting explicitly"])
    J -->|No| L["Check general<br/>deployment playbook"]
    K1 ~~~ L
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class A,B,C,C1,D,E,E1,F,G,G1,H,I,I1,J,K,K1,L baseNeutral;
    linkStyle default stroke-width:2px;
```

**Reading key:** Diamonds are Yes/No checks, rounded boxes are candidate hypotheses,
stadiums are the symptom or proposed mitigations, and the rectangle is the fallback.
The arrows select what to investigate, not a proven cause; use Section 6 to validate
or disprove each candidate before applying its mitigation.

| Key | Candidate detail retained from the flow | Proposed mitigation |
|---|---|---|
| H1 | Attempted `az functionapp plan create --sku FC1`. | Use `az functionapp create --flexconsumption-location`; see [Flex app creation](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-how-to#create-a-flex-consumption-app). |
| H2 | `allowSharedKeyAccess` is `false`; check deployment authentication too, not the flag alone. | Configure `az functionapp deployment config set --deployment-storage-auth-type UserAssignedIdentity` with the identity resource ID and required storage permissions; see [deployment settings](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-how-to#configure-deployment-settings) and [Shared Key rejection](https://learn.microsoft.com/en-us/azure/storage/common/shared-key-authorization-prevent). |
| H3 | `--default-action Deny` is not set. | After ensuring required access, use `az storage account update --default-action Deny` to restrict the public endpoint to allowed sources, not to guarantee private-endpoint-only access; see [default network access](https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security-set-default-access). |
| H4a | Check for a missing trigger connection setting; 503/Error alone does not confirm it. | Add the missing app setting for the trigger binding; retain the supporting/disproving checks in Section 6. |
| H4b | Check whether the application's `ENVIRONMENT` value was explicitly set. | Set the `ENVIRONMENT` app setting explicitly; this application-specific name is distinct from the runtime's [`AZURE_FUNCTIONS_ENVIRONMENT`](https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings#azure_functions_environment). |


### Incident framing

- Common symptom: provisioning command fails, publish returns auth error, or app deploys but host enters error state.
- Flex Consumption concepts in scope: `--flexconsumption-location`, deployment storage auth type, managed identity for storage, private endpoint network lockdown, host listener initialization.
- Use objective evidence first: CLI error messages, app settings snapshot, host state, and storage network rules.

### Variables

```bash
RG="rg-flexdemo"
APP_NAME="flexdemo-func"
STORAGE_NAME="flexdemostorage"
MI_NAME="flexdemo-identity"
SUBSCRIPTION_ID="<subscription-id>"
```

## 2. Common Misreadings

1. **"FC1 is just another SKU like Y1 or EP1"**
    - Flex Consumption does not use `az functionapp plan create`. The plan is created implicitly via `az functionapp create --flexconsumption-location`.
    - Attempting `--sku FC1` will fail with an invalid SKU error.

2. **"Private Endpoints mean storage is private"**
    - Creating private endpoints and DNS zones does NOT block public access. You must explicitly set `--default-action Deny` on the storage account.
    - Without this, data-plane requests from the public internet still succeed.

3. **"Managed Identity is configured, so deployment will use it"**
    - Assigning a managed identity to the function app does NOT change deployment storage authentication. By default, deployment storage uses connection string auth.
    - If `allowSharedKeyAccess: false`, publish fails unless you explicitly switch deployment storage to identity-based auth.

4. **"Azure sets ENVIRONMENT=production automatically"**
    - Azure does not set any `ENVIRONMENT` variable. Python code using `os.environ.get("ENVIRONMENT", "development")` will return `"development"` unless you set it explicitly.

5. **"Only the trigger's own function is affected by a missing connection setting"**
    - A missing connection string referenced in any trigger binding causes the entire Function host to enter Error state. ALL functions become inaccessible (HTTP 503), not just the one with the bad binding.

## 3. Competing Hypotheses

### H1: Provisioning model mismatch

- Operator uses the standard `az functionapp plan create --sku FC1` pattern.
- FC1 is not a recognized SKU value for App Service Plans.
- Flex Consumption requires `az functionapp create --flexconsumption-location` — no separate plan creation step.

### H2: Identity/auth configuration gap

- Storage account has `allowSharedKeyAccess: false` for security.
- Deployment storage defaults to connection string authentication.
- `func azure functionapp publish` fails with `InaccessibleStorageException`.
- Fix requires explicitly configuring deployment storage to use managed identity.

### H3: Network lockdown incomplete

- Private endpoints and DNS zones are correctly configured.
- But `--default-action` on the storage account is still `Allow` (default).
- Storage accepts data-plane requests from the public internet.
- PE setup creates a private path but does not remove the public path.

### H4: Missing app settings break host

- **H4a**: A trigger binding references a connection setting (e.g., `EventHubConnection`) that does not exist in app settings. The host fails to initialize trigger listeners and enters Error state (HTTP 503 for all endpoints).
- **H4b**: Application code reads `ENVIRONMENT` from environment variables with a `"development"` default. Azure does not set this variable, so it always returns `"development"`.

## 4. What to Check First

### First 5-minute checklist

1. Identify the exact error message from the failing CLI command or publish output.
2. Check whether the function app exists and its state:
    ```bash
    az functionapp show \
        --name $APP_NAME \
        --resource-group $RG \
        --query "{name:name, state:properties.state, sku:properties.sku}" \
        --output json
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az functionapp show` |
    | Key flags | `--name`, `--resource-group`, `--query`, `--output` |
    | Variables | `$APP_NAME`, `$RG` |
    | Expected result | Azure CLI returns the requested resource data; verify names, IDs, status fields, or metric values match the scenario. |

3. Check storage account security settings:
    ```bash
    az storage account show \
        --name $STORAGE_NAME \
        --resource-group $RG \
        --query "{allowSharedKeyAccess:allowSharedKeyAccess, defaultAction:networkRuleSet.defaultAction}" \
        --output json
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az storage account show` |
    | Key flags | `--name`, `--resource-group`, `--query`, `--output` |
    | Variables | `$STORAGE_NAME`, `$RG` |
    | Expected result | Azure CLI returns the requested resource data; verify names, IDs, status fields, or metric values match the scenario. |

4. Check deployment storage auth type:
    ```bash
    az functionapp deployment config show \
        --name $APP_NAME \
        --resource-group $RG \
        --query "deploymentStorage" \
        --output json
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az functionapp deployment config show` |
    | Key flags | `--name`, `--resource-group`, `--query`, `--output` |
    | Variables | `$APP_NAME`, `$RG` |
    | Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |

5. Check for missing app settings referenced by trigger bindings.

## 5. Evidence to Collect

### Sample Log Patterns

```text
# H1: Invalid SKU error
ERROR: 'FC1' is not a valid value for '--sku'. Allowed values: B1, B2, B3, D1, EP1, EP2, EP3, F1, FREE, I1, ...

# H2: Deployment storage auth failure
InaccessibleStorageException: Failed to access storage account for deployment: Key based authentication is not permitted on this storage account.

# H4a: Missing trigger connection setting — host error state
2026-04-09T05:15:02.214Z error  Microsoft.Azure.WebJobs.EventHubs: Value cannot be null. (Parameter 'connectionString')
2026-04-09T05:15:02.215Z error  A host error has occurred during startup operation '<object-id>'
2026-04-09T05:15:08.122Z info   Host is in error state.
```

### KQL Queries with Example Output

#### Query 1: Host startup errors after deployment

```kusto
let appName = "flexdemo-func";
traces
| where timestamp > ago(1h)
| where cloud_RoleName =~ appName
| where severityLevel >= 3
| where message has_any ("host error", "Error state", "Value cannot be null", "InaccessibleStorage")
| project timestamp, severityLevel, message
| order by timestamp desc
```

Example output:

| timestamp | severityLevel | message |
|---|---:|---|
| 2026-04-09T05:15:08Z | 3 | Host is in error state. |
| 2026-04-09T05:15:02Z | 3 | A host error has occurred during startup operation '<object-id\>' |
| 2026-04-09T05:15:02Z | 3 | Microsoft.Azure.WebJobs.EventHubs: Value cannot be null. (Parameter 'connectionString') |

#### Query 2: Function invocation failures after deployment

```kusto
let appName = "flexdemo-func";
requests
| where timestamp > ago(1h)
| where cloud_RoleName =~ appName
| where success == false
| summarize
    Count = count(),
    P95Ms = percentile(duration, 95)
  by resultCode
| order by Count desc
```

Example output:

| resultCode | Count | P95Ms |
|---|---:|---:|
| 503 | 42 | 102.30 |

!!! tip "How to Read This"
    A flood of `503` responses immediately after deployment strongly indicates a host-level failure. Check startup traces for the root cause — typically a missing connection setting or storage auth error.

### CLI Investigation Commands

#### Storage network rules

```bash
az storage account show \
    --name $STORAGE_NAME \
    --resource-group $RG \
    --query "{defaultAction:networkRuleSet.defaultAction, bypass:networkRuleSet.bypass, privateEndpointConnections:privateEndpointConnections[].{name:name,state:privateLinkServiceConnectionState.status}}" \
    --output json
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az storage account show` |
| Key flags | `--name`, `--resource-group`, `--query`, `--output` |
| Variables | `$STORAGE_NAME`, `$RG` |
| Expected result | Azure CLI returns the requested resource data; verify names, IDs, status fields, or metric values match the scenario. |


Example output:

```json
{
  "bypass": "AzureServices",
  "defaultAction": "Allow",
  "privateEndpointConnections": [
    { "name": "pe-st-blob", "state": "Approved" },
    { "name": "pe-st-queue", "state": "Approved" },
    { "name": "pe-st-table", "state": "Approved" },
    { "name": "pe-st-file", "state": "Approved" }
  ]
}
```

!!! tip "How to Read This"
    `defaultAction: Allow` with approved private endpoints means the storage account accepts traffic from BOTH private endpoints AND the public internet. Set `--default-action Deny` to force traffic through private endpoints only.

#### Deployment storage configuration

```bash
az functionapp deployment config show \
    --name $APP_NAME \
    --resource-group $RG \
    --query "deploymentStorage" \
    --output json
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp deployment config show` |
| Key flags | `--name`, `--resource-group`, `--query`, `--output` |
| Variables | `$APP_NAME`, `$RG` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


Example output:

```json
{
  "authentication": {
    "type": "userassignedidentity",
    "userAssignedIdentityResourceId": "/subscriptions/<subscription-id>/resourcegroups/rg-flexdemo/providers/Microsoft.ManagedIdentity/userAssignedIdentities/flexdemo-identity"
  },
  "type": "blobcontainer",
  "value": "https://flexdemostorage.blob.core.windows.net/app-package-flexdemofunc-<id>"
}
```

### Normal vs Abnormal Comparison

| Signal | Normal (Flex Consumption) | Abnormal |
|---|---|---|
| Plan creation | `az functionapp create --flexconsumption-location` succeeds | `az functionapp plan create --sku FC1` fails |
| Deployment storage auth | `type: userassignedidentity` when shared key is disabled | `type: storageaccountconnectionstring` with shared key disabled |
| Storage network rules | `defaultAction: Deny` with approved PEs | `defaultAction: Allow` — public access still open |
| Host state after publish | `state: Running`, functions indexed | `state: Error` or HTTP 503 on all endpoints |
| `ENVIRONMENT` app setting | Explicitly set to desired value | Missing — defaults to `"development"` in code |

## 6. Validation and Disproof by Hypothesis

### H1: Provisioning model mismatch

#### Signals that support

- CLI returns "FC1 is not a valid value for '--sku'"
- No function app or plan is created
- Operator was following Consumption/Premium documentation

#### Signals that weaken

- Function app already exists and is running
- `az functionapp show` returns `sku: FlexConsumption`

#### What to verify

```bash
# Check if function app exists
az functionapp show \
    --name $APP_NAME \
    --resource-group $RG \
    --query "{name:name, sku:properties.sku}" \
    --output json
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp show` |
| Key flags | `--name`, `--resource-group`, `--query`, `--output` |
| Variables | `$APP_NAME`, `$RG` |
| Expected result | Azure CLI returns the requested resource data; verify names, IDs, status fields, or metric values match the scenario. |


### H2: Identity/auth configuration gap

#### Signals that support

- `func azure functionapp publish` fails with `InaccessibleStorageException`
- Storage account has `allowSharedKeyAccess: false`
- Deployment config shows `type: storageaccountconnectionstring`

#### Signals that weaken

- Deployment config already shows `type: userassignedidentity`
- `allowSharedKeyAccess` is `true`
- Publish succeeds without error

#### What to verify

```bash
az storage account show \
    --name $STORAGE_NAME \
    --resource-group $RG \
    --query "allowSharedKeyAccess" \
    --output tsv

az functionapp deployment config show \
    --name $APP_NAME \
    --resource-group $RG \
    --query "deploymentStorage.authentication.type" \
    --output tsv
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az storage account show`, `az functionapp deployment config show` |
| Key flags | `--name`, `--resource-group`, `--query`, `--output` |
| Variables | `$STORAGE_NAME`, `$RG`, `$APP_NAME` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


!!! tip "How to Read This"
    If `allowSharedKeyAccess` is `false` and deployment auth type is `storageaccountconnectionstring`, this is the root cause. Switch to managed identity auth before publishing.

### H3: Network lockdown incomplete

#### Signals that support

- Private endpoints exist and are approved
- `defaultAction` is still `Allow`
- Storage is accessible from local machine despite PE setup

#### Signals that weaken

- `defaultAction` is `Deny`
- Storage requests from outside VNet are rejected

#### What to verify

```bash
az storage account show \
    --name $STORAGE_NAME \
    --resource-group $RG \
    --query "networkRuleSet.defaultAction" \
    --output tsv
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az storage account show` |
| Key flags | `--name`, `--resource-group`, `--query`, `--output` |
| Variables | `$STORAGE_NAME`, `$RG` |
| Expected result | Azure CLI returns the requested resource data; verify names, IDs, status fields, or metric values match the scenario. |


### H4: Missing app settings break host

#### Signals that support

- Host state is `Error` or all endpoints return 503
- Startup traces show "Value cannot be null" for a connection setting
- App code references a binding connection that has no matching app setting

#### Signals that weaken

- Host is `Running` and functions are indexed
- All connection settings referenced in bindings exist in app settings
- Error is limited to a single function, not host-wide

#### What to verify

KQL:

```kusto
let appName = "flexdemo-func";
traces
| where timestamp > ago(1h)
| where cloud_RoleName =~ appName
| where message has_any ("Value cannot be null", "connectionString", "listener", "Error state")
| project timestamp, severityLevel, message
| order by timestamp desc
```

CLI:

```bash
az functionapp config appsettings list \
    --name $APP_NAME \
    --resource-group $RG \
    --output table
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp config appsettings list` |
| Key flags | `--name`, `--resource-group`, `--output` |
| Variables | `$APP_NAME`, `$RG` |
| Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


## 7. Likely Root Cause Patterns

1. **Provisioning model confusion**
    - Operator applies Y1/EP1 pattern (`az functionapp plan create --sku FC1`) to Flex Consumption
    - Fix: use `az functionapp create --flexconsumption-location`

2. **Deployment storage auth mismatch**
    - Storage account locked down (`allowSharedKeyAccess: false`) but deployment storage still uses connection string
    - Fix: `az functionapp deployment config set --deployment-storage-auth-type UserAssignedIdentity`

3. **Private endpoint without public access lockdown**
    - PEs created and working, but storage still accepts public requests
    - Fix: `az storage account update --default-action Deny` (after PE + DNS + container creation)

4. **Missing trigger connection settings**
    - Any binding with a missing connection string crashes the entire host
    - Fix: add the required app setting (real value or placeholder if trigger is inactive)

5. **Implicit environment defaults**
    - Code assumes Azure sets `ENVIRONMENT` but it does not
    - Fix: set `ENVIRONMENT=production` explicitly in app settings

## 8. Immediate Mitigations

1. **FC1 SKU error**: Replace `az functionapp plan create --sku FC1` with `az functionapp create --flexconsumption-location "$LOCATION"`.

2. **Deployment storage auth error**: Run before publishing:
    ```bash
    az functionapp deployment config set \
        --name $APP_NAME \
        --resource-group $RG \
        --deployment-storage-auth-type UserAssignedIdentity \
        --deployment-storage-auth-value "$MI_ID"
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az functionapp deployment config set` |
    | Key flags | `--name`, `--resource-group`, `--deployment-storage-auth-type`, `--deployment-storage-auth-value` |
    | Variables | `$APP_NAME`, `$RG`, `$MI_ID` |
    | Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


3. **Storage public access**: Lock down after PE and DNS setup:
    ```bash
    az storage account update \
        --name $STORAGE_NAME \
        --resource-group $RG \
        --default-action Deny
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az storage account update` |
    | Key flags | `--name`, `--resource-group`, `--default-action` |
    | Variables | `$STORAGE_NAME`, `$RG` |
    | Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


4. **Missing connection setting**: Add the missing app setting:
    ```bash
    az functionapp config appsettings set \
        --name $APP_NAME \
        --resource-group $RG \
        --settings "EventHubConnection=<connection-string>"
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az functionapp config appsettings set` |
    | Key flags | `--name`, `--resource-group`, `--settings` |
    | Variables | `$APP_NAME`, `$RG` |
    | Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


5. **Environment variable**: Set explicitly:
    ```bash
    az functionapp config appsettings set \
        --name $APP_NAME \
        --resource-group $RG \
        --settings "ENVIRONMENT=production"
    ```

    | CLI element | Explanation |
    |---|---|
    | Command(s) | `az functionapp config appsettings set` |
    | Key flags | `--name`, `--resource-group`, `--settings` |
    | Variables | `$APP_NAME`, `$RG` |
    | Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


## 9. Prevention

1. **Use the Flex Consumption tutorial as reference**: Follow the validated step-by-step guide rather than adapting Y1/EP documentation.

2. **Always pair `allowSharedKeyAccess: false` with MI deployment storage**: Add the deployment config step to your provisioning runbook immediately after creating the function app.

3. **Lock down storage as a final provisioning step**: Create PE → DNS zones → blob container → THEN `--default-action Deny`. This ordering prevents locking yourself out during provisioning.

4. **Validate all trigger bindings have matching app settings**: Before publishing, compare `function.json` / decorator-declared bindings against current app settings.

5. **Set all environment variables explicitly**: Never rely on Azure to set environment-specific variables. Include `ENVIRONMENT`, `LOG_LEVEL`, and similar in your app settings template.

!!! warning "Order of operations matters"
    The sequence for Flex Consumption with full private networking is:

    1. Storage account (public access still allowed)
    2. Managed identity + RBAC roles
    3. VNet + subnets
    4. Private endpoints + DNS zones
    5. Deployment blob container
    6. **Lock down storage** (`--default-action Deny`)
    7. Function app creation
    8. Deployment storage → managed identity
    9. App settings (identity-based storage)
    10. VNet integration
    11. Publish

## See Also

- [General Deployment Failures](deployment-failures.md)
- [Managed Identity and RBAC Failure](auth-config/managed-identity-rbac-failure.md)
- [First 10 Minutes](../first-10-minutes/index.md)
- [Flex Consumption Tutorial — First Deploy](../../language-guides/python/tutorial/flex-consumption/02-first-deploy.md)
- [Methodology](../methodology.md)

## Sources

- [Flex Consumption plan hosting](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan)
- [Create and manage Flex Consumption apps](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-how-to)
- [Azure Functions deployment technologies](https://learn.microsoft.com/en-us/azure/azure-functions/functions-deployment-technologies)
- [Azure Storage firewalls and virtual networks](https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security)
- [Azure Functions app settings reference](https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings)
- [Prevent Shared Key authorization](https://learn.microsoft.com/en-us/azure/storage/common/shared-key-authorization-prevent)
- [Set default Storage public network access](https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security-set-default-access)
