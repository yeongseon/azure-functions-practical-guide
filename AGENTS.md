# AGENTS.md

Shared entry point for humans, Codex, OpenCode, and Claude Code (`CLAUDE.md`
imports this file; read it directly if imports are unavailable).

## Project Overview

**Azure Functions Practical Guide** — documentation, reference applications, and
hands-on troubleshooting labs for building and operating Azure Functions.

- [Live site](https://yeongseon.dev/azure-functions-python/practical-guide/)
- [Repository](https://github.com/yeongseon/azure-functions-practical-guide)
- [Repository structure and local setup](docs/contributing/index.md)
- [Related projects](README.md#related-projects)

## Workflow Authority

Read [CONTRIBUTING.md](CONTRIBUTING.md) before issue/PR work: it owns issue
authoring, repository-local evidence, duplicate checks, triage/labels, focused
implementation, overengineering assessment, title convention, issue linkage,
and maintainer-led review/merge. Preserve its post-save issue field checks.
Do not duplicate rules in tool-specific files or automatically install/invoke
agent plugins, hooks, or frameworks.

## Content Contract: Read Before Editing

[Documentation Content Contract](docs/contributing/content-contract.md) is the
shared, mandatory detailed authoring policy, not optional background reading.
Read the relevant sections before changing documentation, scripts, or captures.
The [contributing guide](docs/contributing/index.md) routes local setup and templates.

| Change area | Required detailed rules |
|---|---|
| Organization and navigation | [Series contract](docs/contributing/content-contract.md#series-wide-documentation-contract), [Start Here](docs/contributing/content-contract.md#start-here-rules), [navigation budget](docs/contributing/content-contract.md#navigation-budget), [content categories](docs/contributing/content-contract.md#content-categories) |
| Page authoring | [Conventions](docs/contributing/content-contract.md#documentation-conventions), [seven canonical templates](docs/contributing/content-contract.md#canonical-document-templates), [tail sections](docs/contributing/content-contract.md#tail-section-naming) |
| Sources and diagrams | [Source requirements](docs/contributing/content-contract.md#content-source-requirements), [Mermaid requirements/orientation](docs/contributing/content-contract.md#mermaid-diagrams), [legacy provenance](docs/contributing/content-contract.md#diagram-source-documentation) |
| Validation metadata or generators | [Scope/schema](docs/contributing/content-contract.md#text-content-validation), [YAML style](docs/contributing/content-contract.md#frontmatter-yaml-style), [tutorial validation](docs/contributing/content-contract.md#tutorial-validation-tracking) |
| Troubleshooting and evidence | [Evidence levels](docs/contributing/content-contract.md#evidence-levels), [annotation policy](docs/contributing/content-contract.md#evidence-annotation-policy), [playbook/lab standards](docs/contributing/content-contract.md#troubleshooting-content-standards) |
| Images or Portal captures | [Image rules and capture pipeline](docs/contributing/content-contract.md#image-and-screenshot-rules), [screenshot evidence](docs/contributing/content-contract.md#screenshot-evidence-pattern), [PII rules](docs/contributing/content-contract.md#pii-removal-quality-gate) |

## Hard Rules

- Preserve the series core sections: Start Here, Platform, Best Practices,
  Operations, Troubleshooting, Reference. Use only approved extensions; do not
  add a top-level section when an existing one fits. Keep Start Here orientation-only.
- **Microsoft Learn first:** trace content and architecture diagrams to official
  sources; platform claims need direct URLs. Justify self-generated content;
  community sources are not allowed for core content. Use `en-us` Learn URLs.
- **PII:** never commit real Azure/account identifiers, emails, secrets, tokens,
  keys, connection strings, customer data, or unsafe CLI output. Use documented
  placeholders; synthetic examples are allowed. Sanitize real deployment evidence.
- **CLI:** use long Azure CLI flags. Every `bash` fence containing `az` commands
  needs an immediately following explanation table, one row per base command and
  long flag. Terminate the table with a blank line or EOF. Run the validator and
  spot-check rendered HTML; a strict build alone cannot prove correct tables.
- Use `bash`, `python`, `kusto`, and `mermaid` fences for their respective languages;
  use four-space nested lists/admonition bodies and canonical filenames/templates.
  End pages with See Also, then Sources when external references are cited.
- **Mermaid:** add meaningful diagrams for required document types, not decoration.
  Use TD for sequential flows with 5+ nodes and layered architecture; LR is fine
  for shorter flows. Every diagram needs source metadata and a matching
  `<!-- diagram-id: ... -->`. New/edited Mermaid pages must populate per-diagram
  `content_sources.diagrams[]`; do not introduce or export reference-only legacy
  metadata. Existing legacy escapes remain until owner-authorized policy change.
- **Validation honesty:** never invent dates, results, logs, or Azure execution.
  Use evidence tags only in their documented scope; distinguish observed/measured
  evidence from inference and unproven hypotheses. Playbooks/labs require real,
  sanitized evidence and falsification, not synthetic claims of reproduction.
- Add `content_validation` only in the scope defined by
  `scripts/lib/content_scope.py`; `docs/contributing/` is out of scope. In-scope
  pages need 2–5 factual Azure claims with Learn sources, not tautologies.
  Mark verified only after all core sources are checked. Regenerate the content
  dashboard after metadata updates; update the scope code and policy together.
- Stamp tutorial `validation` only after end-to-end Azure execution; preserve the
  other method's results when one fails. Regenerate/commit the tutorial dashboard;
  never hand-edit it. Source review is not Azure validation.
- Frontmatter mutators must use `scripts/lib/yaml_style.py` (`dump_frontmatter()`
  or `build_yaml()`), not PyYAML dumps. Keep its contributor policy mirror in sync.
- **Screenshots:** require task-relevant alt text/explanation, safe masking and
  visual verification of final committed PNG/WebP bytes against captions and PII.
  Re-encoding requires rechecking. Use the manifest/stable-ID capture pipeline;
  attach to a device-compliant human-signed-in browser; never bypass Conditional
  Access or automate MFA. Unverifiable images block merge; remove references or
  disclose debt, never silently weaken the gate.

## Build, Preview, and Quality Gates

Run from the repository root; see [gate details](docs/contributing/content-contract.md#documentation-repetition-gate-quality-gate).
Use applicable existing tests as well as these documentation checks:

```bash
pip install -r requirements-docs.txt
mkdocs build --strict
mkdocs serve  # local preview when needed
python scripts/validate_cli_explanations.py
python scripts/validate_mermaid_format.py
python scripts/validate_mermaid_syntax.py
python scripts/normalize_yaml_frontmatter.py --check
python scripts/normalize_mslearn_locale.py --check
python scripts/scan_lab_pii.py
python scripts/validate_content_sources.py
python scripts/detect_repetition.py docs
python scripts/validate_pii.py
python scripts/validate_visual_content.py --all
```

Run associated doctests as CI does. Preserve existing blocking/advisory semantics:
PII blocks changed Markdown; full PII and historical source audits are advisory;
visual coverage is WARN-only. Never allowlist boilerplate instead of removing it.
Do not weaken workflows, publishing checks, or security gates to make checks pass.

## Pull Request Descriptions

Follow [CONTRIBUTING.md](CONTRIBUTING.md#pull-request-writing) for concise,
reader-focused PR descriptions. Preserve required Azure and screenshot evidence,
source/validation distinctions, and all existing CI and image gates.

## Merge Policy (Tool-Neutral Review)

Follow [the complete review/merge policy](CONTRIBUTING.md#tool-neutral-pr-review-and-merge).
All required GitHub CI must pass on the final PR head; record CI links and
applicable final-image/PII verification in the PR. Local checks and AI feedback
are not approval. Resolve blocking security, scope, factual and image findings;
obtain independent scrutiny for high-risk publishing/permissions changes.
Only the responsible maintainer authorizes squash merge. Never bypass checks with
`--admin`, merge on AI scores/green CI alone, or proceed with pending/failing
checks, unverifiable images, unresolved blockers, or missing maintainer approval.
Report blockers instead. Merging alone does not authorize deployment.
