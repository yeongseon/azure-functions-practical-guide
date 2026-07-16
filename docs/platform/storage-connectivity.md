---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/storage-considerations
content_validation:
  status: verified
  last_reviewed: 2026-07-16
  reviewer: agent
  core_claims:
    - claim: "Azure Functions requires an associated storage account (AzureWebJobsStorage) used for host operations such as trigger management, leases, timers, and default key storage; losing access can make the host unhealthy."
      source: https://learn.microsoft.com/en-us/azure/azure-functions/storage-considerations
      verified: true
    - claim: "Premium and Consumption plans use an Azure Files content share (WEBSITE_CONTENTAZUREFILECONNECTIONSTRING / WEBSITE_CONTENTSHARE), and WEBSITE_CONTENTOVERVNET routes that content share over the virtual network."
      source: https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
      verified: true
    - claim: "Setting a storage firewall defaultAction to Deny keeps the public endpoint enabled while blocking unlisted sources, which is a different control from disabling public network access entirely."
      source: https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security
      verified: true
    - claim: "A private endpoint requires Private DNS so the storage FQDN resolves to a private IP; if the private DNS zone is missing, the FQDN resolves to a public IP and connectivity behavior can mask the misconfiguration."
      source: https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints
      verified: true
    - claim: "Flex Consumption can use managed identity for AzureWebJobsStorage via AzureWebJobsStorage__accountName and AzureWebJobsStorage__credential=managedidentity."
      source: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
      verified: true
---

# Storage Connectivity

Azure Functions has a deeper storage dependency than a typical web app: the runtime itself relies on storage for host operations. This page is the central reference for **how the Function App reaches storage**, independent of **how it authenticates** to it. It covers every network posture — public endpoint, service endpoint, and private endpoint — and maps them against the different storage **roles** a Function App uses.

Use the scenario pages for step-by-step procedures:

- [Public Only](networking-scenarios/public-only.md)
- [Storage Service Endpoint](networking-scenarios/storage-service-endpoint.md)
- [Private Egress (Private Endpoint)](networking-scenarios/private-egress.md)

## 1. Storage Roles in Azure Functions

Unlike a plain web app, "the storage account" for Functions is really several distinct roles. Each has its own network path and must be verified independently.

| Storage role | Example / setting | What breaks if the network path fails |
|--------------|-------------------|----------------------------------------|
| **Host Storage** | `AzureWebJobsStorage` | Host startup, trigger management, leases, timers, queue state — the **host itself** can go unhealthy, not just one function |
| **Content Share** | `WEBSITE_CONTENTAZUREFILECONNECTIONSTRING`, `WEBSITE_CONTENTSHARE`, `WEBSITE_CONTENTOVERVNET` | App content (the deployed files) becomes unreachable — requires the Storage **file** endpoint and TCP **445** |
| **Trigger / Binding Storage** | Blob/Queue trigger `Connection` (may be a separate account) | The specific trigger stops firing while the host stays healthy — easy to misdiagnose |
| **Deployment Storage** | Flex Consumption deployment container / `WEBSITE_RUN_FROM_PACKAGE` URL | Deployments fail or the package cannot be mounted at runtime |
| **Application Data Storage** | Accounts accessed directly from function code / SDK | Business logic fails; host and triggers may look fine |

!!! danger "Host Storage is not just another dependency"
    If `AzureWebJobsStorage` connectivity is blocked, the Functions host can fail to start or become **Unhealthy** — this is qualitatively different from a single downstream call failing. See the [Storage Access Failure lab](../troubleshooting/lab-guides/storage-access-failure.md).

## 2. Authentication vs Network — Two Independent Axes

Storage access has **two** independent controls. Confusing them is the most common source of misconfiguration.

- **Authentication** — *who* is allowed: shared key (connection string) vs **managed identity + RBAC**.
- **Network** — *from where* access is allowed: public endpoint, service endpoint (subnet rule), or private endpoint.

A request must satisfy **both**. Managed identity with correct RBAC still fails if the network firewall denies the source. A permissive network still fails if the identity lacks the right data-plane role. Always diagnose them separately.

## 3. Public Endpoint

The storage account is reachable over its public endpoint. This is the default and requires no VNet integration.

- DNS resolves to a **public IP**.
- `publicNetworkAccess = Enabled`, `defaultAction = Allow`.
- Suitable for dev/test; for production, layer on IP rules or move to service/private endpoints.

See [Public Only](networking-scenarios/public-only.md).

## 4. Service Endpoint

The storage account keeps its **public endpoint**, but only accepts traffic from an authorized **subnet** (`Microsoft.Storage` service endpoint + VNet rule on Selected networks).

- DNS still resolves to a **public IP** (this is expected).
- `publicNetworkAccess = Enabled`, `defaultAction = Deny`, plus a VNet rule for the integration subnet.
- No Private DNS zone; Route All not required.

See [Storage Service Endpoint](networking-scenarios/storage-service-endpoint.md).

## 5. Private Endpoint

A private endpoint places a NIC with a **private IP** into the VNet for the storage account.

- Requires Private DNS zones (`privatelink.blob|queue|table|file.core.windows.net`) so the storage FQDN resolves to the **private IP**.
- For a fully private posture, set `publicNetworkAccess = Disabled`.
- Functions typically need private endpoints for **blob, queue, table, and file** depending on plan and features.

