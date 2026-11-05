---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/app-service/overview-nat-gateway-integration
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/app-service/networking/private-endpoint
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/nat-gateway/nat-overview
  diagrams:
    - id: nat-gateway-architecture
      type: flowchart
      source: self-generated
      justification: "NAT Gateway integration pattern from MSLearn documentation"
      based_on:
        - https://learn.microsoft.com/en-us/azure/app-service/overview-nat-gateway-integration
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/nat-gateway/nat-overview
    - id: full-isolation-with-nat
      type: flowchart
      source: self-generated
      justification: "Full private ingress and NAT egress pattern synthesized from MSLearn networking documentation"
      based_on:
        - https://learn.microsoft.com/en-us/azure/app-service/networking/private-endpoint
        - https://learn.microsoft.com/en-us/azure/app-service/overview-nat-gateway-integration
        - https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
        - https://learn.microsoft.com/en-us/azure/nat-gateway/nat-overview
content_validation:
  status: verified
  last_reviewed: 2026-09-11
  reviewer: agent
  core_claims:
    - claim: "Azure Functions plans without VNet integration cannot use NAT Gateway for outbound egress control"
      source: https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options
      verified: true
    - claim: "App Service VNet integration can route outbound traffic through a NAT Gateway attached to the integration subnet"
      source: https://learn.microsoft.com/en-us/azure/app-service/overview-nat-gateway-integration
      verified: true
    - claim: "NAT Gateway provides stable outbound public IP addresses for internet egress"
      source: https://learn.microsoft.com/en-us/azure/nat-gateway/nat-overview
      verified: true
---

# Scenario 4: Fixed Outbound IP (NAT Gateway)

Stable outbound IP addresses for function app egress through NAT Gateway, enabling IP-based allowlisting on downstream services.

## Portal Walkthrough

The Networking blade shows the baseline outbound configuration before NAT Gateway is applied. PII is masked.

![Networking blade showing outbound DNS and addresses](../../assets/operations/networking/01-networking.png)

[Observed] Outbound addresses are "Dynamic" on Consumption (Y1). NAT Gateway integration requires Flex Consumption (FC1) or Premium (EP) plans with VNet integration enabled.

## When to Use

- Downstream services require IP allowlisting (legacy firewalls, third-party APIs)
- Regulatory requirements for predictable egress identity
- Multi-region deployments needing consistent outbound IPs per region
- SaaS integrations that authenticate by source IP

## Architecture

<!-- diagram-id: nat-gateway-architecture -->
```mermaid
flowchart TD
    accTitle: Function app fixed outbound IP and private Blob access
    accDescr: Public HTTPS ingress reaches the Function app outside the customer VNet. Outbound VNet integration reaches Blob over a private endpoint; external-service calls use the integration subnet's NAT Gateway public IP. The address and allowlist are illustrative.
    client(["Internet<br/>HTTPS caller"])
    app_runtime["Function App<br/>Managed compute"]
    external_service(["External Service<br/>IP Allowlist: 203.0.113.10"])
    storage_db[("Storage Account")]
    subgraph vnet_fn["Customer VNet"]
        subgraph subnet_int_fn["Integration [NAT Gateway]"]
            vnet_integration[["VNet integration<br/>Outbound only"]]
        end
        subgraph subnet_pe_fn["Private Endpoint Subnet"]
            pe_storage[["Private Endpoint<br/>blob"]]
        end
    end
    client -->|"[Configured] HTTPS"| app_runtime
    app_runtime -->|"[Configured] Outbound"| vnet_integration
    vnet_integration -->|"[Illustrative] NAT public IP<br/>203.0.113.10"| external_service
    vnet_integration -->|"[Configured] Private IP"| pe_storage
    pe_storage -->|"[Configured] Private Link"| storage_db
    %% Layout-only link tiers the destinations; no connection or step is added.
    storage_db ~~~ external_service
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    classDef focusActive fill:#e6f0fd,stroke:#287ce4,stroke-width:2.5px,color:#14202e;
    classDef netBox fill:transparent,stroke:#287ce4,stroke-width:2px,stroke-dasharray:6 3;
    class client,external_service,storage_db baseNeutral;
    class app_runtime,vnet_integration,pe_storage focusActive;
    class vnet_fn,subnet_int_fn,subnet_pe_fn netBox;
    linkStyle default stroke-width:2px;
```

