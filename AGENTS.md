# AGENTS.md

Guidance for AI agents working in this repository.

## Project Overview

**Azure Functions Practical Guide** — a unified documentation hub, reference applications, and hands-on troubleshooting labs for building and operating serverless applications on Azure Functions.

- **Live site**: <https://yeongseon.github.io/azure-functions-practical-guide/>
- **Repository**: <https://github.com/yeongseon/azure-functions-practical-guide>

## Series-Wide Documentation Contract

This repository is part of the Azure Practical Guide series. All repositories in the series must preserve a consistent reader experience while allowing repository-specific extensions.

### Core Sections

Every service-focused repository SHOULD use these core sections unless the repository-specific addendum explains an exception.

| Section | Required | Purpose |
|---|---:|---|
| `Start Here` | Yes | Entry points, overview, learning paths, repository map |
| `Platform` | Yes | Service concepts, architecture, core behavior |
| `Best Practices` | Yes | Production patterns, anti-patterns, design guidance |
| `Operations` | Yes | Day-2 operational procedures and verification |
| `Troubleshooting` | Yes | Symptom-based diagnosis, playbooks, evidence collection |
| `Reference` | Yes | CLI, KQL, limits, glossary, decision tables |

### Approved Extension Sections

| Section | Use When |
|---|---|
| `Tutorials` | The repository provides hands-on learning or lab sequences |
| `Lab Guides` | Reproducible experiments or validation exercises are first-class content |
| `Language Guides` | The service has language/runtime-specific implementation tutorials |
| `SDK Guides` | The service is primarily consumed through SDKs |
| `Service Guides` | The repository configures or monitors multiple Azure services |
| `Workload Guides` | The repository is architecture/workload oriented |
| `Architecture Reviews` | The repository includes architecture review methodology and playbooks |
| `Design Labs` | The repository includes architecture design exercises |
| `Visualization` | Visual maps are a deliberate learning surface, not generated leftovers |
| `Meta` | Repository taxonomy, content model, or generated metadata |

Do not create a new top-level section if the content can fit under one of the core or approved extension sections.

## Functions-Specific Addendum

This repository is an advanced Azure Functions runtime guide. It carries a legacy diagram-provenance schema that is being migrated to the series-standard shape.

### Functions-Specific Diagram Provenance Migration

Legacy `content_sources.references` is accepted only for existing pages.

When editing a page that contains Mermaid diagrams:

1. Add `content_sources.diagrams[]`.
2. Add one entry per Mermaid block.
3. Ensure the diagram `id` matches the HTML comment before the fence.
4. Do not copy legacy reference-only pages into sibling repositories.
5. New pages must never use the legacy shape.

## Repository Structure

```text
.
├── .github/
│   └── workflows/              # GitHub Pages deployment
├── apps/
│   ├── python/                 # Python reference application (v2 model)
│   ├── nodejs/                 # Node.js reference application (v4 model)
│   ├── dotnet/                 # .NET reference application (isolated worker)
│   └── java/                   # Java reference application (Maven)
├── docs/
│   ├── assets/                 # Images, icons
│   ├── best-practices/         # Production patterns and anti-patterns (9 pages)
│   ├── javascripts/            # Mermaid zoom JS
│   ├── language-guides/
│   │   ├── python/             # Python — 4 plans × 7-8 tutorials + recipes
│   │   ├── nodejs/             # Node.js — 4 plans × 7-8 tutorials + recipes
│   │   ├── java/               # Java — 4 plans × 7-8 tutorials + recipes
│   │   └── dotnet/             # .NET — 4 plans × 7-8 tutorials + recipes
│   ├── operations/             # Day-2 operational execution (9 pages)
│   ├── platform/               # Architecture and design decisions (7 pages)
│   ├── reference/              # CLI cheatsheet, host.json, limits (5 pages)
│   ├── start-here/             # Overview, learning paths, repository map (4 pages)
│   ├── stylesheets/            # Custom CSS (mermaid zoom, etc.)
│   └── troubleshooting/        # Troubleshooting hub
│       ├── architecture.md
│       ├── evidence-map.md
│       ├── first-10-minutes/   # First-10-minutes guides
│       ├── kql/                # KQL query packs
│       ├── lab-guides/         # Lab guide documents
│       ├── methodology/        # Methodology guides
│       └── playbooks/          # Playbook documents
├── infra/                      # Bicep templates for all hosting plans
│   ├── consumption/
│   ├── flex-consumption/
│   ├── premium/
│   ├── dedicated/
│   └── modules/
├── labs/                       # Lab infrastructure + app source
│   ├── code-storage-verification/
│   ├── cold-start/
│   ├── dns-vnet-resolution/
│   ├── event-hub-checkpoint-lag/
│   ├── managed-identity-auth/
│   ├── queue-backlog-scaling/
│   └── storage-access-failure/
└── mkdocs.yml                  # MkDocs Material configuration (7-tab nav)
```

## Start Here Rules

`Start Here` is orientation content. It must not become a language tutorial, SDK tutorial, operations runbook, troubleshooting playbook, or lab guide.

Required pages:

| Page | Purpose |
|---|---|
| `overview.md` | Who this guide is for, what is in scope, and what is out of scope |
| `learning-paths.md` | Role-based and experience-based reading paths |
| `repository-map.md` | Map of major sections and when to use them |

Optional pages:

| Page Pattern | Purpose |
|---|---|
| `when-to-use-*.md` | Service selection guidance |
| `prerequisites.md` | Required tools, permissions, and accounts |
| `common-scenarios.md` | Common use cases |
| `*-vs-other-compute.md` | Positioning against neighboring Azure services |
| `how-to-use-this-guide.md` | Reader navigation guidance |

