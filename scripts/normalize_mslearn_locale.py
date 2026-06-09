#!/usr/bin/env python3
"""Normalize Microsoft Learn URLs to use the ``en-us`` locale prefix.

Microsoft Learn URLs accept any locale prefix (``en-us``, ``ja-jp``, ``ko-kr``)
and ALSO accept a locale-free form that redirects to the visitor's
geo-detected locale. This produces three problems:

1. **Inconsistency.** The same article links to multiple URL shapes across
   pages, which leaks into search indexes and confuses readers.
2. **Implicit geo-redirect.** Locale-free URLs serve different content per
   reader location, so screenshots, anchors, and quoted excerpts drift.
3. **Reviewer cognitive load.** Mixed forms force reviewers to mentally
   normalize URLs when comparing sources.

This script enforces a single canonical form: every ``learn.microsoft.com``
URL MUST include the ``en-us`` locale prefix.

The script:

1. Walks the project tree (defaulting to the repo root) with an explicit
   file-type allowlist.
2. Rewrites every Microsoft Learn URL to use the ``en-us`` locale prefix:

   - URLs whose first path segment is a generic doc-tree name (such as
     ``azure/`` or ``cli/``) get ``en-us/`` inserted between the hostname
     and the segment.
   - URLs whose first path segment is any non-``en-us`` locale (such as
     ``ja-jp/``, ``zh-Hans/``, or ``en-US/``) have the locale segment
     replaced with ``en-us/``.
   - URLs whose first path segment is a known non-locale root (the Learn
     catalog API root ``api/``) are left unchanged so we do not produce
     a 404.

3. Writes back when the result differs.

Modes:

- ``--check`` (default): exit code 1 if any file would change. Suitable
  for CI and pre-commit hooks.
- ``--apply``: write changes to disk.

This script preserves the repo invariant of **UTF-8 without BOM, LF line
endings**. Files outside that invariant are handled defensively: BOM is
preserved byte-for-byte when no rewrite is needed; CRLF files would be
re-encoded as LF on ``--apply`` (no CRLF files exist in this repo today).
Binary files are detected via UTF-8 decode failure and skipped.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# Capture the first path segment after the ``learn.microsoft.com/`` hostname
# so a per-match function can decide whether to insert, replace, or leave
# the locale alone. A naive "insert en-us unless an xx-xx/ locale is already
# present" regex corrupts four real-world URL shapes:
#   1. The Learn catalog API root segment ``api/`` (no locale exists; would 404)
#   2. Title-Case locale variants such as ``en-US/`` (old AGENTS.md guidance)
#   3. Script-tag locale variants such as ``zh-Hans/`` (valid Learn locale)
#   4. Non-Learn hosts whose name ends in ``learn.microsoft.com`` because of a
#      substring (``mylearn.microsoft.com``), a hyphenated prefix
#      (``my-learn.microsoft.com``), or a subdomain
#      (``foo.learn.microsoft.com``). A leading ``\b`` is NOT sufficient
#      because ``-`` and ``.`` are non-word characters and produce a word
#      boundary before ``l``. The negative lookbehind ``(?<![\w.-])`` rejects
#      every hostname-valid character (letters, digits, underscore, dot,
#      hyphen) so only a non-hostname separator (``/``, ``(``, ``"``,
#      whitespace, start-of-string, etc.) is allowed immediately before
#      ``learn``.
LEARN_URL_RE = re.compile(
    r"(?<![\w.-])learn\.microsoft\.com/(?P<seg>[A-Za-z]+(?:-[A-Za-z]+)?)/"
)

# Lowercase two-letter language-region form currently used by Learn article
# locales (``en-us``, ``ja-jp``, ``ko-kr``), broadened to also recognize
# Title-Case script tags (``zh-Hans``, ``zh-Hant``) and mixed case (``en-US``)
# that historical pasted URLs may still carry.
LOCALE_SHAPE_RE = re.compile(r"^[A-Za-z]{2,3}-[A-Za-z]{2,4}$")

# Path segments that legitimately appear immediately after the hostname
# WITHOUT a locale prefix. The Learn catalog API root segment ``api/``
# returns 404 if a locale is prepended.
NON_LOCALE_ROOTS = frozenset({"api"})

CANONICAL_LOCALE = "en-us"


def _normalize_match(match: re.Match) -> str:
    seg = match.group("seg")
    if seg == CANONICAL_LOCALE:
        return match.group(0)
    if LOCALE_SHAPE_RE.match(seg):
        return f"learn.microsoft.com/{CANONICAL_LOCALE}/"
    if seg.lower() in NON_LOCALE_ROOTS:
        return match.group(0)
    return f"learn.microsoft.com/{CANONICAL_LOCALE}/{seg}/"


def normalize_text(text: str) -> tuple[str, int]:
    """Return ``(new_text, replacements_made)``.

    ``replacements_made`` counts ACTUAL URL changes, not regex matches.
    A match where ``_normalize_match`` returns the original text (e.g.
    already-canonical ``en-us`` URL or a ``/api/`` root) does NOT count.
    Callers rely on a zero count meaning "no rewrite needed" so they can
    skip writing the file back to disk.
    """
    changes = 0

    def _wrapped(match: re.Match) -> str:
        nonlocal changes
        original = match.group(0)
        replacement = _normalize_match(match)
        if replacement != original:
            changes += 1
        return replacement

    new_text, _matches = LEARN_URL_RE.subn(_wrapped, text)
    return new_text, changes


EXTENSIONS = frozenset(
    {".md", ".py", ".yml", ".yaml", ".json", ".bicep", ".tf", ".txt"}
)
SPECIAL_FILES = frozenset({"Dockerfile", "sshd_config", "AGENTS.md"})

SKIP_DIRS = frozenset(
    {
        ".git",
        ".playwright-mcp",
        "node_modules",
        "site",
        "__pycache__",
        ".venv",
        "venv",
        ".pytest_cache",
        ".mypy_cache",
        "dist",
        "build",
        ".tox",
    }
)


def is_scannable(path: Path) -> bool:
    if not path.is_file():
        return False
    if set(path.parts) & SKIP_DIRS:
        return False
    if path.suffix in EXTENSIONS:
        return True
    if path.name in SPECIAL_FILES:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scan-root",
        type=Path,
        default=Path("."),
        help=(
            "Path to scan (default: repo root). MUST be inside the project "
            "root; absolute paths or ``..`` traversal that escape the project "
            "are rejected."
        ),
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
    scan_root = (project_root / args.scan_root).resolve()
    try:
        scan_root.relative_to(project_root)
    except ValueError:
        print(
            f"Error: --scan-root must be inside the project root "
            f"({project_root}); refusing to scan {scan_root}",
            file=sys.stderr,
        )
        return 1
    if not scan_root.exists():
        print(f"Error: scan root not found: {scan_root}", file=sys.stderr)
        return 1

    changed: list[Path] = []
    skipped_binary: list[Path] = []
    scanned = 0
    total_replacements = 0

    # os.walk + in-place dir mutation prunes descent into SKIP_DIRS. Switching
    # to ``Path.rglob`` with a post-filter would still descend into ``.git``,
    # ``node_modules``, and ``site`` (tens of thousands of generated files),
    # making scans significantly slower because the walk visits every entry
    # before the filter can reject it.
    for current_dir, dirs, files in os.walk(scan_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in sorted(files):
            path = Path(current_dir) / filename
            if not is_scannable(path):
                continue
            scanned += 1
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                skipped_binary.append(path)
                continue
            except PermissionError as exc:
                print(f"  WARN  {path}  [{exc}]", file=sys.stderr)
                continue

            new_text, count = normalize_text(text)
            if count == 0:
                continue

            changed.append(path)
            total_replacements += count
            try:
                rel = path.relative_to(project_root)
            except ValueError:
                rel = path
            if args.apply:
                path.write_text(new_text, encoding="utf-8")
                if not args.quiet:
                    print(f"  FIXED  {rel}  ({count} URL{'s' if count != 1 else ''})")
            else:
                if not args.quiet:
                    print(f"  DRIFT  {rel}  ({count} URL{'s' if count != 1 else ''})")

    print("")
    print("Summary:")
    print(f"  Files scanned: {scanned}")
    print(f"  Files with locale drift: {len(changed)}")
    print(f"  Total URLs needing en-us prefix: {total_replacements}")
    if skipped_binary and not args.quiet:
        print(f"  Skipped (binary/non-UTF-8): {len(skipped_binary)}")

    if changed and not args.apply:
        print("")
        print(
            "Drift detected. Run "
            "`python3 scripts/normalize_mslearn_locale.py --apply` "
            "to fix."
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
