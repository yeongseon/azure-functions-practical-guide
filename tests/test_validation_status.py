"""Offline validation-report regressions; synthetic fixtures are not Azure runs."""

import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from scripts.generate_validation_status import generate_dashboard
from scripts.lib.tutorial_validation import (
    YAMLValue,
    assess_method,
    extract_tutorial_info,
    tutorial_status,
)

AS_OF = date(2026, 10, 25)
ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("stamp", ["bad", "2026-02-30", "2026-10-26", "20261025", None])
def test_pass_with_invalid_date_is_not_fresh(stamp: str | None) -> None:
    # Given an unsupported claimed pass date.
    data = {"result": "pass", "last_tested": stamp}
    # When the report evaluates that method.
    result = assess_method(data, AS_OF, ROOT)
    # Then the claim is preserved but cannot count as a fresh pass.
    assert result.result == "pass"
    assert result.freshness == "invalid"
    assert result.trust == "unverified"


@pytest.mark.parametrize("age,expected", [(89, "fresh"), (90, "fresh"), (91, "stale")])
def test_stale_boundary(age: int, expected: str) -> None:
    from datetime import timedelta

    # Given a real ISO date at the policy boundary.
    data = {"result": "pass", "last_tested": AS_OF - timedelta(days=age)}
    # When freshness is calculated against a fixed date.
    result = assess_method(data, AS_OF, ROOT)
    # Then only dates older than 90 days are stale.
    assert result.freshness == expected


def test_fresh_bicep_does_not_refresh_stale_cli() -> None:
    cli = assess_method({"result": "pass", "last_tested": "2026-04-12"}, AS_OF, ROOT)
    bicep = assess_method({"result": "pass", "last_tested": "2026-10-25"}, AS_OF, ROOT)
    assert cli.freshness == "stale"
    assert bicep.freshness == "fresh"
    assert tutorial_status([cli, bicep]) == "Stale pass claim"


def test_failure_takes_precedence_without_hiding_other_method() -> None:
    cli = assess_method({"result": "fail", "last_tested": "2026-04-12"}, AS_OF, ROOT)
    bicep = assess_method({"result": "pass", "last_tested": "2026-10-25"}, AS_OF, ROOT)
    assert tutorial_status([cli, bicep]) == "Failed claim"
    assert bicep.result == "pass"
    assert cli.freshness == "stale"


def test_methods_keep_independent_dates_and_results() -> None:
    # Given a failed CLI attempt and an unexecuted Bicep method.
    path = ROOT / "docs/language-guides/python/tutorial/consumption/02-first-deploy.md"
    tutorial = extract_tutorial_info(path, ROOT / "docs")
    # When both method records are rendered.
    report = generate_dashboard([tutorial], AS_OF)
    # Then the historical failure/date and unexecuted method remain distinct.
    assert "| az_cli | fail | 2026-04-12 | stale |" in report
    assert "| bicep | not_tested | — | NOT_RUN |" in report


@pytest.mark.parametrize("reference", ["missing.md", "run.md#absent", "run.md#run"])
def test_evidence_reference_mismatch_stays_unverified(
    tmp_path: Path, reference: str
) -> None:
    # Given a retained note that belongs to a different run.
    (tmp_path / "run.md").write_text("# Run\nrun_id: different\naz_cli 2026-10-25\n")
    data = {
        "result": "pass",
        "last_tested": "2026-10-25",
        "run_id": "expected",
        "evidence_ref": reference,
    }
    # When the optional locator is checked.
    result = assess_method(data, AS_OF, tmp_path)
    # Then a locator mismatch never promotes evidence trust.
    assert result.trust == "unverified"
    assert "mismatch" in result.binding


def test_matching_locator_does_not_prove_provenance(tmp_path: Path) -> None:
    # Given an author-entered note, not proof of a live run.
    (tmp_path / "run.md").write_text("# Run\nrun_id: expected\n")
    data = {
        "result": "pass",
        "last_tested": "2026-10-25",
        "run_id": "expected",
        "evidence_ref": "run.md#run",
    }
    # When the locator resolves.
    result = assess_method(data, AS_OF, tmp_path)
    # Then provenance, environment and retained captures still need human scrutiny.
    assert result.trust == "unverified"
    assert data["evidence_ref"] in result.binding


def test_absent_anchor_with_matching_run_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "run.md").write_text("# Run\nrun_id: expected\n")
    data = {
        "result": "pass",
        "last_tested": "2026-10-25",
        "run_id": "expected",
        "evidence_ref": "run.md#absent",
    }
    result = assess_method(data, AS_OF, tmp_path)
    assert "mismatch" in result.binding
    assert result.trust == "unverified"


@pytest.mark.parametrize("value", [[], "malformed", 42, False, {}])
def test_malformed_method_shape_is_invalid(value: YAMLValue) -> None:
    result = assess_method(value, AS_OF, ROOT)
    assert result.freshness == "invalid"


