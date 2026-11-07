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
   width use the header's **Switch to dark mode** control for **slate**, and
   **Switch to light mode** for **default**. Verify the resulting
   `body[data-md-color-scheme]` attribute in Elements; OS color-scheme emulation
   alone does not establish the selected Material palette. Wait for palette
   transitions to finish before capturing. Check the in-place palette change
   as well as a fresh navigation. If instant navigation is enabled, repeat after
   following an internal link and waiting for Material's `document$` update.
3. Capture the inline diagram with its nearby explanation. Click the diagram to
   open the existing zoom overlay. Wait for its opacity/transform transitions to
   finish before capturing; `.mermaid-zoom-visible` alone is too early and can
   capture prose showing through the opening fade. Wheel/pinch to enlarge, drag
   to inspect both ends and all branches, then press Escape or Close. Record the
   wheel event count/delta or pinch amount, resulting scale when available, drag
   distance, and whether pan persists after release (read the computed transform
   while held and after settling). Record whether labels actually became easier
   to read, anything clipped, and any theme change.
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

For a single-key migration PR, copy this block once. For multi-key PRs (for
example, an issue owning eight diagrams), record shared browser/SHA/environment
details once per PR, with per-key matrices and findings underneath; do not repeat
the whole block. Replace every
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
- Wheel/pinch amount / resulting scale / drag distance / pan persists on release:
- Palette and overlay transitions settled before capture: NOT_CHECKED
- Automatic rendering vs manual compatibility fallback; console/network errors:
- Shared grammar: NOT_CHECKED — consistent component names/icons and stable
  unchanged components across variants; distinguish DNS/auth/control from data.
- Arrows: NOT_CHECKED — invocation, control/metadata, dependency, return or order;
  explain line legend; do not imply a measured network trace.
- Fault/decision: NOT_CHECKED — symptom -> evidence -> next decision; label every
  branch, start and end; distinguish evidence, hypothesis and confirmed verdict.
  For sequences check participants, message direction and temporal order instead.
- Fault placement, when applicable: NOT_CHECKED — normal path and accessible fault
  marker at the affected component/edge, with evidence and next check.
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
used the site's click overlay and one wheel-up event, not CSS zoom. That baseline
did not retain the wheel delta, resulting scale or post-release pan persistence;
the follow-up below records a measured interaction separately.

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

The overlay cells describe the sampled opening/one-wheel state, not the maximum
enlargement achievable through repeated wheel events.

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
- **Overlay — #217, affecting #234/#273:** In the sampled opening/one-wheel state,
   clicking opens a white panel; at 1440 the moved diagrams become smaller than
   inline. One wheel-up event did not yield
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

## Follow-up Interaction Observation — 2026-11-03 23:50–23:51 UTC

An independent reviewer reported the pan reset and repeated-wheel enlargement
first. A follow-up **AI-reviewer browser run** reproduced them on the built site
at source **`2ed31cfe162461d72b1477c724be6acd1b16af5e`**, using the host key/route
above, Playwright headless Chrome **145.0.0.0**, **1440 × 1000** CSS pixels,
device scale factor 1 and browser zoom 100%. This is separately timed evidence,
not a change to the baseline's date or attribution; human approval is **NOT_DONE**.
The diagram rendered automatically without manual Mermaid calls, while its light
DOM remained empty. The header controls selected slate/default and the body
attribute confirmed each palette. Captures waited 500 ms after overlay/palette
changes and final input; settled overlay opacity was 1.

- **Pan persistence — FAIL, existing interaction defect for #217:** Starting at
  `translate(0px, 0px) scale(1.5)`, a 100 CSS px rightward mouse drag produced
  `translate(100px, 0px) scale(1.5)` while held (computed
  `matrix(1.5, 0, 0, 1.5, 100, 0)`). On release it reset to
  `translate(0px, 0px) scale(1.5)` (computed `matrix(1.5, 0, 0, 1.5, 0, 0)`),
  still reset after 500 ms. Two `mermaid-zoom-overlay` IDs briefly existed just
  after release, returning to one after settling. This is consistent with the
  existing diagram click handler in `docs/javascripts/mermaid-zoom.js` reopening
  the overlay after a drag; it is not proof of every possible input path.
