"""Focused positive-glob selection checks, not a replacement Actions classifier."""

import shutil
import subprocess
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Final

import pytest
import yaml

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
    matches = any(fnmatchcase(path, pattern) for pattern in patterns)
    # Then relevant build inputs select CI while unrelated prose/languages do not.
    assert matches is selected


@pytest.mark.parametrize("empty_file", [False, True])
def test_node_runner_rejects_zero_tests(tmp_path: Path, empty_file: bool) -> None:
    # Given a test directory with no actual node:test cases.
    test_dir = tmp_path / "test"
    test_dir.mkdir()
    shutil.copyfile(ROOT / "apps/nodejs/test/run.cjs", test_dir / "run.cjs")
    if empty_file:
        (test_dir / "empty.test.js").write_text("", encoding="utf-8")
    # When the same runner used by npm test executes it.
    result = subprocess.run(
        ["node", "test/run.cjs"], cwd=tmp_path, capture_output=True, check=False,
    )
    # Then neither missing files nor an empty suite can report success.
    assert result.returncode == 1
