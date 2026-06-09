#!/usr/bin/env python3
"""Normalize Markdown frontmatter to the canonical ``ruamel.yaml`` style.

PyYAML's ``yaml.dump()`` reformats frontmatter aggressively each time a tool
touches it (quoting dates, flattening nested sequences, folding multi-line
strings). This produces large noisy diffs and means style drifts whenever any
automation runs. This script:

1. Walks ``docs/**/*.md``.
2. Round-trips frontmatter through the shared :mod:`lib.yaml_style`
   configuration (block style, ``mapping=2 sequence=4 offset=2``,
   quotes preserved, width practically disabled).
3. Writes back when the result differs.

Modes:

- ``--check`` (default): exit code 1 if any file would change. Suitable for
  CI and pre-commit hooks.
- ``--apply``: write changes to disk.

The script preserves the markdown body verbatim for the current repo
invariant of **UTF-8 without BOM, LF line endings**. Files outside that
invariant are handled defensively rather than transparently:

- **BOM-prefixed files** are skipped silently because the leading
  ``\ufeff`` makes the frontmatter regex miss; the file is left untouched.
- **CRLF files** are read with Python's universal-newlines (``\r\n`` -> ``\n``)
  and would be written back as LF on ``--apply``, which is a body change.
  No CRLF files exist in this repo today; if that ever changes, document
  the line-ending policy first or extend this script to preserve the
  original line ending.

The repo invariant is documented in ``AGENTS.md`` Frontmatter YAML Style.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.yaml_style import build_yaml, dump_frontmatter  # noqa: E402

# Matches a frontmatter delimiter pair: ``---\n...\n---\n``. The body is
# captured separately so it is preserved byte-for-byte during normalization.
#
# Uses ``[ \t]*`` (horizontal whitespace only) rather than ``\s*`` because
# ``\s`` includes ``\n``: greedy ``\s*\n`` would swallow a blank line that
# follows the closing ``---``, silently deleting the conventional blank line
# between frontmatter and the first heading.
FRONTMATTER = re.compile(r"^---[ \t]*\n(.*?)\n---[ \t]*\n", re.DOTALL)


def normalize_text(text: str) -> tuple[str, bool]:
    """Return ``(new_text, changed)``.

    ``changed`` is False when the file has no frontmatter or when the
    round-trip produces byte-identical output, so callers can detect drift
    without comparing strings themselves.
    """
    match = FRONTMATTER.match(text)
    if not match:
        return text, False

    yaml_text = match.group(1)
    body = text[match.end() :]

    data = build_yaml().load(yaml_text)
    if data is None:
        return text, False

    new_yaml = dump_frontmatter(data)
    new_text = f"---\n{new_yaml}---\n" + body
    return new_text, new_text != text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("docs"),
        help="Path to docs directory (default: docs)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if any file would change (CI mode, default)",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="Write changes to disk",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-file output",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    docs_dir = (project_root / args.docs_dir).resolve()
    try:
        docs_dir.relative_to(project_root)
    except ValueError:
        print(
            f"Error: --docs-dir must be inside the project root "
            f"({project_root}); refusing to scan {docs_dir}",
            file=sys.stderr,
        )
        return 1
    if not docs_dir.exists():
        print(f"Error: docs directory not found: {docs_dir}", file=sys.stderr)
        return 1

    changed: list[Path] = []
    errors: list[tuple[Path, str]] = []
    scanned = 0

    for md_file in sorted(docs_dir.rglob("*.md")):
        scanned += 1
        text = md_file.read_text(encoding="utf-8")
        try:
            new_text, did_change = normalize_text(text)
        except Exception as exc:
            errors.append((md_file, str(exc)))
            if not args.quiet:
                rel = md_file.relative_to(project_root)
                print(f"  ERROR  {rel}  [{exc}]")
            continue

        if not did_change:
            continue

        changed.append(md_file)
        rel = md_file.relative_to(project_root)
        if args.apply:
            md_file.write_text(new_text, encoding="utf-8")
            if not args.quiet:
                print(f"  FIXED  {rel}")
        else:
            if not args.quiet:
                print(f"  DRIFT  {rel}")

    print("")
    print("Summary:")
    print(f"  Files scanned: {scanned}")
    print(f"  Files with style drift: {len(changed)}")
    print(f"  Parse errors: {len(errors)}")

    if errors:
        print("")
        print("Parse errors (require manual review):")
        for md_file, msg in errors:
            print(f"  - {md_file.relative_to(project_root)}: {msg}")
        return 1

    if changed and not args.apply:
        print("")
        print(
            "Drift detected. Run "
            "`python3 scripts/normalize_yaml_frontmatter.py --apply` "
            "to fix."
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
