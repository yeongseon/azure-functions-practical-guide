---
title: ADR - Diagram Composition and Shared Topology Strategy
description: Proposed reuse boundaries and composition alternatives for the Azure Functions diagram migration.
---

# ADR: Diagram Composition and Shared Topology Strategy

This reference records the proposed diagram reuse strategy, not an accepted composition interface or a completed migration.

## Status

Proposed, pending the [App Service shared prototype #283](https://github.com/yeongseon/azure-app-service-practical-guide/issues/283). Functions #211 adopts the resulting contract; #212–#216 migrate the existing diagrams; #217 owns final coverage and rendering validation. Parent #209 remains open.

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

Keep inline Mermaid as the reviewed source of truth. Compare Options B and C in App Service #283 using a base, distinct extensions and normal/failure overlays before Functions adopts a composition path in #211. Preserve sequence/state/timeline/chart semantics as hand-authored typed Mermaid where composition adds no value. A flowchart remains a flow or decision tree when that is its teaching purpose.

For this inventory only, share `scripts/diagram_inventory.py` and `diagram-manifest.schema.json` byte-identically with Container Apps. The manifest pins the scanner and repository-specific rules by SHA-256. Schema v1 is an **inventory interchange contract**, not a composition/build API. Rules, ownership, exclusions and pages remain Functions-specific. A future scanner change must be reconciled and re-synchronized rather than independently extended here.

The scanner is a scanning, consistency-validation, and reporting tool that never renders, converts, or verifies source provenance. `--write` writes the manifest and generated inventory-page blocks; `--check` validates consistency, not provenance. `--verify-tree` compares extracted records with the baseline, not extraction completeness; `--check` reports `unrecognized_mermaid_fences`.

Every entry retains a traceable source key, location, source-body hash, owning batch or explicit exclusion, and a provisional target record. `target.base` remains null and extensions/overlays empty until the prototype establishes meaningful names; this is deferred design, not an unmapped owner. Migration remains `not-started`. The [hosting/trigger plan](diagram-inventory.md#functions-specific-hosting-and-trigger-plan) derives candidate variants from paths without adding scanner fields.

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
