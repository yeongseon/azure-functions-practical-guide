---
title: Diagram Inventory and Migration Manifest
description: Functions diagram baseline, exclusions, ownership and path-derived hosting and trigger migration candidates.
---

# Diagram Inventory and Migration Manifest

This reference inventories the repository for #210 under umbrella #209. It records source facts and migration ownership, not rendered correctness, verified provenance or completed migration.

## Purpose and Scope

The [manifest](diagram-manifest.json) and [schema](diagram-manifest.schema.json) record the Mermaid occurrences that the scanner finds in tracked Markdown, including repository-only lab sources, and the tracked drawing and image assets it classifies by path; fences it cannot place are recorded as findings, and corrupted fence syntax remains a documented limitation. The [ADR](adr-diagram-composition.md) compares reuse options and defers composition to the shared App Service prototype #283.

Each diagram has a unique `<page>#<diagram-id>` key, or provisional ordinal when an ID is absent, source line/heading and body hash, declared metadata, an owning batch or exclusion, and a provisional target record. Targets intentionally remain null/empty until #211 adopts a composition interface; no approved base/extension vocabulary is invented by this baseline. Every migration-required entry has an owner; nothing has been converted.

## Counting Policy

Every Mermaid fence in a tracked Markdown file is one occurrence. Repeated text still counts separately. An asset referenced repeatedly is one asset with multiple usages. Published means under `docs/`, not that its semantics or render was verified.

Non-Mermaid visuals are reported separately; `totals.by_batch` counts Mermaid migration-required occurrences only, not visual records.

Observed at manifest baseline `f643166`:

- 569 occurrences in 364 diagram-bearing Markdown files. The current tracked tree has 455 Markdown files (`git ls-files '*.md' | wc -l`).
- 568 published occurrences and one repository-only occurrence, `labs/code-storage-verification/README.md:19`, whose key is `labs/code-storage-verification/README.md#~1`.
- Three excluded occurrences: the orientation example in `docs/contributing/content-contract.md`, and generator-owned charts in `docs/reference/content-validation-status.md` and `docs/reference/validation-status.md`. Exclusions have reasons and no owning batch.
- 566 migration-required occurrences; batch counts sum to this total.
- No non-Mermaid published diagram detected by the searched mechanisms; 27 raster assets grouped as screenshots and two SVGs classified as branding are reported separately, not exhaustively classified visually.

## Inventory Tables

Only `python3 scripts/diagram_inventory.py --write` fills these generated blocks. Counts include exclusions except in the batch table.

### Occurrences by Section

<!-- BEGIN GENERATED: diagram-inventory:section -->
| Section | Count |
|---|---:|
| best-practices | 21 |
| contributing | 2 |
| docs-root | 1 |
| language-guides | 326 |
| operations | 18 |
| platform | 54 |
| reference | 12 |
| repository | 1 |
| start-here | 5 |
| troubleshooting | 129 |

<!-- END GENERATED: diagram-inventory:section -->

### Occurrences by Mermaid Syntax Type

<!-- BEGIN GENERATED: diagram-inventory:type -->
| Type | Count |
|---|---:|
| flowchart | 504 |
| gantt | 12 |
| graph | 22 |
| pie | 2 |
| sequenceDiagram | 25 |
| stateDiagram-v2 | 1 |
| timeline | 3 |

<!-- END GENERATED: diagram-inventory:type -->

### Migration-Required Occurrences by Batch

<!-- BEGIN GENERATED: diagram-inventory:batch -->
| Batch | Count |
|---|---:|
| 212 | 27 |
| 213 | 22 |
| 214 | 38 |
| 215 | 130 |
| 216 | 349 |

<!-- END GENERATED: diagram-inventory:batch -->

### Asset Exclusions by Group

Asset groups are path-based claims, not visual verification. Wildcard `paths` entries claim only raster images (`.png`, `.webp`, `.jpg`, `.jpeg`, `.gif`); vector or diagram-source assets require an exact path without wildcard characters, or a matching path rule whose optional `extensions` array explicitly lists dotted suffixes (for example, `[".svg", ".mmd"]`). Asset suffixes and `extensions` entries are case-insensitive (`[".SVG"]` opts into `.svg`); path matching remains case-sensitive. Otherwise they remain in `exceptions.unclassified_assets` for review. The Functions `branding` group claims `docs/assets/logo.svg` and `docs/assets/favicon.svg` by exact path; no current group uses `extensions`.

