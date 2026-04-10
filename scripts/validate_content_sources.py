#!/usr/bin/env python3
"""
Content Sources Validation Script

Validates that all markdown files with mermaid diagrams have proper content_sources
metadata in their frontmatter.

Checks:
1. All mermaid blocks have preceding <!-- diagram-id: --> comments
2. All files with mermaid have content_sources in frontmatter
3. Each diagram in content_sources has required fields
4. Source types are valid (mslearn, mslearn-adapted, self-generated)
5. Self-generated diagrams have justification

Usage:
    python scripts/validate_content_sources.py [--verbose]

Exit codes:
    0 - All validations passed
    1 - Validation errors found
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("Error: PyYAML library required. Install with: pip install pyyaml")
    sys.exit(1)


# Valid source types
VALID_SOURCE_TYPES = {"mslearn", "mslearn-adapted", "self-generated"}

# Required fields for each source type
REQUIRED_FIELDS = {
    "mslearn": ["id", "type", "source", "mslearn_url"],
    "mslearn-adapted": ["id", "type", "source", "mslearn_url"],
    "self-generated": ["id", "type", "source", "justification"],
}


class ValidationError:
    def __init__(self, file: str, message: str, line: Optional[int] = None):
        self.file = file
        self.message = message
        self.line = line

    def __str__(self):
        if self.line:
            return f"{self.file}:{self.line}: {self.message}"
        return f"{self.file}: {self.message}"


def extract_frontmatter(content: str) -> Tuple[Optional[dict], int]:
    """
    Extract YAML frontmatter from markdown content.
    Returns (frontmatter_dict, end_line_number).
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None, 0

    frontmatter_text = match.group(1)
    end_line = frontmatter_text.count("\n") + 2  # +2 for the --- lines

    try:
        return yaml.safe_load(frontmatter_text), end_line
    except yaml.YAMLError as e:
        return None, 0


def find_mermaid_blocks(content: str) -> List[Tuple[int, str]]:
    """
    Find all mermaid code blocks in content.
    Returns list of (line_number, block_content).
    """
    blocks = []
    lines = content.split("\n")
    in_mermaid = False
    block_start = 0
    block_content = []
    fence_indent = 0

    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if not in_mermaid:
            if stripped.startswith("```mermaid"):
                in_mermaid = True
                block_start = i
                fence_indent = indent
                block_content = [line]
        else:
            block_content.append(line)
            # Check for closing fence at same or less indentation
            if stripped.startswith("```") and indent <= fence_indent:
                in_mermaid = False
                blocks.append((block_start, "\n".join(block_content)))

    return blocks


def find_diagram_id_comments(content: str) -> Dict[int, str]:
    """
    Find all diagram-id comments in content.
    Returns dict of {line_number: diagram_id}.
    """
    comments = {}
    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        match = re.search(r"<!--\s*diagram-id:\s*([^\s>]+)\s*-->", line)
        if match:
            comments[i] = match.group(1)

    return comments


