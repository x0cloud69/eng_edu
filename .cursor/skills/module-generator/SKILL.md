---
name: module-generator
description: >-
  Generates a complete business module (7 files) following the AI-Native SaaS
  Standard Framework pattern. Use when the user says "모듈 만들어줘", "create
  module", "새 모듈 생성", "XX 기능 추가해줘", "generate CRUD module", or "module
  for XX".
---

# Module Generator

You are a module generator for the AI-Native SaaS Standard Framework.
When the user requests a new module, generate ALL 7 files following the exact patterns below.

## Step 0: Gather Information

Ask the user (if not already provided):
1. **모듈 이름** (snake_case, 예: `esignature`, `payment`, `document`)
2. **주요 엔티티 필드** (예: title, amount, status 등)
3. **Authority Level** — L0(조회 전용) / L1(승인 필요, 기본값) / L2(관리자) / L3(시스템)
4. **허용 Tool** — 기본값: `["db_query", "db_write"]`
5. **고위험 액션** — ApprovalGate가 필수인 액션 (예: sign, approve, delete)

## Step 1: Generate 7 Files

모든 파일은 `backend/src/modules/{module_name}/` 아래에 생성한다.

---

### 1-1. `__init__.py`
```python
# 빈 파일
```

---

### 1-2. `models.py` — TenantBaseModel 상속 필수

```python
"""
{ModuleName} 모듈 DB 모델 — TenantBaseModel 상속
"""
from __future__ import annotations

from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base_model import TenantBaseModel


class {EntityName}(TenantBaseModel):
    """
    {설명} — TenantBaseModel 상속
    자동 제공: id(UUID), tenant_id, created_at, updated_at, is_active, is_deleted, deleted_at, created_by
    """
    __tablename__ = "{table_name}"

    # 비즈니스 필드만 추가
    {fields}
```

**규칙:**
- 반드시 `TenantBaseModel` 상속 (글로벌 테이블만 `BaseModel`)
- `__tablename__` 은 복수형 snake_case
- TenantBaseModel이 제공하는 컬럼(id, tenant_id, created_at 등)은 재선언 금지

---

### 1-3. `schemas.py` — Pydantic v2

```python
"""
{ModuleName} 모듈 Pydantic 스키마
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class {EntityName}Create(BaseModel):
    """생성 요청"""
    {create_fields}


class {EntityName}Update(BaseModel):
    """수정 요청 — 모든 필드 Optional"""
    {update_fields}


class {EntityName}Out(BaseModel):
    """응답 스키마"""
    id: UUID
    tenant_id: UUID
    {output_fields}
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
```

**규칙:**
- Create: 필수 필드는 `...`, 선택은 `None`
- Update: 모든 필드 `Optional` (PATCH 지원)
- Out: `model_config = {"from_attributes": True}` 필수

---

### 1-4. `repository.py` — DB CRUD만, 비즈니스 로직 없음

```python
"""
{ModuleName} Repository — DB CRUD
"""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.{module_name}.models import {EntityName}


class {EntityName}Repository:
    """{EntityName} DB CRUD"""

    async def get(
        self, item_id: UUID, tenant_id: UUID, session: AsyncSession
    ) -> {EntityName} | None:
        result = await session.execute(
            select({EntityName}).where(
                {EntityName}.id == item_id,
                {EntityName}.tenant_id == tenant_id,
                {EntityName}.deleted_at.is_(None),       # ★ soft delete 필터
            )
        )
        return result.scalars().first()

    async def list(
        self,
        tenant_id: UUID,
        session: AsyncSession,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[{EntityName}], int]:
        base = select({EntityName}).where(
            {EntityName}.tenant_id == tenant_id,
            {EntityName}.deleted_at.is_(None),
        )
        count_stmt = select(func.count()).select_from(base.subquery())
        total_result = await session.execute(count_stmt)
        total = total_result.scalar() or 0

        result = await session.execute(
            base.order_by({EntityName}.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def create(
        self, item: {EntityName}, session: AsyncSession
    ) -> {EntityName}:
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    async def update(
        self, item: {EntityName}, session: AsyncSession
    ) -> {EntityName}:
        await session.flush()
        await session.refresh(item)
        return item

    async def soft_delete(
        self, item: {EntityName}, session: AsyncSession
    ) -> None:
        from datetime import datetime, timezone
        item.deleted_at = datetime.now(timezone.utc)
        item.is_active = False
        await session.flush()
```

**규칙:**
- 모든 조회에 `tenant_id` 필터 + `deleted_at.is_(None)` 필수
- 물리 DELETE 금지 — soft_delete만 허용
- 비즈니스 로직 금지 — Service에서 처리

---

### 1-5. `service.py` — 비즈니스 로직 + Audit Log

