# AI Agent SaaS — Implementation Guide
### 📗 문서 2 of 3 — 구현 가이드 (How to Build)

> **목적:** Framework에서 결정된 내용을 코드로 구현하는 순서, 파일 구조, 핵심 코드를 제공한다.  
> **독자:** 실제 코드를 작성하는 개발자  
> **버전:** v1.0 | **작성일:** 2026년 3월

> ⚠️ **선행 조건:** 📘 Framework 문서를 먼저 읽고 설계 결정 내용을 이해한 후 이 문서를 따라 구현한다.

---

## 전체 구현 흐름

```
Phase 1 — 인프라 기반 (Docker Compose, 환경 설정)
     ↓
Phase 2 — Backend 공통 기반 (FastAPI Core)
     ↓
Phase 3 — 인증·테넌트 도메인 (Auth, Organization)
     ↓
Phase 4 — Frontend 공통 기반 (Next.js)
     ↓
Phase 5 — AI Agent 도메인
     ↓
Phase 6 — 통합 검증 및 CI/CD
```

> 각 Phase는 순서를 지켜야 한다. Phase 내 Step도 의존성 순서를 반드시 따른다.

---

## 전체 디렉토리 구조

```
project-root/
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   └── app/
│       ├── main.py
│       ├── core/
│       │   ├── config.py          설정 관리
│       │   ├── logging.py         구조화 로그
│       │   ├── security.py        JWT + 비밀번호 해시
│       │   ├── cache.py           Redis 클라이언트
│       │   ├── exceptions.py      커스텀 예외
│       │   ├── feature_flags.py   Feature Flag 평가
│       │   └── audit.py           감사 로그 자동화
│       ├── db/
│       │   ├── base.py            DeclarativeBase
│       │   ├── session.py         async engine + get_db
│       │   └── migrations/        Alembic 마이그레이션
│       ├── models/
│       │   └── base.py            BaseModel + TenantModel + SoftDeleteMixin
│       ├── schemas/
│       │   └── base.py            ApiResponse + PaginatedResponse
│       ├── utils/
│       │   ├── datetime.py
│       │   ├── pagination.py
│       │   ├── security.py
│       │   ├── validators.py
│       │   └── formatters.py
│       ├── domains/
│       │   ├── auth/              router · service · repository · models · schemas
│       │   ├── users/
│       │   ├── organizations/
│       │   ├── billing/
│       │   ├── agents/
│       │   └── notifications/
│       └── api/
│           ├── deps.py            공통 Depends (인증, 테넌트)
│           └── v1/                라우터 모음
├── frontend/
│   └── src/
│       ├── app/                   Next.js App Router
│       ├── components/
│       │   ├── ui/                공통 컴포넌트
│       │   └── agents/            AI Agent UI
│       ├── lib/
│       │   ├── axios.ts
│       │   └── queryClient.ts
│       ├── hooks/
│       ├── stores/                Zustand
│       ├── types/
│       └── utils/
├── docker-compose.yml
├── .env.example
└── Makefile
```

---

# Phase 1 — 인프라 기반

## Step 1-1. docker-compose.yml

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s

  backend:
    build: ./backend
    env_file: .env
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_healthy }
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app   # 개발 시 핫 리로드

  frontend:
    build: ./frontend
    env_file: .env
    depends_on:
      - backend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app

volumes:
  postgres_data:
```

## Step 1-2. .env.example

```bash
# ── 앱 ──────────────────────────────────
ENVIRONMENT=local
DEBUG=true
SECRET_KEY=your-secret-key-min-32-chars

# ── Database ─────────────────────────────
POSTGRES_DB=saas_db
POSTGRES_USER=saas_user
POSTGRES_PASSWORD=saas_password
DATABASE_URL=postgresql+asyncpg://saas_user:saas_password@db:5432/saas_db

# ── Redis ────────────────────────────────
REDIS_URL=redis://redis:6379/0

# ── AI ───────────────────────────────────
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
AGENT_MAX_ITERATIONS=10
AGENT_TIMEOUT_SECONDS=120

# ── 스토리지 ─────────────────────────────
AWS_S3_BUCKET=
AWS_REGION=ap-northeast-2

# ── 결제 ─────────────────────────────────
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# ── Frontend ─────────────────────────────
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Step 1-3. Makefile

```makefile
.PHONY: up down logs shell-be shell-db migrate seed test lint

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

shell-be:
	docker compose exec backend bash

shell-db:
	docker compose exec db psql -U saas_user -d saas_db

migrate:
	docker compose exec backend alembic upgrade head

seed:
	docker compose exec backend python scripts/seed.py

test-be:
	docker compose exec backend pytest tests/ -v

test-fe:
	docker compose exec frontend npm run test

lint-be:
	docker compose exec backend ruff check . && mypy app/

lint-fe:
	docker compose exec frontend npm run lint
```

**검증:** `make up` → 모든 컨테이너 `healthy` 상태 확인

---

# Phase 2 — Backend 공통 기반

> 이 Phase의 파일들은 모든 도메인이 의존하는 기반이다. 반드시 Phase 3보다 먼저 완성해야 한다.

