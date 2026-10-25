"""Deployment scenario replay with SYNTHETIC data only; never calls Azure."""

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
    ("deploy-only", "INCONCLUSIVE"),
    ("deploy-and-running", "INCONCLUSIVE"),
    ("missing-function-list", "INCONCLUSIVE"),
    ("telemetry-settings-unavailable", "INCONCLUSIVE"),
    ("telemetry-ingestion-delayed", "INCONCLUSIVE"),
    ("no-discriminator", "INCONCLUSIVE"),
    ("fault-invoked", "CONTRADICTED"),
    ("not-run", "NOT_TESTED"),
])
def test_synthetic_deployment_outcome(tmp_path: Path, case: str, expected: str) -> None:
    # Given a predeclared scenario and explicitly fictional observation variants.
    scenario = json.loads((FIXTURES / "deployment-scenario.json").read_text())
    fixture = json.loads((FIXTURES / "synthetic-deployment-cases.json").read_text())
    variant = fixture["cases"][case]
    bundle = fixture["bundle"]
    bundle["assertions"] = scenario["assertions"]
    bundle["execution"] = variant.get("execution", bundle["execution"])
    bundle["events"] = [
        dict(event, value=variant.get("replace", {}).get(event["signal"], event["value"]))
        for event in bundle["events"]
        if event["signal"] not in variant.get("omit", [])
        and ("keep" not in variant or event["signal"] in variant["keep"])
    ]
    retained = tmp_path / "synthetic.json"
    retained.write_text(json.dumps(bundle))
    # When the real evaluator recomputes assertions, ignoring the forged PASS.
    result = evaluate(retained, hashlib.sha256(retained.read_bytes()).hexdigest(), EVALUATED_AT)
    # Then absence/unavailable data cannot masquerade as success or disproof.
    assert result.hypothesis == expected
    assert result.evaluation_mode == "offline-replay"
    assert result.execution == ("NOT_RUN" if case == "not-run" else "COMPLETE")


def test_scenario_definition_has_no_live_capture_or_test_date() -> None:
    # Given the committed definition, rather than any fictional observation bundle.
    scenario = json.loads((FIXTURES / "deployment-scenario.json").read_text())
    # When its execution record is inspected independently of synthetic cases.
    execution = scenario["execution"]
    # Then it remains unattempted with no invented live timestamp or verification.
    assert execution == {"attempted": False, "blocked": False, "failed": False, "finished": False}
    assert scenario["execution_status"] == "NOT_RUN"
    assert scenario["hypothesis_status"] == "NOT_TESTED"
    assert "captured_at" not in scenario
    assert "last_tested" not in scenario
    assert scenario["events"] == []
