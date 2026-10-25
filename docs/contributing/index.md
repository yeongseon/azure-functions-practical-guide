---
title: Contributing
---

# Contributing

Thank you for your interest in contributing to Azure Functions Practical Guide!

The repository's [CONTRIBUTING.md](https://github.com/yeongseon/azure-functions-practical-guide/blob/main/CONTRIBUTING.md)
is the authority for issue authoring, labels and triage, focused implementation,
PR sections, and maintainer-authorized review/merge. This page covers authoring
and local setup; coding agents also start with `AGENTS.md`.

## Quick Start

1. Fork the repository
2. Clone: `git clone https://github.com/yeongseon/azure-functions-practical-guide.git`
3. Install dependencies: `pip install -r requirements-docs.txt`
4. Start local preview: `mkdocs serve`
5. Open `http://127.0.0.1:8000` in your browser
6. Create a feature branch: `git checkout -b feature/your-change`
7. Make changes and validate: `mkdocs build --strict`
8. Submit a Pull Request

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
│   ├── best-practices/         # Production patterns and anti-patterns
│   ├── javascripts/            # Mermaid zoom JS
│   ├── language-guides/
│   │   ├── python/             # Python — 4 plans tutorials + recipes
│   │   ├── nodejs/             # Node.js — 4 plans tutorials + recipes
│   │   ├── java/               # Java — 4 plans tutorials + recipes
│   │   └── dotnet/             # .NET — 4 plans tutorials + recipes
│   ├── operations/             # Day-2 operational execution
│   ├── platform/               # Architecture and design decisions
│   ├── reference/              # CLI cheatsheet, host.json, limits
│   ├── start-here/             # Overview, learning paths, repository map
│   ├── stylesheets/            # Custom CSS
│   └── troubleshooting/        # Troubleshooting hub
│       ├── architecture-components-reference.md
│       ├── request-flow-for-incident-response.md
│       ├── evidence-map.md
│       ├── first-10-minutes/   # First-10-minutes guides
│       ├── kql/                # KQL query packs
│       ├── lab-guides/         # Lab guide documents
│       ├── methodology/        # Methodology guides
│       └── playbooks/          # Playbook documents
├── infra/                      # Bicep templates for all hosting plans
├── labs/                       # Lab infrastructure + app source
└── mkdocs.yml                  # MkDocs Material configuration
```

## Content Categories

| Section | Purpose |
|---|---|
| **Start Here** | Entry points, learning paths, repository map |
| **Platform** | Architecture, design decisions — WHAT and HOW it works |
| **Best Practices** | Production patterns — HOW to use the platform well |
| **Language Guides** | Per-language step-by-step tutorials and recipes |
| **Operations** | Day-2 execution — HOW to run in production |
| **Troubleshooting** | Diagnosis and resolution — hypothesis-driven |
| **Reference** | Quick lookup — CLI, host.json, platform limits |

## Document Templates

Use the [seven canonical document templates](content-contract.md#canonical-document-templates)
for your section. Do not invent new structures. The detailed versions include
optional prerequisites, advanced topics, language-specific details, and the
required See Also / Sources order.

## Writing Standards

Read the [Documentation Content Contract](content-contract.md) sections relevant
to your change; these requirements apply equally to human and agent authors.

| Area | Rules and examples |
|---|---|
| CLI Commands | [Long flags](content-contract.md#cli-command-style) and [explanation tables, blank-line termination, rendered-HTML verification](content-contract.md#cli-explanation-table-rule-quality-gate) |
| Variables | [Variable naming convention](content-contract.md#variable-naming-convention) |
| Mermaid Diagrams | [Required document types and orientation](content-contract.md#mermaid-diagrams); avoid redundant diagrams/screenshots |
| Nested Lists | [Four-space nesting](content-contract.md#nested-list-indentation) |
| Admonitions | [Four-space body indentation](content-contract.md#admonition-indentation-rule) |
| Tail Sections | [See Also followed by Sources](content-contract.md#tail-section-naming) |
| Evidence | [Levels](content-contract.md#evidence-levels), [annotation scope](content-contract.md#evidence-annotation-policy), [playbook/lab evidence](content-contract.md#troubleshooting-content-standards) |
| Screenshots | [Capture pipeline, compliant authentication, final-byte review](content-contract.md#image-and-screenshot-rules) |
| Frontmatter | [YAML serialization rules](content-contract.md#frontmatter-yaml-style) and [validation scope/schema](content-contract.md#text-content-validation) |

## Content Source Policy

All content must be traceable to official Microsoft Learn documentation. Follow
the [source types and provenance policy](content-contract.md#content-source-requirements),
including the Functions-specific legacy migration rules for edited Mermaid pages.

## PII Rules

NEVER include real Azure identifiers, emails, secrets, tokens, or connection
strings. Use the [PII placeholders and synthetic-example rules](content-contract.md#pii-removal-quality-gate)
and [image safeguards](content-contract.md#image-and-screenshot-rules).

## Build and Validate

```bash
# Install dependencies
pip install -r requirements-docs.txt

# Recommended local validation (required GitHub CI validates final PR head)
mkdocs build --strict

# Local preview
mkdocs serve
```

Run applicable [quality-gate commands](https://github.com/yeongseon/azure-functions-practical-guide/blob/main/AGENTS.md#build-preview-and-quality-gates)
and their CI doctests. The contract preserves the full [repetition](content-contract.md#documentation-repetition-gate-quality-gate),
[PII](content-contract.md#pii-detection-gate-quality-gate), and
[visual coverage](content-contract.md#visual-content-gate-quality-gate) gate semantics.

### Tutorial Validation Dashboard Scope

`docs/reference/validation-status.md` tracks executable leaf tutorial runbooks under `docs/language-guides/*/tutorial/<hosting-plan>/*.md`.

The dashboard intentionally excludes:

- Tutorial `index.md` chooser pages, because they explain plan selection and navigation rather than an end-to-end Azure deployment.
- Troubleshooting lab guides under `docs/troubleshooting/lab-guides/`, because they are experiment reports. Validate them through their lab metadata, experiment log, expected evidence, and content source metadata instead of tutorial `validation` frontmatter.

Only add or update tutorial `validation` frontmatter after actually executing the documented steps against Azure. Do not add synthetic `last_tested` dates to close dashboard gaps.
See [tutorial validation tracking](content-contract.md#tutorial-validation-tracking)
for the schema, method-specific results, staleness and dashboard regeneration rules.

## Git Commit Style

Titles for issues, pull requests, and commits follow the **Title Convention** in [`CONTRIBUTING.md`](https://github.com/yeongseon/azure-functions-practical-guide/blob/main/CONTRIBUTING.md#title-convention), the single source of truth for the format and the allowed types.

## Review Process

Follow the [review and merge policy](https://github.com/yeongseon/azure-functions-practical-guide/blob/main/CONTRIBUTING.md#tool-neutral-pr-review-and-merge):
required GitHub CI on the final head, relevant content/image/PII checks, and a
responsible maintainer's squash-merge decision. AI feedback is advisory. Publishing
remains a separate workflow; merging alone does not authorize a deployment.

## Code of Conduct

Please read our [Code of Conduct](https://github.com/yeongseon/azure-functions-practical-guide/blob/main/CODE_OF_CONDUCT.md) before contributing.

## See Also

- [Documentation Content Contract](content-contract.md)
- [Repository Map](../start-here/repository-map.md)
- [Learning Paths](../start-here/learning-paths.md)
