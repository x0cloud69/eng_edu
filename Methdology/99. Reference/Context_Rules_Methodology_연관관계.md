# Context, Rules, Methodology 연관관계 및 목적

> **작성일:** 2026년 3월  
> **목적:** `.cursor/context`, `.cursor/rules`, `WBS/Methodology` 폴더 및 문서 간 연관관계와 각 목적을 정리한 참조 문서

---

## 1. 전체 구조 개요

```
WBS Methodology (문서)          →    .cursor/context (JSON)    →    .cursor/rules (MDC)
     ↓                                    ↓                              ↓
  방법론·가이드                    Cursor AI가 참조하는 컨텍스트         코드 생성 규칙
```

- **WBS Methodology**: 사람이 읽는 방법론·가이드 문서
- **.cursor/context**: Cursor AI가 코드 생성 시 참조하는 구조화된 JSON 컨텍스트
- **.cursor/rules**: Cursor AI가 코드 생성 시 적용하는 규칙

흐름: **WBS Methodology → context JSON 추출/정리 → rules로 구체화 → 코드 생성**

---

## 2. .cursor/context — Cursor AI 컨텍스트

**역할:** Cursor AI가 코드 생성 시 참조하는 **구조화된 JSON 컨텍스트**.

| 파일 | Phase | 목적 |
|------|-------|------|
| `project_context.json` | Phase 1 | 문제 정의, 범위, 이해관계자, KPI, 기술 스택 |
| `persona_context.json` | Phase 1 | Persona, 사용 시나리오 |
| `rr_matrix_context.json` | Phase 1 | Agent R&R, 역할·책임 매트릭스 |
| `governance.json` | Phase 1 | Authority Level, 자율성 모델 |
| `hitl_context.json` | Phase 1 | Human-in-the-Loop 구조(P1/P2/P3), ApprovalGate 구현 기준 |
| `governance_charter.json` | Phase 1 | 거버넌스 헌장, 5대 원칙, 위반 시 대응 |
| `operation_standards.json` | Phase 1 | 운영 표준(0_0~0_C), 5대 원칙 |
| `workflow_context.json` | Phase 2 | Agent 계층, Workflow, Gate, Tool, Escalation |
| `saas_foundation.json` | Phase 0 | SaaS 공통 기반(멀티테넌시, 인증, LLM 등) |
| `phase3_context.json` | Phase 3 | Boilerplate 연계, 파일별 do/don't |
| `saas_implementation.json` | Phase 0 | 구현 순서, 금지 패턴 |

---

## 3. .cursor/rules — 코드 생성 규칙

**역할:** Cursor AI가 **코드 생성 시 적용하는 규칙**.

| 파일 | 우선순위 | 목적 |
|------|----------|------|
| `00_master.mdc` | - | 마스터 규칙, 참조 파일 목록, 우선순위 정의 |
| `01_principles.mdc` | 1순위 | 5대 원칙 |
| `02_security.mdc` | 2순위 | 보안·데이터 |
| `03_context_management.mdc` | 3순위 | Context 3계층, 변경 절차 |
| `04_saas_stack.mdc` | 5순위 | SaaS 기술 스택, 파일 생성 순서 |
| `05_naming_errors.mdc` | 6순위 | Naming Rule, 에러 코드 체계 |
| `06_api_patterns.mdc` | 7순위 | REST API, React Query 패턴 |

`00_master.mdc`에서 context 파일과 rules 파일의 참조 관계를 정의한다.

---

## 4. WBS Methodology — 방법론 문서

### 4.1 0. SaaS Foundation

**역할:** AI Agent SaaS 개발의 **기술·구조 기준**.

| 문서 | 목적 |
|------|------|
| `0.1.1 AI Agent Development Framework.md` | 프레임워크 개요 |
| `0.1.2 AI Agent SaaS — Implementation Guide.md` | 구현 가이드 |
| `0.1.3 AI Agent SaaS — Quick Reference Card.md` | 개발 시 즉시 참조용 규칙(Naming, API, DB 등) |

→ `saas_foundation.json`, `05_naming_errors.mdc`, `06_api_patterns.mdc`의 **원본** 역할.

---

### 4.2 1. Vision and Role

**역할:** Phase 1 **전략·역할 정의** 방법론.

| 문서 | 목적 |
|------|------|
| `AI_Agent_Methodology_Phase1.md` | Phase 1 절차, 산출물 정의 |

정의 항목: Problem Definition, Persona, Agent 역할, Authority, HITL, 거버넌스.

→ `project_context.json`, `persona_context.json`, `rr_matrix_context.json`, `governance.json`, `hitl_context.json`, `governance_charter.json`의 **산출 기준**.

---

### 4.3 2. Agent Workflow

**역할:** Phase 2 **Agent Workflow 설계** 방법론.

현재 폴더에는 별도 문서가 없고, 내용은 `workflow_context.json`에 통합되어 있다.

- Layer 모델(L1~L5)
- `standard_flow`, `decision_gates`, `tools`, `escalation_rules`
- `agent_message_spec`, `interaction_rules`

---

### 4.4 3. Capability

**역할:** Phase 3 **Boilerplate 연계·수정** 가이드.

| 문서 | 목적 |
|------|------|
| `3.1.1 Boilerplate 수정가이드.md` | base_agent, base_model, security 등 수정 절차 |
| `3.1.2 Boilerplate Guide.md` | Boilerplate 연계 확인 |

→ `phase3_context.json`의 **문서화 버전**. Boilerplate 파일별 do/don't, 영향 범위, 수정 절차를 설명한다.

---

## 5. 연관관계 다이어그램

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WBS Methodology (문서)                               │
├─────────────────┬─────────────────┬─────────────────┬───────────────────┤
│ 0. SaaS Found.  │ 1. Vision&Role  │ 2. Agent Work.  │ 3. Capability     │
│ (기술 기준)      │ (전략·역할)     │ (Workflow 설계) │ (Boilerplate)     │
└────────┬────────┴────────┬────────┴────────┬────────┴────────┬─────────┘
         │                 │                 │                 │
         ▼                 ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    .cursor/context (JSON)                                │
├──────────────┬──────────────┬──────────────┬──────────────┬──────────────┤
│saas_found.   │project_ctx   │workflow_ctx  │phase3_ctx    │governance_   │
│phase3_ctx    │persona_ctx   │             │saas_impl.   │charter 등    │
│              │rr_matrix     │             │             │              │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    .cursor/rules (MDC)                                   │
│  00_master → 01_principles → 02_security → 03_context → 04~06           │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    실제 코드 (backend/src, frontend/src)                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 6. 요약

| 구분 | 목적 |
|------|------|
| **WBS Methodology** | 사람이 읽는 방법론·가이드 문서 |
| **.cursor/context** | Cursor AI가 참조하는 구조화된 JSON 컨텍스트 |
| **.cursor/rules** | Cursor AI가 코드 생성 시 적용하는 규칙 |

흐름: **WBS Methodology → context JSON 추출/정리 → rules로 구체화 → 코드 생성**
