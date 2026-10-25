# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# How to run: python scripts/golden_e2e_guard.py context|preflight|cleanup|scan
"""Fail-closed, offline-only harness. No Azure deployment or deletion is implemented."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Final

try:
    from scripts.lib.evidence_eval import evaluate, write_result
except ModuleNotFoundError:
    from lib.evidence_eval import evaluate, write_result

REPOSITORY: Final = "yeongseon/azure-functions-practical-guide"
WORKFLOW_REF: Final = f"{REPOSITORY}/.github/workflows/e2e-azure.yml@refs/heads/main"
SHA: Final = re.compile(r"[0-9a-fA-F]{40}")
UUID: Final = re.compile(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}")
# Reject rather than redact: unknown/binary artifacts must never reach upload.
SENSITIVE: Final = re.compile(
    r"(?i)(authorization|bearer\s|accountkey|connectionstring|client_secret|password|"
    r"[?&]?(?:sig|token|secret)\s*[=:]|gh[pousr]_[a-z0-9_]+|github_pat_|"
    r"-----BEGIN .*PRIVATE KEY|[\w.+-]+@[\w.-]+\.[a-z]{2,}|"
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b|"
    r"[\w.-]+\.(?:azurewebsites\.net|windows\.net|azure\.com)|"
    r"eyJ[a-z0-9_-]+\.[a-z0-9_-]+\.[a-z0-9_-]+)"
)


def context_errors(env: Mapping[str, str], root: Path) -> list[str]:
    expected = (REPOSITORY, "refs/heads/main", WORKFLOW_REF, "workflow_dispatch")
    observed = tuple(env.get(key, "") for key in (
        "GITHUB_REPOSITORY", "GITHUB_REF", "GITHUB_WORKFLOW_REF", "GITHUB_EVENT_NAME",
    ))
    errors = []
    if observed != expected:
        errors.append("untrusted-context")
    sha = env.get("TARGET_COMMIT", "")
    if not SHA.fullmatch(sha):
        errors.append("invalid-target-sha")
    else:
        result = subprocess.run(
            ["git", "-C", str(root), "merge-base", "--is-ancestor", sha, "origin/main"],
            capture_output=True, check=False, timeout=30,
            env={**os.environ, "GIT_MASTER": "1"},
        )
        if result.returncode != 0:
            errors.append("target-not-on-main")
    return errors


def preflight_errors(env: Mapping[str, str]) -> list[str]:
    errors = []
    for key in ("AZURE_CLIENT_ID", "AZURE_TENANT_ID", "AZURE_SUBSCRIPTION_ID"):
        if not UUID.fullmatch(env.get(key, "")):
            errors.append(f"missing-or-invalid-{key.lower()}")
    run = env.get("GITHUB_RUN_ID", "")
    attempt = env.get("GITHUB_RUN_ATTEMPT", "")
    if not re.fullmatch(r"[1-9][0-9]*", run) or not re.fullmatch(r"[1-9][0-9]*", attempt):
        errors.append("invalid-run-identity")
    if env.get("AZURE_E2E_ENABLED") != "true":
        errors.append("environment-not-enabled")
    if env.get("AZURE_E2E_SCOPE") != f"rg-azf-e2e-{run}-{attempt}":
        errors.append("run-scope-not-approved")
    if env.get("RUNNER_ENVIRONMENT") != "github-hosted" or env.get("RUNNER_OS") != "Linux":
        errors.append("unsupported-runner")
    hours = env.get("TTL_HOURS", "")
    if hours not in {"1", "2", "3", "4", "5", "6"}:
        errors.append("invalid-ttl")
    if env.get("REGION") not in {"koreacentral", "eastus", "westeurope"}:
        errors.append("invalid-region")
    # A configuration toggle must not turn this unfinished harness into a paid run.
    errors.append("scenario-not-implemented")
    return errors


def safe_value(value: str, pattern: str) -> str:
    return value if re.fullmatch(pattern, value) else "unknown"


def record(root: Path, env: Mapping[str, str], errors: list[str]) -> None:
    """Capture harness facts only; timestamps do not imply Azure collection."""
    root.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).isoformat()
    run = safe_value(env.get("GITHUB_RUN_ID", ""), r"[1-9][0-9]*")
    attempt = safe_value(env.get("GITHUB_RUN_ATTEMPT", ""), r"[1-9][0-9]*")
    region = env.get("REGION", "")
    hours = env.get("TTL_HOURS", "")
    payload = {
        "status": "BLOCKED" if errors else "VALIDATED_CONTEXT",
        "blockers": errors, "scenario_execution": "NOT_RUN",
        "source_sha": safe_value(env.get("TARGET_COMMIT", ""), SHA.pattern),
        "github_run_id": run, "github_run_attempt": attempt,
        "run_id": f"{run}-{attempt}", "operator_kind": "ci",
        "captured_at": now, "capture_kind": "harness-metadata-only",
        "azure_captured_at": None, "raw_evidence": [],
        "region": region if region in {"koreacentral", "eastus", "westeurope"} else "unknown",
        "planned": {"sku": "Y1", "os": "Linux", "language": "Python",
                    "programming_model": "v2", "functions_runtime": "v4"},
        "observed": {"sku": None, "os": None, "language_version": None,
                     "functions_runtime_version": None},
        "resource_group": f"rg-azf-e2e-{run}-{attempt}",
        "planned_tags": {"owner": "azf-golden", "run-id": f"{run}-{attempt}",
                         "repository": REPOSITORY,
                         "expires-at": (datetime.fromisoformat(now) + timedelta(hours=int(hours))).isoformat()
                         if hours in {"1", "2", "3", "4", "5", "6"} else None},
    }
    path = root / ("preflight.json" if "scenario-not-implemented" in errors else "context.json")
    with path.open("x", encoding="utf-8") as output:
        output.write(json.dumps(payload, indent=2) + "\n")
    scenario = json.loads((Path(__file__).resolve().parents[1] /
                           "tests/fixtures/evidence/deployment-scenario.json").read_text())
    bundle = {
        "run_id": f"{run}-{attempt}", "captured_at": now,
        "capture_kind": "harness-metadata-only", "azure_captured_at": None,
        "window": {"start": now, "end": now},
        "execution": {"attempted": False, "blocked": bool(errors), "failed": False, "finished": False},
        "assertions": scenario["assertions"], "events": [],
    }
    retained = root / "evidence.json"
    with retained.open("x", encoding="utf-8") as output:
        output.write(json.dumps(bundle, indent=2) + "\n")
    digest = hashlib.sha256(retained.read_bytes()).hexdigest()
    (root / "manifest.sha256").write_text(digest + "\n")
    write_result(root / "evaluation.json", evaluate(retained, digest, datetime.now(UTC).isoformat()))


def cleanup(root: Path, env: Mapping[str, str]) -> int:
    """No Azure resources can be created here; unexpected ledgers block deletion."""
    root.mkdir(parents=True, exist_ok=True)
    unexpected = (root / "created-resources.json").exists()
    receipt = {
        "status": "BLOCKED" if unexpected else "NO_RESOURCES_CREATED",
        "captured_at": datetime.now(UTC).isoformat(),
        "github_run_id": safe_value(env.get("GITHUB_RUN_ID", ""), r"[1-9][0-9]*"),
        "github_run_attempt": safe_value(env.get("GITHUB_RUN_ATTEMPT", ""), r"[1-9][0-9]*"),
        "deleted": [], "azure_calls": False,
        "ownership_verification": "NOT_APPLICABLE_INERT_HARNESS",
    }
    with (root / "cleanup.json").open("x", encoding="utf-8") as output:
        output.write(json.dumps(receipt, indent=2) + "\n")
    return 3 if unexpected else 0


def artifacts_safe(root: Path) -> bool:
    if not root.is_dir() or root.is_symlink():
        return False
    paths = list(root.rglob("*"))
    if not paths:
        return False
    for path in paths:
        if path.is_symlink() or not path.is_file() or path.suffix not in {".json", ".sha256"}:
            return False
        try:
            text = path.read_text(encoding="utf-8")
            if path.suffix == ".json":
                text = json.dumps(json.loads(text, object_pairs_hook=list), ensure_ascii=False)
        except (OSError, UnicodeError, ValueError):
            return False
        if UUID.search(text) or SENSITIVE.search(text) or SENSITIVE.search(path.name):
            return False
    return True


def main() -> int:
    env = os.environ
    root = Path(env["EVIDENCE_DIR"])
    match sys.argv[1:]:
        case ["context"]:
            errors = context_errors(env, Path.cwd())
            record(root, env, errors)
            if not errors:
                with Path(env["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
                    output.write(f"sha={env['TARGET_COMMIT']}\n")
            return 3 if errors else 0
        case ["preflight"]:
            errors = context_errors(env, Path.cwd()) + preflight_errors(env)
            record(root, env, errors)
            return 3
        case ["cleanup"]:
            return cleanup(root, env)
        case ["scan"]:
            return 0 if artifacts_safe(root) else 3
        case _:
            return 3


if __name__ == "__main__":
    raise SystemExit(main())
