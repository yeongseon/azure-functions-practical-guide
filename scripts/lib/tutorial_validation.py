"""Offline tutorial metadata audit, never an attestation of Azure provenance."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TypeAlias

import yaml

YAMLValue: TypeAlias = (
    Mapping[str, "YAMLValue"]
    | list["YAMLValue"]
    | str
    | int
    | float
    | bool
    | date
    | None
)
STALENESS_DAYS = 90
METHODS = ("az_cli", "bicep")


class MetadataLoader(yaml.SafeLoader):
    """Retain malformed YAML date scalars so the audit can report them."""


MetadataLoader.add_constructor(
    "tag:yaml.org,2002:timestamp", yaml.SafeLoader.construct_yaml_str
)


@dataclass(frozen=True, slots=True)
class MethodAssessment:
    result: str
    last_tested: str
    freshness: str
    tools: str
    binding: str
    trust: str = "unverified"


def evidence_binding(data: Mapping[str, YAMLValue], root: Path) -> str:
    """Resolve optional run-note locators without treating existence as proof."""
    reference = data.get("evidence_ref")
    run_id = data.get("run_id")
    if not reference:
        return "No run/environment/artifact binding retained in metadata"
    if (
        not isinstance(reference, str)
        or not isinstance(run_id, str)
        or not run_id.strip()
    ):
        return "Evidence-reference mismatch: missing run identity"
    filename, _, anchor = reference.partition("#")
    path = (root / filename).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        return "Evidence-reference mismatch: absent or outside repository"
    text = path.read_text(encoding="utf-8")
    headings = re.findall(r"^#+\s+(.+)$", text, re.MULTILINE)
    slugs = {
        re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-")
        for heading in headings
    }
    if (anchor and anchor not in slugs) or not re.search(
        rf"(?m)^\s*run_id:\s*{re.escape(run_id)}\s*$", text
    ):
        return "Evidence-reference mismatch: anchor or run identity"
    return f"{reference} (run {run_id}); method/environment/artifacts require review"


def assess_method(value: YAMLValue, as_of: date, root: Path) -> MethodAssessment:
    """Keep reported outcome, date freshness, and evidence trust independent."""
    if value is None:
        return MethodAssessment(
            "no_data", "—", "unknown", "unknown", "No method record"
        )
    if not isinstance(value, dict):
        return MethodAssessment(
            "invalid", "—", "invalid", "unknown", "Malformed method record"
        )
    result = str(value.get("result", "invalid"))
    raw_date = value.get("last_tested")
    stamp = str(raw_date) if raw_date is not None else "—"
    tools = (
        "; ".join(
            f"{key}={value[key]}"
            for key in ("cli_version", "core_tools_version")
            if value.get(key)
        )
        or "unknown"
    )
    binding = evidence_binding(value, root)
    if result == "not_tested" and raw_date is None:
        return MethodAssessment(result, stamp, "NOT_RUN", tools, binding)
    if result == "syntax_validated":
        return MethodAssessment(result, stamp, "static-only", tools, binding)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", stamp):
        return MethodAssessment(result, stamp, "invalid", tools, binding)
    try:
        tested = date.fromisoformat(str(raw_date))
    except ValueError:
        return MethodAssessment(result, stamp, "invalid", tools, binding)
    if tested > as_of or result not in {"pass", "fail"}:
        return MethodAssessment(result, stamp, "invalid", tools, binding)
    freshness = "stale" if (as_of - tested).days > STALENESS_DAYS else "fresh"
    return MethodAssessment(result, stamp, freshness, tools, binding)


@dataclass(frozen=True, slots=True)
class Tutorial:
    rel_path: str
    language: str
    plan: str
    title: str
    validation: dict[str, YAMLValue]
    root: Path


def extract_tutorial_info(filepath: Path, docs_dir: Path) -> Tutorial:
    """Read existing method records without rewriting historical frontmatter."""
    text = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    metadata = yaml.load(match[1], Loader=MetadataLoader) if match else {}
    validation = (
        metadata.get("validation", {})
        if isinstance(metadata, dict)
        else "Malformed frontmatter"
    )
    if not isinstance(validation, dict):
        validation = {method: "Malformed validation container" for method in METHODS}
    else:
        validation = {
            method: ("Malformed method record" if value is None else value)
            for method, value in validation.items()
        }
    rel = filepath.relative_to(docs_dir)
    return Tutorial(
        rel.as_posix(),
        rel.parts[1],
        rel.parts[3],
        filepath.stem.replace("-", " ").title(),
        validation,
        docs_dir.parent,
    )


def tutorial_status(methods: list[MethodAssessment]) -> str:
    """Summarize historical claims conservatively; method rows retain detail."""
    if any(method.freshness == "invalid" for method in methods):
        return "Invalid metadata"
    if any(method.result == "fail" for method in methods):
        return "Failed claim"
    if any(method.freshness == "stale" for method in methods):
        return "Stale pass claim"
    if any(
        method.result == "pass" and method.freshness == "fresh" for method in methods
    ):
        return "Fresh pass claim"
    return "Not tested / no data"
