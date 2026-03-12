# AI Agent SaaS — Quick Reference Card
### 📙 문서 3 of 3 — 즉시 참조 (Lookup While Coding)

> **목적:** 개발 중 매번 긴 문서를 찾아볼 필요 없이, 자주 쓰는 규칙을 즉시 확인한다.  
> **독자:** 코드 작성 중인 개발자  
> **버전:** v1.0 | **작성일:** 2026년 3월

---

## 1. Naming Rule

### Python

| 대상 | 규칙 | 예시 |
|------|------|------|
| 파일명 | `snake_case` | `agent_service.py` `auth_router.py` |
| 클래스 | `PascalCase` | `AgentService` `RunResult` `TenantContext` |
| 함수 / 변수 | `snake_case` | `run_agent()` `token_count` `org_id` |
| 상수 | `UPPER_SNAKE_CASE` | `MAX_ITERATIONS` `JWT_ALGORITHM` |
| 타입 별칭 | `PascalCase` | `AgentList = list[Agent]` |
| Private | `_underscore` 접두사 | `_execute()` `_validate()` |

### TypeScript / React

| 대상 | 규칙 | 예시 |
|------|------|------|
| 파일 (일반) | `kebab-case` | `agent-client.ts` `use-pagination.ts` |
| 파일 (컴포넌트) | `PascalCase` | `AgentChat.tsx` `UserProfile.tsx` |
| 클래스 / 컴포넌트 | `PascalCase` | `AgentCard` `AuthProvider` |
| 함수 / 변수 | `camelCase` | `runAgent()` `tokenCount` |
| 상수 | `UPPER_SNAKE_CASE` | `MAX_RETRIES` `API_BASE_URL` |
| 타입 / 인터페이스 | `PascalCase` (**I 접두사 금지**) | `Agent` `RunResult` `ApiResponse<T>` |
| React 훅 | `use` 접두사 + `camelCase` | `useAuth()` `useAgentRun()` |
| Zustand 스토어 | `use` + `PascalCase` + `Store` | `useAuthStore()` `useAgentStore()` |
| 이벤트 핸들러 | `handle` 접두사 | `handleSubmit` `handleRunAgent` |

### Database

| 대상 | 규칙 | 예시 |
|------|------|------|
| 테이블명 | `snake_case` **복수형** | `agents` `organization_members` `agent_runs` |
| 컬럼명 | `snake_case` | `agent_id` `created_at` `is_active` |
| PK | `id` (UUID) | `id UUID DEFAULT gen_random_uuid()` |
| FK | `{참조테이블 단수}_id` | `agent_id` `organization_id` `created_by` |
| Boolean | `is_` 또는 `has_` 접두사 | `is_active` `is_deleted` `has_memory` |
| 시간 | `_at` 접미사 | `created_at` `completed_at` `deleted_at` |
| 인덱스 | `idx_{테이블}_{컬럼}` | `idx_agents_org_id` `idx_users_email` |
| 유니크 제약 | `uq_{테이블}_{컬럼}` | `uq_organizations_slug` |
| FK 제약 | `fk_{테이블}_{참조테이블}` | `fk_agent_runs_agents` |

---

## 2. API 엔드포인트 패턴

```
GET    /api/v1/agents                    목록 조회
POST   /api/v1/agents                    생성
GET    /api/v1/agents/{id}               단건 조회
PATCH  /api/v1/agents/{id}               부분 수정 (일부 필드)
PUT    /api/v1/agents/{id}               전체 수정 (모든 필드)
DELETE /api/v1/agents/{id}               삭제

POST   /api/v1/agents/{id}/run           액션 (동사형 서브 리소스)
POST   /api/v1/agents/{id}/run/stream    SSE 스트리밍 실행
GET    /api/v1/agents/{id}/runs          중첩 리소스 목록

GET    /api/v1/organizations/{id}/members   중첩 리소스
POST   /api/v1/organizations/{id}/members   중첩 리소스 생성
```

### 쿼리 파라미터

```
?page=1&size=20                  오프셋 페이지네이션
?cursor=eyJpZCI6Ii4uLiJ9&size=20  커서 페이지네이션 (무한 스크롤)
?sort=-created_at                내림차순 (- 접두사)
?sort=name                       오름차순
?search=키워드                    텍스트 검색
?status=active&plan=pro          필터 (복수 파라미터)
```

---

## 3. 에러 코드 전체 목록

### AUTH (인증/인가)

| 코드 | HTTP | 메시지 |
|------|------|--------|
| `ERR_AUTH_001` | 401 | 인증 토큰이 없습니다 |
| `ERR_AUTH_002` | 401 | 인증 토큰이 만료되었습니다 |
| `ERR_AUTH_003` | 401 | 인증 토큰이 유효하지 않습니다 |
| `ERR_AUTH_004` | 403 | 권한이 없습니다 |
| `ERR_AUTH_005` | 403 | 현재 플랜에서 지원하지 않는 기능입니다 |
| `ERR_AUTH_006` | 403 | 로그인 시도 횟수를 초과했습니다 (15분 후 재시도) |

