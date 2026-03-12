"""
FastAPI 앱 진입점 — lifespan, CORS, 예외 핸들러, /health.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.cache import close_redis
from src.core.exceptions import AppException
from src.core.logging import setup_logging
from src.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield
    await engine.dispose()
    close_redis()


app = FastAPI(
    title="eng_edu API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": exc.error_code, "message": exc.detail}},
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
