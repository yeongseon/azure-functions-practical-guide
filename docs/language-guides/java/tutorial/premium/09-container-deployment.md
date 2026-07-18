---
validation:
  az_cli:
    last_tested:
    result: not_tested
  bicep:
    last_tested:
    result: not_tested
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-how-to-custom-container
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-create-container-registry
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-deploy-container
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/container-apps/functions-overview
---
# 09 - Container Deployment (Premium)

Package your Java function app as a Linux container with a multi-stage build, push it to Azure Container Registry, and deploy it to a Premium plan with a managed-identity registry pull.

## Which Plans Support Custom Containers?

Custom container images are **not** available on every hosting plan. Choose your target deliberately:

| Hosting plan | Custom container image? | Notes |
|---|:---:|---|
| Consumption (Y1) | ❌ | Code deploy only (zip / run-from-package) |
| Flex Consumption (FC1) | ❌ | One-deploy zip only; no custom image |
| **Premium (EP)** | ✅ | Elastic Premium — this tutorial |
| Dedicated (App Service) | ✅ | Also supports webhook-based continuous deployment |
| Azure Container Apps | ✅ | Recommended for most **new** container workloads |

!!! tip "New container workloads: consider Azure Container Apps"
    Microsoft now recommends [Azure Functions on Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/functions-overview) for most new containerized workloads. This tutorial targets the **Premium (EP) plan**, which is the right choice when you need custom containers alongside classic Functions networking and slots.

## Prerequisites

| Tool | Minimum version | Purpose |
|---|---|---|
| Java | 17 | Function app runtime |
| Maven | 3.9 | Build the deployable artifact |
| Azure Functions Core Tools | 4.x | Generate the Dockerfile |
| Docker | Latest | Build the image locally (optional if using ACR build) |
| Azure CLI | 2.83+ | Provision ACR, plan, and app |

## What You'll Build

You will add a multi-stage Dockerfile to the Java app, build and push the image to ACR, create a Premium plan function app configured to pull that image, and grant the app's managed identity `AcrPull` so it authenticates without registry passwords.

## 1. Create a Multi-Stage Dockerfile

Java requires a Maven build step. Use a builder stage, then copy the staged app into the Functions base image.

```dockerfile
# Build stage
FROM mcr.microsoft.com/openjdk/jdk:17-mariner AS build
WORKDIR /src
COPY . .
RUN mvn clean package -DskipTests

# Runtime stage
FROM mcr.microsoft.com/azure-functions/java:4-java17
ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true
COPY --from=build /src/target/azure-functions/*/ /home/site/wwwroot
```

!!! warning "Keep the base image current"
    You own the base image. Rebuild and redeploy monthly from the latest [`mcr.microsoft.com/azure-functions/java`](https://mcr.microsoft.com/catalog?search=functions) tag to pick up runtime and security fixes.

## 2. Build and Push to Azure Container Registry

```bash
az acr create --resource-group $RG --name $REGISTRY_NAME --sku Basic
az acr build --registry $REGISTRY_NAME --image functions/java-app:v1.0.0 .
```

## 3. Create the Premium Plan and Function App

```bash
az functionapp plan create --resource-group $RG --name $PLAN_NAME \
  --location $LOCATION --sku EP1 --is-linux

az functionapp create --resource-group $RG --name $APP_NAME \
  --storage-account $STORAGE_NAME --plan $PLAN_NAME \
  --functions-version 4 --runtime java \
  --image $REGISTRY_NAME.azurecr.io/functions/java-app:v1.0.0 \
  --assign-identity "[system]"
```

## 4. Grant Managed-Identity Registry Pull

```bash
PRINCIPAL_ID=$(az functionapp identity show --resource-group $RG --name $APP_NAME --query principalId --output tsv)
REGISTRY_ID=$(az acr show --name $REGISTRY_NAME --query id --output tsv)

az role assignment create --assignee $PRINCIPAL_ID --role AcrPull --scope $REGISTRY_ID
az resource update --ids "$(az functionapp show --resource-group $RG --name $APP_NAME --query id --output tsv)/config/web" \
  --set properties.acrUseManagedIdentityCreds=true
```

## 5. Update the Image

```bash
az acr build --registry $REGISTRY_NAME --image functions/java-app:v1.0.1 .
az functionapp config container set --resource-group $RG --name $APP_NAME \
  --image $REGISTRY_NAME.azurecr.io/functions/java-app:v1.0.1
```

!!! info "Continuous deployment on Premium"
    Webhook-based container CD is **not** supported on the Elastic Premium plan. Either restart the app after pushing a new image, or deploy on a **Dedicated (App Service) plan** if you need webhook auto-redeploy. If the container listens on a non-default port, set the `WEBSITES_PORT` app setting.

## Verification

- [ ] `az acr build` completes and the image appears in `az acr repository list --name $REGISTRY_NAME`.
- [ ] The function app starts and serves requests from the container image.
- [ ] `az functionapp config container show` reports the expected image, and `acrUseManagedIdentityCreds` is `true` (no stored registry password).

## Next Steps

- Automate build-and-push in your pipeline — see [06 - CI/CD](06-ci-cd.md).
- For webhook-based redeploys, evaluate the Dedicated plan or Azure Container Apps.

## See Also

- [08 - Testing and Debugging](../flex-consumption/08-testing-and-debugging.md) — Test before you containerize
- [Work with Azure Functions in containers](https://learn.microsoft.com/en-us/azure/azure-functions/functions-how-to-custom-container)
- [Azure Functions on Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/functions-overview)

## Sources

- [Work with Azure Functions in containers (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-how-to-custom-container)
- [Create a function app in a local Linux container (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-create-container-registry)
- [Azure Container Apps hosting of Azure Functions (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/container-apps/functions-overview)
</content>
