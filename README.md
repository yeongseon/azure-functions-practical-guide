# Azure Functions Practical Guide

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

![Docs](https://github.com/yeongseon/azure-functions-practical-guide/actions/workflows/docs.yml/badge.svg)
![CI](https://github.com/yeongseon/azure-functions-practical-guide/actions/workflows/ci.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

Comprehensive guide for running serverless applications on Azure Functions — from first deployment to production troubleshooting.

## Who This Guide Is For

- Developers building Azure Functions for the first time
- Engineers operating production Function Apps
- Support engineers investigating timeout, cold start, scaling, networking, and deployment issues
- Teams choosing between Flex Consumption, Premium, Dedicated, and existing Consumption workloads

## Recommended Starting Path

| Scenario | Recommended plan | Start here |
|---|---|---|
| New serverless app | **Flex Consumption** | [Flex Consumption tutorial](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) |
| Existing Consumption workload | Consumption (legacy) | [Consumption tutorial](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) |
| Always-ready instances or VNet-heavy | Premium | [Premium tutorial](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) |
| Existing App Service Plan estate | Dedicated | [Dedicated tutorial](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) |
| Container-native hosting | Container Apps | Planned — see [Hosting Scope](#hosting-scope) |

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

## Hosting Scope

This guide currently focuses on Azure Functions classic hosting plans:

- **Flex Consumption (FC1)** — recommended default for most new serverless workloads
- **Consumption (Y1)** — legacy; maintained for existing workloads and migration reference
- **Premium (EP)** — always-ready instances with enterprise networking
- **Dedicated (App Service Plan)** — fixed-capacity for existing App Service estates

Azure Container Apps hosting for Azure Functions is planned as a separate section.

## Language Guides

- **Python** (v2 decorator model, 4 hosting plan tracks)
- **Node.js** (v4 programming model, 4 hosting plan tracks)
- **Java** (4 hosting plan tracks)
- **.NET** (isolated worker model, 4 hosting plan tracks)

Each guide covers: local development, first deploy, configuration, logging, infrastructure as code, CI/CD, and trigger extensions.

## Quick Start

```bash
git clone https://github.com/yeongseon/azure-functions-practical-guide.git
cd azure-functions-practical-guide

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-docs.txt

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

Contributions welcome! Please see our [Contributing Guide](https://yeongseon.github.io/azure-functions-practical-guide/contributing/) for:

- Repository structure and content organization
- Document templates and writing standards
- CLI command style and PII rules
- Local development setup and build validation
- Pull request process

## Related Projects

| Repository | Description |
|---|---|
| [azure-virtual-machine-practical-guide](https://github.com/yeongseon/azure-virtual-machine-practical-guide) | Azure Virtual Machines practical guide |
| [azure-networking-practical-guide](https://github.com/yeongseon/azure-networking-practical-guide) | Azure Networking practical guide |
| [azure-storage-practical-guide](https://github.com/yeongseon/azure-storage-practical-guide) | Azure Storage practical guide |
| [azure-app-service-practical-guide](https://github.com/yeongseon/azure-app-service-practical-guide) | Azure App Service practical guide |
| [azure-container-apps-practical-guide](https://github.com/yeongseon/azure-container-apps-practical-guide) | Azure Container Apps practical guide |
| [azure-communication-services-practical-guide](https://github.com/yeongseon/azure-communication-services-practical-guide) | Azure Communication Services practical guide |
| [azure-kubernetes-service-practical-guide](https://github.com/yeongseon/azure-kubernetes-service-practical-guide) | Azure Kubernetes Service (AKS) practical guide |
| [azure-architecture-practical-guide](https://github.com/yeongseon/azure-architecture-practical-guide) | Azure Architecture practical guide |
| [azure-monitoring-practical-guide](https://github.com/yeongseon/azure-monitoring-practical-guide) | Azure Monitoring practical guide |

## Disclaimer

This is an independent community project. Not affiliated with or endorsed by Microsoft. Azure and Azure Functions are trademarks of Microsoft Corporation.

## License

[MIT](LICENSE)
