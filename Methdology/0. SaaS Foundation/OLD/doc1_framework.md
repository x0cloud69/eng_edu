# AI Agent SaaS Development Framework
### 📘 문서 1 of 3 — 설계 지도 (Why & What)

> **목적:** 우리 SaaS가 다뤄야 할 설계 영역 전체와, 각 영역에서 내린 결정 및 그 이유를 기록한다.  
> **독자:** 전체 팀 — 특히 신규 팀원 온보딩 첫 번째 문서  
> **버전:** v1.0 | **작성일:** 2026년 3월

> ⚠️ **이 문서를 읽는 순서**
> 1. 📘 **이 문서** — "우리가 무엇을, 왜 이렇게 결정했는가?" 를 이해한다
> 2. 📗 **Implementation Guide** — "어떻게 코드로 구현하는가?" 를 따라 만든다
> 3. 📙 **Quick Reference** — 개발 중 Naming/에러코드 등 규칙을 즉시 참조한다

---

## 전체 설계 영역 지도

```
AI Agent SaaS Framework  (이 문서)
│
├── 01 Platform Foundation        기반 구조, 기술 스택, 환경 설정
├── 02 Identity & Access          인증·인가·세션·OAuth
├── 03 Tenant Management          멀티테넌시, 조직, 구독 플랜
├── 04 Data Governance            데이터 보안·보존·감사
├── 05 Application Architecture   서비스 구조, 모듈, 이벤트
├── 06 Integration & API          API 설계, Webhook, 외부 연동
├── 07 Observability              로깅, 메트릭, 트레이싱, 알림
├── 08 Governance & Standards     네이밍, 컨벤션, 보안, ADR
├── 09 Localization               다국어, 시간대, 통화
└── 10 AI Agent Architecture      Agent 설계·메모리·오케스트레이션·안전
```

> **이 문서의 역할:** 각 영역에서 "무엇을 결정해야 하는가"와 "우리는 어떻게 결정했는가"를 담는다.
> 실제 구현 코드와 파일 생성 순서는 📗 Implementation Guide를 참고한다.

---

# 01 Platform Foundation

## 결정 1 — 기술 스택

### 왜 이 기술들을 선택했는가?

| 계층 | 선택 | 선택하지 않은 대안 | 결정 이유 |
|------|------|--------------------|-----------|
| Backend | **FastAPI** | Django REST, Express | async 완전 지원 + 자동 OpenAPI 문서 + Python AI 생태계 |
| ORM | **SQLAlchemy 2.0 async** | Tortoise ORM, Prisma | 가장 성숙한 Python async ORM, Alembic 마이그레이션 통합 |
| Frontend | **Next.js 14 (App Router)** | Vite+React, Remix | SSR/SSG/ISR 혼합 가능, TypeScript 기본, SEO |
| Primary DB | **PostgreSQL 16** | MySQL, MongoDB | ACID + JSONB + pgvector(AI 임베딩) 단일 DB로 해결 |
| Cache/Queue | **Redis 7** | Memcached, RabbitMQ | In-Memory + Pub/Sub + Stream + Session 단일 도구 |
| Task Queue | **Celery** | Dramatiq, ARQ | Python 생태계 표준, 재시도·스케줄링 완성도 |
| AI Orchestration | **LangChain + LangGraph** | AutoGen, CrewAI | Agent 상태 기반 워크플로우 표준, 생태계 최대 |
| Vector DB | **pgvector → Qdrant** | Pinecone, Weaviate | 초기엔 PG 통합, 규모 증가 시 전문 벡터 DB 전환 |
| UI Component | **shadcn/ui + Tailwind** | MUI, Ant Design | 컴포넌트 소유권 + 번들 크기 최소화 + 커스터마이징 자유 |

### 기술 선택 기준 (우선순위)

```
1순위  팀 숙련도 + AI/ML 생태계 호환성  ★★★★★
2순위  생태계 성숙도 + 레퍼런스 풍부도  ★★★★☆
3순위  성능 및 수평 확장 가능성         ★★★★☆
4순위  장기 유지보수성                  ★★★★☆
5순위  채용 용이성                      ★★★☆☆
6순위  라이선스 및 운영 비용            ★★★☆☆
```

