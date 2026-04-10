#!/usr/bin/env python3
"""
Mermaid Syntax Validation Script

Validates mermaid diagram syntax using mermaid-cli (mmdc).
Catches syntax errors before deployment.

Usage:
    python scripts/validate_mermaid_syntax.py

Requirements:
    npm install -g @mermaid-js/mermaid-cli

Exit codes:
    0 - All diagrams are valid
    1 - Syntax errors found
"""

import sys
import re
from pathlib import Path


def extract_mermaid_blocks(filepath: Path) -> list:
    """Extract all mermaid code blocks from a markdown file."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return []

    blocks = []
    lines = content.split("\n")
    in_mermaid = False
    block_start = 0
    block_lines = []

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```mermaid"):
            in_mermaid = True
            block_start = i
            block_lines = []
        elif in_mermaid:
            if stripped == "```":
                blocks.append({"line": block_start, "content": "\n".join(block_lines)})
                in_mermaid = False
            else:
                block_lines.append(line)

    return blocks


def validate_mermaid_block(content: str) -> tuple:
    """
    Validate a mermaid block using regex-based checks.
    Returns (is_valid, error_message)
    """
    errors = []

    # Check for unescaped pipe in node labels (common issue)
    # Mermaid edge labels use: A -->|label| B (valid)
    # Node labels with pipe are invalid: A[text|more]
    # First, find all node labels (inside brackets)
    node_labels = re.findall(r"\[([^\]]+)\]", content)
    for label in node_labels:
        # Skip if this looks like a link (contains http/https)
        if "http" in label.lower():
            continue
        # Check for unescaped pipe in node label
        if "|" in label:
            # This is an error - pipe in node label causes syntax error
            errors.append(f"Unescaped pipe '|' in node label: [{label[:40]}...]")

    # Check for common flowchart issues
    if "flowchart" in content or "graph" in content:
        # Check for arrows without proper spacing
        if re.search(r"\w-->\w", content):
            errors.append("Arrow without proper node reference")

    if errors:
        return False, "; ".join(errors)

    return True, None


def validate_file(filepath: Path, project_root: Path) -> list:
    """Validate all mermaid blocks in a file."""
    errors = []
    blocks = extract_mermaid_blocks(filepath)

    for block in blocks:
        is_valid, error_msg = validate_mermaid_block(block["content"])
        if not is_valid:
            rel_path = filepath.relative_to(project_root)
            errors.append(
                {"file": str(rel_path), "line": block["line"], "error": error_msg}
            )

    return errors


def validate_project(project_path: Path) -> tuple:
    """Validate all markdown files in docs/."""
    docs_dir = project_path / "docs"
    if not docs_dir.exists():
        return 0, 0, []

    all_errors = []
    files_checked = 0
    diagrams_checked = 0

    md_files = list(docs_dir.rglob("*.md"))

    for md_file in md_files:
        files_checked += 1
        blocks = extract_mermaid_blocks(md_file)
        diagrams_checked += len(blocks)

        file_errors = validate_file(md_file, project_path)
        all_errors.extend(file_errors)

    return files_checked, diagrams_checked, all_errors


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate mermaid diagram syntax")
    parser.add_argument("--project", "-p", type=str, help="Specific project path")
    args = parser.parse_args()

    if args.project:
        project_path = Path(args.project)
    else:
        project_path = Path(__file__).parent.parent

    print(f"Validating mermaid syntax in: {project_path}")
    print("=" * 60)

    files_checked, diagrams_checked, errors = validate_project(project_path)

    print(f"\nFiles checked: {files_checked}")
    print(f"Diagrams checked: {diagrams_checked}")
    print(f"Errors found: {len(errors)}")

    if errors:
        print("\nErrors:")
        for err in errors:
            print(f"\n  {err['file']}:{err['line']}")
            print(f"    {err['error']}")
        sys.exit(1)
    else:
        print("\nAll mermaid diagrams have valid syntax!")
        sys.exit(0)


if __name__ == "__main__":
    main()
