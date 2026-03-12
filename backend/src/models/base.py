"""
공통 BaseModel, SoftDeleteMixin, TenantModel — PK는 반드시 UUID v4.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class BaseModel(Base):
    """id(UUID v4) + created_at + updated_at."""
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SoftDeleteMixin:
    """deleted_at + deleted_by, is_deleted property."""
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class TenantModel(BaseModel, SoftDeleteMixin):
    """BaseModel + SoftDeleteMixin + organization_id + created_by."""
    __abstract__ = True

    organization_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    created_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
