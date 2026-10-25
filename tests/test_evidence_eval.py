"""Offline synthetic replay cases; none of these tests executes Azure."""

import hashlib
import json
from pathlib import Path

import pytest

from scripts.lib.evidence_eval import EvidenceError, evaluate, write_result

FIXTURE = Path(__file__).parent / "fixtures/evidence/synthetic-run.json"
EVALUATED_AT = "2026-01-01T00:00:00Z"
DIGEST = "f53f350ee53784fbb90665550cb6da1a41070698deac0f938b99ad92f4d7551e"


def test_replay_preserves_historical_capture(tmp_path: Path) -> None:
    # Given a retained synthetic historical run and an independently pinned digest.
    original = FIXTURE.read_bytes()
    digest = DIGEST
    # When replay creates a new derived result.
    result = evaluate(FIXTURE, digest, EVALUATED_AT)
    write_result(tmp_path / "evaluation.json", result)
    # Then capture bytes/time remain historical and replay is explicitly offline.
    assert FIXTURE.read_bytes() == original
    assert result.hypothesis == "SUPPORTED"
    assert result.captured_at == "2025-01-01T00:05:00Z"
    assert result.evaluated_at == EVALUATED_AT
    assert result.evaluation_mode == "offline-replay"


def test_digest_rejects_changed_retained_run(tmp_path: Path) -> None:
    original = FIXTURE.read_bytes()
    retained = tmp_path / "run.json"
    retained.write_bytes(original + b"\n")
    with pytest.raises(EvidenceError, match="digest"):
        evaluate(retained, hashlib.sha256(original).hexdigest(), EVALUATED_AT)


def test_result_cannot_overwrite_retained_evidence() -> None:
    result = evaluate(FIXTURE, hashlib.sha256(FIXTURE.read_bytes()).hexdigest(), EVALUATED_AT)
    with pytest.raises(FileExistsError):
        write_result(FIXTURE, result)


def test_negative_replay(tmp_path: Path) -> None:
    # Given an author-entered PASS but no retained events.
    data = json.loads(FIXTURE.read_text())
    data.pop("events")
    retained = tmp_path / "run.json"
    retained.write_text(json.dumps(data))
    # When the raw evidence is recomputed, not the stored verdict read.
    result = evaluate(retained, hashlib.sha256(retained.read_bytes()).hexdigest(), EVALUATED_AT)
    # Then a finished collection with no usable logs is inconclusive, not contradicted.
    assert result.execution == "COMPLETE"
    assert result.hypothesis == "INCONCLUSIVE"


@pytest.mark.parametrize("case", [
    "empty", "wrong-run", "wrong-window", "conflicting", "unknown-value",
    "symptom-only", "supporting-only", "recovery-only", "missing-control",
    "broken-control", "missing-discriminator", "counter-wrong-run", "counter-wrong-window",
])
def test_missing_or_ambiguous_evidence_is_inconclusive(tmp_path: Path, case: str) -> None:
    data = json.loads(FIXTURE.read_text())
    match case:
        case "empty":
            data["events"] = []
        case "wrong-run":
            data["events"][1]["run_id"] = "different-run"
        case "counter-wrong-run":
            data["events"][1].update(run_id="different-run", value="alternative")
        case "wrong-window":
            data["events"][1]["timestamp"] = "2025-01-02T00:00:00Z"
        case "counter-wrong-window":
            data["events"][1].update(timestamp="2025-01-02T00:00:00Z", value="alternative")
        case "conflicting":
            data["events"].append(dict(data["events"][1], value="alternative"))
        case "unknown-value":
            data["events"][1]["value"] = "unrecognized"
        case "symptom-only" | "supporting-only" | "recovery-only":
            data["assertions"][1]["role"] = case.removesuffix("-only")
        case "missing-control":
            data["events"] = data["events"][1:]
        case "broken-control":
            data["events"][0]["value"] = "broken"
        case "missing-discriminator":
            data["events"] = data["events"][:1]
    retained = tmp_path / "run.json"
    retained.write_text(json.dumps(data))
    result = evaluate(retained, hashlib.sha256(retained.read_bytes()).hexdigest(), EVALUATED_AT)
    assert result.execution == "COMPLETE"
    assert result.hypothesis == "INCONCLUSIVE"


