# Phase 6 — Evolution Loop 방법론
> Version: v1.0 | Date: 2026-03-11 | Author: AI Architect
> Status: **DRAFT**
> Predecessor: Phase 5 Deploy & Monitoring (G-08 통과 필수)
> Gate: **G-09 Context 수정 승인 Gate** (Approver: Governance Board, HITL: P1, SLA: 24h)

---

## 1. Phase 6 개요

### 1.1 목적

프로덕션 운영 중 발생하는 KPI Drift를 자동 감지하고, Evolution Agent(Evol-A)가 Context/Workflow 수정 제안을 생성하며, Governance Board 승인을 거쳐 시스템을 지속적으로 개선하는 피드백 루프를 구축한다.

### 1.2 핵심 원칙

> **Principle 5 — 지속적 개선 체계 내재화**
> 1. KPI 및 모니터링 결과는 반드시 개선 활동으로 연결
> 2. Context 수정은 승인 및 회귀 테스트 후 반영
> 3. 반복되는 예외는 구조적 개선 대상으로 전환

### 1.3 Phase 6 범위 (WBS)

| Section | Title | 핵심 산출물 |
|---------|-------|------------|
| 6.1 | Drift Analysis & Pattern Detection | Evol-A trajectory_logs 분석, 패턴 분류 |
| 6.2 | Context Modification Proposal | 수정 제안서 생성, 영향 범위 분석, Risk 평가 |
| 6.3 | G-09 Approval Workflow | Governance Board P1 승인, SLA 24h |
| 6.4 | Regression Test & Validation | Test-A 회귀 테스트, 기존 93개 테스트 재실행 |
| 6.5 | Redeployment & Verification | 승인 후 재배포, Post-Redeploy 모니터링 |
| 6.6 | Periodic Review Cycle | 월 1회 정기 재검증, Evolution Report |

### 1.4 담당 Agent

| Agent | Layer | Authority | 역할 |
|-------|-------|-----------|------|
| Monitor-A | L4 (Monitoring) | L0 | KPI Drift 탐지, trajectory_logs 데이터 제공 |
| Evol-A | L5 (Evolution) | L1 | 로그 분석, Context 수정 제안 생성 |
| Test-A | L3 (Quality) | L1 | Regression Test 실행, 검증 |
| Back-A | L2 (Capability) | L1 | 재배포 실행 |
| Orch | L1 (Orchestration) | L0 | 워크플로우 라우팅, 에스컬레이션 |
| Gov-A | L2 (Governance) | L2 | 거버넌스 규칙 준수 검증 |

### 1.5 선행 조건

- [ ] G-08 Release Gate PASS (Phase 5)
- [ ] 프로덕션 48h 안정 운영 확인
- [ ] KPI 전체 GREEN 유지
- [ ] Monitor-A Drift Detection 활성
- [ ] Post-Deploy Report 제출 완료

---

## 2. Section 6.1 — Drift Analysis & Pattern Detection

### 2.1 Evolution Loop 트리거 조건

| Trigger Type | Condition | Source | Action |
|-------------|-----------|--------|--------|
| 자동 (Drift) | KPI RED (20%+ 하락) | Monitor-A → trajectory_logs | Orch → Evol-A 제안 생성 |
| 자동 (반복 실패) | 동일 Agent 3회 연속 failure | trajectory_logs.failure_tagged | Orch → Evol-A 분석 |
| 수동 (요청) | PM/Architect 개선 요청 | review_requests | Evol-A 분석 시작 |
| 정기 (스케줄) | 월 1회 정기 재검증 | 크론 스케줄 | 전체 KPI + 모델 재검증 |

### 2.2 Evol-A 분석 대상 데이터

