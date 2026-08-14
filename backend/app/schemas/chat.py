"""Pydantic schemas untuk endpoint chatbot & memory."""
from typing import Literal, Optional

from pydantic import BaseModel, Field

ReadinessStage = Literal["precontemplation", "contemplation", "action", "maintenance", "relapse"]
PolicyAction = Literal["ALLOW", "SAFE_REDIRECT", "CLARIFY", "BLOCK_AND_SIGNPOST"]
ZoneRoute = Literal["zone_1_craving", "zone_1_contemplation", "zone_2_emotional", "zone_3_out_of_scope", "refusal_script", "crisis"]


class ClientContext(BaseModel):
    location_chip: Optional[str] = None
    offline: bool = False


class ConversationCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    readiness_stage: ReadinessStage = "contemplation"


class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    conversation_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    client_context: ClientContext = ClientContext()


class MemoryInfo(BaseModel):
    updated: bool
    context_tags: dict[str, str] = {}


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