## Step 2-1. core/config.py

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache
from typing import Literal

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # 환경
    environment: Literal["local", "dev", "staging", "prod"] = "local"
    debug: bool = False

    # 앱
    app_name: str = "AI SaaS"
    app_version: str = "1.0.0"
    secret_key: str
    cors_origins: list[str] = ["http://localhost:3000"]

    # DB
    database_url: str
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    # AI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    agent_max_iterations: int = 10
    agent_timeout_seconds: int = 120

    # 스토리지
    aws_s3_bucket: str = ""
    aws_region: str = "ap-northeast-2"

    # 결제
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    @field_validator("secret_key")
    def secret_key_must_be_long(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    @property
    def is_production(self) -> bool:
        return self.environment == "prod"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

## Step 2-2. db/base.py

`models/base.py`가 import하므로 반드시 먼저 작성한다.

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

> ⚠️ `Base`는 모든 ORM 모델이 상속하는 루트 클래스다. `models/base.py`에 직접 넣지 않고 별도 파일로 분리하는 이유는 Alembic이 마이그레이션 자동 감지를 위해 `Base.metadata`를 독립적으로 import해야 하기 때문이다. 순환 참조를 방지하는 핵심 분리점이다.

## Step 2-3. core/logging.py

```python
import logging
import sys
import structlog

def setup_logging(debug: bool = False) -> None:
    log_level = logging.DEBUG if debug else logging.INFO

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            # 민감 정보 자동 마스킹
            _mask_sensitive_fields,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )

# 로그에서 반드시 제외할 필드 (Framework 결정 18번)
_SENSITIVE_KEYS = {"password", "token", "api_key", "secret", "card_number", "authorization"}

def _mask_sensitive_fields(logger, method, event_dict: dict) -> dict:
    for key in list(event_dict.keys()):
        if key.lower() in _SENSITIVE_KEYS:
            event_dict[key] = "***MASKED***"
    return event_dict

def get_logger(name: str):
    return structlog.get_logger(name)
```

## Step 2-4. models/base.py

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from datetime import datetime, timezone
import uuid

class Base(DeclarativeBase):
    pass

class BaseModel(Base):
    """모든 모델의 기본 클래스"""
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

class SoftDeleteMixin:
    """Soft Delete 믹스인 — 삭제 시 deleted_at 설정"""
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    deleted_by: Mapped[uuid.UUID | None] = mapped_column(nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

class TenantModel(BaseModel, SoftDeleteMixin):
    """멀티테넌시 기반 도메인 모델의 기본 클래스"""
    __abstract__ = True

    organization_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False, index=True
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
```

## Step 2-5. db/session.py

```python
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession, async_sessionmaker
)
from contextvars import ContextVar
from uuid import UUID
from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    echo=settings.db_echo,
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# 현재 요청의 테넌트 ID를 저장하는 컨텍스트 변수
current_tenant_id: ContextVar[UUID | None] = ContextVar(
    "current_tenant_id", default=None
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

## Step 2-6. Alembic 초기화

> ⚠️ 이 Step은 **최초 1회만** 실행한다. 이미 `migrations/` 폴더가 있으면 건너뛴다.

```bash
# backend 컨테이너 안에서 실행
cd /app
alembic init app/db/migrations
```

`alembic.ini` 수정 — `sqlalchemy.url`을 비워두고 `env.py`에서 동적 주입:

```ini
# alembic.ini
[alembic]
script_location = app/db/migrations
# sqlalchemy.url 은 env.py에서 settings에서 읽어오므로 여기선 비워둠
sqlalchemy.url =
```

`app/db/migrations/env.py` 핵심 수정:

```python
from app.core.config import settings
from app.db.base import Base
# 모든 모델을 여기서 import해야 Alembic이 변경사항을 자동 감지한다
from app.domains.users.models import User          # noqa
from app.domains.organizations.models import Organization  # noqa
# ... 이후 도메인 모델 추가 시 이곳에 계속 추가

config.set_main_option("sqlalchemy.url", settings.database_url.replace("+asyncpg", ""))

target_metadata = Base.metadata
```

> ⚠️ `env.py`에서 모델 import를 빠뜨리면 해당 테이블이 마이그레이션에 포함되지 않는다. 새 도메인 모델을 추가할 때마다 이 파일에 import를 추가해야 한다.

## Step 2-7. schemas/base.py

```python
from pydantic import BaseModel
from typing import Generic, TypeVar
from datetime import datetime

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    """단건 응답 표준 포맷"""
    success: bool = True
    data: T | None = None

class PaginatedResponse(BaseModel, Generic[T]):
    """목록 응답 표준 포맷"""
    success: bool = True
    data: PaginatedData[T]

class PaginatedData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    total_pages: int

class ErrorResponse(BaseModel):
    """에러 응답 표준 포맷"""
    success: bool = False
    error: ErrorDetail

class ErrorDetail(BaseModel):
    code: str
    message: str
    detail: str | None = None
    request_id: str | None = None
    timestamp: datetime = datetime.utcnow()
```

## Step 2-8. core/exceptions.py

```python
from fastapi import HTTPException

class AppException(HTTPException):
    def __init__(self, code: str, status: int, message: str):
        super().__init__(status_code=status, detail={"code": code, "message": message})

# 에러 코드 체계: ERR_{DOMAIN}_{3자리}
class UnauthorizedException(AppException):
    def __init__(self, code="ERR_AUTH_001", msg="인증이 필요합니다."):
        super().__init__(code, 401, msg)

class TokenExpiredException(AppException):
    def __init__(self):
        super().__init__("ERR_AUTH_002", 401, "인증 토큰이 만료되었습니다.")

class ForbiddenException(AppException):
    def __init__(self, code="ERR_AUTH_004", msg="권한이 없습니다."):
        super().__init__(code, 403, msg)

class NotFoundException(AppException):
    def __init__(self, resource="리소스"):
        super().__init__("ERR_DATA_001", 404, f"{resource}를 찾을 수 없습니다.")

class PlanLimitException(AppException):
    def __init__(self, feature: str):
        super().__init__("ERR_AUTH_005", 403,
            f"현재 플랜에서는 '{feature}' 기능을 사용할 수 없습니다. 플랜을 업그레이드해 주세요.")

class AgentGuardrailException(AppException):
    def __init__(self, reason: str):
        super().__init__("ERR_AGENT_003", 422,
            f"Agent 안전 정책에 의해 차단되었습니다: {reason}")

class AgentTimeoutException(AppException):
    def __init__(self):
        super().__init__("ERR_AGENT_002", 503, "Agent 실행 시간이 초과되었습니다.")
```

## Step 2-9. core/security.py

```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timezone, timedelta
from uuid import UUID
import secrets
import hashlib
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(user_id: UUID, org_id: UUID, role: str, plan: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": str(user_id), "org_id": str(org_id),
         "role": role, "plan": plan,
         "jti": secrets.token_urlsafe(16),
         "exp": expire, "type": "access"},
        settings.secret_key, algorithm=settings.jwt_algorithm
    )

def create_refresh_token(user_id: UUID) -> tuple[str, str]:
    """Refresh Token 생성. (token, jti) 반환"""
    jti = secrets.token_urlsafe(16)
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    token = jwt.encode(
        {"sub": str(user_id), "jti": jti,
         "exp": expire, "type": "refresh"},
        settings.secret_key, algorithm=settings.jwt_algorithm
    )
    return token, jti

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])

def hash_api_token(token: str) -> str:
    """API Token을 SHA-256으로 해시 (DB 저장용)"""
    return hashlib.sha256(token.encode()).hexdigest()
```

## Step 2-10. core/cache.py

`AuthService`가 이 파일을 import하므로 `deps.py`보다 먼저 작성한다.

```python
import redis.asyncio as redis
import json
from app.core.config import settings
from typing import Any

# 싱글톤 패턴 — 앱 시작 시 1회만 생성, 재사용
_redis_client: redis.Redis | None = None

async def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client

# 편의 래퍼 — 직렬화/역직렬화 자동 처리
async def cache_get(key: str) -> Any | None:
    r = await get_redis()
    value = await r.get(key)
    return json.loads(value) if value else None

async def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    r = await get_redis()
    await r.setex(key, ttl, json.dumps(value, default=str))

async def cache_delete(key: str) -> None:
    r = await get_redis()
    await r.delete(key)

# Redis 인스턴스 직접 접근 (setex, incr 등 직접 호출 시)
async def get_redis_client() -> redis.Redis:
    return await get_redis()

# FastAPI lifespan에서 종료 시 호출
async def close_redis() -> None:
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None
```

> 캐시 키 네이밍 규칙: `{namespace}:{entity}:{id}` 형태로 통일한다.
> 예: `login_attempts:user@email.com` / `refresh_token:{user_id}:{jti}` / `feature_flag:{org_id}:{flag_key}`

## Step 2-11. utils/datetime.py

```python
from datetime import datetime, timezone
import zoneinfo

KST = zoneinfo.ZoneInfo("Asia/Seoul")

def now_utc() -> datetime:
    """현재 시각 (UTC, timezone-aware)"""
    return datetime.now(timezone.utc)

def to_kst(dt: datetime) -> datetime:
    """UTC datetime을 KST로 변환"""
    return dt.astimezone(KST)

def format_kst(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    return to_kst(dt).strftime(fmt)
```

## Step 2-12. utils/pagination.py

```python
from dataclasses import dataclass
from sqlalchemy import Select, func
from sqlalchemy.ext.asyncio import AsyncSession

@dataclass
class PaginationParams:
    page: int = 1
    size: int = 20

    def __post_init__(self):
        self.page = max(1, self.page)
        self.size = min(100, max(1, self.size))

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

async def paginate(
    session: AsyncSession,
    query: Select,
    params: PaginationParams,
) -> dict:
    """쿼리에 페이지네이션을 적용하고 표준 응답 dict를 반환한다."""
    from sqlalchemy import select

    # 전체 count
    count_query = select(func.count()).select_from(query.subquery())
    total = await session.scalar(count_query) or 0

    # 실제 데이터
    result = await session.scalars(
        query.offset(params.offset).limit(params.size)
    )
    items = result.all()

    return {
        "items": items,
        "total": total,
        "page": params.page,
        "size": params.size,
        "total_pages": max(1, -(-total // params.size)),  # ceil division
    }
```

## Step 2-13. api/deps.py

```python
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from dataclasses import dataclass
from uuid import UUID
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, TokenExpiredException, ForbiddenException
from app.db.session import current_tenant_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@dataclass
class TenantContext:
    user_id: UUID
    org_id: UUID
    role: str
    plan: str

async def get_tenant_context(
    token: str = Depends(oauth2_scheme)
) -> TenantContext:
    try:
        payload = decode_token(token)
    except Exception:
        raise TokenExpiredException()

    if payload.get("type") != "access":
        raise UnauthorizedException()

    ctx = TenantContext(
        user_id=UUID(payload["sub"]),
        org_id=UUID(payload["org_id"]),
        role=payload["role"],
        plan=payload["plan"],
    )
    # 테넌트 컨텍스트 주입 (자동 필터링에 사용)
    current_tenant_id.set(ctx.org_id)
    return ctx

def require_role(*allowed_roles: str):
    """역할(Role) 기반 엔드포인트 보호"""
    async def checker(ctx: TenantContext = Depends(get_tenant_context)):
        if ctx.role not in allowed_roles:
            raise ForbiddenException()
        return ctx
    return checker

def require_plan(*allowed_plans: str):
    """플랜 기반 기능 제한"""
    async def checker(ctx: TenantContext = Depends(get_tenant_context)):
        if ctx.plan not in allowed_plans:
            from app.core.exceptions import PlanLimitException
            raise PlanLimitException("이 기능")
        return ctx
    return checker
```

## Step 2-14. core/audit.py

```python
from functools import wraps
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

async def create_audit_log(
    session: AsyncSession,
    org_id: UUID,
    user_id: UUID | None,
    action: str,            # 'agent.created', 'user.deleted'
    resource_type: str,     # 'Agent', 'User'
    resource_id: UUID | None = None,
    before_data: dict | None = None,
    after_data: dict | None = None,
    severity: str = "info",
):
    from app.domains.audit.models import AuditLog
    log = AuditLog(
        organization_id=org_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        before_data=before_data,
        after_data=after_data,
        severity=severity,
        created_at=datetime.now(timezone.utc),
    )
    session.add(log)
    # 커밋은 호출자가 관리 (Service 레이어 트랜잭션 내에서 실행)
```

## Step 2-15. main.py

모든 core/db/models/schemas 파일이 준비된 후 **마지막**에 작성한다.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.cache import close_redis
from app.core.exceptions import AppException
from app.db.session import engine

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작
    setup_logging(debug=settings.debug)
    logger.info("app.startup", env=settings.environment, version=settings.app_version)
    yield
    # 종료
    await engine.dispose()
    await close_redis()
    logger.info("app.shutdown")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 예외 핸들러
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail},
    )

