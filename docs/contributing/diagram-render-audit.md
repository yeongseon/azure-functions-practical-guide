---
title: Diagram Render Audit
description: Reproducible browser sampling checklist and baseline Functions diagram observations.
---

# Diagram Render Audit

Use this protocol in each diagram migration PR (#231–#383). A successful build or
syntax check is not a visual review. This sample establishes a repeatable method,
not approval of the sampled diagrams or completion of the full-coverage tracker
[#217](https://github.com/yeongseon/azure-functions-practical-guide/issues/217).

## Prerequisites

- Use the existing [local documentation setup](index.md#quick-start), a browser
  with developer tools, and network access to the configured Mermaid CDN.
- Record the source commit, observation date/time zone, browser/version, viewport
  in CSS pixels, device scale factor, page route and diagram key. A live page is
  supplementary evidence unless its deployed revision is known.
- Locate the exact `page#diagram-id` in the [manifest](../reference/diagram-manifest.json),
  then reconcile its source comment, fence, provenance and owning migration issue
  with the current tree. The inventory's genre is a candidate, not an editorial
  classification. Do not regenerate the manifest merely to record a render audit.

## Browser Procedure

### Build and Open the Actual Site

From the repository root, build and serve the generated HTML in one terminal:

```bash
mkdocs build --strict
python -m http.server 8000 --bind 127.0.0.1 --directory site
```

Open `http://127.0.0.1:8000/platform/architecture/#architecture-at-a-glance`
for `docs/platform/architecture/index.md#functions-architecture-overview`, or
`http://127.0.0.1:8000/troubleshooting/playbooks/queue-piling-up/#1-summary`
for `docs/troubleshooting/playbooks/queue-piling-up.md#1-summary`.
Diagram comments are source identifiers, **not necessarily HTML anchors**: use
the nearest heading and verify the diagram by its labels and source order.
`mkdocs serve --dev-addr 127.0.0.1:8000` is an alternative preview server; stop
the static server first. Do not serve the source Markdown as the rendered site.

1. Start with a fresh page load at browser zoom 100%. Wait for the CDN, page
   load and fonts, then scroll the selected diagram into view. Inspect the
   **pixels**, not just the presence of a container. If automating with existing
   browser tooling, wait for `networkidle`, `document.fonts.ready` and the diagram
   host's visible bounding box, then take and open a screenshot. None of those
   waits alone proves that drawing succeeded.
2. In DevTools responsive mode set **1440 × 1000**, then **390 × 1000** CSS pixels.
   Record device scale factor (the sample used 1, not a physical phone). At each
   width use the site's palette toggle for **default** and **slate**. Confirm
   `body[data-md-color-scheme]` in Elements; OS color-scheme emulation alone does
   not establish the selected Material palette. Check the in-place palette change
   as well as a fresh navigation. If instant navigation is enabled, repeat after
   following an internal link and waiting for Material's `document$` update.
3. Capture the inline diagram with its nearby explanation. Click the diagram to
   open the existing zoom overlay; wheel/pinch to enlarge, drag to inspect both
   ends and all branches, then press Escape or Close. Record whether labels
   actually became easier to read, anything clipped, and any theme change.
   Overlay zoom is not browser zoom. Optionally repeat at **200% browser zoom**
   and record it separately; changing device scale factor is not browser zoom.
4. Open **every captured image** before writing observations. Record exact labels,
   arrows, collisions and omitted semantics; attach sanitized before/after pairs
   to the PR or retain them outside Git with a shareable evidence reference.
   Capture the same cases before editing and after the final diagram edit.
   Do not commit derived PNGs or add them to the Portal capture manifest; see
   the [composition ADR](../reference/adr-diagram-composition.md#over-engineering-assessment).
5. Use the checklist below per diagram. A failed cell is a finding, not permission
   to silently drop that case. Link findings to the owning migration issue;
   renderer/overlay findings also belong in #217's final review. Run existing
   source, privacy, diagram and strict-build checks without weakening them.

### Avoid the Empty-Container False Negative

On the sampled build, Material converts `pre.mermaid` into `div.mermaid`, renders
the SVG, and installs it in a **closed shadow root**. Consequently the host's
`innerHTML` is empty, `shadowRoot` is null, and ordinary document SVG selectors
find nothing **even while the diagram is visible**. The built Material bundle's
Mermaid handler calls `mermaid.initialize({startOnLoad:false, ...})`,
`mermaid.render(...)`, and `attachShadow({mode:"closed"})`. The lack of a
repository-authored initializer does not mean no initialization occurs.

Use actual screenshots as the primary check. Do not run `mermaid.run()` against
already processed hosts: that is a different rendering path, not a reader's
automatic page load. In this audit it rejected on the processed page even though
the preceding automatic render was visible. An earlier report's “Could not find
a suitable point for the given distance” does not establish a site-load failure
or a font/subgraph defect without a blank screenshot and a minimal reproduction.

If a future page really is blank, preserve console/network errors and compare a
fresh local build with the live route. Check CDN completion, fonts, visible
layout, palette and browser version before classifying it as a sandbox artifact
or reader-facing defect. Only then use a **compatibility-only fallback** in a
throwaway page: fetch the unmodified built HTML, extract the original selected
`pre.mermaid` fence text before Material replaces it, load the site's pinned
Mermaid **10.9.1**, initialize with `startOnLoad:false`, and call `mermaid.render`
with a unique ID into a visible page container. Record every overridden setting.
That fallback proves only diagram compatibility, **not automatic site rendering**;
do not replace a failed automatic matrix cell with its result. No fallback or
additional browser package is needed for the successful automatic procedure above.

## Per-Diagram Sampling Checklist

Copy this block into a migration PR body once per exact key. Replace every
`NOT_CHECKED` with `PASS` or `FAIL` only after observing that case; keep a reason
for unperformed checks. `PASS` means readable and semantically correct, not just
“an SVG exists.” Use `not applicable: reason` for absent topology/fault features.

~~~~text
### Diagram render sample
- Key / diagram-id / owning issue:
- Source SHA / date and time zone / route and heading:
- Observer: AI-reviewer observation or named human observation:
- Human visual approval: NOT_DONE (change only after actual human approval)
- Browser/version / CSS viewport height / device scale factor / load mode:
- Type: topology | invocation flow | decision | sequence | evidence chain | other
- One reader question and one-sentence takeaway:
- Provenance: NOT_CHECKED — matching diagram-id comment + content_sources.diagrams
  entry; source type/justification; exact en-us Learn URLs and claims checked:

| Width | Palette | Inline | Overlay zoom + pan | Evidence reference / finding |
|---|---|---|---|---|
| 1440 | default | NOT_CHECKED | NOT_CHECKED | |
| 1440 | slate | NOT_CHECKED | NOT_CHECKED | |
| 390 | default | NOT_CHECKED | NOT_CHECKED | |
| 390 | slate | NOT_CHECKED | NOT_CHECKED | |

- Optional 200% browser zoom: NOT_CHECKED — reason or observations:
- Automatic rendering vs manual compatibility fallback; console/network errors:
- Arrows: NOT_CHECKED — invocation, control/metadata, dependency, return or order;
  explain line legend; do not imply a measured network trace.
- Fault/decision: NOT_CHECKED — symptom -> evidence -> next decision; label every
  branch, start and end; distinguish evidence, hypothesis and confirmed verdict.
  For sequences check participants, message direction and temporal order instead.
- Network boundaries: NOT_CHECKED — identify hosting plan and integration mode.
  Do not infer customer-subnet containment from multitenant VNet integration;
  documented ASE hosting is a distinct case where the environment and hosted apps
  run within a customer-VNet subnet. A PE is a NIC in a subnet providing private
  inbound access to its target service, not containment of that service. Regional
  VNet integration provides outbound connectivity through a delegated subnet, not
  private inbound access; check plan-specific support and delegation. Show Private
  DNS zones as linked to VNets, not contained within them.
- Accessibility: NOT_CHECKED — meaningful accTitle/accDescr or nearby caption;
  accessible name/description checked; meaning not conveyed by colour alone.
- Readability: NOT_CHECKED — label size, whitespace, hierarchy, viewBox behavior,
  clipping, collisions, arrow routing, contrast and readable caption at each size.
- Prose consistency: NOT_CHECKED — title/takeaway/caption match the actual arrows.
- Evidence honesty: NOT_CHECKED — documented / observed / inferred / illustrative;
  identify unverified mechanisms; no invented Azure runs or refreshed test dates.
- Before/after evidence (same width/palette/zoom; images opened, outside Git):
- Findings / exception rationale / owning migration issue / remaining checks:
~~~~

These are the guide-native criteria from #211: one question, deliberate hierarchy,
fault-aware mapping, mechanism-appropriate types, accessible responsive figures,
and source-backed explanations. Follow the [local content contract](content-contract.md),
not another repository's presentation rulebook. The shared topology grammar is a
semantic boundary check, not a requirement for a new renderer.

## Sample Observations — 2026-11-03 UTC

**AI-reviewer observations from actual automatic browser renders**, pinned to
`origin/main` **`e1c409ee42d179d65ff0033295d998dc96fb1953`**. Human visual approval:
**NOT_DONE**. This is a pre-migration baseline; no sampled diagram was changed.
Screenshots were opened and inspected outside Git. Their reproducible filename
pattern was `394-{host|queue}-{1440|390}-{default|slate}-{inline|zoom}.png`
(16 images); the findings below are retained even when temporary images expire.

### Rendering Investigation

The automatic local-site matrix used system Chrome **145.0.7632.67**, headless,
viewport height 1000, device scale factor 1, light/dark media emulation plus the
explicit Material palette attribute, `networkidle`, font readiness and scrolling
into view. It made **no manual Mermaid rendering calls**. Both diagrams rendered
in every cell without page errors. Installed font families included DejaVu Sans,
Liberation Sans and FreeSans; no font installation was needed.

The architecture figure also rendered automatically in the Playwright browser,
in headed system Chrome under Xvfb, and on the live architecture URL in system
Chrome; screenshots of those controls were inspected. Live deployment SHA was
not established, so it is not the pinned baseline. The empty-light-DOM symptom
is **(a) an inspection artifact**, explained by Material's closed shadow root,
not evidence of (b) a blank site for readers. The overlay problems below **are**
reader-facing defects. No zero-text-metrics cause was demonstrated. Instant
navigation and 200% browser zoom were **NOT_CHECKED**; the required zoom sample
used the site's click overlay and a wheel-up event, not CSS zoom.

### Sample Keys and Outcomes

| Alias | Exact key | Classification / owner |
|---|---|---|
| host | `docs/platform/architecture/index.md#functions-architecture-overview` | Host/trigger topology with invocation and control/dependency edges; migration #234, batch #212 |
| queue | `docs/troubleshooting/playbooks/queue-piling-up.md#1-summary` | Diagnostic decision flow, not network topology; migration #273, batch #215 |

Both comments and matching `content_sources.diagrams` entries are present.
Both are declared `self-generated` with justifications and `based_on` Learn URLs,
not observed deployment traces. The queue-trigger source supports retry/poison
behavior, not a deterministic verdict from one metric. The networking source
distinguishes inbound PE from outbound integration. This scoped review does not
attest every claim in either page or change manifest provenance status.

The following verdicts assess **legibility**, not rendering presence (which
succeeded in all eight inline cases). Each cell was inspected in both palettes.

| Sample / width | default inline | slate inline | default overlay | slate overlay |
|---|---|---|---|---|
| host / 1440 | FAIL: grouped titles collide | FAIL: same collision | FAIL: smaller labels than inline | FAIL: pale text on white |
| host / 390 | FAIL: labels too small | FAIL: labels too small | FAIL: side nodes outside viewport | FAIL: clipping and pale text |
| queue / 1440 | FAIL: small labels despite large diamonds | FAIL: same small labels | FAIL: shrinks to a small central panel | FAIL: pale text on white |
| queue / 390 | FAIL: branch/leaf labels unreadable | FAIL: same labels | FAIL: outer leaves outside viewport | FAIL: clipping and pale text |

### Concrete Findings and Semantic Review

- **Host — #234:** At 1440 the “Functions host runtime”, “Language worker process”,
  “Storage account” and “Scale controller” labels are readable, but “Hosting plan”,
  its plan list and “Function app instance” overlap. Long arrows from the host
  crowd the Storage/monitoring row. At 390 none of those labels is comfortably
  readable inline; surrounding explanatory bullets remain readable. Preserve the
  host/worker grouping while separating titles and reducing density in migration.
- **Host arrow meaning — #234:** Event sources branch to trigger/binding
  extensions and the scale controller; configuration points to the host, host
  points to worker/storage/monitoring, worker points to downstream services.
  All use the same unlabelled arrow style, conflating invocation, scale control,
  configuration and telemetry without a legend. ARM is disconnected. The prose
  helps interpret these conceptual paths but does not make them measured traces
  or a universal per-plan scale-controller model. Add explicit edge meaning and
  plan qualifications during migration, not an invented physical topology.
- **Queue — #273:** The start is “Queue count and age rising”; four diamonds ask
  about retries/poison, scale events, P95/P99 regression and dependency spikes.
  At 1440 Yes/No labels can be followed and no edge crossing or label collision
  was apparent, but the long mitigation leaf labels are small. At 390 neither
  Yes/No nor “H2 Poison-message loop” or the mitigation text is comfortably
  readable. Diamonds consume much more space than their text. Rebalance layout
  and label sizes without replacing this decision tree with a topology.
- **Queue evidence meaning — #273:** The H1–H4 rectangles lead directly to
  mitigation leaves; the final No branch leads to “Re-check host config, release
  timeline, and trigger settings”. These are diagnostic candidates and actions,
  not confirmed incident verdicts. The diagram does not show falsification or
  competing concurrent causes. Preserve the healthy-enqueue assumption in the
  caption and make evidence → hypothesis → next check explicit; absence of scale
  events alone does not prove H1. The playbook's later evidence sections are
  necessary context, not evidence that this audit ran an Azure experiment.
- **Overlay — #217, affecting #234/#273:** Clicking opens a white panel; at 1440
  the moved diagrams become smaller than inline. A wheel-up event did not yield
  readable mobile branch labels: at 390 the side nodes/leaves extend beyond the
  viewport. In slate, formerly light text/edges become faint against white.
  The visible zoom hint is not proof of usable enlargement. Review overlay
  sizing, pan reachability and theme inheritance separately; do not mark a
  migration's dark/zoom cell passed merely because the overlay opens.
- **Accessibility — #234/#273:** Neither source supplies `accTitle`/`accDescr`.
  Nearby headings and explanation bullets (host) or summary table/assumption
  sentence (queue) give context, but an accessible SVG name was **NOT_CHECKED**.
  Rectangles/diamonds, text and arrow direction carry meaning without colour;
  there is no colour-only fault verdict. Add an intentional caption/takeaway or
  accessible description and verify the accessibility tree in migration.
- **Network boundary applicability:** Neither sample draws a VNet, subnet,
  Private Endpoint or Private DNS zone. The host is inside a logical hosting-plan
  group, **not** a customer subnet. No PE placement can be approved from these
  samples; the network-boundary checklist is **not applicable: absent**, not a
  sampled networking pass. Future networking samples must apply every boundary
  rule above, with plan-specific Learn sources and the shared topology contract.

These findings do not block publishing an honest baseline audit, but they prevent
calling these diagrams visually approved. Full coverage, migration before/after
inspection, human approval and renderer follow-up remain with the owning issues
and #217; this sample closes none of those trackers.

## See Also

- [Contributing](index.md)
- [Documentation Content Contract](content-contract.md#mermaid-diagrams)
- [Diagram Inventory](../reference/diagram-inventory.md)
- [Composition ADR](../reference/adr-diagram-composition.md)
- [Architecture Sample](../platform/architecture/index.md#architecture-at-a-glance)
- [Queue Decision Sample](../troubleshooting/playbooks/queue-piling-up.md#1-summary)

## Sources

- [Guide-native quality criteria — #211](https://github.com/yeongseon/azure-functions-practical-guide/issues/211)
- [Final coverage and bounded audit scope — #217](https://github.com/yeongseon/azure-functions-practical-guide/issues/217)
- [Shared Azure topology grammar — App Service #296](https://github.com/yeongseon/azure-app-service-practical-guide/issues/296)
- [Functions networking options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options)
- [App Service Environment overview](https://learn.microsoft.com/en-us/azure/app-service/environment/overview)
- [Queue trigger behavior](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue-trigger)
- [Material native Mermaid integration](https://squidfunk.github.io/mkdocs-material/reference/diagrams/)