- **Repeated wheel enlargement — observed, not a usability pass:** Twenty
  wheel-up events, each `deltaY = -100` CSS px (20 ms between events), enlarged
  the host overlay from scale 1.5 to **3.5** (computed
  `matrix(3.5, 0, 0, 3.5, 0, 0)`) in both default and slate. Thus the earlier
  small-panel finding concerns the sampled opening/one-wheel state, not an
  inability to enlarge. At scale 3.5 the slate labels/edges remained pale on the
  white panel: **FAIL** for contrast. Pinch and mobile pan were **NOT_CHECKED**
  in this follow-up.

Five screenshots (inline, drag-held, released, default wheel-20 and slate
wheel-20) were opened outside Git, named `394-followup-host-*.png`. The measured
findings remain here if temporary captures expire. Fixing site JavaScript/CSS
is outside this audit PR; retain the interaction/contrast findings for #217 and
diagram repairs for #234/#273.

## Sample Observations — 2026-11-07 (Premium Blob Path, Fault Overlay, Sequence)

**AI-reviewer observations from actual automatic browser renders**, pinned to
`origin/main` **`bdd61acebf9a51f695fca43a69a8e37545166303`**, observed 2026-11-07
09:06 KST (00:06 UTC). Human visual approval: **NOT_DONE**. This second sample
covers the three cases the cross-guide parity checklist asks for that the
2026-11-03 sample did not: an Azure network/host topology with a private-endpoint
boundary, its fault overlay, and a non-topology typed view. No sampled diagram was
changed by this PR; no Azure resource was created or queried.

### Method

Chromium **156.0.8078.4** (headless, Playwright), viewports **1440 × 900** and
**390 × 900** CSS pixels, device scale factor 1, browser zoom 100%, the built site
served from `site/`, default and slate palettes selected through Material's stored
palette (checked by the rendered colours), automatic Material rendering with
no manual Mermaid calls. Because Material installs each SVG in a closed shadow root,
the inspection script made `attachShadow` open **before page load** (inspection
only; it does not alter layout), then read each rendered SVG. *Effective label
font* is the computed label font size multiplied by the SVG's rendered width over
its `viewBox` width, i.e. the size a reader sees. Every captured image was opened
before the notes below were written; images were kept outside Git (pattern
`394-r2-{key}-{1440|390}-{default|slate}.png`, 32 images).

### Sample Keys

