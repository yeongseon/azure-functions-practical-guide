#!/usr/bin/env bash
# verify-storage.sh — Automated baseline verification for code storage lab
# Usage: ./verify-storage.sh [y1|fc1|ep|asp|all]
set -euo pipefail

LOCATION="koreacentral"
RG_Y1="rg-func-codeverify-y1"
RG_FC1="rg-func-codeverify-fc1"
RG_EP="rg-func-codeverify-ep"
RG_ASP="rg-func-codeverify-asp"
BASE_Y1="codeverifyy1"
BASE_FC1="codeverifyfc1"
BASE_EP="codeverifyep"
BASE_ASP="codeverifyasp"
APP_Y1="${BASE_Y1}-func"
APP_FC1="${BASE_FC1}-func"
APP_EP="${BASE_EP}-func"
APP_ASP="${BASE_ASP}-func"
STORAGE_Y1="${BASE_Y1}storage"
STORAGE_FC1="${BASE_FC1}storage"
STORAGE_EP="${BASE_EP}storage"
STORAGE_ASP="${BASE_ASP}storage"

readonly ROLE_BLOB_CONTRIBUTOR="Storage Blob Data Contributor"
readonly ROLE_BLOB_OWNER="Storage Blob Data Owner"
readonly ROLE_QUEUE_CONTRIBUTOR="Storage Queue Data Contributor"
readonly ROLE_FILE_PRIVILEGED="Storage File Data Privileged Contributor"
readonly ROLE_ACCOUNT_CONTRIBUTOR="Storage Account Contributor"

if [ -t 1 ]; then
  COLOR_GREEN='\033[0;32m'; COLOR_RED='\033[0;31m'; COLOR_BLUE='\033[0;34m'; COLOR_RESET='\033[0m'
else
  COLOR_GREEN=''; COLOR_RED=''; COLOR_BLUE=''; COLOR_RESET=''
fi

declare -A PLAN_PASS_COUNT=()
declare -A PLAN_FAIL_COUNT=()
TOTAL_CHECKS=0
TOTAL_FAILS=0

print_usage() { printf 'Usage: %s [y1|fc1|ep|asp|all]\n' "$0"; }

require_command() {
  local command_name="$1"
  if ! command -v "$command_name" >/dev/null 2>&1; then
    printf '%bERROR:%b command not found: %s\n' "$COLOR_RED" "$COLOR_RESET" "$command_name" >&2
    exit 1
  fi
}

record_check() {
  local plan_code="$1" check_name="$2" status="$3" detail="$4"
  TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
  if [ "$status" = "PASS" ]; then
    PLAN_PASS_COUNT["$plan_code"]=$(( ${PLAN_PASS_COUNT["$plan_code"]:-0} + 1 ))
    printf '%b✅ PASS%b [%s] %s\n' "$COLOR_GREEN" "$COLOR_RESET" "$plan_code" "$check_name"
  else
    PLAN_FAIL_COUNT["$plan_code"]=$(( ${PLAN_FAIL_COUNT["$plan_code"]:-0} + 1 ))
    TOTAL_FAILS=$((TOTAL_FAILS + 1))
    printf '%b❌ FAIL%b [%s] %s\n' "$COLOR_RED" "$COLOR_RESET" "$plan_code" "$check_name"
  fi
  [ -n "$detail" ] && printf '    %s\n' "$detail"
}

get_setting_value() {
  local appsettings_json="$1" setting_name="$2"
  jq -r --arg name "$setting_name" '([.[] | select(.name == $name) | .value] | first) // ""' <<<"$appsettings_json"
}

check_setting_present() {
  local plan_code="$1" appsettings_json="$2" setting_name="$3" value
  value="$(get_setting_value "$appsettings_json" "$setting_name")"
  if [ -n "$value" ] && [ "$value" != "null" ]; then
    record_check "$plan_code" "App setting present: $setting_name" "PASS" "Value detected"
  else
    record_check "$plan_code" "App setting present: $setting_name" "FAIL" "Missing required setting"
  fi
}

check_setting_absent() {
  local plan_code="$1" appsettings_json="$2" setting_name="$3" key_exists
  key_exists="$(jq -r --arg name "$setting_name" 'any(.[]; .name == $name)' <<<"$appsettings_json")"
  if [ "$key_exists" = "false" ]; then
    record_check "$plan_code" "App setting absent: $setting_name" "PASS" "Not present as expected"
  else
    record_check "$plan_code" "App setting absent: $setting_name" "FAIL" "Key exists (should not be present)"
  fi
}

check_setting_equals() {
  local plan_code="$1" appsettings_json="$2" setting_name="$3" expected_value="$4" value
  value="$(get_setting_value "$appsettings_json" "$setting_name")"
  if [ "$value" = "$expected_value" ]; then
    record_check "$plan_code" "App setting equals: $setting_name=$expected_value" "PASS" "Value matches"
  else
    record_check "$plan_code" "App setting equals: $setting_name=$expected_value" "FAIL" "Actual value: ${value:-<empty>}"
  fi
}

