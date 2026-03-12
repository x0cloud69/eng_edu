"""
SQLAlchemy DeclarativeBase — 모든 ORM 모델의 루트.
Alembic env.py가 Base.metadata를 import하므로 반드시 별도 파일로 유지.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """공통 DeclarativeBase. 모든 모델이 상속."""
    pass