See [Private Egress](networking-scenarios/private-egress.md).

## 6. Hosting Plan Differences

| Plan | Host Storage auth | Content share | Notable settings |
|------|-------------------|---------------|------------------|
| Consumption (Y1) | Connection string (shared key) | Azure Files content share required | Cannot use VNet integration |
| Flex Consumption (FC1) | **Managed identity** supported | No classic content share; uses deployment container | `AzureWebJobsStorage__accountName`, `AzureWebJobsStorage__credential=managedidentity` |
| Premium (EP) | Managed identity supported for host storage | Azure Files content share **required** | `WEBSITE_CONTENTAZUREFILECONNECTIONSTRING`, `WEBSITE_CONTENTSHARE`, `WEBSITE_CONTENTOVERVNET=1` |
| Dedicated (ASP) | Connection string or identity | Required by default (can avoid with `WEBSITE_RUN_FROM_PACKAGE=1`) | `WEBSITE_RUN_FROM_PACKAGE=1` pattern |

!!! warning "Enterprise policy: allowSharedKeyAccess=false"
    Subscriptions that enforce `allowSharedKeyAccess: false` block plans that require an Azure Files content share with shared key (Y1, EP content share). Prefer FC1 (identity-based blob storage) or ASP with `WEBSITE_RUN_FROM_PACKAGE=1`.

## 7. Storage Network Settings Combination Matrix

This is the central table. It separates the **storage setting**, the **Function App network config**, what **DNS returns**, the **actual endpoint** used, and the **expected result**.

| Storage setting | Function App config | DNS result | Actual endpoint | Expected result |
|-----------------|---------------------|------------|-----------------|-----------------|
| All networks | No VNet integration | Public IP | Public endpoint | Works |
| All networks | VNet integration | Public IP | Public endpoint | Works — VNet integration alone does **not** make storage private |
| All networks | VNet integration + Route All | Public IP | Public endpoint | Traffic can traverse the VNet, but the storage endpoint is still public |
| Selected networks + IP rule | Allow function outbound IP | Public IP | Public endpoint | Plan/region dependent — outbound IP must be stable and allowlisted. **Consumption (Y1) outbound IPs are shared and can change; Flex Consumption IPs are not stable without a NAT Gateway**, making IP-rule access unreliable |
| Selected networks + Service Endpoint | Integration subnet allowed | Public IP | Public endpoint + service endpoint | Works — subnet identity grants access |
| Private Endpoint + All networks | Private DNS correct | Private IP | Private endpoint | Function uses private path; other clients can still reach the public endpoint |
| Private Endpoint + All networks | Private DNS **missing** | Public IP | Public endpoint | Connection may still succeed publicly, **masking** the DNS misconfiguration |
| Public network access Disabled | Private endpoint + Private DNS | Private IP | Private endpoint | Correct private-only configuration |
| Public network access Disabled | No private endpoint | Public IP | Unreachable | Host startup or trigger failure |

!!! tip "The dangerous row"
    *Private Endpoint + All networks + missing Private DNS* is the silent failure: because the public endpoint is still open, the app keeps working while resolving to a public IP. The private path is not actually in use, and the day you set `publicNetworkAccess = Disabled` it breaks. Always verify DNS returns a private IP.

## 8. Host Startup Impact

Because `AzureWebJobsStorage` participates in host startup, a storage network change that blocks it does not degrade gracefully — the host may fail to initialize. When tightening storage networking:

1. Configure private/service endpoints and DNS **first**.
2. Verify the app still resolves and reaches storage.
3. Only then set `defaultAction = Deny` or `publicNetworkAccess = Disabled`.

Reversing this order is a leading cause of self-inflicted outages. See [Private Egress — Order Matters](networking-scenarios/private-egress.md).

## 9. DNS and Connectivity Verification

```bash
# Storage FQDNs should resolve to PRIVATE IPs when private endpoints + Private DNS are configured
for SVC in blob queue table file; do
  echo "== $SVC =="
  nslookup "$STORAGE_NAME.$SVC.core.windows.net"
done
```

Interpretation:

- **Private IP (10.x / VNet range)** → private endpoint + Private DNS working.
- **Public IP** → either public/service-endpoint scenario (expected there), or a **missing Private DNS zone** in a private-endpoint scenario (misconfiguration).

For content share (Azure Files) also verify the **file** endpoint resolves and that TCP **445** egress is permitted.

## See Also

- [Networking Scenarios Overview](networking-scenarios/index.md)
- [Public Only](networking-scenarios/public-only.md)
- [Storage Service Endpoint](networking-scenarios/storage-service-endpoint.md)
- [Private Egress](networking-scenarios/private-egress.md)
- [Platform: Networking](networking.md)
- [Troubleshooting: Storage Access Failure](../troubleshooting/lab-guides/storage-access-failure.md)

## Sources

- [Azure Functions storage considerations (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/storage-considerations)
- [Azure Functions networking options (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options)
- [Configure Azure Storage firewalls and virtual networks (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security)
- [Use private endpoints for Azure Storage (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints)
- [Azure Functions Flex Consumption plan (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan)
