# Phase 5 — Deploy & Monitoring 방법론
> Version: v1.0 | Date: 2026-03-11 | Author: AI Architect
> Status: **DRAFT**
> Predecessor: Phase 4 Simulation (G-07 통과 필수)
> Gate: **G-08 Release Gate** (Approver: AI Architect + PM, HITL: P1, SLA: 24h)

---

## 1. Phase 5 개요

### 1.1 목적

Phase 4에서 검증된 코드를 프로덕션 환경에 배포하고, 지속적 KPI 모니터링 인프라를 구축하여 Phase 6 Evolution Loop의 데이터 기반을 마련한다.

### 1.2 Phase 5 범위 (WBS)

| Section | Title | 핵심 산출물 |
|---------|-------|------------|
| 5.1 | Container Packaging | Dockerfile, docker-compose.yml, .env.template |
| 5.2 | Deployment Pipeline | CI/CD 파이프라인, 배포 스크립트, Rollback 전략 |
| 5.3 | KPI Monitoring Infrastructure | Monitor-A Agent, trajectory_logs, Drift Detection |
| 5.4 | Alert & Incident Response | Alert Rule, Escalation 정책, Override 절차 |
| 5.5 | Release Gate (G-08) | Release Checklist, 승인 워크플로우, Compliance 확인 |
| 5.6 | Post-Deployment Verification | Smoke Test, Health Check, KPI Baseline 확인 |

### 1.3 담당 Agent

| Agent | Layer | Authority | 역할 |
|-------|-------|-----------|------|
| Back-A | Layer 3 (Capability) | L1 | 배포 실행, Docker 패키징, 인프라 설정 |
| Monitor-A | Layer 4 (Monitoring) | L0 | KPI 모니터링, Drift 탐지, Alert 발행 |
| Orch | Layer 1 (Orchestration) | L0 | 배포 워크플로우 라우팅 |
| Gov-A | Layer 2 (Governance) | L2 | 거버넌스 규칙 준수 검증 |

### 1.4 선행 조건

- [ ] G-07 Evaluation Report 통과 (Phase 4)
- [ ] CRITICAL 이슈 0건
- [ ] 93개 시뮬레이션 테스트 전체 Pass
- [ ] KPI Baseline 측정 완료 (Phase 4.5)

---

## 2. Section 5.1 — Container Packaging

### 2.1 Docker 표준 구조

```
infra/
├── docker/
│   ├── Dockerfile.backend       # FastAPI 백엔드
│   ├── Dockerfile.frontend      # Next.js 프론트엔드
│   ├── docker-compose.yml       # 전체 오케스트레이션
│   ├── docker-compose.dev.yml   # 개발 환경 Override
│   ├── docker-compose.prod.yml  # 프로덕션 환경 Override
│   └── .env.template            # 환경 변수 템플릿
├── nginx/
│   └── nginx.conf               # Reverse Proxy 설정
└── scripts/
    ├── deploy.sh                # 배포 스크립트
    ├── rollback.sh              # 롤백 스크립트
    └── health-check.sh          # 헬스체크 스크립트
```

### 2.2 Dockerfile 설계 원칙

| 원칙 | 설명 |
|------|------|
| Multi-Stage Build | 빌드/런타임 이미지 분리 → 최종 이미지 크기 최소화 |
| Non-root User | 프로덕션 컨테이너는 non-root 사용자로 실행 |
| Health Check | HEALTHCHECK 명령어 포함 (30s interval) |
| Layer Caching | requirements.txt → COPY → pip install 순서로 캐시 최적화 |
| Secret 관리 | .env 파일은 Docker secrets 또는 Vault 연동 (하드코딩 금지) |

### 2.3 Backend Dockerfile 스펙

```dockerfile
# Stage 1: Build
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim AS runtime
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin
COPY backend/src/ ./src/

# Non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.4 docker-compose 서비스 맵

| Service | Image | Port | Depends On |
|---------|-------|------|------------|
| backend | framework-backend:latest | 8000 | postgres, redis |
| frontend | framework-frontend:latest | 3000 | backend |
| postgres | postgres:15-alpine | 5432 | — |
| redis | redis:7-alpine | 6379 | — |
| nginx | nginx:alpine | 80/443 | backend, frontend |

### 2.5 환경 변수 템플릿 (.env.template)

```env
# Application
APP_ENV=production
APP_VERSION=1.0.0
APP_SECRET_KEY=  # 반드시 설정 필요

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/framework
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://redis:6379/0