### USER (사용자)

| 코드 | HTTP | 메시지 |
|------|------|--------|
| `ERR_USER_001` | 404 | 사용자를 찾을 수 없습니다 |
| `ERR_USER_002` | 409 | 이미 사용 중인 이메일입니다 |
| `ERR_USER_003` | 422 | 비밀번호가 조건을 충족하지 않습니다 |

### ORG (조직)

| 코드 | HTTP | 메시지 |
|------|------|--------|
| `ERR_ORG_001` | 404 | 조직을 찾을 수 없습니다 |
| `ERR_ORG_002` | 403 | 멤버 수가 플랜 한도를 초과했습니다 |
| `ERR_ORG_003` | 409 | 이미 사용 중인 조직 슬러그입니다 |
| `ERR_ORG_004` | 404 | 초대를 찾을 수 없거나 만료되었습니다 |

### DATA (데이터)

| 코드 | HTTP | 메시지 |
|------|------|--------|
| `ERR_DATA_001` | 404 | 리소스를 찾을 수 없습니다 |
| `ERR_DATA_002` | 403 | 이 데이터를 수정할 권한이 없습니다 |
| `ERR_DATA_003` | 422 | 입력값이 유효하지 않습니다 |

### AGENT (AI Agent)

| 코드 | HTTP | 메시지 |
|------|------|--------|
| `ERR_AGENT_001` | 422 | Agent 입력값이 유효하지 않습니다 |
| `ERR_AGENT_002` | 503 | Agent 실행 시간이 초과되었습니다 |
| `ERR_AGENT_003` | 422 | 안전 정책에 의해 요청이 차단되었습니다 |
| `ERR_AGENT_004` | 503 | AI 서비스에 일시적 오류가 발생했습니다 |
| `ERR_AGENT_005` | 429 | Agent 실행 한도를 초과했습니다 (플랜 업그레이드 필요) |

### FILE (파일)

| 코드 | HTTP | 메시지 |
|------|------|--------|
| `ERR_FILE_001` | 422 | 허용되지 않는 파일 형식입니다 |
| `ERR_FILE_002` | 422 | 파일 크기가 한도를 초과했습니다 |

### BILL (결제)

| 코드 | HTTP | 메시지 |
|------|------|--------|
| `ERR_BILL_001` | 402 | 결제에 실패했습니다 |
| `ERR_BILL_002` | 402 | 구독이 만료되었습니다 |

### SYS (시스템)

| 코드 | HTTP | 메시지 |
|------|------|--------|
| `ERR_SYS_001` | 500 | 내부 서버 오류가 발생했습니다 |
| `ERR_SYS_002` | 503 | 서비스가 일시적으로 불가능합니다 |

---

## 4. Numbering Rule

### ID 체계

| 유형 | 형식 | 예시 |
|------|------|------|
| DB PK | UUID v4 | `550e8400-e29b-41d4-a716-446655440000` |
| 사용자 노출 ID | `{PREFIX}-{YYYYMMDD}-{SEQ5}` | `AGT-20260301-00001` `RUN-20260301-00023` |
| API Token | `sk_{env}_{random32}` | `sk_live_[32자리_예시]` |
| 요청 추적 ID | UUID (X-Request-ID 헤더) | `req_a1b2c3d4` |

### PREFIX 목록

| 리소스 | PREFIX |
|--------|--------|
| Agent | `AGT` |
| Agent Run | `RUN` |
| Organization | `ORG` |
| User | `USR` |
| Invoice | `INV` |
| Webhook | `WHK` |

### 버전 체계

| 항목 | 형식 | 예시 |
|------|------|------|
| 앱 버전 | `MAJOR.MINOR.PATCH` (Semantic) | `2.1.3` |
| API 버전 | `v{MAJOR}` | `v1` `v2` |
| DB 마이그레이션 | `{YYYYMMDDHHMMSS}_{description}` | `20260301143022_add_agents` |
| Docker 이미지 | `{name}:git-{short-sha}` | `myapp:git-a3f8b2c` |
| 환경별 태그 | `{name}:{env}-{sha}` | `myapp:prod-a3f8b2c` |

---

## 5. 표준 응답 포맷

```json
// ✅ 성공 — 단건
{
  "success": true,
  "data": { "id": "...", "name": "..." },
  "meta": { "request_id": "req_abc", "timestamp": "2026-03-01T12:00:00Z" }
}

// ✅ 성공 — 목록
{
  "success": true,
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "size": 20,
    "total_pages": 5
  }
}

// ❌ 실패
{
  "success": false,
  "error": {
    "code": "ERR_AUTH_002",
    "message": "인증 토큰이 만료되었습니다.",
    "detail": null,
    "request_id": "req_abc",
    "timestamp": "2026-03-01T12:00:00Z"
  }
}
```

