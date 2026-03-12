---
name: simulation-runner
description: >-
  Runs Phase 4 Simulation Test for the AI-Native SaaS Standard Framework.
  Executes all 6 test categories, generates reports, and produces Evaluation Report for G-07 Gate.
  Use when the user says "시뮬레이션 실행", "Phase 4 실행", "테스트 돌려줘",
  "run simulation", "run phase 4 tests", "Evaluation Report 만들어줘",
  or "G-07 준비해줘".
---

# Simulation Runner

You are a simulation runner for Phase 4 of the AI-Native SaaS Standard Framework.
When the user requests a simulation run, execute tests following the exact steps below.

## Prerequisites

Before running, verify:
1. `backend/tests/conftest.py` 존재 여부 — 없으면 `test-scenario-generator` Skill로 먼저 생성
2. `backend/tests/modules/{module}/test_agent.py` 존재 여부 — 없으면 생성
3. `backend/pytest.ini` 존재 여부 — 없으면 생성

## Step 0: Gather Information

Ask the user (if not already provided):
1. **실행 범위** — 전체(full) / 특정 모듈(module name) / 특정 카테고리(category)
2. **보고서 생성 여부** — Evaluation Report까지 생성할지

자동으로 확인할 사항:
- `backend/src/modules/` 에서 등록된 모듈 목록 파악
- `backend/src/api/main.py` 에서 Orchestrator 등록된 Agent 목록 파악

## Step 1: Generate Missing Test Files

등록된 각 모듈에 대해 테스트 파일이 없으면 생성한다.

### 1-1. conftest.py (없을 경우)

```bash
# conftest.py 존재 확인
ls backend/tests/conftest.py
```

없으면 `test-scenario-generator` Skill의 conftest.py 패턴대로 생성:
- `mock_db` fixture (AsyncMock)
- `make_context` fixture (AgentContext factory)
- TENANT_ID, USER_ID, OTHER_TENANT_ID 상수

### 1-2. 모듈별 test_agent.py (없을 경우)

각 모듈의 agent.py를 분석하여 6개 테스트 클래스를 포함하는 test_agent.py 생성:
1. `TestBasicCRUD` — S-01 ~ S-06
2. `TestApprovalGate` — 8가지 Authority×Risk 매트릭스
3. `TestScopeValidation` — allowed/blocked Tool
4. `TestMultiTenantIsolation` — Cross-Tenant 접근
5. `TestAuditLog` — A-01 ~ A-05
6. `TestErrorHandling` — 알 수 없는 액션, 파라미터 누락, db=None

### 1-3. pytest.ini (없을 경우)

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

## Step 2: Run Tests

### 2-1. 전체 실행

```bash
cd backend && python -m pytest tests/ -v --tb=short 2>&1 | tee tests/results/simulation_output.txt
```

### 2-2. 모듈별 실행

```bash
cd backend && python -m pytest tests/modules/{module_name}/ -v --tb=short
```

### 2-3. 카테고리별 실행

```bash
# ApprovalGate만
cd backend && python -m pytest tests/ -k "TestApprovalGate" -v

# AuditLog만
cd backend && python -m pytest tests/ -k "TestAuditLog" -v

# ErrorHandling만
cd backend && python -m pytest tests/ -k "TestErrorHandling" -v
```

## Step 3: Collect Results

테스트 결과를 파싱하여 JSON으로 저장한다.

### 3-1. Simulation Log

파일: `backend/tests/results/simulation_log.json`

```json
{
  "run_id": "{uuid}",
  "run_at": "{ISO timestamp}",
  "total_tests": 0,
  "passed": 0,
  "failed": 0,
  "errors": 0,
  "modules": {
    "{module_name}": {
      "test_basic_crud": { "passed": 0, "failed": 0, "details": [] },
      "test_approval_gate": { "passed": 0, "failed": 0, "details": [] },
      "test_scope_validation": { "passed": 0, "failed": 0, "details": [] },
      "test_multi_tenant": { "passed": 0, "failed": 0, "details": [] },
      "test_audit_log": { "passed": 0, "failed": 0, "details": [] },
      "test_error_handling": { "passed": 0, "failed": 0, "details": [] }
    }
  }
}
```

