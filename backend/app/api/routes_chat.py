"""HTTP routes untuk chatbot Renti (health, conversations, chat)."""
import json
import logging
import time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
)
from app.services.orchestrator import Orchestrator

logger = logging.getLogger(__name__)

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

    start_time = time.perf_counter()
    resp = _orchestrator.process(payload)
    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    metadata = {
        "conversation_id": resp.conversation_id,
        "route": resp.route,
        "readiness_stage": resp.readiness_stage,
        "policy_action": resp.policy_action,
        "provider": resp.provider.name,
        "latency_ms": latency_ms,
        "fallback_used": resp.provider.fallback_used,
    }
    logger.info(json.dumps(metadata))

    return resp
