#!/usr/bin/env python3
"""Validate that Azure CLI code fences have nearby explanation tables."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


AZ_PATTERN = re.compile(r"(^|[^A-Za-z0-9_-])az\s+[A-Za-z0-9_-]")
FENCE_PATTERN = re.compile(r"^(\s*)```")

_HOUSE_FIRST_CELLS = {
    "flag",
    "parameter",
    "code",
    "setting",
    "tool",
    "variable",
    "key",
    "key flags",
}


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    message: str


def has_az_command(block: list[str]) -> bool:
    return any(AZ_PATTERN.search(line) for line in block)


def fence_language(line: str) -> str:
    """Return the language token from a fence opener like '```bash {.copy}'.

    Handles fences of arbitrary length (```, ````, `````, ...) by
    stripping all leading backticks before parsing the language token.
    Returns an empty string for closing fences or unlabeled fences.

    >>> fence_language("```bash")
    'bash'
    >>> fence_language("```bash {.copy}")
    'bash'
    >>> fence_language("    ```python")
    'python'
    >>> fence_language("````bash")
    'bash'
    >>> fence_language("`````bash")
    'bash'
    >>> fence_language("```")
    ''
    >>> fence_language("````")
    ''
    """
    info = line.strip().lstrip("`").strip()
    return info.split(maxsplit=1)[0] if info else ""


def has_following_table(lines: list[str], start_index: int) -> bool:
    """Return True when a Markdown table appears shortly after a fence."""
    checked = 0
    i = start_index
    while i < len(lines) and checked < 8:
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            checked += 1
            continue
        if stripped.startswith(("!!!", "???", "##", "```")):
            return False
        if stripped.startswith("|") and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            return next_line.startswith("|") and "---" in next_line
        i += 1
        checked += 1
    return False


def _table_cells(line: str) -> list[str]:
    """Split a Markdown table row into trimmed, lower-cased cell values.

    Leading and trailing pipes produce empty edge cells, which are dropped.

    >>> _table_cells("| Command | Purpose |")
    ['command', 'purpose']
    >>> _table_cells("| Command/Parameter | Purpose |")
    ['command/parameter', 'purpose']
    >>> _table_cells("| Key flags |")
    ['key flags']
    """
    return [cell.strip().lower() for cell in line.strip().strip("|").split("|")]


def _is_house_table_header(cells: list[str]) -> bool:
    """Return True for an explanation-table header row.

    Recognition is header-agnostic across the series' repository-local
    conventions: any first cell beginning with ``command`` (covering
    ``Command``, ``Command/Parameter``, ``Command/Code``, ``Command/Flag``,
    ``Command part``, ``Command flag``, ``Command or Query``) or one of the
    known callout headers (``Flag``, ``Parameter``, ``Code``, ``Setting``,
    ``Tool``, ``Variable``, ``Key``, ``Key flags``). Column count is not
    constrained, so three-column variants such as ``Command | Purpose | Key
    flags`` and single-column ``Key flags`` callouts are both covered.

    >>> _is_house_table_header(["command", "purpose"])
    True
    >>> _is_house_table_header(["command/parameter", "purpose"])
    True
    >>> _is_house_table_header(["command", "why it is used"])
    True
    >>> _is_house_table_header(["command", "purpose", "key flags"])
    True
    >>> _is_house_table_header(["flag", "description"])
    True
    >>> _is_house_table_header(["key flags"])
    True
    >>> _is_house_table_header(["name", "value"])
    False
    """
    if not cells:
        return False
    first = cells[0]
    return first.startswith("command") or first in _HOUSE_FIRST_CELLS


def find_unterminated_tables(lines: list[str]) -> list[int]:
    """Return the 1-based line numbers where an explanation table is immediately
    followed by a non-blank line.

    python-markdown's ``tables`` extension treats the first non-blank line after
    a table as another table row (a phantom ``<td>...</td>`` cell) unless a blank
    line terminates the table. Fenced code regions are tracked so that pipe-led
    lines inside ```` ```kusto ```` blocks (``| where``, ``| summarize``) are not
    mistaken for table rows.

    >>> ok = ["| Command | Purpose |", "| --- | --- |", "| `az x` | y |", "", "next"]
    >>> find_unterminated_tables(ok)
    []
    >>> bad = ["| Command | Purpose |", "| --- | --- |", "| `az x` | y |", "Example output:"]
    >>> find_unterminated_tables(bad)
    [4]
    >>> variant = ["| Command/Parameter | Purpose |", "| --- | --- |", "| `az x` | y |", "prose"]
    >>> find_unterminated_tables(variant)
    [4]
    >>> why = ["| Command | Why it is used |", "| --- | --- |", "| `az x` | y |", "prose"]
    >>> find_unterminated_tables(why)
    [4]
    >>> eof = ["| Command | Purpose |", "| --- | --- |", "| `az x` | y |"]
    >>> find_unterminated_tables(eof)
    []
    >>> kql = ["```kusto", "AzureActivity", "| where x == 1", "```", "prose"]
    >>> find_unterminated_tables(kql)
    []
    """
    hits: list[int] = []
    i = 0
    n = len(lines)
    in_fence = False
    while i < n:
        if FENCE_PATTERN.match(lines[i]):
            in_fence = not in_fence
            i += 1
            continue
        if (
            not in_fence
            and lines[i].lstrip().startswith("|")
            and _is_house_table_header(_table_cells(lines[i]))
        ):
            j = i
            while j < n and lines[j].lstrip().startswith("|"):
                j += 1
            if j < n and lines[j].strip() != "":
                hits.append(j + 1)
            i = j
            continue
        i += 1
    return hits


def validate_file(path: Path) -> list[Finding]:
    lines = path.read_text(encoding="utf-8").splitlines()
    findings: list[Finding] = []
    for line_no in find_unterminated_tables(lines):
        findings.append(
            Finding(
                path=path,
                line=line_no,
                message="Explanation table must be followed by a blank line "
                "(otherwise the next line is absorbed as a phantom table row).",
            )
        )
    in_fence = False
    fence_indent = ""
    block_start = 0
    block_lines: list[str] = []

    for index, line in enumerate(lines):
        fence = FENCE_PATTERN.match(line)
        if not in_fence and fence:
            # Only track ```bash fences. Other languages (mermaid, text, json,
            # kusto, etc.) may legitimately contain `az ...` text in diagram
            # labels or console-output transcripts, and do not need an
            # explanation table per AGENTS.md ("Shell: Use bash for all CLI
            # examples").
            if fence_language(line) != "bash":
                continue
            in_fence = True
            fence_indent = fence.group(1)
            block_start = index + 1
            block_lines = []
            continue

        if in_fence and fence and len(fence.group(1)) <= len(fence_indent):
            if has_az_command(block_lines) and not has_following_table(
                lines, index + 1
            ):
                findings.append(
                    Finding(
                        path=path,
                        line=block_start,
                        message="Azure CLI code fence must be followed by a "
                        "command explanation table.",
                    )
                )
            in_fence = False
            fence_indent = ""
            block_lines = []
            continue

        if in_fence:
            block_lines.append(line)

    return findings


def validate_docs(docs_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(docs_dir.glob("**/*.md")):
        findings.extend(validate_file(path))
    return findings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs-dir", type=Path, default=Path("docs"))
    args = parser.parse_args()

    findings = validate_docs(args.docs_dir)
    if findings:
        for finding in findings:
            print(f"{finding.path}:{finding.line}: {finding.message}")
        raise SystemExit(
            f"{len(findings)} Azure CLI code fence(s) need explanation tables."
        )

    print("All Azure CLI code fences have following explanation tables.")


if __name__ == "__main__":
    main()
