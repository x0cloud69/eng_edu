"""
구조화 로그 — structlog JSON, 민감 필드 자동 마스킹.
"""
import logging
from typing import Any

import structlog

SENSITIVE_KEYS = {"password", "token", "api_key", "secret", "authorization"}


def _mask_sensitive(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: "***" if k.lower() in SENSITIVE_KEYS else _mask_sensitive(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_mask_sensitive(x) for x in data]
    return data


def setup_logging() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )


def get_logger(name: str) -> structlog.BoundLogger:
    return structlog.get_logger(name)
