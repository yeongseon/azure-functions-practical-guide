#!/usr/bin/env python3
"""Scan tracked lab files for PII leaks.

Purpose:
    Fail CI if real subscription IDs, employee emails, Azure hostnames,
    or secret tokens appear in tracked lab artifacts. Local authors mask
    values per the PII Removal rules in AGENTS.md; this scanner is the
    repo-side merge gate that enforces them.

Scope:
    Only ``git ls-files`` output under ``labs/`` (and optional extra paths)
    is scanned. Binary files (PNG, JPG, ICO, ZIP, PDF) are skipped by
    extension. Files that cannot be decoded as UTF-8 are also skipped
    with a warning.

Allow list (patterns that are NOT PII):
    - Zero-GUID: ``00000000-0000-0000-0000-000000000000``
    - Known public Azure built-in role definition IDs (AcrPull, Owner,
      Contributor, Reader, etc.) — these are documented, public constants.
    - Sanitizer output tokens: the masked UUID ``xxxxxxxx-xxxx-...`` is
      not matched by the UUID regex (character class is ``[a-f0-9]``).
    - Redacted placeholders: ``<email-redacted>``, ``<ip-redacted>``,
      ``<token-redacted>``, ``<azurewebsites-domain-redacted>`` — not
      matched by the corresponding value regexes.
    - Documentation domains: ``example.com``, ``example.org``,
      ``contoso.com``, ``contoso.onmicrosoft.com``.

Exit codes:
    0 — no PII findings
    1 — one or more findings (annotated with ``::error`` for GitHub Actions)

Usage:
    python3 scripts/scan_lab_pii.py
    python3 scripts/scan_lab_pii.py --paths labs/ docs/troubleshooting/
    python3 scripts/scan_lab_pii.py --verbose
"""

from __future__ import annotations

import argparse
import ipaddress
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

ZERO_GUID = "00000000-0000-0000-0000-000000000000"

# Public Azure built-in role definition IDs — documented at
# https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles
# These are public constants used in Bicep/ARM templates and are not PII.
# Each entry MUST retain its human-readable name so auditors can verify a
# candidate GUID actually corresponds to the labeled built-in role.
PUBLIC_AZURE_ROLE_IDS = frozenset(
    {
        "7f951dda-4ed3-4680-a7ca-43fe172d538d",  # AcrPull
        "8e3af657-a8ff-443c-a75c-2fe8c4bcb635",  # Owner
        "b24988ac-6180-42a0-ab88-20f7382dd24c",  # Contributor
        "acdd72a7-3385-48ef-bd42-f606fba81ae7",  # Reader
        "8311e382-0749-4cb8-b61a-304f252e45ec",  # AcrPush
        "ba92f5b4-2d11-453d-a403-e96b0029c9fe",  # Storage Blob Data Contributor
        "2a2b9908-6ea1-4ae2-8e65-a410df84e7d1",  # Storage Blob Data Reader
        "4633458b-17de-40c3-b3c0-e79bb2e4a2fe",  # Key Vault Secrets User
        "de139f84-1756-47ae-9be6-808fbbe84772",  # Website Contributor
        "73c42c96-874c-492b-b04d-ab87d138a893",  # Log Analytics Reader
        "b7e6dc6d-f1e8-4753-8033-0f276bb0955b",  # Storage Blob Data Owner
        "17d1049b-9a84-46fb-8f53-869881c3d3ab",  # Storage Account Contributor
        "3913510d-42f4-4e42-8a64-420c390055eb",  # Monitoring Metrics Publisher
        "749f88d5-cbae-40b8-bcfc-e573ddc772fa",  # Monitoring Contributor
        "43d0d8ad-25c7-4714-9337-8ba259a9fe05",  # Monitoring Reader
    }
)

ALLOWED_EMAIL_DOMAINS = frozenset(
    {
        "example.com",
        "example.org",
        "example.net",
        "contoso.com",
        "contoso.onmicrosoft.com",
        "test.com",
        "localhost",
    }
)

# Hostnames that appear in documentation as illustrative examples. Real
# Azure-provisioned hostnames (e.g. ``app-lab-foo-abc123.azurewebsites.net``)
# are considered PII because they combine the app name with a random suffix
# that identifies a specific deployment.
ALLOWED_HOSTNAMES = frozenset(
    {
        "contoso.azurewebsites.net",
        "example.azurewebsites.net",
        "myapp.azurewebsites.net",
        "yourapp.azurewebsites.net",
        "app.azurewebsites.net",
        "app-name.azurewebsites.net",
        "scm.azurewebsites.net",
        "staging.azurewebsites.net",
    }
)

# Suffix words that indicate a documentation placeholder rather than a real
# deployment. When the last hyphen-separated component of the app-name label
# equals one of these, the hostname is treated as documentation.
PLACEHOLDER_SUFFIXES = frozenset(
    {
        "abcd",
        "abcdef",
        "foo",
        "bar",
        "baz",
        "test",
        "demo",
        "sample",
        "placeholder",
        "yourapp",
        "myapp",
        "xxxx",
        "xxxxxxxx",
        "xxxxxxxxxxxx",
        "xxx",
    }
)

UUID_RE = re.compile(
    r"\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b",
    re.IGNORECASE,
)
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
# Matches the full hostname chain including all subdomains before
# ``.azurewebsites.net`` so ``app-foo-abc123.scm.azurewebsites.net`` is
# captured as a whole rather than as just ``scm.azurewebsites.net``.
AZURE_HOST_RE = re.compile(
    r"\b((?:[a-z0-9][a-z0-9-]{0,62}\.)+azurewebsites\.net)\b",
    re.IGNORECASE,
)
BEARER_RE = re.compile(r"\bBearer\s+[A-Za-z0-9._\-+/=]{20,}", re.IGNORECASE)
SAS_RE = re.compile(r"[?&]sig=[A-Za-z0-9%_\-+/=]{20,}", re.IGNORECASE)
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