@pytest.mark.parametrize("stored", ["PASS", "SUPPORTED", "CONTRADICTED", "INCONCLUSIVE"])
def test_valid_counter_evidence_overrides_stored_verdict(tmp_path: Path, stored: str) -> None:
    data = json.loads(FIXTURE.read_text())
    data["verdict"] = stored
    data["events"][1]["value"] = "alternative"
    retained = tmp_path / "run.json"
    retained.write_text(json.dumps(data))
    result = evaluate(retained, hashlib.sha256(retained.read_bytes()).hexdigest(), EVALUATED_AT)
    assert result.hypothesis == "CONTRADICTED"
    assert result.assertions[1].event_indexes == (1,)


@pytest.mark.parametrize("flags,execution", [
    ((False, False, False, False), "NOT_RUN"),
    ((False, True, False, False), "BLOCKED"),
    ((True, True, True, False), "BLOCKED"),
    ((True, False, True, False), "FAILED"),
    ((True, False, True, True), "FAILED"),
    ((True, False, False, False), "PARTIAL"),
])
def test_incomplete_execution_never_verifies_hypothesis(
    tmp_path: Path, flags: tuple[bool, ...], execution: str,
) -> None:
    data = json.loads(FIXTURE.read_text())
    data["execution"] = dict(zip(("attempted", "blocked", "failed", "finished"), flags))
    retained = tmp_path / "run.json"
    retained.write_text(json.dumps(data))
    result = evaluate(retained, hashlib.sha256(retained.read_bytes()).hexdigest(), EVALUATED_AT)
    assert result.execution == execution
    assert result.hypothesis == "NOT_TESTED"


@pytest.mark.parametrize("case", [
    "predicate", "role", "event", "timestamp", "window", "execution", "assertions",
    "duplicate-id", "same-counter", "future-capture", "events-type", "unattempted-finished",
])
def test_malformed_or_unsupported_input_is_rejected(tmp_path: Path, case: str) -> None:
    data = json.loads(FIXTURE.read_text())
    match case:
        case "predicate":
            data["assertions"][1]["predicate"] = "eval"
        case "role":
            data["assertions"][1]["role"] = "root-cause"
        case "event":
            data["events"][1] = {"verdict": "PASS"}
        case "timestamp":
            data["events"][1]["timestamp"] = "2025-01-01T00:02:00"
        case "window":
            data["window"]["end"] = "2024-01-01T00:00:00Z"
        case "execution":
            data["execution"]["finished"] = "true"
        case "assertions":
            data["assertions"] = []
        case "duplicate-id":
            data["assertions"][1]["id"] = "collection"
        case "same-counter":
            data["assertions"][1]["counter"] = "fault"
        case "future-capture":
            data["captured_at"] = "2027-01-01T00:00:00Z"
        case "events-type":
            data["events"] = None
        case "unattempted-finished":
            data["execution"]["attempted"] = False
    retained = tmp_path / "run.json"
    retained.write_text(json.dumps(data))
    with pytest.raises(EvidenceError):
        evaluate(retained, hashlib.sha256(retained.read_bytes()).hexdigest(), EVALUATED_AT)


@pytest.mark.parametrize("raw", [b"{", b"[]", b"\xff", b"null"])
def test_invalid_json_is_rejected(tmp_path: Path, raw: bytes) -> None:
    retained = tmp_path / "run.json"
    retained.write_bytes(raw)
    with pytest.raises(EvidenceError):
        evaluate(retained, hashlib.sha256(raw).hexdigest(), EVALUATED_AT)


def test_absent_artifact_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(EvidenceError):
        evaluate(tmp_path / "missing.json", DIGEST, EVALUATED_AT)


def test_each_replay_writes_new_result_only(tmp_path: Path) -> None:
    result = evaluate(FIXTURE, DIGEST, EVALUATED_AT)
    earlier = tmp_path / "earlier.json"
    write_result(earlier, result)
    original = earlier.read_bytes()
    replay = evaluate(FIXTURE, DIGEST, "2026-02-01T00:00:00Z")
    write_result(tmp_path / "new.json", replay)
    assert earlier.read_bytes() == original
    assert replay.evidence_sha256 == result.evidence_sha256
    assert replay.captured_at == result.captured_at
    with pytest.raises(FileExistsError):
        write_result(earlier, replay)