<!-- BEGIN GENERATED: diagram-inventory:exclusions -->
| Exclusions | Count |
|---|---:|
| branding | 2 |
| operations-portal-screenshots | 23 |
| troubleshooting-portal-screenshots | 4 |

<!-- END GENERATED: diagram-inventory:exclusions -->

### Data-Quality Exceptions Summary

<!-- BEGIN GENERATED: diagram-inventory:exceptions -->
| Exceptions | Count |
|---|---:|
| duplicate_ids_on_page | 0 |
| fences_without_frontmatter_entry | 2 |
| frontmatter_duplicate_ids | 0 |
| frontmatter_entries_without_fence | 0 |
| frontmatter_unparseable | 0 |
| id_reused_on_other_pages | 34 |
| missing_id_comment | 1 |
| unclassified_assets | 0 |
| unclosed_fences | 0 |
| unrecognized_mermaid_fences | 0 |
| unresolved_overlaps | 0 |

<!-- END GENERATED: diagram-inventory:exceptions -->

## Batch Map and Ownership Rules

The manifest stores the verbatim trimmed `Affected scope` of each child payload, its title and phase. Explicit path rules quote those scopes in their rationale:

- #211, P1: reusable Functions base/integration contract; no existing diagram allocated. The base is future work, not an extra legacy occurrence.
- #212, P2: architecture, hosting, triggers and core runtime/programming-model pages.
- #213, P3a: networking scenarios, storage connectivity, security and assigned operational identity controls.
- #214, P3b: scaling, Durable recipes/orchestration, reliability/retry and cold-start execution.
- #215, P3c: troubleshooting decision cards, incident flows, KQL/evidence workflows and lab diagrams, including the repository-only README.
- #216, P3d: explicit residual language tutorials, recipes, operations, practices, reference, orientation and other supporting published diagrams.
- #217, P4: final CI and visual audit; `owns_diagrams: false`, no diagrams allocated.

### Rule Priority and Residual Assignments

All matching rules are recorded in `assignment.candidates`. Specific topical rules have priority 100; explicit residual rules have priority 10. The baseline has 41 multiple-candidate entries, resolved by these declared priorities, with no tied highest priorities, no reviewed overrides and zero unresolved/unassigned items. A future semantic override requires a reviewed reason; silently choosing the first matching rule is not permitted.

Residual ownership is explicit because #216 names language guides, operations, best-practices, reference and other published files not allocated to the topical migrations. It is not a catch-all for unknown paths. Lab screenshots remain exclusions, not lab diagrams.

## Functions-Specific Hosting and Trigger Plan

**Inferred: path-based classification, unreviewed.** These candidate sets are planning aids, not platform validation. The scanner deliberately has no hosting-plan or trigger field. Counts are occurrences, including repeated tutorial baselines; they do not prove unique topologies. Paths not matching these expressions remain unclassified for this planning dimension, not unmapped in migration ownership.

### Hosting Plans Requiring Separate Variants

The tutorial directories identify 177 plan-specific-by-construction entries:

| Plan directory | Diagram occurrences |
|---|---:|
| Consumption (`consumption`) | 43 |
| Flex Consumption (`flex-consumption`) | 55 |
| Premium (`premium`) | 43 |
| Dedicated (`dedicated`) | 36 |

Run this one-liner from the repository root to reproduce both counts and the **complete list of plan-specific diagram keys**. `keys` is the exact set allocated by construction, not a sampled list:

```bash
python3 -c 'import json,re; ds=json.load(open("docs/reference/diagram-manifest.json"))["diagrams"]; plans=("consumption","flex-consumption","premium","dedicated"); print(json.dumps({p:{"count":len(keys),"keys":keys} for p in plans for keys in [[d["key"] for d in ds if re.match(r"^docs/language-guides/[^/]+/tutorial/"+p+r"/",d["page"])]]},indent=2))'
```

Representative traceable keys for the separate plan variants (all four first-deploy baselines are retained, not collapsed):

- `docs/language-guides/python/tutorial/consumption/02-first-deploy.md#what-you-ll-build`
- `docs/language-guides/python/tutorial/flex-consumption/02-first-deploy.md#what-you-ll-build`
- `docs/language-guides/python/tutorial/premium/02-first-deploy.md#what-you-ll-build`
- `docs/language-guides/python/tutorial/dedicated/02-first-deploy.md#what-you-ll-build`

