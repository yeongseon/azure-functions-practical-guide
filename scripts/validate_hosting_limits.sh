#!/usr/bin/env bash
# Lightweight cross-document guard, not a quota database or live Azure test.
# An optional repository root supports negative regression fixtures.
set -euo pipefail

ROOT=${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}
REFERENCE="$ROOT/docs/reference/platform-limits.md"
PYTHON="$ROOT/docs/language-guides/python/platform-limits.md"
HOSTING="$ROOT/docs/platform/hosting.md"
failed=0

require_text() {
  if ! grep -Fq -- "$2" "$1"; then
    printf 'FAIL: %s must link to %s\n' "$1" "$2" >&2
    failed=1
  fi
}

require_text "$HOSTING" '../reference/platform-limits.md'
require_text "$PYTHON" '../../reference/platform-limits.md'
require_text "$PYTHON" '#runtime-support-and-linux-consumption-migration'
require_text "$REFERENCE" '## Sources'
require_text "$REFERENCE" 'https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale'
require_text "$REFERENCE" 'https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan'

# Keep numeric service-limit rows and language-version matrices centralized.
QUOTA_ROW='^\|[[:space:]]*(\*\*)?(Max instances|Max execution timeout|Max timeout|Timeout max|Default timeout|Instance memory|Memory per instance|Deployment slots|Python versions|PowerShell version|Recommended Java runtime|Max connections|Storage per app|Function apps per plan)'
for language in python nodejs java dotnet powershell; do
  selector="$ROOT/docs/language-guides/$language/tutorial/index.md"
  require_text "$selector" '../../../reference/platform-limits.md'
  require_text "$selector" '#runtime-support-and-linux-consumption-migration'
  if grep -Ein -- "$QUOTA_ROW" "$selector"; then
    printf 'FAIL: %s duplicates shared quota/runtime rows\n' "$selector" >&2
    failed=1
  fi
done
if grep -Ein -- "$QUOTA_ROW" "$PYTHON"; then
  printf 'FAIL: Python limits page duplicates the shared limits database\n' >&2
  failed=1
fi

if (( failed )); then
  exit 1
fi
printf 'PASS: shared hosting-limit links and no duplicated selector quota rows\n'
