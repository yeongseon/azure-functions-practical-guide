#!/usr/bin/env python3
"""Backfill per-diagram provenance into ``content_sources.diagrams``.

Promotes Markdown pages from the legacy *references-only* ``content_sources``
shape to the canonical shape that carries one provenance entry per Mermaid
diagram:

    # BEFORE (legacy escape -- validator is lenient)
    content_sources:
      references:
        - type: mslearn-adapted
          url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale

    # AFTER (canonical -- validator strictly checks each diagram)
    content_sources:
      references:
        - type: mslearn-adapted
          url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
      diagrams:
        - id: scale-controller-fundamentals   # matches <!-- diagram-id: ... -->
          type: flowchart
          source: mslearn-adapted
          mslearn_url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale

Every Mermaid block in this repository already carries a matching
``<!-- diagram-id: X -->`` comment (enforced by the CI "diagram IDs" audit),
so this migration is **frontmatter-only**: it mirrors each existing diagram-id
into a ``diagrams:`` entry and never edits the Markdown body. The ``references``
list and every other frontmatter key are preserved; only the ``diagrams`` key
is added.

Two source-classification modes (see ``--mode``):

- ``mslearn-adapted`` (default): each diagram is ``source: mslearn-adapted``
  with ``mslearn_url`` set to the page's primary (first) reference URL. Adds no
  generated prose. Requires the page to have at least one reference URL.
- ``self-generated``: each diagram is ``source: self-generated`` with a
  ``justification`` derived from the diagram-id and ``based_on`` listing every
  reference URL on the page. Matches the shape of the repo's hand-authored
  canonical pages.

The field requirements per mode are dictated by
``scripts/validate_content_sources.py`` REQUIRED_FIELDS.

Modes:

- ``--check`` (default): exit 1 if any file would change (CI / preview).
- ``--apply``: write changes to disk.

Scope flags mirror ``normalize_content_sources_schema.py``:

- ``--docs-dir <path>``: directory to walk (default ``docs``).
- ``--paths-glob <pattern>``: relative glob under ``--docs-dir``
  (default ``**/*.md``), e.g. ``platform/**/*.md``.
- ``--limit <N>``: only act on the first N (sorted) eligible files -- used to
  stage a small sample before a full run.

YAML is emitted through :mod:`lib.yaml_style` so the output is byte-identical
to what ``normalize_yaml_frontmatter.py --check`` expects (no canonical-style
drift). The Markdown body is preserved verbatim (UTF-8, no BOM, LF).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.yaml_style import build_yaml, dump_frontmatter  # noqa: E402

from ruamel.yaml.comments import CommentedMap, CommentedSeq  # noqa: E402

FRONTMATTER = re.compile(r"^---[ \t]*\n(.*?)\n---[ \t]*\n", re.DOTALL)
DIAGRAM_ID_RE = re.compile(r"<!--\s*diagram-id:\s*([^\s>]+)\s*-->")

# Generated dashboards contain illustrative Mermaid blocks and are skipped by
# the validator; skip them here too.
SKIP_FILENAMES = {"content-validation-status.md", "validation-status.md"}

VALID_MODES = ("mslearn-adapted", "self-generated")


def find_mermaid_blocks(text: str) -> List[Tuple[int, str]]:
    """Return ``[(fence_line, mermaid_type), ...]`` in document order.

    ``mermaid_type`` is the first whitespace-delimited token on the first
    non-empty line inside the fence (e.g. ``flowchart``, ``sequenceDiagram``,
    ``graph``, ``gantt``). Fence detection mirrors
    ``validate_content_sources.find_mermaid_blocks`` (indentation-aware close).

    >>> find_mermaid_blocks("a\\n```mermaid\\nflowchart TD\\n  A-->B\\n```\\n")
    [(2, 'flowchart')]
    >>> find_mermaid_blocks("```mermaid\\nsequenceDiagram\\n```\\n")
    [(1, 'sequenceDiagram')]
    """
    blocks: List[Tuple[int, str]] = []
    lines = text.split("\n")
    in_block = False
    fence_indent = 0
    fence_line = 0
    dtype: Optional[str] = None

    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if not in_block:
            if stripped.startswith("```mermaid"):
                in_block = True
                fence_indent = indent
                fence_line = i
                dtype = None
        else:
            if stripped.startswith("```") and indent <= fence_indent:
                blocks.append((fence_line, dtype or "flowchart"))
                in_block = False
                continue
            if dtype is None and stripped:
                dtype = stripped.split()[0]

    return blocks


def find_diagram_id_comments(text: str) -> dict:
    """Return ``{line_number: diagram_id}`` for every diagram-id comment."""
    comments = {}
    for i, line in enumerate(text.split("\n"), 1):
        match = DIAGRAM_ID_RE.search(line)
        if match:
            comments[i] = match.group(1)
    return comments


def collect_page_diagrams(body: str) -> List[Tuple[Optional[str], str]]:
    """Pair each Mermaid block with its preceding diagram-id comment.

    Returns ``[(diagram_id, mermaid_type), ...]`` in document order. A
    ``diagram_id`` of ``None`` means the block has no diagram-id comment within
    the 3 preceding lines (the caller treats this as "needs manual review" and
    skips the whole page).
    """
    blocks = find_mermaid_blocks(body)
    comments = find_diagram_id_comments(body)
    result: List[Tuple[Optional[str], str]] = []
    for fence_line, dtype in blocks:
        did: Optional[str] = None
        for check_line in range(fence_line - 1, fence_line - 4, -1):
            if check_line in comments:
                did = comments[check_line]
                break
        result.append((did, dtype))
    return result


def page_reference_urls(content_sources) -> List[str]:
    """Extract the list of reference URLs from a ``content_sources`` value."""
    refs = None
    if isinstance(content_sources, dict):
        refs = content_sources.get("references")
    elif isinstance(content_sources, list):
        refs = content_sources
    if not isinstance(refs, list):
        return []
    urls = []
    for item in refs:
        if isinstance(item, dict) and item.get("url"):
            urls.append(item["url"])
    return urls


_SECTION_PREFIX = re.compile(r"^\d+(?:-\d+)*-")

# Type-specific justification lead-in plus the key noun that lead-in introduces.
# When the diagram-id already contains that noun (e.g. an ``...-flow`` id for a
# flowchart), the lead-in is dropped to avoid redundant phrasing like
# "Flow view of ... decision flow".
_TYPE_LEAD = {
    "flowchart": ("Flow view of", "flow"),
    "graph": ("Flow view of", "flow"),
    "sequenceDiagram": ("Interaction sequence for", "sequence"),
    "gantt": ("Timeline view of", "timeline"),
    "timeline": ("Timeline view of", "timeline"),
    "pie": ("Proportional breakdown of", "breakdown"),
    "stateDiagram": ("State model of", "state"),
    "stateDiagram-v2": ("State model of", "state"),
}


def _describe(diagram_id: str) -> str:
    """Humanize a diagram-id into a readable phrase.

    Strips a leading section-number prefix (e.g. ``3-6-``) that encodes document
    structure rather than diagram content, then converts the remaining slug to
    spaced words.

    >>> _describe("scale-controller-fundamentals")
    'scale controller fundamentals'
    >>> _describe("3-6-triage-decision-flow")
    'triage decision flow'
    """
    slug = _SECTION_PREFIX.sub("", diagram_id)
    label = slug.replace("-", " ").replace("_", " ").strip()
    return label or diagram_id


def _justification(diagram_id: str, dtype: str) -> str:
    """Build a type-aware, non-redundant self-generated justification.

    >>> _justification("scale-controller-fundamentals", "flowchart")
    'Flow view of scale controller fundamentals, synthesized from Microsoft Learn documentation cited on this page.'
    >>> _justification("autoscale-decision-flow", "flowchart")
    'Autoscale decision flow, synthesized from Microsoft Learn documentation cited on this page.'
    >>> _justification("evidence-timeline", "gantt")
    'Evidence timeline, synthesized from Microsoft Learn documentation cited on this page.'
    """
    desc = _describe(diagram_id)
    lead, keyword = _TYPE_LEAD.get(dtype, ("Diagram of", None))
    tail = "synthesized from Microsoft Learn documentation cited on this page."
    if keyword and keyword in desc.lower():
        phrase = desc[:1].upper() + desc[1:]
    else:
        phrase = f"{lead} {desc}"
    return f"{phrase}, {tail}"


def build_diagram_entry(diagram_id: str, dtype: str, ref_urls: List[str], mode: str):
    """Build one canonical ``diagrams`` entry as an ordered ``CommentedMap``."""
    entry = CommentedMap()
    entry["id"] = diagram_id
    entry["type"] = dtype
    if mode == "mslearn-adapted":
        entry["source"] = "mslearn-adapted"
        entry["mslearn_url"] = ref_urls[0]
    else:  # self-generated
        entry["source"] = "self-generated"
        entry["justification"] = _justification(diagram_id, dtype)
        if ref_urls:
            based_on = CommentedSeq()
            for url in ref_urls:
                based_on.append(url)
            entry["based_on"] = based_on
    return entry


def transform_text(text: str, mode: str) -> Tuple[str, bool, str]:
    """Return ``(new_text, changed, status)`` for one Markdown file's text.

    ``status`` is a short machine-readable reason string for reporting.
    """
    match = FRONTMATTER.match(text)
    if not match:
        return text, False, "no-frontmatter"
    yaml_text = match.group(1)
    body = text[match.end() :]

    if "```mermaid" not in body:
        return text, False, "no-mermaid"

    data = build_yaml().load(yaml_text)
    if not isinstance(data, dict) or "content_sources" not in data:
        return text, False, "no-content_sources"

    cs = data["content_sources"]
    if isinstance(cs, dict) and "diagrams" in cs:
        return text, False, "already-canonical"

    diagrams = collect_page_diagrams(body)
    if not diagrams:
        return text, False, "no-diagrams-found"
    if any(did is None for did, _ in diagrams):
        return text, False, "missing-diagram-id-comment"

    ref_urls = page_reference_urls(cs)
    if mode == "mslearn-adapted" and not ref_urls:
        return text, False, "no-reference-url"

    seq = CommentedSeq()
    for did, dtype in diagrams:
        seq.append(build_diagram_entry(did, dtype, ref_urls, mode))

    # Normalize a bare list-form content_sources into {references: [...]} so the
    # diagrams key has a canonical sibling. (No such pages exist today, but be
    # forward-safe.)
    if isinstance(cs, list):
        new_cs = CommentedMap()
        new_cs["references"] = list(cs)
        cs = new_cs
        data["content_sources"] = cs

    cs["diagrams"] = seq

    new_yaml = dump_frontmatter(data)
    new_text = f"---\n{new_yaml}---\n" + body
    return new_text, True, "migrated"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs-dir", type=Path, default=Path("docs"))
    parser.add_argument("--paths-glob", default="**/*.md")
    parser.add_argument(
        "--mode",
        choices=VALID_MODES,
        default="mslearn-adapted",
        help="Diagram source classification (default: mslearn-adapted)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Only act on the first N eligible files (0 = no limit)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--check", action="store_true", help="Exit 1 if any file would change"
    )
    group.add_argument("--apply", action="store_true", help="Write changes to disk")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    docs_dir = (project_root / args.docs_dir).resolve()
    try:
        docs_dir.relative_to(project_root)
    except ValueError:
        print(f"Error: --docs-dir must be inside {project_root}", file=sys.stderr)
        return 1
    if not docs_dir.exists():
        print(f"Error: docs directory not found: {docs_dir}", file=sys.stderr)
        return 1

    changed: List[Path] = []
    skipped: dict = {}
    errors: List[Tuple[Path, str]] = []
    scanned = 0

    for md_file in sorted(docs_dir.glob(args.paths_glob)):
        if not md_file.is_file() or md_file.suffix != ".md":
            continue
        if md_file.name in SKIP_FILENAMES:
            continue
        scanned += 1
        text = md_file.read_text(encoding="utf-8")
        try:
            new_text, did_change, status = transform_text(text, args.mode)
        except Exception as exc:  # noqa: BLE001
            errors.append((md_file, str(exc)))
            continue

        if not did_change:
            skipped[status] = skipped.get(status, 0) + 1
            continue

        rel = md_file.relative_to(project_root)
        changed.append(md_file)
        if args.apply:
            md_file.write_text(new_text, encoding="utf-8")
            if not args.quiet:
                print(f"  MIGRATED  {rel}")
        else:
            if not args.quiet:
                print(f"  WOULD-MIGRATE  {rel}")

        if args.limit and len(changed) >= args.limit:
            break

    print("")
    print("Summary:")
    print(f"  Mode: {args.mode}")
    print(f"  Files scanned: {scanned}")
    print(f"  Files migrated: {len(changed)}")
    if skipped:
        print("  Skipped (by reason):")
        for reason, count in sorted(skipped.items()):
            print(f"    - {reason}: {count}")
    print(f"  Errors: {len(errors)}")

    if errors:
        print("")
        print("Errors (require manual review):")
        for md_file, msg in errors:
            print(f"  - {md_file.relative_to(project_root)}: {msg}")
        return 1

    if changed and not args.apply:
        print("")
        print("Run with --apply to write these changes.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
