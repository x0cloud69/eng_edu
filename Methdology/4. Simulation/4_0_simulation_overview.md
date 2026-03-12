# Phase 4. Simulation Test — 방법론 문서
> Phase 4 | 버전: v1.0 | 작성: KY Song
> 기준: workflow_context.json (Phase 4), hitl_context.json, phase3_context.json
> Gate: G-07 Evaluation Report 확정 (approver: QA Engineer, HITL: P3, SLA: 48h)

---

## Phase 4 목적

Phase 3에서 구현된 Agent·Module·거버넌스 코드가 **설계 의도대로 동작하는지** 시뮬레이션으로 검증한다.
단순 기능 테스트가 아니라, **AI-Native SaaS 프레임워크로서의 표준 준수**를 확인하는 것이 핵심이다.

### 검증 대상 3축

```
1. Agent 동작    — Agent가 설계대로 실행되는가?
2. 거버넌스 준수  — ApprovalGate, Scope, AuditLog가 작동하는가?
3. SaaS 격리     — 멀티테넌트 데이터가 격리되는가?
```

---

## WBS 구조

```
4. Simulation Test
│
├── 4.1 Agent Role-play Simulation
│   ├── 4.1.1 Multi-Agent Test Run          → 산출물: Simulation Log
│   └── 4.1.2 Conversation Log 생성          → 산출물: Conversation Log
│
├── 4.2 Failure Scenario Test
│   ├── 4.2.1 Loop Failure Test              → 산출물: Issue List
│   └── 4.2.2 Role Conflict Test             → 산출물: Issue List
│
├── 4.3 Governance Compliance Test    ★ 추가
│   ├── 4.3.1 ApprovalGate Flow Test         → 산출물: Gate Test Report
│   ├── 4.3.2 Scope Validation Test          → 산출물: Scope Violation Log
│   └── 4.3.3 AuditLog Integrity Test        → 산출물: Audit Coverage Report
│
├── 4.4 SaaS Isolation Test           ★ 추가
│   ├── 4.4.1 Multi-Tenant Data Isolation    → 산출물: Isolation Test Report
│   └── 4.4.2 Cross-Tenant Access Denial     → 산출물: Isolation Test Report
│
├── 4.5 KPI Baseline Measurement      ★ 추가
│   ├── 4.5.1 Framework KPI 측정             → 산출물: KPI Baseline Report
│   └── 4.5.2 Performance Benchmark          → 산출물: Performance Report
│
└── 4.6 Evaluation Report & G-07 Gate ★ 추가
    ├── 4.6.1 Evaluation Report 작성         → 산출물: Evaluation Report
    └── 4.6.2 G-07 Gate 승인                 → 산출물: approval_requests 기록
```

---

## 4.1 Agent Role-play Simulation

### 목적
Agent가 Orchestrator 경유 원칙을 지키며, 요청 → 분배 → 실행 → 응답 흐름이 정상 동작하는지 검증한다.

### 4.1.1 Multi-Agent Test Run

| 항목 | 내용 |
|------|------|
| 입력 | 승인된 Test Scenario (모듈별 CRUD 시나리오) |
| 실행 | Orchestrator → Capability Agent → Service → Repository 전체 체인 |
| 검증 기준 | AgentResult.success == True, trace_id 체인 일관성, execution_ms 기록 |
| 산출물 | Simulation Log (trace_id, agent_name, action, success, execution_ms) |

**테스트 시나리오:**

| # | 시나리오 | Agent | 예상 결과 |
|---|---------|-------|----------|
| S-01 | 모듈 목록 조회 | 각 모듈 Agent | success=True, items 반환 |
| S-02 | 단건 생성 (승인 후) | 각 모듈 Agent | success=True, 생성된 데이터 반환 |
| S-03 | 단건 조회 | 각 모듈 Agent | success=True, 해당 ID 데이터 |
| S-04 | 수정 (승인 후) | 각 모듈 Agent | success=True, 변경된 데이터 |
| S-05 | 삭제 (soft delete, 승인 후) | 각 모듈 Agent | success=True, deleted=True |
| S-06 | 존재하지 않는 ID 조회 | 각 모듈 Agent | success=False, 에러 메시지 |

