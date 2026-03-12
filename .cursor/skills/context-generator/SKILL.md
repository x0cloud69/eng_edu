---
name: context-generator
description: >
  Generates Context JSON files for a new project following the AI-Native SaaS Standard Framework methodology.
  Use when the user says "새 프로젝트 시작", "context 생성", "Phase 1 시작", "프로젝트 초기화",
  "generate context", "init project", or any request to set up a new project's governance and workflow definitions.
---

# Context Generator — AI-Native SaaS 표준 프레임워크

## 역할

새 프로젝트를 시작할 때 `.cursor/context/` 폴더에 들어갈 17개 Context JSON 파일을
방법론(Phase 0~3)에 따라 순서대로 생성한다.

## 핵심 원칙

17개 파일 중:
- **🔴 3개**는 프로젝트마다 반드시 새로 작성해야 한다
- **🟡 2개**는 프로젝트에 맞게 조정할 수 있다
- **🟢 12개**는 프레임워크 표준이므로 그대로 복사한다

따라서 이 Skill의 핵심은 **🔴 3개 파일을 사용자와 대화하며 생성하는 것**이다.

---

## Step 0: 사용자에게 프로젝트 정보 수집

아래 정보를 대화형으로 수집한다. 한 번에 전부 묻지 말고, 자연스럽게 나누어 묻는다.

### 필수 정보 (🔴 project_context.json용)
1. **프로젝트 이름** (예: smart-factory, hr-management)
2. **핵심 문제 정의** — 이 프로젝트가 해결하려는 문제 한 줄
3. **주요 이해관계자** — 누가 이 시스템을 쓰는가 (역할 2~5개)
4. **목표 KPI** — 측정 가능한 성공 지표 3~7개
5. **기술 스택 변경 여부** — 기본(Python/FastAPI/React/PostgreSQL)에서 변경할 게 있는지

### 필수 정보 (🔴 persona_context.json용)
6. **주요 사용자 페르소나** — 2~5명 (이름, 역할, 핵심 고민)
7. **핵심 사용 시나리오** — 2~4개 (happy path + edge case)

### 필수 정보 (🔴 scope_context.json용)
8. **In-Scope** — 이 프로젝트가 포함하는 범위 (주요 기능 5~9개)
9. **Out-of-Scope** — 명시적으로 제외하는 범위 (5~9개)

### 선택 정보 (🟡 조정용)
10. **Authority Level 기본값** — L0 / L1(기본) / L2 / L3
11. **SLA 조정** — 기본(P1:24h, P2:1h, P3:48h)에서 변경할 게 있는지
12. **추가 Agent** — 기본 7개(Orch, UIUX-A, Front-A, Back-A, Test-A, Monitor-A, Evol-A) 외 추가할 Agent가 있는지

---

## Step 1: Phase 0 — Foundation (🟢 표준 복사 2개)

아래 파일을 프레임워크 표준에서 **그대로 복사**한다.
사용자의 기술 스택 변경 요청이 있으면 해당 부분만 수정한다.

### 1-1. `saas_foundation.json`
- 아키텍처(멀티테넌트 Row-Level, i18n), 12개 공통 모듈
- LLM Commons, 보안(Zero-Trust), 디자인 시스템, DB 스키마, 인프라
- **수정 가능**: 기술 스택이 다르면 해당 섹션만 변경

### 1-2. `saas_implementation.json`
- Backend 15단계 + Frontend 15단계 파일 생성 순서
- Domain 구조, 설계 결정 11개, 금지 패턴 12개
- **수정 없음**: 구현 순서와 패턴은 프레임워크 표준

---

## Step 2: Phase 1 — Vision & Role (🔴 3개 생성 + 🟡 2개 조정 + 🟢 4개 복사)

### 2-1. 🔴 `project_context.json` — 반드시 새로 작성

