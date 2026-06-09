#!/usr/bin/env python3
"""Validate that Azure CLI code fences have nearby explanation tables."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


AZ_PATTERN = re.compile(r"(^|[^A-Za-z0-9_-])az\s+[A-Za-z0-9_-]")
FENCE_PATTERN = re.compile(r"^(\s*)```")


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


def validate_file(path: Path) -> list[Finding]:
    lines = path.read_text(encoding="utf-8").splitlines()
    findings: list[Finding] = []
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
                        message="Azure CLI code fence is missing a following explanation table.",
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
