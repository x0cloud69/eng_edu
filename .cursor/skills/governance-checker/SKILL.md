---
name: governance-checker
description: >
  Scans all business modules for missing governance patterns — BaseAgent inheritance, ApprovalGate,
  AuditLog, Scope validation, tenant isolation, and soft delete compliance.
  Use when the user says "거버넌스 검사", "governance check", "누락 검사", "compliance check",
  "표준 준수 확인", "Phase 3 점검", or any request to verify framework standard compliance.
---

# Governance Checker — AI-Native SaaS 표준 프레임워크

## 역할

프로젝트의 모든 비즈니스 모듈이 프레임워크 표준을 준수하는지 검사하고,
위반 항목을 보고하며 수정 방법을 제시한다.

## 검사 실행 방법

사용자가 검사를 요청하면, 아래 6개 카테고리를 순서대로 전체 스캔한다.
모든 모듈(`backend/src/modules/*/`)을 대상으로 한다.
`example` 모듈은 참조 구현이므로 검사에서 제외하지 않는다(오히려 기준으로 사용).

---

## 카테고리 1: Agent 연결 검사

### 검사 항목

| ID | 검사 | 위반 시 |
|----|------|---------|
| AG-01 | 모듈 폴더에 `agent.py` 파일이 존재하는가? | 🔴 CRITICAL — Agent 없으면 거버넌스 흐름 미적용 |
| AG-02 | Agent 클래스가 `BaseAgent`를 상속하는가? | 🔴 CRITICAL — run() 표준 흐름 미적용 |
| AG-03 | `name` 속성이 선언되어 있는가? | 🟡 WARNING — 감사 로그에 Agent 식별 불가 |
| AG-04 | `authority_level` 속성이 선언되어 있는가? | 🔴 CRITICAL — ApprovalGate 판단 불가 |
| AG-05 | `allowed_tools` 속성이 선언되어 있는가? | 🔴 CRITICAL — Scope 검증 불가 |
| AG-06 | `execute()` 메서드가 `async def`로 구현되어 있는가? | 🔴 CRITICAL — Agent 실행 불가 |
| AG-07 | `execute()`가 항상 `AgentResult`를 반환하는가? (예외 시에도) | 🟡 WARNING — 에러 시 미처리 |

### 검사 방법

```
1. backend/src/modules/ 하위의 모든 디렉토리를 순회
2. 각 디렉토리에서 agent.py 파일 존재 확인
3. agent.py 내의 클래스가 BaseAgent를 상속하는지 확인
4. name, authority_level, allowed_tools 클래스 속성 확인
5. execute() 메서드 존재 및 async 여부 확인
```

---

## 카테고리 2: Orchestrator 등록 검사

### 검사 항목

| ID | 검사 | 위반 시 |
|----|------|---------|
| OR-01 | `main.py`에 `OrchestratorAgent.register("{module}.*", Agent())` 호출이 있는가? | 🔴 CRITICAL — Agent가 존재해도 호출 불가 |
| OR-02 | `main.py`에 `app.include_router(router)`가 있는가? | 🟡 WARNING — REST API 미노출 |
| OR-03 | Agent 등록 패턴이 `"{module_name}.*"` 형식인가? | 🟡 WARNING — 라우팅 매칭 실패 가능 |

### 검사 방법

```
1. backend/src/api/main.py 파일을 읽는다
2. OrchestratorAgent.register() 호출 목록을 추출한다
3. app.include_router() 호출 목록을 추출한다
4. modules/ 하위 모듈 목록과 대조하여 누락된 것을 찾는다
```

---

## 카테고리 3: 테넌트 격리 검사

### 검사 항목

| ID | 검사 | 위반 시 |
|----|------|---------|
| TN-01 | `models.py`의 모델이 `TenantBaseModel`을 상속하는가? | 🔴 CRITICAL — 테넌트 격리 없음 |
| TN-02 | `repository.py`의 모든 쿼리에 `tenant_id` 필터가 있는가? | 🔴 CRITICAL — 데이터 유출 위험 |
| TN-03 | `repository.py`의 모든 쿼리에 `deleted_at.is_(None)` 필터가 있는가? | 🔴 CRITICAL — 삭제된 데이터 노출 |
| TN-04 | `service.py` 생성자에서 `tenant_id`를 받는가? | 🟡 WARNING — 테넌트 주입 패턴 미준수 |
| TN-05 | 물리 DELETE 쿼리(`session.delete()`)가 없는가? | 🔴 CRITICAL — 물리 삭제 금지 위반 |

### 검사 방법

```
1. models.py → 클래스 상속 대상 확인 (TenantBaseModel 또는 BaseModel)
2. repository.py → select() 문에서 tenant_id, deleted_at 필터 존재 확인
3. repository.py → session.delete() 호출이 없는지 확인
4. service.py → __init__() 파라미터에 tenant_id 존재 확인
```

---

## 카테고리 4: 감사 로그 검사

### 검사 항목

