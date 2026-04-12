# Azure Functions 実務ガイド

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

最初のデプロイから本番環境のトラブルシューティングまで、Azure Functions でサーバーレスアプリケーションを実行するための包括的なガイドです。

## 主な内容

| セクション | 説明 |
|---------|-------------|
| [ここから開始 (Start Here)](https://yeongseon.github.io/azure-functions-practical-guide/) | 概要、学習パス、およびリポジトリマップ |
| [プラットフォーム (Platform)](https://yeongseon.github.io/azure-functions-practical-guide/platform/) | アーキテクチャ、ホスティングプラン、スケーリング、ネットワーク、セキュリティ |
| [ベストプラクティス (Best Practices)](https://yeongseon.github.io/azure-functions-practical-guide/best-practices/) | ホスティング選択、トリガー、スケーリング、信頼性、セキュリティ、デプロイ |
| [言語別ガイド (Language Guides)](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) | Python、Node.js、Java、および .NET のステップバイステップチュートリアル |
| [運用 (Operations)](https://yeongseon.github.io/azure-functions-practical-guide/operations/) | デプロイ、モニタリング、アラート、コスト最適化、リカバリ |
| [トラブルシューティング (Troubleshooting)](https://yeongseon.github.io/azure-functions-practical-guide/troubleshooting/) | プレイブック、KQL クエリ、方法論、およびハンズオンラボ |
| [リファレンス (Reference)](https://yeongseon.github.io/azure-functions-practical-guide/reference/) | CLI チートシート、host.json、プラットフォームの制限 |

## 言語別ガイド

- **Python** (v2 デコレータモデル、4 つのホスティングプラントラック)
- **Node.js** (v4 プログラミングモデル、4 つのホスティングプラントラック)
- **Java** (4 つのホスティングプラントラック)
- **.NET** (分離ワーカーモデル、4 つのホスティングプラントラック)

各ガイドでは、ローカル開発、最初のデプロイ、構成、ロギング、Infrastructure as Code (IaC)、CI/CD、およびトリガー拡張について説明します。

## クイックスタート

```bash
# リポジトリをクローン
git clone https://github.com/yeongseon/azure-functions-practical-guide.git

# MkDocs の依存関係をインストール
pip install mkdocs-material mkdocs-minify-plugin

# ローカルドキュメントサーバーを起動
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

貢献を歓迎します。以下の点を確認してください：
- すべての CLI の例で長いフラグを使用してください (`-g` ではなく `--resource-group`)
- すべてのドキュメントに Mermaid ダイアグラムを含めてください
- すべてのコンテンツは、ソース URL とともに Microsoft Learn を参照してください
- CLI 出力の例に個人情報 (PII) を含めないでください

## 関連プロジェクト

| リポジトリ | 説明 |
|---|---|
| [azure-virtual-machine-practical-guide](https://github.com/yeongseon/azure-virtual-machine-practical-guide) | Azure Virtual Machines 実務ガイド |
| [azure-networking-practical-guide](https://github.com/yeongseon/azure-networking-practical-guide) | Azure Networking 実務ガイド |
| [azure-storage-practical-guide](https://github.com/yeongseon/azure-storage-practical-guide) | Azure Storage 実務ガイド |
| [azure-app-service-practical-guide](https://github.com/yeongseon/azure-app-service-practical-guide) | Azure App Service 実務ガイド |
| [azure-container-apps-practical-guide](https://github.com/yeongseon/azure-container-apps-practical-guide) | Azure Container Apps 実務ガイド |
| [azure-aks-practical-guide](https://github.com/yeongseon/azure-aks-practical-guide) | Azure Kubernetes Service 実務ガイド |
| [azure-monitoring-practical-guide](https://github.com/yeongseon/azure-monitoring-practical-guide) | Azure Monitoring 実務ガイド |

## 免責事項

これは独立したコミュニティプロジェクトです。Microsoft との提携や承認を受けているものではありません。Azure および Azure Functions は Microsoft Corporation の商標です。

## ライセンス

[MIT](LICENSE)
