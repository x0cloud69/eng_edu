"""
FastAPI 공통 의존성 — 인증, 테넌트, 역할.
"""
from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.exceptions import UnauthorizedException
from src.core.security import decode_token

security = HTTPBearer(auto_error=False)


@dataclass
class TenantContext:
    user_id: UUID
    org_id: UUID
    role: str
    plan: str


async def get_tenant_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> TenantContext | None:
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise UnauthorizedException()
        return TenantContext(
            user_id=UUID(payload["sub"]),
            org_id=UUID(payload["org_id"]),
            role=payload.get("role", "user"),
            plan=payload.get("plan", "free"),
        )
    except Exception:
        raise UnauthorizedException()


def require_role(*roles: str):
    """지정 역할만 허용 (의존성)."""
    async def _check(ctx: TenantContext | None = Depends(get_tenant_context)):
        if ctx is None:
            raise UnauthorizedException()
        if ctx.role not in roles:
            from src.core.exceptions import ForbiddenException
            raise ForbiddenException()
        return ctx
    return Depends(_check)


def require_plan(*plans: str):
    """지정 플랜만 허용 (의존성)."""
    async def _check(ctx: TenantContext | None = Depends(get_tenant_context)):
        if ctx is None:
            raise UnauthorizedException()
        if ctx.plan not in plans:
            from src.core.exceptions import ForbiddenException
            raise ForbiddenException()
        return ctx
    return Depends(_check)
