"""Generate a read-only tutorial claim/evidence report; --as-of fixes its clock."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.lib.tutorial_validation import (
    METHODS,
    STALENESS_DAYS,
    Tutorial,
    assess_method,
    extract_tutorial_info,
    tutorial_status,
)
from scripts.lib.yaml_style import dump_frontmatter

TUTORIAL_GLOB = "language-guides/*/tutorial/*/*.md"
PLAN_DISPLAY = {
    "consumption": "Consumption (Y1)",
    "flex-consumption": "Flex Consumption (FC1)",
    "premium": "Premium (EP)",
    "dedicated": "Dedicated (App Service)",
}


def cell(text: str) -> str:
    return text.replace("|", "&#124;").replace("\n", " ")


def generate_dashboard(tutorials: list[Tutorial], today: date) -> str:
    """Render per-method audit rows, retaining claims separately from trust."""
    assessments = [
        [assess_method(t.validation.get(method), today, t.root) for method in METHODS]
        for t in tutorials
    ]
    counts = Counter(tutorial_status(methods) for methods in assessments)
    method_counts = Counter(m.freshness for methods in assessments for m in methods)
    source = (
        "https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview"
    )
    frontmatter = {
        "content_sources": {
            "references": [{"type": "mslearn-adapted", "url": source}],
            "diagrams": [
                {
                    "id": "tutorial-validation-status-pie",
                    "type": "pie",
                    "source": "self-generated",
                    "justification": "Generated historical claim freshness, not proof of Azure execution.",
                    "based_on": [source],
                }
            ],
        }
    }
    lines = [
        "---",
        dump_frontmatter(frontmatter).rstrip(),
        "---",
        "",
        "# Tutorial Validation Status",
        "",
        (
            "This is an **offline audit of reported tutorial results**, not a current Azure-verified pass count. "
            "Historical `pass`/`fail` claims and attempt dates are preserved; absent run-owned evidence stays **unverified**."
        ),
        "",
        "## Scope",
        "",
        (
            "Leaf runbooks under `docs/language-guides/*/tutorial/<hosting-plan>/*.md` are included; "
            "`index.md` chooser pages are excluded. Labs use the [existing lab evidence audit](validation-evidence-audit.md), "
            "not tutorial validation or factual-claim `content_validation` counts."
        ),
        "",
        "## Summary",
        "",
        "The June snapshot counted 120 tutorials; this inventory counts 158. The additional 38 (30 PowerShell and 8 testing/container pages) already existed but were absent from that snapshot; they are not newly executed tutorials.",
        "",
        f"*Generated / freshness as of: {today.isoformat()}*",
        "",
        (
            "This is a dated snapshot, not a rolling live badge. Regenerate to assess a later date. "
            f"Fresh means age ≤{STALENESS_DAYS} days; stale means age >{STALENESS_DAYS} days, including failed attempts. "
            "Freshness never upgrades evidence trust. Invalid metadata takes precedence, then failures, in tutorial totals; "
            "per-method counts below include the failed attempt's age."
        ),
        "",
        "| Historical tutorial claim | Count |",
        "|---|---:|",
        f"| Total tutorials | {len(tutorials)} |",
    ]
    categories = (
        "Fresh pass claim",
        "Stale pass claim",
        "Failed claim",
        "Not tested / no data",
        "Invalid metadata",
    )
    lines.extend(f"| {label} | {counts[label]} |" for label in categories)
    lines.extend(["", "| Method freshness / evidence | Count |", "|---|---:|"])
    lines.extend(
        f"| {label} | {method_counts[label]} |"
        for label in ("fresh", "stale", "NOT_RUN", "static-only", "unknown", "invalid")
    )
    lines.extend(
        [
            f"| Methods with unverified evidence trust | {sum(len(ms) for ms in assessments)} |",
            "",
            "<!-- diagram-id: tutorial-validation-status-pie -->",
            "```mermaid",
            "pie title Historical tutorial claim freshness",
        ]
    )
    lines.extend(
        f'    "{label}" : {counts[label]}' for label in categories if counts[label]
    )
    lines.extend(
        [
            "```",
            "",
            "## What Each Term Means",
            "",
            "| Field | Meaning / limits |",
            "|---|---|",
            "| Source review | [Content Validation Status](content-validation-status.md) tracks Learn-source review for its own factual-page scope, not tutorial execution. |",
            "| Code/static check | Legacy `syntax_validated` means static-only, not a live Azure pass; its historical date is retained but never counted as Azure freshness. Offline pytest, lint and builds check code/docs only; see PR/CI results. |",
            "| Live Azure run | `pass`/`fail` and `last_tested` below are historical author-entered claims; `not_tested` with no date means NOT_RUN. Missing history is unknown, not proof no run happened. |",
            "| Evidence trust | `unverified` until run identity, executed revision, method, captured environment and retained sanitized artifacts/digests are checked. A resolving reference is not an attestation. |",
            "| Reproduction status | Not independently reproduced by this audit; source review and offline replay are not new live runs. |",
            "| Recovery | Not established by a tutorial pass; needs a post-mitigation probe/window where relevant. |",
            "| Cleanup | Not established by deployment success or a cleanup command example; needs its own retained outcome or explicit non-applicability. |",
            "",
            (
                "Vocabulary and provenance requirements follow the [evidence and hypothesis contract](../troubleshooting/methodology/troubleshooting-method.md#evidence-and-hypothesis-contract). "
                "No tutorial in this inventory currently binds a run/environment/artifact set in its method metadata. "
                "Inline output excerpts and tool versions may be useful reported history, but cannot by themselves bind an end-to-end run. "
                "The missing bindings remain audit gaps, not evidence that the historical runs were fabricated."
            ),
            "",
            "## Per-Method Validation and Evidence Audit",
            "",
            (
                "Tool versions are reported metadata, not a complete environment capture. Each row keeps its own date; "
                "a later Bicep run cannot refresh CLI freshness (or vice versa). "
                "Recovery, cleanup and independent reproduction are **not established** for all tutorial rows in this audit."
            ),
            "",
        ]
    )
    for language in sorted({t.language for t in tutorials}):
        lines.extend(
            [
                f"### {language}",
                "",
                "| Tutorial / plan | Method | Reported result | Last tested / attempted | Freshness | Reported tools | Evidence trust | Run / environment / retained artifacts |",
                "|---|---|---|---|---|---|---|---|",
            ]
        )
        for tutorial, methods in zip(tutorials, assessments, strict=True):
            if tutorial.language != language:
                continue
            link = f"[{tutorial.title}](../{tutorial.rel_path}) / {PLAN_DISPLAY.get(tutorial.plan, tutorial.plan)}"
            for name, assessment in zip(METHODS, methods, strict=True):
                values = (
                    link,
                    name,
                    assessment.result,
                    assessment.last_tested,
                    assessment.freshness,
                    assessment.tools,
                    assessment.trust,
                    assessment.binding,
                )
                lines.append("| " + " | ".join(cell(value) for value in values) + " |")
        lines.append("")
    lines.extend(
        [
            "## How to Update",
            "",
            (
                "Follow the [tutorial validation rules](../contributing/content-contract.md#agent-rules-for-validation): "
                "a pass requires end-to-end Azure execution; a failed Azure attempt records fail with the genuine attempt date. "
                "Preserve the other method and all historical dates when no new execution occurs. "
                "Never substitute source review, document editing, static checks or offline replay for live execution."
            ),
            "",
            (
                "Optional method-level `run_id` and repository-relative `evidence_ref` (Markdown run note, optionally `#heading`) "
                "locate an existing run identity record; do not invent identifiers retrospectively. "
                "The note must follow the existing experiment-log contract and link the executed tutorial/method, "
                "environment, captures and digests. The generator checks path/anchor/run identity only; "
                "method/date/environment/artifact provenance still requires independent review and remains unverified here."
            ),
            "",
            "Reproduce this exact snapshot (omit `--as-of` to use today's date):",
            "",
            "```bash",
            f"python3 scripts/generate_validation_status.py --as-of {today.isoformat()}",
            f"python3 scripts/generate_validation_status.py --as-of {today.isoformat()} --check",
            "```",
            "",
            "`--check` is read-only and fails on drift, including a changed as-of date. No Azure access is performed.",
            "",
            "## See Also",
            "",
            "- [Existing Lab Evidence Audit](validation-evidence-audit.md)",
            "- [Content Validation Status](content-validation-status.md)",
            "- [Tutorial Overview & Plan Chooser](../language-guides/python/tutorial/index.md)",
            "",
            "## Sources",
            "",
            f"- [Microsoft Learn overview]({source})",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs-dir", type=Path, default=Path("docs"))
    parser.add_argument(
        "--output", type=Path, default=Path("docs/reference/validation-status.md")
    )
    parser.add_argument(
        "--as-of",
        type=date.fromisoformat,
        default=date.today(),
        help="Freshness snapshot date (YYYY-MM-DD); defaults to today",
    )
    parser.add_argument("--check", action="store_true", help="Read-only drift check")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    docs_dir, output = root / args.docs_dir, root / args.output
    if not docs_dir.is_dir():
        parser.error(f"docs directory not found: {docs_dir}")
    tutorials = [
        extract_tutorial_info(path, docs_dir)
        for path in sorted(docs_dir.glob(TUTORIAL_GLOB))
        if path.name != "index.md"
    ]
    report = generate_dashboard(tutorials, args.as_of)
    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != report:
            print(f"Dashboard drift: use --as-of {args.as_of}", file=sys.stderr)
            raise SystemExit(1)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    print(
        f"Scanned {len(tutorials)} tutorials; generated {output} as of {args.as_of}; no Azure execution"
    )


if __name__ == "__main__":
    main()