# 헬스체크
@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.app_version}

# 라우터 등록 (도메인 추가 시 여기에 include_router 추가)
# from app.api.v1 import router as v1_router
# app.include_router(v1_router, prefix="/api/v1")
```

**검증:**
```bash
make up
docker compose exec backend python -c "from app.core.config import settings; print(settings.app_name)"
# → AI SaaS

curl http://localhost:8000/health
# → {"status":"ok","version":"1.0.0"}

# API 문서 확인 (local/dev 환경에서만 노출)
# → http://localhost:8000/docs
```

---

# Phase 3 — 인증·테넌트 도메인

> 모든 도메인은 동일한 구조를 따른다: models → schemas → repository → service → router

## Step 3-1. 사용자 모델 (domains/users/models.py)

```python
from app.models.base import BaseModel, SoftDeleteMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Enum as SAEnum
import enum

class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"
    deleted = "deleted"

class User(BaseModel, SoftDeleteMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    password_hash: Mapped[str | None] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(nullable=True)
    locale: Mapped[str] = mapped_column(String(10), default="ko")
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Seoul")
    status: Mapped[UserStatus] = mapped_column(
        SAEnum(UserStatus), default=UserStatus.active
    )
    last_login_at: Mapped[datetime | None] = mapped_column(nullable=True)
```

## Step 3-2. 조직 모델 (domains/organizations/models.py)

```python
from app.models.base import BaseModel, SoftDeleteMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Enum as SAEnum, JSON
import enum, uuid

class OrgPlan(str, enum.Enum):
    free = "free"
    starter = "starter"
    pro = "pro"
    enterprise = "enterprise"

class OrgMemberRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    member = "member"
    viewer = "viewer"

class Organization(BaseModel, SoftDeleteMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    plan: Mapped[OrgPlan] = mapped_column(SAEnum(OrgPlan), default=OrgPlan.free)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class OrganizationMember(BaseModel):
    __tablename__ = "organization_members"

    organization_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    role: Mapped[OrgMemberRole] = mapped_column(
        SAEnum(OrgMemberRole), default=OrgMemberRole.member
    )
    invited_by: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
```

## Step 3-3. 인증 서비스 (domains/auth/service.py)

```python
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.exceptions import UnauthorizedException
from app.core.cache import redis_client

class AuthService:
    async def login(self, email: str, password: str, db) -> dict:
        # 1. 로그인 실패 횟수 확인
        attempts_key = f"login_attempts:{email}"
        attempts = await redis_client.get(attempts_key)
        if attempts and int(attempts) >= 5:
            raise UnauthorizedException(msg="너무 많은 로그인 시도. 15분 후 재시도 해주세요.")

        # 2. 사용자 조회
        user = await self.user_repo.get_by_email(email, db)
        if not user or not verify_password(password, user.password_hash):
            # 실패 횟수 증가
            await redis_client.incr(attempts_key)
            await redis_client.expire(attempts_key, 900)  # 15분
            raise UnauthorizedException(msg="이메일 또는 비밀번호가 올바르지 않습니다.")

        # 3. 조직 정보 조회
        member = await self.org_repo.get_member(user.id, db)

        # 4. 토큰 발급
        access_token = create_access_token(
            user.id, member.organization_id, member.role, member.plan
        )
        refresh_token, jti = create_refresh_token(user.id)

        # 5. Refresh Token Redis 저장
        await redis_client.setex(
            f"refresh_token:{user.id}:{jti}",
            60 * 60 * 24 * 30,  # 30일
            "valid"
        )

        # 6. 로그인 성공 시 실패 횟수 초기화
        await redis_client.delete(attempts_key)

        return {"access_token": access_token, "refresh_token": refresh_token}
```

**마이그레이션:**
```bash
alembic revision --autogenerate -m "add_users_organizations"
alembic upgrade head
```

---

# Phase 4 — Frontend 공통 기반

## Step 4-1. tsconfig.json

`@/` path alias를 설정하지 않으면 이후 모든 import가 상대경로가 되어 코드가 지저분해진다. **가장 먼저** 작성한다.

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "module": "esnext",
    "moduleResolution": "bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "paths": {
      "@/*":            ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*":        ["./src/lib/*"],
      "@/types/*":      ["./src/types/*"],
      "@/hooks/*":      ["./src/hooks/*"],
      "@/stores/*":     ["./src/stores/*"],
      "@/utils/*":      ["./src/utils/*"],
      "@/constants/*":  ["./src/constants/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

## Step 4-2. .eslintrc.json / .prettierrc

```json
// .eslintrc.json
{
  "extends": ["next/core-web-vitals", "next/typescript"],
  "rules": {
    "no-console": "warn",
    "prefer-const": "error",
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }]
  }
}
```

```json
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

