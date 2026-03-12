# Section 5.3 — KPI Monitoring Infrastructure Spec
> Version: v1.0 | Date: 2026-03-11
> Owner: Monitor-A (L0, Layer 4)

---

## 1. Monitor-A Agent 스펙

### 1.1 Agent 정의

| 항목 | 값 |
|------|-----|
| Name | MonitorAgent (Monitor-A) |
| Layer | 4 (Monitoring) |
| Authority | L0 (읽기 전용) |
| Risk | LOW |
| allowed_tools | [db_query] |
| Orchestrator 패턴 | `monitor.*` |
| System Prompt | KPI 수집·Drift 탐지·Alert 발행 전용 Agent |

### 1.2 Actions

| Action | Risk | 설명 |
|--------|------|------|
| collect_kpi | LOW | 전체 KPI 데이터 수집 및 trajectory_logs INSERT |
| check_drift | LOW | KPI 값 대비 Drift Level 판정 |
| get_dashboard | LOW | 현재 KPI 상태 대시보드 반환 |
| get_history | LOW | 특정 KPI의 이력 조회 |
| get_alerts | LOW | 활성 Alert 목록 조회 |

### 1.3 Monitor-A 금지 사항

- ❌ DB 직접 쓰기 (INSERT/UPDATE/DELETE → Orch 경유)
- ❌ Agent 중지/재시작 (Override 권한 없음)
- ❌ Evolution 트리거 직접 실행 (제안만 가능)
- ❌ Human 승인 없는 설정 변경

---

## 2. KPI 상세 정의

### K-01: 프레임워크 채택률

| 항목 | 값 |
|------|-----|
| Target | 70%+ |
| Formula | (사용 프로젝트 수 / 전체 등록 프로젝트) × 100 |
| Data Source | reuse_projects 테이블 (status = 'ACTIVE') |
| Collection | 일간 (00:00 UTC) |
| Drift Alert | < 60% |
| Drift Detection | < 50% |

### K-02: 공통 모듈 재사용률

| 항목 | 값 |
|------|-----|
| Target | 50%+ |
| Formula | (재사용 모듈 / 전체 등록 모듈) × 100 |
| Data Source | reuse_modules, reuse_usage_records |
| Collection | 일간 |
| Drift Alert | < 40% |
| Drift Detection | < 30% |

### K-03: 개발 기간 단축

| 항목 | 값 |
|------|-----|
| Target | 30%+ |
| Formula | (기존 평균 기간 - 현재 평균 기간) / 기존 평균 × 100 |
| Data Source | 프로젝트별 started_at ~ completed_at |
| Collection | 주간 (월요일 00:00 UTC) |
| Drift Alert | < 20% |
| Drift Detection | < 10% |

### K-04: AI 승인 프로세스 단축

| 항목 | 값 |
|------|-----|
| Target | 30~40% |
| Formula | (기존 처리시간 - 현재 처리시간) / 기존 × 100 |
| Data Source | review_requests (requested_at ~ resolved_at) |
| Collection | 일간 |
| Drift Alert | < 25% |
| Drift Detection | < 15% |

### K-05: 감사 준비 기간 단축

| 항목 | 값 |
|------|-----|
| Target | 50% |
| Formula | (기존 감사 준비 기간 - 현재) / 기존 × 100 |
| Data Source | audit_logs 기반 보고서 생성 시간 |
| Collection | 월간 (매월 1일) |
| Drift Alert | < 40% |
| Drift Detection | < 30% |

### K-06: 규제 준수율

| 항목 | 값 |
|------|-----|
| Target | 95%+ |
| Formula | governance-checker Pass 수 / 전체 검사 수 × 100 |
| Data Source | governance_check_results 테이블 |
| Collection | 일간 |
| Drift Alert | < 90% |
| Drift Detection | < 85% |

### K-07: Drift 탐지 적용률