## 결정 2 — 환경 전략

| 환경 | 목적 | 인프라 | 데이터 |
|------|------|--------|--------|
| `local` | 개발자 개인 개발 | Docker Compose | 개인 더미 데이터 |
| `dev` | 팀 통합 테스트 | Railway / Render | 공유 테스트 데이터 |
| `staging` | 프로덕션 검증 | AWS (운영 동일 구성) | 프로덕션 익명화 데이터 |
| `production` | 실제 서비스 | AWS ECS + RDS | 실제 데이터 |

**왜 4개 환경인가?** dev가 없으면 main 브랜치가 곧 staging이 되어 팀 협업이 어려워진다. staging이 없으면 프로덕션 배포 전 검증이 불가능하다.

## 결정 3 — Feature Flag

코드 배포 없이 기능을 켜고 끌 수 있게 한다. 플랜 제한·베타 테스트·점진적 롤아웃에 사용한다.

**왜 필요한가?** 완성되지 않은 기능이 코드에 있더라도 사용자에게 노출되지 않아야 하고, 특정 플랜(pro/enterprise) 사용자에게만 기능을 선별 제공해야 한다.

| 플래그 키 | 기본값 | 활성화 조건 | 용도 |
|-----------|--------|-------------|------|
| `ai_agent_enabled` | false | pro 이상 | AI Agent 전체 기능 |
| `ai_agent_advanced` | false | enterprise | 멀티에이전트 오케스트레이션 |
| `api_access` | false | pro 이상 | API Token 직접 접근 |
| `sso_saml` | false | enterprise | SAML SSO |
| `export_excel` | false | pro 이상 | Excel 내보내기 |
| `custom_domain` | false | enterprise | 커스텀 도메인 연결 |

---

# 02 Identity & Access

## 결정 4 — 인증 방식

**결정: JWT Access Token (15분) + Refresh Token (30일, Rotate)**

### 왜 JWT인가?

| 방식 | 고려 이유 | 탈락 이유 |
|------|-----------|-----------|
| JWT ✅ | Stateless → 수평 확장 용이 | 토큰 강제 만료 어려움 → Refresh Rotate로 보완 |
| Session | 즉시 무효화 가능 | Redis 의존 + 수평 확장 시 세션 공유 복잡 |
| Passwordless | 보안 강화 | UX 변화 크고 이메일 발송 인프라 의존 |

### 토큰 전략 세부 결정

```
Access Token  : 만료 15분  | 저장: 클라이언트 메모리 (Zustand)
Refresh Token : 만료 30일  | 저장: HttpOnly Cookie (SameSite=Strict)
Refresh Rotate: 사용할 때마다 새 Refresh Token 발급 + 이전 토큰 즉시 Blacklist
Blacklist     : Redis에 jti 저장, TTL = 토큰 남은 만료 시간

왜 Access Token을 메모리에? → LocalStorage는 XSS 공격으로 탈취 가능
왜 Refresh Rotate? → 탈취된 Refresh Token을 1회 사용 즉시 감지 가능
```

## 결정 5 — 인가 모델 (RBAC)

**결정: 4단계 역할 기반 접근 제어**

**왜 RBAC인가?** ABAC(속성 기반)는 표현력이 높지만 구현 복잡도가 높다. 초기 B2B SaaS는 RBAC으로 95%의 요구사항을 충족할 수 있으며, 이후 ABAC을 레이어로 추가할 수 있다.

| 역할 | 코드 | 핵심 권한 |
|------|------|-----------|
| 소유자 | `owner` | 모든 권한 + 조직 삭제. 조직당 1명. 양도 가능 |
| 관리자 | `admin` | 멤버 관리 + 설정 변경 + 전체 데이터 CRUD |
| 멤버 | `member` | 데이터 CRUD + Agent 실행 |
| 뷰어 | `viewer` | 읽기 전용 |

### 퍼미션 매트릭스

