"""Orchestrator - Central coordination of the Renti AI Companion pipeline.

Alur eksekusi lengkap (docs/STRUCTURE.md & ADR 02, 04, 06, 09, 10, 11, 12, 13):
1. Canonicalize input
2. Safety policy triage (fast-path crisis / injection check)
3. Load memory (rolling summary & recent message history)
4. Hybrid readiness transition evaluation (Zone 1 candidate turns) -> update stage if valid
5. Contextual Zone & intent routing (evaluated with latest readiness stage)
6. Deterministic tone detection & storage
7. System prompt composition with tone, readiness, and rolling summary
8. Context assembly (summary + up to 6 raw messages) via MemoryService
9. LLM Provider generation (Gemini -> Groq -> template fallback)
10. Output Guardrail (KEEP / SANITIZE / REPLACE)
11. Rolling summary update & persistent storage via MemoryService
"""
from typing import Optional

from app.core.canonicalize import canonicalize_text
from app.core.policy import SafetyPolicyEngine
from app.core.settings import get_settings
from app.prompts.companion import build_system_prompt, detect_tone
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    MemoryInfo,
    ProviderInfo,
    ReadinessStage,
)
from app.services.llm_provider import LLMProvider
from app.services.memory import MemoryService
from app.services.output_guardrail import OutputGuardrail
from app.services.readiness import ReadinessService
from app.services.routing import ZoneRouter
from app.storage.sqlite_store import SQLiteStore


class Orchestrator:
    def __init__(
        self,
        store: Optional[SQLiteStore] = None,
        policy_engine: Optional[SafetyPolicyEngine] = None,
        router: Optional[ZoneRouter] = None,
        provider: Optional[LLMProvider] = None,
        guardrail: Optional[OutputGuardrail] = None,
        readiness_service: Optional[ReadinessService] = None,
        memory_service: Optional[MemoryService] = None,
    ):
        settings = get_settings()
        self.store = store or SQLiteStore(db_path=settings.db_path)
        self.policy_engine = policy_engine or SafetyPolicyEngine(crisis_hotline=settings.crisis_hotline)
        self.router = router or ZoneRouter()
        self.provider = provider or LLMProvider(
            gemini_api_key=settings.gemini_api_key,
            groq_api_key=settings.groq_api_key,
            gemini_model=settings.llm_primary_provider,
            groq_model=settings.llm_fallback_provider,
            per_provider_timeout=settings.llm_per_provider_timeout,
            total_deadline=settings.llm_total_deadline,
        )
        self.guardrail = guardrail or OutputGuardrail()
        self.readiness_service = readiness_service or ReadinessService()
        self.memory_service = memory_service or MemoryService()

    def create_conversation(
        self,
        conversation_id: str,
        user_id: str,
        readiness: ReadinessStage = "contemplation",
        tone: str = "standard",
    ) -> None:
        self.store.create_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            readiness_stage=readiness,
            tone=tone,
        )

    def conversation_exists(self, conversation_id: str) -> bool:
        return self.store.conversation_exists(conversation_id)

    def process(self, req: ChatRequest) -> ChatResponse:
        conv = self.store.get_conversation(req.conversation_id)
        if not conv:
            raise ValueError(f"Conversation {req.conversation_id} not found")

        current_readiness: ReadinessStage = conv["readiness_stage"]
        current_tone: str = conv.get("tone", "standard")
        raw_msg = req.message
        canonical_msg = canonicalize_text(raw_msg)

        # 1. Safety Policy Evaluation (Fast-path & Crisis Check - ADR 09, 12)
        policy_result = self.policy_engine.evaluate(raw_msg, canonical_msg)

        # 2. Fast-path: Acute crisis / self-harm / medical emergency
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

        # 3. Direct Prompt Injection / System Violation
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
                provider=ProviderInfo(name="template", fallback_used=True),
            )

        # 4. Load Memory & History
        old_summary = conv.get("summary", "").strip()
        past_msgs = self.store.get_messages(req.conversation_id, limit=6)

        # 5. Candidate Routing & Hybrid Readiness Evaluation (ADR 06, 13)
        candidate_decision = self.router.route_message(
            canonical_text=canonical_msg,
            readiness_stage=current_readiness,
            location_chip=req.client_context.location_chip,
        )

        if candidate_decision.route in ("zone_1_craving", "zone_1_contemplation"):
            new_stage, evidence = self.readiness_service.evaluate_transition(
                current_stage=current_readiness,
                message=raw_msg,
                route=candidate_decision.route,
                provider=self.provider,
            )
            if evidence and new_stage != current_readiness:
                self.store.update_readiness(req.conversation_id, new_stage)
                self.store.record_readiness_event(
                    conversation_id=req.conversation_id,
                    from_stage=current_readiness,
                    to_stage=new_stage,
                    evidence=evidence,
                )
                current_readiness = new_stage

        # 6. Final Zone Routing with Updated Readiness Stage
        decision = self.router.route_message(
            canonical_text=canonical_msg,
            readiness_stage=current_readiness,
            location_chip=req.client_context.location_chip,
        )
        policy_act = "SAFE_REDIRECT" if decision.route == "zone_3_out_of_scope" else "ALLOW"

        # 7. Tone Mirroring Classifier (ADR 04)
        detected_tone = detect_tone(raw_msg)
        if detected_tone != "standard" or current_tone == "standard":
            current_tone = detected_tone
            self.store.update_tone(req.conversation_id, current_tone)

        # 8. Assemble Prompt & Context Window via MemoryService (ADR 02)
        context_notes, history_for_llm = self.memory_service.build_context_window(
            old_summary=old_summary,
            past_messages=past_msgs,
            current_msg=raw_msg,
            limit=6,
        )
        sys_prompt = build_system_prompt(
            route=decision.route,
            readiness_stage=current_readiness,
            tone=current_tone,
            context_notes=context_notes,
        )

        # 9. LLM Provider Generation with Zero-Crash Fallback (T1 #3)
        gen_result = self.provider.generate(
            system_prompt=sys_prompt,
            messages=history_for_llm,
        )

        # 10. Output Guardrail (KEEP / SANITIZE / REPLACE) (T5 #6)
        filtered_reply, _ = self.guardrail.filter_output(gen_result.text)

        # 11. Update Rolling Summary & Persistent Storage via MemoryService
        new_summary = self.memory_service.update_rolling_summary(
            old_summary=old_summary,
            raw_msg=raw_msg,
            current_readiness=current_readiness,
            current_tone=current_tone,
            route=decision.route,
        )
        merged_tags = self.memory_service.merge_tags(
            existing_tags=conv.get("context_tags", {}),
            new_tags=decision.suggested_tags,
        )
        self.store.update_summary_and_tags(
            conversation_id=req.conversation_id,
            summary=new_summary,
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
            raw_content=filtered_reply,
            canonical_content=filtered_reply,
            route=decision.route,
            policy_action=policy_act,
        )

        return ChatResponse(
            conversation_id=req.conversation_id,
            reply=filtered_reply,
            route=decision.route,
            intent=decision.intent,
            readiness_stage=current_readiness,
            policy_action=policy_act,
            memory=MemoryInfo(updated=True, context_tags=decision.suggested_tags),
            provider=ProviderInfo(
                name=gen_result.provider_name,
                fallback_used=gen_result.fallback_used,
            ),
        )