### 3-2. Issue List

실패한 테스트를 Issue로 분류:

| Severity | 기준 |
|----------|------|
| CRITICAL | ApprovalGate 미차단, AuditLog 미기록, 멀티테넌트 누출, Exception 누출 |
| WARNING | 성능 기준 초과, 에러 메시지 불명확 |
| INFO | 개선 가능한 패턴, 코드 스타일 |

## Step 4: Generate Reports

### 4-1. Section Reports

각 WBS 섹션별 보고서를 `methodology/phase4_simulation/reports/`에 생성:

```markdown
# {Section Name} Test Report
> Date: {date} | Module: {module_name}

## Result: [PASS / FAIL]

## Test Summary
| Test | Result | Details |
|------|--------|---------|

## Issues Found
| # | Severity | Description |
|---|----------|-------------|
```

### 4-2. Evaluation Report (4.6.1)

파일: `methodology/phase4_simulation/4_6_evaluation_report.md`

```markdown
# Phase 4 Evaluation Report
> Version: v1.0 | Date: {date} | Author: Test-A (automated)

## 1. Executive Summary

| Metric | Value |
|--------|-------|
| Total Tests | {n} |
| Passed | {n} |
| Failed | {n} |
| Pass Rate | {n}% |
| CRITICAL Issues | {n} |
| Phase 5 Decision | [GO / NO-GO] |

## 2. Test Results by Section

### 4.1 Agent Role-play Simulation: [PASS/FAIL]
{details}

### 4.2 Failure Scenario Test: [PASS/FAIL]
{details}

### 4.3 Governance Compliance Test: [PASS/FAIL]
{details}

### 4.4 SaaS Isolation Test: [PASS/FAIL]
{details}

### 4.5 KPI Baseline Measurement: [MEASURED/NOT MEASURED]
{details}

## 3. Issue List

| # | Severity | Section | Description | Status |
|---|----------|---------|-------------|--------|

## 4. G-07 Gate Checklist

| Condition | Status |
|-----------|--------|
| 4.1 Agent CRUD 전체 Pass | [ ] |
| 4.2 Failure 안전 실패 확인 | [ ] |
| 4.3 ApprovalGate 매트릭스 Pass | [ ] |
| 4.3 AuditLog 기록률 100% | [ ] |
| 4.4 멀티테넌트 격리 Pass | [ ] |
| 4.5 KPI Baseline 측정 완료 | [ ] |
| CRITICAL 이슈 0건 | [ ] |

## 5. Recommendations

### Phase 5 전 필수 조치
{list}

### Phase 6 추적 항목
{list}
```

## Step 5: G-07 Gate 준비

Evaluation Report 완성 후:

1. CRITICAL 이슈 0건이면 → "G-07 Gate 제출 준비 완료" 메시지
2. CRITICAL 이슈 있으면 → Issue 목록 + 수정 필요 사항 안내
3. 사용자에게 G-07 승인 절차 안내:
   - review_requests에 INSERT 필요 (status=PENDING)
   - QA Engineer 검토 (SLA 48h)
   - CONFIRMED 시 Phase 5 진행

## Step 6: Verify

실행 완료 후 확인:
1. 모든 모듈의 6개 테스트 카테고리 실행 여부
2. Simulation Log JSON 생성 여부
3. 섹션별 Report 생성 여부
4. Evaluation Report 생성 여부
5. Issue 분류 정확성 (CRITICAL/WARNING/INFO)
6. G-07 통과 조건 체크리스트 완성 여부

## Reference Files

- `.cursor/context/phase4_context.json` — Phase 4 테스트 기준
- `.cursor/context/workflow_context.json` — Phase 4 Workflow 정의
- `.cursor/context/hitl_context.json` — ApprovalGate P1/P2/P3
- `.cursor/rules/12_simulation.mdc` — Phase 4 코드 생성 규칙
- `backend/src/core/base_agent.py` — BaseAgent 표준 흐름
- `backend/src/modules/*/agent.py` — 테스트 대상 Agent
- `.cursor/skills/test-scenario-generator/SKILL.md` — 테스트 생성 패턴