`learning-paths.md` MUST:

- Start with role-based or goal-based paths.
- Link to tutorials instead of embedding a full tutorial sequence.
- Avoid service-specific code walkthroughs except short examples.
- Avoid `content_validation` unless this repository explicitly includes Start Here pages in content validation scope.

Preferred title:

```markdown
# Learning Paths
```

Avoid:

```markdown
# Tutorial: {Service} for {Language}
```

## Navigation Budget

The left navigation should help orientation, not expose every file.

Recommended:

- Top-level sections SHOULD stay between 6 and 9 items.
- Direct children under a top-level section SHOULD stay between 5 and 8 items.
- Large collections such as tutorials, recipes, KQL packs, lab guides, and playbooks SHOULD be listed on index pages rather than fully expanded in `mkdocs.yml`.
- Use hub pages, tables, tags, and search for deep inventory.
- Keep `mkdocs.yml` readable enough that a contributor can understand the site structure without scrolling through hundreds of deep links.

Preferred troubleshooting structure:

```text
Troubleshooting
├─ Overview
├─ Quick Diagnosis
├─ Decision Tree
├─ First 10 Minutes
├─ Playbooks
├─ KQL Query Packs
└─ Labs
```

Avoid exposing every individual playbook, KQL query, and lab guide in `mkdocs.yml` unless the repository is intentionally small.

## Content Validation Scope

`content_validation` is required for factual-claim pages, not for every Markdown file.

Required by default:

- `docs/platform/**`
- `docs/best-practices/**`
- `docs/operations/**`
- factual troubleshooting methodology/playbook pages

Usually out of scope:

- `docs/start-here/**`
- `docs/reference/**`
- `docs/language-guides/**`
- `docs/sdk-guides/**`
- `docs/tutorials/**`
- `docs/troubleshooting/kql/**`
- `docs/troubleshooting/lab-guides/**`
- generated dashboards
- navigation-only index pages

Content-type-specific rules:

- Tutorials use `validation`.
- Labs use evidence and falsification integrity.
- KQL packs document query purpose, expected interpretation, required tables, and assumptions.
- KQL packs do not need `content_validation` unless they make factual platform claims outside the query explanation.
- Never fabricate validation dates or test results.

## Mermaid Diagrams

Use Mermaid diagrams when they clarify architecture, flow, dependency, decision logic, or troubleshooting paths.

Required for:

- Platform architecture pages
- Complex operations pages
- Decision trees
- Troubleshooting playbooks with multi-step diagnosis
- Lab guides with failure progression or evidence timelines
- Architecture review or design decision flows

Optional for:

- Reference tables
- CLI cheatsheets
- Glossary pages
- Generated validation dashboards
- Short landing pages
- Simple tutorial steps where prose is clearer

Do not add a diagram just to satisfy a checkbox. A diagram must explain something better than prose or a table.

### Diagram Orientation Rule

- **Sequential flows with 5+ nodes**: Use `flowchart TD` (top-down) to prevent horizontal overflow.
- **Short diagrams with fewer than 5 nodes**: `flowchart LR` (left-right) is acceptable.
- **Layered architecture diagrams** (e.g., network layers, stack diagrams): Always use `flowchart TD`.

```mermaid
%% CORRECT — 5+ node sequential flow uses TD
flowchart TD
    A[Commit] --> B[Build and test]
    B --> C[Package artifact]
    C --> D[Deploy to staging]
    D --> E[Validation]
    E --> F[Swap to production]

%% WRONG — long horizontal overflow
flowchart LR
    A[Commit] --> B[Build and test] --> C[Package] --> D[Deploy] --> E[Validate] --> F[Swap]
```

## Image and Screenshot Rules

Images must support the reader's task. Do not add screenshots only for decoration.

Every referenced image MUST have:

- Descriptive alt text.
- A nearby explanation of what the reader should verify.
- No real subscription IDs, tenant IDs, object IDs, emails, phone numbers, secrets, keys, connection strings, or customer data.
- Visual verification before merge when the image is referenced from Markdown.

Recommended explanation pattern:

```markdown
![Container App overview showing a healthy revision](../assets/example.png)

Purpose: Confirm why this image exists.
Look for: Tell the reader what values or states to confirm.
Expected result: State the healthy or expected condition.
Next step: Link the image to the next action.
```

Portal screenshots:

- Prefer text replacement over black-box redaction.
- Use black-box masking only for unavoidable avatar/profile pixels and only with the repository-approved mask color.
- If a screenshot cannot be visually verified, remove the Markdown reference or disclose the debt explicitly in the PR.

### Authenticating the capture browser (Conditional Access)

Portal captures use the reusable PII helper at [`scripts/portal-capture-helpers.js`](scripts/portal-capture-helpers.js) (usage in [`scripts/portal-capture-helpers.md`](scripts/portal-capture-helpers.md)). The capture browser MUST reuse a **device-compliant, interactively signed-in** session. A fresh, isolated Chromium — whether launched by standalone Playwright or by the MCP browser tool — is **not** an Intune-enrolled / device-compliant browser, so it CANNOT pass Microsoft Entra Conditional Access for the MSIT (`ms.portal.azure.com`) tenant. It loops on the sign-in / `ConditionalAccess/Enrollment` ("install Company Portal") wall. **Do not** burn cycles trying to defeat this from automation — it is a device-level security control, not a cookie problem.