| 퍼미션 | owner | admin | member | viewer |
|--------|-------|-------|--------|--------|
| `org:delete` | ✅ | ❌ | ❌ | ❌ |
| `org:settings` | ✅ | ✅ | ❌ | ❌ |
| `members:invite` | ✅ | ✅ | ❌ | ❌ |
| `data:create` | ✅ | ✅ | ✅ | ❌ |
| `data:read` | ✅ | ✅ | ✅ | ✅ |
| `data:delete` | ✅ | ✅ | ❌ | ❌ |
| `agent:run` | ✅ | ✅ | ✅ | ❌ |
| `agent:manage` | ✅ | ✅ | ❌ | ❌ |
| `billing:manage` | ✅ | ✅ | ❌ | ❌ |

## 결정 6 — 소셜 로그인 우선순위

| Provider | 우선순위 | 이유 |
|----------|----------|------|
| Google OAuth2 | 1순위 (필수) | B2B 고객 대부분이 Google Workspace 사용. 프로필 자동 수집 |
| GitHub OAuth | 2순위 | 개발자 향 제품. 내부 테스트에도 유용 |
| Microsoft Entra | 3순위 (Enterprise) | 대기업 고객 SAML/SSO 확장 시 필요 |

---

# 03 Tenant Management

## 결정 7 — 멀티테넌시 격리 전략

**결정: Pool 방식 (Row-level isolation, organization_id)**

### 왜 Pool인가?

| 전략 | 격리 수준 | 운영 비용 | 결정 |
|------|-----------|-----------|------|
| Silo (DB 분리) | 최상 | 테넌트 수 × 비용 | ❌ 초기 스타트업에 부적합 |
| Bridge (Schema 분리) | 높음 | 관리 복잡도 증가 | ❌ 마이그레이션 관리 어려움 |
| **Pool (Row 분리)** | 중간 | 낮음 | ✅ 초기 비용 최소화, 향후 Bridge 전환 경로 확보 |

**Pool의 단점 보완책:** SQLAlchemy Session Event로 `WHERE organization_id = :tenant_id` 자동 주입. 개발자가 실수로 조건을 빠뜨려도 데이터 누출 없음.

## 결정 8 — 도메인 계층 구조

```
Organization (테넌트 = 회사)
  └── Workspace (프로젝트/팀 단위 공간)
        └── Member (Workspace 접근 사용자)
              └── User (실제 사람)
Subscription (결제/플랜 — Organization 단위)
```

**왜 Workspace를 분리하는가?** 하나의 회사 안에서 팀·프로젝트별로 데이터를 분리해야 하는 요구가 거의 항상 발생한다. 나중에 추가하면 DB 마이그레이션 비용이 크다.

## 결정 9 — 구독 플랜 구성

| 항목 | Free | Starter | Pro | Enterprise |
|------|------|---------|-----|------------|
| 가격 | 무료 | $29/월 | $99/월 | 협의 |
| 멤버 수 | 3명 | 10명 | 50명 | 무제한 |
| Agent 실행/월 | 10회 | 100회 | 1,000회 | 무제한 |
| API 접근 | ❌ | ❌ | ✅ | ✅ |
| SSO/SAML | ❌ | ❌ | ❌ | ✅ |

---

# 04 Data Governance

## 결정 10 — 데이터 등급 분류

| 등급 | 예시 | 처리 |
|------|------|------|
| Public | 공개 문서, 마케팅 | 일반 저장 |
| Internal | 업무 데이터, 프로젝트 | 테넌트 격리 |
| Confidential | 계약서, 인사 정보 | 암호화 저장 |
| PII | 이메일, 전화번호 | 마스킹 + 암호화 |
| Restricted | API 키, 비밀번호 | AES-256 + AWS KMS |

## 결정 11 — 데이터 보존 정책

| 데이터 | 보존 기간 | 이유 |
|--------|----------|------|
| 사용자 계정 | 탈퇴 후 30일 Soft Delete → Hard Delete | 개인정보보호법 |
| 감사 로그 | 3년 | SOC2, ISO27001 |
| 결제 기록 | 5년 | 세법 |
| AI 대화 기록 | 1년 (테넌트 설정 가능) | 내부 정책 |
| 세션 로그 | 90일 | 내부 정책 |

## 결정 12 — Soft Delete 전략

**결정: 모든 중요 데이터는 Soft Delete (`deleted_at` 컬럼)**

