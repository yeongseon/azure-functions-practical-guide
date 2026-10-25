"""SYNTHETIC independence checks; no real operators, approvals or Azure runs."""

import hashlib
import json
from pathlib import Path

import pytest

from scripts.lib import reproduction_check
from scripts.lib.evidence_eval import EvidenceError, evaluate

FIXTURE = Path(__file__).parent / "fixtures/evidence/synthetic-reproduction.json"
EVALUATED_AT = "2026-01-01T00:00:00Z"


@pytest.fixture
def retained(tmp_path: Path) -> Path:
    """Materialize fictional raw collections and operator receipts in distinct packages."""
    data = json.loads(FIXTURE.read_text())
    for name in ("original", "reproduction"):
        run = data[name]
        package = tmp_path / name
        package.mkdir()
        raw = package / "raw.json"
        raw.write_text(json.dumps({"synthetic": True, "run_id": run["run_id"]}))
        receipt = package / "operator.json"
        receipt.write_text(json.dumps({
            key: run[key] for key in
            ("operator_id", "operator_kind", "run_id", "mode", "captured_at")
        } | {"synthetic": True}))
        run["package"] = name
        run["raw"] = [{"path": str(raw.relative_to(tmp_path)),
                       "sha256": hashlib.sha256(raw.read_bytes()).hexdigest()}]
        run["operator_provenance"] = str(receipt.relative_to(tmp_path))
        window = package / "window.json"
        window.write_text(json.dumps(run.pop("collection_window") | {
            "synthetic": True, "run_id": run["run_id"], "raw": run["raw"],
        }))
        run["window_evidence"] = str(window.relative_to(tmp_path))
    path = tmp_path / "comparison.json"
    path.write_text(json.dumps(data))
    return path


def check(path: Path) -> reproduction_check.ReproductionResult:
    return reproduction_check.evaluate(
        path, hashlib.sha256(path.read_bytes()).hexdigest(), EVALUATED_AT,
    )


def test_synthetic_independent_collections_meet_structural_contract(retained: Path) -> None:
    # Given two fictional human collections of the same recipe, in different conditions.
    original = retained.read_bytes()
    # When retained bytes and provenance are checked.
    result = check(retained)
    # Then only the synthetic structural contract is MET, not real human approval.
    assert result.independence == "MET"
    assert result.synthetic is True
    assert result.reasons == ()
    assert retained.read_bytes() == original


@pytest.mark.parametrize("case,reason", [
    ("run-id", "reused run identity"),
    ("raw-path", "reused raw evidence path"),
    ("raw-digest", "reused raw evidence digest"),
    ("provenance", "missing operator provenance"),
    ("same-operator", "same operator"),
    ("ci", "not two human collections"),
    ("ai", "not two human collections"),
    ("offline", "not two human collections"),
    ("recipe", "different scenario or recipe revision"),
    ("scenario", "different scenario or recipe revision"),
    ("timestamp", "reused capture timestamp"),
    ("package", "reused retained package"),
])
def test_rejects_false_independence(retained: Path, case: str, reason: str) -> None:
    # Given exactly one broken independence prerequisite (plus any necessary binding edits).
    data = json.loads(retained.read_text())
    first, second = data["original"], data["reproduction"]
    match case:
        case "run-id":
            second["run_id"] = first["run_id"]
        case "raw-path":
            second["raw"] = first["raw"]
        case "raw-digest":
            raw = retained.parent / second["raw"][0]["path"]
            raw.write_bytes((retained.parent / first["raw"][0]["path"]).read_bytes())
            second["raw"][0]["sha256"] = first["raw"][0]["sha256"]
        case "provenance":
            second.pop("operator_provenance")
        case "same-operator":
            second["operator_id"] = first["operator_id"]
        case "ci" | "ai":
            second.update(operator_kind=case, mode="automation-rerun")
        case "offline":
            second["mode"] = "offline-reevaluation"
        case "recipe":
            second["recipe_revision"] = "synthetic-recipe-v2"
        case "scenario":
            second["scenario_id"] = "another-synthetic-scenario"
        case "timestamp":
            second["captured_at"] = first["captured_at"]
        case "package":
            first["package"] = second["package"] = "."
    if "operator_provenance" in second:
        receipt = retained.parent / second["operator_provenance"]
        receipt.write_text(json.dumps({key: second[key] for key in
            ("operator_id", "operator_kind", "run_id", "mode", "captured_at")
        } | {"synthetic": True}))
    window = retained.parent / second["window_evidence"]
    window_data = json.loads(window.read_text())
    window_data.update(run_id=second["run_id"], raw=second["raw"])
    if case == "timestamp":
        first["captured_at"] = second["captured_at"] = "2025-01-03T00:05:00Z"
        for run in (first, second):
            receipt = retained.parent / run["operator_provenance"]
            provenance = json.loads(receipt.read_text())
            provenance["captured_at"] = run["captured_at"]
            receipt.write_text(json.dumps(provenance))
    window.write_text(json.dumps(window_data))
    data["independence"] = "MET"  # A stored result has no authority.
    retained.write_text(json.dumps(data))
    # When the checker recomputes rather than trusting the stored MET.
    result = check(retained)
    # Then the named prerequisite alone must prevent MET.
    assert result.independence == "NOT_MET"
    assert reason in result.reasons


