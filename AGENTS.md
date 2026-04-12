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
│   │   ├── python/             # Python — 4 plans × 7 tutorials + recipes
│   │   ├── nodejs/             # Node.js — 4 plans × 7 tutorials + recipes
│   │   ├── java/               # Java — 4 plans × 7 tutorials + recipes
│   │   └── dotnet/             # .NET — 4 plans × 7 tutorials + recipes
│   ├── operations/             # Day-2 operational execution (9 pages)
│   ├── platform/               # Architecture and design decisions (7 pages)
│   ├── reference/              # CLI cheatsheet, host.json, limits (5 pages)
│   ├── start-here/             # Overview, learning paths, repository map (4 pages)
│   ├── stylesheets/            # Custom CSS (mermaid zoom, etc.)
│   └── troubleshooting/        # Troubleshooting hub (7 pages)
│       ├── architecture.md
│       ├── evidence-map.md
│       ├── first-10-minutes.md
│       ├── kql.md
│       ├── lab-guides.md
│       ├── methodology.md
│       └── playbooks.md
├── infra/                      # Bicep templates for all hosting plans
│   ├── consumption/
│   ├── flex-consumption/
│   ├── premium/
│   ├── dedicated/
│   └── modules/
├── labs/                       # Lab infrastructure + app source
│   ├── cold-start/
│   ├── dns-vnet-resolution/
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

Every non-tutorial document should include a `content_validation` block in frontmatter to track the verification status of its core claims.

```yaml
---
content_sources:
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/...
content_validation:
  status: verified  # verified | pending_review | unverified
  last_reviewed: 2026-04-12
  reviewer: agent  # agent | human
  core_claims:
    - claim: "Flex Consumption supports VNet integration"
      source: https://learn.microsoft.com/azure/azure-functions/flex-consumption-plan
      verified: true
    - claim: "Premium plan requires Azure Files content share"
      source: https://learn.microsoft.com/azure/azure-functions/storage-considerations
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

1. When creating or modifying Platform, Best Practices, or Operations documents, add `content_validation` frontmatter.
2. List 2-5 core claims that are factual assertions (not opinions or procedures).
3. Each claim must have a Microsoft Learn source URL.
4. Set `status: verified` only when ALL core claims have verified sources.
5. Run `python3 scripts/generate_content_validation_status.py` after updates.

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

### Admonition Indentation Rule

For MkDocs admonitions (`!!!` / `???`), every line in the body must be indented by **4 spaces**.

```markdown
!!! warning "Important"
    This line is correctly indented.

    - List item also inside
```

### Mermaid Diagrams

All architectural diagrams use Mermaid. Every documentation page should include at least one diagram. Test with `mkdocs build --strict`.

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
