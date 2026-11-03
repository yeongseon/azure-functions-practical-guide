"""Fixture-based tests for Functions CI policy, using the shared scanner unchanged."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import diagram_inventory as inventory
from scripts.check_diagram_inventory_tree import check_tree

ROOT = Path(__file__).resolve().parents[1]
FENCE = '<!-- diagram-id: x -->\n```mermaid\nflowchart LR\nA --> B\n```\n'


class TreePolicyTests(unittest.TestCase):
    def __init__(self, methodName: str = 'runTest') -> None:
        super().__init__(methodName)
        self.root: Path = Path(tempfile.gettempdir())
        self.page: Path = self.root

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / 'scripts').mkdir()
        (self.root / 'docs/reference').mkdir(parents=True)
        for relative in (inventory.SCRIPT, inventory.SCHEMA, inventory.RULES):
            _ = shutil.copyfile(ROOT / relative, self.root / relative)
        self.page = self.root / 'docs/reference/x.md'
        _ = self.page.write_text(FENCE)
        _ = (self.root / inventory.PAGE).write_text('\n'.join(
            f'<!-- BEGIN GENERATED: diagram-inventory:{name} -->\n<!-- END GENERATED: diagram-inventory:{name} -->'
            for name in ('section', 'type', 'batch', 'exclusions', 'exceptions')))
        self.write()

    def write(self) -> None:
        result = subprocess.run([sys.executable, str(self.root / inventory.SCRIPT),
                                 '--root', str(self.root), '--write', '--base-commit', '0' * 40],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_clean_tree_passes(self) -> None:
        # Given the generated fixture, when checked, then no structural drift exists.
        self.assertEqual(check_tree(self.root), [])

    def test_unregistered_fence_fails(self) -> None:
        # Given a registered fixture and a new fence, when checked, then coverage fails.
        _ = (self.root / 'docs/reference/new.md').write_text(FENCE)
        errors = check_tree(self.root)
        self.assertTrue(any('tree drift added:' in error for error in errors))

    def test_removed_fence_fails(self) -> None:
        # Given a manifest key whose fence is removed, when checked, then coverage fails.
        _ = self.page.write_text('# No diagram\n')
        errors = check_tree(self.root)
        self.assertTrue(any('tree drift removed:' in error for error in errors))

    def test_moved_or_renamed_key_fails(self) -> None:
        # Given the same body under another ID, when checked, then the key move fails.
        _ = self.page.write_text(FENCE.replace('diagram-id: x', 'diagram-id: new'))
        errors = check_tree(self.root)
        self.assertTrue(any('tree drift moved:' in error for error in errors))

    def test_duplicate_ids_fail_even_after_regeneration(self) -> None:
        # Given scanner-suffixed duplicate IDs, when checked, then uniqueness fails.
        _ = self.page.write_text(FENCE * 2)
        self.write()
        errors = check_tree(self.root)
        self.assertTrue(any('duplicate_ids_on_page:' in error for error in errors))

    def test_invalid_ids_fail_even_after_regeneration(self) -> None:
        for identifier in ('', 'two words', 'x#y', '~1', 'x/y', '<x>'):
            with self.subTest(identifier=identifier):
                # Given an invalid registered ID, when checked, then ID policy fails.
                _ = self.page.write_text(FENCE.replace('diagram-id: x', f'diagram-id: {identifier}'))
                self.write()
                errors = check_tree(self.root)
                self.assertTrue(any('invalid or missing diagram ID' in error for error in errors))

    def test_duplicate_frontmatter_ids_fail(self) -> None:
        # Given repeated source IDs, when checked, then duplicate metadata fails.
        _ = self.page.write_text('---\ncontent_sources:\n  diagrams: [{id: x}, {id: x}]\n---\n' + FENCE)
        self.write()
        errors = check_tree(self.root)
        self.assertTrue(any('frontmatter_duplicate_ids:' in error for error in errors))

    def test_wrong_valid_owner_fails(self) -> None:
        # Given a self-consistent snapshot assigned to another valid batch, check live rules.
        manifest = json.loads((self.root / inventory.MANIFEST).read_text())
        manifest['diagrams'][0]['assignment']['batch_issue'] = 212
        manifest['totals']['by_batch'] = {'212': 1}
        for batch in manifest['batches']:
            batch['count'] = int(batch['issue'] == 212)
        _ = (self.root / inventory.MANIFEST).write_text(inventory.encoded(manifest))
        _, updated = inventory.generated_page(self.root, manifest)
        assert updated is not None
        _ = (self.root / inventory.PAGE).write_text(updated)
        self.assertEqual(inventory.check(self.root, manifest, json.loads(
            (self.root / inventory.RULES).read_text())), [])
        errors = check_tree(self.root)
        self.assertTrue(any('tree drift reclassified:' in error for error in errors))

    def test_stale_live_type_reference_fails(self) -> None:
        # Given internally consistent old type tables, when the live type changes, fail.
        _ = self.page.write_text(FENCE.replace('flowchart LR\nA --> B', 'sequenceDiagram\nA->>B: hi'))
        errors = check_tree(self.root)
        self.assertTrue(any('stale generated blocks' in error for error in errors))

    def test_absent_generated_reference_fails(self) -> None:
        # Given deleted generated markers, when checked, then the missing reference fails.
        _ = (self.root / inventory.PAGE).write_text('# Inventory\n')
        errors = check_tree(self.root)
        self.assertTrue(any('expected one BEGIN marker' in error for error in errors))

    def test_body_and_location_only_drift_passes(self) -> None:
        # Given changed labels and shifted lines, when structure is unchanged, pass.
        _ = self.page.write_text('\n\n' + FENCE.replace('A --> B', 'A[New label] --> C'))
        self.assertEqual(check_tree(self.root), [])

    def test_reused_id_on_another_page_passes_after_registration(self) -> None:
        # Given page-qualified IDs, when registered on another page, then reuse is valid.
        _ = (self.root / 'docs/reference/second.md').write_text(FENCE)
        self.write()
        self.assertEqual(check_tree(self.root), [])

    def test_existing_repository_only_missing_id_passes(self) -> None:
        # Given the exact existing debt key, when registered, then migration is not forced.
        path = self.root / 'labs/code-storage-verification/README.md'
        path.parent.mkdir(parents=True)
        _ = path.write_text(FENCE.replace('<!-- diagram-id: x -->\n', ''))
        self.write()
        self.assertEqual(check_tree(self.root), [])

    def test_cli_returns_failure_for_structural_drift(self) -> None:
        # Given an added fence, when invoking the real CI entry point, then exit 1.
        _ = (self.root / 'docs/reference/new.md').write_text(FENCE)
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/check_diagram_inventory_tree.py'),
                                 '--root', str(self.root)], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_cli_returns_success_for_clean_tree(self) -> None:
        # Given the generated fixture, when invoking the CI entry point, then exit 0.
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/check_diagram_inventory_tree.py'),
                                 '--root', str(self.root)], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_topic_owner_change_fails_with_same_type_and_id(self) -> None:
        # Given a topic-sensitive owner, when the live heading changes, then fail.
        rules = json.loads((self.root / inventory.RULES).read_text())
        rules['ownership_rules'].append({'id': 'topic', 'paths': ['docs/reference/*'],
                                        'topic_regex': 'Runtime', 'priority': 200,
                                        'batch_issue': 212, 'rationale': 'Runtime topic'})
        _ = (self.root / inventory.RULES).write_text(inventory.encoded(rules))
        self.write()
        _ = self.page.write_text('# Runtime\n\n' + FENCE)
        errors = check_tree(self.root)
        self.assertTrue(any('tree drift reclassified:' in error for error in errors))

    def test_override_owner_passes_after_registration(self) -> None:
        # Given an override distinct from path ownership, when registered, then pass.
        rules = json.loads((self.root / inventory.RULES).read_text())
        rules['overrides']['docs/reference/x.md#x'] = {'batch_issue': 212, 'rationale': 'Reviewed owner'}
        _ = (self.root / inventory.RULES).write_text(inventory.encoded(rules))
        self.write()
        self.assertEqual(check_tree(self.root), [])

    def test_provenance_drift_fails(self) -> None:
        # Given newly declared source metadata, when not regenerated, then fail.
        _ = self.page.write_text('---\ncontent_sources:\n  diagrams: [{id: x}]\n---\n' + FENCE)
        errors = check_tree(self.root)
        self.assertTrue(any('tree drift provenance:' in error for error in errors))

    def test_asset_drift_fails(self) -> None:
        # Given a new tracked asset in the fixture tree, when not registered, then fail.
        _ = (self.root / 'docs/reference/new.svg').write_text('<svg/>')
        errors = check_tree(self.root)
        self.assertTrue(any('tree drift assets:' in error for error in errors))

    def test_existing_check_rejects_duplicate_or_missing_manifest_key(self) -> None:
        for defect in ('duplicate', 'missing', 'empty', 'spaces'):
            with self.subTest(defect=defect):
                # Given corrupt manifest keys, when the existing check runs, then fail.
                self.write()
                manifest = json.loads((self.root / inventory.MANIFEST).read_text())
                if defect == 'duplicate':
                    manifest['diagrams'].append(manifest['diagrams'][0])
                elif defect == 'missing':
                    del manifest['diagrams'][0]['key']
                else:
                    manifest['diagrams'][0]['key'] = '' if defect == 'empty' else 'bad key'
                rules = json.loads((self.root / inventory.RULES).read_text())
                errors = inventory.check(self.root, manifest, rules)
                self.assertTrue(errors)

    def test_visual_drift_fails(self) -> None:
        # Given an added visual in current rules, when the snapshot is stale, then fail.
        rules = json.loads((self.root / inventory.RULES).read_text())
        rules['visuals'] = [{'key': 'visual:x', 'kind': 'svg', 'pages': ['docs/reference/x.md'],
                             'sources': ['docs/reference/x.svg'],
                             'assignment': {'batch_issue': 216, 'method': 'rule', 'rule': 'fixture',
                                            'candidates': [], 'rationale': 'Fixture'},
                             'disposition': 'migration-required', 'rationale': 'Fixture'}]
        _ = (self.root / inventory.RULES).write_text(inventory.encoded(rules))
        errors = check_tree(self.root)
        self.assertTrue(any('tree drift visuals:' in error for error in errors))


if __name__ == '__main__':
    _ = unittest.main(verbosity=2)
