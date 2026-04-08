# 03 - Configuration (Dedicated)

Apply environment settings, JVM arguments, and host-level configuration so the same artifact can run across environments.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| JDK | 17+ | Compile and run Java functions locally |
| Maven | 3.9+ | Build and deploy Java artifacts |
| Azure Functions Core Tools | v4 | Start local host and publish artifacts |
| Azure CLI | 2.61+ | Provision Azure resources and inspect app state |

!!! info "Plan basics"
    Dedicated (App Service Plan) runs Functions on reserved capacity. Choose it when you already operate App Service workloads and prefer fixed-cost hosting.

```mermaid
flowchart TD
    A[local.settings.json] --> B[App Settings in Azure]
    B --> C[Functions host]
    C --> D[Java worker startup]
    D --> E[Function method behavior]
```

## What You'll Build

- A portable app settings baseline for local and Azure environments.
- Plan-appropriate JVM tuning through `JAVA_OPTS`.
- Dedicated-specific runtime guardrails for package deployment and Always On.

## Steps

### Step 1 - Baseline local settings

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "java",
    "APP_ENV": "local"
  }
}
```

### Step 2 - Configure app settings in Azure

```bash
az functionapp config appsettings set --name $APP_NAME --resource-group $RG --settings "FUNCTIONS_WORKER_RUNTIME=java" "APP_ENV=prod" "JAVA_OPTS=-Xms256m -Xmx512m"
```

### Step 3 - Set JVM and runtime guardrails

```bash
az functionapp config appsettings set --name $APP_NAME --resource-group $RG --settings "WEBSITE_RUN_FROM_PACKAGE=1"
az functionapp config set --name $APP_NAME --resource-group $RG --always-on true
```

### Step 4 - Validate `pom.xml` dependency and plugin

```xml
<dependency>
    <groupId>com.microsoft.azure.functions</groupId>
    <artifactId>azure-functions-java-library</artifactId>
    <version>3.1.0</version>
</dependency>
```

```xml
<plugin>
    <groupId>com.microsoft.azure</groupId>
    <artifactId>azure-functions-maven-plugin</artifactId>
</plugin>
```

### Step 5 - Verify effective settings

```bash
az functionapp config appsettings list --name $APP_NAME --resource-group $RG --output table
```

## Verification

```text
Name                              Value
--------------------------------  -------------------------
FUNCTIONS_WORKER_RUNTIME          java
APP_ENV                           prod
JAVA_OPTS                         -Xms256m -Xmx512m
```

## See Also

- [Tutorial Overview & Plan Chooser](../index.md)
- [Java Language Guide](../../index.md)
- [Platform: Hosting Plans](../../../../platform/hosting.md)
- [Operations: Deployment](../../../../operations/deployment.md)
- [Recipes Index](../../recipes/index.md)

## Sources

- [Azure Functions Java developer guide (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-java)
- [Azure Functions hosting options (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-scale)
- [Create a Java function with Azure Functions Core Tools (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/create-first-function-cli-java)
