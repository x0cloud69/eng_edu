"""
Redis 싱글톤 클라이언트 및 편의 래퍼.
"""
from typing import Any, Optional

from src.core.config import get_settings

_settings = get_settings()
_redis_client: Optional[Any] = None


def get_redis():
    global _redis_client
    if _redis_client is None:
        try:
            import redis
            _redis_client = redis.from_url(_settings.redis_url, decode_responses=True)
        except ImportError:
            _redis_client = None
    return _redis_client


def cache_get(key: str) -> Any | None:
    r = get_redis()
    if r is None:
        return None
    return r.get(key)


def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    r = get_redis()
    if r is not None:
        r.setex(key, ttl, str(value))


def cache_delete(key: str) -> None:
    r = get_redis()
    if r is not None:
        r.delete(key)


def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        _redis_client.close()
        _redis_client = None
