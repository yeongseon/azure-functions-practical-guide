# Azure Functions 실무 가이드

📘 **문서 사이트:** <https://yeongseon.github.io/azure-functions-practical-guide/>

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

[![Docs](https://github.com/yeongseon/azure-functions-practical-guide/actions/workflows/docs.yml/badge.svg)](https://github.com/yeongseon/azure-functions-practical-guide/actions/workflows/docs.yml)
[![CI](https://github.com/yeongseon/azure-functions-practical-guide/actions/workflows/ci.yml/badge.svg)](https://github.com/yeongseon/azure-functions-practical-guide/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

첫 배포부터 운영 환경의 트러블슈팅까지, Azure Functions에서 서버리스 애플리케이션을 실행하기 위한 포괄적인 가이드입니다.

## 이 가이드의 대상

- Azure Functions를 처음 구축하는 개발자
- 운영 환경의 Function App을 관리하는 엔지니어
- 타임아웃, 콜드 스타트, 스케일링, 네트워킹 및 배포 문제를 조사하는 기술 지원 엔지니어
- Flex Consumption, Premium, Dedicated 및 기존 Consumption 워크로드 사이에서 고민하는 팀

## 권장 시작 경로

| 시나리오 | 권장 플랜 | 시작하기 |
|---|---|---|
| 새로운 서버리스 앱 | **Flex Consumption** | [Flex Consumption 튜토리얼](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) |
| 기존 Consumption 워크로드 | Consumption (기존) | [Consumption 튜토리얼](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) |
| 상시 대기 인스턴스 또는 VNet 집중형 | Premium | [Premium 튜토리얼](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) |
| 기존 App Service 플랜 자산 | Dedicated | [Dedicated 튜토리얼](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) |
| 컨테이너 네이티브 호스팅 | Container Apps | 계획됨 — [호스팅 범위](#hosting-scope) 참조 |

## 주요 내용

| 섹션 | 설명 | 상태 |
|---------|-------------|--------|
| [시작하기](https://yeongseon.github.io/azure-functions-practical-guide/) | 개요, 학습 경로 및 저장소 맵 | 포괄적임 |
| [플랫폼](https://yeongseon.github.io/azure-functions-practical-guide/platform/) | 아키텍처, 호스팅 플랜, 스케일링, 네트워킹, 보안 | 포괄적임 |
| [베스트 프랙티스](https://yeongseon.github.io/azure-functions-practical-guide/best-practices/) | 호스팅 선택, 트리거, 스케일링, 안정성, 보안, 배포 | 포괄적임 |
| [언어별 가이드](https://yeongseon.github.io/azure-functions-practical-guide/language-guides/) | Python, Node.js, Java 및 .NET을 위한 단계별 튜토리얼 | 포괄적임 |
| [운영](https://yeongseon.github.io/azure-functions-practical-guide/operations/) | 배포, 모니터링, 알림, 비용 최적화, 복구 | 포괄적임 |
| [트러블슈팅](https://yeongseon.github.io/azure-functions-practical-guide/troubleshooting/) | 플레이북, KQL 쿼리, 방법론 및 실습 랩 | 랩 검증됨 |
| [참조](https://yeongseon.github.io/azure-functions-practical-guide/reference/) | CLI 치트시트, host.json, 플랫폼 제한 사항 | 포괄적임 |

**상태 범례**: **랩 검증됨** = 포괄적임 + 재현 가능한 실습 랩을 통한 가이드 입증 · **포괄적임** = 전체 섹션 완료, MSLearn 검증됨, 운영 환경 준비 완료 · **게시됨** = 핵심 콘텐츠 준비됨, 계속 확장 중 · **진행 중** = 콘텐츠 일부 작성됨, 활발히 개발 중 · **계획됨** = 자리 표시자, 콘텐츠 아직 시작되지 않음

## 호스팅 범위

이 가이드는 현재 Azure Functions의 클래식 호스팅 플랜에 중점을 둡니다:

- **Flex Consumption (FC1)** — 대부분의 새로운 서버리스 워크로드에 권장되는 기본값
- **Consumption (Y1)** — 기존 워크로드 및 마이그레이션 참조를 위해 유지되는 레거시
- **Premium (EP)** — 엔터프라이즈 네트워킹을 지원하는 상시 대기 인스턴스
- **Dedicated (App Service Plan)** — 기존 App Service 자산을 위한 고정 용량

Azure Functions용 Azure Container Apps 호스팅은 별도의 섹션으로 계획되어 있습니다.

## 언어별 가이드

- **Python** (v2 데코레이터 모델, 4개 호스팅 플랜 트랙)
- **Node.js** (v4 프로그래밍 모델, 4개 호스팅 플랜 트랙)
- **Java** (4개 호스팅 플랜 트랙)
- **.NET** (격리 작업자(isolated worker) 모델, 4개 호스팅 플랜 트랙)

각 가이드는 로컬 개발, 첫 배포, 설정, 로깅, 코드형 인프라(IaC), CI/CD 및 트리거 확장을 다룹니다.

## 빠른 시작

```bash
git clone https://github.com/yeongseon/azure-functions-practical-guide.git
cd azure-functions-practical-guide

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-docs.txt

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

기여는 언제나 환영합니다! 다음 사항은 [기여 가이드](https://yeongseon.github.io/azure-functions-practical-guide/contributing/)를 참조하세요:

- 저장소 구조 및 콘텐츠 구성
- 문서 템플릿 및 작성 표준
- CLI 명령 스타일 및 PII 규칙
- 로컬 개발 설정 및 빌드 검증
- 풀 리퀘스트 프로세스

## 관련 프로젝트

| 저장소 | 설명 |
|---|---|
| [azure-virtual-machine-practical-guide](https://github.com/yeongseon/azure-virtual-machine-practical-guide) | Azure Virtual Machines 실무 가이드 |
| [azure-networking-practical-guide](https://github.com/yeongseon/azure-networking-practical-guide) | Azure Networking 실무 가이드 |
| [azure-storage-practical-guide](https://github.com/yeongseon/azure-storage-practical-guide) | Azure Storage 실무 가이드 |
| [azure-app-service-practical-guide](https://github.com/yeongseon/azure-app-service-practical-guide) | Azure App Service 실무 가이드 |
| [azure-functions-practical-guide](https://github.com/yeongseon/azure-functions-practical-guide) | Azure Functions 실무 가이드 |
| [azure-communication-services-practical-guide](https://github.com/yeongseon/azure-communication-services-practical-guide) | Azure Communication Services 실무 가이드 |
| [azure-container-apps-practical-guide](https://github.com/yeongseon/azure-container-apps-practical-guide) | Azure Container Apps 실무 가이드 |
| [azure-kubernetes-service-practical-guide](https://github.com/yeongseon/azure-kubernetes-service-practical-guide) | Azure Kubernetes Service 실무 가이드 |
| [azure-architecture-practical-guide](https://github.com/yeongseon/azure-architecture-practical-guide) | Azure Architecture 실무 가이드 |
| [azure-monitoring-practical-guide](https://github.com/yeongseon/azure-monitoring-practical-guide) | Azure Monitoring 실무 가이드 |

## 면책 조항

이 프로젝트는 독립적인 커뮤니티 프로젝트입니다. Microsoft와 제휴하거나 보증을 받지 않았습니다. Azure 및 Azure Functions는 Microsoft Corporation의 상표입니다.

## 라이선스

[MIT](LICENSE)
