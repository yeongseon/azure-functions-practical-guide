#!/usr/bin/env bash
# Static compiled-ARM guard for Linux Y1 package settings (no Azure deployment).
# Optional compiled JSON argument supports regression fixtures without rebuilding.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
BUILD_DIR=$(mktemp -d)
trap 'rm -rf "$BUILD_DIR"' EXIT

FILTER='
  def valid:
    ([.resources[] | select(.type == "Microsoft.Web/serverfarms" and .sku.name == "Y1")] | length > 0) as $y1 |
    [.resources[] | select(.type == "Microsoft.Web/sites" and (.kind | contains("linux")))] as $apps |
    if $y1 and ($apps | length > 0) then
      all(.resources[] | select(.type == "Microsoft.Web/sites" or .type == "Microsoft.Web/sites/config");
        all((.properties.siteConfig.appSettings // [])[];
          .name != "WEBSITE_RUN_FROM_PACKAGE" or (.value | tostring) != "1") and
        ((.properties.WEBSITE_RUN_FROM_PACKAGE // "" | tostring) != "1"))
    else true end;
'

if [[ ${1:-} == --self-test ]]; then
  # Cover both creation-time arrays and deferred appsettings objects; preserve
  # valid URL, absent setting, Windows Y1 and Linux Premium/Dedicated behavior.
  jq --null-input --exit-status "$FILTER
    def fixture(\$sku; \$kind; \$creation; \$deferred):
      {resources: [
        {type: \"Microsoft.Web/serverfarms\", sku: {name: \$sku}},
        {type: \"Microsoft.Web/sites\", kind: \$kind,
         properties: {siteConfig: {appSettings: \$creation}}},
        {type: \"Microsoft.Web/sites/config\", properties: \$deferred}]};
    [{name: \"WEBSITE_RUN_FROM_PACKAGE\", value: \"1\"}] as \$local |
    {WEBSITE_RUN_FROM_PACKAGE: \"1\"} as \$settings |
    (fixture(\"Y1\"; \"functionapp,linux\"; \$local; {}) | valid | not) and
    (fixture(\"Y1\"; \"functionapp,linux\"; []; \$settings) | valid | not) and
    (fixture(\"Y1\"; \"functionapp,linux\"; []; {}) | valid) and
    (fixture(\"Y1\"; \"functionapp,linux\";
      [{name: \"WEBSITE_RUN_FROM_PACKAGE\", value: \"https://example.com/app.zip\"}];
      {WEBSITE_RUN_FROM_PACKAGE: \"https://example.com/app.zip\"}) | valid) and
    (fixture(\"Y1\"; \"functionapp\"; \$local; \$settings) | valid) and
    (fixture(\"EP1\"; \"functionapp,linux\"; \$local; \$settings) | valid) and
    (fixture(\"S1\"; \"functionapp,linux\"; \$local; \$settings) | valid)
  " >/dev/null
  printf 'PASS: package guard rejects Linux Y1 local mode in both settings shapes; allows supported modes\n'
  exit 0
fi

TEMPLATE=${1:-"$BUILD_DIR/consumption.json"}
if [[ $# == 0 ]]; then
  az bicep build --file "$ROOT/infra/consumption/main.bicep" --outfile "$TEMPLATE"
fi
jq --exit-status "$FILTER valid" "$TEMPLATE" >/dev/null || {
  printf 'FAIL: Linux Consumption must not set WEBSITE_RUN_FROM_PACKAGE=1\n' >&2
  exit 1
}
printf 'PASS: compiled Linux Consumption package configuration\n'
