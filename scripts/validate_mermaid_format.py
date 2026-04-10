#!/usr/bin/env python3
"""
Mermaid Format Validation Script

Validates that mermaid blocks are not incorrectly indented.
Indented mermaid blocks will not render properly.

Usage:
    python scripts/validate_mermaid_format.py [--fix]

Exit codes:
    0 - All validations passed
    1 - Validation errors found
"""

import os
import sys
import re
import argparse
from pathlib import Path


def find_indented_mermaid(filepath: Path) -> list:
    """Find incorrectly indented mermaid blocks."""
    errors = []
    
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return [f"Could not read file: {e}"]
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Check for mermaid blocks that start with spaces (incorrect)
        if re.match(r'^[ \t]+```mermaid', line):
            errors.append(f"Line {i}: Indented mermaid block will not render")
    
    return errors


def fix_indented_mermaid(filepath: Path) -> bool:
    """Fix incorrectly indented mermaid blocks."""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception:
        return False
    
    lines = content.split('\n')
    new_lines = []
    in_indented_mermaid = False
    indent_size = 0
    
    for line in lines:
        # Detect indented mermaid start
        match = re.match(r'^([ \t]+)```mermaid', line)
        if match:
            in_indented_mermaid = True
            indent_size = len(match.group(1))
            new_lines.append(line[indent_size:])
        elif in_indented_mermaid:
            # Check for closing fence
            if re.match(r'^[ \t]*```\s*$', line):
                if line.startswith(' ' * indent_size):
                    new_lines.append(line[indent_size:])
                else:
                    new_lines.append(line.lstrip())
                in_indented_mermaid = False
                indent_size = 0
            elif line.startswith(' ' * indent_size):
                new_lines.append(line[indent_size:])
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    filepath.write_text('\n'.join(new_lines), encoding='utf-8')
    return True


def validate_project(project_path: Path, fix: bool = False) -> tuple:
    """Validate all markdown files in docs/."""
    docs_dir = project_path / 'docs'
    if not docs_dir.exists():
        return 0, 0, []
    
    files_checked = 0
    files_with_errors = 0
    all_errors = []
    
    for md_file in docs_dir.rglob('*.md'):
        files_checked += 1
        errors = find_indented_mermaid(md_file)
        
        if errors:
            files_with_errors += 1
            rel_path = md_file.relative_to(project_path)
            
            if fix:
                if fix_indented_mermaid(md_file):
                    print(f"  [FIXED] {rel_path}")
                else:
                    print(f"  [ERROR] {rel_path}: Could not fix")
                    all_errors.append((str(rel_path), errors))
            else:
                all_errors.append((str(rel_path), errors))
    
    return files_checked, files_with_errors, all_errors


def main():
    parser = argparse.ArgumentParser(description='Validate mermaid block formatting')
    parser.add_argument('--fix', action='store_true', help='Auto-fix indented mermaid blocks')
    parser.add_argument('--project', '-p', type=str, help='Specific project path')
    args = parser.parse_args()
    
    if args.project:
        project_path = Path(args.project)
    else:
        project_path = Path(__file__).parent.parent
    
    print(f"Validating mermaid format in: {project_path}")
    print("=" * 60)
    
    files_checked, files_with_errors, errors = validate_project(project_path, args.fix)
    
    print(f"\nFiles checked: {files_checked}")
    print(f"Files with errors: {files_with_errors}")
    
    if errors and not args.fix:
        print("\nErrors found:")
        for filepath, file_errors in errors:
            print(f"\n  {filepath}:")
            for err in file_errors:
                print(f"    - {err}")
        print("\nRun with --fix to auto-correct these issues.")
        sys.exit(1)
    elif args.fix and files_with_errors > 0:
        print(f"\nFixed {files_with_errors} file(s).")
        sys.exit(0)
    else:
        print("\nAll mermaid blocks are correctly formatted!")
        sys.exit(0)


if __name__ == '__main__':
    main()
