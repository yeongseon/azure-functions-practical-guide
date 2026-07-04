#!/usr/bin/env python3
"""Remove tautological `content_validation` blocks from documentation frontmatter.

Rationale: AGENTS.md ("Agent Rules for Content Validation", rule 3) forbids
meta-statement core_claims; this tool strips blocks that consist only of them.
A `content_validation` block is considered tautological (and therefore safe to
remove) when ALL of its `core_claims` carry the placeholder text "primary source
basis", which is a meta-statement rather than a verifiable factual assertion.

This script:

1. Discovers Markdown files containing the placeholder text in `docs/`.
2. Parses each file's YAML frontmatter with PyYAML.
3. Verifies that EVERY core_claim is tautological (safety guard - a file with
   even one real claim is skipped and reported for manual review).
4. Surgically removes the `content_validation:` block from the frontmatter text
   using a regex anchored to the YAML block scalar (preserves all other keys,
   ordering, quoting style, and comments).

Usage:
    python3 scripts/remove_tautological_validation.py                # dry-run
    python3 scripts/remove_tautological_validation.py --apply        # write
    python3 scripts/remove_tautological_validation.py --apply --quiet
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.content_scope import (  # noqa: E402
    TAUTOLOGICAL_CLAIM_MARKER,
    is_tautological_text,
)

CONTENT_VALIDATION_BLOCK = re.compile(
    r"^content_validation:[ \t]*\n"
    r"(?:[ \t]+[^\n]*\n|[ \t]*\n)*",
    re.MULTILINE,
)

FRONTMATTER_DELIMITER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def find_candidate_files(docs_dir: Path) -> list[Path]:
    candidates: list[Path] = []
    marker = TAUTOLOGICAL_CLAIM_MARKER.casefold()
    for md_file in sorted(docs_dir.rglob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        if marker in text.casefold():
            candidates.append(md_file)
    return candidates


def split_frontmatter(text: str) -> tuple[str | None, str, str]:
    match = FRONTMATTER_DELIMITER.match(text)
    if not match:
        return None, "", text
    yaml_text = match.group(1)
    full_block = match.group(0)
    body = text[match.end() :]
    return yaml_text, full_block, body


def is_tautological_claim(claim: Any) -> bool:
    if not isinstance(claim, dict):
        return False
    return is_tautological_text(claim.get("claim"))


def classify(filepath: Path) -> tuple[str, str | None]:
    """Classify a file for removal eligibility.

    Returns (decision, reason) where decision is one of:
        "remove"         - all core_claims are tautological, safe to strip
        "skip-mixed"     - file has a mix of real and tautological claims
        "skip-no-block"  - placeholder text exists outside content_validation
        "skip-no-yaml"   - frontmatter could not be parsed
    """
    text = filepath.read_text(encoding="utf-8")
    yaml_text, _, _ = split_frontmatter(text)
    if yaml_text is None:
        return "skip-no-yaml", "no frontmatter delimiters"

    try:
        frontmatter = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        return "skip-no-yaml", f"YAML parse error: {exc}"

    if not isinstance(frontmatter, dict):
        return "skip-no-yaml", "frontmatter is not a mapping"

    cv = frontmatter.get("content_validation")
    if not isinstance(cv, dict):
        return "skip-no-block", "placeholder text not inside content_validation"

    claims = cv.get("core_claims", [])
    if not isinstance(claims, list) or not claims:
        return "skip-no-block", "content_validation has no core_claims list"

    tautological = [is_tautological_claim(c) for c in claims]
    if all(tautological):
        return "remove", None
    if any(tautological):
        return (
            "skip-mixed",
            f"{sum(tautological)}/{len(claims)} claims are tautological - manual review",
        )
    return "skip-no-block", "core_claims contain no tautological text"


def remove_content_validation(text: str) -> tuple[str, int]:
    yaml_text, full_block, body = split_frontmatter(text)
    if yaml_text is None:
        return text, 0

    if not yaml_text.endswith("\n"):
        yaml_text = yaml_text + "\n"

    new_yaml, n = CONTENT_VALIDATION_BLOCK.subn("", yaml_text)
    if n == 0:
        return text, 0

    new_frontmatter = f"---\n{new_yaml}---\n"
    return new_frontmatter + body, n


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("docs"),
        help="Path to docs directory (default: docs)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes to disk (default: dry-run)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-file output",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    docs_dir = project_root / args.docs_dir
    if not docs_dir.exists():
        print(f"Error: docs directory not found: {docs_dir}", file=sys.stderr)
        return 1

    candidates = find_candidate_files(docs_dir)
    if not candidates:
        print("No files contain the placeholder text. Nothing to do.")
        return 0

    removed: list[Path] = []
    skipped: list[tuple[Path, str, str]] = []

    for filepath in candidates:
        decision, reason = classify(filepath)
        rel = filepath.relative_to(project_root)

        if decision != "remove":
            skipped.append((filepath, decision, reason or ""))
            if not args.quiet:
                print(f"  SKIP    {rel}  [{decision}: {reason}]")
            continue

        text = filepath.read_text(encoding="utf-8")
        new_text, n = remove_content_validation(text)
        if n == 0:
            skipped.append((filepath, "skip-regex-miss", "regex did not match"))
            if not args.quiet:
                print(f"  SKIP    {rel}  [regex did not match block]")
            continue

        if args.apply:
            filepath.write_text(new_text, encoding="utf-8")
            if not args.quiet:
                print(f"  REMOVE  {rel}")
        else:
            if not args.quiet:
                print(f"  WOULD   {rel}")

        removed.append(filepath)

    print("")
    print("Summary:")
    print(f"  Candidates scanned: {len(candidates)}")
    print(f"  Tautological blocks removed: {len(removed)}")
    print(f"  Skipped: {len(skipped)}")
    if not args.apply and removed:
        print("")
        print("Dry-run only. Re-run with --apply to write changes.")

    if skipped and not args.quiet:
        print("")
        print("Skipped files (require manual review):")
        for filepath, decision, reason in skipped:
            print(f"  - {filepath.relative_to(project_root)}  [{decision}: {reason}]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