## Step 4-3. next.config.ts

```typescript
import type { NextConfig } from 'next';

const config: NextConfig = {
  // 프로덕션 빌드 시 TypeScript/ESLint 오류가 있으면 빌드 실패
  typescript: { ignoreBuildErrors: false },
  eslint: { ignoreDuringBuilds: false },

  // API 프록시 (개발 환경에서 CORS 우회)
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
      },
    ];
  },
};

export default config;
```

## Step 4-4. types/api.ts · types/auth.ts

Backend의 표준 응답 포맷과 1:1로 대응한다.

```typescript
// types/api.ts
export interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  meta?: { request_id?: string; timestamp?: string };
}

export interface PaginatedData<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  total_pages: number;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: PaginatedData<T>;
}

export interface ApiError {
  code: string;        // ERR_AUTH_002
  message: string;
  detail?: string;
  request_id?: string;
}

export interface ApiErrorResponse {
  success: false;
  error: ApiError;
}
```

```typescript
// types/auth.ts
export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url: string | null;
  locale: string;
  timezone: string;
  status: 'active' | 'inactive' | 'suspended';
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  plan: 'free' | 'starter' | 'pro' | 'enterprise';
}

export interface MemberContext {
  user: User;
  organization: Organization;
  role: 'owner' | 'admin' | 'member' | 'viewer';
}
```