**왜?** Hard Delete는 복구 불가. 실수·법적 분쟁·감사 시 데이터가 필요한 경우가 반드시 생긴다. 30일 후 스케줄러로 Hard Delete 실행하여 스토리지 낭비도 방지.

---

# 05 Application Architecture

## 결정 13 — 서비스 아키텍처

**결정: Modular Monolith → 필요 시 Microservice 분리**

**왜 Monolith 먼저인가?**

| 아키텍처 | 장점 | 단점 | 적합 시점 |
|----------|------|------|-----------|
| Monolith | 개발 속도 빠름, 디버깅 쉬움 | 팀 규모 커지면 병목 | 팀 10명 이하, 초기 제품 |
| Modular Monolith ✅ | 빠른 개발 + 미래 분리 경로 확보 | 모듈 경계 규율 필요 | 팀 5~20명 |
| Microservice | 독립 배포, 기술 다양성 | 운영 복잡도 폭발적 증가 | 팀 20명 이상, 도메인 안정화 후 |

**Modular Monolith 규칙:** 도메인 간 직접 `import` 금지. 서비스 레이어 또는 내부 이벤트 버스를 통해서만 통신.

## 결정 14 — 레이어드 아키텍처

```
Router     → HTTP 요청/응답 처리. 비즈니스 로직 금지
Schema     → 데이터 직렬화/역직렬화. 로직 금지
Service    → 비즈니스 로직 전담. DB 직접 접근 금지
Repository → DB 쿼리 전담. 비즈니스 로직 금지
Model      → DB 스키마 정의. 로직 금지
```

**왜 레이어를 엄격하게 나누는가?** 각 레이어의 책임이 섞이면 테스트가 불가능해지고, 도메인 분리 시 경계가 모호해진다.

## 결정 15 — 이벤트 처리 전략

**현재:** 내부 이벤트 버스 (메모리 기반, 동일 프로세스)  
**이후:** Kafka 또는 AWS SQS (서비스 분리 시)

**왜 내부 이벤트 버스를 먼저?** 도메인 간 결합을 줄이면서 Kafka 없이 시작할 수 있다. 인터페이스를 동일하게 유지하면 나중에 Kafka로 교체해도 비즈니스 로직 변경이 없다.

---

# 06 Integration & API

## 결정 16 — API 설계 원칙

```
리소스는 복수 명사          /agents, /organizations
HTTP 메서드로 행위 구분     GET(조회) POST(생성) PATCH(수정) DELETE(삭제)
계층 구조는 중첩            /organizations/{id}/members
버전 접두사                 /api/v1/
필터/정렬은 쿼리 파라미터   ?status=active&sort=-created_at
```

**버전 관리 정책:**
- Breaking Change(필드 제거, 타입 변경)가 있을 때만 v2로 올린다
- 구버전은 Deprecated 공지 후 6개월 유지, Sunset-Date 헤더로 명시

## 결정 17 — 표준 응답 포맷

```json
// 성공 (단건)
{ "success": true, "data": {...}, "meta": { "request_id": "..." } }

// 성공 (목록)
{ "success": true, "data": { "items": [...], "total": 100, "page": 1, "size": 20, "total_pages": 5 } }

// 실패
{ "success": false, "error": { "code": "ERR_AUTH_002", "message": "...", "request_id": "..." } }
```

**왜 통일된 응답 포맷?** Frontend에서 응답 처리 로직을 단일화할 수 있고, 에러 코드 기반으로 다국어 메시지를 매핑할 수 있다.

---

# 07 Observability & Operations

## 결정 18 — 구조화 로그

**결정: JSON 구조화 로그 (structlog) + trace_id 포함**

**왜 JSON 로그?** 텍스트 로그는 검색·필터·집계가 어렵다. JSON이면 CloudWatch Logs Insights나 Grafana Loki에서 즉시 쿼리 가능하다.

**모든 로그에 포함되는 필드:**
```
timestamp, level, logger, message,
trace_id, org_id, user_id, request_id
```

**로그에서 반드시 제외할 필드:** `password`, `token`, `api_key`, `secret`, `card_number`

## 결정 19 — 핵심 모니터링 임계값