Working pattern (attach to a real, human-authenticated Chrome over CDP):

1. **Launch the user's Chrome with a dedicated debug profile and a remote-debugging port.** A dedicated `--user-data-dir` avoids Chrome's block on debugging the default profile, and OS-level Platform SSO / Company Portal still satisfies device compliance:
    ```bash
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
      --remote-debugging-port=9222 \
      --user-data-dir="$HOME/.chrome-portal-capture" \
      --no-first-run --no-default-browser-check \
      "https://ms.portal.azure.com/"
    ```
2. **The human signs in interactively (including MFA) and navigates to the target blade.** The agent CANNOT complete MFA — hand this step to the user explicitly and wait.
3. **Verify the port is bound before attaching:** `curl -s http://localhost:9222/json/version`, and poll `http://localhost:9222/json` to detect when the target blade URL has loaded.
4. **Attach Playwright over CDP** with `chromium.connectOverCDP('http://localhost:9222')`, pick the page whose URL contains `portal.azure.com`, apply the PII helper, then screenshot. `browser.close()` on a CDP-attached browser only detaches the debugger; it does NOT close the user's Chrome.

Common failure: relaunching the Chrome binary while Chrome is already running just opens a tab in the existing (non-debug) process and silently ignores `--remote-debugging-port`. Always confirm the port with `curl`/`nc` before assuming the debug instance is up.

### Manifest-driven capture pipeline

Portal screenshots are managed as **build artifacts driven by a manifest** (`scripts/capture/`), not hand-placed files. Docs reference a screenshot by a **stable ID** via the `shot()` macro, so re-capturing a blade overwrites the same `.webp` and never requires editing markdown.

- Register every capture in `scripts/capture/manifest.yaml` with a stable `id` (equal to the file stem), `file` path under `docs/assets/`, and accurate `alt` text.
- Reference it in markdown with `[[[ shot("<id>") ]]]` (custom Jinja delimiters `[[[ ]]]` / `[[% %]]` / `[[# #]]`, configured in `mkdocs.yml`, avoid collisions with `{{ }}`).
- Encode/downscale raw PNGs to WebP with the `capture-optimize-webp` CLI; refresh existing captures through the `capture-diff-gate` CLI (both provided by the `azure-guide-capture-toolkit` package; below `diff_threshold` only `verified` is bumped, image bytes untouched).
- Screenshots may be committed as WebP produced by this pipeline. When a capture is optimized to WebP, the **final rendered `.webp`** — not only the raw PNG — MUST be visually verified for PII and caption accuracy before merge. A PII or caption defect introduced or hidden by re-encoding is treated the same as one in a raw PNG.
- See `scripts/capture/README.md` for the full workflow.

## Microsoft Learn URL Locale

All `learn.microsoft.com` URLs SHOULD use the `en-us` locale prefix.

Canonical form:

```text
https://learn.microsoft.com/en-us/azure/{service}/...
```

Avoid locale-less URLs (URLs missing the `/en-us/` segment immediately after the hostname):

```text
https://learn.microsoft.com/<missing-locale>/azure/{service}/...
```

The `<missing-locale>` placeholder marks the position where `/en-us/` must appear. A real locale-less URL would omit that segment entirely; the placeholder is used here only so this anti-pattern example does not trip the `scripts/normalize_mslearn_locale.py` CI gate.

Reason:

- Stable reader experience.
- Stable reviewer experience.
- Easier link checking.
- Less URL drift across repositories.

## Related Projects

