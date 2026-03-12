# Section 5.5 — G-08 Release Gate Checklist
> Version: v1.0 | Date: 2026-03-11
> Gate: G-08 Release Gate
> Approver: AI Architect + PM (공동 승인)
> HITL: P1 (Pre-approval) | SLA: 24h

---

## 1. 선행 Gate 확인

| Gate | Phase | Status | Evidence |
|------|-------|--------|----------|
| G-01 | Phase 0 | ✅ PASS | saas_foundation.json 확정 |
| G-02 | Phase 1 | ✅ PASS | project_context.json 확정 |
| G-03 | Phase 1 | ✅ PASS | Persona + Scenario 확정 |
| G-04 | Phase 1 | ✅ PASS | Agent R&R 확정 |
| G-05 | Phase 2 | ✅ PASS | Workflow + HITL 확정 |
| G-06 | Phase 3 | ✅ PASS | Capability Code 확정 |
| G-07 | Phase 4 | [ ] | Evaluation Report 확정 |

---

## 2. G-08 필수 체크리스트

### 2.1 Phase 4 검증 완료

| # | 항목 | Status | Evidence |
|---|------|--------|----------|
| RC-01 | G-07 Evaluation Report 통과 | [ ] | 4_6_evaluation_report.md |
| RC-02 | 93개 시뮬레이션 테스트 전체 Pass | [ ] | simulation_log.json (passed=93, failed=0) |
| RC-03 | CRITICAL 이슈 0건 | [ ] | simulation_log.json (critical=0) |

### 2.2 Container Build 검증

| # | 항목 | Status | Command |
|---|------|--------|---------|
| RC-04 | Backend Dockerfile 빌드 성공 | [ ] | `docker build -f Dockerfile.backend .` → exit 0 |
| RC-05 | Frontend Dockerfile 빌드 성공 | [ ] | `docker build -f Dockerfile.frontend .` → exit 0 |
| RC-06 | docker-compose 전체 서비스 기동 | [ ] | `docker-compose ps` → all UP |

### 2.3 Health Check

| # | 항목 | Status | Expected |
|---|------|--------|----------|
| RC-07 | /health 응답 | [ ] | HTTP 200 |
| RC-08 | /ready 응답 | [ ] | HTTP 200 |
| RC-09 | PostgreSQL 연결 | [ ] | `SELECT 1` 성공 |
| RC-10 | Redis 연결 | [ ] | PONG 응답 |

### 2.4 Monitoring 인프라

| # | 항목 | Status | Evidence |
|---|------|--------|----------|
| RC-11 | Monitor-A Agent 등록 | [ ] | OrchestratorAgent.register("monitor.*") |
| RC-12 | trajectory_logs 테이블 생성 | [ ] | `\dt trajectory_logs` |
| RC-13 | KPI 수집 첫 실행 정상 | [ ] | trajectory_logs row count >= 1 |
| RC-14 | Drift Detection 활성 | [ ] | drift_level 판정 로직 정상 |

### 2.5 배포 인프라

| # | 항목 | Status | Evidence |
|---|------|--------|----------|
| RC-15 | Rollback 스크립트 테스트 | [ ] | rollback.sh 실행 → 이전 버전 복원 확인 |
| RC-16 | .env.template 완성 | [ ] | 모든 필수 환경 변수 포함 |
| RC-17 | Secret 하드코딩 없음 | [ ] | grep -r 'password\|secret\|api_key' → 0 결과 |

---

## 3. G-08 권장 체크리스트

| # | 항목 | Status | Note |
|---|------|--------|------|
| RR-01 | Smoke Test 7개 시나리오 통과 | [ ] | ST-01 ~ ST-07 |
| RR-02 | KPI Baseline 대비 Drift 없음 | [ ] | 전체 GREEN |
| RR-03 | Alembic 마이그레이션 정상 | [ ] | alembic current 최신 |
| RR-04 | nginx 리버스 프록시 설정 완료 | [ ] | HTTPS 설정 포함 |
| RR-05 | 로그 수집 (stdout → 중앙 로그) | [ ] | 구조화된 JSON 로그 |

---

## 4. 승인 워크플로우

### 4.1 요청

```json
{
  "gate_id": "G-08",
  "requested_by": "Back-A",
  "requested_at": "2026-03-11T00:00:00Z",
  "evidence": {
    "phase4_report": "methodology/phase4_simulation/4_6_evaluation_report.md",
    "simulation_log": "backend/tests/results/simulation_log.json",
    "docker_build_log": "infra/logs/docker_build.log",
    "health_check_log": "infra/logs/health_check.log"
  },
  "checklist_summary": {
    "mandatory_pass": "17/17",
    "recommended_pass": "5/5"
  }
}
```

### 4.2 승인 (AI Architect + PM 양쪽 모두 필요)

| Approver | Decision | Timestamp | Comment |
|----------|----------|-----------|---------|
| AI Architect | [ ] APPROVED / REJECTED | — | — |
| PM | [ ] APPROVED / REJECTED | — | — |

### 4.3 최종 결정

- 양쪽 모두 APPROVED → **G-08 PASS** → 배포 진행
- 1명이라도 REJECTED → **G-08 FAIL** → 사유 기재 후 재제출

---

## 5. G-08 통과 후 행동

| Step | Action | Owner |
|------|--------|-------|
| 1 | `deploy.sh` 실행 | Back-A |
| 2 | Post-Deploy Smoke Test | Back-A |
| 3 | 48h Monitoring 시작 | Monitor-A |
| 4 | Post-Deploy Report 작성 | AI Architect |
| 5 | Phase 6 진입 준비 | Governance Board |
