#!/usr/bin/env bash
# Static negative fixtures: ensure the consistency check can actually fail.
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
FIXTURE=$(mktemp -d)
trap 'rm -rf "$FIXTURE"' EXIT
for file in docs/reference/platform-limits.md docs/platform/hosting.md \
  docs/language-guides/python/platform-limits.md \
  docs/language-guides/{python,nodejs,java,dotnet,powershell}/tutorial/index.md; do
  mkdir -p "$FIXTURE/$(dirname "$file")"
  cp "$ROOT/$file" "$FIXTURE/$file"
done

expect_failure() {
  if bash "$ROOT/scripts/validate_hosting_limits.sh" "$FIXTURE" >/dev/null 2>&1; then
    printf 'FAIL: consistency guard accepted %s\n' "$1" >&2
    exit 1
  fi
}

bash "$ROOT/scripts/validate_hosting_limits.sh" "$FIXTURE"
selector="$FIXTURE/docs/language-guides/python/tutorial/index.md"
printf '\n| **Max instances** | 200 | 1000 |\n' >> "$selector"
expect_failure 'duplicated selector quota'
cp "$ROOT/docs/language-guides/python/tutorial/index.md" "$selector"
printf '\n| Deployment slots | 2 |\n' >> "$FIXTURE/docs/language-guides/python/platform-limits.md"
expect_failure 'duplicated Python quota'
cp "$ROOT/docs/language-guides/python/platform-limits.md" "$FIXTURE/docs/language-guides/python/platform-limits.md"
printf '# Selector without shared-reference links\n' > "$selector"
expect_failure 'missing canonical and migration links'
cp "$ROOT/docs/language-guides/python/tutorial/index.md" "$selector"
printf '# Hosting without shared-reference link\n' > "$FIXTURE/docs/platform/hosting.md"
expect_failure 'missing hosting reference link'
cp "$ROOT/docs/platform/hosting.md" "$FIXTURE/docs/platform/hosting.md"
printf '## Sources\nhttps://learn.microsoft.com/en-us/azure/azure-functions/functions-scale\n' > "$FIXTURE/docs/reference/platform-limits.md"
expect_failure 'missing Flex official-source link'
cp "$ROOT/docs/reference/platform-limits.md" "$FIXTURE/docs/reference/platform-limits.md"
bash "$ROOT/scripts/validate_hosting_limits.sh" "$FIXTURE"
printf 'PASS: duplicate rows, missing selector/hosting/source links, and restored fixtures checked\n'
