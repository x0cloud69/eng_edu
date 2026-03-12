# Skill: deploy-runner
> Phase 5 Deploy & Monitoring 실행 자동화

## 목적
Phase 5 배포 파이프라인 전체를 자동화하여 실행한다.
Container 빌드 → G-08 체크리스트 검증 → 배포 → Post-Deploy 확인 → KPI 모니터링 시작

## 선행 조건
- [ ] G-07 Evaluation Report PASS (Phase 4)
- [ ] CRITICAL 이슈 0건
- [ ] Phase 4 시뮬레이션 93개 테스트 전체 Pass

## 참조 파일
- `@.cursor/context/phase5_context.json`
- `@.cursor/rules/13_deploy.mdc`
- `@.cursor/context/workflow_context.json`
- `@.cursor/context/hitl_context.json`
- `@.cursor/context/governance_rules_context.json`

---

## 실행 단계

### Step 1: Prerequisites Check
```
확인 사항:
1. phase4_context.json → G-07 PASS 확인
2. simulation_log.json → passed=93, failed=0
3. CRITICAL 이슈 0건
4. phase5_context.json → container_spec 확인
```

### Step 2: Docker Infrastructure 생성
```
생성 대상:
1. infra/docker/Dockerfile.backend
   - python:3.11-slim multi-stage
   - Non-root user (appuser)
   - HEALTHCHECK 포함
2. infra/docker/Dockerfile.frontend
   - node:20-alpine multi-stage
3. infra/docker/docker-compose.yml
   - 5 services: backend, frontend, postgres, redis, nginx
   - depends_on, volumes, networks
4. infra/docker/.env.template
   - 모든 필수 환경 변수 포함, Secret 비워둠
5. infra/docker/.dockerignore
```

### Step 3: Monitor-A Agent 생성
```
생성 대상:
1. backend/src/modules/monitoring/__init__.py
2. backend/src/modules/monitoring/agent.py
   - MonitorAgent(BaseAgent)
   - L0, allowed_tools=["db_query"]
   - Actions: collect_kpi, check_drift, get_dashboard, get_history, get_alerts
3. backend/src/modules/monitoring/service.py
   - KPICollector: K-01 ~ K-07 수집
   - DriftDetector: variance 계산 → drift_level 판정
4. backend/src/modules/monitoring/models.py
   - TrajectoryLog(TenantBaseModel)
   - KPIAlert(TenantBaseModel)
   - OverrideLog(TenantBaseModel)
5. backend/src/modules/monitoring/schemas.py
   - KPIDashboard, KPIHistoryItem, AlertItem

검증:
- MonitorAgent authority_level == L0
- allowed_tools == ["db_query"] (db_write 없음)
- 모든 action → AgentResult 반환
```

### Step 4: Orchestrator 등록
```
수정 대상: backend/src/api/main.py

추가:
  from src.modules.monitoring.agent import MonitorAgent
  OrchestratorAgent.register("monitor.*", MonitorAgent())

검증:
  GET /api/v1/capability/skills → monitor.* 포함
```

### Step 5: DB Migration 생성
```
생성 대상: Alembic migration
- trajectory_logs 테이블
- kpi_alerts 테이블
- override_logs 테이블
- 인덱스 생성

검증:
  alembic current → 최신 revision
```

### Step 6: 배포/롤백 스크립트 생성
```
생성 대상:
1. infra/scripts/deploy.sh
   - G-08 승인 확인 → Docker 빌드 → 배포 → Health Check → Rollback
2. infra/scripts/rollback.sh
   - 이전 버전 복원
3. infra/scripts/health-check.sh
   - /health, /ready 확인
4. infra/scripts/smoke_test.sh
   - ST-01 ~ ST-07 시나리오 실행
```

### Step 7: G-08 Release Checklist 검증
```
필수 17항목 자동 확인:
- RC-01 ~ RC-03: Phase 4 결과
- RC-04 ~ RC-06: Docker 빌드/기동
- RC-07 ~ RC-10: Health Check / DB / Redis
- RC-11 ~ RC-14: Monitor-A / KPI / Drift
- RC-15 ~ RC-17: Rollback / env / Secret

결과 → methodology/phase5_deploy/5_5_release_checklist_result.json
```

### Step 8: Post-Deploy Verification
```
48h 모니터링:
- +1h:  Health Check 3회 연속 성공
- +6h:  trajectory_logs row count >= 6
- +12h: Drift YELLOW/RED 0건
- +24h: API 응답시간 500ms 이내
- +48h: Post-Deploy Report 생성

결과 → methodology/phase5_deploy/reports/5_6_post_deploy_report.md
```

### Step 9: Phase 6 전환 준비
```
확인 사항:
- G-08 PASS
- 48h 안정 운영
- KPI 전체 GREEN
- Monitor-A 활성
- Post-Deploy Report 제출

결론 → Phase 6 진입 가능 여부 판단
```

---

## 산출물 체크리스트

| # | File | Status |
|---|------|--------|
| 1 | infra/docker/Dockerfile.backend | [ ] |
| 2 | infra/docker/Dockerfile.frontend | [ ] |
| 3 | infra/docker/docker-compose.yml | [ ] |
| 4 | infra/docker/.env.template | [ ] |
| 5 | infra/docker/.dockerignore | [ ] |
| 6 | backend/src/modules/monitoring/agent.py | [ ] |
| 7 | backend/src/modules/monitoring/service.py | [ ] |
| 8 | backend/src/modules/monitoring/models.py | [ ] |
| 9 | backend/src/modules/monitoring/schemas.py | [ ] |
| 10 | infra/scripts/deploy.sh | [ ] |
| 11 | infra/scripts/rollback.sh | [ ] |
| 12 | infra/scripts/smoke_test.sh | [ ] |
| 13 | G-08 Checklist Result JSON | [ ] |
| 14 | Post-Deploy Report MD | [ ] |

---

## 이슈 분류

| Severity | 기준 | G-08 영향 |
|----------|------|----------|
| CRITICAL | 필수 조건 미충족 | Gate 차단 |
| WARNING | 권장 조건 미충족 | Pass (경고) |
| INFO | 참고 사항 | 영향 없음 |
