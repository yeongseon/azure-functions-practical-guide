"""Offline guard tests; no Azure credentials or network required."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from scripts import golden_e2e_guard as guard


def context(sha: str) -> dict[str, str]:
    return {
        "GITHUB_REPOSITORY": guard.REPOSITORY,
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_WORKFLOW_REF": guard.WORKFLOW_REF,
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "TARGET_COMMIT": sha,
        "GITHUB_RUN_ID": "123",
        "GITHUB_RUN_ATTEMPT": "1",
        "TTL_HOURS": "2",
        "REGION": "koreacentral",
        "RUNNER_ENVIRONMENT": "github-hosted",
        "RUNNER_OS": "Linux",
        "AZURE_CLIENT_ID": "11111111-1111-1111-1111-111111111111",
        "AZURE_TENANT_ID": "22222222-2222-2222-2222-222222222222",
        "AZURE_SUBSCRIPTION_ID": "33333333-3333-3333-3333-333333333333",
        "AZURE_E2E_ENABLED": "true",
        "AZURE_E2E_SCOPE": "rg-azf-e2e-123-1",
    }


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True,
        env={**os.environ, "GIT_MASTER": "1"}, stderr=subprocess.DEVNULL,
    ).strip()


@pytest.fixture
def history(tmp_path: Path) -> tuple[Path, str, str]:
    # Given a local reviewed main and an unrelated side commit.
    git(tmp_path, "init", "-b", "main")
    git(tmp_path, "-c", "user.name=Test", "-c", "user.email=test@example.com",
        "commit", "--allow-empty", "-m", "main")
    main = git(tmp_path, "rev-parse", "HEAD")
    git(tmp_path, "update-ref", "refs/remotes/origin/main", main)
    git(tmp_path, "checkout", "-b", "side")
    git(tmp_path, "-c", "user.name=Test", "-c", "user.email=test@example.com",
        "commit", "--allow-empty", "-m", "side")
    return tmp_path, main, git(tmp_path, "rev-parse", "HEAD")


@pytest.mark.parametrize("sha", ["", "main", "a" * 39, "a" * 41, "g" * 40, "--help"])
def test_invalid_sha_is_blocked(history: tuple[Path, str, str], sha: str) -> None:
    root, _, _ = history
    assert "invalid-target-sha" in guard.context_errors(context(sha), root)


def test_sha_must_be_ancestor_of_main(history: tuple[Path, str, str]) -> None:
    root, main, side = history
    assert guard.context_errors(context(main), root) == []
    assert "target-not-on-main" in guard.context_errors(context(side), root)


@pytest.mark.parametrize("key,value", [
    ("GITHUB_REF", "refs/heads/side"),
    ("GITHUB_WORKFLOW_REF", guard.WORKFLOW_REF.replace("main", "side")),
    ("GITHUB_REPOSITORY", "fork/repo"),
    ("GITHUB_EVENT_NAME", "pull_request_target"),
])
def test_wrong_context_is_blocked(history: tuple[Path, str, str], key: str, value: str) -> None:
    root, main, _ = history
    env = {**context(main), key: value}
    assert "untrusted-context" in guard.context_errors(env, root)


@pytest.mark.parametrize("hours", ["0", "7", "-1", "1.5", "nan", "", "999999"])
def test_ttl_bounds(hours: str) -> None:
    assert "invalid-ttl" in guard.preflight_errors({**context("a" * 40), "TTL_HOURS": hours})


@pytest.mark.parametrize("hours", ["1", "6"])
def test_ttl_endpoints(hours: str) -> None:
    assert "invalid-ttl" not in guard.preflight_errors({**context("a" * 40), "TTL_HOURS": hours})


@pytest.mark.parametrize("key", [
    "AZURE_CLIENT_ID", "AZURE_TENANT_ID", "AZURE_SUBSCRIPTION_ID", "AZURE_E2E_ENABLED",
    "AZURE_E2E_SCOPE", "REGION", "RUNNER_ENVIRONMENT", "RUNNER_OS",
])
def test_missing_prerequisites_are_blocked(key: str) -> None:
    env = context("a" * 40)
    env.pop(key)
    assert guard.preflight_errors(env)


@pytest.mark.parametrize("content", [
    "Authorization: Bearer abc", "AccountKey=abc", "sig=abc", "ghp_" + "a" * 36,
    "person@company.invalid", "12345678-1234-4321-abcd-123456789abc",
    "https://private.azurewebsites.net", "10.1.2.3", "-----BEGIN PRIVATE KEY-----",
])
def test_scan_rejects_sensitive_content(tmp_path: Path, content: str) -> None:
    (tmp_path / "raw.json").write_text(json.dumps({"raw": content}))
    assert not guard.artifacts_safe(tmp_path)


def test_scan_rejects_symlinks_and_unknown_files(tmp_path: Path) -> None:
    (tmp_path / "raw.json").symlink_to(__file__)
    assert not guard.artifacts_safe(tmp_path)


def test_scan_decodes_json_escapes(tmp_path: Path) -> None:
    (tmp_path / "raw.json").write_text('{"raw": "Account\\u004bey=abc"}')
    assert not guard.artifacts_safe(tmp_path)


def test_workflow_privilege_boundary() -> None:
    workflow = YAML(typ="safe").load(
        (Path(__file__).resolve().parents[1] / ".github/workflows/e2e-azure.yml").read_text()
    )
    assert set(workflow["on"]) == {"workflow_dispatch"}
    assert workflow["permissions"] == {"contents": "read"}
    jobs = workflow["jobs"]
    assert set(jobs) == {"validate-context", "azure-scenario"}
    assert "permissions" not in jobs["validate-context"]
    azure = jobs["azure-scenario"]
    assert azure["permissions"] == {"contents": "read", "id-token": "write"}
    assert azure["environment"] == "azure-functions-e2e"
    assert azure["needs"] == "validate-context"
    steps = azure["steps"]
    login = next(step for step in steps if step.get("uses", "").startswith("azure/login@"))
    assert login["if"] == "success() && steps.preflight.outputs.azure_ready == 'true'"
    assert next(i for i, step in enumerate(steps) if step.get("id") == "preflight") < steps.index(login)
    for job in jobs.values():
        for step in job["steps"]:
            if "uses" in step:
                assert guard.SHA.fullmatch(step["uses"].split("@")[1])
            if step.get("uses", "").startswith("actions/checkout@"):
                assert step["with"]["persist-credentials"] is False
            if step.get("uses", "").startswith("actions/upload-artifact@"):
                assert "steps.scan.outcome == 'success'" in step["if"]


def test_blocked_cli_retains_only_safe_metadata(tmp_path: Path) -> None:
    # Given missing configuration and intentionally hostile input values.
    env = {**os.environ, **context("a" * 40), "AZURE_CLIENT_ID": "secret-value",
           "REGION": "person@company.invalid", "EVIDENCE_DIR": str(tmp_path)}
    # When the actual CLI preflight runs, it cannot reach login or Azure.
    result = subprocess.run([sys.executable, str(Path(guard.__file__)), "preflight"],
                            env=env, capture_output=True, text=True, check=False)
    record = json.loads((tmp_path / "preflight.json").read_text())
    # Then a nonzero BLOCKED harness record preserves honest NOT_RUN scenario status.
    assert result.returncode == 3
    assert record["status"] == "BLOCKED"
    assert record["scenario_execution"] == "NOT_RUN"
    assert record["raw_evidence"] == []
    assert record["azure_captured_at"] is None
    assert record["source_sha"] == "a" * 40
    assert record["github_run_id"] == "123"
    assert record["github_run_attempt"] == "1"
    assert "secret-value" not in (tmp_path / "preflight.json").read_text()
    derived = json.loads((tmp_path / "evaluation.json").read_text())
    assert derived["execution"] == "BLOCKED"
    assert derived["hypothesis"] == "NOT_TESTED"
    assert guard.artifacts_safe(tmp_path)


def test_placeholder_blocks_even_configured_preflight() -> None:
    assert guard.preflight_errors(context("a" * 40)) == ["scenario-not-implemented"]


def test_cleanup_refuses_unexpected_ownership(tmp_path: Path) -> None:
    (tmp_path / "created-resources.json").write_text("[]")
    assert guard.cleanup(tmp_path, context("a" * 40)) == 3
    assert json.loads((tmp_path / "cleanup.json").read_text())["status"] == "BLOCKED"


def test_cleanup_of_inert_run_has_receipt(tmp_path: Path) -> None:
    assert guard.cleanup(tmp_path, context("a" * 40)) == 0
    receipt = json.loads((tmp_path / "cleanup.json").read_text())
    assert receipt["status"] == "NO_RESOURCES_CREATED"
    assert receipt["deleted"] == []


def test_wrong_ref_test_kills_disabled_check(tmp_path: Path) -> None:
    # Given a temporary mutant with the context comparison disabled.
    source = Path(guard.__file__).read_text()
    mutant = source.replace("if observed != expected:", "if False:")
    assert mutant != source
    (tmp_path / "mutant.py").write_text(mutant)
    (tmp_path / "test_mutant.py").write_text(
        "from mutant import context_errors\n"
        "from pathlib import Path\n"
        "def test_wrong_ref():\n"
        "    assert 'untrusted-context' in context_errors({}, Path('.'))\n"
    )
    # When the same rejection assertion runs under pytest against the mutant.
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", str(tmp_path / "test_mutant.py")],
                            capture_output=True, text=True, check=False)
    # Then the regression test fails rather than accepting the weakened boundary.
    assert result.returncode == 1
    assert "1 failed" in result.stdout
