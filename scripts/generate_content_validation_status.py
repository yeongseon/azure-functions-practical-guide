#!/usr/bin/env python3
"""Generate content validation status dashboard from frontmatter metadata.

Scans in-scope factual-claim markdown files (per ``scripts/lib/content_scope``)
for ``content_validation`` frontmatter and generates a dashboard page showing
verification status of core claims.

Fails fast when any in-scope page contains a tautological placeholder claim
(see ``scripts/lib/content_scope.TAUTOLOGICAL_CLAIM_MARKER``).

Usage:
    python3 scripts/generate_content_validation_status.py
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.content_scope import (  # noqa: E402
    EXCLUDED_SUBPATHS,
    NAVIGATION_INDEXES,
    SCANNED_SECTIONS,
    TAUTOLOGICAL_CLAIM_MARKER,
    is_in_scope,
    is_tautological_text,
)

ICON_VERIFIED = "✅ Verified"
ICON_PENDING = "⚠️ Pending Review"
ICON_UNVERIFIED = "➖ Unverified"
ICON_NO_META = "❓ No Metadata"


def parse_frontmatter(filepath: Path) -> dict[str, Any] | None:
    text = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def get_section_from_path(filepath: Path, docs_dir: Path) -> str:
    rel = filepath.relative_to(docs_dir)
    parts = rel.parts
    if len(parts) > 0:
        return parts[0]
    return "unknown"


def scan_documents(docs_dir: Path) -> list[dict[str, Any]]:
    """Return one record per in-scope factual-claim page.

    Scope is defined by ``scripts/lib/content_scope.is_in_scope``. Pages
    outside scope (navigation indexes, KQL packs, lab guides, tutorials,
    reference look-ups) are intentionally excluded from the dashboard.
    """
    documents = []

    for section in sorted(SCANNED_SECTIONS):
        section_dir = docs_dir / section
        if not section_dir.exists():
            continue

        for md_file in section_dir.rglob("*.md"):
            rel_path = md_file.relative_to(docs_dir)
            if not is_in_scope(rel_path):
                continue

            frontmatter = parse_frontmatter(md_file)

            doc_info = {
                "filepath": md_file,
                "rel_path": str(rel_path),
                "section": get_section_from_path(md_file, docs_dir),
                "filename": md_file.stem,
                "title": md_file.stem.replace("-", " ").title(),
                "has_content_sources": False,
                "has_content_validation": False,
                "validation_status": "no_metadata",
                "core_claims_count": 0,
                "verified_claims_count": 0,
                "tautological_claims_count": 0,
                "last_reviewed": None,
            }

            if frontmatter and isinstance(frontmatter, dict):
                if "content_sources" in frontmatter:
                    doc_info["has_content_sources"] = True

                cv = frontmatter.get("content_validation", {})
                if cv and isinstance(cv, dict):
                    doc_info["has_content_validation"] = True
                    doc_info["validation_status"] = cv.get("status", "unverified")
                    doc_info["last_reviewed"] = cv.get("last_reviewed")

                    claims = cv.get("core_claims", [])
                    if isinstance(claims, list):
                        doc_info["core_claims_count"] = len(claims)
                        doc_info["verified_claims_count"] = sum(
                            1
                            for c in claims
                            if isinstance(c, dict) and c.get("verified", False)
                        )
                        doc_info["tautological_claims_count"] = sum(
                            1
                            for c in claims
                            if isinstance(c, dict)
                            and is_tautological_text(c.get("claim"))
                        )

            documents.append(doc_info)

    return documents


def get_status_icon(status: str) -> str:
    mapping = {
        "verified": ICON_VERIFIED,
        "pending_review": ICON_PENDING,
        "unverified": ICON_UNVERIFIED,
        "no_metadata": ICON_NO_META,
    }
    return mapping.get(status, ICON_NO_META)


def count_mermaid_diagrams(docs_dir: Path) -> int:
    count = 0
    for md_file in docs_dir.rglob("*.md"):
        rel_path = md_file.relative_to(docs_dir)
        if any(part.startswith("_") or part.startswith(".") for part in rel_path.parts):
            continue

        text = md_file.read_text(encoding="utf-8")
        count += len(re.findall(r"^```mermaid\s*$", text, re.MULTILINE))
    return count


def _scope_summary_lines() -> list[str]:
    sections = ", ".join(f"`docs/{s}/`" for s in sorted(SCANNED_SECTIONS))
    excluded = ", ".join(f"`docs/{p}`" for p in EXCLUDED_SUBPATHS)
    nav_examples = ", ".join(
        f"`docs/{p}`" for p in sorted(NAVIGATION_INDEXES) if "/" in p
    )
    return [
        "This page tracks `content_validation` metadata for **in-scope "
        "factual-claim documents** under "
        f"{sections}. Pages outside this scope — navigation indexes "
        f"({nav_examples}), reference-lookup KQL packs and lab guides "
        f"({excluded}), tutorials, language guides, and start-here "
        "landing pages — are not counted here, even when legacy "
        "`content_validation` blocks exist on them (the cleanup tool "
        "removes those blocks; see "
        "`scripts/remove_out_of_scope_validation.py`). See `AGENTS.md` "
        "§Text Content Validation for the full policy and "
        "`scripts/lib/content_scope.py` for the executable scope definition.",
    ]


def generate_dashboard(
    documents: list[dict[str, Any]], docs_dir: Path, today: date
) -> str:
    total = len(documents)
    verified = sum(1 for d in documents if d["validation_status"] == "verified")
    pending = sum(1 for d in documents if d["validation_status"] == "pending_review")
    unverified = sum(1 for d in documents if d["validation_status"] == "unverified")
    no_meta = sum(1 for d in documents if d["validation_status"] == "no_metadata")

    diagram_count = count_mermaid_diagrams(docs_dir)

    lines: list[str] = []
    lines.append("---")
    lines.append("content_sources:")
    lines.append("  - type: self-generated")
    lines.append(
        "    justification: Auto-generated dashboard tracking content validation status"
    )
    lines.append("---")
    lines.append("")
    lines.append("# Content Validation Status")
    lines.append("")
    lines.extend(_scope_summary_lines())
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(f"*Generated: {today.isoformat()}*")
    lines.append("")
    lines.append(
        "| Content Type | Total | Verified | Pending | Unverified | No Metadata |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|")
    lines.append(
        f"| Mermaid Diagrams | {diagram_count} | {diagram_count} | 0 | 0 | 0 |"
    )
    lines.append(
        "| In-Scope Factual-Claim Documents "
        f"| {total} | {verified} | {pending} | {unverified} | {no_meta} |"
    )
    lines.append("")

    if verified == total and total > 0:
        lines.append('!!! success "All In-Scope Documents Verified"')
        lines.append(
            "    Every in-scope factual-claim document has verified "
            "Microsoft Learn sources for its core claims."
        )
    elif no_meta > 0:
        lines.append('!!! warning "Validation In Progress"')
        lines.append(
            f"    {no_meta} in-scope document(s) need `content_validation` "
            "metadata added."
        )
    lines.append("")

    lines.append("<!-- diagram-id: content-validation-status-pie -->")
    lines.append("```mermaid")
    lines.append("pie title In-Scope Document Validation Status")
    if verified > 0:
        lines.append(f'    "Verified" : {verified}')
    if pending > 0:
        lines.append(f'    "Pending Review" : {pending}')
    if unverified > 0:
        lines.append(f'    "Unverified" : {unverified}')
    if no_meta > 0:
        lines.append(f'    "No Metadata" : {no_meta}')
    lines.append("```")
    lines.append("")

    by_section: dict[str, list[dict[str, Any]]] = {}
    for d in documents:
        section = d["section"]
        by_section.setdefault(section, []).append(d)

    lines.append("## By Section")
    lines.append("")

    section_order = ["platform", "best-practices", "operations", "troubleshooting"]

    for section in section_order:
        if section not in by_section:
            continue

        section_docs = by_section[section]
        section_display = section.replace("-", " ").title()

        lines.append(f"### {section_display}")
        lines.append("")
        lines.append("| Document | Has Sources | Status | Claims | Last Reviewed |")
        lines.append("|---|---|---|---|---|")

        section_docs.sort(key=lambda d: d["filename"])

        for d in section_docs:
            doc_link = f"[{d['title']}](../{d['rel_path']})"
            has_sources = "✅" if d["has_content_sources"] else "❌"
            status = get_status_icon(d["validation_status"])

            if d["core_claims_count"] > 0:
                claims = f"{d['verified_claims_count']}/{d['core_claims_count']}"
            else:
                claims = "—"

            last_reviewed = d["last_reviewed"] if d["last_reviewed"] else "—"

            lines.append(
                f"| {doc_link} | {has_sources} | {status} | {claims} | {last_reviewed} |"
            )

        lines.append("")

    lines.append("## Validation Categories")
    lines.append("")
    lines.append("### Source Types")
    lines.append("")
    lines.append("| Type | Description | Allowed? |")
    lines.append("|---|---|---|")
    lines.append(
        "| `mslearn` | Content directly from or based on Microsoft Learn | Yes |"
    )
    lines.append(
        "| `mslearn-adapted` | Microsoft Learn content adapted for this guide | Yes, with source URL |"
    )
    lines.append(
        "| `self-generated` | Original content created for this guide | Requires justification |"
    )
    lines.append("| `community` | From community sources | Not for core content |")
    lines.append("| `unknown` | Source not documented | Must be validated |")
    lines.append("")

    lines.append("### Validation Status")
    lines.append("")
    lines.append("| Status | Description |")
    lines.append("|---|---|")
    lines.append("| `verified` | All core claims traced to Microsoft Learn sources |")
    lines.append(
        "| `pending_review` | Document exists but claims need source verification |"
    )
    lines.append("| `unverified` | New document, no validation performed |")
    lines.append("")

    lines.append("## How to Add Validation")
    lines.append("")
    lines.append(
        "Before adding metadata, confirm the page is in scope. The block is "
        "required ONLY for factual-claim pages under `docs/platform/`, "
        "`docs/best-practices/`, `docs/operations/`, and `docs/troubleshooting/` "
        "(excluding `troubleshooting/kql/`, `troubleshooting/lab-guides/`, and "
        "navigation landing pages listed in "
        "`scripts/lib/content_scope.NAVIGATION_INDEXES`)."
    )
    lines.append("")
    lines.append(
        "For an in-scope page, add a `content_validation` block to its frontmatter:"
    )
    lines.append("")
    lines.append("```yaml")
    lines.append("---")
    lines.append("content_sources:")
    lines.append("  - type: mslearn-adapted")
    lines.append("    url: https://learn.microsoft.com/en-us/azure/azure-functions/...")
    lines.append("content_validation:")
    lines.append("  status: verified")
    lines.append("  last_reviewed: 2026-04-12")
    lines.append("  reviewer: agent")
    lines.append("  core_claims:")
    lines.append(
        '    - claim: "Flex Consumption supports VNet integration with regional VNet."'
    )
    lines.append(
        "      source: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan"
    )
    lines.append("      verified: true")
    lines.append("---")
    lines.append("```")
    lines.append("")
    lines.append(
        "Each `core_claim` MUST be a verifiable factual assertion about Azure "
        "Functions behavior (a documented limit, default, or feature). "
        'Meta-statements such as "this page uses Microsoft Learn as the '
        f'primary source basis" are tautological and rejected — the marker '
        f"text `{TAUTOLOGICAL_CLAIM_MARKER}` triggers a fail-fast in this "
        "generator."
    )
    lines.append("")
    lines.append("Then regenerate this page:")
    lines.append("")
    lines.append("```bash")
    lines.append("python3 scripts/generate_content_validation_status.py")
    lines.append("```")
    lines.append("")

    lines.append("## See Also")
    lines.append("")
    lines.append("- [Tutorial Validation Status](validation-status.md)")
    lines.append("- [CLI Cheatsheet](cli-cheatsheet.md)")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate content validation status dashboard"
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("docs"),
        help="Path to docs directory (default: docs)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/reference/content-validation-status.md"),
        help="Output file path",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    docs_dir = project_root / args.docs_dir
    output_path = project_root / args.output

    if not docs_dir.exists():
        print(f"Error: docs directory not found: {docs_dir}")
        raise SystemExit(1)

    documents = scan_documents(docs_dir)

    tautological_docs = [d for d in documents if d["tautological_claims_count"] > 0]
    if tautological_docs:
        print(
            f"ERROR: {len(tautological_docs)} in-scope document(s) contain "
            f"tautological placeholder claims (text containing "
            f"'{TAUTOLOGICAL_CLAIM_MARKER}').",
            file=sys.stderr,
        )
        print(
            "Tautological claims are forbidden by AGENTS.md \u00a7Text Content "
            "Validation (Agent Rule 3). Edit each offending file to replace the "
            "placeholder claim with a verifiable factual assertion about Azure "
            "Functions behavior, or — if the page does not actually contain "
            "factual claims — remove the `content_validation` block entirely.",
            file=sys.stderr,
        )
        print("Offending files:", file=sys.stderr)
        for d in tautological_docs:
            print(
                f"  - {d['rel_path']} "
                f"({d['tautological_claims_count']}/{d['core_claims_count']} claims)",
                file=sys.stderr,
            )
        raise SystemExit(1)

    today = date.today()
    dashboard = generate_dashboard(documents, docs_dir, today)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(dashboard, encoding="utf-8")

    verified = sum(1 for d in documents if d["validation_status"] == "verified")
    print(
        f"Scanned {len(documents)} in-scope documents, "
        f"{verified} verified, "
        f"generated {output_path}"
    )


if __name__ == "__main__":
    main()
