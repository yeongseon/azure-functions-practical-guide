#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
BUILD_DIR=$(mktemp -d)
trap 'rm -rf "$BUILD_DIR"' EXIT

for shape in creation deferred; do
  jq --arg shape "$shape" '
    .resources |= map(
      if $shape == "creation" and .type == "Microsoft.Web/sites" then
        .properties.siteConfig.appSettings += [{name:"WEBSITE_RUN_FROM_PACKAGE", value:"1"}]
      elif $shape == "deferred" and .type == "Microsoft.Web/sites/config" then
        .properties.WEBSITE_RUN_FROM_PACKAGE = "1"
      else . end)
  ' "$ROOT/infra/consumption/main.json" >"$BUILD_DIR/$shape.json"
  if bash "$ROOT/scripts/validate_package_config.sh" "$BUILD_DIR/$shape.json" >/dev/null 2>&1; then
    printf 'FAIL: guard accepted %s ARM mutation\n' "$shape" >&2
    exit 1
  fi
done

source "$ROOT/labs/code-storage-verification/scripts/verify-storage.sh"
for value in 1 0 invalid ''; do
  settings=$(jq --null-input --arg value "$value" '[{name:"WEBSITE_RUN_FROM_PACKAGE",value:$value}]')
  before=$TOTAL_FAILS
  check_linux_consumption_package y1 "$settings" >/dev/null
  [[ $TOTAL_FAILS == $((before + 1)) ]]
done
before=$TOTAL_FAILS
check_linux_consumption_package y1 '[{"name":"WEBSITE_RUN_FROM_PACKAGE","value":"https://example.com/app.zip?sig=synthetic"}]' >/dev/null
check_linux_consumption_package y1 '[{"name":"SCM_DO_BUILD_DURING_DEPLOYMENT","value":"true"},{"name":"ENABLE_ORYX_BUILD","value":"true"}]' >/dev/null
[[ $TOTAL_FAILS == "$before" ]]
printf 'PASS: actual tracked ARM mutations rejected; offline lab package fixtures passed\n'