Migration review must keep the following candidate differences separate and validate them against the preserved Learn references before conversion:

| Candidate variant | Difference to preserve in separate diagram or explicit overlay | Owner |
|---|---|---|
| Consumption | Legacy hosting/storage and public-network assumptions; do not inherit Flex private networking or deployment paths | #212 / #213 / #216 |
| Flex Consumption | Blob deployment storage, identity, per-function scaling and always-ready assumptions; distinguish event-based Blob activation | #212 / #213 / #214 / #216 |
| Premium | Warm capacity, elastic scaling, content/deployment storage and VNet assumptions; not a relabeled Flex graph | #212 / #213 / #214 / #216 |
| Dedicated | App Service plan capacity, Always On and supported deployment/network choices; do not depict serverless scale-to-zero | #212 / #213 / #214 / #216 |

The common platform and operational views need plan overlays or separate variants rather than a universal-plan drawing. Reproduce their complete diagram-key lists with this one-liner; the selected pages are explicit so classification is rerunnable:

```bash
python3 -c 'import json; ds=json.load(open("docs/reference/diagram-manifest.json"))["diagrams"]; pages=("docs/platform/architecture/index.md","docs/platform/hosting.md","docs/platform/deployment-scenarios.md","docs/platform/networking.md","docs/platform/storage-connectivity.md","docs/platform/scaling.md","docs/platform/triggers-and-bindings.md","docs/platform/durable-functions.md","docs/operations/cold-start.md","docs/operations/deployment.md","docs/operations/migration.md","docs/operations/retries-and-poison-handling.md"); print(json.dumps({p:[d["key"] for d in ds if d["page"]==p] for p in pages},indent=2))'
```

For example, `docs/platform/hosting.md#hosting-plans-at-a-glance`, `docs/platform/scaling.md#flex-specific-operational-constraints-affecting-scale` and `docs/platform/triggers-and-bindings.md#event-grid-vs-polling-blob-trigger-model` already expose where plan assumptions matter. Selection of all diagrams on a page is deliberately conservative, not a judgment that every fence needs every overlay.

### Trigger Families Requiring Separate Diagrams

Path-based recipe classification identifies HTTP API, HTTP authentication, Queue, Blob, Timer, Event Hubs, Event Grid, Service Bus and Cosmos DB integration recipes. HTTP authentication is a subfamily of HTTP; Cosmos DB pages can describe bindings rather than a change-feed trigger. Do not infer the trigger from the recipe name alone. Each recipe family has four occurrences in this baseline; the HTTP family combines eight. Tutorial `07-extending-triggers.md` pages and mixed platform pages are additional multi-trigger contexts, not assigned to a single family by this recipe-only count.

```bash
python3 -c 'import json,re; ds=json.load(open("docs/reference/diagram-manifest.json"))["diagrams"]; families={"HTTP":r"http-(api|auth)","Queue":"queue","Blob":"blob-storage","Timer":"timer","Event Hubs":"event-hub","Event Grid":"event-grid","Service Bus":"service-bus","Cosmos DB binding/trigger candidate":"cosmosdb"}; print(json.dumps({f:{"count":len(keys),"keys":keys} for f,pattern in families.items() for keys in [[d["key"] for d in ds if re.match(r"^docs/language-guides/[^/]+/recipes/(?:"+pattern+r")\.md$",d["page"])]]},indent=2))'
```

Review separate HTTP ingress/response, Queue dequeue/retry/poison, Blob event delivery versus polling, Timer schedule/lease, Event Hubs partition/checkpoint, Service Bus settlement/dead-letter and Event Grid subscription delivery diagrams. Do not flatten these into a generic “event source” edge. Durable orchestration needs typed replay/activity/entity/state-storage views under #214, not an ordinary trigger label. Mixed host/worker execution stays with #212; diagnostic variants stay with #215.

## Non-Mermaid Visuals

The current inventory classifies no non-Mermaid published visual as detected by the searched mechanisms across `docs/` (`<svg`, `<img`, `<iframe`, `<script`, `cytoscape`, `d3`, `vis-network`, `plotly`). The baseline search found branding SVG markup, `D3` node/case identifiers and fenced Swagger UI example scripts in the Python/Node.js OpenAPI recipes. `mermaid-zoom.js` only interacts with existing Mermaid. No standalone drawing sources, snippet-generated diagram or separate visual dataset was found by this textual search; it is not an exhaustive visual classification of raster assets.

