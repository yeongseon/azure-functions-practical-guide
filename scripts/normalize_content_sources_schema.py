#!/usr/bin/env python3
"""Normalize ``content_sources`` frontmatter to the canonical dict shape.

The repository's content-sources schema has accumulated three historical
shapes that all describe the same concept (a list of source references
attached to a Markdown page):

1. **List-form** -- ``content_sources: [{type, url}, ...]``.
   Used by older generators that did not distinguish reference-level and
   diagram-level provenance.

2. **Dict-form with alias keys** -- ``content_sources: {sources|text|documents: [...]}``,
   optionally with a sibling ``diagrams:`` list.
   Different generators introduced different key names for the same idea.

3. **Canonical dict-form** -- ``content_sources: {references: [...], diagrams: [...]}``.
   The target shape. ``references`` is the agreed canonical key for the
   reference list (see PR 2d.2b sequence); ``diagrams`` carries
   per-diagram provenance and is left untouched here because it already
   uses a single canonical key.

This script rewrites shapes 1 and 2 into shape 3 while preserving every
other key in ``content_sources`` and the rest of the frontmatter byte-for-byte
(modulo the canonical YAML style applied by :mod:`lib.yaml_style`). It is
the data-migration counterpart to :mod:`validate_mslearn_urls`'s defensive
reader: the reader accepts every legacy shape so consumers keep working
during migration; this script converges the data so consumers can later
be tightened to require shape 3 only.

Modes:

- ``--check`` (default): exit 1 if any file would change. Suitable for CI
  and pre-commit hooks.
- ``--apply``: write changes to disk.

Scope flags:

- ``--docs-dir <path>``: which directory to walk (default ``docs``).
- ``--paths-glob <pattern>``: relative glob applied under ``--docs-dir``
  to scope per-section migration (default ``**/*.md``). Example:
  ``--paths-glob 'platform/**/*.md'`` migrates only the platform section.

The script preserves the markdown body verbatim for the current repo
invariant of **UTF-8 without BOM, LF line endings** (same invariant as
:mod:`normalize_yaml_frontmatter`). Files without frontmatter or without
a ``content_sources`` key are skipped silently.

Limitation: any YAML inline comments attached to a renamed alias key
(``sources:``, ``text:``, ``documents:``) are lost during the rename
because the rename is implemented by rebuilding the mapping rather than
mutating it in place. ``content_sources`` blocks in this repo carry
structured metadata with no inline comments, so this is acceptable; if
that ever changes, the rename loop must be reworked to copy comment
attributes from the source key onto the new ``references`` key.

Validator compatibility note: ``validate_content_sources`` historically
allows the legacy list-form ``content_sources: [...]`` on pages that
contain Mermaid blocks but lack per-diagram metadata, treating the
absent ``diagrams`` key as a legacy-permissive case. After migration
those pages become ``content_sources: {references: [...]}`` -- the same
information in canonical shape, but the validator no longer recognizes
the legacy-permissive case because the shape is now a dict. Running
``--apply`` across the entire repo can therefore surface previously
silent validation errors on pages where ``content_sources`` carries
document-level references only. Coordinate the migration with either
(a) a validator update that treats references-only dict-form as
legacy-equivalent, or (b) backfilling per-diagram metadata on the
affected pages before running ``--apply`` on them. The ``--paths-glob``
flag exists to scope migration to safe sections so this coordination
work can be staged.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.yaml_style import build_yaml, dump_frontmatter  # noqa: E402

from ruamel.yaml.comments import CommentedMap  # noqa: E402

# Legacy alias keys that are folded into the canonical ``references`` key.
# Order matters only for documentation: every alias is treated identically.
ALIAS_KEYS: Tuple[str, ...] = ("sources", "text", "documents")
CANONICAL_KEY: str = "references"

# Matches a frontmatter delimiter pair. Same regex as
# ``normalize_yaml_frontmatter.FRONTMATTER`` -- uses ``[ \t]*`` (horizontal
# whitespace only) so the blank line that conventionally follows the closing
# ``---`` is not eaten by a greedy ``\s*``.
FRONTMATTER = re.compile(r"^---[ \t]*\n(.*?)\n---[ \t]*\n", re.DOTALL)


def transform_content_sources(cs):
    """Return ``(new_cs, changed)`` for a single ``content_sources`` value.

    The transformation rules are:

    1. ``None`` -> unchanged. A bare ``content_sources:`` line with no
       value is treated as "not set" and left alone.
    2. List value -> wrap in ``{references: <list>}`` (transformation A).
    3. Dict value containing any of ``ALIAS_KEYS`` -> rebuild the dict
       so every alias key is folded into a single ``references`` key
       (transformation B). The first encountered alias / canonical key
       defines the position of ``references`` in the output, preserving
       the original visual order of "references first, diagrams last"
       when that was the input layout.
    4. Dict value with no alias keys -> unchanged (already canonical or
       diagrams-only).
    5. Any other scalar value -> unchanged. The validator will reject it
       separately; this tool only touches recognized shapes.

    Multi-alias inputs (e.g. both ``sources`` and ``text`` present, or
    ``references`` already alongside an alias) are theoretical given the
    current data audit, but the implementation merges every reference
    list into a single ``references`` list so the tool is forward-safe
    if such files appear later.

    >>> transform_content_sources(None)
    (None, False)

    List-form -> wrapped in a single-key references dict:

    >>> result, changed = transform_content_sources([{'url': 'a'}, {'url': 'b'}])
    >>> changed
    True
    >>> list(result.keys())
    ['references']
    >>> [item['url'] for item in result['references']]
    ['a', 'b']

    Diagrams-only dict is already canonical:

    >>> transform_content_sources({'diagrams': [{'id': 'foo'}]})[1]
    False

    Already-canonical references-only dict is unchanged:

    >>> transform_content_sources({'references': [{'url': 'a'}]})[1]
    False

    Single alias key -> renamed to references:

    >>> result, changed = transform_content_sources({'sources': [{'url': 'a'}]})
    >>> changed
    True
    >>> list(result.keys())
    ['references']
    >>> [item['url'] for item in result['references']]
    ['a']

    Alias key with sibling diagrams -> order preserved (references first):

    >>> result, changed = transform_content_sources(
    ...     {'text': [{'url': 'a'}], 'diagrams': [{'id': 'foo'}]}
    ... )
    >>> changed
    True
    >>> list(result.keys())
    ['references', 'diagrams']

    Alias coexisting with existing references key -> merged in order:

    >>> result, changed = transform_content_sources(
    ...     {'references': [{'url': 'a'}], 'sources': [{'url': 'b'}]}
    ... )
    >>> changed
    True
    >>> [item['url'] for item in result['references']]
    ['a', 'b']

    Empty list is wrapped (consistency with non-empty list case):

    >>> result, changed = transform_content_sources([])
    >>> changed
    True
    >>> list(result.keys())
    ['references']
    >>> result['references']
    []

    Empty dict is left alone (no alias keys -> nothing to migrate):

    >>> transform_content_sources({})[1]
    False

    Scalar values are passed through untouched:

    >>> transform_content_sources('not a structured value')
    ('not a structured value', False)
    """
    if cs is None:
        return cs, False

    # Transformation A: list-form -> {references: [...]}.
    # ``list(cs)`` produces a plain Python list with the original CommentedMap
    # items inside, dropping the outer ``CommentedSeq``'s parsed position /
    # indentation hints. Reusing the original ``CommentedSeq`` here causes
    # ``ruamel.yaml`` to retain the hints and emit ``references:   -`` on a
    # single line (the dump tries to position the first item relative to the
    # *original* parent key column, which is no longer correct under the new
    # ``references:`` parent). The inner item formatting is unaffected because
    # each item is its own ``CommentedMap`` with its own (correct) hints.
    if isinstance(cs, list):
        new_cs = CommentedMap()
        new_cs[CANONICAL_KEY] = list(cs)
        return new_cs, True

    # Transformation B: dict-form with alias keys -> rebuilt dict.
    # Use ``isinstance(cs, dict)`` so plain dicts (test inputs) and
    # ruamel ``CommentedMap`` instances (real frontmatter) both match.
    if isinstance(cs, dict):
        has_alias = any(k in cs for k in ALIAS_KEYS)
        if not has_alias:
            return cs, False

        new_cs = CommentedMap()
        merged_refs = None  # populated lazily on first reference-bearing key

        for key, value in cs.items():
            if key == CANONICAL_KEY or key in ALIAS_KEYS:
                # Treat every reference-bearing key uniformly. A non-list
                # value is wrapped in a single-item list so the merge logic
                # has uniform input; this preserves data that would
                # otherwise be silently dropped.
                items = list(value) if isinstance(value, list) else [value]
                if merged_refs is None:
                    merged_refs = items
                    new_cs[CANONICAL_KEY] = merged_refs
                else:
                    merged_refs.extend(items)
            else:
                new_cs[key] = value

        return new_cs, True

    # Unrecognized scalar shape -> leave for the validator to flag.
    return cs, False


def normalize_text(text: str) -> Tuple[str, bool]:
    """Return ``(new_text, changed)`` for a single Markdown file's text.

    ``changed`` is False when the file has no frontmatter, no
    ``content_sources`` key, or the value is already canonical, so callers
    can detect drift without comparing strings themselves. When ``changed``
    is True the entire frontmatter is re-dumped through
    :func:`lib.yaml_style.dump_frontmatter` so the output remains
    byte-stable across runs and across tools.

    End-to-end round-trip test for the list-form transformation. This test
    is critical: the ``transform_content_sources`` doctests verify in-memory
    structure but cannot catch YAML serialization bugs caused by parsed
    ``CommentedSeq`` instances retaining stale position hints. Without this
    test the regression that produces ``references:   -`` on a single line
    would slip through.

    >>> text = (
    ...     '---\\n'
    ...     'content_sources:\\n'
    ...     '  - type: mslearn-adapted\\n'
    ...     '    url: https://example.com/a\\n'
    ...     '  - type: mslearn-adapted\\n'
    ...     '    url: https://example.com/b\\n'
    ...     '---\\n'
    ...     '# body\\n'
    ... )
    >>> new_text, changed = normalize_text(text)
    >>> changed
    True
    >>> '  references:\\n    - type: mslearn-adapted' in new_text
    True
    >>> 'references:   -' in new_text
    False
    >>> new_text.endswith('# body\\n')
    True

    Files with no frontmatter pass through unchanged:

    >>> normalize_text('# just a body\\n')
    ('# just a body\\n', False)

    Files with frontmatter but no ``content_sources`` pass through unchanged:

    >>> text = '---\\ntitle: foo\\n---\\nbody\\n'
    >>> normalize_text(text)
    ('---\\ntitle: foo\\n---\\nbody\\n', False)
    """
    match = FRONTMATTER.match(text)
    if not match:
        return text, False

    yaml_text = match.group(1)
    body = text[match.end() :]

    data = build_yaml().load(yaml_text)
    if data is None:
        return text, False

    # Defensive: only top-level mappings can carry ``content_sources``.
    # A list-form frontmatter (very rare, but possible if someone hand-edits
    # YAML) has no concept of keyed fields and is skipped.
    if not isinstance(data, dict) or "content_sources" not in data:
        return text, False

    new_cs, changed = transform_content_sources(data["content_sources"])
    if not changed:
        return text, False

    data["content_sources"] = new_cs
    new_yaml = dump_frontmatter(data)
    new_text = f"---\n{new_yaml}---\n" + body
    return new_text, True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("docs"),
        help="Path to docs directory (default: docs)",
    )
    parser.add_argument(
        "--paths-glob",
        default="**/*.md",
        help=(
            "Glob pattern relative to --docs-dir (default: '**/*.md'). "
            "Use to scope per-section migration, e.g. 'platform/**/*.md'."
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

    # Sorted iteration so output is deterministic across runs and CI logs
    # can be diffed meaningfully when the set of changed files changes.
    for md_file in sorted(docs_dir.glob(args.paths_glob)):
        if not md_file.is_file() or md_file.suffix != ".md":
            continue
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
    print(f"  Files with content_sources schema drift: {len(changed)}")
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
            "`python3 scripts/normalize_content_sources_schema.py --apply` "
            "to fix."
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