---

## 6. React Query Key 규칙

```typescript
// 목록:             ['agents']
// 목록 + 필터:      ['agents', { page, size, status }]
// 단건:             ['agents', agentId]
// 중첩 목록:        ['organizations', orgId, 'members']
// 중첩 단건:        ['organizations', orgId, 'members', memberId]
// 사용자 관련:      ['users', 'me']
// 구독 정보:        ['billing', 'subscription']

// 무효화 예시
queryClient.invalidateQueries({ queryKey: ['agents'] })
queryClient.invalidateQueries({ queryKey: ['agents', agentId] })
```

---

## 7. 코딩 컨벤션 핵심 규칙

### Python — 절대 금지

```python
# ❌ 타입 힌트 없음
def get_agent(id, db):  ...

# ❌ 동기 DB 함수
def get_agent(id: UUID, db) -> Agent:
    return db.query(Agent).filter(...).first()

# ❌ any 타입
def process(data: Any) -> Any:  ...

# ❌ 직접 SQL 문자열
await db.execute(f"SELECT * FROM agents WHERE id = '{agent_id}'")

# ✅ 올바른 예
async def get_agent(agent_id: UUID, session: AsyncSession) -> Agent | None:
    return await session.scalar(
        select(Agent).where(Agent.id == agent_id)
    )
```

### TypeScript — 절대 금지

```typescript
// ❌ any 사용
const data: any = response.data;

// ❌ I 접두사 인터페이스
interface IAgent { ... }

// ❌ enum 키워드 (런타임 번들 포함됨)
enum Status { Active, Inactive }

// ✅ 올바른 예
const data: Agent = response.data;
interface Agent { ... }
const Status = { Active: 'active', Inactive: 'inactive' } as const;
type Status = typeof Status[keyof typeof Status];
```

### Linter 설정

```
Python:     Ruff (Black + isort + flake8 통합) + mypy (strict)
TypeScript: ESLint (recommended + react-hooks) + Prettier
줄 길이:    Python 100자 / TypeScript 100자
Import 정렬: 자동 (Ruff / ESLint)
PR 통과 조건: 위 Linter 오류 0개 (CI에서 강제)
```

---

## 8. 도메인 이벤트 명명 규칙

```
형식: {resource}.{action}

agent.created          agent.updated          agent.deleted
agent.run.started      agent.run.completed    agent.run.failed
user.created           user.updated           user.deleted
user.email_verified    user.password_changed
org.created            org.deleted
org.member.invited     org.member.joined      org.member.removed
billing.subscribed     billing.upgraded       billing.canceled
billing.payment_failed
```

---

## 9. 환경변수 체크리스트

로컬 개발 시작 전 반드시 확인:

```bash
□  DATABASE_URL         postgresql+asyncpg://...
□  REDIS_URL            redis://...
□  SECRET_KEY           32자 이상 랜덤 문자열
□  OPENAI_API_KEY       sk-...
□  NEXT_PUBLIC_API_URL  http://localhost:8000
```

프로덕션 배포 전 반드시 AWS Secrets Manager 확인:

```bash
□  DATABASE_URL         RDS 엔드포인트
□  REDIS_URL            ElastiCache 엔드포인트
□  SECRET_KEY           KMS로 관리
□  OPENAI_API_KEY       KMS로 관리
□  STRIPE_SECRET_KEY    KMS로 관리
□  STRIPE_WEBHOOK_SECRET
```

---

## 10. 자주 쓰는 Make 명령어

```bash
make up           # 전체 서비스 시작
make down         # 전체 서비스 중지
make logs         # 전체 로그 스트리밍
make shell-be     # Backend 컨테이너 bash
make shell-db     # PostgreSQL psql 접속
make migrate      # 마이그레이션 적용 (alembic upgrade head)
make test-be      # Backend 테스트 실행
make test-fe      # Frontend 테스트 실행
make lint-be      # Backend ruff + mypy
make lint-fe      # Frontend eslint + tsc
```

---

## 문서 연결

| 궁금한 내용 | 확인할 문서 |
|------------|------------|
| "왜 이 기술을 선택했나?" | 📘 Framework — 해당 결정 항목 |
| "왜 이렇게 설계했나?" | 📘 Framework — ADR 목록 |
| "어떤 순서로 만드나?" | 📗 Implementation Guide — Phase 1~6 |
| "이 파일을 어떻게 만드나?" | 📗 Implementation Guide — 해당 Step |
| "함수/파일 이름을 어떻게 짓나?" | 📙 이 문서 — Section 1 |
| "에러 코드가 뭐지?" | 📙 이 문서 — Section 3 |
| "API URL 형식이 뭐지?" | 📙 이 문서 — Section 2 |
