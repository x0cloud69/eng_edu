# Phase 1 산출물 검토 보고서
## Standard Framework Project

| 항목 | 내용 |
|------|------|
| 검토 범위 | Phase 1 전체 산출물 (1.1~1.6) + Cursor context/rules |
| 검토 방식 | 문서 간 교차 검증 + Cursor 컨텍스트 일관성 검토 |
| 발견 이슈 | 6건 (Critical 2, Medium 2, Minor 2) |
| 수정 완료 | 6건 전체 |

---

## 발견된 이슈 및 수정 내역

---

### [이슈 #1] 🔴 Critical — `governance.json` drift_monitoring 오기

**파일**: `.cursor/context/governance.json`

| 항목 | 내용 |
|------|------|
| 위치 | `current_project_governance.drift_monitoring` |
| 기존 값 | `false` |
| 수정 값 | `true` |
| 근거 | 1.4 Authority Model 명시: "Drift 모니터링: Monitor-A가 담당 — KPI Threshold 초과 시 즉시 알림" |
| 영향 | Cursor가 코드 생성 시 Drift 탐지 로직을 선택 사항으로 인식할 위험 |

**수정 전**
```json
"drift_monitoring": false
```
**수정 후**
```json
"drift_monitoring": true
```

---

### [이슈 #2] 🔴 Critical — `saas_foundation.json` vs `04_saas_stack.mdc` Refresh Token TTL 불일치

**파일**: `.cursor/context/saas_foundation.json`

| 항목 | 내용 |
|------|------|
| 위치 | `common_modules.auth.refresh_token_ttl` |
| 기존 값 | `"7일"` |
| 수정 값 | `"30일"` |
| 근거 | `04_saas_stack.mdc` 규칙 4에서 `create_refresh_token(user_id) # 30일`로 명시 |
| 영향 | Cursor가 코드 생성 시 어느 값을 따를지 불명확. 보안 정책 불일치 발생 가능 |

**수정 전**
```json
"refresh_token_ttl": "7일"
```
**수정 후**
```json
"refresh_token_ttl": "30일"
```

---

### [이슈 #3] 🟡 Medium — `1.4 Authority Model.md` Orch 카드 `자동 실행` 항목 오기

**파일**: `1_4_Authority_Model.md`

| 항목 | 내용 |
|------|------|
| 위치 | Orch Agent 카드 — `자동 실행` 항목 |
| 기존 값 | "L0 — 탐지·알림 자동 수행 (실행 권한 없음) / Incident 대응 결정은 Human 승인 필수" |
| 수정 값 | "불가 — Human 승인 필수" |
| 근거 | Orch는 Authority L1이므로 자동 실행 불가. 기재된 내용은 Monitor-A(L0)의 설명으로 오기된 것 |
| 영향 | Orch Agent의 자율성 범위를 잘못 해석할 수 있음 |

---

### [이슈 #4] 🟡 Medium — `1.5 HITL Structure.md` Back-A 비고 항목에 Evol-A 설명 혼재

**파일**: `1_5_HITL_Structure.md`

| 항목 | 내용 |
|------|------|
| 위치 | 4장 Agent별 HITL 적용 기준 표 — Back-A 비고 |
| 기존 값 | "DB 변경 = P1. 실행 중 = P2. 코드 = P3. **P2 없음: Context 제안 단계는 실행 없음 — 이상 시 Orch P2 대리 처리**" |
| 수정 값 | "DB 변경 = P1. 실행 중 Risk 감지 = P2. 코드 산출물 = P3" |
| 근거 | "Context 제안 단계" 설명은 Evol-A 관련 내용. Back-A는 P2=✅ 이므로 P2 없음 문구는 오기. Evol-A 비고와 혼재된 것으로 추정 |

---

### [이슈 #5] 🟢 Minor — `governance.json` L0 `human_approval` 정의 불명확

**파일**: `.cursor/context/governance.json`

| 항목 | 내용 |
|------|------|
| 위치 | `authority_levels.L0.human_approval` |
| 기존 값 | `"불필요"` |
| 수정 값 | `"탐지·알림은 자동, 대응 결정은 Human 필요"` |
| 근거 | Monitor-A는 L0이지만 1.4에서 "Incident 대응 결정"은 Human Gate 명시. "불필요"는 오해 소지 |
| 추가 | `description`, `typical_use`, `note` 필드도 Monitor-A 실제 역할에 맞게 보완 |

---

### [이슈 #6] 🟢 Minor — `03_context_management.mdc` agents/ 서브폴더 미생성 상태 미표기

**파일**: `.cursor/rules/03_context_management.mdc`

| 항목 | 내용 |
|------|------|
| 위치 | "Context 파일 구조" 섹션 내 agents/ 서브폴더 |
| 문제 | 규칙 파일에 agents/ 하위 5개 JSON 정의되어 있으나 실제 파일 미존재. Cursor가 해당 파일을 참조하려 할 경우 오류 발생 가능 |
| 수정 | agents/ 폴더에 "Phase 3 구현 시 생성 예정 (현재 미생성)" 주석 추가 및 생성 방식 안내 |

---

## 수정 파일 목록

| 파일 | 이슈 | 변경 버전 |
|------|------|-----------|
| `.cursor/context/governance.json` | #1, #2, #5 | v1.1 → v1.2 |
| `.cursor/context/saas_foundation.json` | #3 | - |
| `.cursor/rules/03_context_management.mdc` | #6 | - |
| `1_4_Authority_Model.md` | #4 | v1.0 → v1.1 |
| `1_5_HITL_Structure.md` | #5 | v1.0 → v1.1 |

---

## Phase 1 산출물 전반 평가

전반적으로 문서 간 일관성이 높고, Cursor 컨텍스트와 소스 문서 간 매핑 구조가 잘 잡혀 있습니다. 발견된 이슈는 모두 **단순 오기 또는 복사-붙여넣기 실수** 수준이며, 구조적 설계 문제는 없습니다.

특히 다음 사항들은 잘 설계되어 있습니다.

- Authority Level 체계(L0~L3)와 Agent별 HITL 패턴(P1/P2/P3)의 이중 통제 구조
- governance.json / hitl_context.json / rr_matrix_context.json 간 교차 참조 구조
- Cursor rules 우선순위 체계 (01_principles > 02_security > ... 순)
- scope_context.json과 governance_rules_context.json을 Phase 3 직전에 추가한 판단

---

*검토일: 2026-03-09 | 검토자: Claude*
