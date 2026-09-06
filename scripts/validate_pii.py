#!/usr/bin/env python3
"""
PII / Secret Validation Script (series-wide)

Validates Markdown documentation for potential PII that must never leak into a
public guide. It is intentionally tuned for the Azure Practical Guide series,
which uses many *synthetic* example identifiers (sequential UUIDs, RFC 1918
private IP ranges, ``example.com`` / ``contoso.com`` addresses) as teaching
aids. Those must NOT trip the gate, while a real leaked identifier must.

Checks:
- UUID-shaped subscription / tenant / object identifiers  -> ERROR (blocking)
- Real email addresses outside approved safe domains       -> ERROR (blocking)
- RFC 1918 private IPv4 addresses                           -> WARN (advisory)

Private IPs are advisory by default: RFC 1918 addresses are non-routable and
non-identifying, and the series documents them heavily as examples. Pass
``--strict-private-ip`` to treat them as blocking.

A per-repository allowlist of exact values (one per line, ``#`` comments) can
be supplied via ``--allowlist`` (defaults to ``scripts/pii-allowlist.txt`` next
to this script when present). Allowlisted values are skipped for every check.

Usage:
    python scripts/validate_pii.py [--verbose]
    python scripts/validate_pii.py --files docs/a.md docs/b.md   # changed-only
    python scripts/validate_pii.py --strict-private-ip

Exit codes:
    0 - No blocking findings (advisory warnings may still be printed)
    1 - One or more blocking findings

Only Python standard library is used, so the script runs in CI without extra
dependencies.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Set, Tuple


UUID_PATTERN = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)
PRIVATE_IP_PATTERN = re.compile(
    r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})\b"
)
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")

# Placeholder/reserved domains only. Real personal/corporate domains
# (microsoft.com, outlook.com, ...) are deliberately excluded so a real address
# still trips the gate; route a genuinely-safe sample through pii-allowlist.txt.
SAFE_EMAIL_DOMAINS = {
    "example.com",
    "contoso.com",
    "yourdomain.com",
}
# RFC 2606 / 6761 reserved TLDs plus placeholder patterns used across the series.
SAFE_EMAIL_TLDS = {"example", "invalid", "test", "localhost"}
SAFE_EMAIL_DOMAIN_SUFFIXES = (".azurecomm.net",)  # ACS system sender addresses

# Documented, public Azure built-in role definition IDs. These UUIDs are global
# constants (identical in every tenant), so citing one leaks no account data.
# Source: learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles
PUBLIC_AZURE_ROLE_IDS = frozenset(
    {
        "7f951dda-4ed3-4680-a7ca-43fe172d538d",
        "8e3af657-a8ff-443c-a75c-2fe8c4bcb635",
        "b24988ac-6180-42a0-ab88-20f7382dd24c",
        "acdd72a7-3385-48ef-bd42-f606fba81ae7",
        "8311e382-0749-4cb8-b61a-304f252e45ec",
        "ba92f5b4-2d11-453d-a403-e96b0029c9fe",
        "2a2b9908-6ea1-4ae2-8e65-a410df84e7d1",
        "4633458b-17de-40c3-b3c0-e79bb2e4a2fe",
        "de139f84-1756-47ae-9be6-808fbbe84772",
        "73c42c96-874c-492b-b04d-ab87d138a893",
        "b7e6dc6d-f1e8-4753-8033-0f276bb0955b",
        "17d1049b-9a84-46fb-8f53-869881c3d3ab",
        "3913510d-42f4-4e42-8a64-420c390055eb",
        "749f88d5-cbae-40b8-bcfc-e573ddc772fa",
        "43d0d8ad-25c7-4714-9337-8ba259a9fe05",
    }
)

TENANT_KEYWORDS = ("tenant", "tenantid", "tenant-id", "--tenant")
OBJECT_KEYWORDS = ("object id", "objectid", "object-id", "principal id", "principalid")
FENCED_CODE_PATTERN = re.compile(r"^```([A-Za-z0-9_-]+)?\s*$")
HEX_SEQUENCE = "0123456789abcdef"


def _has_sequential_run(compact: str, length: int = 6) -> bool:
    """Return True if ``compact`` contains an ascending hex run of ``length``.

    >>> _has_sequential_run("a1b2c3d4e5f67890abcdef1234567890")
    True
    >>> _has_sequential_run("0a3728f5aee84ea19b844dc6e1aef664")
    False
    """
    run = 1
    for i in range(1, len(compact)):
        prev = HEX_SEQUENCE.find(compact[i - 1])
        cur = HEX_SEQUENCE.find(compact[i])
        if prev >= 0 and cur == prev + 1:
            run += 1
            if run >= length:
                return True
        else:
            run = 1
    return False


def _uniform_groups(value: str, minimum: int = 3) -> bool:
    """Return True if at least ``minimum`` hyphen groups are a single repeated char.

    >>> _uniform_groups("11111111-2222-3333-4444-555555555555")
    True
    >>> _uniform_groups("0a3728f5-aee8-4ea1-9b84-4dc6e1aef664")
    False
    """
    groups = value.lower().split("-")
    return sum(1 for g in groups if g and len(set(g)) == 1) >= minimum


def is_safe_uuid(value: str) -> bool:
    """Return True when a UUID-like value is a known placeholder or synthetic example.

    >>> is_safe_uuid("00000000-0000-0000-0000-000000000000")
    True
    >>> is_safe_uuid("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    True
    >>> is_safe_uuid("0a3728f5-aee8-4ea1-9b84-4dc6e1aef664")
    False
    >>> is_safe_uuid("7f951dda-4ed3-4680-a7ca-43fe172d538d")
    True
    """
    normalized = value.lower()
    compact = normalized.replace("-", "")

    if normalized in PUBLIC_AZURE_ROLE_IDS:
        return True
    if len(set(compact)) == 1:
        return True
    if _uniform_groups(normalized):
        return True
    if _has_sequential_run(compact):
        return True
    return False


def should_skip_uuid(
    line: str, value: str, in_frontmatter: bool, code_language: Optional[str]
) -> bool:
    """Return True when a UUID match is a known safe example."""
    lower_line = line.lower()

    if "diagram-id:" in lower_line:
        return True
    if in_frontmatter and re.match(r"^\s*id\s*:\s*", line):
        return True
    if re.search(r"\b(x{8}-x{4}-x{4}-x{4}-x{12})\b", lower_line):
        return True
    if is_safe_uuid(value):
        return True
    if code_language and any(
        keyword in lower_line for keyword in ("example", "placeholder", "sample")
    ):
        return True
    return False


def should_skip_private_ip(
    line: str, match_end: int, code_language: Optional[str]
) -> bool:
    """Return True when a private IP is part of a safe CIDR example."""
    after = line[match_end:]
    if re.match(r"/\d{1,2}\b", after):
        return True
    if code_language == "mermaid" and re.search(r"/\d{1,2}\b", line):
        return True
    return False


def classify_uuid(line: str) -> str:
    """Classify a UUID match using nearby identity keywords."""
    lower_line = line.lower()
    if any(keyword in lower_line for keyword in TENANT_KEYWORDS):
        return "Potential tenant ID"
    if any(keyword in lower_line for keyword in OBJECT_KEYWORDS):
        return "Potential object/principal ID"
    return "Potential subscription ID"


def is_safe_email(domain: str) -> bool:
    """Return True for documentation-safe email domains/TLDs.

    >>> is_safe_email("example.com")
    True
    >>> is_safe_email("contoso.example")
    True
    >>> is_safe_email("acme.io")
    False
    >>> is_safe_email("microsoft.com")
    False
    >>> is_safe_email("outlook.com")
    False
    """
    domain = domain.lower()
    if domain in SAFE_EMAIL_DOMAINS:
        return True
    tld = domain.rsplit(".", 1)[-1]
    if tld in SAFE_EMAIL_TLDS:
        return True
    if any(domain.endswith(suffix) for suffix in SAFE_EMAIL_DOMAIN_SUFFIXES):
        return True
    return False


class Finding:
    def __init__(self, file: str, kind: str, line: int, value: str, blocking: bool):
        self.file = file
        self.kind = kind
        self.line = line
        self.value = value
        self.blocking = blocking

    def __str__(self) -> str:
        tag = "ERROR" if self.blocking else "WARN "
        return f"[{tag}] {self.file}:{self.line}: {self.kind}: {self.value}"


def validate_file(
    file_path: Path,
    root: Path,
    allowlist: Set[str],
    strict_private_ip: bool,
) -> List[Finding]:
    """Validate a single Markdown file."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - I/O edge case
        return [Finding(str(file_path), "Read error", 1, str(exc), True)]

    try:
        rel_path = str(file_path.relative_to(root))
    except ValueError:
        rel_path = str(file_path)

    findings: List[Finding] = []
    in_frontmatter = False
    frontmatter_complete = False
    code_language: Optional[str] = None

    for i, line in enumerate(content.split("\n"), 1):
        if i == 1 and line.strip() == "---":
            in_frontmatter = True
            continue
        if in_frontmatter and line.strip() == "---":
            in_frontmatter = False
            frontmatter_complete = True
            continue

        fence_match = FENCED_CODE_PATTERN.match(line.strip())
        if fence_match:
            if code_language is None:
                code_language = (fence_match.group(1) or "").lower() or None
            else:
                code_language = None
            continue

        for match in UUID_PATTERN.finditer(line):
            value = match.group(0)
            if value.lower() in allowlist:
                continue
            if should_skip_uuid(
                line, value, in_frontmatter and not frontmatter_complete, code_language
            ):
                continue
            findings.append(Finding(rel_path, classify_uuid(line), i, value, True))

        for match in PRIVATE_IP_PATTERN.finditer(line):
            value = match.group(0)
            if value in allowlist:
                continue
            if should_skip_private_ip(line, match.end(), code_language):
                continue
            findings.append(
                Finding(rel_path, "Private IP address", i, value, strict_private_ip)
            )

        for match in EMAIL_PATTERN.finditer(line):
            value = match.group(0)
            if value.lower() in allowlist:
                continue
            if is_safe_email(match.group(1)):
                continue
            findings.append(
                Finding(rel_path, "Potential real email address", i, value, True)
            )

    return findings


def load_allowlist(path: Optional[Path]) -> Set[str]:
    """Load exact allowlisted values (case-insensitive for emails/UUIDs)."""
    if path is None or not path.exists():
        return set()
    values: Set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        values.add(line)
        values.add(line.lower())
    return values


def collect_files(root: Path, explicit: Optional[List[str]]) -> List[Path]:
    """Resolve the Markdown files to scan."""
    if explicit:
        result = []
        for name in explicit:
            p = Path(name)
            if not p.is_absolute():
                p = root / name
            if p.suffix == ".md" and p.exists():
                result.append(p)
        return result
    docs_dir = root / "docs"
    if not docs_dir.exists():
        return []
    return sorted(docs_dir.glob("**/*.md"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate documentation for potential PII / leaked identifiers"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show per-file OK lines"
    )
    parser.add_argument(
        "--project", "-p", type=str, help="Repository root (default: script's repo)"
    )
    parser.add_argument(
        "--files",
        nargs="*",
        help="Validate only these Markdown files (changed-only / blocking on PRs)",
    )
    parser.add_argument(
        "--allowlist",
        type=str,
        help="Path to an allowlist file (default: scripts/pii-allowlist.txt if present)",
    )
    parser.add_argument(
        "--strict-private-ip",
        action="store_true",
        help="Treat private IPv4 addresses as blocking instead of advisory",
    )
    args = parser.parse_args()

    root = Path(args.project) if args.project else Path(__file__).parent.parent
    root = root.resolve()

    if args.allowlist:
        allowlist_path: Optional[Path] = Path(args.allowlist)
    else:
        default_allowlist = root / "scripts" / "pii-allowlist.txt"
        allowlist_path = default_allowlist if default_allowlist.exists() else None
    allowlist = load_allowlist(allowlist_path)

    files = collect_files(root, args.files)

    print(f"Validating PII in: {root}")
    if args.files is not None:
        print(f"Mode: changed-files ({len(files)} Markdown file(s))")
    print("=" * 60)

    all_findings: List[Finding] = []
    for md_file in files:
        all_findings.extend(
            validate_file(md_file, root, allowlist, args.strict_private_ip)
        )

    blocking = [f for f in all_findings if f.blocking]
    advisory = [f for f in all_findings if not f.blocking]

    print(f"\nFiles checked: {len(files)}")
    print(f"Blocking findings: {len(blocking)}")
    print(f"Advisory findings: {len(advisory)}")

    if advisory:
        print("\nAdvisory (non-blocking):")
        for finding in advisory:
            print(f"  {finding}")

    if blocking:
        print("\nBlocking:")
        for finding in blocking:
            print(f"  {finding}")
        print(
            "\nRemove real subscription/tenant/object IDs and real email addresses, "
            "or add confirmed-safe example values to scripts/pii-allowlist.txt."
        )
        sys.exit(1)

    print("\nNo blocking PII patterns detected!")
    sys.exit(0)


if __name__ == "__main__":
    main()
