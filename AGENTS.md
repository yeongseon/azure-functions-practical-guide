# AGENTS.md

Guidance for AI agents working in this repository.

## Project Overview

**Azure Functions Practical Guide** — a unified documentation hub, reference applications, and hands-on troubleshooting labs for building and operating serverless applications on Azure Functions.

- **Live site**: <https://yeongseon.github.io/azure-functions-practical-guide/>
- **Repository**: <https://github.com/yeongseon/azure-functions-practical-guide>

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

### Content Validation Tracking

- See [Content Validation Status](docs/reference/content-validation-status.md) for current status.
- See [Tutorial Validation Status](docs/reference/validation-status.md) for tutorial testing.

### Text Content Validation

Factual-claim documents include a `content_validation` block in frontmatter to track the verification status of their core technical assertions.

The single source of truth for "is this page in scope?" is [`scripts/lib/content_scope.py`](scripts/lib/content_scope.py) — specifically the `is_in_scope(rel_path)` function. The dashboard generator and the out-of-scope cleanup tool both import this helper, so they are guaranteed to agree on scope. If you change the scope policy, update both `scripts/lib/content_scope.py` AND this section in the same commit.

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

### Mermaid Diagrams

All architectural diagrams use Mermaid. Every documentation page should include at least one diagram. Test with `mkdocs build --strict`.

#### Diagram Orientation Rule

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

## Related Projects

| Repository | Description |
|---|---|
| [azure-virtual-machine-practical-guide](https://github.com/yeongseon/azure-virtual-machine-practical-guide) | Azure Virtual Machines practical guide |
| [azure-networking-practical-guide](https://github.com/yeongseon/azure-networking-practical-guide) | Azure Networking practical guide |
| [azure-storage-practical-guide](https://github.com/yeongseon/azure-storage-practical-guide) | Azure Storage practical guide |
| [azure-app-service-practical-guide](https://github.com/yeongseon/azure-app-service-practical-guide) | Azure App Service practical guide |
| [azure-container-apps-practical-guide](https://github.com/yeongseon/azure-container-apps-practical-guide) | Azure Container Apps practical guide |
| [azure-communication-services-practical-guide](https://github.com/yeongseon/azure-communication-services-practical-guide) | Azure Communication Services practical guide |
| [azure-kubernetes-service-practical-guide](https://github.com/yeongseon/azure-kubernetes-service-practical-guide) | Azure Kubernetes Service (AKS) practical guide |
| [azure-architecture-practical-guide](https://github.com/yeongseon/azure-architecture-practical-guide) | Azure Architecture practical guide |
| [azure-monitoring-practical-guide](https://github.com/yeongseon/azure-monitoring-practical-guide) | Azure Monitoring practical guide |