# Multi-Tenancy
DEFAULT_TENANT_ID=00000000-0000-0000-0000-000000000001

# Monitoring (Phase 5)
KPI_COLLECT_INTERVAL_SECONDS=60
DRIFT_ALERT_THRESHOLD=0.10
DRIFT_DETECTION_THRESHOLD=0.20

# CORS
CORS_ORIGINS=["https://app.framework.example.com"]
```

---

## 3. Section 5.2 — Deployment Pipeline

### 3.1 CI/CD 워크플로우

```
┌─────────┐    ┌──────────┐    ┌───────────┐    ┌─────────┐    ┌──────────┐
│  Push /  │───►│  Build   │───►│   Test    │───►│ G-08    │───►│  Deploy  │
│  PR Merge│    │  Images  │    │  (Phase4) │    │ Release │    │  Prod    │
└─────────┘    └──────────┘    └───────────┘    │  Gate   │    └──────────┘
                                                └─────────┘         │
                                                   │ FAIL           │
                                                   ▼                ▼
                                              ┌──────────┐    ┌──────────┐
                                              │ Block &  │    │ Post-    │
                                              │ Notify   │    │ Deploy   │
                                              └──────────┘    │ Verify   │
                                                              └──────────┘
```

### 3.2 배포 전략

| 전략 | 설명 | 사용 조건 |
|------|------|----------|
| Blue-Green | 두 환경 교대 배포 | 주요 릴리스 (Major/Minor) |
| Rolling Update | 점진적 교체 | 패치 릴리스 (Patch) |
| Canary | 일부 트래픽 우선 전환 | 위험도 높은 변경 |

### 3.3 Rollback 전략

| 단계 | 트리거 | 행동 |
|------|--------|------|
| 자동 롤백 | Health Check 3회 연속 실패 | 이전 버전 자동 복원 |
| 수동 롤백 | 운영자 판단 (CRITICAL Alert) | `rollback.sh` 실행 |
| DB 롤백 | Alembic 마이그레이션 실패 | `alembic downgrade -1` |

### 3.4 배포 스크립트 규격

```bash
#!/bin/bash
# deploy.sh — Back-A Agent 배포 실행 스크립트
set -euo pipefail

# Step 1: G-08 승인 확인
check_release_gate() {
    # review_requests에서 G-08 APPROVED 확인
    STATUS=$(curl -s "$API_URL/api/v1/agents/invoke" \
        -d '{"action":"approvals.list","payload":{"gate_id":"G-08","status":"APPROVED"}}' \
        | jq -r '.data.total')
    [ "$STATUS" -gt 0 ] || { echo "G-08 미승인. 배포 중단."; exit 1; }
}

# Step 2: Docker 이미지 빌드
build_images() {
    docker compose -f docker-compose.prod.yml build --no-cache
}

# Step 3: 배포 실행
deploy() {
    docker compose -f docker-compose.prod.yml up -d
}

# Step 4: Post-deploy Health Check
verify() {
    for i in $(seq 1 5); do
        sleep 10
        curl -sf http://localhost:8000/ready && echo "Ready!" && return 0
    done
    echo "Health check failed. Rolling back..."
    rollback
    exit 1
}

# Step 5: Rollback
rollback() {
    docker compose -f docker-compose.prod.yml down
    docker compose -f docker-compose.prod.yml up -d --force-recreate
}

# Main
check_release_gate
build_images
deploy
verify
echo "Deployment complete."
```

---

## 4. Section 5.3 — KPI Monitoring Infrastructure

### 4.1 Monitor-A Agent 정의

```
Agent: Monitor-A
Layer: 4 (Monitoring)
Authority: L0 (읽기 전용 — 상태 변경 불가)
Risk: LOW
allowed_tools: [db_query]
System Prompt: KPI 수집, Drift 탐지, 자동 Alert 발행

금지 사항:
  - DB 쓰기 (INSERT/UPDATE/DELETE 불가)
  - 직접적인 시스템 조치 (Alert만 발행)
  - Phase 6 Evolution 트리거 (제안만 가능)
