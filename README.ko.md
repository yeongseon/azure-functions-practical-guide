# Azure Functions 실무 가이드

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

첫 배포부터 운영 환경의 트러블슈팅까지, Azure Functions에서 서버리스 애플리케이션을 실행하기 위한 포괄적인 가이드입니다.

## 주요 내용

| 섹션 | 설명 |
|---------|-------------|
| [시작하기 (Start Here)](https://yeongseon.github.io/azure-functions-practical-guide/) | 개요, 학습 경로 및 저장소 맵 |
| [플랫폼 (Platform)](https://yeongseon.github.io/azure-functions-practical-guide/platform/) | 아키텍처, 호스팅 플랜, 스케일링, 네트워킹, 보안 |
| [베스트 프랙티스 (Best Practices)](https://yeongseon.github.io/azure-functions-practical-guide/best-practices/) | 호스팅 선택, 트리거, 스케일링, 안정성, 보안, 배포 |
| [언어별 가이드 (Language Guides)](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) | Python, Node.js, Java, .NET을 위한 단계별 튜토리얼 |
| [운영 (Operations)](https://yeongseon.github.io/azure-functions-practical-guide/operations/) | 배포, 모니터링, 알림, 비용 최적화, 복구 |
| [트러블슈팅 (Troubleshooting)](https://yeongseon.github.io/azure-functions-practical-guide/troubleshooting/) | 플레이북, KQL 쿼리, 방법론, 실습 랩 |
| [참조 (Reference)](https://yeongseon.github.io/azure-functions-practical-guide/reference/) | CLI 치트시트, host.json, 플랫폼 제한 사항 |

## 언어별 가이드

- **Python** (v2 데코레이터 모델, 4개 호스팅 플랜 트랙)
- **Node.js** (v4 프로그래밍 모델, 4개 호스팅 플랜 트랙)
- **Java** (4개 호스팅 플랜 트랙)
- **.NET** (격리 작업자(isolated worker) 모델, 4개 호스팅 플랜 트랙)

각 가이드는 로컬 개발, 첫 배포, 설정, 로깅, 코드형 인프라(IaC), CI/CD, 트리거 확장을 다룹니다.

## 빠른 시작

```bash
# 저장소 복제
git clone https://github.com/yeongseon/azure-functions-practical-guide.git

# MkDocs 의존성 설치
pip install mkdocs-material mkdocs-minify-plugin

# 로컬 문서 서버 시작
mkdocs serve
```

로컬에서 `http://127.0.0.1:8000`에 접속하여 문서를 확인하세요.

## 참조 애플리케이션

Azure Functions 패턴을 보여주는 최소한의 참조 애플리케이션들입니다:

- `apps/python/` — 블루프린트와 OpenTelemetry를 사용하는 v2 프로그래밍 모델
- `apps/nodejs/` — HTTP, Timer, Queue, Event Hub 트리거를 사용하는 v4 프로그래밍 모델
- `apps/java/` — HTTP 및 Timer 트리거를 사용하는 Maven 기반
- `apps/dotnet/` — HTTP 및 Timer 트리거를 사용하는 격리 작업자 모델

## 코드형 인프라(Infrastructure as Code)

`infra/` 폴더에 4개의 호스팅 플랜에 대한 Bicep 템플릿이 포함되어 있습니다:

- `main.bicep` — Flex Consumption 참조 아키텍처 (VNet + Private Endpoint)
- `consumption/` — Consumption (Y1) 플랜
- `flex-consumption/` — Flex Consumption (FC1) 플랜
- `premium/` — Premium (EP) 플랜
- `dedicated/` — Dedicated (App Service Plan)

## 트러블슈팅 실험 (Troubleshooting Labs)

`labs/` 폴더에는 실제 Azure Functions 이슈를 재현하는 실습 실험이 포함되어 있습니다.

## 기여하기

기여는 언제나 환영합니다. 다음 사항을 준수해 주세요:
- 모든 CLI 예제에는 긴 플래그를 사용하세요 (`-g` 대신 `--resource-group`)
- 모든 문서에는 Mermaid 다이어그램을 포함하세요
- 모든 콘텐츠는 출처 URL과 함께 Microsoft Learn을 참조해야 합니다
- CLI 출력 예제에 개인 식별 정보(PII)를 포함하지 마세요

## 관련 프로젝트

| 저장소 | 설명 |
|---|---|
| [azure-virtual-machine-practical-guide](https://github.com/yeongseon/azure-virtual-machine-practical-guide) | Azure Virtual Machines 실무 가이드 |
| [azure-networking-practical-guide](https://github.com/yeongseon/azure-networking-practical-guide) | Azure Networking 실무 가이드 |
| [azure-storage-practical-guide](https://github.com/yeongseon/azure-storage-practical-guide) | Azure Storage 실무 가이드 |
| [azure-app-service-practical-guide](https://github.com/yeongseon/azure-app-service-practical-guide) | Azure App Service 실무 가이드 |
| [azure-container-apps-practical-guide](https://github.com/yeongseon/azure-container-apps-practical-guide) | Azure Container Apps 실무 가이드 |
| [azure-aks-practical-guide](https://github.com/yeongseon/azure-aks-practical-guide) | Azure Kubernetes Service 실무 가이드 |
| [azure-monitoring-practical-guide](https://github.com/yeongseon/azure-monitoring-practical-guide) | Azure Monitoring 실무 가이드 |

## 면책 조항

이 프로젝트는 독립적인 커뮤니티 프로젝트입니다. Microsoft와 제휴하거나 보증을 받지 않았습니다. Azure 및 Azure Functions는 Microsoft Corporation의 상표입니다.

## 라이선스

[MIT](LICENSE)