| 메트릭 | 임계값 | 초과 시 액션 |
|--------|--------|-------------|
| API 에러율 | > 1% 경고 / > 5% 즉시 대응 | Slack → PagerDuty |
| API P99 응답시간 | > 2초 경고 / > 5초 즉시 대응 | Slack → PagerDuty |
| Agent 실행 성공률 | < 95% | Slack #alerts |
| DB 연결 풀 사용률 | > 80% | Slack #alerts |
| CPU / 메모리 | > 80% | Slack #alerts |

---

# 08 Governance & Standards

## 결정 20 — CI/CD 파이프라인 전략

```
PR 생성 시:
  Backend  → ruff + mypy + pytest (unit + integration)
  Frontend → eslint + tsc --noEmit + jest
  공통     → Docker 이미지 빌드 검증

main 머지 시:
  Docker 이미지 빌드 & ECR 푸시
  Dev 환경 자동 배포
  E2E 테스트 (Playwright)

릴리즈 태그 생성 시:
  Staging 자동 배포 → Slack 알림 → 수동 승인 → Production Blue-Green 배포
```

## 결정 21 — 배포 전략

| 전략 | 적용 환경 | 이유 |
|------|-----------|------|
| Rolling Update | Dev | 빠른 배포, 약간의 다운타임 허용 가능 |
| Blue-Green | Production | 무중단 + 즉시 롤백 가능 |
| Canary | 대규모 기능 출시 | 5% → 25% → 100% 점진적 트래픽 이동 |
| Feature Flag | 기능 단위 | 코드 배포 없이 기능 on/off |

## 결정 22 — 보안 정책

| 영역 | 결정 | 이유 |
|------|------|------|
| 전송 암호화 | TLS 1.3 강제 | 중간자 공격 방어 |
| 저장 암호화 | AES-256 + AWS KMS | 민감 데이터 유출 시 복호화 불가 |
| 비밀번호 | bcrypt cost=12 | 무차별 대입 공격 방어 |
| Rate Limiting | IP 100 req/min / API Token 1,000 req/min | DoS 방어 |
| 로그인 실패 제한 | 5회 / 15분 잠금 | Brute-force 방어 |
| 취약점 스캔 | GitHub Dependabot + Snyk CI 통합 | 의존성 취약점 자동 감지 |

---

# 09 Localization & Globalization

## 결정 23 — 다국어 지원 전략

**지원 언어:** 한국어(기본) → 영어 → 일본어(예정)  
**도구:** next-intl (Frontend) / Babel (Backend)

**왜 처음부터 i18n 구조를 만드는가?** 나중에 추가하면 모든 UI 문자열을 한 번에 바꿔야 한다. 처음에 구조만 잡아두면 번역 파일 추가만으로 언어를 확장할 수 있다.

## 결정 24 — 시간대 전략

```
원칙: DB 저장 = UTC (TIMESTAMPTZ)
      API 응답 = ISO 8601 UTC ("2026-03-01T12:00:00Z")
      UI 표시 = 사용자 timezone 설정으로 변환 (dayjs + timezone)

왜 UTC로만 저장? → 다국가 서비스 시 시간대 변환 버그의 원천 차단
```

## 결정 25 — 금액 저장 전략

```
원칙: 정수(최소 단위)로 저장
  $10.00  → 1000 (cents)
  ₩10,000 → 10000 (won)

왜 정수? → 부동소수점 반올림 오차로 결제 금액이 틀어지는 버그 방지
```

---

# 10 AI Agent Architecture

## 결정 26 — Agent 실행 아키텍처

**결정: LangGraph 기반 상태 그래프 워크플로우**

**왜 LangGraph인가?**

| 프레임워크 | 특징 | 탈락 이유 |
|-----------|------|-----------|
| LangChain Agents | 단순 ReAct Loop | 복잡한 멀티에이전트 흐름 표현 어려움 |
| **LangGraph ✅** | 상태 기반 그래프, 조건부 분기 | — |
| AutoGen | 대화형 멀티에이전트 | 워크플로우 제어가 어려움 |
| CrewAI | 역할 기반 에이전트 팀 | 커스터마이징 제약 |

## 결정 27 — Agent 유형 분류

