"""Narrow offline replay of retained JSON, not proof of Azure provenance.

Call evaluate(path, independently_retained_sha256, evaluated_at), then
write_result(new_path, result). The input bundles predeclared assertions, execution
notes and sanitized events. A digest detects changes, not fabricated captures.
Only explicit string equality and counter-equality are supported; absence is
never counter-evidence. No claim level or tutorial validation date is assigned.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal, TypeAlias

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
Hypothesis: TypeAlias = Literal["SUPPORTED", "CONTRADICTED", "INCONCLUSIVE", "NOT_TESTED"]
Execution: TypeAlias = Literal["COMPLETE", "PARTIAL", "BLOCKED", "FAILED", "NOT_RUN"]


class EvidenceError(ValueError):
    """Retained input cannot safely be evaluated."""


@dataclass(frozen=True, slots=True)
class Assertion:
    identifier: str
    role: str
    signal: str
    expected: str
    counter: str


@dataclass(frozen=True, slots=True)
class Event:
    run_id: str
    timestamp: datetime
    signal: str
    value: str


@dataclass(frozen=True, slots=True)
class AssertionResult:
    identifier: str
    status: str
    event_indexes: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class Evaluation:
    run_id: str
    evidence_path: str
    evidence_sha256: str
    captured_at: str
    evaluated_at: str
    execution: Execution
    hypothesis: Hypothesis
    assertions: tuple[AssertionResult, ...]
    evaluation_mode: str = "offline-replay"


def _mapping(value: JSON) -> dict[str, JSON]:
    if not isinstance(value, dict):
        raise EvidenceError("expected a JSON object")
    return value


def _text(value: JSON) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceError("expected a nonempty string")
    return value


def _time(value: JSON) -> datetime:
    stamp = datetime.fromisoformat(_text(value).replace("Z", "+00:00"))
    if stamp.utcoffset() != timedelta(0):
        raise EvidenceError("timestamps must be UTC")
    return stamp


def _sequence(value: JSON) -> list[JSON]:
    if not isinstance(value, list):
        raise EvidenceError("expected a JSON array")
    return value


def _execution(value: JSON) -> Execution:
    notes = _mapping(value)
    flags = [notes[key] for key in ("attempted", "blocked", "failed", "finished")]
    if not all(type(flag) is bool for flag in flags):
        raise EvidenceError("execution flags must be booleans")
    attempted, blocked, failed, finished = flags
    if blocked:
        return "BLOCKED"
    if not attempted:
        if failed or finished:
            raise EvidenceError("unattempted run cannot fail or finish")
        return "NOT_RUN"
    if failed:
        return "FAILED"
    return "COMPLETE" if finished else "PARTIAL"


def _assertion(value: JSON) -> Assertion:
    data = _mapping(value)
    if data["predicate"] != "equals":
        raise EvidenceError("unsupported predicate")
    role = _text(data["role"])
    if role not in {"symptom", "supporting", "discriminating", "control", "recovery"}:
        raise EvidenceError("unsupported evidence role")
    expected, counter = _text(data["expected"]), _text(data["counter"])
    if expected == counter:
        raise EvidenceError("expected and counter must differ")
    return Assertion(_text(data["id"]), role, _text(data["signal"]), expected, counter)


def _event(value: JSON) -> Event:
    data = _mapping(value)
    return Event(_text(data["run_id"]), _time(data["timestamp"]),
                 _text(data["signal"]), _text(data["value"]))


def _check(assertion: Assertion, events: tuple[tuple[int, Event], ...]) -> AssertionResult:
    matches = tuple((index, event) for index, event in events if event.signal == assertion.signal)
    values = {event.value for _, event in matches}
    status = "INCONCLUSIVE"
    if values == {assertion.expected}:
        status = "SUPPORTED"
    if values == {assertion.counter}:
        status = "CONTRADICTED"
    return AssertionResult(assertion.identifier, status, tuple(index for index, _ in matches))


def _hypothesis(assertions: tuple[Assertion, ...],
                results: tuple[AssertionResult, ...]) -> Hypothesis:
    controls = [result for assertion, result in zip(assertions, results)
                if assertion.role == "control"]
    discriminators = [result for assertion, result in zip(assertions, results)
                     if assertion.role == "discriminating"]
    if not controls or not discriminators or any(r.status != "SUPPORTED" for r in controls):
        return "INCONCLUSIVE"
    if any(r.status == "INCONCLUSIVE" for r in results):
        return "INCONCLUSIVE"
    decisive = {r.status for r in discriminators}
    if decisive == {"CONTRADICTED"}:
        return "CONTRADICTED"
    if all(r.status == "SUPPORTED" for r in results):
        return "SUPPORTED"
    return "INCONCLUSIVE"


def evaluate(path: Path, expected_sha256: str, evaluated_at: str) -> Evaluation:
    """Recompute from exact retained bytes; supplied verdict/PASS fields are ignored.

    The caller must pin the digest independently of the input. Malformed inputs
    raise EvidenceError; absent/empty events remain inconclusive on COMPLETE runs.
    Event references are zero-based indexes in the retained events array.
    """
    try:
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != expected_sha256:
            raise EvidenceError("retained evidence digest mismatch")
        data = _mapping(json.loads(raw))
        run_id = _text(data["run_id"])
        captured_at = _text(data["captured_at"])
        if _time(evaluated_at) < _time(captured_at):
            raise EvidenceError("evaluation predates capture")
        window = _mapping(data["window"])
        start, end = _time(window["start"]), _time(window["end"])
        if start > end or end > _time(captured_at):
            raise EvidenceError("invalid capture window")
        execution = _execution(data["execution"])
        assertions = tuple(_assertion(value) for value in _sequence(data["assertions"]))
        if not assertions or len({a.identifier for a in assertions}) != len(assertions):
            raise EvidenceError("assertions need unique IDs and must not be empty")
        events = tuple(_event(value) for value in _sequence(data.get("events", [])))
        scoped = tuple((index, event) for index, event in enumerate(events)
                       if event.run_id == run_id and start <= event.timestamp <= end)
        results = tuple(_check(assertion, scoped) for assertion in assertions)
        hypothesis = _hypothesis(assertions, results) if execution == "COMPLETE" else "NOT_TESTED"
        return Evaluation(run_id, str(path.resolve()), digest, captured_at, evaluated_at,
                          execution, hypothesis, results)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        raise EvidenceError(f"cannot evaluate retained evidence: {exc}") from exc


def write_result(path: Path, result: Evaluation) -> None:
    """Exclusively create a derived file, never replace any existing file or symlink."""
    payload = json.dumps(asdict(result), indent=2, sort_keys=True) + "\n"
    with path.open("x", encoding="utf-8") as output:
        output.write(payload)
