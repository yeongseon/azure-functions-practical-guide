"""Canonical YAML serialization for documentation frontmatter.

Centralizes the ``ruamel.yaml.YAML`` configuration used by every script that
mutates Markdown frontmatter so the output is byte-stable across runs and
across tools. PyYAML's ``yaml.dump()`` aggressively quotes dates, flattens
nested sequences, and flows multi-line strings; routing all mutations through
this module prevents that drift.

Style rules (must stay in sync with ``AGENTS.md`` §Frontmatter YAML Style):

- Block style for mappings and sequences (no flow style).
- Indentation: ``mapping=2, sequence=4, offset=2`` -- each list item's hyphen
  is at column 2 and its content at column 4, matching the historical layout.
- Quoting: preserved from the source (``preserve_quotes=True``) so existing
  files are normalized for *structure* without rewriting quoted dates,
  intentionally-quoted strings, or block-scalar form.
- Line width: practically disabled (``width = 4096``) so long ``claim`` and
  ``summary`` strings stay on one line instead of folding.
- Explicit document end: disabled (``explicit_end = False``) -- frontmatter
  is delimited by ``---`` on its own, no ``...`` terminator.

Consumed by:

- ``scripts/normalize_yaml_frontmatter.py`` (bulk normalizer + CI check).
- Any future generator or mutation tool MUST import :func:`dump_frontmatter`
  (preferred, single-call) or :func:`build_yaml` (when you need to call
  ``load`` and ``dump`` on the same instance). Direct use of PyYAML's
  ``yaml.dump`` is banned.
"""

from __future__ import annotations

from io import StringIO

from ruamel.yaml import YAML

__all__ = ["build_yaml", "dump_frontmatter", "CANONICAL_INDENT"]

# Captured for documentation/tests; mirror in ``AGENTS.md`` if changed.
CANONICAL_INDENT: dict[str, int] = {
    "mapping": 2,
    "sequence": 4,
    "offset": 2,
}


def build_yaml() -> YAML:
    """Return a configured ``ruamel.yaml.YAML`` instance for frontmatter I/O.

    Each call returns a fresh instance because ``YAML`` carries mutable state
    (anchors, comments) across load/dump pairs; sharing one instance across
    files would leak that state and produce inconsistent output.
    """
    yaml = YAML(typ="rt")
    yaml.indent(**CANONICAL_INDENT)
    yaml.preserve_quotes = True
    yaml.width = 4096
    yaml.explicit_end = False
    return yaml


def dump_frontmatter(data: object, *, trailing_newline: bool = True) -> str:
    """Serialize ``data`` (a ruamel.yaml CommentedMap / dict) to canonical YAML.

    Returns the YAML body only -- the caller is responsible for wrapping it in
    the ``---`` / ``---`` frontmatter delimiters. The output always ends with
    a single newline when ``trailing_newline`` is true so callers can splice
    it cleanly between the closing ``---`` and the document body.
    """
    yaml = build_yaml()
    buffer = StringIO()
    yaml.dump(data, buffer)
    text = buffer.getvalue()
    if trailing_newline and not text.endswith("\n"):
        text = text + "\n"
    return text