@pytest.mark.parametrize("mode,kind", [
    ("automation-rerun", "ci"), ("automation-rerun", "ai"),
    ("offline-reevaluation", "human"), ("human-run", "human"),
])
def test_unsupported_human_approval_is_rejected(retained: Path, mode: str, kind: str) -> None:
    # Given a purported approval backed only by CI/AI/replay/the same operator.
    data = json.loads(retained.read_text())
    second = data["reproduction"]
    second.update(mode=mode, operator_kind=kind)
    if mode == "human-run":
        second["operator_id"] = data["original"]["operator_id"]
    data["synthetic"] = False
    for run in (data["original"], second):
        receipt = retained.parent / run["operator_provenance"]
        receipt.write_text(json.dumps({key: run[key] for key in
            ("operator_id", "operator_kind", "run_id", "mode", "captured_at")
        } | {"synthetic": False}))
        window = retained.parent / run["window_evidence"]
        window_data = json.loads(window.read_text())
        window_data["synthetic"] = False
        window.write_text(json.dumps(window_data))
    data["claim"] = "independent-human-reproduction"
    retained.write_text(json.dumps(data))
    # When the fictional record attempts to claim non-synthetic human approval.
    with pytest.raises(EvidenceError, match="unsupported independent human claim"):
        check(retained)


def test_no_second_run_is_not_tested_despite_stored_met(retained: Path) -> None:
    data = json.loads(retained.read_text())
    data.update(reproduction=None, independence="MET")
    retained.write_text(json.dumps(data))
    result = check(retained)
    assert result.independence == "NOT_TESTED"


def test_independence_does_not_gate_inconclusive_publication(retained: Path) -> None:
    # Given no second operator and a finished synthetic collection without decisive events.
    data = json.loads(retained.read_text())
    data["reproduction"] = None
    retained.write_text(json.dumps(data))
    bundle = json.loads((FIXTURE.parent / "synthetic-run.json").read_text())
    bundle["events"] = []
    evidence = retained.parent / "evidence.json"
    evidence.write_text(json.dumps(bundle))
    # When hypothesis and independence are independently computed.
    hypothesis = evaluate(evidence, hashlib.sha256(evidence.read_bytes()).hexdigest(), EVALUATED_AT)
    # Then honest INCONCLUSIVE publication remains possible.
    assert hypothesis.hypothesis == "INCONCLUSIVE"
    assert check(retained).independence == "NOT_TESTED"


@pytest.mark.parametrize("case", ["digest", "receipt", "future", "environment"])
def test_unverifiable_package_is_rejected(retained: Path, case: str) -> None:
    data = json.loads(retained.read_text())
    second = data["reproduction"]
    match case:
        case "digest":
            second["raw"][0]["sha256"] = "0" * 64
            window = retained.parent / second["window_evidence"]
            window_data = json.loads(window.read_text())
            window_data["raw"] = second["raw"]
            window.write_text(json.dumps(window_data))
        case "receipt":
            receipt = retained.parent / second["operator_provenance"]
            provenance = json.loads(receipt.read_text())
            provenance["operator_id"] = "synthetic-unrelated-person"
            receipt.write_text(json.dumps(provenance))
        case "future":
            second["captured_at"] = "2027-01-01T00:00:00Z"
            receipt = retained.parent / second["operator_provenance"]
            provenance = json.loads(receipt.read_text())
            provenance["captured_at"] = second["captured_at"]
            receipt.write_text(json.dumps(provenance))
        case "environment":
            second["environment"] = ""
    retained.write_text(json.dumps(data))
    with pytest.raises(EvidenceError):
        check(retained)


@pytest.mark.parametrize("token", [
    "OPERATOR-SYNTHETIC-A", "Operator-Synthetic-A", " operator-synthetic-a ",
    "synthetic.operator@example.com", "synthetic.operator+alias@example.com",
])
def test_noncanonical_operator_is_malformed(retained: Path, token: str) -> None:
    data = json.loads(retained.read_text())
    second = data["reproduction"]
    second["operator_id"] = token
    receipt = retained.parent / second["operator_provenance"]
    provenance = json.loads(receipt.read_text())
    provenance["operator_id"] = token
    receipt.write_text(json.dumps(provenance))
    retained.write_text(json.dumps(data))
    with pytest.raises(EvidenceError, match="non-canonical operator token"):
        check(retained)


@pytest.mark.parametrize("case", ["missing", "identical", "overlap", "subset", "unbound", "utc", "order", "capture"])
def test_retained_collection_windows(retained: Path, case: str) -> None:
    data = json.loads(retained.read_text())
    first, second = data["original"], data["reproduction"]
    window_path = retained.parent / second["window_evidence"]
    window = json.loads(window_path.read_text())
    match case:
        case "missing":
            second.pop("window_evidence")
        case "identical":
            window.update(start="2025-01-01T00:00:00Z", end="2025-01-01T00:04:00Z")
        case "overlap" | "subset":
            window.update(start="2025-01-01T00:02:00Z", end="2025-01-01T00:06:00Z"
                          if case == "overlap" else "2025-01-01T00:03:00Z")
        case "unbound":
            window["raw"] = first["raw"]
        case "utc":
            window["start"] = "2025-01-02T00:00:00+01:00"
        case "order":
            window["start"] = "2025-01-02T00:04:01Z"
        case "capture":
            window["end"] = "2025-01-02T00:05:01Z"
    window_path.write_text(json.dumps(window))
    retained.write_text(json.dumps(data))
    if case in {"unbound", "utc", "order", "capture"}:
        with pytest.raises(EvidenceError):
            check(retained)
    else:
        result = check(retained)
        assert result.independence == ("MET" if case in {"overlap", "subset"} else "NOT_MET")
        assert result.reasons == (() if case in {"overlap", "subset"} else
                                  ("missing collection window" if case == "missing" else
                                   "reused collection window",))
