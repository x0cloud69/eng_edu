"""
감사 로그 헬퍼 — action 형식: {resource}.{action}
"""
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


async def create_audit_log(
    session: AsyncSession,
    org_id: UUID,
    user_id: UUID,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    details: dict | None = None,
) -> None:
    """감사 로그 기록. 실제 구현 시 audit_logs 테이블에 insert."""
    # TODO: AuditLog 모델 및 테이블 연동
    pass
