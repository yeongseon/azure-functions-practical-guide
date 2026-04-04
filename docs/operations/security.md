# Security Operations

This guide covers day-to-day security operations for Azure Functions: key rotation, RBAC audits, CORS controls, TLS/HTTPS enforcement, IP restrictions, and security monitoring.

!!! tip "Platform Guide"
    For security architecture and auth design decisions, see [Security](../platform/security.md).

!!! tip "Language Guide"
    For Python authentication code examples, see [HTTP Authentication](../language-guides/python/recipes/http-auth.md).

## Introduction

Treat security as continuous operations, not one-time setup.
For production function apps, run a recurring process for keys, access, transport, network boundaries, and monitoring.

## Function key rotation

Function keys are shared secrets.
Rotate on schedule (for example, every 30-90 days) and immediately after leakage or incident response.

List current function and host keys:

```bash
az functionapp function keys list --name "$APP_NAME" --resource-group "$RG" --function-name "$FUNCTION_NAME"
az functionapp keys list --name "$APP_NAME" --resource-group "$RG"
```

Regenerate by setting new values:

```bash
NEW_FUNCTION_KEY="<new-function-key-value>"
NEW_HOST_KEY="<new-host-key-value>"
az functionapp function keys set --name "$APP_NAME" --resource-group "$RG" --function-name "$FUNCTION_NAME" --key-name "default" --key-value "$NEW_FUNCTION_KEY"
az functionapp keys set --name "$APP_NAME" --resource-group "$RG" --key-type "functionKeys" --key-name "default" --key-value "$NEW_HOST_KEY"
```

Automate rotation with Azure Automation, Logic Apps, or a scheduled function.
Recommended runbook:

1. Generate and set new keys.
2. Save values as new Azure Key Vault secret versions.
3. Notify consumers to refresh secrets.
4. Confirm traffic cutover.
5. Revoke old keys.

## RBAC and access control audit

RBAC drift is a frequent operational risk.
Review role assignments regularly and remove broad standing access.

```bash
APP_RESOURCE_ID="/subscriptions/<subscription-id>/resourceGroups/$RG/providers/Microsoft.Web/sites/$APP_NAME"
az role assignment list --scope "$APP_RESOURCE_ID" --include-inherited true
```

Audit Owner/Contributor grants:

```bash
az role assignment list --scope "$APP_RESOURCE_ID" --include-inherited true --query "[?roleDefinitionName=='Owner' || roleDefinitionName=='Contributor'].{principalName:principalName,principalType:principalType,role:roleDefinitionName,scope:scope}" --output table
```

Audit one deployment principal (masked ID):

```bash
az role assignment list --assignee "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" --all true --query "[].{role:roleDefinitionName,scope:scope,principalType:principalType}"
```

Least-privilege guidance: prefer GitHub Actions OIDC over client secrets, scope deployment identity to minimum required resources, and re-validate after pipeline ownership changes.

## CORS configuration

CORS controls which browser origins can call HTTP endpoints.
It is not authentication and must be combined with auth controls.

```bash
az functionapp cors show --name "$APP_NAME" --resource-group "$RG"
```

Add approved origins:

```bash
az functionapp cors add --name "$APP_NAME" --resource-group "$RG" --allowed-origins "https://portal.contoso.example" "https://admin.contoso.example"
```

Remove deprecated origins:

```bash
az functionapp cors remove --name "$APP_NAME" --resource-group "$RG" --allowed-origins "https://old.contoso.example"
```

Enable credentialed requests only when required:

```bash
az functionapp cors credentials --name "$APP_NAME" --resource-group "$RG" --enable true
```

!!! warning "Wildcard risk"
    Avoid `*` in production. With credentialed traffic, wildcard origins can expose session context to unintended browser origins.

## TLS and HTTPS enforcement

Enforce encrypted transport for all production apps.
Set HTTPS-only and minimum TLS version 1.2 or higher.

```bash
az functionapp update --name "$APP_NAME" --resource-group "$RG" --https-only true
az functionapp config set --name "$APP_NAME" --resource-group "$RG" --min-tls-version "1.2"
```

Custom domain and certificate operations:

```bash
az functionapp config hostname add --name "$APP_NAME" --resource-group "$RG" --hostname "api.contoso.example"
az functionapp config ssl bind --name "$APP_NAME" --resource-group "$RG" --certificate-thumbprint "<certificate-thumbprint>" --ssl-type "SNI"
```

Operational checks: monitor certificate expiry, verify HTTPS redirection, and re-check TLS baseline after IaC or policy changes.

## IP restrictions

Use access restrictions to constrain inbound access to app and deployment surfaces.
Always manage main site and SCM site independently.

