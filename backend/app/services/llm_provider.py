"""LLM Provider Port and Zero-Crash Fallback Service (Gemini -> Groq -> template).

Implements single entry point generate() for all Day 2 LLM consumers:
1. Conversation reply generation
2. Readiness proposal extraction
3. Rolling summary rollup

Never-raise guarantee: any exception / quota error / timeout / empty response
automatically drops one level down without bubbling up to HTTP 500.
"""
from dataclasses import dataclass, field
import logging
from typing import Any, Optional

try:
    from litellm import completion
except ImportError:
    completion = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class ProviderResult:
    text: str
    provider_name: str  # "gemini", "groq", "template", "policy_fallback"
    fallback_used: bool = False


class LLMProvider:
    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        groq_api_key: Optional[str] = None,
        gemini_model: str = "gemini/gemini-2.0-flash",
        groq_model: str = "groq/llama-3.3-70b-versatile",
        timeout: float = 10.0,
    ):
        self.gemini_api_key = (gemini_api_key or "").strip()
        self.groq_api_key = (groq_api_key or "").strip()
        self.gemini_model = gemini_model
        self.groq_model = groq_model
        self.timeout = timeout

    def generate(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> ProviderResult:
        """Call LLM with Zero-Crash fallback cascade: Gemini -> Groq -> template."""
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        # 1. Try Primary: Gemini
        if self.gemini_api_key and completion is not None:
            try:
                response = completion(
                    model=self.gemini_model,
                    messages=full_messages,
                    api_key=self.gemini_api_key,
                    timeout=self.timeout,
                    **kwargs,
                )
                text = self._extract_text(response)
                if text:
                    return ProviderResult(
                        text=text,
                        provider_name="gemini",
                        fallback_used=False,
                    )
                logger.warning("Gemini returned empty response, falling back to Groq")
            except Exception as exc:
                logger.warning("Gemini call failed (%s), falling back to Groq", exc)

        # 2. Try Secondary: Groq
        if self.groq_api_key and completion is not None:
            try:
                response = completion(
                    model=self.groq_model,
                    messages=full_messages,
                    api_key=self.groq_api_key,
                    timeout=self.timeout,
                    **kwargs,
                )
                text = self._extract_text(response)
                if text:
                    return ProviderResult(
                        text=text,
                        provider_name="groq",
                        fallback_used=True,
                    )
                logger.warning("Groq returned empty response, falling back to template")
            except Exception as exc:
                logger.warning("Groq call failed (%s), falling back to template", exc)

        # 3. Deterministic Template Fallback (Offline / No Key / All Providers Failed)
        fallback_text = self._generate_template_fallback(system_prompt, messages)
        return ProviderResult(
            text=fallback_text,
            provider_name="template",
            fallback_used=True,
        )

    def _extract_text(self, response: Any) -> str:
        try:
            if hasattr(response, "choices") and response.choices:
                choice = response.choices[0]
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    return (choice.message.content or "").strip()
                if isinstance(choice, dict):
                    return (choice.get("message", {}).get("content") or "").strip()
            elif isinstance(response, dict) and "choices" in response:
                choices = response["choices"]
                if choices:
                    return (choices[0].get("message", {}).get("content") or "").strip()
        except Exception as exc:
            logger.warning("Failed to extract content from completion response: %s", exc)
        return ""

    def _generate_template_fallback(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> str:
        last_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_msg = m.get("content", "").lower()
                break

        sp_lower = system_prompt.lower()

        # 1. Structured JSON Readiness extraction
        if "ekstraksi klinis" in sp_lower or "proposed_stage" in sp_lower or "keluarkan hanya format json" in sp_lower:
            if "2 hari" in last_msg or "berhenti" in last_msg or "nggak ngerokok" in last_msg or "tidak merokok" in last_msg:
                return '{"proposed_stage": "action", "evidence": "Pengguna melaporkan sudah mulai berhenti merokok."}'
            if "kambuh" in last_msg or "ngerokok lagi" in last_msg or "batal" in last_msg:
                return '{"proposed_stage": "relapse", "evidence": "Pengguna melaporkan merokok kembali."}'
            return '{"proposed_stage": "contemplation", "evidence": "Pengguna masih berdiskusi seputar keinginan berhenti."}'

        # 2. Refusal script
        if "refusal script" in sp_lower or "tugas utama (refusal" in sp_lower:
            return (
                "1. 'Gak dulu bro, paru-paru gue lagi minta rehat nih, es teh aja.'\n"
                "2. 'Santai, gue lagi rehat ngerokok dulu hari ini.'\n"
                "3. 'Thanks tawarannya, tapi lagi fokus ngurangin nikotin nih.'"
            )

        # 3. Zone 1: Craving & Urge Surfing
        if "fokus zone 1 (craving" in sp_lower:
            return (
                "Gue paham banget, rasa craving ini bisa terasa sangat kuat tapi sifatnya seperti ombak yang akan surut dalam beberapa menit. "
                "Yuk coba teknik napas 4-7-8 dulu selama 1-2 menit untuk melewati puncak dorongannya."
            )

        # 4. Zone 1: Contemplation & Motivational Interviewing
        if "fokus zone 1 (motivational" in sp_lower:
            return (
                "Wajar banget kalau kamu merasa ragu atau menimbang-nimbang antara kenyamanan merokok dengan keinginan hidup lebih sehat. "
                "Menurutmu, apa hal paling berat saat memikirkan untuk berhenti?"
            )

        # 5. Zone 2: Emotional Venting & Pivot
        if "fokus zone 2" in sp_lower:
            return (
                "Pasti berat banget rasanya menghadapi situasi yang bikin stres begini. Wajar kalau pikiran langsung mencari pelarian ke rokok/vape. "
                "Apakah saat ini kamu lagi merasakan dorongan kuat untuk merokok?"
            )

        # 6. Zone 3: Out-of-scope Redirect
        if "fokus zone 3" in sp_lower:
            return (
                "Sebagai AI Companion di Renti, aku didesain khusus mendampingi perjalanan berhenti merokok dan vaping. "
                "Ada yang bisa kubantu seputar pemicu atau rencanamu berhenti merokok hari ini?"
            )

        # Default companion response
        return (
            "Sebagai teman pendamping di Renti, aku siap mendengarkan dan membantumu melewati proses ini langkah demi langkah. "
            "Apa yang sedang kamu rasakan saat ini?"
        )


class RecordingProvider(LLMProvider):
    """Test stub that records all generate() calls and returns configured or template response."""

    def __init__(
        self,
        canned_response: Optional[str] = None,
        provider_name: str = "template",
        fallback_used: bool = False,
    ):
        super().__init__()
        self.canned_response = canned_response
        self.stub_provider_name = provider_name
        self.stub_fallback_used = fallback_used
        self.history: list[dict[str, Any]] = []

    def generate(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> ProviderResult:
        self.history.append({
            "system_prompt": system_prompt,
            "messages": messages,
            "kwargs": kwargs,
        })
        if self.canned_response is not None:
            return ProviderResult(
                text=self.canned_response,
                provider_name=self.stub_provider_name,
                fallback_used=self.stub_fallback_used,
            )
        return super().generate(system_prompt, messages, **kwargs)