## Step 4-5. constants/api.ts

```typescript
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? '';

export const ENDPOINTS = {
  auth: {
    login:    '/api/v1/auth/login',
    refresh:  '/api/v1/auth/refresh',
    logout:   '/api/v1/auth/logout',
    register: '/api/v1/auth/register',
  },
  users: {
    me:     '/api/v1/users/me',
    update: '/api/v1/users/me',
  },
  organizations: {
    list:    '/api/v1/organizations',
    detail:  (id: string) => `/api/v1/organizations/${id}`,
    members: (id: string) => `/api/v1/organizations/${id}/members`,
  },
  agents: {
    list:   '/api/v1/agents',
    detail: (id: string) => `/api/v1/agents/${id}`,
    run:    (id: string) => `/api/v1/agents/${id}/run`,
    stream: (id: string) => `/api/v1/agents/${id}/run/stream`,
  },
} as const;
```

## Step 4-6. lib/axios.ts

```typescript
import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/stores/authStore';

const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true,   // HttpOnly Cookie (Refresh Token) 포함
  timeout: 30000,
});

// 요청 인터셉터: Access Token 자동 첨부
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// 응답 인터셉터: 401 시 토큰 재발급 후 재시도
let isRefreshing = false;
let failedQueue: Array<{ resolve: Function; reject: Function }> = [];

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          original.headers.Authorization = `Bearer ${token}`;
          return apiClient(original);
        });
      }
      original._retry = true;
      isRefreshing = true;
      try {
        const { data } = await axios.post(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/refresh`,
          {}, { withCredentials: true }
        );
        const newToken = data.data.access_token;
        useAuthStore.getState().setAccessToken(newToken);
        failedQueue.forEach(({ resolve }) => resolve(newToken));
        original.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(original);
      } catch {
        failedQueue.forEach(({ reject }) => reject(error));
        useAuthStore.getState().logout();
        window.location.href = '/login';
      } finally {
        isRefreshing = false;
        failedQueue = [];
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

## Step 4-7. stores/authStore.ts

```typescript
import { create } from 'zustand';

interface AuthState {
  accessToken: string | null;
  user: User | null;
  setAccessToken: (token: string) => void;
  setUser: (user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  setAccessToken: (token) => set({ accessToken: token }),
  setUser: (user) => set({ user }),
  logout: () => set({ accessToken: null, user: null }),
}));
```

## Step 4-8. lib/queryClient.ts

```typescript
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime:          1000 * 60 * 5,   // 5분간 fresh 상태 유지
      gcTime:             1000 * 60 * 10,  // 10분 후 캐시 제거
      retry:              1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
});
```

## Step 4-9. hooks/useAuth.ts · hooks/usePagination.ts

```typescript
// hooks/useAuth.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/axios';
import { useAuthStore } from '@/stores/authStore';
import { ENDPOINTS } from '@/constants/api';
import type { MemberContext } from '@/types/auth';

export function useMe() {
  return useQuery({
    queryKey: ['users', 'me'],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: MemberContext }>(ENDPOINTS.users.me);
      return data.data;
    },
    enabled: !!useAuthStore.getState().accessToken,
  });
}

export function useLogout() {
  const qc = useQueryClient();
  const { logout } = useAuthStore();
  return useMutation({
    mutationFn: () => apiClient.post(ENDPOINTS.auth.logout),
    onSettled: () => {
      logout();
      qc.clear();
      window.location.href = '/login';
    },
  });
}
```

```typescript
// hooks/usePagination.ts
import { useState } from 'react';

export function usePagination(initialPage = 1, initialSize = 20) {
  const [page, setPage] = useState(initialPage);
  const [size, setSize] = useState(initialSize);

  const goToPage = (newPage: number) => setPage(Math.max(1, newPage));
  const reset = () => setPage(1);

  return { page, size, setPage: goToPage, setSize, reset };
}
```

## Step 4-10. 공통 컴포넌트

```tsx
// components/common/LoadingSpinner.tsx
export function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const cls = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-12 h-12' }[size];
  return (
    <div className={`animate-spin rounded-full border-2 border-primary-600
                     border-t-transparent ${cls}`} />
  );
}
```

```tsx
// components/common/ErrorBoundary.tsx
'use client';
import { Component, type ReactNode } from 'react';

interface Props { children: ReactNode; fallback?: ReactNode }
interface State { hasError: boolean; error?: Error }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? (
        <div className="p-8 text-center text-red-600">
          <p className="font-semibold">오류가 발생했습니다.</p>
          <p className="text-sm mt-2">{this.state.error?.message}</p>
        </div>
      );
    }
    return this.props.children;
  }
}
```

| 컴포넌트 | 경로 | 핵심 Props | 구현 방식 |
|----------|------|-----------|-----------|
| Button | `ui/Button.tsx` | variant, size, loading, disabled | shadcn/ui 기반 |
| Input | `ui/Input.tsx` | label, error, helpText | shadcn/ui 기반 |
| Modal | `ui/Modal.tsx` | isOpen, onClose, title, size | Radix Dialog 래핑 |
| Toast | `ui/Toast.tsx` | type, message, duration | Radix Toast 래핑 |
| Table | `ui/Table.tsx` | columns, data, loading | TanStack Table |
| Skeleton | `ui/Skeleton.tsx` | className | 로딩 플레이스홀더 |
| LoadingSpinner | `common/LoadingSpinner.tsx` | size | 위 코드 참고 |
| ErrorBoundary | `common/ErrorBoundary.tsx` | fallback | 위 코드 참고 |
| AgentChat | `agents/AgentChat.tsx` | agentId, sessionId | SSE 스트리밍 |
| AgentStatus | `agents/AgentStatus.tsx` | runId | 실행 상태 표시 |

## Step 4-11. app/providers.tsx · app/layout.tsx

```tsx
// app/providers.tsx
'use client';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from '@/lib/queryClient';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        {children}
        {process.env.NODE_ENV === 'development' && (
          <ReactQueryDevtools initialIsOpen={false} />
        )}
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
```

```tsx
// app/layout.tsx
import type { Metadata } from 'next';
import { Providers } from './providers';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI SaaS',
  description: 'AI Agent SaaS Platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

## Step 4-12. tailwind.config.ts

```typescript
export default {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50:  '#EFF6FF',
          500: '#3B82F6',
          600: '#2563EB',   // 기본 버튼
          700: '#1D4ED8',   // Hover
        },
        agent: {
          bg:     '#F0F9FF',
          border: '#BAE6FD',
          text:   '#0369A1',
        },
      },
      fontFamily: {
        sans: ['Pretendard', 'Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
}
```

---

# Phase 5 — AI Agent 도메인

## Step 5-1. Agent 모델 (domains/agents/models.py)

```python
from app.models.base import TenantModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, JSON, Integer, Float, Boolean, Enum as SAEnum
import enum

class AgentType(str, enum.Enum):
    general = "general"
    analyst = "analyst"
    researcher = "researcher"
    coder = "coder"
    workflow = "workflow"
    custom = "custom"

class AgentRunStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"
    canceled = "canceled"

class Agent(TenantModel):
    __tablename__ = "agents"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    agent_type: Mapped[AgentType] = mapped_column(SAEnum(AgentType))
    model: Mapped[str] = mapped_column(String(100), default="gpt-4o")
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    tools: Mapped[list] = mapped_column(JSON, default=list)
    memory_config: Mapped[dict] = mapped_column(JSON, default=dict)
    max_iterations: Mapped[int] = mapped_column(Integer, default=10)
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class AgentRun(TenantModel):
    __tablename__ = "agent_runs"

    agent_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    input: Mapped[str] = mapped_column(Text, nullable=False)
    output: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[AgentRunStatus] = mapped_column(
        SAEnum(AgentRunStatus), default=AgentRunStatus.queued
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    steps: Mapped[list] = mapped_column(JSON, default=list)
    tokens_input: Mapped[int] = mapped_column(Integer, default=0)
    tokens_output: Mapped[int] = mapped_column(Integer, default=0)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
```

## Step 5-2. Agent 실행 서비스 (domains/agents/service.py)

```python
from langgraph.graph import StateGraph, END
from app.core.exceptions import PlanLimitException, AgentTimeoutException, AgentGuardrailException
import asyncio

class AgentService:
    async def run_agent(
        self,
        agent_id: UUID,
        input_text: str,
        ctx: TenantContext,
        session: AsyncSession
    ) -> AgentRun:
        # 1. Feature Flag 확인
        if not await is_feature_enabled("ai_agent_enabled", ctx.org_id, ctx.plan):
            raise PlanLimitException("AI Agent")

        # 2. Input Guardrail
        await self.guardrail.validate_input(input_text)

        # 3. Agent 조회
        agent = await self.repo.get(agent_id, ctx.org_id, session)
        if not agent:
            raise NotFoundException("Agent")

        # 4. Run 레코드 생성
        run = AgentRun(
            organization_id=ctx.org_id,
            agent_id=agent_id,
            user_id=ctx.user_id,
            input=input_text,
            status=AgentRunStatus.running,
            started_at=now_utc(),
        )
        session.add(run)
        await session.flush()

        # 5. 실행 (타임아웃 포함)
        try:
            result = await asyncio.wait_for(
                self._execute(agent, input_text, ctx),
                timeout=settings.agent_timeout_seconds
            )
        except asyncio.TimeoutError:
            run.status = AgentRunStatus.failed
            run.error_message = "실행 시간 초과"
            await session.commit()
            raise AgentTimeoutException()

        # 6. Output Guardrail
        output = await self.guardrail.validate_output(result.output)

        # 7. Run 업데이트
        run.status = AgentRunStatus.completed
        run.output = output
        run.tokens_input = result.usage.input_tokens
        run.tokens_output = result.usage.output_tokens
        run.duration_ms = int((now_utc() - run.started_at).total_seconds() * 1000)
        run.completed_at = now_utc()
        await session.commit()

        # 8. 감사 로그
        await create_audit_log(session, ctx.org_id, ctx.user_id,
            "agent.run.completed", "AgentRun", run.id)

        return run
```

## Step 5-3. SSE 스트리밍 라우터

```python
from fastapi.responses import StreamingResponse
import json

@router.post("/{agent_id}/run/stream")
async def run_agent_stream(
    agent_id: UUID,
    request: AgentRunRequest,
    ctx: TenantContext = Depends(get_tenant_context),
):
    async def event_generator():
        try:
            async for chunk in agent_service.run_agent_stream(
                agent_id, request.input, ctx
            ):
                event = json.dumps(chunk.dict())
                yield f"data: {event}\n\n"
        except AgentGuardrailException as e:
            yield f"data: {json.dumps({'type':'error','code':'ERR_AGENT_003','message':str(e)})}\n\n"
        except AgentTimeoutException:
            yield f"data: {json.dumps({'type':'error','code':'ERR_AGENT_002'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # nginx 버퍼링 비활성화
        }
    )