| 유형 | 코드 | 역할 | 최소 플랜 |
|------|------|------|-----------|
| 범용 대화 | `general` | 일반 질의응답 | pro |
| 데이터 분석 | `analyst` | 데이터 분석·시각화 | pro |
| 리서치 | `researcher` | 웹 검색·정보 수집 | pro |
| 코드 | `coder` | 코드 생성·리뷰 | pro |
| 워크플로우 | `workflow` | 멀티에이전트 오케스트레이션 | enterprise |
| 도메인 특화 | `custom` | 고객 정의 Agent | enterprise |

## 결정 28 — Agent Memory 전략

| 메모리 유형 | 저장 위치 | 범위 | TTL |
|------------|----------|------|-----|
| 단기 (대화 컨텍스트) | Redis | 현재 세션 | 세션 종료 |
| 중기 (대화 요약) | PostgreSQL | 이전 대화 요약 | 90일 |
| 장기 (지식 베이스) | pgvector | 영구 지식 | 영구 (명시적 삭제) |
| 작업 (실행 중 상태) | Redis | Agent 실행 중 | 실행 종료 |

**왜 pgvector를 먼저 쓰고 Qdrant를 나중에?** 초기에는 PostgreSQL 안에서 벡터 검색을 처리해 인프라를 단순하게 유지한다. 임베딩 규모가 수천만 건을 넘으면 전문 벡터 DB로 전환한다.

## 결정 29 — AI 안전성 (Guardrail) 전략

**3중 Guardrail 구조:**

```
입력 단계 (Input Guardrail)
  → 최대 토큰 길이 제한 (50,000자)
  → OpenAI Moderation API (유해 콘텐츠 필터)
  → 프롬프트 인젝션 패턴 감지
  → PII 자동 마스킹

실행 단계 (Execution Guardrail)
  → max_iterations 제한 (기본 10회)
  → 타임아웃 강제 (기본 120초)
  → 허용된 Tool 목록만 실행
  → 외부 접근 URL 화이트리스트

출력 단계 (Output Guardrail)
  → 유해 콘텐츠 재검증
  → PII 마스킹
  → 환각 신뢰도 체크
```

---

# Architecture Decision Record (ADR)

설계를 변경할 때마다 이 목록에 추가하고 이유를 기록한다.

| # | 결정 사항 | 상태 | 결정 이유 요약 | 재검토 조건 |
|---|-----------|------|--------------|-------------|
| 001 | Backend: FastAPI | ✅ 확정 | async + AI 생태계 + 자동 문서 | 팀 기술 스택 전환 시 |
| 002 | DB: PostgreSQL + pgvector | ✅ 확정 | ACID + 벡터 검색 단일 DB | 임베딩 수천만 건 초과 시 |
| 003 | 인증: JWT Rotate | ✅ 확정 | Stateless + 탈취 감지 가능 | — |
| 004 | 멀티테넌시: Pool 방식 | ✅ 확정 | 초기 비용 최소화 | 테넌트 10,000개 초과 시 Bridge 검토 |
| 005 | 아키텍처: Modular Monolith | ✅ 확정 | 개발 속도 + 분리 경로 확보 | 팀 20명 초과 or 도메인 안정화 후 |
| 006 | AI: LangChain + LangGraph | ✅ 확정 | 상태 기반 워크플로우 표준 | 더 나은 Agent 프레임워크 등장 시 |
| 007 | Vector DB: pgvector → Qdrant | 📋 계획 | 초기 단순화 | 임베딩 규모 확대 시 |
| 008 | 이벤트: 내부 버스 → Kafka | 📋 계획 | 초기 단순화 | 서비스 분리 시 |
| 009 | 상태관리: React Query + Zustand | ✅ 확정 | 서버 상태 / 클라이언트 상태 분리 | — |
| 010 | 배포: Docker → ECS → K8s | 📋 계획 | 단계별 인프라 확장 | 월 트래픽 1M 초과 시 |

---

> 📗 **다음 단계:** Implementation Guide에서 이 결정들을 코드로 구현하는 방법과 순서를 확인하세요.
> 📙 **즉시 참조:** 개발 중 Naming Rule, 에러 코드, API 패턴은 Quick Reference Card를 확인하세요.
