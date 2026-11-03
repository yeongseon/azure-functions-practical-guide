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

Semantic reuse review belongs to [#113](https://github.com/yeongseon/azure-functions-practical-guide/issues/113)
and its audit child [#385](https://github.com/yeongseon/azure-functions-practical-guide/issues/385),
not this census. For example, the storage-access-failure lab references generic
identity, environment-variable and Log Stream images; counts alone do not
establish that those images show its plan-specific failure state.

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
| Python Flex configuration / [#109](https://github.com/yeongseon/azure-functions-practical-guide/issues/109), after #227 | `python/tutorial/flex-consumption/03-configuration.md` | Environment variables and system identity: existing `py-flex-03-environment-variables`, `py-flex-03-identity-system-assigned` |
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

## See Also

- [Contributing](index.md)
- [Image and Screenshot Rules](content-contract.md#image-and-screenshot-rules)
- [Tutorial Validation Dashboard](../reference/validation-status.md) — a separate execution-history axis
- [Screenshot tracker #108](https://github.com/yeongseon/azure-functions-practical-guide/issues/108) — language trackers and capture ownership
