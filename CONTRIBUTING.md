# Contributing to Azure Functions Practical Guide

Thank you for your interest in contributing!

To ensure consistency and quality across this guide, please refer to our full contributing documentation:

**[Contributing Guide](https://yeongseon.dev/azure-functions-python/practical-guide/contributing/)**

This guide covers:

- Repository structure and content organization
- Document templates and writing standards (Markdown, CLI style, PII rules)
- Local development setup and build validation
- Pull request process and review standards

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
refactor!: rename the public configuration keys
```

Not accepted: `[Bug] crash on save` (bracket prefix, no type), `Fix: crash on save` (uppercase type), `feature: add export` (type not in the table), `fix: crash on save.` (trailing period).

Pull requests are squash-merged and the pull request title becomes the final commit title. GitHub appends the pull request number, for example `docs: correct the hosting-plan comparison (#503)`. The **PR title** check validates the format whenever a pull request is opened, edited, reopened, or updated. Individual commits on a branch are not checked.

Issue titles are not enforced. Anyone can open an issue without knowing this convention; maintainers adjust the title during triage.

## Issue Workflow and Triage

Search this repository for duplicates and review the affected pages, scripts and evidence before opening an issue. Write a local task in **Context / Acceptance Checklist / Out of scope / References** order. A relevant upstream dependency may be cited, but another repository's process is not a requirement here.

All new reports begin with `needs-triage`. A maintainer checks the problem's validity, duplicates, user impact, available evidence, smallest useful scope and appropriate type. Then select **exactly one** priority and **exactly one** size; compare urgency against **all open issues** before removing `needs-triage`.

| Priority label | Meaning |
|---|---|
| `priority:critical` | Immediate security/data loss or blocked documentation publication |
| `priority:high` | Serious correctness or reliability; fix before the next publication |
| `priority:medium` | Normal planned work, or limited impact with a workaround |
| `priority:low` | Non-urgent improvement |

| Size label | Scope |
|---|---|
| `size: XS` | Tiny, isolated correction |
| `size: S` | Small, independently reviewable change |
| `size: M` | Moderate, several related changes |
| `size: L` | Broad; split when possible |
| `size: XL` | Too large for one PR; create independently useful child issues |

Priority is impact/urgency; size is effort/scope. Neither belongs in the issue title. Verify the **saved GitHub labels** before removing `needs-triage`; when a label is unavailable or evidence is insufficient, leave triage open and state the blocker. Revisit all open priorities after a material scope/urgency change or completed issue. Avoid extra lane, milestone, WIP or status labels that duplicate native GitHub state.

## Post-Triage Development

1. Confirm the failure or missing capability and its observable success criterion. Identify one simpler change or existing approach before designing anything new.
2. Prefer the smallest direct fix to extra classes, abstractions, wrappers, files, duplicated tutorials, speculative features or more CI gates. Do not create a framework for a single case. Keep Golden evidence and source validation correct without applying experiment requirements to navigation-only pages.
3. Work issue-first in a focused branch. Split `L`/`XL` issues into independently useful changes; do not silently expand scope.
4. Run only relevant tests, source/factual checks, documentation rendering and final-image privacy checks. Static CI is **not** Azure execution evidence.
5. Open a focused PR with the common headings below. Resolve current-head review findings, verify all required GitHub checks on the final SHA, and obtain maintainer authorization before squash merge. Use `Closes #N` only for completed local scope; use `Refs #N` with an explicit remainder otherwise.
6. Reassess the remaining backlog's priority after merge. Never auto-escalate a task simply because it is old or large.

## PR and Coding Agent Rules

PR bodies use `Summary / Changes / Type of Change / Validation / Checklist / Related Issues` in that order. Record actually executed commands/results, supporting documentation, evidence and uncompleted work. The same tool-neutral GitHub CI and responsible-maintainer review process applies to humans, Codex, Claude, OpenCode and Copilot. An AI reviewer or score is optional advice, not approval or a substitute for live verification.

Use root `AGENTS.md` as the common coding-agent entry point. Codex and OpenCode read it directly; recent Claude Code reads it when no separate CLAUDE instructions take precedence, and this repository's one-line `CLAUDE.md` imports it for other versions. Never copy the workflow into tool-specific configuration. Preserve the detailed Functions content, PII and source contract already in `AGENTS.md`.