```sql
-- Evolution Agent가 분석하는 trajectory_logs 쿼리
SELECT
    agent_code,
    action,
    risk_level,
    failure_reason,
    kpi_metrics,
    COUNT(*) AS occurrence_count,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) AS avg_duration_sec
FROM trajectory_logs
WHERE tenant_id = :tenant_id
  AND failure_tagged = true
  AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY agent_code, action, risk_level, failure_reason
ORDER BY occurrence_count DESC
LIMIT 20;
```

### 2.3 패턴 분류 체계

| Pattern Code | 패턴 | 설명 | 개선 대상 |
|-------------|------|------|----------|
| P-DRIFT | KPI Drift | 특정 KPI가 지속적 하락 | KPI 수집 로직, Agent 실행 로직 |
| P-FAIL-REPEAT | 반복 실패 | 동일 Agent/Action 3회+ 실패 | Agent execute() 로직, Service 레이어 |
| P-LATENCY | 성능 저하 | 응답 시간 500ms+ 초과 빈발 | DB 쿼리 최적화, 캐시 전략 |
| P-GATE-BLOCK | Gate 병목 | 승인 대기 SLA 초과 빈발 | HITL 워크플로우, SLA 조정 |
| P-SCOPE-EXCEED | Scope 위반 | 허용되지 않은 Tool 호출 시도 | Agent allowed_tools 재정의 |
| P-TENANT-LEAK | 테넌트 누출 | Cross-Tenant 데이터 접근 시도 | Service 레이어 격리 로직 |

### 2.4 Analysis Report 출력 형식

```json
{
  "analysis_id": "EVL-2026-03-001",
  "analyzed_at": "2026-03-11T00:00:00Z",
  "analyzed_by": "Evol-A",
  "period": "2026-02-11 ~ 2026-03-11",
  "total_records_analyzed": 1250,
  "failure_records": 42,
  "patterns_detected": [
    {
      "code": "P-DRIFT",
      "kpi_code": "K-02",
      "severity": "HIGH",
      "occurrence": 7,
      "trend": "DECLINING",
      "root_cause_hypothesis": "신규 프로젝트 등록 후 모듈 재사용 미진행",
      "recommended_action": "reuse_usage_records 자동 트래킹 로직 보강"
    }
  ],
  "overall_risk": "MEDIUM",
  "evolution_required": true
}
```

---

## 3. Section 6.2 — Context Modification Proposal

### 3.1 수정 제안서 구조

| Section | 내용 |
|---------|------|
| 1. 요약 | 제안 배경, 트리거, 긴급도 |
| 2. 분석 결과 | Pattern Detection Report 요약 |
| 3. 수정 대상 | 어떤 Context/Rule/Agent를 변경할 것인지 |
| 4. Before/After | 변경 전/후 비교 (diff 형식) |
| 5. 영향 범위 | 영향받는 Agent, Module, API 목록 |
| 6. Risk 평가 | LOW/MEDIUM/HIGH/CRITICAL 분류 |
| 7. Regression Plan | 회귀 테스트 범위 및 예상 소요시간 |
| 8. Rollback Plan | 수정 실패 시 복원 전략 |

### 3.2 수정 대상 카테고리