Path and alt-text screening grouped 23 raster assets as operational Portal screenshots and four as first-response Portal screenshots. The historical visual sample covered 24 images across all 21 raster directories: each singleton directory once and two images in each remaining directory; it does not classify all 27 raster assets visually. Sampled rasters were Portal blades, not authored drawings. Visual inspection of the two SVGs was unavailable; their branding classification is supported by source and `mkdocs.yml` logo/favicon wiring, not a claimed visual verdict or file-name-only assessment. No final-image PII approval is implied; no image bytes or references are changed here.

## Quality of Classification

### Heuristic Genre Candidates

The 526 flowchart/graph blocks use syntax signals: decision shapes or Yes/No labels suggest `decision`; subgraphs without decisions suggest `topology`; otherwise `flow`. Mixed signals yield `unknown` and `needs_review: true`. Typed sequence/state/timeline/chart candidates follow their syntax. None of these candidates establishes reader intent.

The fixed-seed stratified source-read sample (seed 210, up to 15 per candidate genre, 79 diagrams) was labelled against Functions `main` at `f643166` by an AI agent reading each complete diagram body, not by an independent human review. It measured agreement of 40/46 heuristic candidates (87.0 %) and 33/33 syntax-decided candidates (100 %), not human approval or rendered accuracy. The retained Functions evidence does not establish which sampled diagrams open PR #219 changes or whether their genres remain unchanged; these measurements are not a reassessment of that PR. All manifest classifications remain `unreviewed`; no thresholds were tuned after reading the sample. Dependency maps without subgraphs and grouped processing flows can mislead the heuristic. This disproportionate sample must not be reported as a population accuracy estimate.

### Provenance Extraction and Official References

The 567 attached declarations comprise three `mslearn-adapted` and 564 `self-generated` entries; two fences have no declaration. All declared objects are preserved verbatim as parsed data, including `mslearn_url`, `based_on`, justification and unknown fields. Sibling `content_sources.references` mappings and extra frontmatter such as `slug` are not mistaken for diagram entries. The baseline has no orphan frontmatter diagram entries.

List all declared references and their stable diagram keys without asserting that those references were checked:

```bash
python3 -c 'import json; m=json.load(open("docs/reference/diagram-manifest.json")); print(json.dumps([{ "key":d["key"],"declared":d["provenance"]["declared"]} for d in m["diagrams"] if d["provenance"]["declared"]],indent=2))'
```

Extraction completeness is not source verification. `provenance.verification` remains `not-performed`; changed diagrams in subsequent batches still require source review.

## Data-Quality Findings and Remediation

The missing ID belongs to the repository-only code-storage README. The two missing declarations belong to that README and the generated content-validation chart. The 34 IDs reused across pages are disambiguated by page-qualified keys; there are no duplicate IDs on a page, unclosed fences, unparseable frontmatter or unclassified assets. Preserve these exceptions as evidence rather than retroactively “fixing” the baseline.

## Initial Rendering Test and Binary Screenshots Decision

The supplied one-time measurement on 2026-10-30 ran on Functions `main` at `f643166`, the main revision identified in the retained Functions evidence, before the fixes to its two failing blocks proposed in open PR #219. It used throwaway tooling and headless Chrome 145 with the site's `mermaid@10.9.1`: **566 of 568 published Functions blocks rendered; two parse errors** were tracked in Functions #218. The existing regex validator caught neither. This is a historical measurement, not a rendering result for PR #219; this adoption does not rerun rendering, certify that fix or implement #217's render gate.

Derived Functions PNGs totaled **16.4 MB, about 28 KiB per diagram**. Deliberately deviating from #210's “before screenshots” wording, none is committed: binary history and evidence-image review overhead add no independent evidence for a reproducible source rendering. The [ADR](adr-diagram-composition.md#over-engineering-assessment) records the decision and links the Container Apps measurement rationale. Source commit and per-block hashes provide the structural baseline, not a visual correctness claim.

## Command Reference

Use Python 3.11 and PyYAML; CI additionally installs jsonschema for schema parity tests. Commands resolve paths relative to the script's repository, not the caller's current directory. The scanner never renders, converts, or verifies source provenance. `--write` writes the manifest and this page's generated blocks; `--check` performs consistency validation, not provenance verification.