Allow known ingress and deny default:

```bash
az functionapp config access-restriction add --name "$APP_NAME" --resource-group "$RG" --rule-name "AllowCorpEgress" --action "Allow" --ip-address "203.0.113.0/24" --priority 100
az functionapp config access-restriction add --name "$APP_NAME" --resource-group "$RG" --rule-name "DenyAll" --action "Deny" --ip-address "0.0.0.0/0" --priority 2147483647
```

Restrict SCM endpoint separately:

```bash
az functionapp config access-restriction add --name "$APP_NAME" --resource-group "$RG" --rule-name "AllowScmBuildAgents" --action "Allow" --ip-address "198.51.100.0/24" --priority 110 --scm-site true
```

Combine with virtual network service endpoint rules when needed:

```bash
az functionapp config access-restriction add --name "$APP_NAME" --resource-group "$RG" --rule-name "AllowFromIntegrationSubnet" --action "Allow" --vnet-name "$VNET_NAME" --subnet "$SUBNET_NAME" --priority 120
```

## Diagnostic logging for security events

Enable diagnostics to send platform logs and metrics to Log Analytics for audit and detection.

```bash
WORKSPACE_ID="/subscriptions/<subscription-id>/resourceGroups/$RG/providers/Microsoft.OperationalInsights/workspaces/$LAW_NAME"
az monitor diagnostic-settings create --name "func-security-diagnostics" --resource "$APP_RESOURCE_ID" --workspace "$WORKSPACE_ID" --logs '[{"category":"AppServiceHTTPLogs","enabled":true},{"category":"AppServiceAuditLogs","enabled":true},{"category":"AppServicePlatformLogs","enabled":true}]' --metrics '[{"category":"AllMetrics","enabled":true}]'
```

KQL: failed authentication/authorization trend:

```kql
AppServiceHTTPLogs
| where TimeGenerated > ago(24h)
| where ScStatus in (401, 403)
| summarize Failures=count() by CIp, CsHost, CsUriStem, bin(TimeGenerated, 15m)
| order by Failures desc
```

KQL: suspicious key-query usage pattern:

```kql
AppServiceHTTPLogs
| where TimeGenerated > ago(7d)
| where CsUriQuery has "code="
| summarize Requests=count() by CIp, bin(TimeGenerated, 1h)
| where Requests > 100
| order by Requests desc
```

Create a scheduled query alert for repeated failures:

```bash
az monitor scheduled-query create --name "func-auth-failures" --resource-group "$RG" --scopes "$APP_RESOURCE_ID" --condition "count 'AppServiceHTTPLogs | where ScStatus in (401,403)' > 50" --description "High unauthorized/forbidden response volume" --evaluation-frequency "PT5M" --window-size "PT15M" --severity 2
```

## Security compliance checklist

Use this minimum operating cadence and tighten based on risk and regulation.

### Daily

- Check 401/403 anomalies and unfamiliar source IPs.
- Confirm alert delivery to on-call channels.
- Validate no emergency access grant remains active.

### Weekly

- Review RBAC changes and remove temporary privileges.
- Reconcile CORS allowlist with active front-end domains.
- Verify SCM restrictions still match CI/CD origin ranges.

### Monthly

- Rotate function and host keys.
- Validate Key Vault propagation and client cutover.
- Confirm HTTPS-only and minimum TLS baseline in all environments.

### Quarterly

- Re-certify Owner and Contributor assignments.
- Run tabletop or live drill for leaked key and compromised principal scenarios.
- Review certificate inventory and renew ahead of expiration.

!!! note "Control ownership"
    Assign explicit owners: platform team for RBAC/TLS/network controls, application team for key-consumer rollout, and operations team for monitoring triage and evidence retention.

## Sources

- [Azure Functions security concepts](https://learn.microsoft.com/azure/azure-functions/security-concepts)
- [Work with access keys in Azure Functions](https://learn.microsoft.com/azure/azure-functions/function-keys-how-to)
- [Azure role-based access control overview](https://learn.microsoft.com/azure/role-based-access-control/overview)
- [Use managed identities with Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-identity-based-connections-tutorial)
- [Configure CORS for App Service](https://learn.microsoft.com/azure/app-service/app-service-web-tutorial-rest-api#app-service-cors-versus-your-cors)
- [Configure TLS/SSL bindings in App Service](https://learn.microsoft.com/azure/app-service/configure-ssl-bindings)
- [Set up access restrictions for App Service](https://learn.microsoft.com/azure/app-service/app-service-ip-restrictions)
- [Azure Monitor platform logs overview](https://learn.microsoft.com/azure/azure-monitor/essentials/platform-logs-overview)