```python
"""
{ModuleName} 서비스 — 비즈니스 로직
"""
from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.audit import create_audit_log
from src.modules.{module_name}.models import {EntityName}
from src.modules.{module_name}.repository import {EntityName}Repository
from src.modules.{module_name}.schemas import {EntityName}Create, {EntityName}Update


class {ModuleName}Service:
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID | None = None):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.repo = {EntityName}Repository()

    async def list(self, page: int = 1, size: int = 20) -> tuple[list[{EntityName}], int]:
        offset = (page - 1) * size
        return await self.repo.list(self.tenant_id, self.db, limit=size, offset=offset)

    async def get(self, item_id: uuid.UUID) -> {EntityName} | None:
        return await self.repo.get(item_id, self.tenant_id, self.db)

    async def create(self, data: {EntityName}Create) -> {EntityName}:
        item = {EntityName}(
            tenant_id=self.tenant_id,
            {create_assignment}
        )
        item = await self.repo.create(item, self.db)
        await create_audit_log(
            session=self.db,
            org_id=self.tenant_id,
            user_id=self.user_id,
            action="{module_name}.created",
            resource_type="{EntityName}",
            resource_id=item.id,
            after_data={{"id": str(item.id)}},
            severity="info",
        )
        return item

    async def update(self, item_id: uuid.UUID, data: {EntityName}Update) -> {EntityName} | None:
        item = await self.repo.get(item_id, self.tenant_id, self.db)
        if not item:
            return None
        {update_assignment}
        item = await self.repo.update(item, self.db)
        await create_audit_log(
            session=self.db,
            org_id=self.tenant_id,
            user_id=self.user_id,
            action="{module_name}.updated",
            resource_type="{EntityName}",
            resource_id=item.id,
            severity="info",
        )
        return item

    async def soft_delete(self, item_id: uuid.UUID) -> bool:
        item = await self.repo.get(item_id, self.tenant_id, self.db)
        if not item:
            return False
        await self.repo.soft_delete(item, self.db)
        await create_audit_log(
            session=self.db,
            org_id=self.tenant_id,
            user_id=self.user_id,
            action="{module_name}.deleted",
            resource_type="{EntityName}",
            resource_id=item.id,
            severity="info",
        )
        return True
```

**규칙:**
- 생성자에서 `tenant_id` 주입 필수
- CUD 작업마다 `create_audit_log()` 호출 필수
- Repository만 호출 — 직접 SQL 금지

---

### 1-6. `router.py` — FastAPI 표준 라우터

```python
"""
{ModuleName} API — prefix='/api/v1/{module_name}'
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundException
from src.core.security import CurrentUser, get_current_user
from src.db.session import get_db
from src.schemas.base import ApiResponse, PaginatedData, PaginatedResponse
from src.modules.{module_name}.schemas import (
    {EntityName}Create,
    {EntityName}Out,
    {EntityName}Update,
)
from src.modules.{module_name}.service import {ModuleName}Service

router = APIRouter(prefix="/api/v1/{module_name}", tags=["{ModuleName}"])

_auth = Depends(get_current_user)


@router.get("", response_model=PaginatedResponse[{EntityName}Out])
async def list_items(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = _auth,
):
    svc = {ModuleName}Service(db, current_user.tenant_id)
    items, total = await svc.list(page=page, size=size)
    total_pages = max(1, (total + size - 1) // size)
    return PaginatedResponse(
        data=PaginatedData(
            items=[{EntityName}Out.model_validate(i) for i in items],
            total=total, page=page, size=size, total_pages=total_pages,
        )
    )


@router.post("", response_model=ApiResponse[{EntityName}Out], status_code=201)
async def create_item(
    body: {EntityName}Create,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = _auth,
):
    svc = {ModuleName}Service(db, current_user.tenant_id)
    item = await svc.create(body)
    return ApiResponse(data={EntityName}Out.model_validate(item))


@router.get("/{{item_id}}", response_model=ApiResponse[{EntityName}Out])
async def get_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = _auth,
):
    svc = {ModuleName}Service(db, current_user.tenant_id)
    item = await svc.get(item_id)
    if not item:
        raise NotFoundException("{EntityName}")
    return ApiResponse(data={EntityName}Out.model_validate(item))


@router.patch("/{{item_id}}", response_model=ApiResponse[{EntityName}Out])
async def update_item(
    item_id: UUID,
    body: {EntityName}Update,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = _auth,
):
    svc = {ModuleName}Service(db, current_user.tenant_id)
    item = await svc.update(item_id, body)
    if not item:
        raise NotFoundException("{EntityName}")
    return ApiResponse(data={EntityName}Out.model_validate(item))


@router.delete("/{{item_id}}", status_code=204, response_model=None)
async def delete_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = _auth,
):
    svc = {ModuleName}Service(db, current_user.tenant_id)
    ok = await svc.soft_delete(item_id)
    if not ok:
        raise NotFoundException("{EntityName}")
```

**규칙:**
- prefix: `/api/v1/{module_name}`
- 모든 응답: `ApiResponse` 또는 `PaginatedResponse` 래핑
- 인증: `get_current_user` 의존성 필수
- DELETE: 204 + soft_delete

---

### 1-7. `agent.py` — BaseAgent 상속

