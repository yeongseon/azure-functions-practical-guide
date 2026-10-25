---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-deployment-slots
---
# Platform Limits

Use this shared reference for all language guides. Limits depend on hosting plan, operating system, region, runtime, and configuration; they are not guaranteed available capacity. Azure Container Apps hosting is outside this page's scope.

**Official-source review: 2026-10-25.** Values below were checked against Microsoft Learn, not measured in Azure. Follow the linked source for changes after this review; tutorial settings and historical Portal captures are not service limits.

## Hosting Plan Comparison

The [Functions scale table](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale#scale) defines the unit of scale. The [deployment slots article](https://learn.microsoft.com/en-us/azure/azure-functions/functions-deployment-slots) counts **production in the total**.

| Limit / support | Consumption (Y1), Windows | Consumption (Y1), Linux | Flex Consumption (FC1), Linux only | Elastic Premium (EP), Windows / Linux | Dedicated (App Service), Windows / Linux |
|---|---|---|---|---|---|
| Maximum instances | 200 per app | 100 per app | Up to 1,000 on-demand per function scale group; quota also applies | Up to 100 per plan on Windows; 20–100 on Linux; check region exceptions below | Basic: 3; Standard: 10; Premium v1: 20; Premium v2–v4: 30; Isolated: 100 |
| Default / maximum execution timeout | 5 / 10 minutes | 5 / 10 minutes | 30 minutes / unbounded | 30 minutes / unbounded | 30 minutes / unbounded with Always On |
| Deployment slots, including production | 2 total | 2 total | Not supported | 3 total | SKU-dependent; see App Service slot limits below |
| Instance memory | 1.5 GB | 1.5 GB | 512 / 2,048 / 4,096 MB | EP1: 3.5 GB; EP2: 7 GB; EP3: 14 GB | SKU-dependent; do not infer from EP sizes |
| Function apps per plan | 100 | 100 | 1 | 100 | Resource-constrained, not guaranteed unlimited density |
| VNet integration | No | No | Yes | Yes | Supported on eligible App Service tiers |

### Scale ceilings, configured caps, and quotas

- **Consumption:** Windows and Linux ceilings differ even though both use Y1. Linux also has a scale-out limit of **500 instances per subscription per hour**. A lower app cap can be set with `siteConfig.functionAppScaleLimit`; `0` or `null` removes that configured restriction, not the platform ceiling.
- **Premium:** The [region/OS table](https://learn.microsoft.com/en-us/azure/azure-functions/functions-premium-plan#region-max-scale-out) is more specific than the headline maximum. For example, Korea Central lists Windows 100 / Linux 20; East US 2 lists Windows 80 / Linux 100. Some regions have no Linux availability. Private-endpoint-restricted HTTP triggers have a **20-instance** scale-out limit in the Functions scale table. A plan maximum burst setting and a lower per-app `functionAppScaleLimit` can further restrict scale.
- **Flex:** The default configured maximum is **100**, with supported settings **1–1,000**. The app setting applies separately to on-demand instances in each independently scaling function group, not to combined app instances. Always-ready instances are additional and are not counted against that maximum. HTTP functions share a group, as do Event Grid Blob triggers and Durable Functions triggers; other functions scale independently. See [limit scale-out](https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling#limit-scale-out).
- **Flex regional quota:** All Flex apps in one subscription and region share a default **250-core quota (512,000 MB equivalent)**; Azure Free Trial and Azure for Students default to **15 cores (30,720 MB equivalent)**. Always-ready instances count against this quota. The currently assigned quota and capacity can constrain scale below configured maxima; increases require capacity review. See [regional subscription quotas](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan#regional-subscription-memory-quotas).
- **Dedicated:** The Functions overview summarizes 10–30 (100 ASE), but the more specific [App Service SKU limits](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits#azure-app-service-limits) include Basic at 3. Use the actual SKU, configured worker count, and autoscale rules. Basic, Standard, Premium, and Isolated tiers do not have interchangeable ceilings.

An instance maximum is not invocation concurrency, a scale-out rate, or a reservation. Lower values in this repository's tutorials are workload configuration examples, not revised platform quotas.

### Deployment slots

Current Learn documents **two total Consumption slots**, without a Windows-only restriction; its [migration assessment](https://learn.microsoft.com/en-us/azure/azure-functions/migration/migrate-plan-consumption-to-flex#verify-deployment-slots-usage) also discusses slots for Linux Consumption sources. Do not apply the old Windows-only selector annotation to Linux Python apps. Flex does not support slots on any language stack.

For Dedicated, use the [App Service deployment-slot row](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits#azure-app-service-limits) for your tier. That table counts **staging slots excluding production**, unlike the Functions table: Free/Shared/Basic have no staging slots, Standard has 5, and Premium/Isolated tiers have 20. Do not read the Functions overview's `1–20` summary as 20 additional slots on every Dedicated SKU. Slot swaps can terminate executions; they are not an uninterrupted-execution guarantee.

## Runtime Support and Linux Consumption Migration

Python is supported on **Linux only** in Azure; the Windows Consumption column is not a Python deployment option. Node.js, Java, PowerShell, and .NET support depends on the language version and execution model. Flex requires .NET **isolated worker**, not in-process. Use [supported languages](https://learn.microsoft.com/en-us/azure/azure-functions/supported-languages) and [Flex stack support](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan#supported-language-stack-versions) together, then confirm availability in the target region.

Linux Consumption retires on **September 30, 2028**, receives no new features or language versions, and has these last supported language versions (not a promise of support beyond each language's own lifecycle):

| Stack | Last version added to Linux Consumption |
|---|---|
| Python | 3.12 |
| Node.js | 22 |
| Java | 21 |
| .NET | 9 |
| PowerShell | 7.4 |

Windows Consumption is not affected by this Linux retirement. The separate Linux Consumption **Functions v3** stop-running date was September 30, 2026; do not confuse host runtime retirement with the hosting-plan deadline.

**Migration decision path:** For a new Linux serverless workload, start with [Flex tutorials](../language-guides/python/tutorial/index.md). For an existing app, follow [Consumption-to-Flex assessment and migration](https://learn.microsoft.com/en-us/azure/azure-functions/migration/migrate-plan-consumption-to-flex): check region, runtime version/model, slots, certificates, and Blob trigger source before selecting a target. Migration creates a **new app**, not an in-place plan change. If Flex cannot meet an OS or release requirement, compare [Premium and Dedicated](../platform/hosting.md#hosting-decision-workflow). Windows-dependent code must be made Linux-compatible before moving to Flex. Preserve a tested cutover and rollback path.

## Execution Timeout

`functionTimeout` in `host.json` controls invocation duration. Omitting it uses the plan default above; `"functionTimeout": "-1"` requests unbounded duration only where supported. Timeout errors restart the language worker (or the host for .NET in-process); do not assume a specific HTTP status code follows.

**Unbounded does not mean uninterrupted:** Flex and Premium allow a 60-minute scale-in grace period and a 10-minute platform-update grace period. Dedicated requires Always On for unbounded execution and remains subject to platform updates. See the [timeout table and footnotes](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale#function-app-timeout-duration). For long HTTP work, return an immediate response and process asynchronously, or use Durable Functions.

## HTTP Request and Response Limits

| Constraint | Documented value / boundary | Qualification |
|---|---|---|
| Request body | 210 MB in the Functions service table; 220,200,960 bytes in the app-setting reference | `FUNCTIONS_REQUEST_BODY_SIZE_LIMIT` can reduce, not increase, this maximum. Gateways, proxies, or application code can impose lower limits. |
| Query string length | 4,096 | Host-configured value in the Functions service table, not an Internet-wide standard. |
| Request URL length | 8,192 | Host-configured value in the Functions service table, not an Internet-wide standard. |
| HTTP response wait | 230 seconds | Functions documents this front-end response boundary independently of invocation timeout. Client/proxy timeouts can be shorter; an unbounded function timeout does not extend it. |
| Response body / aggregate headers | No universal value established by the cited Functions service table | The former **100 MB response** and **32 KB headers** entries were unsupported as cross-plan guarantees. Check the actual front end, OS/server configuration, language stack, and any intermediary. |

Sources: [Functions service limits and host-config footnote](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale#service-limits), [request body setting](https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings#functions_request_body_size_limit), and [timeout footnote](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale#function-app-timeout-duration). Do not turn a host default into an end-to-end payload guarantee.

## Connections, Memory, and Storage Boundaries

| Resource | Scope and interpretation |
|---|---|
| Consumption outbound connections | **600 active / 1,200 total per instance**, not per invocation or subscription. Reuse clients and connection pools. |
| Flex / Premium outbound connections | Learn labels these **unbounded** in the Functions table: no listed Functions connection-count cap, **not infinite sockets, ports, bandwidth, or downstream capacity**. |
| Dedicated connections | Use the App Service SKU limits and your network path; do not import Consumption's sandbox connection limit. |
| Memory | The host, dependencies, workers, and concurrent invocations share instance resources. Fixed Python idle-worker estimates are not service limits or measurements of your app. Profile the deployed workload. |
| Temporary storage | Functions lists **0.8 GB Flex**, **11–61 GB Premium**, and **0.5 GB Consumption**, with a Linux Consumption footnote of **1.5 GB**. Temporary storage totals are across apps in the same App Service plan, not a durable data allowance per app. Dedicated is SKU-dependent. |
| Persisted storage | The Functions table lists **0 GB Flex**, **250 GB Premium**, and **1 GB Consumption** with Azure Files and Linux-mount qualifications. These describe hosting storage, not the capacity of `AzureWebJobsStorage` or a deployment Blob container. Linux requires an explicit mount for your own Azure Files share. Dedicated is SKU-dependent. |
| Storage-account throughput | Azure Storage service targets, not Functions quotas. The former 20,000 account requests/s, 60 MiB/s/blob, 2,000 queue messages/s, and 20,000 table operations/s were not universal Functions guarantees. Use the storage service, account type, region, redundancy, and workload-specific target documentation. |

See [Functions service-limit footnotes](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale#service-limits), [connection management](https://learn.microsoft.com/en-us/azure/azure-functions/manage-connections), and [storage connectivity](../platform/storage-connectivity.md#6-hosting-plan-differences). Host storage authentication, deployment Blob authentication, and classic Azure Files content shares are separate concerns; Flex does not use a classic content share or `WEBSITE_RUN_FROM_PACKAGE`. Keep [deployment settings plan/OS-specific](../operations/deployment.md#package-configuration-by-plan-and-os).

## Other App Limits and Usage Notes

- Functions service limits list **5,000 function apps per subscription**. Apps-per-plan counts do not override that limit.
- Custom domains are **25 per Flex app**, versus **500 per Consumption/Premium/Dedicated app**, per the Functions service table. DNS mapping and certificate support have separate plan qualifications.
- Do not use “no hard limit, recommended fewer than 100 functions” as an app-size guarantee. The [scaling article](https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling#understanding-scaling-behaviors) documents a **100 monitored event-trigger** limit for Consumption/Premium scale decisions, not a universal functions-per-app count.
- Package-size restrictions depend on deployment technology; use [run-from-package considerations](https://learn.microsoft.com/en-us/azure/azure-functions/run-functions-from-deployment-package#general-considerations) only for applicable workflows, not as a universal Flex deployment quota.
- The former “4,096 bytes per app setting; no limit on number” entry was not sourced as a universal Functions limit and has been removed. Use the [Functions app settings reference](https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings) and applicable App Service configuration limits.
- Run `bash scripts/validate_hosting_limits.sh` after editing this reference or tutorial selectors. It checks shared-reference links and guards against duplicated selector quota/runtime-version rows; it does not fetch Learn or prove cloud capacity.

## See Also

- [Hosting Plans](../platform/hosting.md)
- [Scaling](../platform/scaling.md)
- [Python Sizing Considerations](../language-guides/python/platform-limits.md)
- [host.json Reference](host-json.md)
- [Deployment](../operations/deployment.md)

## Sources

- [Azure Functions scale, OS support, timeouts, and service limits](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [Flex Consumption: instance sizes, scale groups, quota, and restrictions](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan)
- [Event-driven scaling: configured maxima and monitored triggers](https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling)
- [Premium: SKU resources and region/OS scale ceilings](https://learn.microsoft.com/en-us/azure/azure-functions/functions-premium-plan)
- [Deployment slots: totals including production](https://learn.microsoft.com/en-us/azure/azure-functions/functions-deployment-slots)
- [App Service limits: tier-specific resources and staging slots](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits#azure-app-service-limits)
- [Supported languages and Linux Consumption version ceilings](https://learn.microsoft.com/en-us/azure/azure-functions/supported-languages)
- [Consumption plan retirement](https://learn.microsoft.com/en-us/azure/azure-functions/consumption-plan)
- [Consumption-to-Flex migration assessment](https://learn.microsoft.com/en-us/azure/azure-functions/migration/migrate-plan-consumption-to-flex)
- [Functions app settings](https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings)
- [Managing connections](https://learn.microsoft.com/en-us/azure/azure-functions/manage-connections)
- [Storage considerations](https://learn.microsoft.com/en-us/azure/azure-functions/storage-considerations)
- [Standard storage account scalability targets](https://learn.microsoft.com/en-us/azure/storage/common/scalability-targets-standard-account)
- [Blob scalability targets](https://learn.microsoft.com/en-us/azure/storage/blobs/scalability-targets)
- [Queue scalability targets](https://learn.microsoft.com/en-us/azure/storage/queues/scalability-targets)
- [Table scalability targets](https://learn.microsoft.com/en-us/azure/storage/tables/scalability-targets)
- [Run-from-package considerations](https://learn.microsoft.com/en-us/azure/azure-functions/run-functions-from-deployment-package#general-considerations)
