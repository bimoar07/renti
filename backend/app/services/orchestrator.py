"""Orchestrator - urutan pemrosesan pesan chatbot.

MVP Hari 1: memakai logika deterministik (mock) tanpa LLM sungguhan.
Hari 2+: memori SQLite + policy engine. Hari 7: provider LiteLLM (Gemini/Groq).

Alur (lihat docs/decisions/README.md):
raw -> canonicalize -> safety/policy -> memory -> extract -> route -> generate -> guardrail
"""
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    MemoryInfo,
    ProviderInfo,
    ReadinessStage,
)

# Track conversations secara in-memory utk MVP. (Hari 2: pindah ke sqlite_store.py)
_conversations: dict[str, dict] = {}
_messages: dict[str, list[dict]] = {}


class Orchestrator:
    def create_conversation(self, conversation_id: str, user_id: str, readiness: ReadinessStage) -> None:
        _conversations[conversation_id] = {"user_id": user_id, "readiness_stage": readiness, "summary": ""}
        _messages[conversation_id] = []

    def conversation_exists(self, conversation_id: str) -> bool:
        return conversation_id in _conversations

    def process(self, req: ChatRequest) -> ChatResponse:
        conv = _conversations[req.conversation_id]
        _messages[req.conversation_id].append({"role": "user", "content": req.message})

        # --- Mock STUB (diganti policy engine + provider pada hari berikutnya) ---
        msg = req.message.lower()

        # Crisis / self-harm: prioritas tertinggi (ADR 12)
        if any(k in msg for k in ("bunuh", "menyakiti diri", "mau mati")):
            resp = ChatResponse(
                conversation_id=req.conversation_id,
                reply=(
                    "Aku ikut prihatin. Jika kamu dalam bahaya atau ingin menyakiti diri, "
                    "segera hubungi layanan darurat 119 atau orang tepercaya di dekatmu."
                ),
                route="crisis",
                intent="crisis_support",
                readiness_stage="action",
                policy_action="BLOCK_AND_SIGNPOST",
                memory=MemoryInfo(updated=False),
                provider=ProviderInfo(name="policy_fallback", fallback_used=True),
            )
        # Refuge/social refusal
        elif any(k in msg for k in ("tolak", "ajakan", "disuruh", "nongkrong")):
            resp = ChatResponse(
                conversation_id=req.conversation_id,
                reply=(
                    "Coba bilang: 'Gak dulu bro, paru-paru gua lagi minta rehat nih, es teh aja gua mah.' "
                    "Mau kubuatkan 3 opsi penolakan lain?"
                ),
                route="refusal_script",
                intent="social_refusal",
                readiness_stage=conv["readiness_stage"],
                policy_action="ALLOW",
                memory=MemoryInfo(updated=True, context_tags={"trigger": "social"}),
                provider=ProviderInfo(name="mock"),
            )
        # Zone 1: craving / ingin merokok (Action)
        elif any(k in msg for k in ("ngerokok", "ingin rokok", "craving", "vape", "ngidam")):
            resp = ChatResponse(
                conversation_id=req.conversation_id,
                reply=(
                    "Gue paham, craving bisa terasa kuat. Yuk lewati beberapa menit pertama "
                    "dulu dengan napas pelan 4-7-8 dan urge surfing."
                ),
                route="zone_1_craving",
                intent="cessation_support",
                readiness_stage=conv["readiness_stage"],
                policy_action="ALLOW",
                memory=MemoryInfo(updated=True, context_tags={"trigger": "craving"}),
                provider=ProviderInfo(name="mock"),
            )
        # Zone 3: out of scope
        else:
            resp = ChatResponse(
                conversation_id=req.conversation_id,
                reply=(
                    "Sebagai AI Companion Renti, aku didesain khusus mendampingi perjalanan "
                    "berhenti merokok/vaping. Ada yang bisa kubantu soal itu?"
                ),
                route="zone_3_out_of_scope",
                intent="out_of_scope",
                readiness_stage=conv["readiness_stage"],
                policy_action="SAFE_REDIRECT",
                memory=MemoryInfo(updated=True),
                provider=ProviderInfo(name="mock"),
            )

        _messages[req.conversation_id].append({"role": "assistant", "content": resp.reply})
        return resp
