"""
커스텀 예외 계층 — HTTPException 상속, 에러 코드 체계.
"""
from fastapi import HTTPException


class AppException(HTTPException):
    """기본 앱 예외."""

    def __init__(self, status_code: int, detail: str, error_code: str = "ERR_APP_000"):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(401, detail, "ERR_AUTH_001")


class TokenExpiredException(AppException):
    def __init__(self, detail: str = "Token expired"):
        super().__init__(401, detail, "ERR_AUTH_002")


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(403, detail, "ERR_AUTH_004")


class NotFoundException(AppException):
    def __init__(self, detail: str = "Not found"):
        super().__init__(404, detail, "ERR_DATA_001")
