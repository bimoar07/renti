"""Orchestrator - Central coordination of the Renti AI Companion pipeline.

Alur eksekusi (docs/STRUCTURE.md & ADR 09, 10):
raw input -> canonicalize -> safety triage (policy engine) -> memory update ->
routing (zone & intent) -> response generation -> output guardrail -> persistent storage.
"""
from typing import Optional

from app.core.canonicalize import canonicalize_text
from app.core.policy import SafetyPolicyEngine
from app.core.settings import get_settings
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    MemoryInfo,
    ProviderInfo,
    ReadinessStage,
)
from app.services.routing import ZoneRouter
from app.storage.sqlite_store import SQLiteStore


class Orchestrator:
    def __init__(
        self,
        store: Optional[SQLiteStore] = None,
        policy_engine: Optional[SafetyPolicyEngine] = None,
        router: Optional[ZoneRouter] = None,
    ):
        settings = get_settings()
        self.store = store or SQLiteStore(db_path=settings.db_path)
        self.policy_engine = policy_engine or SafetyPolicyEngine(crisis_hotline=settings.crisis_hotline)
        self.router = router or ZoneRouter()

    def create_conversation(
        self,
        conversation_id: str,
        user_id: str,
        readiness: ReadinessStage = "contemplation",
    ) -> None:
        self.store.create_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            readiness_stage=readiness,
        )

    def conversation_exists(self, conversation_id: str) -> bool:
        return self.store.conversation_exists(conversation_id)

    def process(self, req: ChatRequest) -> ChatResponse:
        conv = self.store.get_conversation(req.conversation_id)
        if not conv:
            raise ValueError(f"Conversation {req.conversation_id} not found")

        current_readiness: ReadinessStage = conv["readiness_stage"]
        raw_msg = req.message
        canonical_msg = canonicalize_text(raw_msg)

        # 1. Safety Policy Evaluation (Fast-path & Crisis Check - ADR 09, 12)
        policy_result = self.policy_engine.evaluate(raw_msg, canonical_msg)

        # 2. If acute crisis / self-harm / medical emergency detected
        if policy_result.action == "BLOCK_AND_SIGNPOST":
            reply_text = policy_result.signpost_message or "Silakan hubungi layanan darurat 119."
            self.store.add_message(
                conversation_id=req.conversation_id,
                role="user",
                raw_content=raw_msg,
                canonical_content=canonical_msg,
                route="crisis",
                policy_action="BLOCK_AND_SIGNPOST",
            )
            self.store.add_message(
                conversation_id=req.conversation_id,
                role="assistant",
                raw_content=reply_text,
                canonical_content=reply_text,
                route="crisis",
                policy_action="BLOCK_AND_SIGNPOST",
            )
            return ChatResponse(
                conversation_id=req.conversation_id,
                reply=reply_text,
                route="crisis",
                intent="crisis_support",
                readiness_stage=current_readiness,
                policy_action="BLOCK_AND_SIGNPOST",
                memory=MemoryInfo(updated=False, context_tags={}),
                provider=ProviderInfo(name="policy_fallback", fallback_used=True),
            )

        # 3. If direct prompt injection or system boundary violation
        if policy_result.action == "SAFE_REDIRECT" and policy_result.signpost_message:
            reply_text = policy_result.signpost_message
            self.store.add_message(
                conversation_id=req.conversation_id,
                role="user",
                raw_content=raw_msg,
                canonical_content=canonical_msg,
                route="zone_3_out_of_scope",
                policy_action="SAFE_REDIRECT",
            )
            self.store.add_message(
                conversation_id=req.conversation_id,
                role="assistant",
                raw_content=reply_text,
                canonical_content=reply_text,
                route="zone_3_out_of_scope",
                policy_action="SAFE_REDIRECT",
            )
            return ChatResponse(
                conversation_id=req.conversation_id,
                reply=reply_text,
                route="zone_3_out_of_scope",
                intent="out_of_scope",
                readiness_stage=current_readiness,
                policy_action="SAFE_REDIRECT",
                memory=MemoryInfo(updated=True, context_tags={}),
                provider=ProviderInfo(name="mock", fallback_used=False),
            )

        # 4. Contextual Zone Routing (ADR 10)
        decision = self.router.route_message(
            canonical_text=canonical_msg,
            readiness_stage=current_readiness,
            location_chip=req.client_context.location_chip,
        )

        # 5. Day 1 Baseline Generation (Mock templates for zone routes)
        # Note: Day 2 replaces this with LiteLLM provider adapter + companion prompt
        if decision.route == "refusal_script":
            reply_text = (
                "Coba bilang: 'Gak dulu bro, paru-paru gua lagi minta rehat nih, es teh aja gua mah.' "
                "Mau kubuatkan 3 opsi penolakan lain?"
            )
            policy_act = "ALLOW"
        elif decision.route == "zone_1_contemplation":
            reply_text = (
                "Aku paham kamu masih menimbang-nimbang antara kenyamanan merokok dan keinginan untuk hidup lebih sehat. "
                "Menurutmu, apa hal paling berat saat memikirkan berhenti?"
            )
            policy_act = "ALLOW"
        elif decision.route == "zone_1_craving":
            reply_text = (
                "Gue paham, craving bisa terasa kuat. Yuk lewati beberapa menit pertama "
                "dulu dengan napas pelan 4-7-8 dan urge surfing."
            )
            policy_act = "ALLOW"
        elif decision.route == "zone_2_emotional":
            reply_text = (
                "Pasti berat banget rasanya menghadapi situasi yang bikin stres begini. "
                "Wajar kalau pikiran langsung mencari pelarian ke rokok/vape. "
                "Apakah saat ini kamu lagi merasakan dorongan kuat untuk merokok?"
            )
            policy_act = "ALLOW"
        else:  # zone_3_out_of_scope
            reply_text = (
                "Sebagai AI Companion Renti, aku didesain khusus mendampingi "
                "perjalanan berhenti merokok dan vape. Ada yang bisa kubantu seputar itu?"
            )
            policy_act = "SAFE_REDIRECT"

        # 6. Persistent Memory Update (SQLite)
        merged_tags = {**conv.get("context_tags", {}), **decision.suggested_tags}
        self.store.update_summary_and_tags(
            conversation_id=req.conversation_id,
            summary=conv.get("summary", ""),
            context_tags=merged_tags,
        )

        self.store.add_message(
            conversation_id=req.conversation_id,
            role="user",
            raw_content=raw_msg,
            canonical_content=canonical_msg,
            route=decision.route,
            policy_action=policy_act,
        )
        self.store.add_message(
            conversation_id=req.conversation_id,
            role="assistant",
            raw_content=reply_text,
            canonical_content=reply_text,
            route=decision.route,
            policy_action=policy_act,
        )

        return ChatResponse(
            conversation_id=req.conversation_id,
            reply=reply_text,
            route=decision.route,
            intent=decision.intent,
            readiness_stage=current_readiness,
            policy_action=policy_act,
            memory=MemoryInfo(updated=True, context_tags=decision.suggested_tags),
            provider=ProviderInfo(name="mock", fallback_used=False),
        )