def test_result_symlink_cannot_modify_evidence(tmp_path: Path) -> None:
    result = evaluate(FIXTURE, DIGEST, EVALUATED_AT)
    output = tmp_path / "result.json"
    output.symlink_to(FIXTURE)
    with pytest.raises(FileExistsError):
        write_result(output, result)


def test_stored_failure_cannot_override_support(tmp_path: Path) -> None:
    data = json.loads(FIXTURE.read_text())
    data.update(verdict="CONTRADICTED", result="FAIL")
    retained = tmp_path / "run.json"
    retained.write_text(json.dumps(data))
    result = evaluate(retained, hashlib.sha256(retained.read_bytes()).hexdigest(), EVALUATED_AT)
    assert result.hypothesis == "SUPPORTED"


@pytest.mark.parametrize("other", ["missing-supporting", "supported-discriminator"])
def test_decisive_counter_precedes_support_completeness(tmp_path: Path, other: str) -> None:
    data = json.loads(FIXTURE.read_text())
    data["events"][1]["value"] = "alternative"
    role = "supporting" if other == "missing-supporting" else "discriminating"
    data["assertions"].append(dict(data["assertions"][1], id="separate", signal="other", role=role))
    if other == "supported-discriminator":
        data["events"].append(dict(data["events"][1], signal="other", value="fault"))
    retained = tmp_path / "run.json"
    retained.write_text(json.dumps(data))
    result = evaluate(retained, hashlib.sha256(retained.read_bytes()).hexdigest(), EVALUATED_AT)
    assert result.hypothesis == "CONTRADICTED"


@pytest.mark.parametrize("control", ["absent-assertion", "absent-observation", "broken"])
def test_decisive_counter_requires_valid_control(tmp_path: Path, control: str) -> None:
    data = json.loads(FIXTURE.read_text())
    data["events"][1]["value"] = "alternative"
    if control == "absent-assertion":
        data["assertions"] = data["assertions"][1:]
    elif control == "absent-observation":
        data["events"] = data["events"][1:]
    else:
        data["events"][0]["value"] = "broken"
    retained = tmp_path / "run.json"
    retained.write_text(json.dumps(data))
    result = evaluate(retained, hashlib.sha256(retained.read_bytes()).hexdigest(), EVALUATED_AT)
    assert result.hypothesis == "INCONCLUSIVE"


def test_conflict_within_assertion_blocks_separate_decisive_counter(tmp_path: Path) -> None:
    data = json.loads(FIXTURE.read_text())
    data["events"][1]["value"] = "alternative"
    data["assertions"].append(dict(data["assertions"][1], id="separate", signal="other"))
    data["events"].extend([
        dict(data["events"][1], signal="other", value="fault"),
        dict(data["events"][1], signal="other", value="alternative"),
    ])
    retained = tmp_path / "run.json"
    retained.write_text(json.dumps(data))
    result = evaluate(retained, hashlib.sha256(retained.read_bytes()).hexdigest(), EVALUATED_AT)
    assert result.hypothesis == "INCONCLUSIVE"


@pytest.mark.parametrize("field", ["event", "capture", "window", "evaluation"])
def test_nonzero_utc_offset_is_rejected(tmp_path: Path, field: str) -> None:
    data = json.loads(FIXTURE.read_text())
    evaluated_at = EVALUATED_AT
    match field:
        case "event":
            data["events"][1]["timestamp"] = "2025-01-01T09:02:00+09:00"
        case "capture":
            data["captured_at"] = "2025-01-01T09:05:00+09:00"
        case "window":
            data["window"]["start"] = "2025-01-01T09:00:00+09:00"
        case "evaluation":
            evaluated_at = "2026-01-01T09:00:00+09:00"
    retained = tmp_path / "run.json"
    retained.write_text(json.dumps(data))
    with pytest.raises(EvidenceError, match="timestamps must be UTC"):
        evaluate(retained, hashlib.sha256(retained.read_bytes()).hexdigest(), evaluated_at)
