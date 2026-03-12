"""
페이지네이션 파라미터 및 쿼리 헬퍼.
"""
from dataclasses import dataclass
from typing import TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


@dataclass
class PaginationParams:
    page: int = 1
    size: int = 20

    def __post_init__(self):
        self.page = max(1, self.page)
        self.size = min(100, max(1, self.size))


async def paginate(
    session: AsyncSession,
    query,
    params: PaginationParams,
) -> dict:
    """쿼리에 limit/offset 적용 후 total과 함께 반환."""
    total_result = await session.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0
    offset = (params.page - 1) * params.size
    result = await session.execute(query.offset(offset).limit(params.size))
    items = result.scalars().all()
    total_pages = (total + params.size - 1) // params.size if params.size else 0
    return {
        "items": items,
        "total": total,
        "page": params.page,
        "size": params.size,
        "total_pages": total_pages,
    }
