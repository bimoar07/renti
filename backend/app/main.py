"""Renti Backend - FastAPI application entrypoint.

Renti (Rekan Berhenti) - AI Companion Chatbot untuk mendampingi berhenti merokok/vape.
Gemastik XIX - Divisi Pengembangan Perangkat Lunak.

Alur orkestrasi (lihat docs/STRUCTURE.md & docs/decisions/README.md):
raw input -> canonicalize -> safety triage -> policy -> memory -> extract -> route -> generate -> guardrail
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes_chat import router as chat_router
from app.core.settings import get_settings


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

app.include_router(chat_router)


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "service": "renti-backend", "version": "0.1.0"}