| Alias | Exact key | Type / role |
|---|---|---|
| pe-normal | `docs/reference/functions-topology-templates.md#functions-v1-network-storage-normal` | Premium Blob-only host-storage slice: outbound VNet integration and Storage inbound private endpoint in separate subnets, Private DNS zone linked to the VNet |
| pe-fault | `docs/reference/functions-topology-templates.md#functions-v1-network-storage-failure` | Same slice with one illustrative fault on the integration → private-endpoint edge |
| sequence | `docs/reference/functions-topology-templates.md#functions-v1-worker-sequence` | Non-topology typed sequence: host ↔ isolated worker |
| decision | `docs/reference/troubleshooting.md#troubleshooting` | Categorical troubleshooting flow (migrated in #560) |

All four have a matching `diagram-id` comment, a `content_sources.diagrams` entry
and `accTitle`/`accDescr` (the accessible title and description exist on the
rendered SVG in every cell; this is not a screen-reader test). The templates are
Premium (multitenant) **illustrations**, not a measured network trace. They show the
Function host **outside** the customer VNet: this is correct for multitenant
hosting, where regional VNet integration provides outbound connectivity only. It
is **not** correct for an App Service Environment, where the environment and its
hosted apps run inside a customer-VNet subnet; the figures must not be reused for
that hosting model without redrawing the boundary. The diagram deliberately
omits the other storage endpoints (File, Queue, Table), as its justification says.

### Measured Legibility

Minimum effective label font in CSS px (identical in default and slate; no clipped
labels in any cell):

| Key | 1440 | 390 | Verdict at 390 |
|---|---:|---:|---|
| pe-normal | 16 | **5.4** | FAIL: boundary and edge labels unreadable inline |
| pe-fault | 16 | **5.4** | FAIL: same; the red edge cannot be told from the red endpoint |
| sequence | 16 | 10.4 | FAIL (marginal): readable with effort, below the 12 px target |
| decision | 16 | 16 | PASS |

The same templates' base and trigger variants measure 7.0 / 6.7 / 6.1 / 6.1 px at
390 (all FAIL) and 16 px at 1440, so the defect is systematic: wide logical
diagrams are scaled down to the narrow content column.

### Findings

- **Topology reading (1440, both palettes) — PASS with notes:** the VNet,
  VNet-integration subnet, private-endpoints subnet, Private Endpoint and Storage
  are distinguishable; the host, scale controller, event source and DNS zone sit
  outside the VNet; integration NIC → Private Endpoint → Blob reads in order. The
  bracketed boundary tags (`[VNet boundary]`, `[delegated]`, `[Inbound NIC]`) sit on
  the dashed borders, so the nesting is harder to read than it should be.
- **Fault overlay (1440) — PASS:** the failing edge is labelled `[FAULT /
  Illustrative] Connection blocked` and also drawn thick and red, so the state is
  not colour-only. The arrowhead still points at the endpoint, which could be read as an
  active connection; the label resolves it. The accessible description correctly
  says private DNS still resolves and to investigate routing/connectivity rather
  than assert a DNS fault. The red endpoint can be read as "the private endpoint
  is faulty" rather than "the connection to it is blocked"; the edge label is the
  disambiguator.
- **Narrow rendering (390) — FAIL:** the nested boundary titles collide with the
  dashed borders and bracketed tags, and the fault is not distinguishable. These
  defects belong to the template keys; they are recorded for the migrations that
  reuse them and for follow-up on the templates themselves. Nothing was repaired
  here.
- **Slate palette — PASS with a note:** node text has adequate contrast; the grey
  connector and boundary annotations are noticeably fainter than node text.
- **Sequence — PASS at 1440, marginal at 390:** participants, message direction and
  order are clear and the dashed return arrow does not depend on colour. The
  participant boxes are repeated at the bottom as Mermaid always does; the
  lifelines connect them.
- **Decision — PASS:** all branches converge on the same outcome, labels are
  legible at 390 in both palettes, and no topology boundary is implied.
- **Common-grammar check:** component vocabulary, the control/metadata (dotted)
  versus data/invocation (solid) distinction, the bracketed evidence-confidence tags
  (`[Configured]`, `[Illustrative]`, `[FAULT / Illustrative]`) and stable component
  identity between the normal and fault variants are consistent. DNS is drawn as a
  VNet-linked zone outside both subnets, and the Private Endpoint as a NIC in its
  own subnet, not as containing Storage.

### Zoom Overlay Observation (Premium Blob Path)

Opening **pe-normal** and inspecting the moved host's SVG:

| Build | Viewport | Opening scale | SVG size | Min effective font | Clipped |
|---|---|---:|---|---:|---|
| `main` at `bdd61ac` | 1440 | 1.5 | 450 × 321 | **6.8** | no |
| `main` at `bdd61ac` | 390 | 1.5 | 450 × 321 | **6.8** | yes (both sides) |
| PR #565 head `3bc5b31` (unmerged) | 1440 | 1.10 | 1128 × 806 | 17.1 | no |
| PR #565 head `3bc5b31` (unmerged) | 390 | 0.75 | 768 × 549 | 11.6 | pannable, opens at the left edge |

On `main` the overlay shrinks this wide diagram to roughly a quarter of its inline
size (inline 16 px → overlay 6.8 px at 1440), because the host collapses to a
default width inside the overlay's flex container; repeated wheel events can
enlarge it, but the opening view is worse than the inline view. That is a
renderer finding for #217, not a template defect; PR #565 changes the opening size
and is recorded here only as a separately measured, unmerged build.

### Cross-guide Check Inventory (Workflow-file Level)

The following was read from each repository's `.github/workflows/` listing on
2026-11-07; it identifies which workflows exist and does **not** show that a
workflow enforces the same rule or that it passed.

| Check | Functions | App Service |
|---|---|---|
| Strict MkDocs build | `docs.yml`, `ci.yml` | `docs.yml` |
| Mermaid format/syntax, content sources, manifest ownership/drift, PII | `validate-content-sources.yml` | `validate-content-sources.yml` |
| Documentation repetition | `validate-repetition.yml` | `validate-repetition.yml` |
| Visual coverage (advisory) | `validate-visual-content.yml` | `validate-visual-content.yml` |
| PR title convention | `pr-title.yml` | `pr-title.yml` |
| Live Azure end-to-end (guarded) | `e2e-azure.yml` | `e2e-azure.yml` |
| Golden-status validation and refresh | **no workflow file** | `validate-golden-status.yml`, `refresh-golden-status.yml` |
| Validation freshness | **no workflow file** | `validation-freshness.yml` |
| Project metadata/operations | **no workflow file** | `project-operations.yml` |

Possible parity gaps to be checked, not assumed, in follow-up work: the three
App Service workflows with no Functions counterpart file. None of the Functions
workflows renders the diagrams in a browser (the App Service workflows were read by
file name only), so every cell of the matrices in this page is a manual or locally
scripted observation, not an automated gate.

### Outcome

The Premium Blob-path pair is semantically sound for the multitenant Premium
hosting model but fails the 390 px legibility criterion; the sequence is marginal
at 390 and the decision flow passes. Human/maintainer visual acceptance is
**NOT_DONE** and is not implied by this audit, by green CI or by these captures.
200% browser zoom, instant navigation, pinch on a physical device, screen-reader
output and cross-browser rendering were **NOT_CHECKED**.

## Full-coverage Measurement — 2026-11-08

**Automated agent measurement, not human visual approval.** Every published diagram
in the manifest (**578** diagrams on **364** pages) was rendered on a build of
`main` at `12168ee` with Chromium (Playwright), at **390** and **1440** CSS pixels,
default palette. *Effective label size* is the computed label font multiplied by
the SVG's rendered width over its `viewBox` width. Material's closed shadow roots
were opened before page load for inspection only. Per-diagram state is recorded in
the [manifest](../reference/diagram-manifest.json): every migration-required record
is `completed` or `exception` with a measured reason; none is `in-progress`.

| Check | 390 px | 1440 px |
|---|---:|---:|
| Diagrams rendered / not rendered | 578 / 0 | 578 / 0 |
| Labels clipped by the SVG | 0 | 0 |
| Minimum effective label size under 12 px | 8 | 10 (before #618), see below |
| Without accessible title and description | 5 | 5 |

- **Under 12 px at 390 px (8):** the six topology flowchart templates in
  [Functions Topology Templates](../reference/functions-topology-templates.md)
  (5.4 to 7.0 px; a documented limitation, spacing and line-break experiments reach at
  most 8.6 px) and the two generator-owned status pie charts
  (`content-validation-status.md` 10.6 px, `validation-status.md` 9.1 px), which are
  excluded from migration because a script regenerates them.
- **Under 12 px at 1440 px (10):** ten lab evidence-timeline Gantt titles at 10.6 px,
  fixed in #618 (title size 16 px; labels 12.1 px or more at both widths).
- **Without accessible title and description (5):** the diagram-orientation example
  in `content-contract.md` and the two generated pie charts (excluded records), and the
  two timeline charts in the `auth-config` playbooks (Mermaid's timeline type does not
  emit `accTitle`/`accDescr` to the SVG; their adjacent legend tables are the text
  alternative, see the manifest exception text).
- **Not covered by this measurement:** slate palette for every diagram (sampled in the
  per-PR reviews only), the zoom viewer for every diagram, instant navigation, 200%
  browser zoom, screen readers, physical phones, other browsers, and **human visual
  approval of any diagram**. Exceptions in the manifest still need maintainer sign-off,
  which is tracked in #217.

## See Also

- [Contributing](index.md)
- [Documentation Content Contract](content-contract.md#mermaid-diagrams)
- [Diagram Inventory](../reference/diagram-inventory.md)
- [Composition ADR](../reference/adr-diagram-composition.md)
- [Architecture Sample](../platform/architecture/index.md#architecture-at-a-glance)
- [Queue Decision Sample](../troubleshooting/playbooks/queue-piling-up.md#1-summary)
- [Functions Topology Templates](../reference/functions-topology-templates.md)

## Sources

- [Guide-native quality criteria — #211](https://github.com/yeongseon/azure-functions-practical-guide/issues/211)
- [Final coverage and bounded audit scope — #217](https://github.com/yeongseon/azure-functions-practical-guide/issues/217)
- [Shared Azure topology grammar — App Service #296](https://github.com/yeongseon/azure-app-service-practical-guide/issues/296)
- [Functions networking options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options)
- [App Service Environment overview](https://learn.microsoft.com/en-us/azure/app-service/environment/overview)
- [Queue trigger behavior](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue-trigger)
- [Private endpoint DNS configuration](https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-dns)
- [Material native Mermaid integration](https://squidfunk.github.io/mkdocs-material/reference/diagrams/)
