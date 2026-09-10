#!/usr/bin/env python3
"""Advisory gate: report in-scope pages that carry no visual aid.

The series mission is comprehensibility. Every other CI gate (repetition,
PII, doc-quality, content sources) inspects **text only**; nothing tracks
whether a page is visually understandable. This gate makes visual coverage
visible in CI without blocking on historical debt:

- **Scope**: exactly the factual-claim pages already defined by
  ``scripts/lib/content_scope.is_in_scope`` (platform, best-practices,
  operations, troubleshooting minus KQL packs / lab guides / navigation
  indexes). Factual pages are where a missing diagram or screenshot hurts
  comprehension the most.
- **Detection**: a page counts as having a visual aid if it contains at
  least one Mermaid code fence, one capture-pipeline ``shot()`` reference,
  or one Markdown image reference.
- **Mode**: WARN-only advisory in this phase. ``--all`` prints per-page
  warnings plus a coverage summary; ``--changed-only --base-ref <sha>``
  narrows the per-page report to files changed since a base ref. The exit
  code is always ``0`` (except usage errors) so CI stays green while the
  metric is being established. Escalation to a blocking gate is a per-repo
  decision tracked in
  `issue #388 <https://github.com/yeongseon/azure-container-apps-practical-guide/issues/388>`_.

Usage::

    python3 scripts/validate_visual_content.py --all
    python3 scripts/validate_visual_content.py --changed-only --base-ref origin/main
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.content_scope import is_in_scope  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

MERMAID_FENCE_RE = re.compile(r"^\s*```mermaid\b", re.MULTILINE)
SHOT_MACRO_RE = re.compile(r"\[\[\[\s*shot\(\s*[\"']")
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\](?:\(|\[)")


def strip_frontmatter(text: str) -> str:
    """Drop the leading YAML frontmatter block from ``text``.

    >>> strip_frontmatter("---\\ndescription: x\\n---\\nbody")
    'body'
    >>> strip_frontmatter("no frontmatter")
    'no frontmatter'
    """
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2].lstrip("\n")
    return text


def page_visual_assets(text: str) -> dict[str, int]:
    """Count visual-asset references in one Markdown page (frontmatter ignored).

    >>> page_visual_assets("```mermaid\\nflowchart TD\\n  A --> B\\n```")
    {'mermaid': 1, 'shots': 0, 'images': 0}
    >>> page_visual_assets('See [[[ shot("overview") ]]] for the blade.')
    {'mermaid': 0, 'shots': 1, 'images': 0}
    >>> page_visual_assets("```mermaid title=\\"diagram\\"\\nflowchart TD\\n```")
    {'mermaid': 1, 'shots': 0, 'images': 0}
    >>> page_visual_assets('![Alt text](../assets/example.webp)')
    {'mermaid': 0, 'shots': 0, 'images': 1}
    >>> page_visual_assets('![Alt text][ref]')
    {'mermaid': 0, 'shots': 0, 'images': 1}
    >>> page_visual_assets('Plain prose with a [link](page.md) only.')
    {'mermaid': 0, 'shots': 0, 'images': 0}
    """
    body = strip_frontmatter(text)
    return {
        "mermaid": len(MERMAID_FENCE_RE.findall(body)),
        "shots": len(SHOT_MACRO_RE.findall(body)),
        "images": len(MARKDOWN_IMAGE_RE.findall(body)),
    }


def has_visual_asset(text: str) -> bool:
    """Return True when the page carries at least one visual aid.

    >>> has_visual_asset("```mermaid\\nflowchart TD\\n```")
    True
    >>> has_visual_asset("text only")
    False
    """
    return any(v > 0 for v in page_visual_assets(text).values())


def in_scope_pages() -> list[Path]:
    """Return factual-claim pages (per ``lib.content_scope``) under docs/."""
    return sorted(
        p for p in DOCS.rglob("*.md") if is_in_scope(p.relative_to(DOCS).as_posix())
    )


def changed_files(base_ref: str) -> list[Path]:
    """Return changed Markdown files between ``base_ref`` and HEAD."""
    diff_args = ["git", "diff", "--name-only"]
    try:
        out = subprocess.run(
            diff_args + ["--merge-base", base_ref, "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=ROOT,
        ).stdout
    except subprocess.CalledProcessError:
        out = subprocess.run(
            diff_args + [f"{base_ref}..HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=ROOT,
        ).stdout
    return [
        ROOT / line.strip() for line in out.splitlines() if line.strip().endswith(".md")
    ]


def report(pages: list[Path], label: str) -> int:
    """Print per-page warnings + a coverage summary. Always non-blocking."""
    warned: list[str] = []
    for path in pages:
        rel = path.relative_to(ROOT).as_posix()
        if not is_in_scope(path.relative_to(DOCS).as_posix()):
            continue
        if not has_visual_asset(path.read_text(encoding="utf-8")):
            warned.append(rel)
            print(f"WARN: no diagram or screenshot on {rel}")

    total = len(pages)
    covered = total - len(warned)
    pct = (100.0 * covered / total) if total else 100.0
    print(
        f"\n{label}: {covered}/{total} in-scope pages carry a visual aid "
        f"({pct:.1f}%). Advisory gate — exit 0 regardless (see issue #388)."
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--all", action="store_true", help="Scan every in-scope page (default)."
    )
    mode.add_argument(
        "--changed-only",
        action="store_true",
        help="Report only Markdown files changed since --base-ref.",
    )
    parser.add_argument(
        "--base-ref",
        default="origin/main",
        help="Base ref for --changed-only (default: origin/main).",
    )
    args = parser.parse_args()

    if args.changed_only:
        pages = [
            p
            for p in changed_files(args.base_ref)
            if p.exists()
            and DOCS in p.parents
            and is_in_scope(p.relative_to(DOCS).as_posix())
        ]
        return report(pages, f"changed in-scope files vs {args.base_ref}")
    return report(in_scope_pages(), "full repo")


if __name__ == "__main__":
    sys.exit(main())