| 항목 | 값 |
|------|-----|
| Target | 100% |
| Formula | Monitor-A 모니터링 KPI 수 / 전체 KPI × 100 |
| Data Source | trajectory_logs (DISTINCT kpi_code) |
| Collection | 실시간 |
| Drift Alert | < 90% |
| Drift Detection | < 70% |

---

## 3. Drift Detection 상세

### 3.1 Drift Level 판정 로직

```python
def calculate_drift_level(target: float, actual: float) -> str:
    """
    governance_rules_context.json RISK-04 기준
    """
    if target == 0:
        return "GREEN"

    variance = abs(actual - target) / target

    if variance <= 0.10:       # ±10% 이내
        return "GREEN"
    elif variance <= 0.20:     # 10~20%
        return "YELLOW"
    else:                      # 20% 초과
        return "RED"
```

### 3.2 Drift Level별 행동 규칙

| Level | Action | Notification | SLA |
|-------|--------|-------------|-----|
| GREEN | trajectory_logs INSERT 만 | — | — |
| YELLOW | Alert Queue INSERT | PM (Slack/Email) | 4h 내 확인 |
| RED | CRITICAL Alert | PM + AI Architect | 1h 내 대응 |

### 3.3 Alert Queue 스키마

```sql
CREATE TABLE kpi_alerts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,

    -- KPI 정보
    kpi_code        VARCHAR(10) NOT NULL,
    drift_level     VARCHAR(10) NOT NULL,       -- YELLOW / RED
    actual_value    DECIMAL(10,2) NOT NULL,
    target_value    DECIMAL(10,2) NOT NULL,
    variance_pct    DECIMAL(5,2) NOT NULL,

    -- Alert 상태
    status          VARCHAR(20) NOT NULL DEFAULT 'OPEN',  -- OPEN / ACKNOWLEDGED / RESOLVED
    notified_to     TEXT[] NOT NULL,             -- ['pm@example.com']
    notified_at     TIMESTAMPTZ,

    -- 해결
    acknowledged_by UUID,
    acknowledged_at TIMESTAMPTZ,
    resolved_by     UUID,
    resolved_at     TIMESTAMPTZ,
    resolution      TEXT,

    -- 표준 필드
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by      UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000'
);

CREATE INDEX idx_alerts_status ON kpi_alerts(status) WHERE status = 'OPEN';
CREATE INDEX idx_alerts_tenant_kpi ON kpi_alerts(tenant_id, kpi_code);
```

---

## 4. 대시보드 API 스펙

### 4.1 KPI Dashboard Endpoint

```
GET /api/v1/monitoring/dashboard
→ Monitor-A Agent 경유
```

Response:

```json
{
  "measured_at": "2026-03-11T00:00:00Z",
  "kpis": [
    {
      "code": "K-01",
      "name": "프레임워크 채택률",
      "target": 70.0,
      "actual": 75.0,
      "variance_pct": 7.14,
      "drift_level": "GREEN",
      "trend": "UP"
    }
  ],
  "alerts": {
    "open": 0,
    "acknowledged": 0
  },
  "overall_status": "GREEN"
}
```

### 4.2 KPI History Endpoint

```
GET /api/v1/monitoring/history?kpi_code=K-01&days=30
→ Monitor-A Agent 경유
```

Response: 시계열 trajectory_logs 반환

---

## 5. 구현 파일 목록

| File | Description |
|------|-------------|
| backend/src/modules/monitoring/__init__.py | 모듈 초기화 |
| backend/src/modules/monitoring/agent.py | MonitorAgent (Monitor-A) |
| backend/src/modules/monitoring/service.py | KPI 수집·Drift 판정 로직 |
| backend/src/modules/monitoring/models.py | trajectory_logs, kpi_alerts ORM |
| backend/src/modules/monitoring/schemas.py | KPIDashboard, KPIHistory Pydantic |
| backend/alembic/versions/xxx_monitoring.py | trajectory_logs + kpi_alerts 마이그레이션 |
