---
content_sources:
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/dotnet-isolated-process-guide
  - type: mslearn-adapted
    url: https://learn.microsoft.com/azure/azure-functions/functions-host-json
---

# CLI Cheatsheet

Quick command reference for .NET isolated worker development, deployment, and operations.

<!-- diagram-id: cli-cheatsheet -->
```mermaid
flowchart TD
    A[Configuration] --> B[Build]
    B --> C[Deploy]
    C --> D[Observe]
```

## Topic/Command Groups

### Project setup and local run
```bash
func init MyProject --worker-runtime dotnet-isolated
cd MyProject
func new --template "HTTP trigger" --name HttpFunction
dotnet build
func start
```

### Deployment
```bash
dotnet publish --configuration Release --output ./publish
func azure functionapp publish "$APP_NAME"
az functionapp create   --name "$APP_NAME"   --resource-group "$RG"   --storage-account "$STORAGE_NAME"   --runtime dotnet-isolated   --runtime-version 8   --functions-version 4   --os-type Linux
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp create` |
| Key flags | `--configuration`, `--output`, `--name`, `--resource-group`, `--storage-account`, `--runtime`, `--runtime-version`, `--functions-version`, `--os-type` |
| Variables | `$APP_NAME`, `$RG`, `$STORAGE_NAME` |
| Expected result | Azure CLI returns provisioning details; confirm the resource name and successful provisioning state before continuing. |


### Operations
```bash
az functionapp config appsettings list --name "$APP_NAME" --resource-group "$RG"
az functionapp log tail --name "$APP_NAME" --resource-group "$RG"
az functionapp restart --name "$APP_NAME" --resource-group "$RG"
```

| CLI element | Explanation |
|---|---|
| Command(s) | `az functionapp config appsettings list`, `az functionapp log tail`, `az functionapp restart` |
| Key flags | `--name`, `--resource-group` |
| Variables | `$APP_NAME`, `$RG` |
| Expected result | Azure CLI applies the configuration change; confirm the returned JSON or follow-up query shows the expected value. |


## See Also
- [.NET Language Guide](index.md)
- [.NET Runtime](dotnet-runtime.md)
- [.NET Isolated Worker Model](isolated-worker-model.md)
- [Recipes Index](recipes/index.md)

## Sources
- [Azure Functions .NET isolated worker guide](https://learn.microsoft.com/azure/azure-functions/dotnet-isolated-process-guide)
- [Azure Functions host.json reference](https://learn.microsoft.com/azure/azure-functions/functions-host-json)
