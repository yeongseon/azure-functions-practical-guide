---
title: Tutorial Screenshot Inventory
---

# Tutorial Screenshot Inventory

Repository-only census for [#384](https://github.com/yeongseon/azure-functions-practical-guide/issues/384),
recorded 2026-11-04 at **`e1c409ee42d179d65ff0033295d998dc96fb1953`**
(the fetched `origin/main`). This contributor reference keeps the cross-language
inventory separate from the existing Python-only capture plan.

## Coverage by Language, Plan, and Step

Scope: numbered leaf pages under `docs/language-guides/<language>/tutorial/<plan>/`;
exclude chooser/index pages. There are **158 unique pages**, **0** with Markdown
images and **0** with screenshot macro references. A plan is not a capture:
**151 missing + 7 planned + 0 blocked + 0 captured + 0 verified = 158 pages**.

| Status | Meaning in this inventory |
|---|---|
| missing | No referenced screenshot and no manifest entry assigned to this step |
| planned | Assigned entries in `scripts/capture/manifest.yaml`; no image bytes yet |
| blocked | Capture work explicitly blocked pending authorized Portal access; not inferred merely from a missing file |
| captured | Image bytes retained, but final-image privacy/caption verification not established |
| verified | Final bytes, provenance, privacy and caption accuracy reviewed; never inferred from file existence or a date alone |

`planned` describes intended coverage, not complete coverage of a tutorial step.
No live capture was attempted here; future Portal work needs authorization even
when its inventory status is `missing` or `planned`. Freshness/staleness of existing
tutorial screenshots is not assessable because none exist.

### Step key

The keys below expand to exact filenames, not ranges of arbitrary files.
Combine a matrix cell's keys with its language/plan directory to identify every
page once. **M** means `missing`, capture source **none**; **P** means `planned`,
capture source the manifest IDs in the next table.

| Key | Exact leaf filename |
|---|---|
| 01 | `01-local-run.md` |
| 02 | `02-first-deploy.md` |
| 02a | `02a-first-deploy-private-egress.md` |
| 03 | `03-configuration.md` |
| 04 | `04-logging-monitoring.md` |
| 05 | `05-infrastructure-as-code.md` |
| 06 | `06-ci-cd.md` |
| 07 | `07-extending-triggers.md` |
| 08 | `08-testing-and-debugging.md` |
| 09 | `09-container-deployment.md` |

**B** expands to `01, 02, 03, 04, 05, 06, 07` (seven distinct pages).
Semicolons separate disjoint status groups, so no page is counted twice.

| Language | consumption | dedicated | flex-consumption | premium | Total |
|---|---|---|---|---|---:|
| dotnet | B: M (7) | B: M (7) | B, 02a, 08: M (9) | B, 02a, 09: M (9) | 32 |
| java | B: M (7) | B: M (7) | B, 02a, 08: M (9) | B, 02a, 09: M (9) | 32 |
| nodejs | B: M (7) | B: M (7) | B, 02a, 08: M (9) | B, 02a, 09: M (9) | 32 |
| powershell | B: M (7) | B: M (7) | B, 08: M (8) | B, 09: M (8) | 30 |
| python | B: M (7) | B: M (7) | B: P (7); 02a, 08: M (2) | B, 02a, 09: M (9) | 32 |
| **Total** | **35** | **35** | **44** | **44** | **158** |

Python Flex `02a` is a separate gap, not covered by the public first-deploy
entries. The other non-PowerShell languages also have `02a` in Flex and Premium;
PowerShell has neither. There is no Premium `08` page in this snapshot.

### Existing planned capture sources

All **14 entries** have `status: planned`, no `captured`/`verified` dates, and no
corresponding files under `docs/assets/`. They cover only Python Flex steps 01–07.
IDs below are identifiers, **not macro calls or image links**. The unchanged
[manifest](https://github.com/yeongseon/azure-functions-practical-guide/blob/e1c409ee42d179d65ff0033295d998dc96fb1953/scripts/capture/manifest.yaml)
and [capture plan](https://github.com/yeongseon/azure-functions-practical-guide/blob/e1c409ee42d179d65ff0033295d998dc96fb1953/scripts/capture/plans/python-flex-consumption.md)
give the target paths and intended scenes.

| Python / flex-consumption step | Capture source: exact manifest IDs | Entries |
|---|---|---:|
| 01 | `py-flex-01-core-tools-local-start` | 1 |
| 02 | `py-flex-02-function-app-overview-running`, `py-flex-02-functions-list`, `py-flex-02-deployment-storage-container` | 3 |
| 03 | `py-flex-03-environment-variables`, `py-flex-03-identity-system-assigned` | 2 |
| 04 | `py-flex-04-app-insights-logs-requests`, `py-flex-04-live-metrics`, `py-flex-04-transaction-search-exception` | 3 |
| 05 | `py-flex-05-deployment-history` | 1 |
| 06 | `py-flex-06-github-actions-run`, `py-flex-06-deployment-center` | 2 |
| 07 | `py-flex-07-functions-list-multi-trigger`, `py-flex-07-event-grid-subscription` | 2 |

Scene reconciliation is still needed: `py-flex-03-identity-system-assigned`
targets the System assigned tab, while the current step 03 configures a
user-assigned host-storage identity. Retain the entry as `planned` in this census,
but exclude it from a capture batch until its intended scene and caption have
been reconciled with the tutorial; its presence is not evidence of suitability.

## Owned Assets and Generic Reuse

There are **29 files** under `docs/assets/`: **27 PNGs** (23 operations, four
first-10-minutes) and two branding SVGs (`favicon.svg`, `logo.svg`). **24 distinct
PNGs** are referenced by Markdown images across `docs/`, in **158 distinct
page/asset pairs** (also 158 image occurrences pointing to existing assets).
The two illustrative `assets/example.png` occurrences in the content contract
are excluded: they are fenced examples, not owned files. No tutorial uses any
of these PNGs. Three owned PNGs are unreferenced by Markdown images:
`operations/certificates/01-certificates.png`,
`operations/custom-domains/01-custom-domains.png`, and
`troubleshooting/first-10-minutes/04-metrics.png` (paths relative to `docs/assets/`).

The table lists **every** referenced asset; counts are distinct Markdown pages,
not evidence of suitability, independent captures, or current Portal accuracy.
Paths are relative to `docs/assets/`; existing generic captures have no manifest IDs.

| Existing image path | Pages |
|---|---:|
| `operations/monitoring/02-log-stream.png` | 30 |
| `operations/configuration/01-environment-variables.png` | 20 |
| `operations/monitoring/01-metrics-explorer.png` | 18 |
| `operations/hosting/01-app-service-plan.png` | 13 |
| `operations/overview/01-function-app-overview.png` | 9 |
| `operations/networking/01-networking.png` | 8 |
| `operations/scaling/01-scale-out.png` | 8 |
| `operations/configuration/02-general-settings.png` | 7 |
| `operations/deployment/01-deployment-center.png` | 7 |
| `operations/monitoring/03-diagnose-and-solve.png` | 7 |
| `operations/security/01-identity.png` | 6 |
| `operations/access-control/01-access-control-iam.png` | 5 |
| `operations/application-insights/01-application-insights.png` | 3 |
| `operations/activity-log/01-activity-log.png` | 2 |
| `operations/app-keys/01-app-keys.png` | 2 |
| `operations/authentication/01-authentication.png` | 2 |
| `operations/diagnostic-settings/01-diagnostic-settings.png` | 2 |
| `operations/durable/01-durable-functions.png` | 2 |
| `operations/logs/01-logs.png` | 2 |
| `operations/cors/01-cors.png` | 1 |
| `operations/deployment-slots/01-deployment-slots.png` | 1 |
| `troubleshooting/first-10-minutes/01-overview.png` | 1 |
| `troubleshooting/first-10-minutes/02-log-stream.png` | 1 |
| `troubleshooting/first-10-minutes/03-diagnose-and-solve.png` | 1 |

See the [generic screenshot reuse audit](#generic-screenshot-reuse-audit)
for the semantic review owned by [#113](https://github.com/yeongseon/azure-functions-practical-guide/issues/113)
and its audit child [#385](https://github.com/yeongseon/azure-functions-practical-guide/issues/385).
Counts alone do not establish that an image shows a page's plan-specific failure state.

## Next Small Batches

Existing first-deployment children retain ownership; do not create replacements:

| Existing child | Exact page relative to `docs/language-guides/` | Capture-source reconciliation |
|---|---|---|
| [#227](https://github.com/yeongseon/azure-functions-practical-guide/issues/227) | `python/tutorial/flex-consumption/02-first-deploy.md` | Reuse the three planned step-02 IDs above; `02a` is outside this batch |
| [#228](https://github.com/yeongseon/azure-functions-practical-guide/issues/228) | `nodejs/tutorial/flex-consumption/02-first-deploy.md` | None registered; proposed ID `node-flex-02-function-app-overview-running` |
| [#229](https://github.com/yeongseon/azure-functions-practical-guide/issues/229) | `java/tutorial/premium/02-first-deploy.md` | None registered; proposed ID `java-premium-02-function-app-overview-running` |
| [#230](https://github.com/yeongseon/azure-functions-practical-guide/issues/230) | `dotnet/tutorial/premium/02-first-deploy.md` | None registered; proposed ID `dotnet-premium-02-function-app-overview-running` |

### Proposed child issues (not created)

These are candidates for the maintainer, not approved work or manifest additions.
Each is one plan and one tutorial step, after reconciling its language tracker
and existing first-deploy child. IDs not already in the manifest are proposals only.

| Candidate / tracker | Exact page relative to `docs/language-guides/` | Bounded scene and exact IDs |
|---|---|---|
| Python Flex configuration / [#109](https://github.com/yeongseon/azure-functions-practical-guide/issues/109), after #227 | `python/tutorial/flex-consumption/03-configuration.md` | Environment variables only: existing `py-flex-03-environment-variables`; exclude `py-flex-03-identity-system-assigned` pending scene reconciliation |
| Node.js Flex configuration / [#110](https://github.com/yeongseon/azure-functions-practical-guide/issues/110), after #228 | `nodejs/tutorial/flex-consumption/03-configuration.md` | Environment variables: proposed `node-flex-03-environment-variables` |
| Java Premium configuration / [#111](https://github.com/yeongseon/azure-functions-practical-guide/issues/111), after #229 | `java/tutorial/premium/03-configuration.md` | Environment variables: proposed `java-premium-03-environment-variables` |
| .NET Premium configuration / [#112](https://github.com/yeongseon/azure-functions-practical-guide/issues/112), after #230 | `dotnet/tutorial/premium/03-configuration.md` | Environment variables: proposed `dotnet-premium-03-environment-variables` |
| PowerShell Consumption first deployment / [#108](https://github.com/yeongseon/azure-functions-practical-guide/issues/108) | `powershell/tutorial/consumption/02-first-deploy.md` | App Overview: proposed `ps-consumption-02-function-app-overview-running`; no PowerShell child among #227–#230 |

Portal batches require an authorized environment and human-signed-in compliant
browser; no access, deployment or capture is authorized by this list. Follow the
[capture pipeline and final-byte privacy review](content-contract.md#image-and-screenshot-rules)
and [caption/evidence pattern](content-contract.md#screenshot-evidence-pattern).
Do not insert a screenshot macro until the image exists. No new issues, images,
manifest entries/statuses or capture plans were changed by this inventory.

## Reproduce at Another SHA

Use a clean detached checkout of the desired SHA, install `requirements-docs.txt`,
and run the following from that checkout's root with Python 3.11. Record the SHA
separately (`git rev-parse HEAD`). This read-only snippet prints every page's
image/macro counts, exact grouped filenames, manifest status/file existence,
owned files, and asset-to-distinct-page mapping. It does not assign verification
status: reconcile manifest IDs to steps using the capture plans, then apply the
status definitions above. New naming schemes need a new mapping, not a guessed
ID-prefix match.

```python
from collections import Counter, defaultdict
from pathlib import Path
import re
import yaml

root = Path.cwd()
assets = root / "docs/assets"
image = re.compile(r"\x21\[[^\]]*\]\(<?([^\s)>]+)")
shot = re.compile(r"\bshot\(\s*['\"]([^'\"]+)['\"]")
pages = sorted(Path("docs/language-guides").glob("*/tutorial/*/[0-9]*.md"))
leaves = {p for p in Path("docs/language-guides").glob("*/tutorial/*/*.md")
          if p.name != "index.md"}
assert len(pages) == len(set(pages)) and set(pages) == leaves
groups = defaultdict(list)
for p in pages:
    text = p.read_text()
    groups[(p.parts[2], p.parts[4])].append(p.name)
    print(p, "images", len(image.findall(text)), "macros", len(shot.findall(text)))
print("tutorials", len(pages), "groups", dict(groups))
entries = yaml.safe_load(Path("scripts/capture/manifest.yaml").read_text())["screenshots"]
print("manifest", len(entries), Counter(e.get("status") for e in entries))
for e in entries:
    print(e["id"], e.get("status"), e.get("captured"), e.get("verified"),
          "file exists", (assets / e["file"]).is_file())
uses = defaultdict(set)
for p in sorted(Path("docs").rglob("*.md")):
    for ref in image.findall(p.read_text()):
        target = (p.parent / ref.split("#")[0]).resolve()
        if target.is_file() and target.is_relative_to(assets):
            uses[str(target.relative_to(assets))].add(str(p))
owned = sorted(str(p.relative_to(assets)) for p in assets.rglob("*") if p.is_file())
print("owned", len(owned), owned)
print("referenced", len(uses), "page/asset pairs", sum(map(len, uses.values())))
for target, users in sorted(uses.items()):
    print(target, len(users), sorted(users))
```

The image query counts literal inline Markdown image syntax, including fenced
examples, but only existing owned targets enter the reuse totals. Macro counts
are literal calls (including examples), not rendered coverage. At this SHA the
only Markdown-image examples outside real assets are the two excluded contract
examples; no tutorial has either syntax. HTML/remote/reference-style images and
theme branding are not Markdown screenshot coverage. Recheck these assumptions
when refreshing the snapshot.

This inventory does **not** establish image authenticity, UI freshness, PII safety,
caption correctness, completeness of the proposed scenes, Azure tutorial success,
or independent reproduction. Azure/Portal execution: **NOT_RUN**. Screenshot
verification: **not performed**; no existing asset is promoted to `verified`.

## Generic Screenshot Reuse Audit

**2026-11-04 · main SHA `d95fcb0d3e3b2b7fb4dae8e603471f62e75ce8f9`.**
This is the repository-only semantic audit for #385 under #113, not a capture
batch. Re-running the query below at this SHA reproduces the
[existing refcount table](#owned-assets-and-generic-reuse): **29 owned assets,
24 referenced PNGs, 158 page/asset pairs**. The **12 high-reuse PNGs** (at least
five distinct pages each) account for **138 pairs**; the other 12 account for
20. Tutorial use is **zero for every audited image**. Best Practices, Start Here
and first-response pages are included below rather than silently folded into
Operations or playbooks.

### Reading the findings

All twelve PNGs were opened and compared with their referring pages' alt text
and nearby walkthrough prose. The classifications are **editorial AI-reviewer
judgements**, not human visual approval, an authenticity/privacy certification,
current Portal validation, or Azure evidence. Azure/Portal execution: **NOT_RUN**.
No image is declared verified or PII-safe. The earlier census's verification
limits still apply; this section adds semantic inspection, not capture provenance.

| Classification | Meaning for the current usage |
|---|---|
| **ACCEPTABLE-NEUTRAL (A)** | A blade locator or explicitly limited example; the task can use it without treating its state as the reader's evidence. This includes explicitly scoped Y1 comparisons, not a claim that every control is plan-independent. |
| **CONTEXT-MISMATCH (C)** | The page's plan, OS, identity/configuration model or required state differs from the capture. A Y1 disclosure identifies the source but does not make it an FC1/EP1 scene. |
| **MISLEADING (M)** | Alt text or nearby observation implies visible traces, charts, assignments or a conclusion the pixels do not establish. This is a risk in presentation, not an accusation that the underlying experiment was fabricated. |

Each table partitions **every referring page once**. Where both C and M apply,
the row records one primary classification and explains the additional defect.
Paths in the page column are **relative to the named `docs/<section>/` directory**;
each filename is exact, with no implied glob/range. Counts are page/asset pairs,
not distinct pages across the whole audit. `A`, `C`, `M` expand to the full names
above.

**Caption-pattern debt:** none of these 138 nearby image explanations supplies
the complete labeled **Purpose / Look for / Expected result / Next step** block.
Some provide equivalent intent through `[Observed]` / `[Inferred]` prose; others
are just a heading, introduction and image list. Thus A is semantic acceptability,
not full content-contract compliance. In each finding, distinguish **what is
shown** from **what the reader must collect next**. Preserve page-specific
diagnostic purpose, expected condition and next action when correcting captions;
never turn an instruction to collect evidence into a claimed observation.

**Manifest reconciliation:** all twelve existing PNGs have **no current manifest
ID**. The 14 manifest entries are planned Python Flex scenes with no image bytes,
not IDs for these generic files. Relevant planned alternatives are named below
only for their exact tutorial scenes. They are not replacements for lab evidence
and must not be referenced as images before authorized capture. The
[existing first-deployment children](#next-small-batches) #227–#230 keep ownership;
this audit adds no competing capture issue, status or plan.

### Log Stream — 30 pages

File: `operations/monitoring/02-log-stream.png` (under `docs/assets/`).
**Shows:** a Function App Log stream blade, toolbar and black console containing
only **Connected!**; no startup, invocation, error, retry or recovery lines.
Plan and OS are not visible; the referring walkthroughs describe its source as
Consumption Y1. The console locator is scenario-independent; its empty state is
not proof that an app is healthy, idle, processing, failing or recovered.
Current manifest ID: **none**. No planned Log Stream equivalent exists;
`py-flex-04-app-insights-logs-requests` is a different, planned KQL scene, not a
drop-in replacement.

| Section / exact pages | Count | Class | Alt/prose match and diagnostic-purpose finding |
|---|---:|---|---|
| operations: `monitoring.md` | 1 | A | Alt correctly says Connected/dark console. Prose describes where future output appears; connection alone must not be used to confirm processing. |
| operations: `retries-and-poison-handling.md`; platform: `reliability.md` | 2 | M | Alt says “showing real-time function logs” and nearby observations name retries/errors, but no such lines appear. Preserve retry investigation; label this as a locator, not a retry observation. |
| reference: `troubleshooting.md` | 1 | A | “for real-time error diagnosis” is a purpose, not a displayed error. Needs the missing caption block and an explicit empty-console limit. |
| troubleshooting/first-10-minutes: `high-latency.md`, `triggers-not-firing.md` | 2 | M | Observations say execution output or startup/listener initialization is shown. Neither is visible. The instruction to look for timeouts/binding errors remains useful, but is not evidence in this image. |
| troubleshooting/lab-guides: `code-storage-verification.md`, `cold-start.md`, `deployment-not-running.md`, `dns-vnet-resolution.md`, `durable-replay-storm.md`, `event-hub-checkpoint-lag.md`, `managed-identity-auth.md`, `out-of-memory-crash.md`, `queue-backlog-scaling.md`, `storage-access-failure.md`, `timer-missed-schedules.md` | 11 | M | Alts promise storage/startup/deployment/DNS/replay/checkpoint/auth/crash/processing/timer traces; the console contains none. Additional C: FC1 focus in cold-start, DNS, identity and storage labs; EP1/Linux in replay, checkpoint and OOM labs. Y1/multi-plan labs still lack the promised incident output. |
| troubleshooting/playbooks: `auth-config/app-settings-misconfiguration.md`, `auth-config/managed-identity-rbac-failure.md`, `blob-trigger-not-firing.md`, `deployment-failures.md`, `flex-consumption-deployment.md`, `functions-failing.md`, `functions-not-executing.md`, `high-latency.md`, `queue-piling-up.md`, `scaling/durable-orchestration-stuck.md`, `scaling/out-of-memory-worker-crash.md`, `triggers/event-hub-service-bus-lag.md`, `triggers/timeout-execution-limit.md` | 13 | M | Trace/error-specific alts without an empty-state disclaimer invite reading this as incident evidence. `deployment-failures.md` already disclaims Flex/new-run evidence but still has an error-specific alt; Flex-specific deployment also has a Y1/FC1 context mismatch. |

**Precise replacement reason:** only a usage that must show diagnostic output
needs different bytes. Use the page's actual plan/OS (FC1/Linux, EP1/Linux or
the declared Y1 environment), the supported logging surface, and retained,
sanitized lines for the specific failure or baseline/recovery interval. Do not
reuse Connected as an error or successful recovery. A truthful locator caption
can avoid recapture where no visible incident is required.

### Environment variables — 20 pages

File: `operations/configuration/01-environment-variables.png`.
**Shows:** Function App Environment variables, App settings tab, four setting
names, hidden values, an empty slot-setting column and editing controls. The
names include host storage, runtime and legacy monitoring settings. No value,
identity-based connection correctness or error state is visible. Plan/OS are not
displayed; source prose says Y1. The blade locator is generic, the four-setting
configuration is not a universal baseline. Current manifest ID: **none**.
`py-flex-03-environment-variables` is planned for Python Flex step 03 with that
tutorial's settings, not for these incident pages.

| Section / exact pages | Count | Class | Alt/prose match and diagnostic-purpose finding |
|---|---:|---|---|
| operations: `configuration.md`, `cost-optimization.md`, `security.md` | 3 | A | Names/hidden-value descriptions match; review of sampling/secrets is an action, not a visible result. Hidden values cannot establish safe secret storage. |
| platform: `security.md`, `triggers-and-bindings.md` | 2 | A | Matches the legacy setting list; prose distinguishes alternate identity-based names. It does not show a binding connection test. |
| reference: `troubleshooting.md`; troubleshooting/first-10-minutes: `triggers-not-firing.md` | 2 | A | Generic configuration locator. First-response prose says connection strings are shown, but only names/hidden-value controls are visible; qualify that wording, not the inferred correctness of values. |
| troubleshooting/lab-guides: `code-storage-verification.md`, `deployment-not-running.md`, `timer-missed-schedules.md` | 3 | A | Explicit Y1 example is usable as orientation for Y1 portions; not a complete multi-plan storage matrix or the faulted runtime/timer setting. |
| troubleshooting/lab-guides: `dns-vnet-resolution.md`, `managed-identity-auth.md`, `storage-access-failure.md` | 3 | C | FC1 scenarios use a Y1 list without their identity-based storage/private-network configuration. “Showing AzureWebJobsStorage” is literally true in the storage lab, but does not show its FC1 auth variants. |
| troubleshooting/playbooks: `auth-config/app-settings-misconfiguration.md`, `auth-config/managed-identity-rbac-failure.md`, `blob-trigger-not-firing.md`, `deployment-failures.md`, `functions-not-executing.md`, `triggers/event-hub-service-bus-lag.md` | 6 | A | Neutral blade labels and explicit Y1 source are suitable locators, not evidence that a specific missing setting exists. Deployment-failures already distinguishes Flex. |
| troubleshooting/playbooks: `flex-consumption-deployment.md` | 1 | C | FC1 deployment diagnosis paired with the Y1 runtime/storage list; source disclosure alone does not demonstrate the Flex configuration under investigation. |

**Precise replacement reason:** a scene-dependent usage needs the declared
plan/OS and actual setting **names** for its auth/runtime variant, values hidden,
with baseline versus missing/misconfigured state labeled. For FC1/Linux, do not
present the legacy four-setting list as the required deployment-storage model.
A general locator needs a disclosure, not a new screenshot of secret values.

### Metrics Explorer — 18 pages

File: `operations/monitoring/01-metrics-explorer.png`.
**Shows:** Function App Metrics with Add metric, **Not configured**, blank chart
and a last-24-hours selector. No selected metric, measured series, latency,
memory, lag or failure rate. Plan/OS absent; Y1 attribution comes from page prose.
Scenario-independent as a chart-builder locator only. Current manifest ID:
**none**. Planned `py-flex-04-live-metrics` is an Application Insights Live
Metrics traffic scene, not this Azure Monitor chart; neither it nor the planned
KQL request scene supplies existing lab measurements.

| Section / exact pages | Count | Class | Alt/prose match and diagnostic-purpose finding |
|---|---:|---|---|
| operations: `monitoring.md` | 1 | A | Alt says empty chart/selector; prose explains Not configured and selecting a metric. Good neutral example to retain. |
| operations: `alerts.md` | 1 | M | Alt says “showing Function App metric charts”; no metric is selected. Baseline/threshold analysis must occur after chart configuration, not be inferred here. |
| platform: `reliability.md`, `scaling.md` | 2 | A | “for monitoring” labels and instructions to select/observe metrics are locator uses, not captured trends. Make the blank state explicit. |
| troubleshooting/first-10-minutes: `high-latency.md`, `scaling-issues.md` | 2 | A | Instructions describe charting/comparing data, not a measured value in the screenshot. Still missing metric/aggregation/time-window captions. |
| troubleshooting/lab-guides: `cold-start.md`, `durable-replay-storm.md`, `event-hub-checkpoint-lag.md`, `out-of-memory-crash.md` | 4 | C | FC1-focused cold-start and EP1/Linux replay/checkpoint/OOM analyses reuse an unconfigured Y1-attributed chart. It cannot show those labs' time windows or measured signals. |
| troubleshooting/lab-guides: `queue-backlog-scaling.md` | 1 | A | Y1 execution-rate-analysis locator only; no throughput/backlog correlation is visible. |
| troubleshooting/playbooks: `functions-failing.md`, `high-latency.md`, `queue-piling-up.md`, `scaling/durable-orchestration-stuck.md`, `scaling/out-of-memory-worker-crash.md`, `triggers/event-hub-service-bus-lag.md`, `triggers/timeout-execution-limit.md` | 7 | A | “for … analysis” or neutral alts identify a tool, not an observed chart. Add explicit Not configured disclosure and the page's metric selection/expected comparison. |

**Precise replacement reason:** if a chart is needed as evidence, capture the
correct resource/plan/OS and selected metric, aggregation, time window and
baseline/incident/recovery series for that page. A blank chart cannot prove
memory pressure, latency or checkpoint lag. Do not substitute Live Metrics for
a platform-metric chart without changing the purpose honestly.

### App Service plan — 13 pages

File: `operations/hosting/01-app-service-plan.png`.
**Shows:** a Function App's App Service plan blade with **Y1**, **Linux**,
Instance Count **0**, apps/slots **1/0**, zone redundancy disabled. A resource
name is visible. This is a specific Consumption plan configuration, not an
instance-history chart, bill or all-plan example. Current manifest ID: **none**;
no planned equivalent of this blade. For Python Flex first-deploy orientation,
`py-flex-02-function-app-overview-running` instead plans an FC1/Linux Overview.

| Section / exact pages | Count | Class | Alt/prose match and diagnostic-purpose finding |
|---|---:|---|---|
| best-practices: `cost-optimization.md`; operations: `cost-optimization.md` | 2 | M | Fields match, but nearby inference converts a displayed count into idle/zero-cost confirmation. This still image cannot establish execution history or the bill. |
| platform: `functions-vs-app-service.md`, `hosting.md`; start-here: `overview.md` | 3 | M | Accurate Y1/zero field descriptions are extended to scale-to-zero behavior; distinguish configuration display from proof of observed scaling. |
| start-here: `hosting-options.md` | 1 | M | Y1 example is identified, but paired prose generalizes its scale-out maximum; this blade shows no maximum. |
| troubleshooting/first-10-minutes: `high-latency.md`, `scaling-issues.md`; troubleshooting/playbooks: `high-latency.md`, `scaling/out-of-memory-worker-crash.md` | 4 | A | Plan-type locator, with Y1 attribution; not a latency or crash measurement. Do not imply the pictured tier is EP1/FC1. |
| troubleshooting/lab-guides: `cold-start.md`, `out-of-memory-crash.md` | 2 | C | Y1/Linux does not represent the FC1-focused cold-start scene or EP1/Linux OOM environment. Cold-start includes Y1 comparison, but this is not its primary FC1 evidence. |
| troubleshooting/lab-guides: `timer-missed-schedules.md` | 1 | A | Matches the declared Y1 context as plan orientation, not a stopped-app or catch-up observation. |

**Precise replacement reason:** show the page's declared plan and OS on the
appropriate plan/Overview blade; use FC1/Linux or EP1/Linux when that is the
scenario. A scaling/cost conclusion also needs actual time-series/billing
evidence; replacing a static plan card cannot establish it.

### Function App Overview — 9 pages

File: `operations/overview/01-function-app-overview.png`.
**Shows:** Function App Overview, Running status, **Linux**, a **Y1** plan link,
runtime version, migration banner and two enabled HTTP-triggered function rows.
Resource/subscription-name and domain fields are visible. It is an app-specific
snapshot; enabled/running is not proof of successful invocations or recovery.
Current manifest ID: **none**. Planned
`py-flex-02-function-app-overview-running` targets Python Flex step 02,
FC1/Linux/Python 3.11; `py-flex-07-functions-list-multi-trigger` targets a
different, multi-trigger Functions scene, not the two HTTP rows here.

| Section / exact pages | Count | Class | Alt/prose match and diagnostic-purpose finding |
|---|---:|---|---|
| best-practices: `trigger-and-binding.md`; operations: `recovery.md`; platform: `deployment-scenarios.md`, `functions-vs-app-service.md`, `triggers-and-bindings.md` | 5 | A | Function-list/status/runtime and toolbar descriptions match a Y1/Linux example. Recovery instructs post-rollback checks; it does not show a rollback or prove processing. |
| best-practices: `reliability.md`; operations: `cold-start.md`; platform: `hosting.md`; start-here: `overview.md` | 4 | M | Visible Y1/zero text is used to infer always-on/idle scaling or cold-start behavior. Preserve plan orientation, but label these conclusions as not established by this capture. |

**Precise replacement reason:** when used for a specific deployment, show its
plan/OS, runtime, functions and required status; FC1 is not interchangeable with
this Y1/Linux example. For recovery/startup behavior, collect the actual
invocation/timeline evidence as well, not merely another Running screenshot.

### Networking — 8 pages

File: `operations/networking/01-networking.png`.
**Shows:** Function App Networking; public access enabled without restrictions,
dynamic addresses, private endpoints/VNet integration/hybrid connections **Not
supported**, default outbound DNS and N/A integration-subnet features. Plan/OS
are not explicitly displayed; the unsupported feature set and page attribution
indicate the legacy Y1 context, not a configured FC1 private network. Current
manifest ID: **none**; no planned Networking alternative.

| Section / exact pages | Count | Class | Alt/prose match and diagnostic-purpose finding |
|---|---:|---|---|
| best-practices: `networking.md`; platform: `networking.md`, `networking-scenarios/public-only.md` | 3 | A | Explicit Y1/public-only comparison matches the shown feature availability. Not proof of a private path. |
| platform: `networking-scenarios/fixed-outbound-nat.md`, `networking-scenarios/private-egress.md`, `networking-scenarios/private-ingress.md` | 3 | C | “Baseline before” wording suggests these are configurable precursors to the scenario, but Not supported is a different plan, not an unconfigured supported feature. Nearby text names Y1; retain as a contrast only if explicitly labeled as such. |
| troubleshooting/lab-guides: `dns-vnet-resolution.md` | 1 | C | FC1/private-DNS lab uses a blade that cannot show its VNet/private-endpoint setup or broken DNS link. |
| troubleshooting/playbooks: `blob-trigger-not-firing.md` | 1 | A | Neutral Networking locator with Y1 source disclosure, not an observed blocked path. |

**Precise replacement reason:** for a real private/NAT scene, use the page's
chosen supported plan/OS and show configured VNet/subnet, inbound private
endpoint or NAT association as applicable; a DNS failure also needs the actual
zone-link/resolution state. No unsupported-to-enabled transition can be inferred
from this Y1 card. Keep neutral public-only orientation rather than recapturing it.

### Scale out — 8 pages

File: `operations/scaling/01-scale-out.png`.
**Shows:** Function App Dynamic Scale out, explanatory Consumption text,
Enforce Scale Out Limit **Yes**, displayed limit **200**. No measured instances,
backlog or autoscale event. OS is absent; the source is attributed to Y1 in the
pages, with Linux visible in the companion plan capture. The control is not
plan-independent and the displayed value is not proof of a platform ceiling.
Current manifest ID: **none**; no planned Scale out equivalent.

| Section / exact pages | Count | Class | Alt/prose match and diagnostic-purpose finding |
|---|---:|---|---|
| best-practices: `cost-optimization.md`, `scaling.md`; platform: `scaling.md`; start-here: `hosting-options.md`; troubleshooting/first-10-minutes: `scaling-issues.md` | 5 | M | Alts match the displayed 200, but prose presents it as a default/general Consumption maximum rather than this control's value. The existing qualification in `platform/hosting.md` already distinguishes captured settings from OS-specific limits; these usages need equivalent precision. |
| troubleshooting/lab-guides: `event-hub-checkpoint-lag.md` | 1 | C | EP1/Linux experiment needs Premium scaling controls, not this Consumption slider. |
| troubleshooting/lab-guides: `queue-backlog-scaling.md`; troubleshooting/playbooks: `queue-piling-up.md` | 2 | A | Y1 cap locator matches; it does not demonstrate that scaling occurred, explain a drain rate, or prove a service maximum. |

**Precise replacement reason:** a cap example must match plan/OS and show the
actual configured cap, explicitly separated from the documented service limit.
EP1 needs its elastic-instance controls; FC1 needs its own scale controls.
Scaling outcomes require corresponding instance/backlog telemetry, not a slider.

### General settings — 7 pages

File: `operations/configuration/02-general-settings.png`.
**Shows:** Function App Configuration, General settings tab; HTTP 2.0,
HTTPS-only unchecked, inbound/SCM TLS 1.2, remote debugging unchecked, client
certificate mode Ignore, plus other platform controls. **No FTPS field is
visible**, and no function timeout/retry value is displayed. Plan/OS absent;
page attribution is Y1. Some controls are generic locators, not proof of a
universal plan baseline or secure deployment. Current manifest ID: **none**;
no planned General settings equivalent.

| Section / exact pages | Count | Class | Alt/prose match and diagnostic-purpose finding |
|---|---:|---|---|
| operations: `configuration.md`, `security.md`; platform: `deployment-scenarios.md` | 3 | M | Captions/prose include FTPS state as shown; this frame does not display it. HTTP/TLS/HTTPS descriptions otherwise match. Do not report the pictured HTTPS-only state as hardened. |
| operations: `retries-and-poison-handling.md` | 1 | M | Generic alt is accurate, but adjacent runtime/timeout discussion risks implying retry/timeout configuration is visible here. It is not; keep the distinction from host.json/runtime policy. |
| platform: `networking.md`; troubleshooting/playbooks: `auth-config/app-settings-misconfiguration.md`, `triggers/timeout-execution-limit.md` | 3 | A | TLS/platform-config locators match visible controls; not a captured misconfiguration or execution-time-limit result. |

**Precise replacement reason:** if FTPS, runtime timeout or a hardening result
is the purpose, show the correct plan/OS and the actual blade/field/state, not
an off-frame setting. A transport-settings locator may retain this image with
accurate text and explicit “not the target hardened state” wording.

### Deployment Center — 7 pages

File: `operations/deployment/01-deployment-center.png`.
**Shows:** Function App Deployment Center Settings, unselected source dropdown
and production-slot advisory; no provider connection, deployment history,
failed build or successful rollout. Plan/OS absent; Y1 source attributed by
pages. Current manifest ID: **none**. Planned `py-flex-06-deployment-center`
requires a GitHub source and successful log entry for Python Flex step 06,
neither present here. Its intended scene must be reconciled with supported Flex
deployment surfaces before capture; a planned entry is not validation.

| Section / exact pages | Count | Class | Alt/prose match and diagnostic-purpose finding |
|---|---:|---|---|
| best-practices: `deployment.md`; operations: `deployment.md`, `recovery.md`; platform: `deployment-scenarios.md` | 4 | A | Source-selection labels match. Advisory text does not prove slot support or a configured rollback pipeline; platform deployment-scenarios explicitly distinguishes Flex. |
| troubleshooting/lab-guides: `deployment-not-running.md`; troubleshooting/playbooks: `deployment-failures.md` | 2 | A | Neutral blade locator for the declared Y1 context; not proof of transport success, indexing failure or recovery. Deployment-failures explicitly disclaims Flex evidence. |
| troubleshooting/playbooks: `flex-consumption-deployment.md` | 1 | C | FC1-specific failure investigation uses a legacy source-selection scene, not its deployment-storage/auth or Flex diagnostic state. |

**Precise replacement reason:** show the actual plan/OS and deployment method,
with provider/history/result only when retained evidence supports it. An FC1
failure needs its supported deployment diagnostic/configuration surface and
the particular failed state, not the unconfigured legacy selector.

### Diagnose and solve problems — 7 pages

File: `operations/monitoring/03-diagnose-and-solve.png`.
**Shows:** Function App diagnostics landing page, five category cards and one
Availability warning. No opened detector, incident diagnosis or root cause.
Plan/OS absent; Y1 attribution is contextual. Scenario-independent as navigation,
not as a detector verdict. Current manifest ID: **none**; no planned equivalent.

| Section / exact pages | Count | Class | Alt/prose match and diagnostic-purpose finding |
|---|---:|---|---|
| operations: `alerts.md`, `monitoring.md` | 2 | A | Generic blade labels/category and warning descriptions match. The warning is not evidence of the reader's alert cause. |
| platform: `reliability.md`; reference: `troubleshooting.md` | 2 | A | First-response locator, not a captured reliability diagnosis. |
| troubleshooting/first-10-minutes: `triggers-not-firing.md`; troubleshooting/playbooks: `functions-failing.md`, `functions-not-executing.md` | 3 | A | Correct landing-page locator; the trigger/failure hypothesis requires opening an appropriate detector and collecting its result. |

**Precise replacement reason:** no replacement is needed for navigation alone.
If the page needs a diagnosis, capture the relevant detector for its plan/OS and
actual incident window, including the warning/result detail; a generic warning
card cannot establish a trigger, deployment or availability root cause.

### Identity — 6 pages

File: `operations/security/01-identity.png`.
**Shows:** Function App Identity, **System assigned**, Status **On**, a
placeholder-looking principal-ID field and Azure role assignments button.
No role list, authorization success or failure. Plan/OS absent; source prose
attributes Y1. Identity-toggle orientation is broadly reusable; enabled is not
equivalent to authorized. Current manifest ID: **none**. Planned
`py-flex-03-identity-system-assigned` is only a scene candidate for Python Flex
step 03 and remains excluded pending the system-/user-assigned reconciliation
[already recorded above](#existing-planned-capture-sources).

| Section / exact pages | Count | Class | Alt/prose match and diagnostic-purpose finding |
|---|---:|---|---|
| best-practices: `security.md`; platform: `security.md` | 2 | A | Enabled system-assigned identity description matches. RBAC verification is a subsequent action, not demonstrated permission. |
| troubleshooting/lab-guides: `code-storage-verification.md` | 1 | A | Y1 example within multi-plan coverage; not a complete identity/storage-role matrix. |
| troubleshooting/lab-guides: `managed-identity-auth.md`, `storage-access-failure.md` | 2 | C | FC1 scenarios reuse Y1-attributed identity orientation. On does not show either lab's removed/granted storage role, or its auth variants. |
| troubleshooting/playbooks: `auth-config/managed-identity-rbac-failure.md` | 1 | A | Neutral identity-status locator; does not show the RBAC failure. |

**Precise replacement reason:** show the page's plan/OS and selected identity
type; distinguish attached/enabled identity from permissions at the target
storage scope. If failure/recovery is the purpose, the appropriate role view
and actual data-plane result are needed, not another enabled toggle.

### Access control (IAM) — 5 pages

File: `operations/access-control/01-access-control-iam.png`.
**Shows:** Function App IAM **Check access** tab with navigation/cards for
checking/granting/viewing access and deny assignments. No selected principal,
role assignment rows or Storage-account scope. Plan/OS absent; generic
navigation is reusable, actual grants are resource-specific. Current manifest
ID: **none**; no planned IAM role-list alternative.

| Section / exact pages | Count | Class | Alt/prose match and diagnostic-purpose finding |
|---|---:|---|---|
| operations: `security.md` | 1 | A | Neutral IAM locator and instructions to inspect access/deny assignments, not a shown permission result. |
| best-practices: `security.md`; platform: `security.md` | 2 | M | Tabs/cards match, but prose implies the Function App's own IAM scope proves what its identity can access elsewhere. No target-storage grant is shown. |
| troubleshooting/lab-guides: `managed-identity-auth.md`; troubleshooting/playbooks: `auth-config/managed-identity-rbac-failure.md` | 2 | M | Adjacent `[Observed]` text directs data-plane RBAC verification, while Check access for the app shows no assignments at the storage scope. Additional FC1/Y1 context mismatch in the lab. |

**Precise replacement reason:** for storage RBAC, show the target resource's
Role assignments view with the relevant identity, role and scope safely
represented, and declared plan/OS provenance; do not confuse app management
access with the app identity's data access. Keep the generic Check access image
only as navigation with that scope distinction explicit.

### First correction batch — proposed child issue (not created)

**One S-sized, text-only batch under #113:** clarify the three generic image
usages in **`docs/troubleshooting/lab-guides/storage-access-failure.md` only**.
This is a proposal, not an edit to that page or permission for Azure access.
It prioritizes a concrete FC1/Linux mismatch without bulk deletion or recapture.

| Exact affected page | Proposed change | Preserve the page-specific evidence pattern |
|---|---|---|
| `docs/troubleshooting/lab-guides/storage-access-failure.md` — Identity image | Retain historical PNG; add Y1/system-assigned orientation-only disclosure and alt describing On, not “RBAC verification”. | **Purpose:** locate identity settings. **Look for:** the identity type selected for the FC1 host-storage variant. **Expected result:** attachment/enabled state alone does not establish a grant. **Next step:** compare required host-storage roles at the target account with the lab's controlled auth variant. |
| Same page — Environment variables image | Retain PNG; disclose legacy Y1 four-setting example, hidden values and absence of FC1 variant-specific settings. Keep the NOT_RUN warning and all historical/source metadata. | **Purpose:** locate settings. **Look for:** setting names for the selected connection-string or identity-based variant, without exposing values. **Expected result:** match the lab's predeclared baseline, not this legacy list. **Next step:** collect the variant's sanitized configuration and independent network/auth controls. |
| Same page — Log Stream image | Change alt to connected empty console; disclose no storage error, listener failure or recovery is pictured. Do not stamp a new capture/validation date. | **Purpose:** locate a logging tool, not validate the FC1 experiment. **Look for:** actual retained storage/listener signals using supported FC1 telemetry. **Expected result:** this image establishes neither failure nor recovery. **Next step:** follow the lab's evidence collection/falsification procedure; missing logs are not disproof. |

Acceptance for that proposed child: all three captions retain distinct purpose,
look-for, expected-result and next-action text; no image/provenance/date changes;
strict build, rendered-caption checks and unchanged privacy/evidence gates.
Any later plan-specific capture is **BLOCKED until authorized Portal access,
retained provenance and final-byte human caption/PII review exist**. None of the
planned Python tutorial IDs supplies this lab's incident evidence. Actual capture
work remains with #108/#113 and the existing #227–#230 slices; the inventory
relationship remains [#384](https://github.com/yeongseon/azure-functions-practical-guide/issues/384).

### Reproduce the high-reuse audit mapping

At the pinned SHA, run the earlier [census snippet](#reproduce-at-another-sha)
from a clean checkout root to construct `uses` (resolved asset path → set of
distinct Markdown pages). Append this exact Python continuation to print each
high-reuse image's section counts and **every exact page path**:

```python
high = {asset: pages for asset, pages in uses.items() if len(pages) >= 5}
print("high-reuse assets", len(high), "pairs", sum(map(len, high.values())))
for asset, pages in sorted(high.items(), key=lambda item: (-len(item[1]), item[0])):
    sections = defaultdict(list)
    for page in sorted(pages):
        parts = Path(page).parts
        section = "/".join(parts[1:3]) if parts[1] == "troubleshooting" else parts[1]
        sections[section].append(page)
    assert sum(map(len, sections.values())) == len(pages)
    print(asset, "manifest ID: none at this audited SHA", "pages", len(pages))
    for section, members in sorted(sections.items()):
        print(section, len(members), members)
assert len(uses) == 24 and sum(map(len, uses.values())) == 158
assert len(high) == 12 and sum(map(len, high.values())) == 138
```

These assertions are **snapshot cross-checks**, not permanent quotas. At another
SHA, reconcile changes against the refcount table and inspect the manifest again
before changing them. The query regenerates membership/counts, **not semantic
classifications**: re-open the image bytes and read each page's alt and nearby
explanation, including plan/OS metadata and evidence disclaimers. It shares the
census's literal-inline-image scope and exclusions; it does not discover remote,
HTML/reference-style images or establish authenticity from file names.

### Identifier concerns and remaining limits

Resource names are visible in all twelve audited images. In particular, account,
subscription-name, domain or directory/header text merits maintainer privacy
follow-up in the files below. Values are intentionally not transcribed; their
presence is not a determination that a real identifier leaked. Placeholder-looking
fields do not establish that every pixel is safe.

- `docs/assets/operations/overview/01-function-app-overview.png`
- `docs/assets/operations/hosting/01-app-service-plan.png`
- `docs/assets/operations/networking/01-networking.png`
- `docs/assets/operations/scaling/01-scale-out.png`
- `docs/assets/operations/deployment/01-deployment-center.png`
- `docs/assets/operations/security/01-identity.png`
- `docs/assets/operations/access-control/01-access-control-iam.png`

No bytes, historical captures, PII/source metadata, manifest/status/plan or other
pages were changed. The audit does not establish that the referenced experiments
ran, that old captures are fresh, that any scenario is independently reproduced,
or that historical privacy debt is resolved. Human review remains necessary
under the [image rules](content-contract.md#image-and-screenshot-rules),
[screenshot evidence pattern](content-contract.md#screenshot-evidence-pattern)
and [PII quality gate](content-contract.md#pii-removal-quality-gate).

## See Also

- [Contributing](index.md)
- [Image and Screenshot Rules](content-contract.md#image-and-screenshot-rules)
- [Tutorial Validation Dashboard](../reference/validation-status.md) — a separate execution-history axis
- [Screenshot tracker #108](https://github.com/yeongseon/azure-functions-practical-guide/issues/108) — language trackers and capture ownership