```json
{
  "_meta": {
    "version": "1.0.0",
    "phase": "Phase 1 — Vision & Role",
    "description": "{프로젝트명} 프로젝트 컨텍스트",
    "dependencies": []
  },
  "problem_statement": {
    "core_problem": "{사용자가 정의한 핵심 문제}",
    "sub_problems": ["{하위 문제 1}", "{하위 문제 2}", "{하위 문제 3}"],
    "assumptions": ["{가정 1}", "{가정 2}"],
    "constraints": ["{제약 1}", "{제약 2}"]
  },
  "stakeholders": {
    "primary": [
      {"role": "{역할}", "goal": "{목표}", "pain_point": "{고충}"}
    ],
    "secondary": [],
    "conflicts": []
  },
  "kpi": [
    {
      "id": "KPI-01",
      "name": "{KPI 이름}",
      "metric": "{측정 방법}",
      "target": "{목표 수치}",
      "current": "{현재 수치 또는 N/A}",
      "owner": "{담당 역할}"
    }
  ],
  "success_criteria": [
    "{성공 기준 1}",
    "{성공 기준 2}"
  ],
  "value_proposition": {
    "brand_trust": "{브랜드/신뢰 관점의 가치}",
    "user_experience": "{사용자 경험 관점의 가치}",
    "operational_efficiency": "{운영 효율 관점의 가치}"
  },
  "tech_stack": {
    "backend": "Python 3.11+ / FastAPI / SQLAlchemy 2.0 async",
    "frontend": "TypeScript / React 18 / Next.js 14",
    "database": "PostgreSQL 16",
    "cache": "Redis 7",
    "llm": "Anthropic Claude",
    "infra": "Docker Compose (dev) / K8s (prod)"
  }
}
```

**생성 규칙:**
- `problem_statement.core_problem`은 사용자가 말한 핵심 문제를 한 문장으로
- `stakeholders`는 최소 2명, 최대 5명
- `kpi`는 최소 3개, 최대 7개 — 반드시 측정 가능해야 함
- `tech_stack`은 기본값 유지, 사용자가 변경 요청한 부분만 수정

---

### 2-2. 🔴 `persona_context.json` — 반드시 새로 작성

```json
{
  "_meta": {
    "version": "1.0.0",
    "phase": "Phase 1 — Persona & Scenario",
    "dependencies": ["project_context.json"]
  },
  "personas": [
    {
      "id": "P-01",
      "name": "{페르소나 이름}",
      "role": "{역할}",
      "department": "{부서}",
      "experience_level": "senior|mid|junior",
      "pain_points": ["{고충 1}", "{고충 2}"],
      "success_criteria": ["{성공 기준 1}"],
      "ai_trust_level": "L0|L1",
      "key_concerns": ["{우려 1}"],
      "interaction_pattern": "{AI와의 상호작용 패턴}"
    }
  ],
  "scenarios": [
    {
      "id": "SC-01",
      "name": "{시나리오 이름}",
      "type": "happy_path|edge_case|error_recovery",
      "persona": "P-01",
      "trigger": "{시작 조건}",
      "steps": ["{단계 1}", "{단계 2}", "{단계 3}"],
      "expected_outcome": "{기대 결과}",
      "ai_intervention_points": [
        {"step": 1, "type": "suggestion|automation|gate", "level": "L0|L1"}
      ]
    }
  ]
}
```

**생성 규칙:**
- 페르소나는 project_context.json의 stakeholders와 연결
- 시나리오는 최소 2개 (happy_path 1개 + edge_case 1개)
- ai_intervention_points는 AI가 개입하는 구체적 지점 명시

---

### 2-3. 🔴 `scope_context.json` — 반드시 새로 작성

```json
{
  "_meta": {
    "version": "1.0.0",
    "phase": "Phase 1 — Scope Definition",
    "dependencies": ["project_context.json"]
  },
  "principles": [
    "Framework Level Only — 프레임워크 수준의 표준만 정의",
    "Reusability First — 재사용 가능한 구조 우선",
    "Governance Boundary — 거버넌스 경계 내에서만 작동"
  ],
  "decision_questions": [
    "이 기능이 프레임워크 표준에 해당하는가?",
    "다른 프로젝트에서도 재사용 가능한가?",
    "거버넌스 경계를 벗어나지 않는가?"
  ],
  "in_scope": [
    {"id": "IS-01", "item": "{범위 내 항목}", "description": "{설명}"},
    {"id": "IS-02", "item": "{범위 내 항목}", "description": "{설명}"}
  ],
  "out_of_scope": [
    {"id": "OS-01", "item": "{범위 외 항목}", "reason": "{제외 이유}"},
    {"id": "OS-02", "item": "{범위 외 항목}", "reason": "{제외 이유}"}
  ],
  "scope_change_control": {
    "approval_required": "PM + AI Architect",
    "trigger_conditions": [
      "이해관계자 요구 변경",
      "기술적 제약 발견",
      "KPI 목표 변경"
    ],
    "documents_to_update": [
      "scope_context.json",
      "project_context.json",
      "rr_matrix_context.json"
    ]
  }
}
```