Files are decoded as UTF-8 with optional BOM. An undecodable file is skipped and recorded in `frontmatter_unparseable` with its path and decoding error, like unparseable frontmatter; this exception means extraction is incomplete, not that no diagram exists. Duplicate usable frontmatter IDs appear in `frontmatter_duplicate_ids`; only the first entry supplies declared provenance. Missing, null, empty, or non-string frontmatter IDs never attach to a fence.

The scanner is a line-based approximation of how the site renders indentation, not a full Markdown container parser. It errs toward reporting Mermaid-opener-like lines in `unrecognized_mermaid_fences` rather than silently dropping them:

- `html-comment` and `indented-code` are informational: the fence is hidden by a multiline HTML comment or shown as plain indented code. Plain-code state starts at an indented line (at least four columns, with tabs expanded) after a blank line or at the start of the page, while no HTML element is open and no list or container ancestor applies. It continues across blank or indented lines and ends at the first nonblank line with fewer than four columns. A heading or thematic break ends a list, and a line indented four columns or more is code, not a list item. `--check` prints each finding without failing.
- `blockquote`, `list-marker`, and `indented` are blocking findings. The last reason covers container indentation, an indented fence while an HTML element is open, and a lazy continuation directly after prose without a blank line. HTML context is a stack of element names: a tag at the start of a line (up to three spaces of indentation) opens an element unless it is a void element, self-closing or closed on the same line; a closing tag line closes the nearest open element of that name, and a closing tag without an open element is ignored. Intervening paragraphs, headings, lists and code blocks do not close an element. Inline HTML that does not start a line, autolinks such as `<https://example.com>` and comments open nothing. This is a heuristic, not an HTML parser: an element that is never closed (for example an unclosed `<p>`, `<li>` or `<td>`) keeps the context open until a closing tag of an ancestor, and an indented fence inside an open element is reported as blocking even where the site shows plain code. `--write` succeeds and warns once per page, listing only blocking findings; `--check` fails. Move the fence to the top level with at most three spaces of indentation, or show it inside a longer outer fence, then regenerate.
- Fence recognition precedes comment detection. Inline code spans containing comment tokens do not open comments. A multiline comment needs a closing `-->`: an unclosed one is shown as literal text by the site, so it hides nothing, and text inside any fence never closes a comment because the site extracts fences first. Unsupported blocks, including indented generic fences of any language or no language, are consumed through their matching closing fence (even a dedented closer) so later canonical fences remain in sync; shorter fences of the same kind and fences of another kind inside the block are content, and only Mermaid openers produce findings. Another opener of the same kind and at least the same length before a closing fence, or no closing fence, means the block is unclosed and the scan resumes on the next line instead of swallowing the page.
- Recognized outer non-Mermaid fences contain examples, not rendered diagrams, and do not produce unsupported-fence findings. The separate Functions `scripts/validate_mermaid_format.py` policy already rejects indented backtick Mermaid openers, including plain indented code examples; use a longer outer fence for examples.

The shared scanner's classification was checked against Python-Markdown 3.10.2 and pymdownx 10.21.3 on 2026-10-30 in local experiments with synthetic corpora, run for the Container Apps pull request. A 3,300-document grammar corpus had no document where rendered diagrams exceeded recognized non-example occurrences plus blocking findings, and no plain-code document with a blocking finding. A generator of 12,448 balanced documents (HTML wrappers with intervening paragraphs, headings, lists and code, longer generic outer fences with shorter or other-kind inner fences and dedented closers, plain code after neighbouring HTML, and lists ended by headings or thematic breaks) had no such surplus and no blocking finding on plain code; in 4,448 of its HTML-wrapper documents the site shows no diagram although an indented fence inside an open element is reported as blocking, which is the conservative direction. A mutation fuzzer (seeds 11, 12, and 13; 4,000 documents each) found 54, 69, and 60 under-accounted documents respectively (183 of 12,000, about 1.5 %); the remaining minimized cases use corrupted or unbalanced fence syntax. Those experiments were not run on Functions pages; their harnesses and evidence are not committed here. The scan result of every Markdown file of this repository is identical between the previous and the current scanner version. These measurements come from synthetic corpora, do not estimate how often such patterns occur in real documentation, and are not a rendering guarantee.

Known limitations:

