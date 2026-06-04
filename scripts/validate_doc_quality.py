#!/usr/bin/env python3
"""Validate documentation quality rules for changed Markdown files.

This gate is intentionally change-scoped by default. The repositories already
contain historical content debt, so PRs should block new regressions without
making every existing issue a permanent CI failure.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - CI installs pyyaml.
    yaml = None


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

GENERIC_PHRASES = [
    "Apply the corrective configuration change described",
    "Use this step to apply the feature under test",
    "It establishes an observable checkpoint for the lab before you continue",
    "A production change affects",
    "Azure VM incidents often start with mismatched expectations",
    "Record the output and any IDs you will reuse in later steps",
]

BEST_PRACTICES_SECTIONS = [
    "Why This Matters",
    "Recommended Practices",
    "Common Mistakes / Anti-Patterns",
    "Validation Checklist",
]

OPERATIONS_SECTIONS = [
    "Prerequisites",
    "When to Use",
    "Procedure",
    "Verification",
    "Rollback / Troubleshooting",
]

TROUBLESHOOTING_SECTIONS = [
    "Symptom",
    "Possible Causes",
    "Diagnosis Steps",
    "Resolution",
    "Prevention",
]

LAB_SECTIONS = [
    "Setup",
    "Hypothesis",
    "Experiment",
    "Observation",
    "Solution",
]

SENSITIVE_CONTEXT_RE = re.compile(
    r"(subscription[-_ ]?id|tenant[-_ ]?id|object[-_ ]?id|app[-_ ]?id|"
    r"client[-_ ]?id|customer[-_ ]?id|workspace.*id)",
    re.IGNORECASE,
)
GUID_RE = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)
SUBSCRIPTION_ID_RE = re.compile(r"/subscriptions/[0-9a-fA-F-]{36}\b")
APP_INSIGHTS_KEY_RE = re.compile(r"InstrumentationKey=([0-9a-fA-F-]{36})")
SECRET_VALUE_RE = re.compile(
    r"(SharedAccessKey|AccountKey|client_secret|clientSecret|password)\s*[=:]\s*"
    r"(?!<|placeholder|xxxx|\\$|\")([^;,\s]+)",
    re.IGNORECASE,
)
ACA_HOST_RE = re.compile(
    r"https://[a-z0-9-]+\.[a-z0-9-]+\.koreacentral\.azurecontainerapps\.io",
    re.IGNORECASE,
)
AZ_SHORT_FLAG_RE = re.compile(r"(?<!\S)(-g|-n|-o|-l)(?![A-Za-z0-9_-])")


@dataclass
class Finding:
    path: Path
    line: int
    message: str


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def line_of(text: str, offset: int) -> int:
    return text[:offset].count("\n") + 1


def add(finding_list: list[Finding], path: Path, line: int, message: str) -> None:
    finding_list.append(Finding(path=path, line=max(1, line), message=message))


def load_frontmatter(text: str) -> tuple[dict[str, Any], int]:
    if not text.startswith("---\n"):
        return {}, 1
    lines = text.splitlines()
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            raw = "\n".join(lines[1:index])
            if yaml is None:
                return {}, index + 2
            data = yaml.safe_load(raw) or {}
            return (data if isinstance(data, dict) else {}), index + 2
    return {}, 1


def changed_markdown_files(base_ref: str) -> list[Path]:
    cmd = ["git", "diff", "--name-only", base_ref, "--", "docs"]
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        print(
            f"warning: could not diff against {base_ref!r}; no changed docs checked",
            file=sys.stderr,
        )
        print(result.stderr.strip(), file=sys.stderr)
        return []
    files: list[Path] = []
    for item in result.stdout.splitlines():
        path = ROOT / item
        if path.suffix == ".md" and path.exists():
            files.append(path)
    return files


def all_markdown_files() -> list[Path]:
    return sorted(DOCS.rglob("*.md"))


def iter_code_fences(text: str):
    lines = text.splitlines()
    in_fence = False
    start = 0
    lang = ""
    indent = 0
    body: list[str] = []
    for number, line in enumerate(lines, 1):
        stripped = line.lstrip()
        line_indent = len(line) - len(stripped)
        if stripped.startswith("```"):
            if not in_fence:
                in_fence = True
                start = number
                indent = line_indent
                lang = stripped[3:].strip()
                body = []
            elif line_indent == indent:
                yield start, number, lang, "\n".join(body), lines
                in_fence = False
        elif in_fence:
            body.append(line)


def has_table_near(lines: list[str], start: int, end: int) -> bool:
    begin = max(0, start - 10)
    finish = min(len(lines), end + 25)
    window = lines[begin:finish]
    for index in range(len(window) - 1):
        if window[index].lstrip().startswith("|") and re.search(
            r"\|\s*:?-{3,}:?\s*\|", window[index + 1]
        ):
            return True
    return False


def headings(text: str) -> dict[str, int]:
    found: dict[str, int] = {}
    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(r"^##\s+(?:\d+[.)]\s*)?(.+?)\s*$", line)
        if match:
            found[match.group(1).strip()] = number
    return found


def section_body(text: str, heading_name: str) -> tuple[int, str] | None:
    pattern = re.compile(rf"^##\s+(?:\d+[.)]\s*)?{re.escape(heading_name)}\s*$", re.M)
    match = pattern.search(text)
    if not match:
        return None
    next_heading = re.search(r"^##\s+", text[match.end() :], re.M)
    end = match.end() + next_heading.start() if next_heading else len(text)
    return line_of(text, match.start()), text[match.end() : end].strip()


def is_index(path: Path) -> bool:
    return path.name == "index.md"


def should_skip_policy(path: Path) -> bool:
    relative = rel(path)
    return relative.startswith("docs/contributing/")


def require_sections(
    findings: list[Finding], path: Path, text: str, names: list[str], label: str
) -> None:
    found = headings(text)
    for name in names:
        if name not in found:
            add(findings, path, 1, f"{label} document is missing required section '## {name}'")


def validate_tail_sections(findings: list[Finding], path: Path, text: str) -> None:
    if should_skip_policy(path) or "docs/reference/content-validation-status.md" == rel(path):
        return
    if "docs/reference/validation-status.md" == rel(path):
        return
    see = re.search(r"^## See Also\s*$", text, re.M)
    sources = re.search(r"^## Sources\s*$", text, re.M)
    if not see:
        add(findings, path, 1, "document is missing final '## See Also' section")
    if not sources:
        add(findings, path, 1, "document is missing final '## Sources' section")
    if see and sources and see.start() > sources.start():
        add(findings, path, line_of(text, sources.start()), "'## See Also' must appear before '## Sources'")


def validate_templates(findings: list[Finding], path: Path, text: str) -> None:
    if should_skip_policy(path) or is_index(path):
        return
    parts = path.relative_to(ROOT).parts
    if len(parts) < 3 or parts[0] != "docs":
        return
    section = parts[1]
    if section == "best-practices":
        require_sections(findings, path, text, BEST_PRACTICES_SECTIONS, "Best Practices")
    elif section == "operations":
        require_sections(findings, path, text, OPERATIONS_SECTIONS, "Operations")
    elif section == "troubleshooting" and "lab-guides" not in parts and "kql" not in parts:
        require_sections(findings, path, text, TROUBLESHOOTING_SECTIONS, "Troubleshooting")


def validate_content_validation(
    findings: list[Finding], path: Path, frontmatter: dict[str, Any], text: str
) -> None:
    if should_skip_policy(path) or is_index(path):
        return
    parts = path.relative_to(ROOT).parts
    needs_validation = len(parts) > 2 and parts[1] in {
        "platform",
        "best-practices",
        "operations",
    }
    content_validation = frontmatter.get("content_validation")
    if needs_validation and not isinstance(content_validation, dict):
        add(findings, path, 1, "platform/best-practices/operations docs require content_validation metadata")
        return
    if not isinstance(content_validation, dict):
        return
    status = content_validation.get("status")
    claims = content_validation.get("core_claims") or []
    if status == "verified":
        for claim in claims:
            if isinstance(claim, dict) and claim.get("verified") is False:
                add(findings, path, 1, "status is verified but at least one core_claim has verified: false")
                break


def diagram_metadata(frontmatter: dict[str, Any]) -> tuple[set[str], bool]:
    sources = frontmatter.get("content_sources")
    if isinstance(sources, dict):
        diagrams = sources.get("diagrams") or []
    else:
        diagrams = []
    ids = {
        item.get("id")
        for item in diagrams
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    has_top_level_diagrams = isinstance(frontmatter.get("diagrams"), list)
    return ids, has_top_level_diagrams


def validate_mermaid_metadata(
    findings: list[Finding], path: Path, text: str, frontmatter: dict[str, Any]
) -> None:
    if "```mermaid" not in text:
        return
    ids, has_top_level_diagrams = diagram_metadata(frontmatter)
    if has_top_level_diagrams:
        add(findings, path, 1, "diagram metadata must be under content_sources.diagrams, not top-level diagrams")
    if not isinstance(frontmatter.get("content_sources"), dict):
        add(findings, path, 1, "files with Mermaid diagrams require content_sources.diagrams metadata")
    lines = text.splitlines()
    for start, _end, lang, _body, _lines in iter_code_fences(text):
        if lang.strip() != "mermaid":
            continue
        nearby = "\n".join(lines[max(0, start - 4) : start - 1])
        match = re.search(r"<!--\s*diagram-id:\s*([A-Za-z0-9_.-]+)\s*-->", nearby)
        if not match:
            add(findings, path, start, "Mermaid block is missing a preceding diagram-id comment")
            continue
        diagram_id = match.group(1)
        if ids and diagram_id not in ids:
            add(findings, path, start, f"diagram-id '{diagram_id}' is missing from content_sources.diagrams")


def validate_cli_blocks(findings: list[Finding], path: Path, text: str) -> None:
    if should_skip_policy(path):
        return
    for start, end, _lang, body, lines in iter_code_fences(text):
        if not re.search(r"(^|\s)az\s+", body):
            continue
        if not has_table_near(lines, start, end):
            add(findings, path, start, "Azure CLI code block needs a nearby command explanation table")
        for offset, line in enumerate(body.splitlines(), start + 1):
            az_index = line.find("az ")
            if az_index == -1:
                continue
            az_part = line[az_index:]
            match = AZ_SHORT_FLAG_RE.search(az_part)
            if match:
                add(
                    findings,
                    path,
                    offset,
                    f"Azure CLI examples must use long flags instead of {match.group(1)}",
                )


def validate_generic_phrases(findings: list[Finding], path: Path, text: str) -> None:
    for phrase in GENERIC_PHRASES:
        start = text.find(phrase)
        if start != -1:
            add(findings, path, line_of(text, start), f"generated placeholder phrase remains: {phrase!r}")


def validate_lab_sections(findings: list[Finding], path: Path, text: str) -> None:
    if "lab-guides" not in path.parts or is_index(path):
        return
    for name in LAB_SECTIONS:
        body = section_body(text, name)
        if body is None:
            continue
        line, content = body
        meaningful = re.sub(r"<!--.*?-->", "", content, flags=re.S).strip()
        if len(meaningful) < 40:
            add(findings, path, line, f"lab section '## {name}' is empty or too thin")


def validate_file_references(findings: list[Finding], path: Path, text: str) -> None:
    ref_patterns = [
        re.compile(r"--(?:source|file)\s+(\./[^\s\\]+)"),
        re.compile(r"--policy\s+@([^\s\\]+)"),
    ]
    for start, _end, _lang, body, _lines in iter_code_fences(text):
        for pattern in ref_patterns:
            for match in pattern.finditer(body):
                ref = match.group(1).strip("\"'")
                if "$" in ref or ref.startswith("<"):
                    continue
                candidates = [path.parent / ref, ROOT / ref]
                if not any(candidate.exists() for candidate in candidates):
                    add(
                        findings,
                        path,
                        start + 1 + body[: match.start()].count("\n"),
                        f"referenced local file or directory does not exist: {ref}",
                    )


def looks_placeholder_guid(value: str) -> bool:
    lowered = value.lower()
    return (
        lowered.startswith("00000000")
        or "aaaa" in lowered
        or "bbbb" in lowered
        or "cccc" in lowered
        or "xxxx" in lowered
        or lowered == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    )


def validate_sensitive_values(findings: list[Finding], path: Path, text: str) -> None:
    for number, line in enumerate(text.splitlines(), 1):
        if SUBSCRIPTION_ID_RE.search(line):
            add(findings, path, number, "real-looking subscription ID must be replaced with <subscription-id>")
        app_key = APP_INSIGHTS_KEY_RE.search(line)
        if app_key and not looks_placeholder_guid(app_key.group(1)):
            add(findings, path, number, "Application Insights instrumentation key must be masked")
        if SECRET_VALUE_RE.search(line):
            add(findings, path, number, "secret-like value must be replaced with a placeholder")
        if ACA_HOST_RE.search(line):
            add(findings, path, number, "live-looking Container Apps hostname must be replaced with a placeholder")
        if SENSITIVE_CONTEXT_RE.search(line):
            for guid in GUID_RE.findall(line):
                if not looks_placeholder_guid(guid):
                    add(findings, path, number, "real-looking Azure identifier must be masked")
                    break


def validate_file(path: Path) -> list[Finding]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    frontmatter, _body_start = load_frontmatter(text)
    findings: list[Finding] = []
    validate_tail_sections(findings, path, text)
    validate_templates(findings, path, text)
    validate_content_validation(findings, path, frontmatter, text)
    validate_mermaid_metadata(findings, path, text, frontmatter)
    validate_cli_blocks(findings, path, text)
    validate_generic_phrases(findings, path, text)
    validate_lab_sections(findings, path, text)
    validate_file_references(findings, path, text)
    validate_sensitive_values(findings, path, text)
    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--changed-only", action="store_true", help="validate Markdown files changed from --base-ref")
    group.add_argument("--all", action="store_true", help="validate every Markdown file under docs/")
    parser.add_argument("--base-ref", default="HEAD~1", help="base ref for --changed-only")
    parser.add_argument("--files", nargs="*", help="explicit files to validate")
    parser.add_argument("--max-errors", type=int, default=200, help="maximum number of errors to print")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.files:
        files = [ROOT / item for item in args.files if item.endswith(".md")]
    elif args.all:
        files = all_markdown_files()
    else:
        files = changed_markdown_files(args.base_ref)
    files = [path for path in files if path.exists() and DOCS in path.parents]
    if not files:
        print("No documentation files to validate.")
        return 0

    findings: list[Finding] = []
    for path in files:
        findings.extend(validate_file(path))

    if not findings:
        print(f"Documentation quality gate passed for {len(files)} file(s).")
        return 0

    github_actions = os.getenv("GITHUB_ACTIONS") == "true"
    for finding in findings[: args.max_errors]:
        relative = rel(finding.path)
        if github_actions:
            print(f"::error file={relative},line={finding.line}::{finding.message}")
        else:
            print(f"{relative}:{finding.line}: error: {finding.message}")
    if len(findings) > args.max_errors:
        print(f"... {len(findings) - args.max_errors} more error(s) not shown")
    print(f"Documentation quality gate failed: {len(findings)} error(s) across {len(files)} file(s).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