```python
"""
{ModuleName} 모듈 Agent — BaseAgent 상속
OrchestratorAgent.register() 등록
"""
from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.base_agent import (
    AgentContext,
    AgentResult,
    AuthorityLevel,
    BaseAgent,
)
from src.modules.{module_name}.service import {ModuleName}Service
from src.modules.{module_name}.schemas import (
    {EntityName}Create,
    {EntityName}Out,
    {EntityName}Update,
)


class {ModuleName}Agent(BaseAgent):
    """
    {ModuleName} Agent — Capability Agent (Layer 2)
    """
    name            = "{ModuleName}Agent"
    authority_level = AuthorityLevel.{authority_level}
    allowed_tools   = {allowed_tools}

    async def execute(self, ctx: AgentContext, db: AsyncSession | None = None) -> AgentResult:
        action = ctx.payload.get("action", "list")
        tenant_id = ctx.tenant_id

        if not db:
            return AgentResult(
                success=False,
                message="{ModuleName}Agent: db 세션 필요",
                trace_id=ctx.trace_id,
            )

        try:
            tid = uuid.UUID(tenant_id) if tenant_id else uuid.UUID("00000000-0000-0000-0000-000000000001")
            svc = {ModuleName}Service(db, tid)

            if action == "list":
                page = int(ctx.payload.get("page", 1))
                size = int(ctx.payload.get("size", 20))
                items, total = await svc.list(page=page, size=size)
                data = {{
                    "items": [{EntityName}Out.model_validate(i).model_dump(mode="json") for i in items],
                    "total": total,
                }}

            elif action == "get":
                item_id = uuid.UUID(str(ctx.payload["item_id"]))
                item = await svc.get(item_id)
                if not item:
                    return AgentResult(success=False, message="항목을 찾을 수 없습니다", trace_id=ctx.trace_id)
                data = {EntityName}Out.model_validate(item).model_dump(mode="json")

            elif action == "create":
                create_data = {EntityName}Create({create_kwargs})
                item = await svc.create(create_data)
                data = {EntityName}Out.model_validate(item).model_dump(mode="json")

            elif action == "update":
                item_id = uuid.UUID(str(ctx.payload["item_id"]))
                update_data = {EntityName}Update({update_kwargs})
                item = await svc.update(item_id, update_data)
                if not item:
                    return AgentResult(success=False, message="항목을 찾을 수 없습니다", trace_id=ctx.trace_id)
                data = {EntityName}Out.model_validate(item).model_dump(mode="json")

            elif action == "delete":
                item_id = uuid.UUID(str(ctx.payload["item_id"]))
                ok = await svc.soft_delete(item_id)
                if not ok:
                    return AgentResult(success=False, message="항목을 찾을 수 없습니다", trace_id=ctx.trace_id)
                data = {{"deleted": True, "item_id": str(item_id)}}

            # {high_risk_actions — ApprovalGate에서 이미 검증됨}

            else:
                return AgentResult(
                    success=False,
                    message=f"{ModuleName}Agent: 알 수 없는 액션 '{{action}}'",
                    trace_id=ctx.trace_id,
                )

            return AgentResult(success=True, data=data, trace_id=ctx.trace_id)

        except KeyError as e:
            return AgentResult(success=False, message=f"필수 파라미터 누락: {{e}}", trace_id=ctx.trace_id)
        except Exception as e:
            return AgentResult(success=False, message=f"{ModuleName}Agent: {{e}}", trace_id=ctx.trace_id)
```

**규칙:**
- `BaseAgent` 상속 필수
- `name`, `authority_level`, `allowed_tools` 선언 필수
- `execute()` 반환: 항상 `AgentResult`
- 예외 시에도 `AgentResult`로 래핑 (raise 금지)

---

## Step 2: Register in main.py

파일 생성 후 반드시 `backend/src/api/main.py`에 아래 2줄을 추가한다:

```python
# Router 등록 (라우터 등록 섹션에)
from src.modules.{module_name}.router import router as {module_name}_router
app.include_router({module_name}_router)

# Agent 등록 (Agent 등록 섹션에)
from src.modules.{module_name}.agent import {ModuleName}Agent
OrchestratorAgent.register("{module_name}.*", {ModuleName}Agent())
```

## Step 3: Verify

생성 완료 후 다음을 확인한다:
1. 7개 파일 모두 생성되었는가
2. models.py — TenantBaseModel 상속
3. repository.py — tenant_id 필터 + deleted_at IS NULL
4. service.py — create_audit_log 호출
5. router.py — ApiResponse/PaginatedResponse 래핑
6. agent.py — BaseAgent 상속 + name/authority_level/allowed_tools
7. main.py — Router + Agent 등록

## Reference Files

- `backend/src/modules/example/` — 완전한 참조 구현
- `backend/src/modules/MODULE_TEMPLATE.md` — 체크리스트
- `.cursor/context/phase3_context.json` — Phase 3 기준
- `.cursor/context/saas_foundation.json` — SaaS 표준
- `.cursor/rules/09_capability.mdc` — 코드 생성 규칙