```

### 4.2 KPI 정의 및 측정 방법

| # | KPI | Target | 측정 방법 | 수집 주기 |
|---|-----|--------|----------|----------|
| K-01 | 프레임워크 채택률 | 70%+ | (사용 프로젝트 / 전체 프로젝트) × 100 | 일간 |
| K-02 | 공통 모듈 재사용률 | 50%+ | (재사용 모듈 수 / 전체 모듈) × 100 | 일간 |
| K-03 | 개발 기간 단축 | 30%+ | (기존 평균 - 현재 평균) / 기존 평균 × 100 | 주간 |
| K-04 | AI 승인 프로세스 단축 | 30~40% | (기존 처리시간 - 현재) / 기존 × 100 | 일간 |
| K-05 | 감사 준비 기간 단축 | 50% | (기존 기간 - 현재 기간) / 기존 × 100 | 월간 |
| K-06 | 규제 준수율 | 95%+ | governance-checker Pass 비율 | 일간 |
| K-07 | Drift 탐지 적용률 | 100% | Monitor-A 모니터링 대상 / 전체 KPI × 100 | 실시간 |

### 4.3 Drift Detection 규칙

governance_rules_context.json RISK-04 기준:

| Level | Condition | Action |
|-------|-----------|--------|
| **GREEN** (정상) | KPI ± 10% 이내 | Monitor-A 로그 기록만 |
| **YELLOW** (경고) | KPI 10~20% 하락 | Alert 발행 → PM 통보 |
| **RED** (위험) | KPI 20%+ 하락 | CRITICAL Alert → Evolution Agent 제안 → Board 검토 |

### 4.4 trajectory_logs 스키마

```sql
CREATE TABLE trajectory_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,

    -- KPI 식별
    kpi_code        VARCHAR(10) NOT NULL,     -- K-01 ~ K-07
    kpi_name        VARCHAR(100) NOT NULL,

    -- 측정값
    target_value    DECIMAL(10,2) NOT NULL,
    actual_value    DECIMAL(10,2) NOT NULL,
    variance_pct    DECIMAL(5,2) NOT NULL,    -- (actual - target) / target × 100

    -- Drift 상태
    drift_level     VARCHAR(10) NOT NULL DEFAULT 'GREEN',  -- GREEN/YELLOW/RED

    -- 메타
    measured_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    measured_by     VARCHAR(50) NOT NULL DEFAULT 'Monitor-A',

    -- 표준 필드
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by      UUID NOT NULL
);

-- 인덱스
CREATE INDEX idx_trajectory_tenant_kpi ON trajectory_logs(tenant_id, kpi_code);
CREATE INDEX idx_trajectory_drift ON trajectory_logs(drift_level) WHERE drift_level != 'GREEN';
CREATE INDEX idx_trajectory_measured ON trajectory_logs(measured_at DESC);
```

### 4.5 Monitor-A 실행 흐름

```
[매 60초]
  ┌─────────────┐
  │ Monitor-A   │
  │ (L0, Query) │
  └──────┬──────┘
         │ 1. KPI 데이터 수집 (db_query)
         ▼
  ┌─────────────┐
  │ Calculate   │──── variance_pct 계산
  │ KPI Values  │
  └──────┬──────┘
         │ 2. Drift Level 판정
         ▼
  ┌─────────────┐
  │ Write       │──── trajectory_logs INSERT (Orch 경유)
  │ trajectory  │
  └──────┬──────┘
         │ 3. Alert 필요 시
         ├─── YELLOW: Alert Queue → PM 통보
         └─── RED: CRITICAL Alert → Orch → Evolution Agent 제안
```

---

## 5. Section 5.4 — Alert & Incident Response

### 5.1 Alert 분류

| Severity | Trigger | Response Time | Responder |
|----------|---------|---------------|-----------|
| INFO | KPI 수집 완료 로그 | — | 자동 기록 |
| WARNING | YELLOW drift (10~20%) | 4h | PM |
| CRITICAL | RED drift (20%+) | 1h | AI Architect + PM |
| EMERGENCY | 시스템 장애/데이터 유출 | 즉시 | Governance Board + 운영팀 |

### 5.2 Escalation Chain

```
Monitor-A Alert
    │
    ├── INFO → trajectory_logs 기록
    │
    ├── WARNING → Alert Queue → PM 알림 (Slack/Email)
    │                 │
    │                 └── 4h 미응답 → CRITICAL 승격
    │
    ├── CRITICAL → PM + AI Architect 알림
    │                 │
    │                 ├── Evolution Agent 개선 제안 생성
    │                 └── 24h 미해결 → EMERGENCY 승격
    │
    └── EMERGENCY → Human Override 절차
                     │
                     ├── Quick Shutdown (L3 권한)
                     └── override_logs INSERT
