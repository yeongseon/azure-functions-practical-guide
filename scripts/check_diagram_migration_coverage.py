"""Fail when the diagram manifest shows unconverted or unsupported migration entries.

Complements diagram_inventory.py --check (schema/ownership/stale output) and
check_diagram_inventory_tree.py (live-tree drift); it reads only the committed
manifest and renders nothing. Mermaid rendering stays a browser review step.
Usage: python scripts/check_diagram_migration_coverage.py [--root PATH]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Final

MANIFEST: Final = 'docs/reference/diagram-manifest.json'
ID: Final = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]*')
DONE: Final = ('completed', 'exception')
MIN_EXCEPTION_CHARS: Final = 20
# Mirrors REQUIRED_FIELDS in validate_content_sources.py (that audit is advisory in CI).
REQUIRED_FIELDS: Final = {
    'mslearn': ('id', 'type', 'source', 'mslearn_url'),
    'mslearn-adapted': ('id', 'type', 'source', 'mslearn_url'),
    'self-generated': ('id', 'type', 'source', 'justification'),
}
# Existing repository-only debt, mirrored from check_diagram_inventory_tree.py.
LEGACY_MISSING_PROVENANCE: Final = 'labs/code-storage-verification/README.md#~1'


def coverage_errors(manifest: dict[str, Any]) -> list[str]:
    """Return one message per migration-coverage violation in a manifest snapshot."""
    errors: list[str] = []
    required = [d for d in manifest['diagrams'] if d['assignment']['method'] != 'excluded']
    for diagram in required:
        key, state = diagram['key'], diagram['migration']['state']
        reason = diagram['migration']['exception']
        if state not in DONE:
            errors.append(f'{key}: unconverted (migration state "{state}")')
        elif state == 'exception' and len((reason or '').strip()) < MIN_EXCEPTION_CHARS:
            errors.append(f'{key}: exception needs a documented reason of at least '
                          f'{MIN_EXCEPTION_CHARS} characters')
        if diagram['provenance']['status'] != 'declared' and key != LEGACY_MISSING_PROVENANCE:
            errors.append(f'{key}: provenance is "{diagram["provenance"]["status"]}", not declared')
        elif key != LEGACY_MISSING_PROVENANCE:
            declared = diagram['provenance'].get('declared') or {}
            fields = REQUIRED_FIELDS.get(declared.get('source'))
            if fields is None:
                errors.append(f'{key}: provenance source {declared.get("source")!r} is not one of '
                              f'{sorted(REQUIRED_FIELDS)}')
            else:
                blank = [f for f in fields if not str(declared.get(f) or '').strip()]
                if blank:
                    errors.append(f'{key}: provenance missing required field(s) {blank} '
                                  f'for source "{declared["source"]}"')
        target = diagram['target']
        refs = [r for r in (target['base'], *target['extensions'], *target['overlays']) if r is not None]
        bad = [r for r in refs if not isinstance(r, str) or ID.fullmatch(r) is None]
        if bad:
            errors.append(f'{key}: invalid shared component ID {bad}')
        if (target['extensions'] or target['overlays']) and target['base'] is None:
            errors.append(f'{key}: extensions or overlays without a base')
        if len(set(refs)) != len(refs):
            errors.append(f'{key}: duplicate shared component ID in target')
    for diagram in manifest['diagrams']:
        if diagram['assignment']['method'] == 'excluded' and diagram['migration']['state'] != 'not-started':
            errors.append(f'{diagram["key"]}: excluded diagram must not carry a migration state')
    for visual in manifest['visuals']:
        if visual['assignment']['method'] != 'excluded':
            errors.append(f'{visual["key"]}: non-Mermaid visual is in migration scope but has no migration record')
    return errors


def summary(manifest: dict[str, Any]) -> str:
    required = [d for d in manifest['diagrams'] if d['assignment']['method'] != 'excluded']
    done = sum(d['migration']['state'] in DONE for d in required)
    return f'{done}/{len(required)} in-scope diagrams migrated or documented as exceptions'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        manifest = json.loads((args.root / MANIFEST).read_text())
        errors = coverage_errors(manifest)
        line = summary(manifest)
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f'diagram migration coverage: cannot read manifest: {error!r}', file=sys.stderr)
        return 1
    print('\n'.join(errors) if errors else f'diagram migration coverage: check passed ({line})')
    return int(bool(errors))


if __name__ == '__main__':
    sys.exit(main())
