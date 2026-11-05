"""Apply Functions CI policy to the shared inventory scanner's live-tree report.

Run after diagram_inventory.py --check; this does not replace that snapshot gate.
Usage: python scripts/check_diagram_inventory_tree.py [--root PATH]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import diagram_inventory as inventory

ID: Final = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]*')
# Existing repository-only debt, not a general exemption for provisional IDs.
LEGACY_MISSING_ID: Final = 'labs/code-storage-verification/README.md#~1'


def check_tree(root: Path) -> list[str]:
    """Rescan with shared machinery; block structure, not body/location snapshots."""
    previous = json.loads(inventory.local(root, inventory.MANIFEST).read_text())
    rules = json.loads(inventory.local(root, inventory.RULES).read_text())
    current = inventory.build(root, rules, previous['baseline']['base_commit'])
    inventory.preserve(current, previous)
    difference = inventory.drift(previous, current)
    errors = []
    for category in ('added', 'removed', 'moved', 'reclassified', 'provenance', 'assets', 'visuals'):
        if difference[category]:
            errors.append(f'tree drift {category}: {json.dumps(difference[category], sort_keys=True)}')
    # Reuse schema, owner validity, extraction and generated-table checks on live facts.
    errors.extend(inventory.check(root, current, rules))
    for snapshot in (previous, current):
        for diagram in snapshot['diagrams']:
            identifier = diagram['diagram_id']
            if identifier is None and diagram['key'] == LEGACY_MISSING_ID:
                continue
            if identifier is None or ID.fullmatch(identifier) is None:
                errors.append(f'{diagram["key"]}: invalid or missing diagram ID')
        for unmatched in snapshot['exceptions']['frontmatter_entries_without_fence']:
            entry = unmatched['entry']
            identifier = entry.get('id') if isinstance(entry, dict) else None
            if not isinstance(identifier, str) or ID.fullmatch(identifier) is None:
                errors.append(f'{unmatched["page"]}: invalid or missing source diagram ID; '
                              f'entry={json.dumps(entry, sort_keys=True)}')
        for category in ('duplicate_ids_on_page', 'frontmatter_duplicate_ids'):
            if snapshot['exceptions'][category]:
                errors.append(f'{category}: {json.dumps(snapshot["exceptions"][category], sort_keys=True)}')
    # generated_page permits absent blocks for fixture/partial pages; CI requires all five.
    page = inventory.local(root, inventory.PAGE).read_text()
    for name in inventory.generated_tables(current):
        for boundary in ('BEGIN', 'END'):
            marker = f'<!-- {boundary} GENERATED: diagram-inventory:{name} -->'
            if page.count(marker) != 1:
                errors.append(f'{inventory.PAGE}: expected one {boundary} marker for {name}')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        errors = check_tree(args.root.resolve())
    except (inventory.InventoryError, OSError, json.JSONDecodeError) as error:
        print(f'diagram inventory tree: {error}', file=sys.stderr)
        return 1
    print('\n'.join(errors) if errors else 'diagram inventory tree: check passed (body/location drift advisory)')
    return int(bool(errors))


if __name__ == '__main__':
    sys.exit(main())