verify_storage_account_settings() {
  local plan_code="$1" rg="$2" storage_name="$3" storage_json
  if ! storage_json="$(az storage account show --resource-group "$rg" --name "$storage_name" --output json 2>/dev/null)"; then
    record_check "$plan_code" "Storage account exists: $storage_name" "FAIL" "Unable to query storage account"
    return
  fi
  record_check "$plan_code" "Storage account exists: $storage_name" "PASS" "Storage account found"

  local allow_blob_public_access allow_shared_key_access
  allow_blob_public_access="$(jq -r '.allowBlobPublicAccess' <<<"$storage_json")"
  allow_shared_key_access="$(jq -r '.allowSharedKeyAccess' <<<"$storage_json")"

  # Expected storage account policies differ by hosting plan (derived from Bicep templates)
  local expected_blob_public expected_shared_key
  case "$plan_code" in
    y1)  expected_blob_public="true";  expected_shared_key="true" ;;
    fc1) expected_blob_public="false"; expected_shared_key="false" ;;
    ep)  expected_blob_public="true";  expected_shared_key="true" ;;
    asp) expected_blob_public="true";  expected_shared_key="false" ;;
    *)   expected_blob_public="false"; expected_shared_key="false" ;;
  esac

  if [ "$allow_blob_public_access" = "$expected_blob_public" ]; then
    record_check "$plan_code" "Storage allowBlobPublicAccess=$expected_blob_public" "PASS" "Public blob access matches plan expectation"
  else
    record_check "$plan_code" "Storage allowBlobPublicAccess=$expected_blob_public" "FAIL" "Expected $expected_blob_public, got: $allow_blob_public_access"
  fi
  if [ "$allow_shared_key_access" = "$expected_shared_key" ]; then
    record_check "$plan_code" "Storage allowSharedKeyAccess=$expected_shared_key" "PASS" "Shared key access matches plan expectation"
  else
    record_check "$plan_code" "Storage allowSharedKeyAccess=$expected_shared_key" "FAIL" "Expected $expected_shared_key, got: $allow_shared_key_access"
  fi
}

verify_identity_and_rbac() {
  local plan_code="$1" rg="$2" app_name="$3" storage_name="$4" identity_json
  if ! identity_json="$(az functionapp identity show --resource-group "$rg" --name "$app_name" --output json 2>/dev/null)"; then
    record_check "$plan_code" "Function app identity query" "FAIL" "Unable to query identity"
    return
  fi
  record_check "$plan_code" "Function app identity query" "PASS" "Identity payload retrieved"

  local identity_type principal_id expected_identity_type
  identity_type="$(jq -r '.type' <<<"$identity_json")"
  if [ "$plan_code" = "fc1" ]; then
    principal_id="$(jq -r '.userAssignedIdentities | to_entries[0].value.principalId' <<<"$identity_json")"
  else
    principal_id="$(jq -r '.principalId' <<<"$identity_json")"
  fi
  # Enforce exact per-plan identity contract
  # FC1: must be exactly "UserAssigned" (not combined with SystemAssigned)
  # Y1/EP/ASP: must be exactly "SystemAssigned" (not combined with UserAssigned)
  if [ "$plan_code" = "fc1" ]; then
    if [ "$identity_type" = "UserAssigned" ]; then
      record_check "$plan_code" "Identity type: UserAssigned" "PASS" "Identity type: $identity_type"
    else
      record_check "$plan_code" "Identity type: UserAssigned" "FAIL" "Expected exactly UserAssigned, got: ${identity_type:-<empty>}"
    fi
  else
    if [ "$identity_type" = "SystemAssigned" ]; then
      record_check "$plan_code" "Identity type: SystemAssigned" "PASS" "Identity type: $identity_type"
    else
      record_check "$plan_code" "Identity type: SystemAssigned" "FAIL" "Expected exactly SystemAssigned, got: ${identity_type:-<empty>}"
    fi
  fi
  if [ -z "$principal_id" ] || [ "$principal_id" = "null" ]; then
    record_check "$plan_code" "Managed identity principalId present" "FAIL" "principalId missing"
    return
  fi
  record_check "$plan_code" "Managed identity principalId present" "PASS" "principalId found"

  local storage_id role_assignments_json assignment_count
  if ! storage_id="$(az storage account show --resource-group "$rg" --name "$storage_name" --query 'id' --output tsv 2>/dev/null)"; then
    record_check "$plan_code" "Storage scope resolved for RBAC" "FAIL" "Unable to resolve storage ID"
    return
  fi
  record_check "$plan_code" "Storage scope resolved for RBAC" "PASS" "Storage ID resolved"

  if ! role_assignments_json="$(az role assignment list --assignee-object-id "$principal_id" --scope "$storage_id" --output json 2>/dev/null)"; then
    record_check "$plan_code" "Role assignment lookup" "FAIL" "Unable to list role assignments"
    return
  fi

  assignment_count="$(jq 'length' <<<"$role_assignments_json")"
  if [ "$assignment_count" -gt 0 ]; then
    record_check "$plan_code" "Role assignments exist on storage scope" "PASS" "Found $assignment_count assignment(s)"
  else
    record_check "$plan_code" "Role assignments exist on storage scope" "FAIL" "No assignments found"
  fi

  local expected_roles=("$ROLE_BLOB_OWNER" "$ROLE_ACCOUNT_CONTRIBUTOR" "$ROLE_QUEUE_CONTRIBUTOR")
  if [ "$plan_code" = "y1" ] || [ "$plan_code" = "ep" ]; then
    expected_roles+=("$ROLE_FILE_PRIVILEGED")
  fi

  local role has_role
  for role in "${expected_roles[@]}"; do
    has_role="$(jq -r --arg r "$role" 'map(.roleDefinitionName) | any(. == $r)' <<<"$role_assignments_json")"
    if [ "$has_role" = "true" ]; then
      record_check "$plan_code" "RBAC role: $role" "PASS" "Role assigned"
    else
      record_check "$plan_code" "RBAC role: $role" "FAIL" "Role not found on storage scope"
    fi
  done
}