@pytest.mark.parametrize(
    "outcome,stamp",
    [("pass", "2026-10-25"), ("pass", "2026-04-12"), ("fail", "2026-10-25")],
)
def test_invalid_metadata_precedes_other_method(outcome: str, stamp: str) -> None:
    valid = assess_method({"result": outcome, "last_tested": stamp}, AS_OF, ROOT)
    invalid = assess_method({"result": "pass", "last_tested": "bad"}, AS_OF, ROOT)
    assert tutorial_status([valid, invalid]) == "Invalid metadata"


@pytest.mark.parametrize(
    "frontmatter",
    [
        "validation: []",
        "validation: malformed",
        "validation: null",
        "validation: 42",
        "validation: false",
        "[]",
        "malformed",
        "validation:\n  az_cli: []",
        "validation:\n  az_cli: {}",
        "validation:\n  az_cli: null",
    ],
)
def test_malformed_container_is_counted_in_report(
    tmp_path: Path, frontmatter: str
) -> None:
    path = tmp_path / "language-guides/python/tutorial/consumption/01-local-run.md"
    path.parent.mkdir(parents=True)
    path.write_text(f"---\n{frontmatter}\n---\n")
    tutorial = extract_tutorial_info(path, tmp_path)
    report = generate_dashboard([tutorial], AS_OF)
    assert "| Invalid metadata | 1 |" in report
    assert "| Not tested / no data | 0 |" in report


@pytest.mark.parametrize("outcome", ["fail", "not_tested", "unexpected"])
def test_nonpass_never_becomes_pass(outcome: str) -> None:
    # Given an outcome other than pass, including malformed input.
    data = {"result": outcome, "last_tested": "2026-10-25"}
    # When it is evaluated.
    result = assess_method(data, AS_OF, ROOT)
    # Then the stored outcome is not silently treated as a successful validation.
    assert result.result == outcome
    assert result.trust == "unverified"


def test_legacy_syntax_check_is_separate_from_live_run() -> None:
    data = {"result": "syntax_validated", "last_tested": "2026-06-06"}
    result = assess_method(data, AS_OF, ROOT)
    assert result.result == "syntax_validated"
    assert result.last_tested == "2026-06-06"
    assert result.freshness == "static-only"


@pytest.mark.parametrize(
    "stamp,expected",
    [
        ("bad", "invalid"), ("2026-02-30", "invalid"),
        ("2026-10-26", "invalid"), ("20261025", "invalid"),
        (20261025, "invalid"), (AS_OF.isoformat(), "static-only"),
    ],
)
def test_static_date_validation_preserves_history(stamp: str | int, expected: str) -> None:
    # Given static history with a present date, including the report-date boundary.
    data = {"result": "syntax_validated", "last_tested": stamp}
    # When the method is assessed.
    result = assess_method(data, AS_OF, ROOT)
    # Then invalid timing is visible without rewriting the reported history.
    assert result.freshness == expected
    assert result.result == "syntax_validated"
    assert result.last_tested == str(stamp)


def test_null_static_date_keeps_unknown_timing() -> None:
    # Given static history without a recorded date.
    data = {"result": "syntax_validated", "last_tested": None}
    # When the method is assessed.
    result = assess_method(data, AS_OF, ROOT)
    # Then it remains static-only without inventing timing.
    assert result.freshness == "static-only"
    assert result.last_tested == "—"
    assert result.result == "syntax_validated"


def test_malformed_static_date_makes_tutorial_invalid() -> None:
    # Given static history with malformed timing.
    method = assess_method(
        {"result": "syntax_validated", "last_tested": "bad"}, AS_OF, ROOT
    )
    # When the tutorial outcome is summarized.
    status = tutorial_status([method])
    # Then malformed static history is not hidden by the absence of live results.
    assert status == "Invalid metadata"


def test_malformed_yaml_date_is_reported_not_crashed(tmp_path: Path) -> None:
    path = tmp_path / "language-guides/python/tutorial/consumption/01-local-run.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "---\nvalidation:\n  az_cli:\n    result: pass\n    last_tested: 2026-02-30\n---\n"
    )
    tutorial = extract_tutorial_info(path, tmp_path)
    result = assess_method(tutorial.validation["az_cli"], AS_OF, tmp_path)
    assert result.last_tested == "2026-02-30"
    assert result.freshness == "invalid"


def test_cli_fixed_date_check_detects_drift(tmp_path: Path) -> None:
    # Given the real offline CLI and an isolated output file.
    output = tmp_path / "report.md"
    command = [
        sys.executable,
        "scripts/generate_validation_status.py",
        "--as-of",
        "2026-10-25",
        "--output",
        str(output),
    ]
    # When generation and check are run at the same fixed date.
    subprocess.run(command, cwd=ROOT, check=True)
    checked = subprocess.run([*command, "--check"], cwd=ROOT, check=False)
    # Then generation is reproducible and a different as-of date detects drift.
    assert checked.returncode == 0
    changed = ["2026-10-26" if item == "2026-10-25" else item for item in command]
    assert subprocess.run([*changed, "--check"], cwd=ROOT, check=False).returncode == 1
