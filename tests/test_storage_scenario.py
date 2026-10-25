"""Storage scenario replay using SYNTHETIC inputs only; never executes Azure."""

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
    ("missing-diagnostic-logs", "INCONCLUSIVE"),
    ("storage-logs-unavailable", "INCONCLUSIVE"),
    ("mixed-failures", "INCONCLUSIVE"),
    ("deployment-role-conflated", "INCONCLUSIVE"),
    ("binding-role-conflated", "INCONCLUSIVE"),
    ("403-alone", "INCONCLUSIVE"),
    ("403-with-controls", "INCONCLUSIVE"),
    ("restart-only-recovery", "INCONCLUSIVE"),
    ("restart-without-restoration", "INCONCLUSIVE"),
    ("dns-alternative", "CONTRADICTED"),
    ("transport-alternative", "CONTRADICTED"),
    ("firewall-alternative", "CONTRADICTED"),
    ("rbac-still-authorized", "CONTRADICTED"),
    ("counter-missing-diagnostics", "INCONCLUSIVE"),
    ("counter-role-conflated", "INCONCLUSIVE"),
    ("counter-mixed-failures", "INCONCLUSIVE"),
    ("counter-missing-baseline", "INCONCLUSIVE"),
    ("counter-package-drift", "INCONCLUSIVE"),
    ("conflicting-attribution", "INCONCLUSIVE"),
    ("counter-missing-recovery", "CONTRADICTED"),
    ("not-run", "NOT_TESTED"),
    ("partial", "NOT_TESTED"),
])
def test_synthetic_storage_outcome(tmp_path: Path, case: str, expected: str) -> None:
    # Given unchanged predeclared assertions and fictional observation variants.
    scenario = json.loads((FIXTURES / "storage-scenario.json").read_text())
    fixture = json.loads((FIXTURES / "synthetic-storage-cases.json").read_text())
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
    # When the existing evaluator recomputes the verdict, ignoring a forged PASS.
    result = evaluate(retained, hashlib.sha256(retained.read_bytes()).hexdigest(), EVALUATED_AT)
    # Then invalid prerequisites beat counters; valid counters beat missing recovery.
    assert result.hypothesis == expected
    assert result.evaluation_mode == "offline-replay"
    assert result.execution == variant.get("expected_execution", "COMPLETE")


def test_storage_definition_is_unexecuted() -> None:
    # Given the definition rather than the separate synthetic capture bundle.
    scenario = json.loads((FIXTURES / "storage-scenario.json").read_text())
    # When execution metadata is inspected.
    execution = scenario["execution"]
    # Then no live capture or tutorial test date is invented.
    assert execution == {"attempted": False, "blocked": False, "failed": False, "finished": False}
    assert scenario["execution_status"] == "NOT_RUN"
    assert scenario["hypothesis_status"] == "NOT_TESTED"
    assert scenario["events"] == []
    assert "captured_at" not in scenario
    assert "last_tested" not in scenario
