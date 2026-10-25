"""Offline regressions for issue #150; not a live language-support scraper.

Run after installing requirements-docs.txt:
    python -m unittest discover -s scripts -p test_python_runtime_docs.py
"""

import re
import unittest
from pathlib import Path
from typing import Final
from xml.etree import ElementTree

import markdown

ROOT: Final = Path(__file__).resolve().parents[1]
PYTHON: Final = ROOT / "docs/language-guides/python"


class PythonRuntimeDocsTests(unittest.TestCase):
    def test_comparison_renders_all_rows_in_one_five_column_table(self) -> None:
        # Given the actual chooser section (including notes after its table).
        source = (PYTHON / "tutorial/index.md").read_text(encoding="utf-8")
        section = source.split("## Plan Comparison at a Glance\n", 1)[1].split(
            "\n## Network Architecture by Plan", 1
        )[0]
        # When Python-Markdown renders it, as in MkDocs.
        html = markdown.markdown(section, extensions=["tables"])
        tables: list[str] = re.findall(r"<table>.*?</table>", html, flags=re.DOTALL)
        # Then no note splits the table or becomes a phantom row.
        self.assertEqual(len(tables), 1)
        table = ElementTree.fromstring(tables[0])
        self.assertEqual(len(table.findall("./thead/tr/th")), 5)
        rows = table.findall("./tbody/tr")
        labels = ["".join(row[0].itertext()) for row in rows]
        self.assertEqual(labels, [
            "Scale to zero", "VNet integration", "Private endpoints", "Python OS",
            "Deployment content", "Kudu / SCM", "Pricing model",
        ])
        self.assertTrue(all(len(row.findall("td")) == 5 for row in rows))

    def test_runtime_table_marks_314_ga_with_documented_support_end(self) -> None:
        # Given the Python runtime page.
        source = (PYTHON / "python-runtime.md").read_text(encoding="utf-8")
        # When its version table is rendered.
        html = markdown.markdown(source, extensions=["tables"])
        tables: list[str] = re.findall(r"<table>.*?</table>", html, flags=re.DOTALL)
        table = ElementTree.fromstring(tables[0])
        # Then the known stale preview row cannot return.
        rows = [["".join(cell.itertext()) for cell in row] for row in table.findall("./tbody/tr")]
        self.assertIn(["3.14", "✅ GA", "April 2029"], rows)
        self.assertFalse(any(row[0] == "3.10" for row in rows))

    def test_known_contradictory_support_claims_stay_absent(self) -> None:
        # Given only the runtime, chooser, and first-deploy pages in this fix.
        paths = [PYTHON / "python-runtime.md", PYTHON / "tutorial/index.md"]
        paths.extend((PYTHON / "tutorial").glob("*/02-first-deploy.md"))
        stale = (
            r"3\.14\s*\(?Preview",
            r"3\.10[–-]3\.12",
            r"3\.10[–-]3\.13",
            r"Remote build support for Python 3\.14 is not yet available",
            r"Windows is also supported on Consumption; this track",
        )
        # When checked against the specific contradictions from issue #150.
        for path in paths:
            source = path.read_text(encoding="utf-8")
            # Then no historical support restriction is presented as current.
            for pattern in stale:
                with self.subTest(path=path, pattern=pattern):
                    self.assertNotRegex(source, pattern)

    def test_deployment_pages_link_to_shared_runtime_guidance(self) -> None:
        # Given each plan's first deployment page.
        for plan in ("consumption", "flex-consumption", "premium", "dedicated"):
            source = (PYTHON / f"tutorial/{plan}/02-first-deploy.md").read_text(encoding="utf-8")
            # When resolving its runtime/build guidance links.
            links = re.findall(r"\]\(([^)]+)\)", source)
            # Then all tracks reach the same maintained support and build rules.
            with self.subTest(plan=plan):
                self.assertIn("../../python-runtime.md#supported-python-versions", links)
                self.assertIn("../../python-runtime.md#build-mode-and-version-availability", links)


if __name__ == "__main__":
    _ = unittest.main()
