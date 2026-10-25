"""Check retained reproduction records, not Azure authenticity or human approval.

Like evidence_eval, evaluate(path, independently_pinned_sha256, evaluated_at)
reads exact bytes and ignores stored result fields. MET means the supplied
records meet structural independence requirements; synthetic stays synthetic.
Human review must establish genuine operator identity and collection provenance.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal, TypeAlias

from scripts.lib.evidence_eval import (
    JSON,
    EvidenceError,
    _mapping,
    _sequence,
    _text,
    _time,
)

Independence: TypeAlias = Literal["MET", "NOT_MET", "NOT_TESTED"]


@dataclass(frozen=True, slots=True)
class ReproductionResult:
    independence: Independence
    synthetic: bool
    reasons: tuple[str, ...]
    evidence_path: str
    evidence_sha256: str
    evaluated_at: str


@dataclass(frozen=True, slots=True)
class Run:
    run_id: str
    scenario_id: str
    recipe_revision: str
    operator_id: str
    operator_kind: str
    mode: str
    captured_at: datetime
    collection_window: tuple[datetime, datetime] | None
    package: Path
    raw_paths: frozenset[Path]
    raw_digests: frozenset[str]
    provenance_present: bool


def _retained_path(root: Path, value: JSON) -> Path:
    path = (root / _text(value)).resolve(strict=True)
    if not path.is_relative_to(root):
        raise EvidenceError("reference escapes retained comparison directory")
    return path


def _run(value: JSON, root: Path, synthetic: bool) -> Run:
    data = _mapping(value)
    identity = {key: _text(data[key]) for key in
                ("run_id", "scenario_id", "recipe_revision", "operator_id", "operator_kind", "mode")}
    if re.fullmatch(r"operator-[a-z0-9]+(?:-[a-z0-9]+)*", identity["operator_id"]) is None:
        raise EvidenceError("non-canonical operator token")
    if identity["operator_kind"] not in {"human", "ci", "ai"}:
        raise EvidenceError("unsupported operator kind")
    if identity["mode"] not in {"human-run", "automation-rerun", "offline-reevaluation"}:
        raise EvidenceError("unsupported collection mode")
    _text(data["environment"])
    _text(data["runtime"])
    captured_at = _time(data["captured_at"])
    package = _retained_path(root, data["package"])
    if not package.is_dir():
        raise EvidenceError("retained package must be a directory")
    raw_paths, raw_digests = set(), set()
    for item in _sequence(data["raw"]):
        reference = _mapping(item)
        path = _retained_path(root, reference["path"])
        digest = _text(reference["sha256"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise EvidenceError("raw evidence digest mismatch")
        raw_paths.add(path)
        raw_digests.add(digest)
    if not raw_paths:
        raise EvidenceError("raw collection must not be empty")
    collection_window = None
    if data.get("window_evidence") is not None:
        window_path = _retained_path(root, data["window_evidence"])
        window = _mapping(json.loads(window_path.read_bytes()))
        if window.get("run_id") != identity["run_id"] or window.get("raw") != data["raw"]:
            raise EvidenceError("collection window does not bind to retained raw collection")
        if window.get("synthetic") is not synthetic or not window_path.is_relative_to(package):
            raise EvidenceError("collection window scope mismatch")
        start, end = _time(window["start"]), _time(window["end"])
        if start > end or end > captured_at:
            raise EvidenceError("invalid collection window")
        collection_window = (start, end)
    provenance_present = bool(data.get("operator_provenance"))
    if provenance_present:
        receipt_path = _retained_path(root, data["operator_provenance"])
        receipt = _mapping(json.loads(receipt_path.read_bytes()))
        binding = {key: data[key] for key in
                   ("operator_id", "operator_kind", "run_id", "mode", "captured_at")}
        if any(receipt.get(key) != value for key, value in binding.items()):
            raise EvidenceError("operator provenance does not bind to collection")
        if receipt.get("synthetic") is not synthetic:
            raise EvidenceError("operator provenance synthetic label mismatch")
    return Run(**identity, captured_at=captured_at, collection_window=collection_window, package=package,
               raw_paths=frozenset(raw_paths), raw_digests=frozenset(raw_digests),
               provenance_present=provenance_present)


def _reasons(first: Run, second: Run) -> tuple[str, ...]:
    checks = (
        (first.run_id == second.run_id, "reused run identity"),
        (bool(first.raw_paths & second.raw_paths), "reused raw evidence path"),
        (bool(first.raw_digests & second.raw_digests), "reused raw evidence digest"),
        (not (first.provenance_present and second.provenance_present), "missing operator provenance"),
        (first.operator_id == second.operator_id, "same operator"),
        (not all(run.operator_kind == "human" and run.mode == "human-run"
                 for run in (first, second)), "not two human collections"),
        ((first.scenario_id, first.recipe_revision) != (second.scenario_id, second.recipe_revision),
         "different scenario or recipe revision"),
        (first.captured_at == second.captured_at, "reused capture timestamp"),
        (first.collection_window is None or second.collection_window is None,
         "missing collection window"),
        (first.collection_window is not None and first.collection_window == second.collection_window,
         "reused collection window"),
        (first.package == second.package, "reused retained package"),
        (any(not path.is_relative_to(run.package) for run in (first, second)
             for path in run.raw_paths), "raw evidence outside run package"),
    )
    return tuple(reason for rejected, reason in checks if rejected)


def evaluate(path: Path, expected_sha256: str, evaluated_at: str) -> ReproductionResult:
    """Compute independence separately from hypothesis; reject unsupported claims.

    References resolve under the comparison directory; digests are checked against
    retained raw bytes. Receipts must bind operator, run, mode, time and synthetic
    scope. Neither a receipt nor a digest authenticates the person or Azure run.
    Missing second run is NOT_TESTED; failed independence criteria are NOT_MET.
    Malformed/missing retained files raise EvidenceError, never return MET.
    """
    try:
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != expected_sha256:
            raise EvidenceError("retained comparison digest mismatch")
        data = _mapping(json.loads(raw))
        synthetic = data["synthetic"]
        if type(synthetic) is not bool:
            raise EvidenceError("synthetic must be an explicit boolean")
        root = path.resolve().parent
        first = _run(data["original"], root, synthetic)
        clock = _time(evaluated_at)
        if first.captured_at > clock:
            raise EvidenceError("evaluation predates capture")
        state: Independence = "NOT_TESTED"
        reasons = ("no second collection",)
        if data.get("reproduction") is not None:
            second = _run(data["reproduction"], root, synthetic)
            if second.captured_at > clock:
                raise EvidenceError("evaluation predates capture")
            reasons = _reasons(first, second)
            state = "NOT_MET" if reasons else "MET"
        if data.get("claim") == "independent-human-reproduction" and (synthetic or state != "MET"):
            raise EvidenceError("unsupported independent human claim")
        return ReproductionResult(state, synthetic, reasons, str(path.resolve()), digest, evaluated_at)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        raise EvidenceError(f"cannot evaluate reproduction records: {exc}") from exc
