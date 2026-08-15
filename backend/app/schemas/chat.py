"""Pydantic schemas untuk endpoint chatbot & memory (re-exports memory schemas)."""
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.memory import (
    ClientContext,
    MemoryInfo,
    PolicyAction,
    ReadinessStage,
    RollingSummary,
    ZoneRoute,
)


class ConversationCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    readiness_stage: ReadinessStage = "contemplation"


class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    conversation_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    client_context: ClientContext = ClientContext()


class ProviderInfo(BaseModel):
    name: str
    fallback_used: bool = False


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    route: ZoneRoute
    intent: str
    readiness_stage: ReadinessStage
    policy_action: PolicyAction
    memory: MemoryInfo
    provider: ProviderInfo


class ConversationResponse(BaseModel):
    conversation_id: str
    user_id: str
    readiness_stage: ReadinessStage
    created_at: str


__all__ = [
    "ReadinessStage",
    "PolicyAction",
    "ZoneRoute",
    "ClientContext",
    "MemoryInfo",
    "RollingSummary",
    "ConversationCreate",
    "ChatRequest",
    "ProviderInfo",
    "ChatResponse",
    "ConversationResponse",
]
