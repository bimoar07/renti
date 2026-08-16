"""LLM Provider Port and Zero-Crash Fallback Service (Gemini -> Groq -> template).

Implements single entry point generate() for all Day 2 LLM consumers:
1. Conversation reply generation
2. Readiness proposal extraction
3. Rolling summary rollup

Never-raise guarantee: any exception / quota error / timeout / empty response
automatically drops one level down without bubbling up to HTTP 500.

Timeout budget:
- Per-provider timeout (~7s)
- Total deadline budget (~12s) shared across the provider chain.
"""
from dataclasses import dataclass
import logging
import re
import time
from typing import Any, Callable, Optional

try:
    from litellm import completion
except ImportError:
    completion = None  # type: ignore

from app.prompts.companion import generate_fallback_reply

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
        per_provider_timeout: float = 7.0,
        total_deadline: float = 12.0,
        timeout: Optional[float] = None,
        fallback_handler: Optional[Callable[[str, list[dict[str, str]]], str]] = None,
    ):
        self.gemini_api_key = (gemini_api_key or "").strip()
        self.groq_api_key = (groq_api_key or "").strip()
        self.gemini_model = gemini_model
        self.groq_model = groq_model
        if timeout is not None:
            self.per_provider_timeout = timeout
        else:
            self.per_provider_timeout = per_provider_timeout
        self.timeout = self.per_provider_timeout
        self.total_deadline = total_deadline
        self.fallback_handler = fallback_handler

    def generate(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> ProviderResult:
        """Call LLM with Zero-Crash fallback cascade: Gemini -> Groq -> template."""
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        start_time = time.monotonic()
        deadline = start_time + self.total_deadline

        # 1. Try Primary: Gemini
        remaining = deadline - time.monotonic()
        if remaining > 0 and self.gemini_api_key and completion is not None:
            call_timeout = min(self.per_provider_timeout, remaining)
            try:
                call_kwargs = dict(kwargs)
                call_kwargs.pop("timeout", None)
                response = completion(
                    model=self.gemini_model,
                    messages=full_messages,
                    api_key=self.gemini_api_key,
                    timeout=call_timeout,
                    **call_kwargs,
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
        elif self.gemini_api_key and remaining <= 0:
            logger.warning("Total deadline budget exceeded before calling Gemini (%.2fs remaining)", remaining)

        # 2. Try Secondary: Groq
        remaining = deadline - time.monotonic()
        if remaining > 0 and self.groq_api_key and completion is not None:
            call_timeout = min(self.per_provider_timeout, remaining)
            try:
                call_kwargs = dict(kwargs)
                call_kwargs.pop("timeout", None)
                response = completion(
                    model=self.groq_model,
                    messages=full_messages,
                    api_key=self.groq_api_key,
                    timeout=call_timeout,
                    **call_kwargs,
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
        elif self.groq_api_key and remaining <= 0:
            logger.warning("Total deadline budget exceeded before calling Groq (%.2fs remaining)", remaining)

        # 3. Deterministic Fallback (Offline / No Key / All Providers Failed / Deadline Exceeded)
        if self.fallback_handler:
            fallback_text = self.fallback_handler(system_prompt, messages)
        else:
            fallback_text = self._default_fallback(system_prompt, messages)

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

    def _default_fallback(
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

        # Structured JSON Readiness extraction
        if "ekstraksi klinis" in sp_lower or "proposed_stage" in sp_lower or "keluarkan hanya format json" in sp_lower:
            current_match = re.search(r"tahap saat ini:\s*(\w+)", sp_lower)
            cur = current_match.group(1) if current_match else "contemplation"

            if "2 hari" in last_msg or "sudah berhenti" in last_msg or "nggak ngerokok sama sekali" in last_msg or "tidak merokok sama sekali" in last_msg:
                return '{"proposed_stage": "action", "evidence": "Pengguna melaporkan sudah mulai berhenti merokok."}'
            if "kambuh" in last_msg or "kemarin ngerokok" in last_msg or "udah ngerokok lagi" in last_msg or "sudah ngerokok lagi" in last_msg or "khilaf" in last_msg:
                return '{"proposed_stage": "relapse", "evidence": "Pengguna melaporkan merokok kembali."}'
            if ("mikirin berhenti" in last_msg or "mau coba" in last_msg or "kepikiran" in last_msg) and cur == "precontemplation":
                return '{"proposed_stage": "contemplation", "evidence": "Pengguna mulai menimbang untuk berhenti."}'

            return f'{{"proposed_stage": "{cur}", "evidence": "Tahap kesiapan pengguna dipertahankan."}}'

        # Detect zone from prompt
        if "refusal script" in sp_lower or "tugas utama (refusal" in sp_lower:
            return generate_fallback_reply("refusal_script", last_msg)
        if "fokus zone 1 (craving" in sp_lower:
            return generate_fallback_reply("zone_1_craving", last_msg)
        if "fokus zone 1 (motivational" in sp_lower:
            return generate_fallback_reply("zone_1_contemplation", last_msg)
        if "fokus zone 2" in sp_lower:
            return generate_fallback_reply("zone_2_emotional", last_msg)
        if "fokus zone 3" in sp_lower:
            return generate_fallback_reply("zone_3_out_of_scope", last_msg)

        return generate_fallback_reply("default", last_msg)


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