### 4.1.2 Conversation Log 생성

| 항목 | 내용 |
|------|------|
| 입력 | S-01 ~ S-06 실행 결과 |
| 실행 | Agent 간 메시지 흐름(AgentMessage) 기록 |
| 검증 기준 | trace_id 일관성, sender/receiver 정확성, message_type 올바름 |
| 산출물 | Conversation Log (JSON, trace_id → 메시지 체인) |

---

## 4.2 Failure Scenario Test

### 목적
의도적으로 실패 상황을 만들어, 프레임워크가 **안전하게 실패**하는지(graceful failure) 검증한다.

### 4.2.1 Loop Failure Test

| 항목 | 내용 |
|------|------|
| 입력 | Failure 기준 정의 (3회 재시도 정책) |
| 실행 | Tool 호출 연속 실패 시나리오 |
| 검증 기준 | 3회 실패 → Orch 에스컬레이션 트리거, Tool 일시 중단 |
| 산출물 | Issue List (trigger, risk_level, escalation_path) |

**테스트 시나리오:**

| # | 시나리오 | 예상 결과 |
|---|---------|----------|
| F-01 | DB 연결 실패 (db=None) | AgentResult(success=False), 에러 메시지 반환 |
| F-02 | 필수 파라미터 누락 | AgentResult(success=False), KeyError 안전 처리 |
| F-03 | 알 수 없는 액션 호출 | AgentResult(success=False), "알 수 없는 액션" 메시지 |
| F-04 | Tool 3회 연속 실패 | Orch 에스컬레이션 트리거 |

### 4.2.2 Role Conflict Test

| 항목 | 내용 |
|------|------|
| 입력 | Agent R&R Matrix (rr_matrix_context.json) |
| 실행 | Agent가 자기 역할 범위를 벗어나는 요청 수행 시도 |
| 검증 기준 | Scope 위반 시 ScopeViolationError → 차단 + 로그 |
| 산출물 | Issue List (violation_type, agent, attempted_action) |

**테스트 시나리오:**

| # | 시나리오 | 예상 결과 |
|---|---------|----------|
| F-05 | MenuAgent(L0)가 db_write Tool 호출 시도 | Scope 초과 → 차단 |
| F-06 | Agent가 Orch 경유 없이 직접 다른 Agent 호출 시도 | 차단 |
| F-07 | L1 Agent가 L2 권한 액션 시도 | ApprovalGate 차단 |

---

## 4.3 Governance Compliance Test ★ 추가

### 목적
프레임워크의 **3대 거버넌스 메커니즘**(ApprovalGate, Scope, AuditLog)이 설계대로 작동하는지 검증한다.

### 4.3.1 ApprovalGate Flow Test

| 항목 | 내용 |
|------|------|
| 입력 | hitl_context.json P1/P2/P3 패턴 정의 |
| 실행 | 각 Authority Level + Risk Level 조합별 Gate 테스트 |
| 검증 기준 | L0=자동통과, L1+=승인필요, HIGH/CRITICAL=무조건 승인필요 |
| 산출물 | Gate Test Report |

**테스트 매트릭스:**

| Authority | Risk | approved_by | 예상 결과 |
|-----------|------|-------------|----------|
| L0 | LOW | 없음 | 자동 통과 (requires_approval=False) |
| L0 | HIGH | 없음 | 자동 통과 (L0는 항상 통과) |
| L1 | MEDIUM | 없음 | 차단 (requires_approval=True) |
| L1 | MEDIUM | "admin" | 통과 |
| L1 | HIGH | 없음 | 차단 |
| L1 | HIGH | "admin" | 통과 |
| L1 | CRITICAL | 없음 | 차단 |
| L1 | CRITICAL | "admin" | 통과 |

### 4.3.2 Scope Validation Test

| 항목 | 내용 |
|------|------|
| 입력 | 각 Agent의 allowed_tools 정의 |
| 실행 | 허용/비허용 Tool 호출 시도 |
| 검증 기준 | 허용 Tool=통과, 비허용 Tool=ScopeViolationError |
| 산출물 | Scope Violation Log |