```

---

# Phase 6 — 통합 검증 및 CI/CD

## Step 6-1. 통합 테스트 체크리스트

```
□ make up → 모든 컨테이너 healthy
□ make migrate → 마이그레이션 오류 없음
□ POST /api/v1/auth/register → 201 Created
□ POST /api/v1/auth/login → 200 + access_token
□ GET /api/v1/users/me → 200 (Bearer token 포함)
□ GET /api/v1/users/me → 401 (token 없음)
□ GET /api/v1/users/me → 401 (만료된 token)
□ POST /api/v1/auth/refresh → 200 + 새 access_token
□ POST /api/v1/auth/logout → 200
□ POST /api/v1/auth/logout → 401 (재사용 시도)
□ POST /api/v1/agents → 201 (pro 플랜)
□ POST /api/v1/agents → 403 (free 플랜)
□ GET /health/detailed → 200 + DB/Redis 상태
```

## Step 6-2. GitHub Actions (.github/workflows/ci.yml)

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -e ".[dev]"
      - run: ruff check .
      - run: mypy app/
      - run: pytest tests/ -v --cov=app

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: npm ci
      - run: npm run lint
      - run: npx tsc --noEmit
      - run: npm test

  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker compose build
```

---

## 전체 구현 체크리스트

### Phase 1 — 인프라
- [ ] docker-compose.yml (DB + Redis + Backend + Frontend + healthcheck)
- [ ] docker-compose.override.yml (로컬 개발 전용 오버라이드)
- [ ] .env.example 작성 + .gitignore 확인 (.env 커밋 금지)
- [ ] .env 복사 후 실제 값 입력
- [ ] Makefile 작성 (up / down / migrate / shell-be / test / lint)
- [ ] `make up` → 모든 컨테이너 healthy 확인

