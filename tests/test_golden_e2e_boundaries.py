"""Offline artifact and workflow trust-boundary regressions."""

import re
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from scripts import golden_e2e_guard as guard


def test_scan_accepts_safe_json(tmp_path: Path) -> None:
    (tmp_path / "raw.json").write_text('{"raw": "safe"}')
    assert guard.artifacts_safe(tmp_path)


def test_scan_rejects_symlink_to_safe_json(tmp_path: Path) -> None:
    target = tmp_path / "raw.json"
    target.write_text('{"raw": "safe"}')
    (tmp_path / "linked.json").symlink_to(target)
    assert not guard.artifacts_safe(tmp_path)


def test_scan_rejects_unsupported_extension_with_safe_json(tmp_path: Path) -> None:
    (tmp_path / "raw.txt").write_text('{"raw": "safe"}')
    assert not guard.artifacts_safe(tmp_path)


@pytest.mark.parametrize("raw", [b'{"raw":', b'\xff\xfe\x00'])
def test_scan_rejects_malformed_or_binary_json(tmp_path: Path, raw: bytes) -> None:
    (tmp_path / "raw.json").write_bytes(raw)
    assert not guard.artifacts_safe(tmp_path)


@pytest.mark.parametrize("raw", [
    '{"raw":"AccountKey=abc","raw":"safe"}',
    '{"raw":"Account\\u004bey=abc","raw":"safe"}',
    '{"nested":{"raw":"Account\\u004bey=abc","raw":"safe"}}',
])
def test_scan_rejects_shadowed_sensitive_values(tmp_path: Path, raw: str) -> None:
    (tmp_path / "raw.json").write_text(raw)
    assert not guard.artifacts_safe(tmp_path)


def test_workflow_privilege_boundary() -> None:
    source = (Path(__file__).resolve().parents[1] / ".github/workflows/e2e-azure.yml").read_text()
    workflow = YAML(typ="safe").load(source)
    assert all("${{" not in line for line in source.splitlines()
               if re.match(r"\s*(?:-\s*)?run:", line))
    assert set(workflow["on"]) == {"workflow_dispatch"}
    assert workflow["permissions"] == {"contents": "read"}
    jobs = workflow["jobs"]
    assert set(jobs) == {"validate-context", "azure-scenario"}
    trusted = jobs["validate-context"]
    assert "permissions" not in trusted
    assert trusted["outputs"]["sha"] == "${{ steps.context.outputs.sha }}"
    checkout = next(step for step in trusted["steps"]
                    if step.get("uses", "").startswith("actions/checkout@"))
    assert checkout["with"]["repository"] == "yeongseon/azure-functions-practical-guide"
    assert checkout["with"]["ref"] == "refs/heads/main"
    azure = jobs["azure-scenario"]
    assert azure["if"] == (
        "github.repository == 'yeongseon/azure-functions-practical-guide' && "
        "github.ref == 'refs/heads/main' && "
        "github.workflow_ref == 'yeongseon/azure-functions-practical-guide/"
        ".github/workflows/e2e-azure.yml@refs/heads/main'"
    )
    assert azure["permissions"] == {"contents": "read", "id-token": "write"}
    assert azure["environment"] == "azure-functions-e2e"
    assert azure["needs"] == "validate-context"
    steps = azure["steps"]
    checkout = next(step for step in steps if step.get("uses", "").startswith("actions/checkout@"))
    assert checkout["with"]["ref"] == "${{ needs.validate-context.outputs.sha }}"
    login = next(step for step in steps if step.get("uses", "").startswith("azure/login@"))
    assert login["if"] == "success() && steps.preflight.outputs.azure_ready == 'true'"
    assert next(i for i, step in enumerate(steps) if step.get("id") == "preflight") < steps.index(login)
    for job in jobs.values():
        for step in job["steps"]:
            assert "${{" not in step.get("run", "")
            if "uses" in step:
                assert guard.SHA.fullmatch(step["uses"].split("@")[1])
            if step.get("uses", "").startswith("actions/checkout@"):
                assert step["with"]["persist-credentials"] is False
                assert step["with"]["fetch-depth"] == 0
            if step.get("uses", "").startswith("actions/upload-artifact@"):
                assert "steps.scan.outcome == 'success'" in step["if"]
