"""
UTC/KST 날짜 유틸.
"""
from datetime import datetime, timezone

KST = timezone(offset=__import__("datetime").timedelta(hours=9))


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def to_kst(dt: datetime) -> datetime:
    return dt.astimezone(KST)


def format_kst(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    return to_kst(dt).strftime(fmt)
