# 문서 ↔ Context ↔ Rule 연관 관계 맵
## Standard Framework Project — Phase 1 산출물 기준

---

## 1. 전체 구조 한눈에 보기

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        원천 문서 (Source Documents)                          │
│                                                                             │
│  Phase 0          Phase 1                          Phase 2   Phase 3       │
│  ─────────  ──────────────────────────────────────  ───────  ─────────     │
│  SaaS       1.1    1.2    1.3    1.4    1.5    1.6  Workflow  Build        │
│  Foundation Prob   Persona R&R   Auth   HITL   Gov  Design    Context      │
│  (0_0~0_C)  Frame  Def    Matrix Model  Struct Chart                       │
└──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬────────────┘
       │      │      │      │      │      │      │      │      │
       ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    .cursor/context/ (JSON 컨텍스트 13개)                     │
│                                                                             │
│  saas_         project_    persona_    rr_matrix_  governance. hitl_        │
│  foundation    context     context     context     json        context      │
│  .json         .json       .json       .json                   .json        │
│                                                                             │
│  saas_impl_    scope_      gov_rules_  gov_charter operation_  workflow_    │
│  ementation    context     context     .json       standards   context      │
│  .json         .json       .json                   .json       .json        │
│                                                                             │
│  phase3_                                                                    │
│  context.json                                                               │
└──────┬──────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    .cursor/rules/ (MDC 규칙 8개)                             │
│                                                                             │
│  00_master   01_principles  02_security  03_context    04_saas_stack        │
│  .mdc        .mdc           .mdc         _management   .mdc                 │
│  (인덱스)    (5대 원칙)     (보안)       .mdc          (기술스택)            │
│                                                                             │
│  05_naming_  06_api_        07_scope_                                       │
│  errors.mdc  patterns.mdc   governance.mdc                                  │
│  (네이밍)    (API패턴)      (Scope경계)                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 원천 문서 → Context JSON 매핑

| 원천 문서 | 생성된 Context JSON | 포함 핵심 내용 |
|-----------|---------------------|----------------|
| **1.1 Problem Framing** | `project_context.json` | 문제 정의, 이해관계자, KPI, 가치 제안 |
| **1.1 Problem Framing** (Scope 섹션) | `scope_context.json` | IS-01~09, OS-01~09 Scope 경계 정의 |
| **1.1 Problem Framing** (Governance Rules 섹션) | `governance_rules_context.json` | AI 리스크 임계값, Zero-Trust, Approval 매트릭스 |
| **1.2 Persona Definition** | `persona_context.json` | Persona 3종(P1~P3), Usage Scenario |
| **1.3 Agent R&R Matrix** | `rr_matrix_context.json` | RACI 매핑, Agent별 allowed/forbidden |
| **1.4 Authority Model** | `governance.json` (v1.1 업데이트) | Authority Level L0~L3, Agent별 레벨 결정 |
| **1.5 HITL Structure** | `hitl_context.json` | P1/P2/P3 패턴, DB 스키마, SLA |
| **1.6 Governance Charter** | `governance_charter.json` | 5대 원칙, 데이터 분류, 금지 행동 |
| **Phase 0 SaaS Foundation** (0_0~0_C) | `operation_standards.json` | 5대 원칙 요약, 운영 표준 통합 |
| **Phase 0 SaaS Foundation** | `saas_foundation.json` | 기술 스택, 공통 모듈, 아키텍처 결정 |
| **Phase 0 SaaS Foundation** (Implementation) | `saas_implementation.json` | 파일 생성 순서, 의존성 기준 |
| **Phase 2 Workflow Design** | `workflow_context.json` | Agent 계층, Decision Gate, Escalation |
| **Phase 3 Build** | `phase3_context.json` | Boilerplate 연계 기준 (depends: saas_foundation + workflow + hitl) |

> 💡 1.1 Problem Framing 문서 하나에서 **3개의 Context JSON**이 파생된다는 점에 주의.

---

## 3. 원천 문서 → Rule MDC 매핑

| 원천 문서 | 직접 기반 Rule | 적용 방식 |
|-----------|----------------|-----------|
| **1.1 Problem Framing** (Scope) | `07_scope_governance.mdc` | In-Scope/Out-Scope 코드 생성 경계, 갈등 해결 기준, MVP 품질 게이트 |
| **1.3 Agent R&R Matrix** | `00_master.mdc` (참조) | Agent 코드 생성 시 역할 범위 확인 기준 |
| **1.4 Authority Model** | `00_master.mdc` (Authority Level 섹션) | L0~L3별 코드 적용 기준표 직접 포함 |
| **1.5 HITL Structure** | `00_master.mdc` (참조) | Phase 3 ApprovalGate 구현 기준 문서로 연결 |
| **1.6 Governance Charter** (5대 원칙) | `01_principles.mdc` | 5대 원칙 코드 적용 규칙 (최상위 우선순위) |
| **1.6 Governance Charter** (보안/데이터) | `02_security.mdc` | 데이터 분류, RBAC, LLM 보안, API 키 규칙 |
| **Phase 0** (Context 관리 기준 0_2) | `03_context_management.mdc` | Context 3계층, 변경 절차, 버전 관리 |
| **Phase 0** (SaaS Foundation) | `04_saas_stack.mdc` | 파일 생성 순서, DB/Auth/캐시/Agent 코드 규칙 |
| **Phase 0** (Quick Reference) | `05_naming_errors.mdc` | 네이밍 규칙, 에러 코드 체계 |
| **Phase 0** (Quick Reference) | `06_api_patterns.mdc` | REST 패턴, React Query, 응답 포맷 |

---

## 4. Context JSON 간 의존 관계

