"""Negative and positive tests for the diagram migration coverage gate."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.check_diagram_migration_coverage import MANIFEST, coverage_errors, main, summary

ROOT = Path(__file__).resolve().parents[1]
REASON = 'Original flow retained: legible at 390px; metadata added only.'


def fixture() -> dict[str, Any]:
    def diagram(key: str, state: str = 'completed', method: str = 'rule') -> dict[str, Any]:
        return {'key': key, 'assignment': {'method': method},
                'migration': {'state': state, 'exception': REASON if state == 'exception' else None},
                'provenance': {'status': 'declared'},
                'target': {'base': None, 'extensions': [], 'overlays': [], 'status': 'provisional'}}
    return {'diagrams': [diagram('a.md#one'), diagram('a.md#two', 'exception'),
                         diagram('b.md#skip', 'not-started', 'excluded')], 'visuals': []}


class CoverageTests(unittest.TestCase):
    def test_committed_manifest_has_full_coverage(self) -> None:
        manifest = json.loads((ROOT / MANIFEST).read_text())
        self.assertEqual(coverage_errors(manifest), [])
        self.assertEqual(main(), 0)

    def test_fixture_passes(self) -> None:
        self.assertEqual(coverage_errors(fixture()), [])
        self.assertIn('2/2', summary(fixture()))

    def test_new_unconverted_diagram_fails(self) -> None:
        for state in ('not-started', 'in-progress'):
            manifest = fixture()
            manifest['diagrams'][0]['migration']['state'] = state
            self.assertEqual(coverage_errors(manifest), [f'a.md#one: unconverted (migration state "{state}")'])

    def test_exception_without_real_reason_fails(self) -> None:
        manifest = fixture()
        manifest['diagrams'][1]['migration']['exception'] = ' todo '
        self.assertEqual(len(coverage_errors(manifest)), 1)

    def test_missing_provenance_fails_except_legacy_debt(self) -> None:
        manifest = fixture()
        manifest['diagrams'][0]['provenance']['status'] = 'missing'
        self.assertIn('a.md#one: provenance is "missing", not declared', coverage_errors(manifest))
        manifest = fixture()
        manifest['diagrams'][0]['key'] = 'labs/code-storage-verification/README.md#~1'
        manifest['diagrams'][0]['provenance']['status'] = 'missing'
        self.assertEqual(coverage_errors(manifest), [])

    def test_invalid_component_ids_fail(self) -> None:
        for target, fragment in (({'base': 'bad id'}, 'invalid shared component ID'),
                                 ({'extensions': ['net']}, 'without a base'),
                                 ({'base': 'b', 'overlays': ['b']}, 'duplicate shared component ID')):
            manifest = fixture()
            manifest['diagrams'][0]['target'].update(target)
            self.assertTrue(any(fragment in e for e in coverage_errors(manifest)), target)

    def test_valid_target_passes(self) -> None:
        manifest = fixture()
        manifest['diagrams'][0]['target'].update({'base': 'functions-base', 'extensions': ['network'], 'overlays': ['fault']})
        self.assertEqual(coverage_errors(copy.deepcopy(manifest)), [])

    def test_excluded_with_state_and_unowned_visual_fail(self) -> None:
        manifest = fixture()
        manifest['diagrams'][2]['migration']['state'] = 'completed'
        manifest['visuals'] = [{'key': 'img.svg', 'assignment': {'method': 'rule'}}]
        self.assertEqual(len(coverage_errors(manifest)), 2)


if __name__ == '__main__':
    unittest.main()
