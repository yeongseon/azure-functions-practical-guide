"""Focused positive-glob selection checks, not a replacement Actions classifier."""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Final

import pytest
import yaml
from wcmatch import glob

ROOT: Final = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("workflow,path,selected", [
    ("python-eventhub-tests", "apps/python/function_app.py", True),
    ("python-eventhub-tests", "apps/python/host.json", True),
    ("python-eventhub-tests", "apps/python/requirements.txt", True),
    ("python-eventhub-tests", "apps/python/config/settings.py", True),
    ("python-eventhub-tests", "apps/nodejs/src/shared/config.js", True),
    ("python-eventhub-tests", "apps/nodejs/host.json", True),
    ("python-eventhub-tests", "apps/nodejs/package-lock.json", True),
    ("python-eventhub-tests", "tests/conftest.py", True),
    ("python-eventhub-tests", "tests/test_reference_app_ci.py", True),
    ("python-eventhub-tests", "tests/test_evidence_eval.py", True),
    ("python-eventhub-tests", "tests/fixtures/evidence/synthetic-run.json", True),
    ("python-eventhub-tests", "scripts/lib/evidence_eval.py", True),
    ("dotnet-tests", "apps/dotnet/Shared/AppConfig.cs", True),
    ("dotnet-tests", "apps/dotnet/host.json", True),
    ("dotnet-tests", "tests/dotnet/AzureFunctionsGuide.Tests.csproj", True),
    ("dotnet-tests", "global.json", True),
    ("dotnet-tests", "Directory.Build.props", True),
    ("dotnet-tests", "Directory.Packages.props", True),
    ("dotnet-tests", "NuGet.Config", True),
    ("java-tests", "apps/java/src/main/java/com/functions/HealthFunction.java", True),
    ("java-tests", "apps/java/host.json", True),
    ("java-tests", "apps/java/pom.xml", True),
    ("java-tests", "pom.xml", True),
    ("java-tests", ".mvn/maven.config", True),
    *[(workflow, f".github/workflows/{workflow}.yml", True)
      for workflow in ("python-eventhub-tests", "dotnet-tests", "java-tests")],
    *[(workflow, "docs/platform/hosting-plans.md", False)
      for workflow in ("python-eventhub-tests", "dotnet-tests", "java-tests")],
    ("dotnet-tests", "apps/java/pom.xml", False),
    ("java-tests", "apps/dotnet/Program.cs", False),
])
def test_reference_workflow_selection(workflow: str, path: str, selected: bool) -> None:
    # Given the actual workflow's native, positive path globs (BaseLoader keeps "on").
    config = yaml.load(
        (ROOT / f".github/workflows/{workflow}.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    patterns = config["on"]["pull_request"]["paths"]
    assert all(not pattern.startswith("!") for pattern in patterns)
    # When one representative changed file is matched against the configured paths.
    matches = any(glob.globmatch(path, pattern, flags=glob.GLOBSTAR | glob.DOTGLOB)
                  for pattern in patterns)
    # Then relevant build inputs select CI while unrelated prose/languages do not.
    assert matches is selected


@pytest.mark.parametrize("source,expected", [
    (None, 1),
    ("", 1),
    ("require('node:test').test.skip('skipped', () => {});", 1),
    ("require('node:test').test.todo('todo');", 1),
    ("require('node:test').test('cancelled', { timeout: 25 }, () => new Promise(() => {}));", 1),
    ("require('node:test').test('failed', () => { throw Error('failure'); });", 1),
    ("require('node:test').test('passed', () => {});", 0),
])
def test_node_runner_exit_status(tmp_path: Path, source: str | None, expected: int) -> None:
    # Given missing, unexecuted, failing, or passing node:test cases.
    test_dir = tmp_path / "test"
    test_dir.mkdir()
    shutil.copyfile(ROOT / "apps/nodejs/test/run.cjs", test_dir / "run.cjs")
    if source is not None:
        (test_dir / "sample.test.js").write_text(source, encoding="utf-8")
    # When the same runner used by npm test executes it.
    result = subprocess.run(
        ["node", "test/run.cjs"], cwd=tmp_path, capture_output=True, check=False, timeout=15,
    )
    # Then only a successful run with executed tests reports success.
    assert result.returncode == expected


def test_single_star_mutation_drops_nested_python_path() -> None:
    config = yaml.load(
        (ROOT / ".github/workflows/python-eventhub-tests.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    patterns = config["on"]["pull_request"]["paths"]
    path = "apps/python/config/settings.py"
    mutated = [pattern.replace("apps/python/**", "apps/python/*") for pattern in patterns]
    flags = glob.GLOBSTAR | glob.DOTGLOB
    assert any(glob.globmatch(path, pattern, flags=flags) for pattern in patterns)
    assert not any(glob.globmatch(path, pattern, flags=flags) for pattern in mutated)


def test_import_time_loopback_connection_is_blocked(tmp_path: Path) -> None:
    shutil.copyfile(ROOT / "tests/conftest.py", tmp_path / "conftest.py")
    (tmp_path / "test_import.py").write_text(
        "import socket\nsocket.create_connection(('127.0.0.1', 9), timeout=0.1)\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q",
         "--disable-socket", "--allow-unix-socket"],
        cwd=tmp_path, capture_output=True, text=True, check=False, timeout=15,
    )
    assert result.returncode == 2
    assert "SocketBlockedError" in result.stdout
    assert "ConnectionRefusedError" not in result.stdout
