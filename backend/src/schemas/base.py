"""
표준 API 응답 Pydantic 스키마 — ApiResponse, PaginatedResponse, ErrorResponse.
"""
from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """단건 응답: success + data."""
    success: bool = True
    data: T | None = None


class PaginatedData(BaseModel, Generic[T]):
    """페이지네이션 데이터."""
    items: list[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    size: int = 20
    total_pages: int = 0


class PaginatedResponse(BaseModel, Generic[T]):
    """페이지네이션 응답."""
    success: bool = True
    data: PaginatedData[T] | None = None


class ErrorDetail(BaseModel):
    """에러 상세."""
    code: str = ""
    message: str = ""
    request_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """에러 응답."""
    success: bool = False
    error: ErrorDetail | None = None
