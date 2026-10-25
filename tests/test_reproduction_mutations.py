"""Disable individual checks only in temporary copies; each regression must fail."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HUMAN_CHECK = ('not all(run.operator_kind == "human" and run.mode == "human-run"\n'
               '                 for run in (first, second))')
MUTATIONS = [
    ("first.run_id == second.run_id", "test_rejects_false_independence[run-id"),
    ("bool(first.raw_paths & second.raw_paths)", "test_rejects_false_independence[raw-path"),
    ("bool(first.raw_digests & second.raw_digests)", "test_rejects_false_independence[raw-digest"),
    ("not (first.provenance_present and second.provenance_present)",
     "test_rejects_false_independence[provenance"),
    ("first.operator_id == second.operator_id", "test_rejects_false_independence[same-operator"),
    (HUMAN_CHECK, "test_rejects_false_independence[ci"),
    (HUMAN_CHECK, "test_rejects_false_independence[ai"),
    (HUMAN_CHECK, "test_rejects_false_independence[offline"),
    ("(first.scenario_id, first.recipe_revision) != (second.scenario_id, second.recipe_revision)",
     "test_rejects_false_independence[recipe"),
    ("(first.scenario_id, first.recipe_revision) != (second.scenario_id, second.recipe_revision)",
     "test_rejects_false_independence[scenario"),
    ("first.captured_at == second.captured_at", "test_rejects_false_independence[timestamp"),
    ("first.package == second.package", "test_rejects_false_independence[package"),
    ('data.get("claim") == "independent-human-reproduction" and (synthetic or state != "MET")',
     "test_unsupported_human_approval_is_rejected"),
    ("hashlib.sha256(path.read_bytes()).hexdigest() != digest",
     "test_unverifiable_package_is_rejected[digest"),
    ("any(receipt.get(key) != value for key, value in binding.items())",
     "test_unverifiable_package_is_rejected[receipt"),
    ("second.captured_at > clock", "test_unverifiable_package_is_rejected[future"),
    ('_text(data["environment"])', "test_unverifiable_package_is_rejected[environment"),
    ('re.fullmatch(r"operator-[a-z0-9]+(?:-[a-z0-9]+)*", identity["operator_id"]) is None',
     "test_noncanonical_operator_is_malformed"),
    ("first.collection_window is None or second.collection_window is None",
     "test_retained_collection_windows[missing"),
    ("first.collection_window is not None and first.collection_window == second.collection_window",
     "test_retained_collection_windows[identical"),
    ('window.get("run_id") != identity["run_id"] or window.get("raw") != data["raw"]',
     "test_retained_collection_windows[unbound"),
    ("start > end or end > captured_at", "test_retained_collection_windows[order"),
    ("start > end or end > captured_at", "test_retained_collection_windows[capture"),
]


@pytest.mark.parametrize("predicate,selection", MUTATIONS, ids=[row[1] for row in MUTATIONS])
def test_rejection_detects_disabled_check(tmp_path: Path, predicate: str, selection: str) -> None:
    # Given an isolated copy, never a modification of the working implementation.
    for relative in ("scripts/lib/evidence_eval.py", "scripts/lib/reproduction_check.py",
                     "tests/test_reproduction_check.py",
                     "tests/fixtures/evidence/synthetic-reproduction.json"):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    module = tmp_path / "scripts/lib/reproduction_check.py"
    source = module.read_text()
    assert source.count(predicate) == 1
    module.write_text(source.replace(predicate, "False"))
    # When one guard is disabled and its rejection tests run in a fresh process.
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_reproduction_check.py", "-q", "-k", selection],
        cwd=tmp_path, env=os.environ | {"PYTHONPATH": str(tmp_path)},
        capture_output=True, text=True, check=False, timeout=30,
    )
    # Then an assertion must fail (not a collection/import error or an empty selection).
    assert result.returncode == 1, result.stdout + result.stderr
    assert "FAILED" in result.stdout
