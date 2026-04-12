# Azure Functions Practical Guide

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

Comprehensive guide for running serverless applications on Azure Functions — from first deployment to production troubleshooting.

## What's Inside

| Section | Description |
|---------|-------------|
| [Start Here](https://yeongseon.github.io/azure-functions-practical-guide/) | Overview, learning paths, and repository map |
| [Platform](https://yeongseon.github.io/azure-functions-practical-guide/platform/) | Architecture, hosting plans, scaling, networking, security |
| [Best Practices](https://yeongseon.github.io/azure-functions-practical-guide/best-practices/) | Hosting selection, triggers, scaling, reliability, security, deployment |
| [Language Guides](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) | Step-by-step tutorials for Python, Node.js, Java, and .NET |
| [Operations](https://yeongseon.github.io/azure-functions-practical-guide/operations/) | Deployment, monitoring, alerts, cost optimization, recovery |
| [Troubleshooting](https://yeongseon.github.io/azure-functions-practical-guide/troubleshooting/) | Playbooks, KQL queries, methodology, and hands-on labs |
| [Reference](https://yeongseon.github.io/azure-functions-practical-guide/reference/) | CLI cheatsheet, host.json, platform limits |

## Language Guides

- **Python** (v2 decorator model, 4 hosting plan tracks)
- **Node.js** (v4 programming model, 4 hosting plan tracks)
- **Java** (4 hosting plan tracks)
- **.NET** (isolated worker model, 4 hosting plan tracks)

Each guide covers: local development, first deploy, configuration, logging, infrastructure as code, CI/CD, and trigger extensions.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yeongseon/azure-functions-practical-guide.git

# Install MkDocs dependencies
pip install mkdocs-material mkdocs-minify-plugin

# Start local documentation server
mkdocs serve
```

Visit `http://127.0.0.1:8000` to browse the documentation locally.

## Reference Applications

Minimal reference applications demonstrating Azure Functions patterns:

- `apps/python/` — v2 programming model with blueprints and OpenTelemetry
- `apps/nodejs/` — v4 programming model with HTTP, Timer, Queue, and Event Hub triggers
- `apps/java/` — Maven-based with HTTP and Timer triggers
- `apps/dotnet/` — Isolated worker model with HTTP and Timer triggers

## Infrastructure as Code

Bicep templates for all four hosting plans in `infra/`:

- `main.bicep` — Flex Consumption reference architecture (VNet + Private Endpoint)
- `consumption/` — Consumption (Y1) plan
- `flex-consumption/` — Flex Consumption (FC1) plan
- `premium/` — Premium (EP) plan
- `dedicated/` — Dedicated (App Service Plan)

## Troubleshooting Labs

Hands-on labs in `labs/` that reproduce real-world Azure Functions issues.

## Contributing

Contributions welcome. Please ensure:
- All CLI examples use long flags (`--resource-group`, not `-g`)
- All documents include mermaid diagrams
- All content references Microsoft Learn with source URLs
- No PII in CLI output examples

## Related Projects

| Repository | Description |
|---|---|
| [azure-virtual-machine-practical-guide](https://github.com/yeongseon/azure-virtual-machine-practical-guide) | Azure Virtual Machines practical guide |
| [azure-networking-practical-guide](https://github.com/yeongseon/azure-networking-practical-guide) | Azure Networking practical guide |
| [azure-storage-practical-guide](https://github.com/yeongseon/azure-storage-practical-guide) | Azure Storage practical guide |
| [azure-app-service-practical-guide](https://github.com/yeongseon/azure-app-service-practical-guide) | Azure App Service practical guide |
| [azure-container-apps-practical-guide](https://github.com/yeongseon/azure-container-apps-practical-guide) | Azure Container Apps practical guide |
| [azure-kubernetes-service-practical-guide](https://github.com/yeongseon/azure-kubernetes-service-practical-guide) | Azure Kubernetes Service practical guide |
| [azure-monitoring-practical-guide](https://github.com/yeongseon/azure-monitoring-practical-guide) | Azure Monitoring practical guide |

## Disclaimer

This is an independent community project. Not affiliated with or endorsed by Microsoft. Azure and Azure Functions are trademarks of Microsoft Corporation.

## License

[MIT](LICENSE)