verify_plan_specific_settings() {
  local plan_code="$1" rg="$2" app_name="$3" appsettings_json="$4"
  case "$plan_code" in
    y1)
      check_setting_present "$plan_code" "$appsettings_json" "AzureWebJobsStorage__accountName"
      check_setting_equals "$plan_code" "$appsettings_json" "AzureWebJobsStorage__credential" "managedidentity"
      check_setting_absent "$plan_code" "$appsettings_json" "AzureWebJobsStorage__clientId"
      check_setting_present "$plan_code" "$appsettings_json" "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING"
      check_setting_present "$plan_code" "$appsettings_json" "WEBSITE_CONTENTSHARE"
      check_setting_equals "$plan_code" "$appsettings_json" "WEBSITE_RUN_FROM_PACKAGE" "1"
      ;;
    fc1)
      check_setting_present "$plan_code" "$appsettings_json" "AzureWebJobsStorage__accountName"
      check_setting_equals "$plan_code" "$appsettings_json" "AzureWebJobsStorage__credential" "managedidentity"
      check_setting_present "$plan_code" "$appsettings_json" "AzureWebJobsStorage__clientId"
      check_setting_absent "$plan_code" "$appsettings_json" "WEBSITE_RUN_FROM_PACKAGE"
      check_setting_absent "$plan_code" "$appsettings_json" "WEBSITE_CONTENTSHARE"
      check_setting_absent "$plan_code" "$appsettings_json" "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING"
      local deployment_storage_json deployment_type deployment_auth_type
      if deployment_storage_json="$(az functionapp show --resource-group "$rg" --name "$app_name" --query "functionAppConfig.deployment.storage" --output json 2>/dev/null)"; then
        deployment_type="$(jq -r '.type' <<<"$deployment_storage_json")"
        if [ "$deployment_type" = "blobContainer" ]; then
          record_check "$plan_code" "FC1 deployment storage type=blobContainer" "PASS" "Deployment storage type matches"
        else
          record_check "$plan_code" "FC1 deployment storage type=blobContainer" "FAIL" "Actual type: ${deployment_type:-<empty>}"
        fi
        deployment_auth_type="$(jq -r '.authentication.type' <<<"$deployment_storage_json")"
        if [ "$deployment_auth_type" = "UserAssignedIdentity" ]; then
          record_check "$plan_code" "FC1 deployment auth type=UserAssignedIdentity" "PASS" "Auth type matches"
        else
          record_check "$plan_code" "FC1 deployment auth type=UserAssignedIdentity" "FAIL" "Actual: ${deployment_auth_type:-<empty>}"
        fi
      else
        record_check "$plan_code" "FC1 deployment storage type=blobContainer" "FAIL" "Unable to query deployment storage"
        record_check "$plan_code" "FC1 deployment auth type=UserAssignedIdentity" "FAIL" "Unable to query deployment storage"
      fi
      ;;
    ep)
      check_setting_present "$plan_code" "$appsettings_json" "AzureWebJobsStorage__accountName"
      check_setting_equals "$plan_code" "$appsettings_json" "AzureWebJobsStorage__credential" "managedidentity"
      check_setting_absent "$plan_code" "$appsettings_json" "AzureWebJobsStorage__clientId"
      check_setting_present "$plan_code" "$appsettings_json" "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING"
      check_setting_present "$plan_code" "$appsettings_json" "WEBSITE_CONTENTSHARE"
      check_setting_absent "$plan_code" "$appsettings_json" "WEBSITE_RUN_FROM_PACKAGE"
      ;;
    asp)
      check_setting_present "$plan_code" "$appsettings_json" "AzureWebJobsStorage__accountName"
      check_setting_equals "$plan_code" "$appsettings_json" "AzureWebJobsStorage__credential" "managedidentity"
      check_setting_absent "$plan_code" "$appsettings_json" "AzureWebJobsStorage__clientId"
      check_setting_equals "$plan_code" "$appsettings_json" "WEBSITE_RUN_FROM_PACKAGE" "1"
      check_setting_absent "$plan_code" "$appsettings_json" "WEBSITE_CONTENTSHARE"
      check_setting_absent "$plan_code" "$appsettings_json" "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING"
      ;;
    *) record_check "$plan_code" "Plan-specific checks" "FAIL" "Unsupported plan code" ;;
  esac
}