```

### 5.3 Human Override 절차 (L3)

| 단계 | 행동 | 기록 |
|------|------|------|
| 1 | Governance Board 긴급 소집 | override_logs.trigger_reason |
| 2 | 위험 Agent 즉시 중지 결정 | override_logs.action = 'STOP' |
| 3 | 정지 실행 (Quick Shutdown) | override_logs.executed_at |
| 4 | 원인 분석 및 개선 계획 | override_logs.resolution |
| 5 | 복구 후 재시작 승인 | override_logs.restart_approved_by |

### 5.4 override_logs 스키마

```sql
CREATE TABLE override_logs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL,

    -- Override 정보
    trigger_reason      TEXT NOT NULL,
    severity            VARCHAR(20) NOT NULL,     -- CRITICAL / EMERGENCY
    affected_agents     TEXT[] NOT NULL,           -- ['Back-A', 'Monitor-A']
    action              VARCHAR(20) NOT NULL,      -- STOP / PAUSE / RESTART

    -- 실행자
    executed_by         UUID NOT NULL,             -- Human (Board member)
    executed_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- 해결
    resolution          TEXT,
    restart_approved_by UUID,
    restart_at          TIMESTAMPTZ,

    -- 표준 필드
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          UUID NOT NULL
);
```

---

## 6. Section 5.5 — Release Gate (G-08)

### 6.1 G-08 정의

| 항목 | 값 |
|------|-----|
| Gate ID | G-08 |
| Gate Name | Release Gate |
| Phase | Phase 5 |
| Approver | AI Architect + PM (공동 승인) |
| HITL Pattern | P1 (Pre-approval: 배포 전 승인 필수) |
| SLA | 24h |
| Risk Level | HIGH |

### 6.2 Release Checklist

#### 필수 조건 (7항목 — 전체 충족 필수)

| # | Condition | Evidence |
|---|-----------|----------|
| RC-01 | G-07 Evaluation Report 통과 | phase4_simulation/4_6_evaluation_report.md |
| RC-02 | Phase 4 테스트 전체 Pass (CRITICAL 0건) | simulation_log.json |
| RC-03 | Docker 이미지 빌드 성공 | docker build exit code 0 |
| RC-04 | docker-compose 전체 서비스 기동 확인 | docker-compose ps (all UP) |
| RC-05 | Health Check 통과 (/health, /ready) | HTTP 200 응답 |
| RC-06 | Monitor-A KPI 수집 정상 작동 | trajectory_logs 최초 INSERT 확인 |
| RC-07 | Rollback 스크립트 테스트 완료 | rollback.sh 실행 → 복원 확인 |

#### 권장 조건 (3항목)

| # | Condition | Evidence |
|---|-----------|----------|
| RC-08 | Smoke Test (주요 API 5개 이상) 통과 | smoke_test_results.json |
| RC-09 | KPI Baseline 대비 Drift 없음 (GREEN) | trajectory_logs drift_level 확인 |
| RC-10 | Alembic 마이그레이션 정상 완료 | alembic current 출력 |

### 6.3 G-08 승인 워크플로우

```
Back-A: release_request INSERT
    │
    ├── review_requests INSERT (gate_id=G-08)
    │     - requested_by: Back-A
    │     - approver: AI Architect + PM
    │     - evidence: RC-01 ~ RC-07 결과 첨부
    │
    ├── AI Architect 검토 (SLA 12h)
    │     └── APPROVED or REJECTED (reason)
    │
    ├── PM 검토 (SLA 12h)
    │     └── APPROVED or REJECTED (reason)
    │
    └── 양쪽 모두 APPROVED → G-08 PASS
         │
         ├── deploy.sh 실행 허용
         └── audit_logs INSERT (action='G-08_PASS')
