---
title: ADR - Diagram Composition and Shared Topology Strategy
description: Accepted shared literal-Mermaid authoring default, Functions topology templates, and historical composition alternatives.
---

# ADR: Diagram Composition and Shared Topology Strategy

This reference records the accepted shared default authoring method and the historical inventory/alternative evaluation. It does not claim the diagram migration or human visual acceptance is complete.

## Status

**Accepted default authoring: literal, typed Mermaid (Option A)** for both Functions and App Service. Functions [#211](https://github.com/yeongseon/azure-functions-practical-guide/issues/211) supplies the existing templates, while #212–#216 own migrations and #217 owns coverage/rendering checks. The earlier proposed composition alternatives remain historical; the upstream opt-in generator is not a prerequisite. Parent #209 remains open.

## Context and Problem Statement

Observed on Functions baseline `f643166`: the [manifest](diagram-manifest.json) contains 569 Mermaid occurrences on 364 tracked Markdown pages, including 568 published blocks and a repository-only lab README. Of these, 526 are flowchart/graph (92.4 %) and 43 use sequence, state, timeline, gantt or pie syntax (7.6 %). Three explicit exclusions leave 566 migration-required occurrences.

The approximate node-label extraction finds `application insights` in 74 diagrams, `function app` in 37, and `microsoft entra id` in 35. These are regex-derived candidates, not an accepted component vocabulary or proof that diagrams are interchangeable. The inventory also records 34 IDs reused across pages and two fences without declared per-diagram provenance. The page-qualified key avoids global ID collisions without editing source IDs.

The [umbrella #209](https://github.com/yeongseon/azure-functions-practical-guide/issues/209) requires typed diagrams and Functions-specific variants, not generic topology replacements for every flow. Hosting, trigger listeners, host/worker boundaries, deployment storage, Durable state and incident evidence must retain their different meanings.

## Decision Drivers

- Preserve reader intent and source attribution, including temporal order and evidence uncertainty.
- Separate Consumption, Flex Consumption, Premium and Dedicated assumptions instead of sharing an inaccurate universal base.
- Keep authoring and local MkDocs preview straightforward; composition must earn its complexity through demonstrated reuse.
- Reconcile the cross-guide interface through the shared prototype, not divergent copied generators.

## Considered Options

### Option A: Keep Inline Mermaid as Reviewed Source of Truth

Retain native Mermaid in Markdown with existing source, ID and format checks. This is the simplest fallback and needs no compiler, but repeated platform fragments remain independently maintained.

### Option B: MkDocs Macros or Snippets for Shared Topology Fragments

Use the existing macros/snippets toolchain for narrowly reusable fragments. This minimizes new tooling, but concatenation can hide node-ID collisions, indentation problems and ownership of edges. A prototype must show that reviewers can still understand the assembled diagram.

### Option C: Small YAML-to-Mermaid Composition Renderer

Describe a base, named extensions and scenario overlays as structured data. This could validate references and reduce duplication, but adds an intermediate language, compilation and stale-output checks. It is not justified merely because many fences use flowchart syntax.

### Option D: Standalone Shared Package Across Repositories

A published package offers central distribution but creates versioning, release and cross-repository coordination costs. Defer it until actual cross-guide reuse is demonstrated, as required by #209. No package is adopted by this inventory.

## Decision Outcome

### Functions-local choice — 2026-11-04 (historical)

> This paragraph documents the earlier Functions-local choice before the cross-guide decision on 2026-11-06. The accepted shared contract below supersedes its statements that no cross-guide authoring decision had yet been made.

For Functions #211, adopt **Option A: typed literal Mermaid templates and documented
copyable snippets**, with the [Functions templates](functions-topology-templates.md)
and a small offline guard. Adopt the App Service [topology grammar v1](https://github.com/yeongseon/azure-app-service-practical-guide/blob/3429ca0/docs/reference/diagram-topology-grammar.md)
by reference; its status remains **Proposed**. No generator, macro, new plugin or
dependency is introduced. Literal fences remain visible to the existing validators
and inventory; the inventory schema/scanner are unchanged.

App Service PR #298 is merged, but #283 remains open with no final maintainer
composition decision recorded. Its opt-in PoC failed its predeclared M4 size budget
(434 generator nonblank lines against 400; 449 test lines against 260). This local
choice neither accepts nor rejects that upstream prototype. Option A is usable
under either outcome; children #231–#383 must not assume a generator. Repeated
declarations are deliberate reviewed source, checked for ID/order drift rather than
compiled from a second specification. Human visual acceptance remains pending;
this note is not a cross-guide ruling or completion of #209/#217.

### Original inventory decision

Keep inline Mermaid as the reviewed source of truth. Compare Options B and C in App Service #283 using a base, distinct extensions and normal/failure overlays before Functions adopts a composition path in #211. Preserve sequence/state/timeline/chart semantics as hand-authored typed Mermaid where composition adds no value. A flowchart remains a flow or decision tree when that is its teaching purpose.

For this inventory only, share `scripts/diagram_inventory.py` and `diagram-manifest.schema.json` byte-identically with Container Apps. The manifest pins the scanner and repository-specific rules by SHA-256. Schema v1 is an **inventory interchange contract**, not a composition/build API. Rules, ownership, exclusions and pages remain Functions-specific. A future scanner change must be reconciled and re-synchronized rather than independently extended here.

The scanner is a scanning, consistency-validation, and reporting tool that never renders, converts, or verifies source provenance. `--write` writes the manifest and generated inventory-page blocks; `--check` validates consistency, not provenance. `--verify-tree` compares extracted records with the baseline, not extraction completeness; `--check` reports `unrecognized_mermaid_fences`.

On pull requests and pushes to `main`, without path restrictions, CI also runs
`python scripts/check_diagram_inventory_tree.py` after `--check`, reusing the
unchanged shared scanner. It blocks added/removed/moved keys,
assignment/type/genre reclassification, provenance and asset/visual drift,
duplicate page/source IDs, and missing or stale generated inventory blocks.
Fence and source-entry IDs use ASCII letters, digits, dots, underscores or
hyphens, starting with a letter or digit, including source entries without a
matching fence; valid unmatched entries are not themselves blocked after
regeneration. Reuse across pages is valid. Only the existing repository-only
`labs/code-storage-verification/README.md#~1` missing ID is retained as debt.
Body hashes and source locations alone remain advisory (`--verify-tree` reports
them); CI does not establish semantic correctness, rendering, source verification
or completed migration. Use `--write` for structural updates, not for every label
edit. Existing source, PII, screenshot, evidence and strict-build checks still apply.

Every entry retains a traceable source key, location, source-body hash, owning batch or explicit exclusion, and a provisional target record. `target.base` remains null and extensions/overlays empty until the prototype establishes meaningful names; this is deferred design, not an unmapped owner. Migration remains `not-started`. The [hosting/trigger plan](diagram-inventory.md#functions-specific-hosting-and-trigger-plan) derives candidate variants from paths without adding scanner fields.

## Shared Mermaid authoring and review contract (2026-11-06)

This is the same authoring policy for the App Service and Functions practical guides. It supersedes an earlier repository-local *proposal* where it conflicts; historical experiment and inventory observations above remain evidence, not a mandate to use a generator.

1. **Single default authoring method:** write and review **literal, typed Mermaid directly in Markdown** (ADR Option A). Keep the complete diagram beside its explanatory text, `diagram-id`, and `content_sources.diagrams[]` provenance where required by that repository. Use the existing MkDocs/Mermaid toolchain. No YAML/JSON composition specification, generated fence, new macro, new renderer, or cross-repository package is required for a normal migration.
2. **One shared visual and semantic grammar:** follow [Azure Topology Visual Grammar v1](https://github.com/yeongseon/azure-app-service-practical-guide/blob/main/docs/reference/diagram-topology-grammar.md) for component naming, official Azure icons when applicable, positions/reading order, resource/VNet/subnet/Private Endpoint boundaries, labeled one-way arrows, line/legend taxonomy, neutral styling, and accessible fault/evidence overlays. Its separate fixture/human-acceptance status remains open; adopting it as the common authoring reference does not claim every old diagram already conforms.
3. **Accurate service adapters, not cloned architectures:** App Service shows its frontend/worker and web-app routing semantics; Functions shows trigger sources, scale/listener/host/worker and hosting-plan-specific behavior. Reuse the same conventions without representing queue/timer delivery as HTTP ingress or placing a multitenant PaaS runtime inside the customer's VNet. Keep DNS, control/management, transport, authentication, and diagnostic evidence distinct. A decision tree, sequence, state, or timing diagram keeps its proper typed form; do not force it into a topology.
4. **No default generator:** the merged [App Service composition prototype PR #298](https://github.com/yeongseon/azure-app-service-practical-guide/pull/298) remains a bounded opt-in experiment; it failed its predeclared tool-size test, so neither guide may require it for bulk migration. Keep existing fixtures/tests intact unless a separately reviewed change removes them. The merged [Functions templates PR #396](https://github.com/yeongseon/azure-functions-practical-guide/pull/396) demonstrates the agreed literal-Mermaid approach. Do not rewrite already-running PRs solely to change the authoring mechanism.
5. **Same acceptance standard, local execution:** inspect each changed diagram's meaning, labeled flows, boundary semantics, source attribution, stable ID and accessibility. Record before/after *rendered* inspection at desktop and narrow width (representatively 1440px and 390px), light/dark, and zoom; check readable text, arrow/key clarity, contrast and no misleading crossings or clipping. Run the repository's existing strict MkDocs, Mermaid, inventory/coverage, source/PII and relevant evidence tests on the **final PR head**. A passing build or headless capture alone is not human visual acceptance. Document untested interactions and `NOT_RUN` rather than claiming them.
6. **Independent repositories, synchronized rules:** keep exact occurrence ownership in each guide's own manifest, and preserve its existing scanner/schema and CI without introducing a second renderer. Coordinate changes to the shared diagram grammar and acceptance expectations across App Service [#289](https://github.com/yeongseon/azure-app-service-practical-guide/issues/289) / [#395](https://github.com/yeongseon/azure-app-service-practical-guide/issues/395) and Functions [#217](https://github.com/yeongseon/azure-functions-practical-guide/issues/217) / [#394](https://github.com/yeongseon/azure-functions-practical-guide/issues/394). These review requirements are shared now; identical automated CI coverage and final rendered sign-off remain **unverified**, not assumed.

Migration completion is independent of this authoring decision: App Service [#281](https://github.com/yeongseon/azure-app-service-practical-guide/issues/281) and Functions [#209](https://github.com/yeongseon/azure-functions-practical-guide/issues/209) stay open until their manifests and final checks prove completion.

## Over-Engineering Assessment

The simple path is curated inline Mermaid. This change adds only a reproducible inventory, its tests and data, plus consistency checks in an existing job. It adds no renderer, converter, new framework, workflow or top-level directory. The inventory does not make #217's final migration/render gate redundant: `--check` checks the frozen manifest's internal consistency, not live render correctness or new-diagram coverage.

The issue's “before screenshots” wording is deliberately not implemented as committed PNGs. The supplied one-time cross-guide measurement recorded **568 published Functions blocks, 16.4 MB of derived PNGs, about 28 KiB each**. The measurement and binary-artifact rationale are recorded in the [Container Apps ADR](https://github.com/yeongseon/azure-container-apps-practical-guide/blob/docs/diagram-inventory-400/docs/reference/adr-diagram-composition.md). Functions image gates require caption accuracy and final-byte PII review for evidence screenshots; hundreds of regenerable images would add binary history and review cost without adding independent evidence. Source commits and per-block hashes retain the structural baseline; a separate throwaway harness can reproduce renders. No harness or derived PNG is committed here.

## Consequences and Risks

- Positive: complete accounting, explicit exclusions, reconciled counts and a single owner per migration-required occurrence; residual scope is visible rather than silently dropped.
- Positive: Python standard library plus PyYAML require no external binary dependencies for inventory scanning.
- Risk: a shared topology can erase plan-specific deployment/storage or trigger semantics. Mitigation: review the path-based candidate sets and cited sources within each migration batch before reusing a component.
- Risk: heuristic genre candidates confuse ungrouped dependency maps with flows, or grouped processing flows with topologies. Mitigation: all entries remain `unreviewed`; the sample measures agreement only, not approval of individual entries.
- Risk: declared source metadata may be stale or incorrect. Mitigation: preserve the entire declared object, including `mslearn_url` and `based_on`, with `verification: not-performed`; source verification belongs to the changed diagram's migration.
- Risk: a line-based scanner cannot fully reproduce the site's Markdown container rendering. Mitigation: `blockquote`, `list-marker`, and `indented` findings block `--check`; `html-comment` and plain `indented-code` findings are informational. `--write` warns once per page for blocking findings only. The Functions Mermaid format validator already rejects indented backtick Mermaid openers; examples belong inside longer outer fences. See the [inventory's known limitations](diagram-inventory.md#command-reference), including extra info words, prefixed comments and conservative nested-container over-reporting. The shared scanner's classification was checked against Python-Markdown 3.10.2 / pymdownx 10.21.3 in local experiments for the Container Apps pull request, not on Functions pages; that experiment is not committed here.
- Risk: the shared prototype may show composition is not simpler. Mitigation: retain Option A without migration lock-in.

Only the responsible Functions maintainer authorizes squash merge. Local checks and AI feedback are not approval; final-head GitHub CI and the repository's existing review gates remain authoritative.

## See Also

- [Diagram Inventory](diagram-inventory.md)
- [Diagram Manifest Schema](diagram-manifest.schema.json)
- [Documentation Content Contract](../contributing/content-contract.md)

## Sources

- [Functions migration umbrella #209](https://github.com/yeongseon/azure-functions-practical-guide/issues/209)
- [Inventory task #210](https://github.com/yeongseon/azure-functions-practical-guide/issues/210)
- [Shared App Service prototype #283](https://github.com/yeongseon/azure-app-service-practical-guide/issues/283)
- [Mermaid documentation](https://mermaid.js.org/)
