# Azure Functions Field Guide

Comprehensive guide for running serverless applications on Azure Functions — from first deployment to production troubleshooting.

## What's Inside

| Section | Description |
|---------|-------------|
| [Start Here](https://yeongseon.github.io/azure-functions/) | Overview, learning paths, and repository map |
| [Platform](https://yeongseon.github.io/azure-functions/platform/) | Architecture, hosting plans, scaling, networking, security |
| [Best Practices](https://yeongseon.github.io/azure-functions/best-practices/) | Hosting selection, triggers, scaling, reliability, security, deployment |
| [Language Guides](https://yeongseon.github.io/azure-functions/language-guides/) | Step-by-step tutorials for Python, Node.js, Java, and .NET |
| [Operations](https://yeongseon.github.io/azure-functions/operations/) | Deployment, monitoring, alerts, cost optimization, recovery |
| [Troubleshooting](https://yeongseon.github.io/azure-functions/troubleshooting/) | Playbooks, KQL queries, methodology, and hands-on labs |
| [Reference](https://yeongseon.github.io/azure-functions/reference/) | CLI cheatsheet, host.json, platform limits |

## Language Guides

- **Python** (v2 decorator model, 4 hosting plan tracks)
- **Node.js** (coming soon)
- **Java** (coming soon)
- **.NET** (coming soon)

Each guide covers: local development, first deploy, configuration, logging, infrastructure as code, CI/CD, and trigger extensions.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yeongseon/azure-functions.git

# Install MkDocs dependencies
pip install mkdocs-material mkdocs-minify-plugin

# Start local documentation server
mkdocs serve
```

Visit `http://127.0.0.1:8000` to browse the documentation locally.

## Reference Applications

Minimal reference applications demonstrating Azure Functions patterns:

- `apps/python/` — v2 programming model with blueprints and OpenTelemetry
- `apps/nodejs/` — Node.js (coming soon)
- `apps/java/` — Java (coming soon)
- `apps/dotnet/` — .NET (coming soon)

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

## Disclaimer

This is an independent community project. Not affiliated with or endorsed by Microsoft. Azure and Azure Functions are trademarks of Microsoft Corporation.

## License

[MIT](LICENSE)