- Info strings with extra words are counted by the first-word `mermaid` rule, but the site shows them as code rather than diagrams.
- A comment that starts after a list marker or blockquote prefix is not tracked.
- Nested list/container structure beyond the less-indented ancestor heuristic may be reported as `indented` when the site shows code. HTML context is a line-start heuristic: a closing tag that does not start a line, or an element that is never closed, keeps or loses context differently from the site, and an indented fence in an open element is blocking even where the site shows plain code. Plain-code continuation is tracked explicitly, but this is not a full container parser.
- Corrupted or unbalanced fence syntax, for example an opener that is never closed, bare marker lines of a different kind, tilde/backtick mixes, or fence markers and comment tokens inside an info string, is parsed differently by CommonMark and by the site's renderer. The scanner uses CommonMark-style boundaries for recognized top-level fences and records their unclosed fences in `unclosed_fences`, but the site can show more diagrams than the scanner accounts for on such a page.

### Validating the Inventory (Blocking CI)

```bash
python3 scripts/test_diagram_inventory.py
python3 scripts/diagram_inventory.py --check
python3 scripts/diagram_inventory.py --verify-tree
python3 scripts/diagram_inventory.py --summary
```

`--check` blocks malformed/stale inventory data and generated tables, validates the schema, reconciles keys/counts/ownership and checks scanner/rules hashes. It does **not** compare the current tree with the baseline. Deterministic fixture reproduction remains blocking; current-tree baseline reproduction is opt-in with `DIAGRAM_INVENTORY_REPRODUCE=1` when the tree is unchanged. Final migration coverage enforcement belongs to #217.

### Regenerating the Manifest

`--write` reads the current working tree and regenerates the whole manifest, recording `baseline.base_commit` as metadata (pass `--base-commit` to pin it); it does not read the tree at that commit or retain separate baseline records and current-tree observations. Run `--verify-tree` before rewriting to see removed and changed records. Reviewed planning fields are preserved by key, while a reviewed classification is preserved only when the diagram body's `baseline.source_sha256` is unchanged; a changed body receives a fresh, unreviewed heuristic classification and must be reviewed again.

To regenerate deliberately, preserving the existing baseline commit unless explicitly replaced:

```bash
python3 scripts/diagram_inventory.py --write
```

Offline regeneration never refreshes Azure execution, capture or verification dates.

### Migration Progress States

Batch owners edit `target`, `context.reader_intent`, and `migration` by key; these planning fields survive body changes and regeneration.

| Migration state | Meaning | `exception` |
|---|---|---|
| `not-started` | Migration has not begun. | `null` |
| `in-progress` | The owning batch is migrating the diagram. | `null` |
| `completed` | The owning batch records migration as complete. | `null` |
| `exception` | Migration has an explicitly recorded exception. | Nonblank explanation string |

These are owner-maintained progress states, not proof of rendering, source verification, or review approval.

### Checking Tree Drift (Advisory)

`--verify-tree` compares extracted diagram records with the baseline; it does not report extraction completeness. Consult `unrecognized_mermaid_fences` through `--check` for blocking extraction findings. A drift-free result alone does not establish a complete inventory.

The JSON categories are `added` and `removed` keys; `moved` key changes with identical bodies; `changed` body hashes; `reclassified` genre, syntax type, or assignment changes; `provenance` changes to the complete provenance record; and `relocated` changes to the same key's line, end line, or heading path. `assets` lists changed exclusion-group path sets as `{group, added, removed}` records, with `group: null` for the unclassified-asset set; `visuals` lists keys added, removed, or changed in non-Mermaid visual records. Paths are compared as sets, not list order. Drift remains advisory (exit zero); adding `--strict` makes any non-empty category fail.

## See Also

- [ADR: Diagram Composition](adr-diagram-composition.md)
- [Manifest JSON](diagram-manifest.json)
- [Documentation Content Contract](../contributing/content-contract.md)
- [Hosting](../platform/hosting.md)
- [Triggers and Bindings](../platform/triggers-and-bindings.md)

## Sources

- [Functions migration umbrella #209](https://github.com/yeongseon/azure-functions-practical-guide/issues/209)
- [Inventory #210](https://github.com/yeongseon/azure-functions-practical-guide/issues/210)
- [App Service shared prototype #283](https://github.com/yeongseon/azure-app-service-practical-guide/issues/283)
- [Azure Functions hosting options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [Azure Functions triggers and bindings](https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings)