```

---

## 7. Section 5.6 — Post-Deployment Verification

### 7.1 Smoke Test 시나리오

| # | Endpoint | Method | Expected |
|---|----------|--------|----------|
| ST-01 | /health | GET | 200 OK |
| ST-02 | /ready | GET | 200 OK |
| ST-03 | /api/v1/agents/invoke (auth.login) | POST | 200 + token |
| ST-04 | /api/v1/agents/invoke (menu.get_tree) | POST | 200 + tree |
| ST-05 | /api/v1/agents/invoke (esignature.list) | POST | 200 + items |
| ST-06 | /api/v1/capability/skills | GET | 200 + skills list |
| ST-07 | /api/v1/capability/tools | GET | 200 + tools list |

### 7.2 KPI Baseline 확인

배포 후 24시간 이내 첫 KPI 수집이 정상적으로 trajectory_logs에 INSERT 되는지 확인:

```sql
SELECT kpi_code, actual_value, drift_level, measured_at
FROM trajectory_logs
WHERE tenant_id = :tenant_id
  AND measured_at >= NOW() - INTERVAL '24 hours'
ORDER BY measured_at DESC;
```

모든 K-01 ~ K-07이 GREEN 상태여야 함.

### 7.3 Post-Deploy Monitoring (48h)

| 시간 | 확인 항목 |
|------|----------|
| +1h | Health Check 연속 성공 (3회) |
| +6h | KPI 수집 정상 (trajectory_logs row count >= 6) |
| +12h | Drift YELLOW/RED 없음 |
| +24h | 전체 API 응답시간 500ms 이내 |
| +48h | G-08 Post-Deploy Report 제출 |

---

## 8. 산출물 목록

| # | 산출물 | 형식 | 위치 |
|---|--------|------|------|
| D-01 | Phase 5 방법론 문서 | MD | methodology/phase5_deploy/5_0_deploy_monitoring_overview.md |
| D-02 | Dockerfile (Backend) | Dockerfile | infra/docker/Dockerfile.backend |
| D-03 | Dockerfile (Frontend) | Dockerfile | infra/docker/Dockerfile.frontend |
| D-04 | docker-compose.yml | YAML | infra/docker/docker-compose.yml |
| D-05 | 환경 변수 템플릿 | .env | infra/docker/.env.template |
| D-06 | 배포 스크립트 | Shell | infra/scripts/deploy.sh |
| D-07 | 롤백 스크립트 | Shell | infra/scripts/rollback.sh |
| D-08 | Monitor-A Agent 코드 | Python | backend/src/agents/monitor_agent.py |
| D-09 | trajectory_logs 마이그레이션 | Alembic | backend/alembic/versions/xxx_add_trajectory_logs.py |
| D-10 | override_logs 마이그레이션 | Alembic | backend/alembic/versions/xxx_add_override_logs.py |
| D-11 | KPI 수집 서비스 | Python | backend/src/modules/monitoring/service.py |
| D-12 | Smoke Test 스크립트 | Shell/Python | infra/scripts/smoke_test.sh |
| D-13 | G-08 Release Checklist | JSON/MD | methodology/phase5_deploy/5_5_release_checklist.md |
| D-14 | Post-Deploy Report | MD | methodology/phase5_deploy/reports/5_6_post_deploy_report.md |

---

## 9. Phase 5 → Phase 6 전환 조건

### G-08 통과 후 Phase 6 진입 조건

| # | 조건 | 상태 |
|---|------|------|
| 1 | G-08 Release Gate PASS | [ ] |
| 2 | 프로덕션 48h 안정 운영 확인 | [ ] |
| 3 | KPI 전체 GREEN 유지 | [ ] |
| 4 | Monitor-A Drift Detection 활성 | [ ] |
| 5 | Post-Deploy Report 제출 | [ ] |

Phase 6 (Evolution)에서는 Monitor-A가 탐지한 Drift를 기반으로 Evolution Agent가 Context 수정을 제안하고, Governance Board가 G-09 Gate를 통해 승인하는 피드백 루프가 시작된다.

---

## 10. 참조 문서

| 문서 | 경로 |
|------|------|
| workflow_context.json (G-08 정의) | .cursor/context/workflow_context.json |
| governance_rules_context.json (RISK-04 Drift) | .cursor/context/governance_rules_context.json |
| hitl_context.json (P1 패턴) | .cursor/context/hitl_context.json |
| operation_standards.json (0_5 KPI/모니터링) | .cursor/context/operation_standards.json |
| project_context.json (KPI 정의) | .cursor/context/project_context.json |
| Phase 4 Evaluation Report | methodology/phase4_simulation/4_6_evaluation_report.md |
| Phase 4 Simulation Overview | methodology/phase4_simulation/4_0_simulation_overview.md |
