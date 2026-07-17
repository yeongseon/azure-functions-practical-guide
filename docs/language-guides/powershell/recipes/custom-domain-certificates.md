---
content_sources:
  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/app-service/configure-ssl-certificate
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell
---
# Custom Domain and Certificates

Configure an HTTPS custom domain and TLS certificate for a PowerShell Function App.

## Add a Custom Hostname

Point a CNAME (or A record) at the Function App, then bind the hostname:

```bash
az functionapp config hostname add --name "$APP_NAME" --resource-group "$RG" --hostname "api.example.com"
```

## Create a Managed Certificate

App Service managed certificates are free and auto-renew:

```bash
az functionapp config ssl create --name "$APP_NAME" --resource-group "$RG" --hostname "api.example.com"
```

## Bind the Certificate

```bash
az functionapp config ssl bind --name "$APP_NAME" --resource-group "$RG" --certificate-thumbprint "<thumbprint>" --ssl-type SNI
```

## Enforce HTTPS

Redirect all HTTP traffic to HTTPS:

```bash
az functionapp update --name "$APP_NAME" --resource-group "$RG" --set httpsOnly=true
```

!!! warning "Hosting plan support"
    Flex Consumption does not support managed/platform certificates. Use Premium or Dedicated plans when you need a bound custom-domain certificate, or front the app with Azure Front Door.

!!! tip "Automating certificate provisioning"
    Use the `Az.Websites` PowerShell module (`New-AzWebAppSSLBinding`) to script certificate binding in a deployment pipeline instead of manual portal steps.

## See Also

- [HTTP Authentication](http-auth.md)
- [Managed Identity](managed-identity.md)
- [Recipes Index](index.md)

## Sources

- [Add and manage TLS/SSL certificates (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/app-service/configure-ssl-certificate)
- [PowerShell developer reference (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell)
