#!/usr/bin/env python3
"""Remove ``content_validation`` blocks from out-of-scope documentation pages.

A page is considered out-of-scope for ``content_validation`` when
:func:`lib.content_scope.is_in_scope` returns ``False`` for its docs-relative
path - that is, navigation indexes, KQL packs (``troubleshooting/kql/``),
lab guides (``troubleshooting/lab-guides/``), tutorials
(``language-guides/``), reference look-ups (``docs/reference/``), and any other
section outside ``SCANNED_SECTIONS``.

This script:

1. Walks ``docs/`` and selects files whose path is out-of-scope.
2. Surgically strips the ``content_validation:`` block from frontmatter using
   the same anchored regex as :mod:`remove_tautological_validation` so that
   all other keys, ordering, and quoting are preserved.

The scope policy lives in :mod:`lib.content_scope`; this script is the
canonical tool for one-time cleanup of legacy out-of-scope
``content_validation`` blocks that pre-date the scope policy (the "follow-up
editorial pass" noted in ``AGENTS.md`` §Text Content Validation).

Usage:
    python3 scripts/remove_out_of_scope_validation.py             # dry-run
    python3 scripts/remove_out_of_scope_validation.py --apply     # write
    python3 scripts/remove_out_of_scope_validation.py --apply --quiet
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.content_scope import is_in_scope  # noqa: E402

# Regex shared semantics with ``remove_tautological_validation``: anchored to a
# top-level ``content_validation:`` key and consumes its indented YAML body
# until the next top-level key. Duplicated literally (not imported) so each
# script remains self-contained and easy to audit in isolation.
CONTENT_VALIDATION_BLOCK = re.compile(
    r"^content_validation:[ \t]*\n"
    r"(?:[ \t]+[^\n]*\n|[ \t]*\n)*",
    re.MULTILINE,
)

FRONTMATTER_DELIMITER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Return ``(yaml_text, body)`` or ``(None, text)`` if no frontmatter."""
    match = FRONTMATTER_DELIMITER.match(text)
    if not match:
        return None, text
    return match.group(1), text[match.end() :]


def remove_content_validation(text: str) -> tuple[str, int]:
    """Strip the ``content_validation`` block from frontmatter.

    Returns ``(new_text, n)`` where ``n`` is the number of blocks removed
    (0 means the file was already clean and is returned unchanged).
    """
    yaml_text, body = split_frontmatter(text)
    if yaml_text is None:
        return text, 0

    if not yaml_text.endswith("\n"):
        yaml_text = yaml_text + "\n"

    new_yaml, n = CONTENT_VALIDATION_BLOCK.subn("", yaml_text)
    if n == 0:
        return text, 0

    return f"---\n{new_yaml}---\n" + body, n


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

    removed: list[Path] = []
    scanned = 0

    for md_file in sorted(docs_dir.rglob("*.md")):
        scanned += 1
        rel = md_file.relative_to(docs_dir)
        if is_in_scope(rel):
            continue

        text = md_file.read_text(encoding="utf-8")
        yaml_text, _ = split_frontmatter(text)
        if yaml_text is None or "content_validation:" not in yaml_text:
            continue

        new_text, n = remove_content_validation(text)
        if n == 0:
            if not args.quiet:
                print(f"  SKIP   {rel}  [regex did not match - manual review]")
            continue

        if args.apply:
            md_file.write_text(new_text, encoding="utf-8")
            if not args.quiet:
                print(f"  REMOVE {rel}")
        else:
            if not args.quiet:
                print(f"  WOULD  {rel}")

        removed.append(md_file)

    print("")
    print("Summary:")
    print(f"  Files scanned: {scanned}")
    print(f"  Out-of-scope content_validation blocks removed: {len(removed)}")
    if not args.apply and removed:
        print("")
        print("Dry-run only. Re-run with --apply to write changes.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
