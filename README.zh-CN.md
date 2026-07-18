# Azure Functions 实操指南

📘 **文档网站：** <https://yeongseon.github.io/azure-functions-practical-guide/>

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

[![Docs](https://github.com/yeongseon/azure-functions-practical-guide/actions/workflows/docs.yml/badge.svg)](https://github.com/yeongseon/azure-functions-practical-guide/actions/workflows/docs.yml)
[![CI](https://github.com/yeongseon/azure-functions-practical-guide/actions/workflows/ci.yml/badge.svg)](https://github.com/yeongseon/azure-functions-practical-guide/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

从首次部署到生产环境故障排除，在 Azure Functions 上运行无服务器应用程序的全方位指南。

## 本指南适用对象

- 首次构建 Azure Functions 的开发人员
- 运营生产级 Function App 的工程师
- 调查超时、冷启动、扩展、网络和部署问题的支持工程师
- 在 Flex Consumption、Premium、Dedicated 和现有 Consumption 工作负载之间进行选择的团队

## 推荐开始路径

| 场景 | 推荐计划 | 从这里开始 |
|---|---|---|
| 新的无服务器应用 | **Flex Consumption** | [Flex Consumption 教程](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) |
| 现有 Consumption 工作负载 | Consumption (旧版) | [Consumption 教程](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) |
| 常备实例或重度使用 VNet | Premium | [Premium 教程](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) |
| 现有 App Service 计划资产 | Dedicated | [Dedicated 教程](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) |
| 容器原生托管 | Container Apps | 已计划 — 参见 [托管范围](#hosting-scope) |

## 主要内容

| 章节 | 描述 | 状态 |
|---------|-------------|--------|
| [从这里开始](https://yeongseon.github.io/azure-functions-practical-guide/) | 概述、学习路径和仓库地图 | 全面 |
| [平台](https://yeongseon.github.io/azure-functions-practical-guide/platform/) | 架构、托管计划、扩展、网络、安全 | 全面 |
| [最佳实践](https://yeongseon.github.io/azure-functions-practical-guide/best-practices/) | 托管选择、触发器、扩展、可靠性、安全、部署 | 全面 |
| [语言指南](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) | Python、Node.js、Java 和 .NET 的分步教程 | 全面 |
| [运营](https://yeongseon.github.io/azure-functions-practical-guide/operations/) | 部署、监控、告警、成本优化、恢复 | 全面 |
| [故障排除](https://yeongseon.github.io/azure-functions-practical-guide/troubleshooting/) | 实战手册、KQL 查询、方法论和动手实验 | 实验已验证 |
| [参考](https://yeongseon.github.io/azure-functions-practical-guide/reference/) | CLI 速查表、host.json、平台限制 | 全面 |

**状态图例**：**实验已验证** = 全面 + 可重现的实验证明了指南的可行性 · **全面** = 完整章节，经过 MSLearn 验证，生产就绪 · **已发布** = 核心内容已就绪，仍持续扩展中 · **进行中** = 部分内容已完成，处于活跃开发中 · **已计划** = 占位符，内容尚未开始

## 托管范围

本指南目前侧重于 Azure Functions 经典托管计划：

- **Flex Consumption (FC1)** — 大多数新无服务器工作负载的推荐默认值
- **Consumption (Y1)** — 旧版；为现有工作负载和迁移参考而维护
- **Premium (EP)** — 具有企业级网络的常备实例
- **Dedicated (App Service Plan)** — 针对现有 App Service 资产的固定容量

针对 Azure Functions 的 Azure Container Apps 托管计划将作为独立章节推出。

## 语言指南

- **Python** (v2 装饰器模型，4 个托管计划轨道)
- **Node.js** (v4 编程模型，4 个托管计划轨道)
- **Java** (4 个托管计划轨道)
- **.NET** (隔离工作器模型，4 个托管计划轨道)

每个指南都涵盖：本地开发、首次部署、配置、日志记录、基础设施即代码 (IaC)、CI/CD 和触发器扩展。

## 快速入门

```bash
git clone https://github.com/yeongseon/azure-functions-practical-guide.git
cd azure-functions-practical-guide

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-docs.txt

mkdocs serve
```

访问 `http://127.0.0.1:8000` 在本地浏览文档。

## 参考应用程序

展示 Azure Functions 模式的最小化参考应用程序：

- `apps/python/` — 使用蓝图和 OpenTelemetry 的 v2 编程模型
- `apps/nodejs/` — 使用 HTTP、Timer、Queue 和 Event Hub 触发器的 v4 编程模型
- `apps/java/` — 使用 HTTP 和 Timer 触发器的 Maven 项目
- `apps/dotnet/` — 使用 HTTP 和 Timer 触发器的隔离工作器模型

## 基础设施即代码

`infra/` 文件夹中包含 4 个托管计划的 Bicep 模板：

- `main.bicep` — Flex Consumption 参考架构 (VNet + Private Endpoint)
- `consumption/` — Consumption (Y1) 计划
- `flex-consumption/` — Flex Consumption (FC1) 计划
- `premium/` — Premium (EP) 计划
- `dedicated/` — Dedicated (App Service Plan)

## 故障排除实验 (Troubleshooting Labs)

`labs/` 文件夹中包含可重现真实 Azure Functions 问题的动手实验。

## 贡献

欢迎贡献！有关以下内容，请参阅我们的 [贡献指南](https://yeongseon.github.io/azure-functions-practical-guide/contributing/)：

- 仓库结构和内容组织
- 文档模板和编写标准
- CLI 命令风格和 PII 规则
- 本地开发设置和构建验证
- 拉取请求流程

## 相关项目

| 仓库 | 描述 |
|---|---|
| [azure-virtual-machine-practical-guide](https://github.com/yeongseon/azure-virtual-machine-practical-guide) | Azure Virtual Machines 实操指南 |
| [azure-networking-practical-guide](https://github.com/yeongseon/azure-networking-practical-guide) | Azure Networking 实操指南 |
| [azure-storage-practical-guide](https://github.com/yeongseon/azure-storage-practical-guide) | Azure Storage 实操指南 |
| [azure-app-service-practical-guide](https://github.com/yeongseon/azure-app-service-practical-guide) | Azure App Service 实操指南 |
| [azure-functions-practical-guide](https://github.com/yeongseon/azure-functions-practical-guide) | Azure Functions 实操指南 |
| [azure-communication-services-practical-guide](https://github.com/yeongseon/azure-communication-services-practical-guide) | Azure Communication Services 实操指南 |
| [azure-container-apps-practical-guide](https://github.com/yeongseon/azure-container-apps-practical-guide) | Azure Container Apps 实操指南 |
| [azure-kubernetes-service-practical-guide](https://github.com/yeongseon/azure-kubernetes-service-practical-guide) | Azure Kubernetes Service 实操指南 |
| [azure-architecture-practical-guide](https://github.com/yeongseon/azure-architecture-practical-guide) | Azure Architecture 实操指南 |
| [azure-monitoring-practical-guide](https://github.com/yeongseon/azure-monitoring-practical-guide) | Azure Monitoring 实操指南 |

## 免责声明

这是一个独立的社区项目。与 Microsoft 无关，也不受其认可。Azure 和 Azure Functions 是 Microsoft Corporation 的商标。

## 许可证

[MIT](LICENSE)
