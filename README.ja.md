# Azure Functions 実務ガイド

📘 **ドキュメントサイト:** <https://yeongseon.github.io/azure-functions-practical-guide/>

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

[![Docs](https://github.com/yeongseon/azure-functions-practical-guide/actions/workflows/docs.yml/badge.svg)](https://github.com/yeongseon/azure-functions-practical-guide/actions/workflows/docs.yml)
[![CI](https://github.com/yeongseon/azure-functions-practical-guide/actions/workflows/ci.yml/badge.svg)](https://github.com/yeongseon/azure-functions-practical-guide/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

最初のデプロイから本番環境のトラブルシューティングまで、Azure Functions でサーバーレスアプリケーションを実行するための包括的なガイドです。

## このガイドの対象読者

- 初めて Azure Functions を構築する開発者
- 本番環境の Function App を運用するエンジニア
- タイムアウト、コールドスタート、スケーリング、ネットワーク、デプロイの問題を調査するサポートエンジニア
- Flex Consumption、Premium、Dedicated、既存の Consumption ワークロードのいずれを選択するか検討しているチーム

## 推奨される開始パス

| シナリオ | 推奨プラン | ここから開始 |
|---|---|---|
| 新規サーバーレスアプリ | **Flex Consumption** | [Flex Consumption チュートリアル](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) |
| 既存の Consumption ワークロード | Consumption (レガシー) | [Consumption チュートリアル](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) |
| 常時稼働インスタンスまたは VNet 重視 | Premium | [Premium チュートリアル](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) |
| 既存の App Service プラン資産 | Dedicated | [Dedicated チュートリアル](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) |
| コンテナネイティブホスティング | Container Apps | 計画中 — [ホスティング範囲](#hosting-scope) を参照 |

## 主な内容

| セクション | 説明 | 状態 |
|---------|-------------|--------|
| [ここから開始](https://yeongseon.github.io/azure-functions-practical-guide/) | 概要、学習パス、およびリポジトリマップ | 包括的 |
| [プラットフォーム](https://yeongseon.github.io/azure-functions-practical-guide/platform/) | アーキテクチャ、ホスティングプラン、スケーリング、ネットワーク、セキュリティ | 包括的 |
| [ベストプラクティス](https://yeongseon.github.io/azure-functions-practical-guide/best-practices/) | ホスティング選択、トリガー、スケーリング、信頼性、セキュリティ、デプロイ | 包括적 |
| [言語別ガイド](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) | Python、Node.js、Java、および .NET のステップバイステップチュートリアル | 包括的 |
| [運用](https://yeongseon.github.io/azure-functions-practical-guide/operations/) | デプロイ、モニタリング、アラート、コスト最適化、リカバリ | 包括的 |
| [トラブルシューティング](https://yeongseon.github.io/azure-functions-practical-guide/troubleshooting/) | プレイブック、KQL クエリ、方法論、およびハンズオンラボ | ラボ検証済み |
| [リファレンス](https://yeongseon.github.io/azure-functions-practical-guide/reference/) | CLI チートシート、host.json、プラットフォームの制限 | 包括的 |

**状態の凡例**: **ラボ検証済み** = 包括的 + 再現可能なラボによりガイダンスを実証済み · **包括的** = セクション全体が完了し、MSLearn で検証済みの本番環境対応 · **公開済み** = コアコンテンツは配置済みで、現在拡張中 · **進行中** = コンテンツの一部が作成済みで、活発に開発中 · **計画中** = プレースホルダーであり、コンテンツは未着手

## ホスティング範囲

このガイドは現在、Azure Functions のクラシックホスティングプランに焦点を当てています：

- **Flex Consumption (FC1)** — ほとんどの新規サーバーレスワークロードに推奨されるデフォルト
- **Consumption (Y1)** — レガシー。既存のワークロードおよび移行リファレンスのために維持
- **Premium (EP)** — エンタープライズネットワークを備えた常時稼働インスタンス
- **Dedicated (App Service Plan)** — 既存の App Service 資産向けの固定容量

Azure Functions の Azure Container Apps ホスティングは、別のセクションとして計画されています。

## 言語別ガイド

- **Python** (v2 デコレータモデル、4 つのホスティングプラントラック)
- **Node.js** (v4 プログラミングモデル、4 つのホスティングプラントラック)
- **Java** (4 つのホスティングプラントラック)
- **.NET** (分離ワーカーモデル、4 つ의 ホスティングプラントラック)

各ガイドでは、ローカル開発、最初のデプロイ、構成、ロギング、Infrastructure as Code (IaC)、CI/CD、およびトリガー拡張について説明します。

## クイックスタート

```bash
git clone https://github.com/yeongseon/azure-functions-practical-guide.git
cd azure-functions-practical-guide

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-docs.txt

mkdocs serve
```

ローカルで `http://127.0.0.1:8000` にアクセスしてドキュメントを閲覧してください。

## リファレンスアプリケーション

Azure Functions のパターンを示す最小限のリファレンスアプリケーションです：

- `apps/python/` — ブループリントと OpenTelemetry を使用した v2 プログラミングモデル
- `apps/nodejs/` — HTTP、Timer、Queue、Event Hub トリガーを使用した v4 プログラミングモデル
- `apps/java/` — HTTP と Timer トリガーを使用した Maven ベース
- `apps/dotnet/` — HTTP と Timer トリガーを使用した分離ワーカーモデル

## Infrastructure as Code

`infra/` フォルダに 4 つのホスティングプランの Bicep テンプレートが含まれています：

- `main.bicep` — Flex Consumption リファレンスアーキテクチャ (VNet + Private Endpoint)
- `consumption/` — Consumption (Y1) プラン
- `flex-consumption/` — Flex Consumption (FC1) プラン
- `premium/` — Premium (EP) プラン
- `dedicated/` — Dedicated (App Service Plan)

## トラブルシューティングラボ (Troubleshooting Labs)

`labs/` フォルダには、実際の Azure Functions の問題を再現するハンズオンラボが含まれています。

## 貢献

貢献を歓迎します！以下の点については [貢献ガイド](https://yeongseon.github.io/azure-functions-practical-guide/contributing/) を確認してください：

- リポジトリ構造とコンテンツの構成
- ドキュメントテンプレートと執筆基準
- CLI コマンドスタイルと PII ルール
- ローカル開発のセットアップとビルドの検証
- プルリクエストプロセス

## 関連プロジェクト

| リポジトリ | 説明 |
|---|---|
| [azure-virtual-machine-practical-guide](https://github.com/yeongseon/azure-virtual-machine-practical-guide) | Azure Virtual Machines 実務ガイド |
| [azure-networking-practical-guide](https://github.com/yeongseon/azure-networking-practical-guide) | Azure Networking 実務ガイド |
| [azure-storage-practical-guide](https://github.com/yeongseon/azure-storage-practical-guide) | Azure Storage 実務ガイド |
| [azure-app-service-practical-guide](https://github.com/yeongseon/azure-app-service-practical-guide) | Azure App Service 実務ガイド |
| [azure-functions-practical-guide](https://github.com/yeongseon/azure-functions-practical-guide) | Azure Functions 実務ガイド |
| [azure-communication-services-practical-guide](https://github.com/yeongseon/azure-communication-services-practical-guide) | Azure Communication Services 実務ガイド |
| [azure-container-apps-practical-guide](https://github.com/yeongseon/azure-container-apps-practical-guide) | Azure Container Apps 実務ガイド |
| [azure-kubernetes-service-practical-guide](https://github.com/yeongseon/azure-kubernetes-service-practical-guide) | Azure Kubernetes Service 実務ガイド |
| [azure-architecture-practical-guide](https://github.com/yeongseon/azure-architecture-practical-guide) | Azure Architecture 実務ガイド |
| [azure-monitoring-practical-guide](https://github.com/yeongseon/azure-monitoring-practical-guide) | Azure Monitoring 実務ガイド |

## 免責事項

これは独立したコミュニティプロジェクトです。Microsoft との提携や承認を受けているものではありません。Azure および Azure Functions は Microsoft Corporation の商標です。

## ライセンス

[MIT](LICENSE)