verify_plan() {
  local plan_code="$1" rg="$2" app_name="$3" storage_name="$4" rg_exists appsettings_json
  printf '\n%b== Verifying %s (%s) ==%b\n' "$COLOR_BLUE" "$plan_code" "$app_name" "$COLOR_RESET"

  if ! rg_exists="$(az group exists --name "$rg" --output tsv 2>/dev/null)"; then
    record_check "$plan_code" "Resource group exists: $rg" "FAIL" "Unable to query resource group"
    return
  fi
  if [ "$rg_exists" != "true" ]; then
    record_check "$plan_code" "Resource group exists: $rg" "FAIL" "Resource group not found"
    return
  fi
  record_check "$plan_code" "Resource group exists: $rg" "PASS" "Resource group found in $LOCATION"

  if ! appsettings_json="$(az functionapp config appsettings list --resource-group "$rg" --name "$app_name" --output json 2>/dev/null)"; then
    record_check "$plan_code" "Function app appsettings query" "FAIL" "Unable to query app settings"
    return
  fi
  record_check "$plan_code" "Function app appsettings query" "PASS" "App settings retrieved"

  verify_plan_specific_settings "$plan_code" "$rg" "$app_name" "$appsettings_json"
  verify_identity_and_rbac "$plan_code" "$rg" "$app_name" "$storage_name"
  verify_storage_account_settings "$plan_code" "$rg" "$storage_name"
}

print_summary() {
  printf '\n%b================ Verification Summary ================%b\n' "$COLOR_BLUE" "$COLOR_RESET"
  printf '%-8s | %-6s | %-6s\n' "Plan" "PASS" "FAIL"
  printf '%-8s-+-%-6s-+-%-6s\n' "--------" "------" "------"
  local plan
  for plan in y1 fc1 ep asp; do
    local pass_count="${PLAN_PASS_COUNT[$plan]:-0}" fail_count="${PLAN_FAIL_COUNT[$plan]:-0}"
    if [ "$pass_count" -gt 0 ] || [ "$fail_count" -gt 0 ]; then
      printf '%-8s | %-6s | %-6s\n' "$plan" "$pass_count" "$fail_count"
    fi
  done
  printf '\nTotal checks: %s\n' "$TOTAL_CHECKS"
  if [ "$TOTAL_FAILS" -eq 0 ]; then
    printf '%bOverall result: PASS%b\n' "$COLOR_GREEN" "$COLOR_RESET"
  else
    printf '%bOverall result: FAIL (%s checks failed)%b\n' "$COLOR_RED" "$TOTAL_FAILS" "$COLOR_RESET"
  fi
}

main() {
  require_command az
  require_command jq
  local selected_plan="${1:-all}"
  case "$selected_plan" in
    y1) verify_plan "y1" "$RG_Y1" "$APP_Y1" "$STORAGE_Y1" ;;
    fc1) verify_plan "fc1" "$RG_FC1" "$APP_FC1" "$STORAGE_FC1" ;;
    ep) verify_plan "ep" "$RG_EP" "$APP_EP" "$STORAGE_EP" ;;
    asp) verify_plan "asp" "$RG_ASP" "$APP_ASP" "$STORAGE_ASP" ;;
    all)
      verify_plan "y1" "$RG_Y1" "$APP_Y1" "$STORAGE_Y1"
      verify_plan "fc1" "$RG_FC1" "$APP_FC1" "$STORAGE_FC1"
      verify_plan "ep" "$RG_EP" "$APP_EP" "$STORAGE_EP"
      verify_plan "asp" "$RG_ASP" "$APP_ASP" "$STORAGE_ASP"
      ;;
    *) print_usage; exit 1 ;;
  esac
  print_summary
  [ "$TOTAL_FAILS" -eq 0 ] || exit 1
}

main "$@"
