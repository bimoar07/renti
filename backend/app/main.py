"""Renti Backend - FastAPI application entrypoint.

Renti (Rekan Berhenti) - AI Companion Chatbot untuk mendampingi berhenti merokok/vape.
Gemastik XIX - Divisi Pengembangan Perangkat Lunak.

Alur orkestrasi (lihat docs/STRUCTURE.md & docs/decisions/README.md):
raw input -> canonicalize -> safety triage -> policy -> memory -> extract -> route -> generate -> guardrail
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.api.routes_chat import router as chat_router
from app.core.settings import get_settings

logger = logging.getLogger("renti.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    # TODO(Hari 2): inisialisasi SQLite store & (Hari 7) provider adapter di sini.
    print(f"[Renti] backend starting. provider_primary={settings.llm_primary_provider}")
    yield


app = FastAPI(
    title="Renti Backend API",
    description="AI Companion Chatbot untuk berhenti merokok/vape (Gemastik XIX).",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "code" in exc.detail and "message" in exc.detail:
        detail = exc.detail
    elif isinstance(exc.detail, str):
        code_map = {
            400: "bad_request",
            404: "not_found",
            422: "validation_error",
            500: "internal_error",
        }
        detail = {
            "code": code_map.get(exc.status_code, "http_error"),
            "message": exc.detail,
        }
    else:
        detail = exc.detail
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail},
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": {
                "code": "internal_error",
                "message": "Terjadi kesalahan internal pada server. Silakan coba lagi nanti.",
            }
        },
    )


app.include_router(chat_router)


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "service": "renti-backend", "version": "0.1.0"}
