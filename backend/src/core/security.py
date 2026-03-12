"""
JWT 발급/검증, bcrypt, API Token 해시.
"""
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(
    user_id: UUID,
    org_id: UUID,
    role: str = "user",
    plan: str = "free",
) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "org_id": str(org_id), "role": role, "plan": plan, "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def create_refresh_token(user_id: UUID) -> tuple[str, str]:
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    import uuid
    jti = str(uuid.uuid4())
    payload = {"sub": str(user_id), "exp": expire, "type": "refresh", "jti": jti}
    token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
    return token, jti


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])


def hash_api_token(token: str) -> str:
    import hashlib
    return hashlib.sha256(token.encode()).hexdigest()