| Repository | Description |
|---|---|
| [azure-virtual-machine-practical-guide](https://github.com/yeongseon/azure-virtual-machine-practical-guide) | Azure Virtual Machines practical guide |
| [azure-networking-practical-guide](https://github.com/yeongseon/azure-networking-practical-guide) | Azure Networking practical guide |
| [azure-storage-practical-guide](https://github.com/yeongseon/azure-storage-practical-guide) | Azure Storage practical guide |
| [azure-app-service-practical-guide](https://github.com/yeongseon/azure-app-service-practical-guide) | Azure App Service practical guide |
| [azure-functions-practical-guide](https://github.com/yeongseon/azure-functions-practical-guide) | Azure Functions practical guide |
| [azure-communication-services-practical-guide](https://github.com/yeongseon/azure-communication-services-practical-guide) | Azure Communication Services practical guide |
| [azure-container-apps-practical-guide](https://github.com/yeongseon/azure-container-apps-practical-guide) | Azure Container Apps practical guide |
| [azure-kubernetes-service-practical-guide](https://github.com/yeongseon/azure-kubernetes-service-practical-guide) | Azure Kubernetes Service (AKS) practical guide |
| [azure-architecture-practical-guide](https://github.com/yeongseon/azure-architecture-practical-guide) | Azure Architecture practical guide |
| [azure-monitoring-practical-guide](https://github.com/yeongseon/azure-monitoring-practical-guide) | Azure Monitoring practical guide |

## Content Categories

The documentation is organized by intent and lifecycle stage:

| Section | Purpose | Page Count |
|---|---|---|
| **Start Here** | Entry points, learning paths, repository map | 4 |
| **Platform** | Architecture, design decisions — WHAT and HOW it works | 7 |
| **Best Practices** | Production patterns — HOW to use the platform well | 9 |
| **Language Guides** | Per-language step-by-step tutorials and recipes | 40+ |
| **Operations** | Day-2 execution — HOW to run in production | 9 |
| **Troubleshooting** | Diagnosis and resolution — hypothesis-driven | 7 |
| **Reference** | Quick lookup — CLI, host.json, platform limits | 5 |

!!! info "Platform vs Best Practices vs Operations"
    - **Platform** = Understand the concepts and architecture.
    - **Best Practices** = Apply practical patterns and avoid common mistakes.
    - **Operations** = Execute day-2 tasks in production.

### Evidence Levels

When documenting troubleshooting steps or analysis, use these tags to specify the strength of the evidence:

- `[Observed]`: Directly seen in logs, metrics, or UI (e.g., 503 errors in Log Analytics).
- `[Measured]`: Quantified data (e.g., 99th percentile latency is 4.5s).
- `[Correlated]`: Two events happening together without proven causation.
- `[Inferred]`: Conclusion based on logic and multiple pieces of evidence.
- `[Strongly Suggested]`: High confidence inference but missing the "smoking gun".
- `[Not Proven]`: Hypothesis that has not yet been validated.
- `[Unknown]`: Missing data or ambiguous behavior.

### Evidence Annotation Policy

The evidence-tag pattern above is a differentiator for this series, but it is an **evidence-annotation tool, not a global writing style**. Applying tags to every image, paragraph, and orientation page causes *annotation fatigue* (readers stop reading them) and invites the `[Observed]`-as-OCR-dump anti-pattern (dumping the full Portal UI text instead of task-relevant values). Scope the tags by document type.

**Where evidence tags are required:**

- Troubleshooting lab guides
- Experiment logs
- KQL result interpretation
- Portal evidence sections
- Incident-style diagnostic walkthroughs

**Where evidence tags are optional:**

- Troubleshooting playbooks (decision points only)
- Platform deep dives (only where documented facts and observed behavior diverge)
- Operations verification sections
- Advanced diagnostic tutorials

**Where evidence tags should usually be avoided:**

- `Start Here`, `Learning Paths`, repository maps
- README files
- Glossary pages and CLI cheatsheets
- Simple tutorial steps
- Navigation-only index pages

**Writing rules — Do:**

- Keep `[Observed]` short and limited to task-relevant facts.
- Use `[Measured]` for numeric query or metric results.
- Use `[Inferred]` only when the reasoning depends on observations.
- Use `[Not Proven]` when a screenshot or query does not fully prove the claim.
- Put long evidence details in collapsible `??? note "Evidence notes"` blocks.

**Writing rules — Do not:**

- Use `[Observed]` as an OCR dump of the entire screen.
- Put long Portal UI text in image alt text.
- Use evidence tags to make normal prose look more rigorous.
- Treat `[Inferred]` as a substitute for Microsoft Learn sourcing.
- Force evidence tags into Start Here or Learning Paths pages.

Document-type matrix:

| Document type | Usage |
|---|---|
| Troubleshooting lab guide | Required |
| Incident-style experiment log | Required |
| KQL result interpretation | Strongly recommended (`[Measured]` / `[Observed]` / `[Inferred]`) |
| Portal evidence screenshot | Strongly recommended, kept short |
| Troubleshooting playbook | Recommended (decision points only) |
| Platform deep-dive | Optional (only where docs and observations diverge) |
| Language tutorial | Limited ("Verify" step only, short) |
| Start Here / Overview / Learning Paths | Nearly forbidden |
| Reference / CLI cheatsheet / glossary | Nearly forbidden (metric-capture reference pages excepted) |
| README / landing page | Effectively forbidden |

This policy is tracked series-wide in [issue #296](https://github.com/yeongseon/azure-container-apps-practical-guide/issues/296).

### Screenshot Evidence Pattern

For tutorial and Portal screenshots, prefer this structure over inline OCR dumps:

```markdown
![Short descriptive alt text](../assets/example.png)

Purpose: Explain why this screenshot is included.
Look for: List the 2-4 values the reader should verify.
Expected result: State the healthy or expected condition.
Next step: Point to the next action.

??? note "Evidence notes"
    [Observed] Short task-relevant observation.

    [Inferred] Interpretation based on the observation.

    [Not Proven] What this screenshot alone does not prove.
```

Rules:

- Alt text describes the image, not every visible UI value.
- `[Observed]` includes only values relevant to the task.
- Long raw observations move into the collapsible block.
- Never include real public IPs, subscription names, tenant IDs, object IDs, emails, secrets, or connection strings in alt text or evidence notes.

## Documentation Conventions

### File Naming

- Tutorial: `XX-topic-name.md` (numbered for sequence)
- All others: `topic-name.md` (kebab-case)

### CLI Command Style

```bash
# ALWAYS use long flags for readability
az functionapp create --resource-group $RG --name $APP_NAME --plan $PLAN_NAME --runtime python

# NEVER use short flags in documentation
az functionapp create -g $RG -n $APP_NAME  # ❌ Don't do this
```

### Variable Naming Convention

| Variable | Description | Example |
|----------|-------------|---------|
| `$RG` | Resource group name | `rg-functions-demo` |
| `$APP_NAME` | Function app name | `func-demo-app` |
| `$PLAN_NAME` | Hosting plan | `plan-demo-functions` |
| `$STORAGE_NAME` | Storage account | `stdemofunctions` |
| `$LOCATION` | Azure region | `koreacentral` |
| `$SUBSCRIPTION_ID` | Subscription identifier placeholder | `<subscription-id>` |

### Language Usage

- **Shell**: Use `bash` for all CLI examples.
- **Python**: Use `python` for all script examples.
- **KQL**: Use `kusto` for all Kusto Query Language blocks.
- **Mermaid**: Use `mermaid` for all architecture and flow diagrams.

## Content Source Requirements

### Microsoft Learn First Policy

All content must be traceable to official Microsoft Learn documentation.

- Platform content must have direct Microsoft Learn source URLs.
- Architecture diagrams must reference official Microsoft documentation.
- Troubleshooting playbooks may synthesize Microsoft Learn content with clear attribution.
- Self-generated content must include justification explaining the source basis.

### Source Types

| Type | Description | Allowed? |
|---|---|---|
| `mslearn` | Directly from Microsoft Learn | Required for platform content |
| `mslearn-adapted` | Microsoft Learn content adapted for this guide | Allowed with source URL |
| `self-generated` | Original content for this guide | Requires justification |
| `community` | From community sources | Not allowed for core content |
| `unknown` | Source not documented | Must be validated |

### Diagram Source Documentation

Every Mermaid diagram must have source metadata in frontmatter.

#### Canonical shape

New pages MUST use the canonical `content_sources.diagrams[…]` shape, with one entry per Mermaid block whose `id` matches the `<!-- diagram-id: … -->` HTML comment that precedes the fence:

```yaml
content_sources:
  diagrams:
    - id: flex-consumption-scaling
      type: flowchart
      source: mslearn-adapted
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
```

#### Legacy escape (Functions-specific, accepted)

The validator (`scripts/validate_content_sources.py`, `get_diagram_sources()`) accepts two legacy shapes that do NOT populate per-diagram entries. When either of these shapes is present, the validator skips per-diagram provenance enforcement for that file:

1. **List-form** `content_sources: [{type, url}, ...]` — the oldest shape, document-level provenance only.
2. **Dict-form** `content_sources: {references: [...]}` with no `diagrams:` key — semantically identical to list-form after the Phase 2d.2b-prep schema migration.

As of Phase 2d, approximately 295 Functions Mermaid pages still rely on the dict-form legacy escape. Promoting these pages to the canonical shape requires populating per-diagram entries on each page (manual editorial work, scoped to a future Phase 2e). The legacy escape is intentionally retained as accepted state until that backlog is closed.

#### What is NOT accepted

- `content_sources: {diagrams: []}` — explicit empty list. Surfaces as `content_sources.diagrams is empty` so the gap is visible.
- `content_sources: {diagrams: <non-list>}` — malformed.
- `content_sources: {}` or dicts with neither `references` nor `diagrams` — no document-level provenance to fall back on; not legacy, just broken.

#### Validator alignment with sibling repositories

The sibling Azure Container Apps and Azure App Service guides do NOT accept the dict-form `{references: [...]}` escape: their `scripts/validate_content_sources.py` rejects any Mermaid page without a populated `diagrams:` list (with `content-validation-status.md` and `validation-status.md` as the only two filename-level skips, since those are generator-owned dashboards). Both sibling repositories migrated all Mermaid pages to the canonical `content_sources.diagrams[…]` shape during Phase 2d, so they have no legacy backlog that requires an escape. This Functions repository keeps the `references` escape because the ~295-page backlog here is not yet migrated; the escape is the only thing preventing those pages from becoming hard validation errors.

A contributor moving a Mermaid page from this guide into Container Apps or App Service MUST populate the canonical `diagrams:` list on the destination side; copying a `references`-only page across will fail validation in the destination repository. This is the intended cross-repo contract, not a misalignment.

#### Deferred to Phase 2e (no committed timeline)

Tightening the validator to require per-diagram provenance on all Mermaid pages — which would expose the ~295-page Functions backlog as hard errors — is intentionally deferred. There is no committed timeline. Phase 2e opens only when the repository owner explicitly decides per-diagram provenance is now required policy.

Doctests covering all activation/non-activation cases of `get_diagram_sources()` live in [`scripts/validate_content_sources.py`](scripts/validate_content_sources.py) and are wired into the `validate-content-sources.yml` workflow as a strict gate. If the legacy escape is ever tightened or removed, those doctests MUST be updated in the same commit.

### Content Validation Tracking

- See [Content Validation Status](docs/reference/content-validation-status.md) for current status.
- See [Tutorial Validation Status](docs/reference/validation-status.md) for tutorial testing.

### Text Content Validation

Factual-claim documents include a `content_validation` block in frontmatter to track the verification status of their core technical assertions.

The single source of truth for "is this page in scope?" is [`scripts/lib/content_scope.py`](scripts/lib/content_scope.py) — specifically the `is_in_scope(rel_path)` function. Both the dashboard generator (`scripts/generate_content_validation_status.py`) and the out-of-scope cleanup tool (`scripts/remove_out_of_scope_validation.py`) import this helper, so the dashboard and the cleanup tool are guaranteed to agree on scope. If you change the scope policy, update both `scripts/lib/content_scope.py` AND this section in the same commit.

#### Scope

The `content_validation` block is **required** on factual-claim pages under these sections:

| Section | Required? | Examples |
|---|---|---|
| `docs/platform/` | Required (including factual subsection landing pages such as `platform/architecture/index.md` and `platform/networking-scenarios/index.md`) | Hosting plans, scaling, networking, security, observability |
| `docs/best-practices/` | Required | Hosting selection, triggers, scaling, reliability, security, deployment |
| `docs/operations/` | Required | Deployment, monitoring, alerts, cost optimization, recovery |
| `docs/troubleshooting/` | Required, except for the `EXCLUDED_SUBPATHS` and `NAVIGATION_INDEXES` listed below | Playbooks, methodology pages, first-10-minutes runbooks |

The block is **out of scope** on these pages — the dashboard does not count them, the cleanup tool does not require them, and new pages added in these locations should not introduce a `content_validation` block:

- **Out-of-scope sections** — any path that does not start with `platform/`, `best-practices/`, `operations/`, or `troubleshooting/`. This covers `docs/start-here/`, `docs/reference/`, `docs/contributing/`, `docs/language-guides/` (tutorials and recipes), and `docs/index.md`.
- **`EXCLUDED_SUBPATHS`** under `troubleshooting/`:
    - `troubleshooting/kql/` — KQL query packs make no factual assertions of their own
    - `troubleshooting/lab-guides/` — labs use the evidence-integrity model (Falsification step) instead
- **`NAVIGATION_INDEXES`** — section landing pages that only introduce a section and make no factual claims:
    - `platform/index.md`
    - `best-practices/index.md`
    - `operations/index.md`
    - `troubleshooting/index.md`
    - `troubleshooting/first-10-minutes/index.md`
    - `troubleshooting/playbooks/index.md`

Subsection landing pages that DO make factual claims (for example `platform/architecture/index.md` and `platform/networking-scenarios/index.md`) are intentionally NOT in `NAVIGATION_INDEXES` — they are treated like any other factual-claim page.

Legacy `content_validation` blocks may still exist on a number of out-of-scope pages (notably under `docs/reference/`, `docs/start-here/`, `docs/troubleshooting/kql/`, and `docs/troubleshooting/lab-guides/`) from before this scope policy was formalized. These blocks are accepted but are not counted by the dashboard; they will be reviewed in a follow-up editorial pass and can be removed with `python3 scripts/remove_out_of_scope_validation.py --apply`.

#### Schema

```yaml
---
content_sources:
  - type: mslearn-adapted
    url: https://learn.microsoft.com/en-us/azure/azure-functions/...
content_validation:
  status: verified  # verified | pending_review | unverified
  last_reviewed: 2026-04-12
  reviewer: agent  # agent | human
  core_claims:
    - claim: "Flex Consumption supports VNet integration"
      source: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
      verified: true
    - claim: "Premium plan requires Azure Files content share"
      source: https://learn.microsoft.com/en-us/azure/azure-functions/storage-considerations
      verified: true
---
```

#### Validation Status Values

| Status | Description |
|--------|-------------|
| `verified` | All core claims have been traced to Microsoft Learn sources |
| `pending_review` | Document exists but claims need source verification |
| `unverified` | New document, no validation performed |

#### Agent Rules for Content Validation

1. Add `content_validation` only when the page is in scope per `scripts/lib/content_scope.is_in_scope`. Do NOT add it to out-of-scope pages (tutorials, recipes, reference look-ups, KQL packs, lab guides, navigation indexes).
2. If you create a new in-scope page, you MUST add `content_validation` to it.
3. Each `core_claim` MUST be a verifiable factual assertion about Azure behavior (a quoted limit, a documented feature behavior, a configuration default). Meta-statements such as "this page uses Microsoft Learn as the primary source basis" are tautological and forbidden.
4. List 2-5 core claims per page; each MUST cite a Microsoft Learn URL.
5. Set `status: verified` only when ALL core claims have verified sources.
6. Run `python3 scripts/generate_content_validation_status.py` after updates to regenerate `docs/reference/content-validation-status.md`.

### PII Removal (Quality Gate)

**CRITICAL**: All CLI output examples MUST have PII removed.

**Must mask (real Azure identifiers):**

- Subscription IDs: `<subscription-id>`
- Tenant IDs: `<tenant-id>`
- Object IDs: `<object-id>`
- Resource IDs containing real subscription/tenant
- Emails: Remove or mask as `user@example.com`
- Secrets/Tokens: NEVER include

**OK to keep (synthetic example values):**

- Demo correlation IDs: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`
- Example request IDs in logs
- Placeholder domains: `example.com`, `contoso.com`
- Sample resource names used consistently in docs

The goal is to prevent leaking **real Azure account information**, not to mask obviously-fake example values that aid readability.

### Frontmatter YAML Style

Every Markdown file in `docs/` begins with a YAML frontmatter block delimited by `---`. The serialization style is **enforced by CI** and centralized in [`scripts/lib/yaml_style.py`](scripts/lib/yaml_style.py). Any script that mutates frontmatter MUST import `dump_frontmatter()` (preferred single-call API) or `build_yaml()` (for tools that need to call `load()` and `dump()` on the same instance) from that module — direct use of PyYAML's `yaml.dump()` is forbidden because it silently reformats files on every run (quoting dates, flattening nested sequences, folding multi-line strings), producing noisy diffs and unstable history.

#### Canonical style

| Setting | Value | Why |
|---|---|---|
| Library | `ruamel.yaml` (`typ='rt'`, round-trip mode) | Preserves comments, quoting, and key order across load/dump cycles. PyYAML cannot. |
| `indent(mapping=2, sequence=4, offset=2)` | `mapping=2`, `sequence=4`, `offset=2` | Matches the historical repository layout: list hyphens sit at column 4 under their parent key, list-item content at column 6. |
| `preserve_quotes` | `True` | Existing files are normalized for *structure* only; intentionally quoted dates and strings are kept as-is to avoid surprising semantic changes (e.g., `"2026-04-12"` becoming a `datetime.date` object). |
| `width` | `4096` | Practically disables line folding so long `claim`, `summary`, and `justification` strings stay on one line. Folding produces fragile diffs and harms grep-ability. |
| `explicit_end` | `False` | Frontmatter is delimited by a single closing `---` (no `...` document terminator). |

Example of correct style (matches the canonical output):

```yaml
---
content_sources:
  diagrams:
    - id: flex-consumption-scaling
      type: flowchart
      source: mslearn-adapted
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
        - https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling
---
```

#### Workflow

1. **Never write frontmatter with PyYAML.** Any new generator or mutation tool MUST import `build_yaml()` (or the higher-level `dump_frontmatter()` helper) from `scripts/lib/yaml_style.py`. `dump_frontmatter()` is the public single-call API used by `scripts/normalize_yaml_frontmatter.py` itself; prefer it over instantiating `build_yaml()` and managing a `StringIO` buffer manually.
2. **Bulk normalize when needed:**

    ```bash
    python3 scripts/normalize_yaml_frontmatter.py --apply
    ```

3. **CI enforces drift:** the `Validate Content Sources` workflow runs `python scripts/normalize_yaml_frontmatter.py --check` and fails if any frontmatter would change. The workflow triggers on changes to `docs/**`, `scripts/**`, `apps/**`, `labs/**`, `infra/**`, the repo-root markdown files (`AGENTS.md`, `README*.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`), or the workflow itself, so that updates to the shared library or the normalizer always re-run the check. The trigger surface intentionally mirrors the `EXTENSIONS` scan set in `scripts/normalize_mslearn_locale.py` (`.md`, `.py`, `.yml`, `.yaml`, `.json`, `.bicep`, `.tf`, `.txt`) so a PR touching only `.json`/`.bicep`/`.tf` files under those paths cannot bypass the locale check. `ruamel.yaml` is pinned to a specific version in CI so the canonical bytes are reproducible across runs.
4. **Body is preserved byte-exact for the repo invariant (UTF-8, no BOM, LF line endings).** The normalizer only rewrites the YAML region between the two `---` delimiters; the blank line (or its absence) between the closing `---` and the first body line is preserved as-is. Files with a UTF-8 BOM are silently skipped (the regex won't match), and files with CRLF line endings would be converted to LF on `--apply` -- no such files exist in this repo today, but if that ever changes, update this policy first.

#### When to update this section

If [`scripts/lib/yaml_style.py`](scripts/lib/yaml_style.py) changes (different indent, width, or quoting policy), the table above MUST be updated in the same commit. The shared library is the source of truth; this section is the human-readable mirror.

### Admonition Indentation Rule

For MkDocs admonitions (`!!!` / `???`), every line in the body must be indented by **4 spaces**.

```markdown
!!! warning "Important"
    This line is correctly indented.

    - List item also inside
```

### Nested List Indentation

All nested list items MUST use **4-space indent** (Python-Markdown standard).

```markdown
# CORRECT (4-space)
1. **Item**
    - Sub item
    - Another sub item
        - Third level

# WRONG (2 or 3 spaces)
1. **Item**
  - Sub item          ← 2 spaces ❌
   - Sub item         ← 3 spaces ❌
```

### Tail Section Naming

Every document ends with these tail sections (in this order):

| Section | Purpose | Content |
|---|---|---|
| `## See Also` | Internal cross-links within this repository | Links to other pages in this guide |
| `## Sources` | External authoritative references | Links to Microsoft Learn (primary) |

- `## See Also` is required on every page.
- `## Sources` is required when external references are cited. Omit if none exist.
- Order is always `## See Also` → `## Sources` (never reversed).
- All content must be based on Microsoft Learn with cited sources.

### Canonical Document Templates

Every document follows one of 7 templates based on its section. Do not invent new structures.

#### Platform docs

```text
# Title
Brief introduction (1-2 sentences)
## Prerequisites (optional — only if hands-on/CLI content)
## Main Content
### Subsections (H3 under Main Content)
#### Sub-subsections (H4 as needed)
## Advanced Topics (optional)
## Language-Specific Details (optional)
## See Also
## Sources (optional)
```

#### Best Practices docs

```text
# Title
Brief introduction
## Prerequisites (optional)
## Why This Matters
## Recommended Practices
## Common Mistakes / Anti-Patterns
## Validation Checklist
## Advanced Topics (optional)
## See Also
## Sources (optional)
```

#### Operations docs

```text
# Title
Brief introduction
## Prerequisites
## When to Use
## Procedure
## Verification
## Rollback / Troubleshooting
## Advanced Topics (optional)
## See Also
## Sources (optional)
```

#### Tutorial docs (Language Guides)

```text
# Title
Brief introduction
## Prerequisites
## What You'll Build
## Steps
## Verification
## Next Steps / Clean Up (optional)
## See Also
## Sources (optional)
```

#### Playbooks

```text
# Title (no intro paragraph — Summary covers it)
## 1. Summary
## 2. Common Misreadings
## 3. Competing Hypotheses
## 4. What to Check First
## 5. Evidence to Collect
## 6. Validation and Disproof by Hypothesis
## 7. Likely Root Cause Patterns
## 8. Immediate Mitigations
## 9. Prevention (optional)
## See Also
## Sources (optional)
```

#### Lab Guides

```text
# Title
Brief introduction
## Lab Metadata (table: difficulty, duration, tier, etc.)
## 1) Background
## 2) Hypothesis
## 3) Runbook
## 4) Experiment Log
## Expected Evidence
## Clean Up
## Related Playbook
## See Also
## Sources
```

#### Reference docs

```text
# Title
Brief introduction
## Prerequisites (optional)
## Topic/Command Groups
## Usage Notes (optional)
## See Also
## Sources (optional)
```

## Troubleshooting Content Standards

### Playbooks

Each playbook includes:

1. Symptom description and hypotheses
2. Evidence collection steps
3. **Sample Log Patterns** — real log lines from Azure deployment
4. **KQL Queries with Example Output** — 2-3 queries with result tables + `!!! tip "How to Read This"` interpretation
5. **CLI Investigation Commands** — with example output and interpretation
6. **Normal vs Abnormal Comparison** — table
7. **Common Misdiagnoses** section
8. **Related Labs** — cross-links to lab guide docs

### Lab Guides

Each lab guide includes:

1. Background and failure progression model
2. Falsifiable hypothesis
3. Step-by-step runbook
4. Experiment log with real artifact data
5. **Expected Evidence** section:
    - Before Trigger (Baseline)
    - During Incident
    - After Recovery
    - Evidence Timeline (Mermaid)
    - Evidence Chain: Why This Proves the Hypothesis (falsification logic)
6. Related Playbook cross-links

### Data Verification

All playbook evidence and lab guide data should be collected from real Azure deployments:

- Azure Functions hosting plans (Consumption, Flex Consumption, Premium, Dedicated)
- Data sources: FunctionAppLogs, AppMetrics, traces, dependencies
- KQL collected via REST API or Application Insights portal
- All data sanitized (PII removed)

## Tutorial Validation Tracking

Every tutorial document supports **validation frontmatter** that records when and how it was last tested against a real Azure deployment.

### Frontmatter Schema

Add a `validation` block inside the YAML frontmatter (`---` fences) of any tutorial file:

```yaml
---
hide:
  - toc
validation:
  az_cli:
    last_tested: 2026-04-09
    cli_version: "2.83.0"
    core_tools_version: "4.8.0"
    result: pass
  bicep:
    last_tested: null
    result: not_tested
---
```

### Field Reference

| Field | Type | Values | Description |
|---|---|---|---|
| `result` | string | `pass`, `fail`, `not_tested` | Outcome of the validation run |
| `last_tested` | date or null | `2026-04-09` / `null` | ISO date of last test, null if never tested |
| `cli_version` | string | `"2.83.0"` | Azure CLI version used during testing |
| `core_tools_version` | string | `"4.8.0"` | Azure Functions Core Tools version used |

### Validation Methods

Each tutorial can be validated via two independent methods:

- **az_cli** — Manual step-by-step execution using Azure CLI commands
- **bicep** — Infrastructure-as-code deployment using Bicep templates

### Staleness Rule

Tutorials not validated within **90 days** are flagged as **stale** on the dashboard.

### Agent Rules for Validation

1. **After deploying a tutorial end-to-end**, add or update the `validation` frontmatter with the current date, CLI version, and `result: pass`.
2. **If a tutorial step fails during validation**, set `result: fail` and note the issue — do NOT remove existing passing metadata for the other method.
3. **Never fabricate validation dates.** Only stamp a tutorial after actually executing all steps against a real Azure environment.
4. **After updating frontmatter**, regenerate the dashboard:
    ```bash
    python3 scripts/generate_validation_status.py
    ```
5. **Include the regenerated dashboard** (`docs/reference/validation-status.md`) in the same commit as the frontmatter change.
6. **Do not manually edit** `docs/reference/validation-status.md` — it is auto-generated by the script.

## Build & Preview

```bash
# Install MkDocs dependencies
pip install mkdocs-material mkdocs-minify-plugin

# Build documentation (strict mode catches broken links)
mkdocs build --strict

# Local preview
mkdocs serve
```

## Git Commit Style

```text
type: short description
```

Allowed types: `feat`, `fix`, `docs`, `chore`, `refactor`

## Merge Policy (AI Agent Rule)

AI agents MAY merge their own pull requests **autonomously**, but ONLY after ALL of the mandatory gates below pass. There is no separate human approval step — passing every gate IS the approval. If any gate cannot be satisfied, the agent MUST stop and hand the PR to the user instead of merging.

### Mandatory merge gates (ALL required)

| # | Gate | How it is verified |
|---|---|---|
| 1 | **Oracle review ≥ 90/100** | Submit the final diff to Oracle for quality review. Score must be **90 or higher with no merge-blocking issues**. Any must-fix item is a blocker even at ≥ 90. |
| 2 | **CI fully green** | Every required GitHub Actions check on the PR head SHA passes. Verify with `gh pr checks <pr> --watch`; do not merge on `pending` or `failure`. |
| 3 | **Caption ↔ image match** | For every added/changed image referenced from markdown, the caption/alt text MUST accurately describe the actual rendered image. |
| 4 | **Final-image PII verification** | Every added/changed `.png`/`.webp` referenced from markdown MUST be visually verified (Read/`look_at`) for PII on the **final committed bytes** — zeroed subscription/tenant IDs, no employee identifiers, no black-box masks. WebP re-encodes are re-verified, not assumed from the raw PNG. |

### Merge procedure

1. Confirm gates 1-4 above, in order. Record the Oracle score and the visual-verification result in the PR thread or the final summary.
2. Merge with **squash-and-merge** only:

    ```bash
    gh pr merge <pr> --squash --delete-branch
    ```

3. Never use merge-commit or rebase-merge; squash keeps `main` history linear and collapses fixup commits.
4. Never bypass a failing or pending gate. Never merge with `--admin` to skip checks.

### When to stop instead of merging

- Oracle score < 90, or any unresolved must-fix.
- Any CI check failing or still pending.
- Any referenced image that cannot be visually verified.
- The PR touches something outside the agent's stated scope.

In these cases, report the blocking gate and hand off to the user instead of merging.