**테스트 매트릭스:**

| Agent | allowed_tools | 허용 Tool 호출 | 비허용 Tool 호출 |
|-------|--------------|---------------|----------------|
| ESignatureAgent | db_query, db_write | 통과 | api_call_external → 차단 |
| MenuAgent | db_query | 통과 | db_write → 차단 |
| ApprovalsAgent | db_query, db_write | 통과 | file_write → 차단 |
| ReuseAgent | db_query, db_write | 통과 | llm_call → 차단 |

### 4.3.3 AuditLog Integrity Test

| 항목 | 내용 |
|------|------|
| 입력 | 모든 Agent 실행 결과 |
| 실행 | CUD 작업 후 AuditLog 기록 여부 확인 |
| 검증 기준 | L0=미기록, L1+=기록, 성공/실패 모두 기록, execution_ms >= 0 |
| 산출물 | Audit Coverage Report (기록률 100% 확인) |

**검증 항목:**

| # | 검증 | 예상 |
|---|------|------|
| A-01 | L1 Agent 성공 시 audit_logged=True | True |
| A-02 | L1 Agent 실패 시 audit_logged=True | True |
| A-03 | L0 Agent 실행 시 audit_logged=False | False |
| A-04 | execution_ms >= 0 | True |
| A-05 | trace_id가 원본 요청과 일치 | True |

---

## 4.4 SaaS Isolation Test ★ 추가

### 목적
멀티테넌트 환경에서 **데이터가 완전히 격리**되는지 검증한다.

### 4.4.1 Multi-Tenant Data Isolation

| 항목 | 내용 |
|------|------|
| 입력 | Tenant A, Tenant B 테스트 데이터 |
| 실행 | 각 Tenant로 CRUD 수행 후 상호 격리 확인 |
| 검증 기준 | Tenant A 데이터가 Tenant B 쿼리에 노출되지 않음 |
| 산출물 | Isolation Test Report |

### 4.4.2 Cross-Tenant Access Denial

| 항목 | 내용 |
|------|------|
| 입력 | Tenant A가 소유한 데이터 ID |
| 실행 | Tenant B 컨텍스트로 해당 ID 직접 조회 시도 |
| 검증 기준 | Repository의 tenant_id 필터로 None 반환 (접근 거부) |
| 산출물 | Isolation Test Report |

---

## 4.5 KPI Baseline Measurement ★ 추가

### 목적
project_context.json에 정의된 **프레임워크 KPI**의 현재 Baseline을 측정하여, Phase 6 Evolution에서 비교할 기준선을 잡는다.

### 4.5.1 Framework KPI 측정

| KPI | 목표 | 측정 방법 | Phase 4 기준 |
|-----|------|----------|-------------|
| 공통 모듈 재사용률 | 50% 이상 | (공통모듈 사용 수 / 전체 모듈 수) × 100 | Baseline 측정 |
| 감사 대응 준비 기간 | 50% 단축 | AuditLog 조회 → 보고서 생성 소요시간 | Baseline 측정 |
| AI 승인 프로세스 | 30~40% 단축 | ApprovalGate 평균 처리시간 | Baseline 측정 |
| 규제 준수율 | 95% 이상 | governance-checker 통과율 | 측정 |
| Drift 자동 탐지 적용률 | 100% | Monitor-A 적용 모듈 수 | Phase 5에서 측정 |

### 4.5.2 Performance Benchmark

| 항목 | 측정 | 기준 |
|------|------|------|
| Agent 평균 응답시간 | execution_ms 평균 | < 500ms (조회), < 2000ms (CUD) |
| ApprovalGate 오버헤드 | Gate 체크 소요시간 | < 10ms |
| Orchestrator 라우팅 시간 | 요청 → Agent 전달 | < 50ms |

---

## 4.6 Evaluation Report & G-07 Gate ★ 추가

### 목적
4.1~4.5 테스트 결과를 종합하여 **Evaluation Report**를 작성하고, G-07 Gate 승인을 받는다.

