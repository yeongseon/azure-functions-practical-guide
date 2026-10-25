"""Queue scenario replay with SYNTHETIC data only; never executes Azure."""

import hashlib
import json
from pathlib import Path
from typing import Final

import pytest

from scripts.lib.evidence_eval import evaluate

FIXTURES: Final = Path(__file__).parent / "fixtures/evidence"
EVALUATED_AT: Final = "2025-01-02T00:00:00Z"  # Fictional replay clock.


@pytest.mark.parametrize("case,expected", [
    ("all-signals", "SUPPORTED"),
    ("status-only", "INCONCLUSIVE"),
    ("missing-acknowledgement", "INCONCLUSIVE"),
    ("redelivery-without-work-record", "INCONCLUSIVE"),
    ("telemetry-gap", "INCONCLUSIVE"),
    ("probe-success-without-commit", "INCONCLUSIVE"),
    ("duplicate-business-effect", "CONTRADICTED"),
    ("positive-poison-mismatch", "CONTRADICTED"),
    ("swallowed-failure", "CONTRADICTED"),
    ("poison-missing", "INCONCLUSIVE"),
    ("application-retry-conflated", "INCONCLUSIVE"),
    ("conflicting-records", "INCONCLUSIVE"),
    ("counter-missing-recovery", "CONTRADICTED"),
    ("not-run", "NOT_TESTED"),
    ("partial", "NOT_TESTED"),
])
def test_synthetic_queue_outcome(tmp_path: Path, case: str, expected: str) -> None:
    # Given unchanged predeclared assertions and explicitly fictional captures.
    scenario = json.loads((FIXTURES / "queue-scenario.json").read_text())
    fixture = json.loads((FIXTURES / "synthetic-queue-cases.json").read_text())
    variant = fixture["cases"][case]
    bundle = fixture["bundle"]
    bundle["assertions"] = scenario["assertions"]
    bundle["execution"] = variant.get("execution", bundle["execution"])
    bundle["events"] = [
        dict(event, value=variant.get("replace", {}).get(event["signal"], event["value"]))
        for event in bundle["events"]
        if event["signal"] not in variant.get("omit", [])
        and ("keep" not in variant or event["signal"] in variant["keep"])
    ] + variant.get("append", [])
    retained = tmp_path / "synthetic.json"
    retained.write_text(json.dumps(bundle))
    # When the existing evaluator recomputes instead of trusting the forged PASS.
    result = evaluate(retained, hashlib.sha256(retained.read_bytes()).hexdigest(), EVALUATED_AT)
    # Then missing data cannot prove success, and valid counters precede absent recovery.
    assert result.hypothesis == expected
    assert result.evaluation_mode == "offline-replay"
    assert result.execution == variant.get("expected_execution", "COMPLETE")


@pytest.mark.parametrize("control", json.loads(
    (FIXTURES / "synthetic-queue-cases.json").read_text(),
)["control_matrix"], ids=lambda control: control[0])
@pytest.mark.parametrize("missing", [True, False], ids=["missing", "invalid"])
def test_counter_requires_every_control(
    tmp_path: Path, control: tuple[str, str], missing: bool,
) -> None:
    # Given decisive duplicate-effect evidence and one missing/invalid prerequisite.
    scenario = json.loads((FIXTURES / "queue-scenario.json").read_text())
    bundle = json.loads((FIXTURES / "synthetic-queue-cases.json").read_text())["bundle"]
    signal, invalid = control
    bundle["assertions"] = scenario["assertions"]
    bundle["events"] = [
        dict(event, value="multiple-durable-effects-for-one-key")
        if event["signal"] == "fault.business-effect"
        else dict(event, value=invalid) if event["signal"] == signal else event
        for event in bundle["events"]
        if not (missing and event["signal"] == signal)
    ]
    retained = tmp_path / "synthetic-control.json"
    retained.write_text(json.dumps(bundle))
    # When the real evaluator applies the scenario's unchanged roles.
    result = evaluate(retained, hashlib.sha256(retained.read_bytes()).hexdigest(), EVALUATED_AT)
    # Then every prerequisite gates contradiction as well as support.
    assert result.execution == "COMPLETE"
    assert result.hypothesis == "INCONCLUSIVE"


def test_control_matrix_covers_all_prerequisites() -> None:
    # Given separately declared assertions and the negative-case matrix.
    scenario = json.loads((FIXTURES / "queue-scenario.json").read_text())
    fixture = json.loads((FIXTURES / "synthetic-queue-cases.json").read_text())
    # When control signals and invalid values are compared.
    controls = {(a["signal"], a["counter"]) for a in scenario["assertions"] if a["role"] == "control"}
    # Then no prerequisite silently escapes the missing/invalid matrix.
    assert controls == {tuple(row) for row in fixture["control_matrix"]}


def test_queue_definition_is_unexecuted() -> None:
    # Given the definition, not the synthetic observation bundle.
    scenario = json.loads((FIXTURES / "queue-scenario.json").read_text())
    # When execution metadata is inspected.
    execution = scenario["execution"]
    # Then no Azure capture or tutorial date is invented.
    assert execution == {"attempted": False, "blocked": False, "failed": False, "finished": False}
    assert scenario["execution_status"] == "NOT_RUN"
    assert scenario["hypothesis_status"] == "NOT_TESTED"
    assert scenario["events"] == []
    assert "captured_at" not in scenario
    assert "last_tested" not in scenario