| ID | 검사 | 위반 시 |
|----|------|---------|
| AU-01 | `service.py`의 create/update/delete 메서드에 `create_audit_log()` 호출이 있는가? | 🔴 CRITICAL — CUD 작업 감사 추적 불가 |
| AU-02 | `create_audit_log()` 호출 시 `action`, `resource_type`, `resource_id`가 포함되는가? | 🟡 WARNING — 감사 로그 식별 불완전 |
| AU-03 | Agent의 `execute()` 실행 결과가 `AuditLogger.log()`로 기록되는가? | 🟢 INFO — BaseAgent.run()이 자동 처리하지만, 확인 필요 |

### 검사 방법

```
1. service.py → create, update, soft_delete 메서드 내에서 create_audit_log 호출 확인
2. create_audit_log 호출의 인자에 action, resource_type, resource_id 존재 확인
3. agent.py → BaseAgent.run()이 자동 처리하므로 INFO 수준으로만 확인
```

---

## 카테고리 5: API 표준 검사

### 검사 항목

| ID | 검사 | 위반 시 |
|----|------|---------|
| AP-01 | `router.py`의 prefix가 `/api/v1/{module_name}` 형식인가? | 🟡 WARNING — API 경로 비표준 |
| AP-02 | GET 목록 응답이 `PaginatedResponse`로 래핑되는가? | 🟡 WARNING — 페이지네이션 비표준 |
| AP-03 | 단건/생성/수정 응답이 `ApiResponse`로 래핑되는가? | 🟡 WARNING — 응답 포맷 비표준 |
| AP-04 | DELETE가 `status_code=204`이고 soft delete를 사용하는가? | 🟡 WARNING — 삭제 패턴 비표준 |
| AP-05 | 인증 의존성(`get_current_user`)이 적용되어 있는가? | 🔴 CRITICAL — 인증 없이 API 노출 |

### 검사 방법

```
1. router.py → APIRouter prefix 형식 확인
2. router.py → response_model 타입 확인 (PaginatedResponse, ApiResponse)
3. router.py → delete 엔드포인트의 status_code와 soft_delete 사용 확인
4. router.py → Depends(get_current_user) 또는 _auth 사용 확인
```

---

## 카테고리 6: 모듈 완성도 검사

### 검사 항목

| ID | 검사 | 위반 시 |
|----|------|---------|
| CM-01 | 7개 필수 파일이 모두 존재하는가? (__init__, models, schemas, repository, service, router, agent) | 🟡 WARNING — 불완전한 모듈 |
| CM-02 | `schemas.py`에 Create, Update, Out 3개 스키마가 있는가? | 🟡 WARNING — CRUD 스키마 불완전 |
| CM-03 | `schemas.py`의 Out 스키마에 `model_config = {"from_attributes": True}`가 있는가? | 🟡 WARNING — ORM → Pydantic 변환 오류 가능 |

---

## 보고 형식

검사 완료 후 아래 형식으로 보고한다:

```
## 거버넌스 검사 보고서

### 검사 대상: {모듈 수}개 모듈
### 검사 일시: {현재 시각}

### 요약
- 🔴 CRITICAL: {n}건 — 즉시 수정 필요
- 🟡 WARNING: {n}건 — 수정 권장
- 🟢 INFO: {n}건 — 참고
- ✅ PASS: {n}건 — 표준 준수

### 모듈별 결과

#### {module_name}
| ID | 결과 | 설명 |
|----|------|------|
| AG-01 | ✅ PASS | agent.py 존재 |
| AG-02 | ✅ PASS | BaseAgent 상속 |
| TN-01 | 🔴 CRITICAL | TenantBaseModel 미상속 — BaseModel 사용 중 |
| AU-01 | 🔴 CRITICAL | create() 메서드에 create_audit_log 누락 |

### 수정 가이드

#### TN-01 수정 — {module_name}/models.py
현재: `class MyModel(BaseModel)`
수정: `class MyModel(TenantBaseModel)`
참조: @backend/src/modules/example/models.py

#### AU-01 수정 — {module_name}/service.py
누락: create() 메서드에 create_audit_log() 호출 추가 필요
참조: @backend/src/modules/example/service.py (lines 32-51)
```

---

## 자동 수정 제안

CRITICAL 위반 항목에 대해서는 수정 코드를 직접 제안한다.
사용자가 승인하면 수정을 적용한다.

### 자동 수정 가능 항목
- AG-01: agent.py 파일 생성 (module-generator 스킬 연계)
- TN-01: models.py 상속 대상 변경
- TN-05: session.delete() → soft_delete() 교체
- AU-01: create_audit_log() 호출 추가

### 자동 수정 불가 항목 (수동 검토 필요)
- AG-04/AG-05: authority_level과 allowed_tools는 비즈니스 판단 필요
- OR-01: Orchestrator 등록 패턴은 모듈 의도에 따라 달라짐

---

## Reference Files
- @backend/src/modules/example/ — 완전한 참조 구현 (7개 파일 표준 패턴)
- @backend/src/modules/MODULE_TEMPLATE.md — 모듈 추가 체크리스트
- @backend/src/core/base_agent.py — BaseAgent 표준 실행 흐름
- @backend/src/core/base_model.py — TenantBaseModel 정의
- @.cursor/rules/09_capability.mdc — Phase 3 코드 생성 규칙
- @.cursor/rules/11_hitl_patterns.mdc — P1/P2/P3 패턴 코드 규칙
- @.cursor/rules/07_scope_governance.mdc — Scope 경계 + MVP 품질 게이트