def validate_file(file_path: Path, verbose: bool = False) -> List[ValidationError]:
    """Validate a single markdown file."""
    errors = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return [ValidationError(str(file_path), f"Could not read file: {e}")]

    # Find mermaid blocks
    mermaid_blocks = find_mermaid_blocks(content)

    if not mermaid_blocks:
        return []  # No mermaid, no validation needed

    rel_path = str(file_path)

    # Skip example code blocks in validation status pages
    if "content-validation-status" in rel_path or "validation-status" in rel_path:
        # These may contain example mermaid blocks in code fences
        pass

    # Check for frontmatter
    frontmatter, fm_end_line = extract_frontmatter(content)

    if not frontmatter:
        errors.append(ValidationError(rel_path, "Missing frontmatter"))
        return errors

    # Check for content_sources
    content_sources = frontmatter.get("content_sources")
    if not content_sources:
        errors.append(
            ValidationError(rel_path, "Missing content_sources in frontmatter")
        )
        return errors

    diagrams = content_sources.get("diagrams", [])
    if not diagrams:
        errors.append(ValidationError(rel_path, "content_sources.diagrams is empty"))
        return errors

    # Find diagram-id comments
    diagram_id_comments = find_diagram_id_comments(content)

    # Validate each mermaid block has a preceding comment
    for block_line, block_content in mermaid_blocks:
        # Look for comment in preceding 3 lines
        found_comment = False
        for check_line in range(block_line - 3, block_line):
            if check_line in diagram_id_comments:
                found_comment = True
                break

        if not found_comment:
            errors.append(
                ValidationError(
                    rel_path, f"Mermaid block missing diagram-id comment", block_line
                )
            )

    # Validate each diagram entry
    diagram_ids_in_frontmatter = set()

    for i, diagram in enumerate(diagrams):
        if not isinstance(diagram, dict):
            errors.append(
                ValidationError(
                    rel_path, f"content_sources.diagrams[{i}] is not a dict"
                )
            )
            continue

        # Check id
        diagram_id = diagram.get("id")
        if not diagram_id:
            errors.append(
                ValidationError(rel_path, f"content_sources.diagrams[{i}] missing 'id'")
            )
        else:
            diagram_ids_in_frontmatter.add(diagram_id)

        # Check source type
        source_type = diagram.get("source")
        if not source_type:
            errors.append(
                ValidationError(
                    rel_path, f"Diagram '{diagram_id}' missing 'source' field"
                )
            )
        elif source_type not in VALID_SOURCE_TYPES:
            errors.append(
                ValidationError(
                    rel_path,
                    f"Diagram '{diagram_id}' has invalid source type: {source_type}",
                )
            )
        else:
            # Check required fields for source type
            required = REQUIRED_FIELDS.get(source_type, [])
            for field in required:
                if field not in diagram or not diagram[field]:
                    errors.append(
                        ValidationError(
                            rel_path,
                            f"Diagram '{diagram_id}' ({source_type}) missing required field: {field}",
                        )
                    )

            # Self-generated should have based_on if adapting from MSLearn
            if source_type == "self-generated":
                if "based_on" not in diagram and "mslearn_url" not in diagram:
                    if verbose:
                        print(
                            f"  Note: {rel_path}: Diagram '{diagram_id}' is self-generated without based_on URLs"
                        )

    # Check that all diagram-id comments have corresponding frontmatter entries
    for line, diagram_id in diagram_id_comments.items():
        if diagram_id not in diagram_ids_in_frontmatter:
            errors.append(
                ValidationError(
                    rel_path,
                    f"Diagram-id comment '{diagram_id}' not found in frontmatter",
                    line,
                )
            )

    return errors


def validate_project(
    project_path: Path, verbose: bool = False
) -> Tuple[int, int, List[ValidationError]]:
    """
    Validate all markdown files in a project.
    Returns (files_checked, files_with_mermaid, errors).
    """
    docs_dir = project_path / "docs"
    if not docs_dir.exists():
        return 0, 0, [ValidationError(str(project_path), "docs directory not found")]

    all_errors = []
    files_checked = 0
    files_with_mermaid = 0

    for md_file in docs_dir.glob("**/*.md"):
        files_checked += 1

        try:
            content = md_file.read_text(encoding="utf-8")
        except:
            continue

        if "```mermaid" in content:
            files_with_mermaid += 1

        errors = validate_file(md_file, verbose)
        all_errors.extend(errors)

    return files_checked, files_with_mermaid, all_errors


def main():
    parser = argparse.ArgumentParser(description="Validate content sources metadata")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )
    parser.add_argument("--project", "-p", type=str, help="Specific project path")
    args = parser.parse_args()

    # Determine project path
    if args.project:
        project_path = Path(args.project)
    else:
        # Assume running from project root
        project_path = Path(__file__).parent.parent

    print(f"Validating content sources in: {project_path}")
    print("=" * 60)

    files_checked, files_with_mermaid, errors = validate_project(
        project_path, args.verbose
    )

    print(f"\nFiles checked: {files_checked}")
    print(f"Files with mermaid: {files_with_mermaid}")
    print(f"Validation errors: {len(errors)}")

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print("\nAll validations passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
