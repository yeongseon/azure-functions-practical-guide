---
title: Phase 2d Final — Cross-Repository Mermaid Audit
hide:
  - toc
---

# Phase 2d Final — Cross-Repository Mermaid Audit

This page captures the audit findings that closed the **Phase 2d** content-sources schema migration. It is intentionally checked in as a durable artifact (rather than living only in PR descriptions) so the rationale survives PR garbage collection and is discoverable from the documentation site.

## Background

Phase 2d migrated `content_sources` frontmatter across the three sibling Azure guide repositories (Azure Functions, Azure Container Apps, Azure App Service) from the legacy list-form (`content_sources: [{type, url}, ...]`) to the canonical dict-form (`content_sources: {diagrams: [...]}` or `content_sources: {references: [...]}`). The migration was performed in seven batches in the Functions repository (PRs #54–#60), preceded by tooling unification in PR #53.

After the data migration completed, an audit asked whether the validator (`scripts/validate_content_sources.py`, function `get_diagram_sources()`) could be tightened to require per-diagram provenance on all Mermaid pages — i.e., to reject the dict-form `{references: [...]}` shape as well as the list-form shape.

## Audit findings

### Cross-repository Mermaid shape distribution

| Repository | Mermaid files | Canonical (`{diagrams: […]}`) | Legacy escape (`{references: […]}`) | Other |
|---|---:|---:|---:|---:|
| `azure-functions-practical-guide` | 302 | 7 | 295 | 0 |
| `azure-container-apps-practical-guide` | 356 | 355 | 1 (path-skipped dashboard) | 0 |
| `azure-app-service-practical-guide` | 218 | 216 | 1 (path-skipped dashboard) | 1 (closed by App Service PR #102) |

The "path-skipped dashboard" rows refer to `docs/reference/content-validation-status.md` and `docs/reference/validation-status.md`, which are explicitly skipped by `scripts/validate_content_sources.py` because they are auto-generated dashboards whose Mermaid pie charts have no upstream Microsoft Learn source.

### Generator-emitted frontmatter shapes

The audit also surveyed the six generators that emit Markdown into `docs/reference/`:

| Repo | Generator | Emitted shape | Status |
|---|---|---|---|
| ACA | `generate_content_validation_status.py` | `{references: [self-generated]}` | Path-skipped — OK |
| ACA | `generate_validation_status.py` | `{diagrams: [tutorial-validation-status-pie]}` + `content_validation` | Canonical — OK |
| AS | `generate_content_validation_status.py` | `{references: [self-generated]}` | Path-skipped — OK |
| AS | `generate_validation_status.py` | (was missing frontmatter — closed by App Service PR #102) | Canonical — OK after PR #102 |
| Functions | `generate_content_validation_status.py` | `{references: [self-generated]}` | Path-skipped — OK |
| Functions | `generate_validation_status.py` | `{references: [mslearn], diagrams: [tutorial-validation-status-pie]}` | Canonical + references — OK |

The single hygiene gap was App Service's `generate_validation_service.py` emitting no frontmatter at all. App Service PR #102 brought it in line with the canonical pattern used by its peer dashboard `content-validation-status.md`.

## Decision

**Functions retains the dict-form `{references: [...]}` legacy escape as accepted state.** Tightening the validator would require populating per-diagram entries on approximately 295 pages — manual editorial work whose value is not currently justified by a policy need. The escape is therefore an intentional design decision, not a bug, and is documented in [`AGENTS.md` — Diagram Source Documentation](https://github.com/yeongseon/azure-functions-practical-guide/blob/main/AGENTS.md#diagram-source-documentation).

The decision is recorded as **deferred to Phase 2e**. There is no committed timeline for Phase 2e. It opens only when the repository owner explicitly decides per-diagram provenance is now required policy.

### What Phase 2d Final actually closed

The closure scope did NOT include any validator tightening. It included only:

1. **Doctests wired into CI** — `python -m doctest scripts/lib/content_scope.py` and `python -m doctest scripts/validate_content_sources.py` are now strict gates in `validate-content-sources.yml`. This freezes the current `get_diagram_sources()` behavior; any future change to legacy-escape activation MUST update the doctests in the same commit.
2. **Removal of an obsolete helper** — `scripts/update_mermaid_metadata.py`, which had zero in-repo references after the migration batches completed, was removed with `git rm`. The migration batches superseded the helper's purpose.
3. **App Service hygiene fix** — App Service PR #102 brought its `validation-status.md` dashboard generator in line with the canonical frontmatter pattern.
4. **Container Apps symmetry PR** — Container Apps received a small PR adding the same doctest CI gate, so the three repositories' validators are operationally identical.
5. **AGENTS.md documentation** — The `### Diagram Source Documentation` section was expanded from a one-line stub into a full description of the canonical shape, the accepted legacy escapes, what is NOT accepted, and the Phase 2e deferral.
6. **This audit artifact** — checked in so the audit data survives PR garbage collection.

## Verification

All three repositories pass the same strict-check matrix locally and in CI:

- `python3 scripts/validate_content_sources.py` — 0 errors
- `python3 scripts/normalize_yaml_frontmatter.py --check` — 0 drift
- `python3 scripts/normalize_content_sources_schema.py --check` — 0 drift
- `python3 scripts/validate_doc_quality.py` — passes
- `python3 -m doctest scripts/lib/content_scope.py -v` — 14 tests pass
- `python3 -m doctest scripts/validate_content_sources.py -v` (Functions only) — 10 tests pass
- `mkdocs build --strict` — builds without errors

## See Also

- [Content Validation Status](content-validation-status.md)
- [Tutorial Validation Status](validation-status.md)
- [`scripts/validate_content_sources.py`](https://github.com/yeongseon/azure-functions-practical-guide/blob/main/scripts/validate_content_sources.py) — `get_diagram_sources()` source
- [`scripts/lib/content_scope.py`](https://github.com/yeongseon/azure-functions-practical-guide/blob/main/scripts/lib/content_scope.py) — `is_in_scope()` source
- [`AGENTS.md` — Diagram Source Documentation](https://github.com/yeongseon/azure-functions-practical-guide/blob/main/AGENTS.md#diagram-source-documentation)
