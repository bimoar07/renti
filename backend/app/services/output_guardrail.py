"""Deterministic Output Guardrail Service (KEEP/SANITIZE/REPLACE) (ADR 09, 11, 13).

Filters LLM-generated responses before sending to the user:
- KEEP: Response is safe as-is.
- SANITIZE: Response contains clinical diagnosis/medical prescription claims -> appends psychoeducation disclaimer.
- REPLACE: Response leaks system prompt/instructions -> replaces with safe canned response.

Crucial guarantee: Never modifies policy_action — only transforms reply text.
"""
import re
from typing import Literal

GuardrailAction = Literal["KEEP", "SANITIZE", "REPLACE"]

MEDICAL_CLAIM_PATTERNS = [
    r"\bterdiagnosis\b",
    r"\bmendiagnosis\b",
    r"\bdiagnosis medis\b",
    r"\bmeresepkan\b",
    r"\bresep obat\b",
    r"\bvarenicline\b",
    r"\bbupropion\b",
    r"\bnikotin tempel dosis\b",
    r"\bdosis \d+\s*(mg|miligram)\b",
    r"\bminum obat\b",
]

PROMPT_LEAK_PATTERNS = [
    r"system prompt\b",
    r"my instructions are\b",
    r"as an ai system prompt\b",
    r"aturan internal renti\b",
    r"ignore previous instructions\b",
    r"reveal the system instructions\b",
    r"system instructions:\b",
]

MEDICAL_DISCLAIMER = (
    "\n\n*Catatan: Renti adalah teman pendamping psikoedukasi dan bukan pengganti diagnosis, "
    "konseling medis, atau resep profesional. Untuk penanganan medis lebih lanjut, silakan konsultasikan "
    "dengan dokter atau fasilitas kesehatan terdekat.*"
)

SAFE_REPLACEMENT_REPLY = (
    "Aku di sini sebagai teman pendamping di Renti untuk mendampingimu melewati proses berhenti merokok dan vaping. "
    "Ada hal seputar pemicu, craving, atau rencanamu hari ini yang ingin kita diskusikan bersama?"
)


class OutputGuardrail:
    def __init__(self) -> None:
        self._medical_regex = re.compile("|".join(MEDICAL_CLAIM_PATTERNS), re.IGNORECASE)
        self._leak_regex = re.compile("|".join(PROMPT_LEAK_PATTERNS), re.IGNORECASE)

    def filter_output(self, reply: str) -> tuple[str, GuardrailAction]:
        """Evaluate generated text and apply KEEP, SANITIZE, or REPLACE."""
        if not reply or not reply.strip():
            return SAFE_REPLACEMENT_REPLY, "REPLACE"

        # 1. Check prompt leak / instruction compromise (REPLACE)
        if self._leak_regex.search(reply):
            return SAFE_REPLACEMENT_REPLY, "REPLACE"

        # 2. Check clinical medical claims (SANITIZE)
        if self._medical_regex.search(reply):
            sanitized = f"{reply.strip()}{MEDICAL_DISCLAIMER}"
            return sanitized, "SANITIZE"

        # 3. Safe response (KEEP)
        return reply, "KEEP"
