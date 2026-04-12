# Azure Functions 实操指南

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

从首次部署到生产环境故障排除，在 Azure Functions 上运行无服务器应用程序的全方位指南。

## 主要内容

| 章节 | 描述 |
|---------|-------------|
| [从这里开始 (Start Here)](https://yeongseon.github.io/azure-functions-practical-guide/) | 概述、学习路径和仓库地图 |
| [平台 (Platform)](https://yeongseon.github.io/azure-functions-practical-guide/platform/) | 架构、托管计划、扩展、网络、安全 |
| [最佳实践 (Best Practices)](https://yeongseon.github.io/azure-functions-practical-guide/best-practices/) | 托管选择、触发器、扩展、可靠性、安全、部署 |
| [语言指南 (Language Guides)](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) | Python、Node.js、Java 和 .NET 的分步教程 |
| [运营 (Operations)](https://yeongseon.github.io/azure-functions-practical-guide/operations/) | 部署、监控、告警、成本优化、恢复 |
| [故障排除 (Troubleshooting)](https://yeongseon.github.io/azure-functions-practical-guide/troubleshooting/) | 实战手册、KQL 查询、方法论和动手实验 |
| [参考 (Reference)](https://yeongseon.github.io/azure-functions-practical-guide/reference/) | CLI 速查表、host.json、平台限制 |

## 语言指南

- **Python** (v2 装饰器模型，4 个托管计划轨道)
- **Node.js** (v4 编程模型，4 个托管计划轨道)
- **Java** (4 个托管计划轨道)
- **.NET** (隔离工作器模型，4 个托管计划轨道)

每个指南都涵盖：本地开发、首次部署、配置、日志记录、基础设施即代码 (IaC)、CI/CD 和触发器扩展。

## 快速入门

```bash
# 克隆仓库
git clone https://github.com/yeongseon/azure-functions-practical-guide.git

# 安装 MkDocs 依赖
pip install mkdocs-material mkdocs-minify-plugin

# 启动本地文档服务器
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

欢迎贡献。请确保：
- 所有 CLI 示例使用长标记 (使用 `--resource-group` 而不是 `-g`)
- 所有文档包含 Mermaid 图表
- 所有内容参考 Microsoft Learn 并附带源 URL
- CLI 输出示例中不含个人身份信息 (PII)

## 相关项目

| 仓库 | 描述 |
|---|---|
| [azure-virtual-machine-practical-guide](https://github.com/yeongseon/azure-virtual-machine-practical-guide) | Azure Virtual Machines 实操指南 |
| [azure-networking-practical-guide](https://github.com/yeongseon/azure-networking-practical-guide) | Azure Networking 实操指南 |
| [azure-storage-practical-guide](https://github.com/yeongseon/azure-storage-practical-guide) | Azure Storage 实操指南 |
| [azure-app-service-practical-guide](https://github.com/yeongseon/azure-app-service-practical-guide) | Azure App Service 实操指南 |
| [azure-container-apps-practical-guide](https://github.com/yeongseon/azure-container-apps-practical-guide) | Azure Container Apps 实操指南 |
| [azure-kubernetes-service-practical-guide](https://github.com/yeongseon/azure-kubernetes-service-practical-guide) | Azure Kubernetes Service 实操指南 |
| [azure-monitoring-practical-guide](https://github.com/yeongseon/azure-monitoring-practical-guide) | Azure Monitoring 实操指南 |

## 免责声明

这是一个独立的社区项目。与 Microsoft 无关，也不受其认可。Azure 和 Azure Functions 是 Microsoft Corporation 的商标。

## 许可证

[MIT](LICENSE)
