# Contributing to Azure Functions Practical Guide

Thank you for your interest in contributing!

This file is the workflow authority for humans and coding agents: issue authoring,
triage, focused implementation, PR review, and merge decisions. `AGENTS.md` is the
shared agent entry point; the detailed Functions-specific content contract lives
in [the contributor reference](docs/contributing/content-contract.md).
For document templates and writing standards, use the site contributing guide:

**[Contributing Guide](https://yeongseon.dev/azure-functions-python/practical-guide/contributing/)**

This guide covers:

- Repository structure and content organization
- Document templates and writing standards (Markdown, CLI style, PII rules)
- Local development setup and build validation
- Pull request process and review standards

## Issue Lifecycle

### Authoring and Required Sections

Use the [Title Convention](#title-convention) and these issue sections, including
when creating an issue through the API or CLI rather than a form:

| Section | Required content |
|---|---|
| Context | Repository-local problem, affected files/pages, evidence, reader/user impact, and proposed work |
| Acceptance Checklist | Observable completion criteria as Markdown checkboxes; distinguish source review from Azure execution or independent reproduction |
| Out of scope | Explicit boundaries that keep this task focused |
| References | Relevant local issues/PRs, Microsoft Learn sources, and genuine upstream dependencies with their relationship explained; write `None` if absent |

Follow [Issue Scope](#issue-scope) for the repository-specific evidence contract,
duplicate/context preflight, and post-save field checks established by merged
PR #142 (#141). Extend matching work rather than opening another tracker. Forms
are an authoring aid, not enforcement for API/CLI submissions.

### Labels and Triage

New issues start with `needs-triage`. The issue forms may assign it only while
that exact repository label exists; API/CLI authors must also verify it after
saving. Contributors may suggest classifications, but maintainers own triage.

| Label | Meaning |
|---|---|
| `priority:critical` | Evidenced active security exposure, production data loss, or equivalent immediate harm; explain urgency, not just a hypothetical risk |
| `priority:high` | Unsafe guidance, broken supported behavior, or a major reader/user blocker |
| `priority:medium` | Valuable correctness or usability improvement with a workaround and no immediate harm |
| `priority:low` | Optional polish or low-impact work behind correctness and safety fixes |
| `size: XS` | One localized, straightforward correction |
| `size: S` | A small bounded change with targeted validation |
| `size: M` | Several related changes and meaningful integration or documentation validation |
| `size: L` | Broad coordination or substantial implementation/validation; look for useful splits |
| `size: XL` | Too large or uncertain for one focused PR; investigate and split into independently useful tasks where practical |

Size estimates effort and uncertainty, not severity or a promised delivery date.
Use exactly one canonical priority and one size on each triaged actionable issue;
`priority: high` is a legacy spelling, not an additional priority tier. Type labels
such as `bug`, `documentation`, or `enhancement` complement these classifications.

1. Confirm validity, local evidence, duplicates, type, scope, completion criteria,
   dependencies, and estimated size. Close invalid/duplicate issues with a reason
   and link to the surviving issue rather than labeling them ready for work.
2. Compare impact, urgency, dependencies, and effort against **all open issues**,
   not only the current batch. Record the relative order and reasoning on the
   issue or PR; do not create a new mandatory tracker.
3. Set one priority and one size, fetch the issue to verify both, and only then
   remove `needs-triage` from valid actionable work. If a required label is
   unavailable, retain `needs-triage`, record the intended classification, and
   request maintainer provisioning; never silently substitute a different label.
4. Repeat triage after material scope changes, new safety evidence, or changed
   dependencies. Restore `needs-triage` until re-evaluation is complete. After
   delivery, reassess remaining backlog priorities and record any changed order.

**Hosted prerequisites:** inspect actual label definitions before relying on them.
The governance implementation audit found `needs-triage`, all five size labels,
and high/medium/low priorities, but no `priority:critical`. A maintainer must
provision that label before it can be used. These text rules do not configure
GitHub label automation or branch protection; report unsupported settings honestly
and do not change hosted settings without separate authorization.

## Focused Implementation

1. Start from a triaged issue and inspect the existing code, documentation,
   tests, and related PRs. Choose the smallest viable correction and a bounded
   validation plan before editing.
2. Make an explicit **overengineering assessment** in the issue or PR: compare
   the existing simple path with the proposed change and explain any necessary
   complexity. Prefer reuse; no speculative abstractions, libraries, shared
   frameworks, broad refactors, extra CI workflows/gates, redundant tests,
   repeated diagrams, documentation, or screenshots. Preserve a straightforward
   alternative. Split oversized work instead of expanding a single PR.
3. Implement only the accepted scope in a small reviewable PR. Keep unrelated
   improvements separate. Retain Functions-specific source metadata,
   troubleshooting evidence, PII protections, and truthful validation dates.
4. Run applicable existing validators and targeted regression tests; use
   `mkdocs build --strict` locally for documentation (recommended; required
   GitHub CI remains authoritative). Record commands, actual results,
   limitations, and the tested commit. Source-reviewed, Azure-executed, and
   independently reproduced are different evidence levels; use `NOT_RUN` for
   unperformed Azure tests. Ordinary docs work does not require paid Azure E2E.
5. Use the PR template sections: **Summary**, **Changes**, **Type of Change**,
   **Validation**, **Checklist**, **Related Issues**. Include scope/risks and
   remaining work under Changes; keep significant decisions in the issue or PR,
   not another mandatory decision template.
6. Review and record required GitHub CI links and findings on the **final PR
   head SHA**. New commits invalidate earlier exact-head evidence; refresh the
   relevant checks and review. Resolve blocking findings and verify captions,
   rendering, and final-image PII where applicable. AI reviews are advisory.
7. Only the responsible maintainer authorizes squash merge after required checks
   pass; do not bypass gates or treat a green build as permission. After an
   authorized merge, verify intended issue closure and reassess the backlog.

### Issue Linkage

Use `Closes #123` only when the PR completes **all accepted repository-local
scope** of that issue. Use `Refs #123` for partial work, prerequisites, or related
context, and list remaining work explicitly. Link same-repository issues in
**Related Issues**, not the PR title. Do not auto-close upstream or sibling work
that this repository does not own.

### Shared Agent Entry Point

Codex and OpenCode start with `AGENTS.md`; Claude Code must read the same file
directly or through the single-line `CLAUDE.md` import. All tools then follow this
workflow authority and the shared Functions content contract. Do not copy long
rules into tool-specific files or automatically install/invoke agent plugins.

## Tool-Neutral PR Review and Merge

Every contribution follows one process, whether human-authored or created
with OpenCode, Codex, Claude Code, ChatGPT, Copilot or another tool.
No Oracle score or particular AI review is required for approval.
AI feedback is optional advisory material.

Required **GitHub CI** results on the final head are authoritative.
Local documentation builds are encouraged, not an additional merge gate.
A maintainer verifies relevant Markdown rendering, screenshot/caption
accuracy, final-image PII safety, outstanding findings and publication
impact before deciding whether to squash merge. Keep all existing PII,
documentation and publishing protections; do not authorize autonomous
merges based only on AI scores or green CI. CI runner hosting is
independent of this review policy.

### Required validation for every PR

1. **GitHub CI:** all required status checks on the final PR head must
   pass. CI is authoritative; local preview and source checks are
   recommended but not a separate merge prerequisite. This policy
   makes no assumption about CI runner hosting.
2. **Caption and image accuracy:** every added/changed referenced image
   must accurately match its Markdown caption and alt text.
3. **Final-image PII verification:** visually inspect the **final committed
   bytes** of every added/changed referenced PNG/WebP for subscription
   or tenant identifiers, employee data or misleading redactions.
   Re-encoded WebP must be rechecked; do not infer it from a PNG.
4. **Security and content:** preserve existing documentation, PII,
   repetition, screenshot integrity and publishing checks; no
   unresolved critical/security issues or unreviewed sensitive assets.
5. **Maintainer decision:** the responsible maintainer reviews final
   code/content, required CI results, image checks and outstanding
   findings, then decides whether to merge. For high-risk publishing
   or permissions changes, obtain independent scrutiny.

### Merge procedure

1. Record required GitHub CI links and the final-image/PII verification
   results in the PR. AI review comments are optional and not test
   evidence or approval.
2. Only after the responsible maintainer's decision, use squash merge:
   `gh pr merge <pr> --squash --delete-branch`.
3. Never use `--admin` to bypass required checks. Do not silently
   downgrade visual verification, security or documentation policy.
4. An autonomous agent may prepare the PR and evidence but must not
   treat a passing score or green CI as permission to merge without
   the maintainer's decision.

### Stop conditions

- Any required CI check is pending or failing.
- A referenced image cannot be verified against the final committed
  bytes or contains unaddressed PII.
- Blocking security, scope or factual accuracy findings remain.
- The responsible maintainer has not authorized the merge.

Report remaining blockers instead of merging.

## Issue Scope

- Describe the problem, evidence, proposed work, priority, and completion criteria
  using this repository's own responsibilities and user impact.
- Adapt reusable ideas to the actual files and conventions here. Another
  project's policy, observations, or release plan do not establish this
  repository's requirements.
- Keep relevant technical evidence and source attribution, including actual
  dependencies, integrations, upstream defects, and official documentation.
  Explain the relationship and the work owned by this repository. Apply the
  same local-evidence requirement to explicitly requested comparisons.
- Before creating or editing an issue, search for duplicates and review every
  project name and repository link in the title and body. Remove unrelated
  copied context; the work must be understandable without an unrelated issue.
- After saving, fetch the issue again and verify its title, body, and labels
  before reporting completion. This applies to API and CLI authoring as well
  as the issue templates.

## Title Convention

This section is the single source of truth for issue, pull request, and commit titles in this repository. `AGENTS.md`, the pull request template, the issue forms, and the documentation site point here instead of restating the rules.

Issues, pull requests, and the final squash commit on the default branch all use:

```text
type: description
type(scope): description
```

- Write titles in English.
- `type` and `scope` are lowercase. Put exactly one space after the colon.
- `scope` is optional. Add it only when it narrows the area; do not add one just for uniformity.
- `description` states what changes and why, concisely. Start with a lowercase word, but keep the spelling of API names, acronyms, error codes, and proper nouns.
- No trailing period.
- No priority, size, status, or owner markers, and no bracket prefixes such as `[Bug]`, `[Feature]`, or `[WIP]`. Use labels and Draft pull requests instead.
- An issue title may describe the problem; the pull request title describes the change that resolves it. Keep them aligned when they cover the same work, without forcing identical wording when the scope differs.
- Do not put issue numbers in pull request titles. Link issues in the pull request body with `Closes #123` or `Refs #123`.

| type | use for |
|---|---|
| `feat` | a user-facing feature or capability |
| `fix` | a bug fix in product behavior |
| `docs` | documentation only |
| `test` | adding or changing tests |
| `perf` | a performance improvement |
| `refactor` | internal restructuring that keeps external behavior |
| `ci` | CI and automation workflows |
| `build` | build, packaging, and dependency changes |
| `chore` | maintenance that fits none of the above |
| `style` | formatting only, no behavior change |
| `revert` | reverting an earlier change |

A breaking change adds `!` before the colon: `type!: description` or `type(scope)!: description`. Whether a change is breaking is decided by the maintainers, not by the title alone. This repository does not publish versioned releases, so titles do not drive versioning.

Examples:

```text
docs: correct the hosting-plan comparison
docs(labs): explain storage access failure evidence
docs(readme): clarify the local setup steps
refactor(labs)!: rename the storage verification script arguments
```

Not accepted: `[Bug] crash on save` (bracket prefix, no type), `Fix: crash on save` (uppercase type), `feature: add export` (type not in the table), `fix: crash on save.` (trailing period).

Pull requests are squash-merged and the pull request title becomes the final commit title. GitHub appends the pull request number, for example `docs: correct the hosting-plan comparison (#503)`. The **PR title** check validates the format whenever a pull request is opened, edited, reopened, or updated. Individual commits on a branch are not checked.

Issue titles are not enforced. Anyone can open an issue without knowing this convention; maintainers adjust the title during triage.
