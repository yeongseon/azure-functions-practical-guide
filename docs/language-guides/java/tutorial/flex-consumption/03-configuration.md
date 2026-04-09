---
hide:
  - toc
validation:
  az_cli:
    last_tested: 2026-04-10
    cli_version: "2.83.0"
    core_tools_version: "4.8.0"
    result: pass
  bicep:
    last_tested: null
    result: not_tested
---

# 03 - Configuration (Flex Consumption)

Apply environment settings, JVM arguments, and host-level configuration so the same artifact can run across environments.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| JDK | 17+ | Compile and run Java functions locally |
| Maven | 3.6+ | Build and package Java artifacts |
| Azure Functions Core Tools | v4 | Start local host and publish artifacts |
| Azure CLI | 2.61+ | Provision Azure resources and inspect app state |

!!! info "Flex Consumption plan basics"
    Flex Consumption (FC1) keeps serverless economics while adding VNet integration, configurable instance memory (512 MB to 4096 MB), and per-function scaling. Microsoft recommends it for many new apps.

## What You'll Build

You will standardize Java runtime app settings for Flex Consumption, understand platform-managed vs user-managed settings, and verify effective configuration from Azure.

```mermaid
flowchart TD
    A[local.settings.json] --> B[App Settings in Azure]
    B --> C[Functions host]
    C --> D[Java worker startup]
    D --> E[Function method behavior]
```

## Steps

### Step 1 - Baseline local settings

The reference app includes a `local.settings.json.example` template:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "java",
    "FUNCTIONS_EXTENSION_VERSION": "~4",
    "QueueStorage": "UseDevelopmentStorage=true",
    "EventHubConnection__fullyQualifiedNamespace": "placeholder.servicebus.windows.net"
  }
}
```

### Step 2 - Configure app settings in Azure

```bash
az functionapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --settings \
    "APP_ENV=production" \
    "JAVA_OPTS=-Xmx512m"
```

!!! note "`FUNCTIONS_WORKER_RUNTIME` is platform-managed"
    On Flex Consumption, `FUNCTIONS_WORKER_RUNTIME` is set by the platform during `az functionapp create`. You cannot override it via app settings. This differs from Consumption where you set it explicitly.

### Step 3 - Set JVM and runtime guardrails

```bash
az functionapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --settings \
    "JAVA_OPTS=-Xmx512m -XX:+UseContainerSupport"
```

### Step 4 - Validate `pom.xml` dependency and plugin

Ensure the Maven project includes the Azure Functions Java library:

```xml
<dependency>
    <groupId>com.microsoft.azure.functions</groupId>
    <artifactId>azure-functions-java-library</artifactId>
    <version>3.1.0</version>
</dependency>
```

And the Maven plugin for packaging:

```xml
<plugin>
    <groupId>com.microsoft.azure</groupId>
    <artifactId>azure-functions-maven-plugin</artifactId>
    <version>1.34.0</version>
    <configuration>
        <appName>${functionAppName}</appName>
        <resourceGroup>${functionResourceGroup}</resourceGroup>
        <runtime>
            <os>linux</os>
            <javaVersion>17</javaVersion>
        </runtime>
    </configuration>
</plugin>
```

### Step 5 - Verify effective settings

```bash
az functionapp config appsettings list \
  --name "$APP_NAME" \
  --resource-group "$RG" \
  --output table
```

### Step 6 - Verify runtime behavior with info endpoint

```bash
curl --request GET "https://$APP_NAME.azurewebsites.net/api/info"
```

```json
{
  "name": "azure-functions-java-guide",
  "version": "1.0.0",
  "java": "17.0.14",
  "os": "Linux",
  "environment": "production",
  "functionApp": "func-jflex-04100144"
}
```

## Verification

App settings output (showing key fields):

```text
Name                                    Value
--------------------------------------  -----------------------------------------------
AzureWebJobsStorage                     DefaultEndpointsProtocol=https;AccountName=...
APPLICATIONINSIGHTS_CONNECTION_STRING   InstrumentationKey=<instrumentation-key>;...
APP_ENV                                 production
JAVA_OPTS                               -Xmx512m -XX:+UseContainerSupport
QueueStorage                            DefaultEndpointsProtocol=https;AccountName=...
EventHubConnection                      Endpoint=sb://placeholder.servicebus.windows.net/;...
```

!!! note "Platform-managed settings"
    On Flex Consumption, `FUNCTIONS_WORKER_RUNTIME` and `FUNCTIONS_EXTENSION_VERSION` may not appear in the app settings list because they are managed by the platform.

## Next Steps

> **Next:** [04 - Logging and Monitoring](04-logging-monitoring.md)

## See Also

- [Tutorial Overview & Plan Chooser](../index.md)
- [Java Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources

- [Azure Functions Java developer guide (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-java)
- [Azure Functions hosting options (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-scale)
- [Azure Functions Flex Consumption plan (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/flex-consumption-plan)