# IPv6 regex mirrors the JS helper regex in portal-capture-helpers.js
# (nine-branch pattern covering full form + all compressed :: positions).
# Uses lookbehind/lookahead on [:.a-fA-F0-9] to avoid partial matches
# inside larger hex tokens (GUIDs, 32-char / 64-char hashes) that other
# rules already handle.
IPV6_RE = re.compile(
    r"(?<![:.a-fA-F0-9])"
    r"(?:"
    r"(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}"
    r"|(?:[0-9a-fA-F]{1,4}:){1,7}:"
    r"|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}"
    r"|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}"
    r"|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}"
    r"|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}"
    r"|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}"
    r"|[0-9a-fA-F]{1,4}:(?::[0-9a-fA-F]{1,4}){1,6}"
    r"|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)"
    r")"
    r"(?![:.a-fA-F0-9])"
)

BINARY_EXTENSIONS = frozenset(
    {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".ico",
        ".webp",
        ".pdf",
        ".zip",
        ".gz",
        ".tar",
        ".tgz",
        ".jar",
        ".class",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".woff",
        ".woff2",
        ".ttf",
        ".otf",
        ".mp4",
        ".mov",
    }
)


def is_public_ip(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False

    if ip.is_private or ip.is_loopback or ip.is_unspecified or ip.is_link_local:
        return False
    if ip.is_reserved or ip.is_multicast:
        return False
    # Network base addresses (last octet 0) are almost always CIDR examples
    # rather than real instance IPs. Skipping them removes the largest
    # source of false positives without hiding real routable IPs.
    if isinstance(ip, ipaddress.IPv4Address) and int(ip) % 256 == 0:
        return False
    return True


def hostname_is_placeholder(host: str) -> bool:
    if host in ALLOWED_HOSTNAMES:
        return True
    # Take the first label of the full FQDN — that is the app-name portion.
    # ``app-lab-memory-abcd.scm.azurewebsites.net`` → ``app-lab-memory-abcd``.
    first_label = host.split(".", 1)[0]
    if "-" in first_label:
        suffix = first_label.rsplit("-", 1)[-1]
        if suffix in PLACEHOLDER_SUFFIXES:
            return True
        # A suffix made of ≤2 unique lowercase letters (e.g. ``xxxx``, ``aaaa``)
        # is a repetition placeholder, not a real random deployment suffix.
        if len(suffix) >= 3 and len(set(suffix)) <= 2 and suffix.isalpha():
            return True
    return False


def find_pii(text: str) -> Iterable[tuple[int, str, str]]:
    for lineno, line in enumerate(text.splitlines(), 1):
        for match in UUID_RE.finditer(line):
            guid = match.group(0).lower()
            if guid == ZERO_GUID:
                continue
            if guid in PUBLIC_AZURE_ROLE_IDS:
                continue
            yield lineno, "real-uuid", guid

        for match in EMAIL_RE.finditer(line):
            email = match.group(0)
            domain = email.split("@", 1)[1].lower()
            if domain in ALLOWED_EMAIL_DOMAINS:
                continue
            yield lineno, "real-email", email

        for match in AZURE_HOST_RE.finditer(line):
            host = match.group(0).lower()
            if hostname_is_placeholder(host):
                continue
            yield lineno, "azurewebsites-host", host

        for _match in BEARER_RE.finditer(line):
            yield lineno, "bearer-token", "Bearer <redacted-from-report>"

        for _match in SAS_RE.finditer(line):
            yield lineno, "sas-token", "sig=<redacted-from-report>"

        for match in IP_RE.finditer(line):
            candidate = match.group(0)
            if is_public_ip(candidate):
                yield lineno, "public-ip", candidate

        for match in IPV6_RE.finditer(line):
            value = match.group(0)
            if is_public_ip(value):
                yield lineno, "public-ipv6", value


def tracked_files(paths: list[str]) -> list[Path]:
    cmd = ["git", "ls-files", "--", *paths]
    output = subprocess.check_output(cmd, text=True)
    return [Path(line) for line in output.splitlines() if line.strip()]


def is_scannable(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--paths",
        nargs="+",
        default=["labs/"],
        help="Paths (relative to repo root) to scan. Default: labs/",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print scanned file count and per-file results.",
    )
    args = parser.parse_args(argv)

    try:
        files = tracked_files(args.paths)
    except subprocess.CalledProcessError as exc:
        print(f"[scan_lab_pii] git ls-files failed: {exc}", file=sys.stderr)
        return 2

    findings: list[tuple[Path, int, str, str]] = []
    scanned = 0
    skipped_binary = 0
    skipped_decode = 0

    for file_path in files:
        if not is_scannable(file_path):
            if file_path.suffix.lower() in BINARY_EXTENSIONS:
                skipped_binary += 1
            continue

        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            skipped_decode += 1
            if args.verbose:
                print(
                    f"[scan_lab_pii] skipped (not utf-8): {file_path}",
                    file=sys.stderr,
                )
            continue

        scanned += 1
        for lineno, category, value in find_pii(text):
            findings.append((file_path, lineno, category, value))

    for file_path, lineno, category, value in findings:
        print(
            f"::error file={file_path},line={lineno},title=Lab artifact PII::"
            f"[{category}] {value}"
        )

    print(
        f"[scan_lab_pii] scanned={scanned} skipped_binary={skipped_binary} "
        f"skipped_decode={skipped_decode} findings={len(findings)}",
        file=sys.stderr,
    )

    if findings:
        print(
            "[scan_lab_pii] PII found. Mask the values per the PII Removal "
            "rules in AGENTS.md before committing.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