**생성 규칙:**
- in_scope: 최소 5개, 최대 9개
- out_of_scope: 최소 5개, 최대 9개 — 반드시 reason 포함
- project_context.json의 문제 정의와 정합성 확인

---

### 2-4. 🟡 `governance.json` — 표준 복사 후 조정

**그대로 복사**하되, 사용자가 요청한 경우만 수정:
- `project_governance.authority_level` — 기본 L1
- `project_governance.risk_level` — 기본 HIGH
- Agent Authority Model — 기본 7개 Agent, 추가 Agent가 있으면 추가

---

### 2-5. 🟡 `rr_matrix_context.json` — 표준 복사 후 조정

**그대로 복사**하되, 사용자가 요청한 경우만 수정:
- 조직 구조에 맞는 역할(Human Role) 조정
- 추가 Agent가 있으면 RACI 행 추가

---

### 2-6~2-9. 🟢 표준 복사 (4개)

아래 파일은 **변경 없이 복사**:
- `governance_charter.json` — 5대 원칙, 데이터 분류, 위반 절차
- `governance_rules_context.json` — AI 리스크 5종, Zero-Trust, 승인 매트릭스
- `hitl_context.json` — P1/P2/P3 패턴, DB 스키마, SLA
- `operation_standards.json` — 5대 원칙, RACI, 보안 표준

---

## Step 3: Phase 2 — Workflow (🟢 표준 복사 1개)

### 3-1. `workflow_context.json`
- 5-Layer 모델, 9 Decision Gates, 10 Escalation Rules
- **변경 없이 복사** — Gate Approver만 조직에 맞게 조정 가능

---

## Step 4: Phase 3 — Capability (🟢 표준 복사 5개)

아래 5개 파일은 **변경 없이 복사**:

| 파일 | 내용 |
|------|------|
| `phase3_context.json` | Boilerplate 10개, 코드 생성 규칙, 모듈 템플릿 |
| `skill_context.json` | 4 Core + 9 Domain Skills |
| `tool_context.json` | 11 Tools + Agent 권한 매트릭스 |
| `system_prompt_context.json` | 5-Layer 프롬프트, 8 Guardrails, 5 Injection 방어 |
| `memory_context.json` | 4계층 Memory, MemoryStore 인터페이스 |

---

## Step 5: 생성 완료 후 검증

### 정합성 체크 (필수)

1. **project_context → scope_context**
   - 문제 정의의 모든 하위 문제가 in_scope에 포함되어 있는가?
   - KPI 측정에 필요한 기능이 in_scope에 있는가?

2. **project_context → persona_context**
   - 모든 stakeholder가 persona로 연결되어 있는가?
   - 각 페르소나의 pain_point가 문제 정의와 일치하는가?

3. **persona_context → scope_context**
   - 각 시나리오의 기능이 in_scope 범위 안에 있는가?
   - edge_case 시나리오가 out_of_scope에 해당하지 않는가?

4. **governance → rr_matrix**
   - Authority Level이 Agent별 권한과 일치하는가?
   - 추가 Agent가 있으면 양쪽 모두 반영되었는가?

### 파일 수 확인

```
.cursor/context/ 폴더에 17개 파일이 있어야 한다:

Phase 0 (2개): saas_foundation.json, saas_implementation.json
Phase 1 (7개): project_context.json, persona_context.json, scope_context.json,
               governance.json, rr_matrix_context.json,
               governance_charter.json, governance_rules_context.json,
               hitl_context.json, operation_standards.json
Phase 2 (1개): workflow_context.json
Phase 3 (5개): phase3_context.json, skill_context.json, tool_context.json,
               system_prompt_context.json, memory_context.json
```

---

## Reference Files
- @.cursor/context/ — 현재 프레임워크의 17개 Context JSON (참조 구현)
- @.cursor/rules/00_master.mdc — 마스터 규칙 (Context 목록 및 우선순위)
- @.cursor/rules/03_context_management.mdc — Context 관리 규칙
