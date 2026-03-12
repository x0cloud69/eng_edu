---
name: evolution-runner
description: Phase 6 Evolution Loop 실행 — Evol-A Agent 구현, Drift 분석, Context 수정 제안, G-09 승인, 회귀 테스트, 재배포까지 전체 Evolution 파이프라인 자동화. Evolution Loop, 개선 루프, Drift 분석, Context 수정
---

# Evolution Runner Skill

Phase 6 Evolution Loop 전체를 실행하는 Cursor Skill입니다.

---

## Reference Files

```
@.cursor/context/phase6_context.json       ← Evolution Loop Context
@.cursor/context/phase5_context.json       ← Deploy & Monitoring Context (Monitor-A, KPI)
@.cursor/context/workflow_context.json      ← Agent Workflow 설계
@.cursor/context/hitl_context.json         ← Human-in-the-Loop 구조
@.cursor/context/governance_rules_context.json ← AI 리스크 임계값
@.cursor/rules/14_evolution.mdc            ← Evolution 코드 생성 규칙
@.cursor/rules/13_deploy.mdc              ← Deploy 규칙 (재배포 시 참조)
@.cursor/rules/12_simulation.mdc          ← Simulation Test 규칙 (회귀 테스트 시 참조)
@backend/src/core/base_agent.py           ← BaseAgent 인터페이스
@backend/src/modules/monitoring/agent.py  ← Monitor-A Agent (Drift 데이터 제공)
@backend/src/modules/monitoring/service.py ← KPICollector, DriftDetector
```

---

## 실행 순서

### Step 1: 선행 조건 확인
```
체크리스트:
  □ G-08 Release Gate PASS (Phase 5)
  □ 프로덕션 48h 안정 운영
  □ Monitor-A Drift Detection 활성
  □ trajectory_logs 테이블 존재
  □ phase6_context.json 로드 확인
  □ 14_evolution.mdc 규칙 확인
```

### Step 2: Evol-A Agent 코드 생성
```
파일 생성:
  backend/src/modules/evolution/__init__.py
  backend/src/modules/evolution/agent.py      ← EvolutionAgent (BaseAgent 상속)
  backend/src/modules/evolution/service.py    ← DriftAnalyzer, ProposalGenerator
  backend/src/modules/evolution/models.py     ← EvolutionProposal, EvolutionLog (SQLAlchemy)
  backend/src/modules/evolution/schemas.py    ← Pydantic 스키마

규칙:
  - phase6_context.json evolution_agent 기준 엄격 준수
  - authority_level: L1, risk_level: HIGH
  - allowed_tools: ["read_logs", "llm_call"]
  - 14_evolution.mdc 금지 사항 전부 반영
```

### Step 3: Orchestrator 등록
```
backend/src/api/main.py에 추가:
  from src.modules.evolution.agent import EvolutionAgent
  OrchestratorAgent.register("evolution.*", EvolutionAgent())
```

### Step 4: DB 모델 및 마이그레이션
```
테이블 생성:
  - evolution_proposals (phase6_context.json proposal_schema)
  - evolution_logs (phase6_context.json evolution_log_schema)

인덱스:
  - idx_evo_proposal_tenant (tenant_id, status)
  - idx_evo_proposal_pattern (pattern_code)
  - idx_evo_proposal_status (status) WHERE status IN ('DRAFT', 'PENDING_APPROVAL', 'APPROVED')
  - idx_evo_log_proposal (proposal_id)
  - idx_evo_log_tenant (tenant_id, created_at DESC)
```

### Step 5: 회귀 테스트 스크립트 생성
```
infra/scripts/regression_test.sh:
  1. Phase 4 테스트 93개 전체 재실행
  2. 수정 대상 Agent 추가 테스트
  3. Multi-Tenant 격리 검증
  4. 결과 JSON 출력
  5. Pass/Fail 판정
```

### Step 6: G-09 Gate 체크리스트 확인
```
G-09 필수 조건 (7개):
  EC-01: Drift Pattern 분석 보고서 첨부
  EC-02: 영향 받는 Context/Agent/Rule 목록
  EC-03: 수정 전후 비교 (diff)
  EC-04: Risk Level 평가
  EC-05: 롤백 계획
  EC-06: 회귀 테스트 시나리오 정의
  EC-07: 기존 93개 테스트 영향도 분석
```

### Step 7: Evolution Loop 흐름 검증
```
Full Cycle 검증:
  Monitor-A (Drift 탐지)
    → Orch 라우팅
    → Evol-A.analyze_drift (패턴 분류)
    → Evol-A.propose_modification (제안 생성)
    → G-09 승인 (Governance Board)
    → Test-A 회귀 테스트 (93개 + α)
    → Back-A 재배포
    → Post-Redeploy 모니터링 (48h)
```

### Step 8: 마스터 참조 업데이트
```
업데이트 파일:
  - 00_master.mdc: Phase 6 규칙/Context 참조 추가
  - .cursor/skills/README.md: evolution-runner 등록
```

### Step 9: 산출물 최종 확인
```
Phase 6 산출물:
  □ phase6_context.json (20th Context)
  □ 14_evolution.mdc (15th Rule)
  □ evolution-runner Skill (9th Skill)
  □ EvolutionAgent (agent.py, service.py, models.py, schemas.py)
  □ regression_test.sh
  □ 00_master.mdc 업데이트
  □ main.py EvolutionAgent 등록
  □ skills README 업데이트
```

---

## 주의사항

1. **Evol-A는 절대 Context를 직접 수정할 수 없다** — 제안만 생성
2. **모든 수정은 G-09 승인 후에만 반영**
3. **P-TENANT-LEAK 발견 시 즉시 EMERGENCY**
4. **회귀 테스트 미통과 시 절대 배포 불가**
5. **5대 원칙, 보안 규칙, BaseAgent 인터페이스는 수정 불가**
