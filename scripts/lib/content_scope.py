"""Shared scope policy for ``content_validation`` enforcement.

Defines which markdown files in ``docs/`` are required to carry the
``content_validation:`` frontmatter block (factual-claim pages) versus those
that are out of scope (navigation indexes, KQL packs, lab guides, tutorials,
reference look-ups, and other non-claim content).

Out-of-scope pages are not required to carry a ``content_validation`` block.
Legacy blocks may still exist on some out-of-scope pages from before this
scope policy was formalized; they are accepted, and a follow-up editorial
pass will remove them. New out-of-scope pages should not add the block.

Imported by:

- ``scripts/remove_out_of_scope_validation.py``

The dashboard generator (``scripts/generate_content_validation_status.py``)
still uses its legacy local ``SCAN_SECTIONS`` list and ``index.md`` skip
heuristic, so the current dashboard may still surface a few out-of-scope
pages (notably lab guides under ``troubleshooting/lab-guides/``). Migrating
the generator to ``is_in_scope`` is the strict-validator sync planned for a
follow-up PR; until then this module is the *authoritative* scope policy and
the dashboard's behavior is *aspirational*.

The policy MUST stay in sync with ``AGENTS.md`` §Text Content Validation.
If you change the rules here, update ``AGENTS.md`` in the same commit.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

SCANNED_SECTIONS: frozenset[str] = frozenset(
    {
        "platform",
        "best-practices",
        "operations",
        "troubleshooting",
    }
)

EXCLUDED_SUBPATHS: tuple[str, ...] = (
    "troubleshooting/kql/",
    "troubleshooting/lab-guides/",
)

NAVIGATION_INDEXES: frozenset[str] = frozenset(
    {
        "platform/index.md",
        "best-practices/index.md",
        "operations/index.md",
        "troubleshooting/index.md",
        "troubleshooting/first-10-minutes/index.md",
        "troubleshooting/playbooks/index.md",
    }
)

TAUTOLOGICAL_CLAIM_MARKER: str = "primary source basis"


def is_in_scope(rel_path: Union[Path, str]) -> bool:
    """Return ``True`` if ``rel_path`` requires a ``content_validation`` block.

    ``rel_path`` must be relative to ``docs/``. The policy is applied in this
    order:

    1. The first path component must be a ``SCANNED_SECTION``.
    2. The path must NOT start with any ``EXCLUDED_SUBPATHS`` prefix.
    3. The path must NOT be a ``NAVIGATION_INDEXES`` entry.

    Examples:

    >>> from pathlib import Path
    >>> is_in_scope("platform/scaling.md")
    True
    >>> is_in_scope("platform/architecture/index.md")  # factual subsection landing
    True
    >>> is_in_scope("platform/networking-scenarios/index.md")  # factual subsection landing
    True
    >>> is_in_scope("platform/index.md")  # navigation
    False
    >>> is_in_scope("troubleshooting/playbooks/high-latency.md")
    True
    >>> is_in_scope("troubleshooting/kql/scaling/index.md")  # excluded subpath
    False
    >>> is_in_scope("troubleshooting/lab-guides/cold-start.md")
    False
    >>> is_in_scope("language-guides/python/tutorial/01-deploy.md")  # outside sections
    False
    >>> is_in_scope("start-here/overview.md")  # outside sections
    False
    """
    rel = Path(rel_path)
    parts = rel.parts
    if not parts or parts[0] not in SCANNED_SECTIONS:
        return False

    posix = rel.as_posix()
    if any(posix.startswith(prefix) for prefix in EXCLUDED_SUBPATHS):
        return False

    if posix in NAVIGATION_INDEXES:
        return False

    return True


def is_tautological_text(text: object) -> bool:
    """Return ``True`` if ``text`` contains the tautological marker.

    The match is case-insensitive (uses :py:meth:`str.casefold`) so variants
    like ``"Primary Source Basis"`` or ``"PRIMARY SOURCE BASIS"`` are caught.
    Non-string inputs return ``False``.

    >>> is_tautological_text("uses Microsoft Learn as the primary source basis")
    True
    >>> is_tautological_text("PRIMARY SOURCE BASIS")
    True
    >>> is_tautological_text("Azure Functions supports Flex Consumption hosting")
    False
    >>> is_tautological_text(None)
    False
    """
    if not isinstance(text, str):
        return False
    return TAUTOLOGICAL_CLAIM_MARKER.casefold() in text.casefold()


__all__ = [
    "SCANNED_SECTIONS",
    "EXCLUDED_SUBPATHS",
    "NAVIGATION_INDEXES",
    "TAUTOLOGICAL_CLAIM_MARKER",
    "is_in_scope",
    "is_tautological_text",
]
