"""HTTP routes untuk chatbot Renti (health, conversations, chat)."""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
    MemoryInfo,
    ProviderInfo,
)
from app.services.orchestrator import Orchestrator

router = APIRouter(prefix="/api/v1", tags=["chat"])

_orchestrator = Orchestrator()


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(payload: ConversationCreate):
    conversation_id = f"conversation-{uuid.uuid4().hex[:8]}"
    _orchestrator.create_conversation(conversation_id, payload.user_id, payload.readiness_stage)
    return ConversationResponse(
        conversation_id=conversation_id,
        user_id=payload.user_id,
        readiness_stage=payload.readiness_stage,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    if not _orchestrator.conversation_exists(payload.conversation_id):
        raise HTTPException(status_code=404, detail="conversation not found; create it first")
    return _orchestrator.process(payload)
