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

## Issue Scope

Follow the [issue-scope guidance in AGENTS.md](AGENTS.md#issue-scope) when
opening or editing an issue. Use this guide's pages, scripts, workflows, and
reader needs to explain the problem and completion criteria, and state why
any external project reference is relevant.

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
