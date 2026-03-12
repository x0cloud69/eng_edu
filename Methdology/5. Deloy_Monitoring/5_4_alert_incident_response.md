# Section 5.4 — Alert & Incident Response
> Version: v1.0 | Date: 2026-03-11
> Owner: Monitor-A (Alert 발행) / Governance Board (Incident 대응)

---

## 1. Alert 체계

### 1.1 Severity 분류

| Level | Trigger | Response Time | Responder | Auto Action |
|-------|---------|---------------|-----------|-------------|
| **INFO** | KPI 수집 완료, 정상 로그 | — | — | trajectory_logs INSERT |
| **WARNING** | YELLOW drift (KPI 10~20% 하락) | 4h | PM | Alert Queue INSERT + 알림 |
| **CRITICAL** | RED drift (KPI 20%+ 하락) | 1h | AI Architect + PM | CRITICAL Alert + Evolution 제안 |
| **EMERGENCY** | 시스템 장애, 데이터 유출, 보안 침해 | 즉시 | Governance Board + 운영팀 | Human Override 절차 가동 |

### 1.2 Alert 생성 규칙

```python
# Monitor-A가 KPI 수집 후 Drift Level에 따라 Alert 생성

async def generate_alert(kpi_result: KPIResult) -> Alert | None:
    if kpi_result.drift_level == "GREEN":
        return None  # Alert 불필요

    elif kpi_result.drift_level == "YELLOW":
        return Alert(
            severity="WARNING",
            kpi_code=kpi_result.kpi_code,
            message=f"{kpi_result.kpi_name}: {kpi_result.variance_pct:.1f}% 하락 (경고)",
            notify_to=["pm"],
            sla_hours=4,
        )

    elif kpi_result.drift_level == "RED":
        return Alert(
            severity="CRITICAL",
            kpi_code=kpi_result.kpi_code,
            message=f"{kpi_result.kpi_name}: {kpi_result.variance_pct:.1f}% 하락 (위험)",
            notify_to=["ai_architect", "pm"],
            sla_hours=1,
            evolution_proposal=True,  # Evolution Agent 개선 제안 트리거
        )
```

---

## 2. Escalation Chain

### 2.1 자동 Escalation 규칙

```
WARNING (4h 미응답)
  → 자동 승격: CRITICAL
    → AI Architect + PM 추가 알림

CRITICAL (24h 미해결)
  → 자동 승격: EMERGENCY
    → Governance Board 긴급 소집 알림
    → Human Override 절차 준비
```

### 2.2 Escalation 타임라인

```
T+0     Monitor-A: Drift 탐지
        │
T+5min  Alert Queue INSERT + 1차 알림 발송
        │
T+4h    ┌── WARNING 미확인 → CRITICAL 승격
        │   └── AI Architect + PM 2차 알림
        │
        └── WARNING 확인됨 → ACKNOWLEDGED
            └── 해결 기한: T+24h
        │
T+24h   ┌── CRITICAL 미해결 → EMERGENCY 승격
        │   └── Governance Board 긴급 소집
        │
        └── CRITICAL 해결됨 → RESOLVED
            └── resolution 기록
```

---

## 3. Incident Response Procedure

### 3.1 CRITICAL Incident 대응

| Step | Action | Owner | SLA |
|------|--------|-------|-----|
| 1 | Alert 수신 및 확인 | PM or AI Architect | 15min |
| 2 | 원인 분석 (trajectory_logs 검토) | AI Architect | 1h |
| 3 | 긴급 조치 결정 (패치/롤백/설정변경) | AI Architect + PM | 2h |
| 4 | 조치 실행 | Back-A (승인 후) | 4h |
| 5 | 검증 (Smoke Test + KPI 재확인) | Monitor-A | 1h |
| 6 | Incident Report 작성 | AI Architect | 24h |

### 3.2 EMERGENCY Incident 대응 (Human Override)

| Step | Action | Owner | SLA |
|------|--------|-------|-----|
| 1 | Governance Board 긴급 소집 | Board Chair | 30min |
| 2 | 위험 Agent 즉시 중지 결정 | Board (과반수) | 1h |
| 3 | Quick Shutdown 실행 | 운영팀 (L3 권한) | 즉시 |
| 4 | override_logs INSERT | 자동 | — |
| 5 | 근본 원인 분석 (RCA) | AI Architect | 48h |
| 6 | 복구 계획 수립 | Board | 24h |
| 7 | 복구 실행 및 재시작 승인 | Board Chair | — |
| 8 | Post-Incident Report | AI Architect | 72h |

### 3.3 Quick Shutdown 절차

```bash
#!/bin/bash
# quick-shutdown.sh — EMERGENCY 시 Agent 즉시 중지
# 실행 권한: Governance Board 승인 필요 (L3)

set -euo pipefail

AGENT_NAME=$1
REASON=$2
EXECUTOR=$3

echo "[EMERGENCY] Shutting down $AGENT_NAME"
echo "Reason: $REASON"
echo "Executor: $EXECUTOR"

# 1. Agent 중지 요청
curl -X POST "$API_URL/api/v1/agents/invoke" \
    -d "{\"action\":\"orch.stop_agent\",\"payload\":{\"agent\":\"$AGENT_NAME\"}}"

# 2. override_logs 기록
curl -X POST "$API_URL/api/v1/agents/invoke" \
    -d "{
        \"action\":\"audit.log_override\",
        \"payload\":{
            \"trigger_reason\": \"$REASON\",
            \"severity\": \"EMERGENCY\",
            \"affected_agents\": [\"$AGENT_NAME\"],
            \"action\": \"STOP\",
            \"executed_by\": \"$EXECUTOR\"
        }
    }"

echo "[EMERGENCY] $AGENT_NAME stopped. Override logged."
```

---

## 4. override_logs 상세

### 4.1 스키마 (재확인)

```sql
CREATE TABLE override_logs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL,
    trigger_reason      TEXT NOT NULL,
    severity            VARCHAR(20) NOT NULL,       -- CRITICAL / EMERGENCY
    affected_agents     TEXT[] NOT NULL,
    action              VARCHAR(20) NOT NULL,        -- STOP / PAUSE / RESTART
    executed_by         UUID NOT NULL,
    executed_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolution          TEXT,
    restart_approved_by UUID,
    restart_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          UUID NOT NULL
);
```

### 4.2 Override 행동 유형

| Action | 설명 | 복구 조건 |
|--------|------|----------|
| STOP | Agent 즉시 중지 | Board 재시작 승인 |
| PAUSE | Agent 일시 중지 (새 요청만 차단) | AI Architect 승인 |
| RESTART | 중지된 Agent 재시작 | Board 승인 + Post-Incident Report 완료 |

---

## 5. Post-Incident Report 템플릿

```markdown
# Post-Incident Report — [INCIDENT_ID]

## 1. 요약
- **발생 시각**: YYYY-MM-DD HH:MM UTC
- **탐지 시각**: YYYY-MM-DD HH:MM UTC (탐지 소요: Xmin)
- **해결 시각**: YYYY-MM-DD HH:MM UTC (해결 소요: Xh)
- **Severity**: CRITICAL / EMERGENCY
- **영향 범위**: [Agent명, Tenant명, 기능 범위]

## 2. 타임라인
| 시각 | 이벤트 |
|------|--------|
| ... | ... |

## 3. 근본 원인 (RCA)
- ...

## 4. 조치 내역
- ...

## 5. 재발 방지 대책
- ...

## 6. KPI 영향 분석
| KPI | 사고 전 | 사고 중 | 사고 후 |
|-----|---------|---------|---------|
| ... | ... | ... | ... |
```