**Reading key:** Solid arrows show initiated connections. The Function app and
Storage service stay outside the customer VNet. The subnet contains the plan-specific integration networking components, not the Function app's compute.
The private endpoint sits in a separate subnet. NAT Gateway is associated
with the integration subnet, not a routed hop. `203.0.113.10` is an illustrative
public source IP and allowlist. Internet-bound traffic must be routed into the
VNet for NAT egress; the Blob private path does not use that public IP
([Functions networking](https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options),
[NAT integration](https://learn.microsoft.com/en-us/azure/app-service/overview-nat-gateway-integration),
[NAT overview](https://learn.microsoft.com/en-us/azure/nat-gateway/nat-overview)).

## Supported Plans

| Plan | Supported | Notes |
|------|:---------:|-------|
| Consumption (Y1) | :material-close: | No VNet integration |
| Flex Consumption (FC1) | :material-check: | Attach NAT to integration subnet |
| Premium (EP) | :material-check: | Full support |
| Dedicated (B1) | :material-minus:[^1] | Not tested in this guide |
| Dedicated (S1+) | :material-check: | Full support |

[^1]: Basic (B1) supports VNet integration per Azure documentation, but is not tested or recommended for NAT Gateway scenarios in this guide. Use Standard (S1+) for production.

## Prerequisites

Complete [Scenario 2: Private Egress](private-egress.md) first. This scenario adds NAT Gateway to the integration subnet.

**Required from Scenario 2:**
- [ ] Function App with VNet integration enabled
- [ ] Integration subnet configured

**Additional requirements:**
- [ ] Public IP address or prefix for NAT Gateway
- [ ] NAT Gateway resource

## Step-by-Step Configuration

### Step 1: Create Public IP for NAT Gateway

```bash
az network public-ip create \
  --name "pip-nat-func" \
  --resource-group "$RG" \
  --location "$LOCATION" \
  --sku Standard \
  --allocation-method Static \
  --zone 1 2 3
```

| Command/Parameter | Purpose |
|-------------------|---------|
| `--sku Standard` | Required for NAT Gateway (Basic not supported) |
| `--allocation-method Static` | Ensures IP doesn't change |
| `--zone 1 2 3` | Zone-redundant for high availability |

### Step 2: Create NAT Gateway

```bash
az network nat gateway create \
  --name "nat-func" \
  --resource-group "$RG" \
  --location "$LOCATION" \
  --public-ip-addresses "pip-nat-func" \
  --idle-timeout 10
```

| Command/Parameter | Purpose |
|-------------------|---------|
| `--public-ip-addresses "pip-nat-func"` | Associates the static public IP |
| `--idle-timeout 10` | Connection idle timeout in minutes (4-120) |

### Step 3: Associate NAT Gateway with Integration Subnet

```bash
az network vnet subnet update \
  --name "snet-integration" \
  --resource-group "$RG" \
  --vnet-name "$VNET_NAME" \
  --nat-gateway "nat-func"
```

| Command/Parameter | Purpose |
|-------------------|---------|
| `--nat-gateway "nat-func"` | Routes all subnet egress through NAT Gateway |

### Step 4: Get NAT Gateway Public IP

```bash
az network public-ip show \
  --name "pip-nat-func" \
  --resource-group "$RG" \
  --query "ipAddress" \
  --output tsv
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az network public-ip show` |
| Key flags | `--name`, `--resource-group`, `--query`, `--output` |
| Variables | `$RG` |
| Expected result | Azure CLI returns the requested resource data; verify names, IDs, status fields, or metric values match the scenario. |


Save this IP address for downstream allowlisting.

### Step 5: Enable Route All (Premium/Dedicated Only)

For Premium and Dedicated plans, ensure all egress routes through VNet:

```bash
az functionapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --settings "WEBSITE_VNET_ROUTE_ALL=1"
```

| Command/Parameter | Purpose |
|-------------------|---------|
| `WEBSITE_VNET_ROUTE_ALL=1` | Forces all outbound traffic through VNet (and thus NAT) |

!!! note "Flex Consumption"
    FC1 already routes outbound traffic through VNet by default. `WEBSITE_VNET_ROUTE_ALL` is not required.

## Using Public IP Prefix (Multiple IPs)

For high-throughput workloads, use a public IP prefix instead of a single IP:

```bash
# Create IP prefix (e.g., /30 = 4 IPs)
az network public-ip prefix create \
  --name "pip-prefix-nat-func" \
  --resource-group "$RG" \
  --location "$LOCATION" \
  --length 30

# Create NAT Gateway with prefix
az network nat gateway create \
  --name "nat-func" \
  --resource-group "$RG" \
  --location "$LOCATION" \
  --public-ip-prefixes "pip-prefix-nat-func" \
  --idle-timeout 10
```

| Command/Parameter | Purpose |
|-------------------|---------|
| `--length 30` | CIDR prefix length (/28 = 16 IPs, /30 = 4 IPs, /31 = 2 IPs) |

## Verification

### Check NAT Gateway Association

```bash
az network vnet subnet show \
  --name "snet-integration" \
  --resource-group "$RG" \
  --vnet-name "$VNET_NAME" \
  --query "natGateway.id" \
  --output tsv
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az network vnet subnet show` |
| Key flags | `--name`, `--resource-group`, `--vnet-name`, `--query`, `--output` |
| Variables | `$RG`, `$VNET_NAME` |
| Expected result | Azure CLI returns the requested resource data; verify names, IDs, status fields, or metric values match the scenario. |


### Verify Outbound IP

Create a function that calls an external service showing the source IP:

```bash
curl --request GET "https://$APP_NAME.azurewebsites.net/api/check-ip"
```

Or call httpbin.org to see your egress IP:

```python
# Example function code
import azure.functions as func
import requests

def main(req: func.HttpRequest) -> func.HttpResponse:
    response = requests.get("https://httpbin.org/ip")
    return func.HttpResponse(response.text)
```

Expected: The `origin` field should match your NAT Gateway public IP.

### Test from Function App

```bash
az functionapp show \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --query "outboundIpAddresses" \
  --output tsv
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp show` |
| Key flags | `--name`, `--resource-group`, `--query`, `--output` |
| Variables | `$APP_NAME`, `$RG` |
| Expected result | Azure CLI returns the requested resource data; verify names, IDs, status fields, or metric values match the scenario. |


!!! warning "outboundIpAddresses vs NAT Gateway"
    The `outboundIpAddresses` property shows default platform IPs. With NAT Gateway configured, actual egress uses the NAT Gateway IP, not these listed IPs.

## Capacity Planning

NAT Gateway has specific capacity limits:

| Metric | Limit |
|--------|-------|
| Concurrent connections per public IP | 64,000 |
| Packets per second | 1 million |
| Connections per second | 50,000 |

For high-scale workloads:

- Add more public IPs or use IP prefix
- Distribute across multiple NAT Gateways with different subnets

## Cost Considerations

NAT Gateway pricing:

| Component | Approximate Cost |
|-----------|------------------|
| NAT Gateway (per hour) | ~$0.045/hour |
| Data processed (per GB) | ~$0.045/GB |
| Public IP (per hour) | ~$0.005/hour |

!!! tip "Cost Optimization"
    NAT Gateway charges apply 24/7 regardless of usage. For development environments, consider:
    
    - Sharing one NAT Gateway across multiple function apps
    - Using NAT only in production, not dev/test

## Troubleshooting

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| External service sees wrong IP | `WEBSITE_VNET_ROUTE_ALL` not set (EP/ASP) | Add the setting and restart |
| Connection timeouts | NAT Gateway not associated | Verify subnet has `natGateway` property |
| SNAT exhaustion | Too many concurrent connections | Add more public IPs or optimize connection pooling |
| High latency | NAT Gateway in different region | Ensure NAT is in same region as function app |

## Combining with Private Ingress

NAT Gateway can be combined with a site private endpoint for private ingress
and fixed-IP public egress:

<!-- diagram-id: full-isolation-with-nat -->
```mermaid
%%{init: {'flowchart': {'nodeSpacing': 20, 'rankSpacing': 45, 'padding': 8}}}%%
flowchart TD
    accTitle: Corporate private ingress with fixed outbound IP
    accDescr: A corporate client initiates a private connection through the site private endpoint to the Function app outside the customer VNet. The app uses a separate outbound integration subnet with NAT Gateway for external API calls. The public source IP is illustrative; this is not an internet-disconnected deployment.
    client(["Corporate Client"])
    app_runtime["Function App<br/>Managed compute"]
    external_service(["External API"])
    subgraph vnet_fn["Customer VNet"]
        subgraph subnet_pe_fn["PE subnet"]
            pe_app[["Site Private Endpoint"]]
        end
        subgraph subnet_int_fn["Integration subnet<br/>[NAT Gateway]"]
            vnet_integration[["VNet integration<br/>Outbound only"]]
        end
    end
    client -->|"[Configured]<br/>Private IP"| pe_app
    pe_app -->|"[Configured]<br/>Private Link"| app_runtime
    app_runtime -->|"[Configured]<br/>Outbound"| vnet_integration
    vnet_integration -->|"[Illustrative]<br/>NAT public IP<br/>203.0.113.10"| external_service
    classDef baseNeutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    classDef focusActive fill:#e6f0fd,stroke:#287ce4,stroke-width:2.5px,color:#14202e;
    classDef netBox fill:transparent,stroke:#287ce4,stroke-width:2px,stroke-dasharray:6 3;
    class client,external_service baseNeutral;
    class app_runtime,pe_app,vnet_integration focusActive;
    class vnet_fn,subnet_int_fn,subnet_pe_fn netBox;
    linkStyle default stroke-width:2px;
```

**Takeaway:** The site private endpoint is inbound-only; outbound calls use VNet
integration in a different subnet. Disable public network access for private-only
ingress. NAT still allows initiated internet egress, so “isolation” here does not
mean no external API connectivity
([private endpoints](https://learn.microsoft.com/en-us/azure/app-service/networking/private-endpoint),
[NAT overview](https://learn.microsoft.com/en-us/azure/nat-gateway/nat-overview)).

## See Also

- [Networking Scenarios Overview](index.md)
- [Scenario 2: Private Egress](private-egress.md)
- [Scenario 3: Private Ingress](private-ingress.md)
- [Platform: Networking](../networking.md)

## Sources

- [Azure Functions networking options (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options)
- [NAT Gateway integration with App Service (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/app-service/overview-nat-gateway-integration)
- [Use private endpoints for Azure App Service (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/app-service/networking/private-endpoint)
- [What is Azure NAT Gateway? (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/nat-gateway/nat-overview)