### 4.6.1 Evaluation Report 작성

**보고서 구조:**

```
1. 요약 (Executive Summary)
   - 전체 Pass/Fail 비율
   - Critical 이슈 수
   - Phase 5 진행 가능 여부 판정

2. 테스트 결과 상세
   - 4.1 Agent Role-play: Pass/Fail 목록
   - 4.2 Failure Scenario: 발견된 Issue 목록
   - 4.3 Governance Compliance: Gate/Scope/Audit 통과율
   - 4.4 SaaS Isolation: 격리 검증 결과
   - 4.5 KPI Baseline: 측정값 목록

3. Issue 목록
   - CRITICAL: 즉시 수정 필수 (Phase 5 진행 차단)
   - WARNING: 수정 권장 (Phase 5 진행 가능)
   - INFO: 참고 사항

4. 권고 사항
   - Phase 5 배포 전 필수 조치
   - Phase 6 Evolution에서 추적할 항목
```

### 4.6.2 G-07 Gate 승인

| 항목 | 내용 |
|------|------|
| Gate ID | G-07 |
| Gate 이름 | Evaluation Report 확정 Gate |
| HITL 패턴 | P3 (Post-review) |
| 승인자 | QA Engineer |
| SLA | 48시간 |
| 승인 기준 | CRITICAL 이슈 0건, 거버넌스 테스트 100% Pass |
| DB | review_requests INSERT (status=PENDING → CONFIRMED/REVISED/REJECTED) |

**G-07 통과 기준:**

| 조건 | 필수 여부 |
|------|----------|
| 4.1 Agent CRUD 전체 Pass | 필수 |
| 4.2 Failure 시나리오 전체 안전 실패 확인 | 필수 |
| 4.3 ApprovalGate 매트릭스 전체 Pass | 필수 |
| 4.3 AuditLog 기록률 100% | 필수 |
| 4.4 멀티테넌트 격리 전체 Pass | 필수 |
| 4.5 KPI Baseline 측정 완료 | 필수 |
| CRITICAL 이슈 0건 | 필수 |
| WARNING 이슈 조치 계획 수립 | 권장 |

---

## 산출물 요약

| WBS | 산출물 | 형식 | 위치 |
|-----|--------|------|------|
| 4.1.1 | Simulation Log | JSON | backend/tests/results/simulation_log.json |
| 4.1.2 | Conversation Log | JSON | backend/tests/results/conversation_log.json |
| 4.2.1 | Issue List (Loop) | MD | methodology/phase4_simulation/issues/ |
| 4.2.2 | Issue List (Role) | MD | methodology/phase4_simulation/issues/ |
| 4.3.1 | Gate Test Report | MD | methodology/phase4_simulation/reports/ |
| 4.3.2 | Scope Violation Log | JSON | backend/tests/results/scope_violations.json |
| 4.3.3 | Audit Coverage Report | MD | methodology/phase4_simulation/reports/ |
| 4.4 | Isolation Test Report | MD | methodology/phase4_simulation/reports/ |
| 4.5.1 | KPI Baseline Report | MD | methodology/phase4_simulation/reports/ |
| 4.5.2 | Performance Report | MD | methodology/phase4_simulation/reports/ |
| 4.6.1 | Evaluation Report | MD | methodology/phase4_simulation/4_6_evaluation_report.md |
| 4.6.2 | G-07 approval record | DB | review_requests 테이블 |

---

## Phase 3 → Phase 4 → Phase 5 연결

```
Phase 3 (Capability)
  └── 모듈 코드 + Agent 코드 + 거버넌스 코드 완성
        ↓
Phase 4 (Simulation) ← 현재
  ├── 4.1~4.2: 코드가 동작하는가? (기능 검증)
  ├── 4.3~4.4: 거버넌스/격리가 지켜지는가? (표준 검증)
  ├── 4.5: KPI 측정 가능한가? (측정 검증)
  └── 4.6: G-07 통과 → Phase 5 진행 가능
        ↓
Phase 5 (Deploy)
  └── Docker 패키징 + 배포 + G-08 Release Gate
```