### Phase 2 — Backend 공통 기반
- [ ] db/base.py (DeclarativeBase — 반드시 가장 먼저)
- [ ] core/config.py (Settings, field_validator)
- [ ] core/logging.py (structlog JSON, 민감 정보 마스킹)
- [ ] db/session.py (async engine, current_tenant_id ContextVar)
- [ ] Alembic 초기화 (alembic init) + alembic.ini + env.py 설정
- [ ] models/base.py (BaseModel · SoftDeleteMixin · TenantModel)
- [ ] schemas/base.py (ApiResponse · PaginatedResponse · ErrorResponse)
- [ ] core/exceptions.py (AppException + 에러 코드 전체)
- [ ] core/security.py (JWT 발급/검증 · bcrypt cost=12)
- [ ] core/cache.py (Redis 싱글톤 · cache_get/set/delete)
- [ ] utils/datetime.py (now_utc · to_kst)
- [ ] utils/pagination.py (PaginationParams · paginate())
- [ ] api/deps.py (TenantContext · require_role · require_plan)
- [ ] core/audit.py (create_audit_log)
- [ ] main.py (lifespan · CORS · 전역 예외 핸들러 · /health)

### Phase 3 — 인증·테넌트 도메인
- [ ] domains/users/models.py
- [ ] domains/organizations/models.py
- [ ] env.py에 모델 import 추가 → 마이그레이션 생성 + 적용
- [ ] domains/auth/service.py (로그인 · Refresh Rotate · 로그아웃)
- [ ] domains/auth/router.py (/login · /refresh · /logout)
- [ ] domains/users/router.py (GET/PATCH /users/me)
- [ ] domains/organizations/router.py (CRUD · 멤버 초대/관리)