```
project_context.json
    ├── scope_context.json          (project_context 참조)
    └── operation_standards.json   (project_context 참조)
        └── persona_context.json   (operation_standards + governance + project_context 참조)

governance.json
    ├── rr_matrix_context.json     (governance 참조)
    ├── workflow_context.json      (governance 참조)
    └── governance_rules_context.json
            ├── governance.json    (Authority Level)
            ├── governance_charter.json (5원칙, 데이터 분류)
            └── hitl_context.json  (P1/P2/P3 패턴)

saas_foundation.json
    └── saas_implementation.json   (saas_foundation 참조)

phase3_context.json  ← 복합 의존 (가장 나중에 생성)
    ├── saas_foundation.json
    ├── workflow_context.json
    └── hitl_context.json
```

---

## 5. Rule MDC 간 우선순위 및 참조 관계

```
00_master.mdc  ← 인덱스 (모든 context + 모든 rule 참조)
│
├── [1순위] 01_principles.mdc   ← 5대 원칙 (최상위. 다른 rule에서 참조됨)
│                                    ↑ 04_saas_stack.mdc가 참조
│                                    ↑ 07_scope_governance.mdc가 참조
│
├── [2순위] 02_security.mdc     ← 보안/데이터 (다른 rule에서 참조됨)
│                                    ↑ 04_saas_stack.mdc가 참조
│                                    ↑ 07_scope_governance.mdc가 참조
│
├── [3순위] 03_context_management.mdc  ← Context 구조 (독립)
│
├── [4순위] 07_scope_governance.mdc    ← Scope 경계 + MVP 게이트
│              └── 참조: 01_principles, 02_security, 04_saas_stack
│
├── [5순위] 00_master.mdc (본 파일)
│
├── [6순위] 04_saas_stack.mdc          ← 기술 스택 규칙
│              └── 참조: 01_principles, 02_security
│
├── [7순위] 05_naming_errors.mdc       ← 네이밍 규칙 (독립)
│
└── [8순위] 06_api_patterns.mdc        ← API 패턴 (독립)
```

---

## 6. 코드 생성 요청 시 Cursor의 참조 흐름

```
Cursor에 코드 생성 요청
         │
         ▼
┌─────────────────────────────────┐
│  00_master.mdc 로드             │  ← 항상 최초 로드
│  → 모든 context JSON 로드       │
└─────────────────────────────────┘
         │
         ├─ In-Scope 판단? ──────────── 07_scope_governance.mdc
         │                               └ scope_context.json (IS/OS 목록)
         │
         ├─ Agent 코드? ─────────────── rr_matrix_context.json (allowed/forbidden)
         │                               governance.json (Authority Level)
         │                               hitl_context.json (승인 게이트 위치)
         │
         ├─ 보안 처리? ──────────────── 02_security.mdc
         │                               governance_charter.json (데이터 분류)
         │                               governance_rules_context.json (Zero-Trust)
         │
         ├─ DB / API 코드? ──────────── 04_saas_stack.mdc
         │                               saas_foundation.json (기술 결정)
         │                               saas_implementation.json (파일 순서)
         │
         ├─ 네이밍? ─────────────────── 05_naming_errors.mdc (독립 규칙)
         │
         ├─ API 응답 패턴? ───────────── 06_api_patterns.mdc
         │                               saas_foundation.json
         │
         └─ 원칙 위반 여부? ──────────── 01_principles.mdc (최우선 체크)
                                          operation_standards.json (5대 원칙 요약)
```

---

## 7. 문서별 "1개 문서가 영향을 미치는 범위" 요약

| 문서 | Context | Rule | 영향 범위 요약 |
|------|---------|------|----------------|
| **1.1 Problem Framing** | 3개 (project, scope, gov_rules) | 1개 (07) | 프로젝트 목표 + Scope 경계 + 리스크 임계값 |
| **1.2 Persona** | 1개 (persona) | 0개 | UX 설계 컨텍스트 |
| **1.3 R&R Matrix** | 1개 (rr_matrix) | 간접 (00 참조) | Agent별 실행 허용 범위 |
| **1.4 Authority Model** | 1개 (governance 일부) | 직접 (00 포함) | 모든 Agent 코드의 승인 게이트 여부 결정 |
| **1.5 HITL Structure** | 1개 (hitl) | 간접 (00 참조) | Phase 3 ApprovalGate 구현의 직접 기준 |
| **1.6 Governance Charter** | 1개 (gov_charter) | 2개 (01, 02) | 모든 코드에 적용되는 5대 원칙 + 보안 규칙 |
| **Phase 0 (SaaS)** | 3개 (saas_f, saas_i, op_std) | 3개 (03, 04, 05, 06) | 기술 스택 표준 전체 |
| **Phase 2 (Workflow)** | 1개 (workflow) | 0개 | Agent 실행 흐름 + Gate 정의 |

---

## 8. 현재 미완성 / Phase 3 이후 추가 예정 항목

| 항목 | 현재 상태 | 생성 시점 | 비고 |
|------|-----------|-----------|------|
| `.cursor/context/agents/*.json` (5개) | **미생성** | Phase 3 시작 시 | Global Context에서 자동 생성 |
| `0_9_Release_Gate.json` | 미생성 | Phase 4~5 | Release Gate 기준 |
| `0_B_Exception_Approval.json` | 미생성 | Phase 4~5 | 예외 승인 절차 |
| `0_5_KPI_Monitoring.json` | 미생성 | Phase 5 | KPI/모니터링 기준 |
| `0_6_Evolution_Loop.json` | 미생성 | Phase 6 | Evolution Loop 기준 |

---

*작성일: 2026-03-09 | Standard Framework Project Phase 1 기준*
