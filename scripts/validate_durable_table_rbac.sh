#!/usr/bin/env bash
# Compile all supported Python reference-app plans and check Durable storage RBAC.
# Source/static verification only: no deployment or live authorization check.
# Run from any directory: bash scripts/validate_durable_table_rbac.sh
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
BUILD_DIR=$(mktemp -d)
trap 'rm -rf "$BUILD_DIR"' EXIT

for plan in consumption flex-consumption premium dedicated; do
  az bicep build --file "$ROOT/infra/$plan/main.bicep" --outfile "$BUILD_DIR/$plan.json"
  jq --exit-status --arg plan "$plan" '
    def rid($type; $name): "[resourceId(\u0027" + $type + "\u0027, " + $name + ")]";
    def assignment_id:
      "[extensionResourceId(" + .scope[1:-1] +
      ", \u0027Microsoft.Authorization/roleAssignments\u0027, " + .name[1:-1] + ")]";
    .variables as $vars |
    [.resources[] | select(.type == "Microsoft.Authorization/roleAssignments")] as $roles |
    ([.resources[] | select(.type == "Microsoft.Web/sites")][0]) as $app |
    ([.resources[] | select(.type == "Microsoft.Web/sites/config")][0]) as $settings |
    rid("Microsoft.Storage/storageAccounts"; "variables(\u0027storageAccountName\u0027)") as $scope |
    rid("Microsoft.Resources/deployments"; "\u0027storageModule\u0027") as $storage |
    rid("Microsoft.Web/sites"; "variables(\u0027functionAppName\u0027)") as $app_id |
    rid("Microsoft.ManagedIdentity/userAssignedIdentities"; "variables(\u0027managedIdentityName\u0027)") as $identity_id |
    (if $plan == "flex-consumption" then
      "[reference(" + $identity_id[1:-1] + ", \u00272023-01-31\u0027).principalId]"
    else
      "[reference(" + $app_id[1:-1] + ", \u00272024-04-01\u0027, \u0027full\u0027).identity.principalId]"
    end) as $principal |
    ("[reference(" + $identity_id[1:-1] + ", \u00272023-01-31\u0027).clientId]") as $client_id |
    ("[reference(" + $storage[1:-1] + ", \u00272025-04-01\u0027).outputs.name.value]") as $storage_name |
    ("[reference(resourceId(\u0027Microsoft.Resources/deployments\u0027, \u0027appInsightsModule\u0027), \u00272025-04-01\u0027).outputs.") as $insights |
    {APPLICATIONINSIGHTS_CONNECTION_STRING: ($insights + "connectionString.value]"),
     APPINSIGHTS_INSTRUMENTATIONKEY: ($insights + "instrumentationKey.value]")} as $monitoring |
    ($monitoring + {FUNCTIONS_EXTENSION_VERSION: "~4", FUNCTIONS_WORKER_RUNTIME: "python"} +
     (if ($plan == "consumption" or $plan == "premium") then
       {WEBSITE_CONTENTSHARE: "[variables(\u0027contentShareName\u0027)]",
        WEBSITE_CONTENTAZUREFILECONNECTIONSTRING:
          "[format(\u0027DefaultEndpointsProtocol=https;AccountName={0};AccountKey={1};EndpointSuffix={2}\u0027, variables(\u0027storageAccountName\u0027), listKeys(resourceId(\u0027Microsoft.Storage/storageAccounts\u0027, variables(\u0027storageAccountName\u0027)), \u00272023-05-01\u0027).keys[0].value, environment().suffixes.storage)]"}
      else {} end) +
     (if ($plan == "consumption" or $plan == "dedicated") then
       {WEBSITE_RUN_FROM_PACKAGE: "1"} else {} end)) as $creation_settings |
    (if $plan == "flex-consumption" then
       $monitoring + {AZURE_FUNCTIONS_ENVIRONMENT: "production", TELEMETRY_MODE: "basic", LOG_LEVEL: "INFO",
         AzureWebJobsStorage__accountName: $storage_name, AzureWebJobsStorage__credential: "managedidentity",
         AzureWebJobsStorage__clientId: $client_id}
     else
       $creation_settings + {AzureWebJobsStorage__accountName: "[variables(\u0027storageAccountName\u0027)]",
         AzureWebJobsStorage__credential: "managedidentity"}
     end) as $complete_settings |
    (["storageBlobDataOwnerRoleId", "storageAccountContributorRoleId",
     "storageQueueDataContributorRoleId", "storageTableDataContributorRoleId"] +
    (if ($plan == "consumption" or $plan == "premium") then
      ["storageFileDataPrivilegedContributorRoleId"] else [] end)) as $expected |
    ($vars.storageTableDataContributorRoleId == "0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3") and
    ($vars.storageBlobDataOwnerRoleId == "b7e6dc6d-f1e8-4753-8033-0f276bb0955b") and
    ($vars.storageQueueDataContributorRoleId == "974c5e8b-45b9-4653-ba55-5f855dd0fb88") and
    ($vars.storageAccountContributorRoleId == "17d1049b-9a84-46fb-8f53-869881c3d3ab") and
    (if ($plan == "consumption" or $plan == "premium") then
      $vars.storageFileDataPrivilegedContributorRoleId == "69566ab7-960f-475b-8e7c-b3118f30c6bd"
    else true end) and
    # Exact existing role set plus Table; reject blanket/extra assignments.
    (($roles | map(.properties.roleDefinitionId) | sort) ==
     ($expected | map("[subscriptionResourceId(\u0027Microsoft.Authorization/roleDefinitions\u0027, variables(\u0027" + . + "\u0027))]") | sort)) and
    (all($roles[];
      .scope == $scope and .properties.principalId == $principal and
      .properties.principalType == "ServicePrincipal" and
      (.dependsOn | index($storage) != null) and
      (.dependsOn | index(if $plan == "flex-consumption" then $identity_id else $app_id end) != null))) and
    ($settings != null) and
    ($settings.properties == $complete_settings) and
    # UAMI allows RBAC before app creation. System identity requires app first,
    # then RBAC, then host settings; never add a cyclic app -> RBAC dependency.
    (if $plan == "flex-consumption" then
      $app.identity.type == "UserAssigned" and
      ($app.identity.userAssignedIdentities | keys ==
        ["[format(\u0027{0}\u0027, " + $identity_id[1:-1] + ")]"]) and
      (all($roles[]; assignment_id as $id | $app.dependsOn | index($id) != null))
    else
      $app.identity.type == "SystemAssigned" and
      (if ($plan == "consumption" or $plan == "premium") then
        ($app.properties.siteConfig.appSettings // [] | map({key: .name, value: .value}) | from_entries) == $creation_settings
       else $app.properties.siteConfig.appSettings == null end) and
      ($settings.dependsOn | index($app_id) != null) and
      (all($roles[]; assignment_id as $id | $settings.dependsOn | index($id) != null))
    end)
  ' "$BUILD_DIR/$plan.json" >/dev/null || {
    printf 'FAIL: %s Durable Table RBAC or provisioning ordering\n' "$plan" >&2
    exit 1
  }
  printf 'PASS: %s compiled; storage-scoped roles, identity and provisioning ordering\n' "$plan"
done