### Phase 4 — Frontend 공통 기반
- [ ] tsconfig.json (path alias @/ — 반드시 가장 먼저)
- [ ] .eslintrc.json + .prettierrc
- [ ] next.config.ts (rewrites 프록시)
- [ ] types/api.ts (ApiResponse · PaginatedResponse · ApiError)
- [ ] types/auth.ts (User · Organization · MemberContext)
- [ ] constants/api.ts (ENDPOINTS)
- [ ] lib/axios.ts (인터셉터 · Refresh 자동 재발급)
- [ ] stores/authStore.ts (Zustand · 메모리 저장)
- [ ] lib/queryClient.ts (React Query)
- [ ] hooks/useAuth.ts · hooks/usePagination.ts
- [ ] components/common/LoadingSpinner.tsx
- [ ] components/common/ErrorBoundary.tsx
- [ ] components/ui/ (Button · Input · Modal · Toast · Table · Skeleton)
- [ ] app/providers.tsx (QueryClientProvider + ErrorBoundary)
- [ ] app/layout.tsx (Providers 감싸기)
- [ ] tailwind.config.ts (디자인 토큰)
- [ ] app/middleware.ts (인증 필요 라우트 보호)

### Phase 5 — AI Agent 도메인
- [ ] domains/agents/models.py (Agent · AgentRun · AgentMemory)
- [ ] env.py에 Agent 모델 import 추가 + 마이그레이션
- [ ] core/guardrails.py (Input · Execution · Output Guardrail)
- [ ] domains/agents/service.py (실행 플로우 · Guardrail 통합)
- [ ] domains/agents/router.py (CRUD · /run · /run/stream)
- [ ] components/agents/AgentChat.tsx (SSE 수신 · 스트리밍)
- [ ] components/agents/AgentStatus.tsx (실행 상태 표시)

### Phase 6 — 통합 검증
- [ ] make up → 전체 컨테이너 healthy
- [ ] make migrate → 오류 없음
- [ ] curl :8000/docs → Swagger UI 접속 확인
- [ ] curl :3000 → Frontend 접속 확인
- [ ] tsc --noEmit → TypeScript 오류 0개
- [ ] npm run lint → ESLint 오류 0개
- [ ] mypy app/ → 타입 오류 0개
- [ ] 통합 테스트 시나리오 9개 전체 통과
- [ ] 브라우저 Network → API CORS 연결 확인
- [ ] .github/workflows/ci.yml 구성
- [ ] README.md 작성 (로컬 실행 방법)

---

## 주의사항

### 의존성 순서를 반드시 지켜야 하는 이유

Python 모듈은 `import`할 때 의존하는 모듈이 먼저 존재해야 한다. 순서를 무시하면 `ImportError` 또는 순환 참조 오류가 발생한다.

```
db/base.py → core/config.py → core/logging.py → db/session.py
  → models/base.py → schemas/base.py → core/exceptions.py
  → core/security.py → core/cache.py → utils/* → api/deps.py → main.py
```

### 환경변수 관리 주의사항

- `.env`는 절대 Git에 커밋하지 않는다. `.gitignore`에 반드시 포함.
- `.env.example`은 실제 값 없이 **키만** 포함하여 커밋한다.
- 새 환경변수 추가 시 `.env.example`도 동시에 업데이트한다.
- 운영 환경에서는 AWS Secrets Manager / Parameter Store에서 주입한다.

### SQLAlchemy async 주의사항

- `asyncpg` 드라이버 필수. `DATABASE_URL`에 `postgresql+asyncpg://` 형식.
- 모든 DB 쿼리 함수는 `async def` + `await` 사용.
- Alembic은 sync 드라이버를 사용하므로 `env.py`에서 URL의 `+asyncpg`를 제거해야 한다.
- **새 모델 추가 시마다 `env.py`에 import를 추가**해야 Alembic이 자동 감지한다.

### Redis 연결 관리

- `redis.asyncio` (async 클라이언트) 사용. 동기 클라이언트와 혼용 금지.
- `core/cache.py`의 싱글톤을 통해 연결을 1회만 생성하고 재사용한다.
- 캐시 키 네이밍: `{namespace}:{entity}:{id}` 형태로 통일.
- 앱 종료 시 `close_redis()`를 lifespan에서 호출하여 연결을 명시적으로 닫는다.

### Frontend 주의사항

- Access Token은 절대 `localStorage`에 저장하지 않는다. Zustand 메모리에만 저장.
- 서버 데이터는 React Query, UI 상태(모달 열림 등)는 `useState`로 분리 관리.
- `queryKey`는 계층적 배열로 구성 (Quick Reference Card Section 6 참고).
- 각 Phase가 완료될 때마다 Git 커밋을 남겨 변경 이력을 관리한다.

---

> 📘 **설계 결정 이유는:** Framework 문서를 참고하세요.
> 📙 **Naming Rule, 에러 코드, API 패턴은:** Quick Reference Card를 참고하세요.