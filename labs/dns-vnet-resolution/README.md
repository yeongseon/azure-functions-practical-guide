# Lab: DNS and VNet Name Resolution Troubleshooting

## Objective
Diagnose DNS resolution failures for Function Apps integrated with virtual networking.

## Prerequisites
- Azure subscription
- Azure Functions Core Tools
- Python runtime (3.11 or later)
- Azure CLI
- Azurite (local storage emulator)

## Scenario
A function can reach public endpoints, but private endpoints intermittently fail by hostname.
You need to determine whether failures are caused by DNS records, resolver configuration,
or virtual network routing.
The goal is to isolate DNS behavior from transport-layer failures.

## Steps
1. Create a Python Functions project and HTTP probe.
   ```bash
   func init dns-vnet-lab --worker-runtime python
   cd dns-vnet-lab
   func new --template "HTTP trigger" --name DnsProbe
   ```
2. Add diagnostic code to resolve and call a target hostname.
   Return resolved IP, response status, and exception details.
3. Run locally to validate baseline behavior.
   ```bash
   func start --verbose
   ```
4. Provision Azure networking resources.
   ```bash
   az group create --name rg-dns-vnet-lab --location eastus
   az network vnet create --name vnet-dns-lab --resource-group rg-dns-vnet-lab --location eastus --address-prefixes 10.10.0.0/16 --subnet-name snet-functions --subnet-prefixes 10.10.1.0/24
   az network private-dns zone create --resource-group rg-dns-vnet-lab --name privatelink.blob.core.windows.net
   az network private-dns link vnet create --resource-group rg-dns-vnet-lab --zone-name privatelink.blob.core.windows.net --name link-dns-lab --virtual-network vnet-dns-lab --registration-enabled false
   ```
5. Create Function App and integrate with VNet.
   ```bash
   az storage account create --name stdnsvnetlab123 --resource-group rg-dns-vnet-lab --location eastus --sku Standard_LRS
   az functionapp create --name func-dns-vnet-lab-123 --resource-group rg-dns-vnet-lab --storage-account stdnsvnetlab123 --consumption-plan-location eastus --runtime python --runtime-version 3.11 --functions-version 4
   ```
6. Deploy app.
   ```bash
   func azure functionapp publish func-dns-vnet-lab-123
   ```
7. Introduce failure: query a private DNS name without corresponding record.
8. Capture function output and platform logs.
   ```bash
   az webapp log tail --name func-dns-vnet-lab-123 --resource-group rg-dns-vnet-lab
   ```
9. Add correct private DNS record and retest.
10. Validate name resolution from Kudu console and from function endpoint.
11. Document before/after behavior and root cause.
12. Add one negative-control test (deliberately wrong record) and confirm expected failure.
13. Restore the valid record and verify success again.
14. Capture a final runbook section with:
    - DNS record checked
    - Resolver used
    - Expected IP
    - Actual result
15. Share the runbook with operations owners for incident reuse.

## Expected Behavior
- Missing private DNS records produce name resolution errors.
- Public DNS continues to resolve while private names fail.
- Adding correct DNS zone linkage and records restores connectivity.
- Diagnostic output clearly separates DNS failures from HTTP failures.
- Negative-control tests confirm the runbook detects real DNS misconfiguration.
- Final runbook data enables faster triage for future incidents.

## Cleanup
```bash
az group delete --name rg-dns-vnet-lab --yes --no-wait
```
Delete local lab project after completion.
If private DNS records were created manually, remove stale test records.

## See Also
- [Networking concepts](../../docs/platform/networking.md)
- [Troubleshooting playbook](../../docs/language-guides/python/troubleshooting.md)
- [Monitoring operations](../../docs/operations/monitoring.md)