| Category | 대상 | 예시 | Risk |
|----------|------|------|------|
| Context JSON 수정 | .cursor/context/*.json | KPI 임계값 조정, Agent R&R 변경 | MEDIUM~HIGH |
| Rule .mdc 수정 | .cursor/rules/*.mdc | 코드 생성 규칙 변경, 금지 사항 추가 | MEDIUM |
| Agent Logic 수정 | backend/src/modules/*/agent.py | execute() 로직, allowed_tools 변경 | HIGH |
| Workflow 변경 | workflow_context.json | Gate SLA 조정, 에스컬레이션 경로 변경 | HIGH |
| Infrastructure 변경 | infra/* | Docker 설정, nginx, 환경 변수 | CRITICAL |

### 3.3 Risk 기반 승인 매트릭스

governance_rules_context.json context_modification 기준:

| Risk Level | Approval Process | Approver |
|-----------|-----------------|----------|
| LOW | P1 Standard | Governance Board |
| MEDIUM | P1 + Board Discussion | Governance Board |
| HIGH | 즉시 중단 + Board 긴급 소집 | Governance Board + AI Architect |
| CRITICAL | 배포 금지 + Executive Escalation | Executive Sponsor |

### 3.4 Evol-A 제약 사항 (절대 금지)

```
❌ Context JSON 직접 수정 (G-09 승인 없이)
❌ Rule .mdc 직접 수정
❌ Agent 코드 직접 변경
❌ 재배포 직접 트리거
❌ 승인 없는 Constraint 변경
❌ trajectory_logs DELETE/UPDATE

✅ 제안서 생성만 가능
✅ P1 approval_requests INSERT만 가능
✅ trajectory_logs / audit_logs 읽기만 가능
```

---

## 4. Section 6.3 — G-09 Approval Workflow

### 4.1 G-09 Gate 정의

| 항목 | 값 |
|------|-----|
| Gate ID | G-09 |
| Gate Name | Context 수정 승인 Gate |
| Phase | Phase 6 |
| Approver | Governance Board |
| HITL Pattern | P1 (Pre-approval: 수정 전 승인 필수) |
| SLA | 24h |
| Risk Level | HIGH |

### 4.2 승인 워크플로우

```
Evol-A: Context 수정 제안서 생성
    │
    ├── approval_requests INSERT (gate_id=G-09, hitl=P1)
    │     - requested_by: Evol-A
    │     - approver: Governance Board
    │     - evidence: Analysis Report + Proposal + Risk Assessment
    │
    ├── Governance Board 검토 (SLA 24h)
    │     ├── APPROVED → Step 4 (Regression Test)
    │     ├── REJECTED → rejection_reason 기재 → Evol-A 재분석
    │     └── MODIFY → 수정 요청 → Evol-A 제안서 갱신
    │
    ├── [APPROVED 후]
    │     ├── review_requests INSERT (P3: Post-review)
    │     ├── Test-A: Regression Test 실행
    │     └── Test-A PASS → Back-A: 재배포 실행
    │
    └── audit_logs INSERT (action='G-09_DECISION')
```

### 4.3 승인 timeout 처리

| 상황 | 행동 |
|------|------|
| 24h 내 응답 없음 | 자동 에스컬레이션 → Executive Sponsor |
| CRITICAL Risk 제안 | 즉시 중단 + 배포 금지 플래그 |
| REJECTED 후 재제출 | 최대 3회까지 허용, 3회 초과 시 Board 대면 회의 |

---

## 5. Section 6.4 — Regression Test & Validation

### 5.1 Regression Test 범위

| Category | 대상 | Tests |
|----------|------|-------|
| Phase 4 전체 재실행 | 5개 모듈 × 6 카테고리 | 93개 |
| 수정 대상 모듈 집중 | 변경된 Context/Agent 관련 | 추가 테스트 |
| Cross-Module 영향 | 의존 관계 모듈 | 통합 테스트 |
| Performance Benchmark | 응답 시간, 처리량 | 성능 테스트 |

### 5.2 Regression Test 실행 절차

```
G-09 APPROVED
    │
    ├── Step 1: Context/Rule 임시 적용 (staging 환경)
    │
    ├── Step 2: Phase 4 전체 테스트 재실행
    │     └── pytest tests/ -v --tb=short
    │
    ├── Step 3: 변경 대상 추가 테스트
    │     └── pytest tests/modules/{changed_module}/ -v
    │
    ├── Step 4: Performance Benchmark
    │     └── Agent 응답시간 < 500ms (query) / < 2000ms (CUD)
    │
    ├── Step 5: 결과 판정
    │     ├── 전체 PASS + 성능 OK → 재배포 승인
    │     └── 1건이라도 FAIL → BLOCK + Evol-A 재분석
    │
    └── regression_report.json 생성
```

### 5.3 Regression Test 통과 기준

| # | 기준 | 필수/권장 |
|---|------|----------|
| 1 | Phase 4 93개 테스트 전체 Pass | 필수 |
| 2 | CRITICAL 이슈 0건 | 필수 |
| 3 | 변경 대상 모듈 추가 테스트 Pass | 필수 |
| 4 | Agent 응답시간 500ms 이내 | 필수 |
| 5 | KPI Drift 없음 (전체 GREEN) | 권장 |
| 6 | Cross-Module 통합 테스트 Pass | 권장 |

---

## 6. Section 6.5 — Redeployment & Verification

### 6.1 재배포 절차

```
Regression Test PASS
    │
    ├── Step 1: Context/Rule 변경 사항 프로덕션 반영
    │     └── git commit + push (변경된 JSON/MDC 파일)
    │
    ├── Step 2: 영향받는 Agent 재빌드
    │     └── docker compose build {affected_service}
    │
    ├── Step 3: Rolling Update 배포
    │     └── docker compose up -d --no-deps {service}
    │
    ├── Step 4: Post-Redeploy Health Check
    │     └── smoke_test.sh 실행
    │
    ├── Step 5: KPI 즉시 수집
    │     └── Monitor-A collect_kpi 트리거
    │
    └── Step 6: 24h 집중 모니터링
          └── Drift YELLOW/RED 발생 시 즉시 Rollback
```

### 6.2 Rollback 판단 기준

| 시점 | 조건 | 행동 |
|------|------|------|
| +1h | Health Check 실패 | 즉시 Rollback |
| +6h | KPI RED 발생 | Rollback + Evol-A 재분석 |
| +12h | KPI YELLOW 지속 | 경고 + 24h 관찰 연장 |
| +24h | 전체 GREEN | 재배포 성공 확정 |

### 6.3 재배포 성공 후 기록

```json
{
  "evolution_id": "EVL-2026-03-001",
  "proposal_id": "PROP-2026-03-001",
  "g09_approved_at": "2026-03-11T10:00:00Z",
  "regression_passed_at": "2026-03-11T12:00:00Z",
  "redeployed_at": "2026-03-11T14:00:00Z",
  "verified_at": "2026-03-12T14:00:00Z",
  "status": "SUCCESS",
  "changes_applied": [
    {"file": ".cursor/context/project_context.json", "type": "KPI 임계값 조정"},
    {"file": "backend/src/modules/reuse/service.py", "type": "자동 트래킹 보강"}
  ],
  "kpi_impact": {
    "K-02": {"before": 38.5, "after": 52.0, "improvement": "+35%"}
  }
}
```

---

## 7. Section 6.6 — Periodic Review Cycle

### 7.1 월간 정기 재검증

| 항목 | 주기 | Owner |
|------|------|-------|
| 전체 KPI 대시보드 리뷰 | 월 1회 (매월 1일) | PM + AI Architect |
| trajectory_logs 패턴 분석 | 월 1회 | Evol-A (자동) |
| Agent 성능 벤치마크 | 월 1회 | Monitor-A + Test-A |
| Governance 규칙 유효성 검토 | 분기 1회 | Governance Board |
| Context 최신성 점검 | 분기 1회 | AI Architect |

### 7.2 Evolution Report 템플릿

```markdown
# Monthly Evolution Report — [YYYY-MM]

## 1. KPI Status Summary
| KPI | Target | Actual | Drift | Trend |
|-----|--------|--------|-------|-------|
| K-01 ~ K-07 ... |

## 2. Evolution Activities This Month
- 제안 건수: X건
- 승인/반려: X/Y건
- 적용 완료: Z건

## 3. Pattern Analysis
- 탐지된 패턴: ...
- 해결된 패턴: ...
- 미해결 패턴: ...

## 4. Performance Trends
- 평균 응답시간: Xms (전월 대비 ±Y%)
- 에러율: X% (전월 대비 ±Y%)

## 5. Recommendations
- ...

## 6. Next Month Focus
- ...
```

---

## 8. Evolution Loop 전체 흐름도

```
┌─────────────────────────────────────────────────────────┐
│                   PRODUCTION ENVIRONMENT                 │
│                                                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ Backend  │───►│ Monitor-A│───►│trajectory│          │
│  │ Agents   │    │ (L0)     │    │ _logs    │          │
│  └──────────┘    └────┬─────┘    └──────────┘          │
│                       │                                  │
│                       │ ① Drift RED 감지                │
│                       ▼                                  │
│                  ┌──────────┐                            │
│                  │   Orch   │ ② 라우팅                  │
│                  └────┬─────┘                            │
│                       ▼                                  │
│                  ┌──────────┐                            │
│                  │  Evol-A  │ ③ 분석 + 제안서 생성      │
│                  │  (L1)    │                            │
│                  └────┬─────┘                            │
│                       │                                  │
│                       │ ④ approval_requests INSERT       │
│                       ▼                                  │
│    ┌──────────────────────────────────┐                  │
│    │  G-09 Gate (Governance Board)    │                  │
│    │  P1 Pre-approval | SLA 24h      │                  │
│    └────────┬──────────┬──────────────┘                  │
│        APPROVED    REJECTED                              │
│             │          │                                 │
│             ▼          └──► Evol-A 재분석               │
│        ┌──────────┐                                      │
│        │  Test-A  │ ⑤ Regression Test (93개+α)          │
│        │  (L1)    │                                      │
│        └────┬─────┘                                      │
│        PASS │  FAIL → BLOCK                              │
│             ▼                                            │
│        ┌──────────┐                                      │
│        │  Back-A  │ ⑥ 재배포 (Rolling Update)           │
│        │  (L1)    │                                      │
│        └────┬─────┘                                      │
│             │                                            │
│             ▼                                            │
│        ┌──────────┐                                      │
│        │ Monitor-A│ ⑦ 24h 집중 모니터링                 │
│        └────┬─────┘                                      │
│             │ GREEN 확인                                 │
│             ▼                                            │
│        ✅ Evolution 완료 → Loop 재시작                   │
└─────────────────────────────────────────────────────────┘
```

---

## 9. 산출물 목록

| # | 산출물 | 형식 | 위치 |
|---|--------|------|------|
| D-01 | Phase 6 방법론 문서 | MD/DOCX | methodology/phase6_evolution/ |
| D-02 | Evol-A Agent 코드 | Python | backend/src/modules/evolution/ |
| D-03 | Evolution Service | Python | backend/src/modules/evolution/ |
| D-04 | Proposal Schema | Python | backend/src/modules/evolution/ |
| D-05 | phase6_context.json | JSON | .cursor/context/ |
| D-06 | 14_evolution.mdc | MDC | .cursor/rules/ |
| D-07 | evolution-runner Skill | MD | .cursor/skills/ |
| D-08 | Regression Test Runner | Shell | infra/scripts/ |
| D-09 | Monthly Evolution Report Template | MD | methodology/phase6_evolution/reports/ |

---

## 10. 참조 문서

| 문서 | 참조 내용 |
|------|----------|
| workflow_context.json | G-09 Gate, Phase 6 workflow, escalation_rules |
| governance_rules_context.json | RISK-04 Drift, context_modification 승인 매트릭스 |
| hitl_context.json | P1 패턴 정의, approval_requests 스키마 |
| system_prompt_context.json | Evol-A System Prompt, 5-Layer spec |
| skill_context.json | evol.propose_improvement, evol.generate_patch_note |
| memory_context.json | trajectory_logs (Episodic Memory L3) |
| rr_matrix_context.json | Phase 6 R&R, lead_agent, key_activities |
| governance_charter.json | 5-Step Continuous Improvement Process |
| operation_standards.json | Principle 5, Phase 6 운영 표준 |
| phase5_context.json | Phase 5→6 전환 조건, Monitor-A spec |
