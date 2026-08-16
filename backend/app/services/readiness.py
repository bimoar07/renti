"""Readiness Hybrid Service and MAPR Transition Validator (ADR 06, 13).

Evaluates user readiness stage transitions via hybrid architecture:
1. LLM Extractor proposes {proposed_stage, evidence} structured JSON
2. Deterministic MAPR Validator enforces legal stage transitions and requires evidence
3. Only safe turns in Zone 1 (zone_1_craving, zone_1_contemplation) are eligible for transition.
"""
import json
import logging
import re
from typing import Optional

from app.schemas.chat import ReadinessStage, ZoneRoute
from app.services.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

# Legal MAPR Transition Matrix
LEGAL_TRANSITIONS: dict[ReadinessStage, set[ReadinessStage]] = {
    "precontemplation": {"precontemplation", "contemplation"},
    "contemplation": {"contemplation", "action", "relapse"},
    "action": {"action", "maintenance", "relapse", "contemplation"},
    "maintenance": {"maintenance", "relapse"},
    "relapse": {"relapse", "contemplation", "action"},
}


def validate_mapr_transition(
    from_stage: ReadinessStage,
    to_stage: ReadinessStage,
    evidence: str,
) -> bool:
    """Deterministic validation of MAPR transition rules.

    - Must follow legal adjacent transitions (no skips)
    - Non-empty evidence required for any stage shift
    """
    if from_stage == to_stage:
        return True

    if not evidence or not evidence.strip():
        return False

    allowed_targets = LEGAL_TRANSITIONS.get(from_stage, set())
    return to_stage in allowed_targets


class ReadinessService:
    def evaluate_transition(
        self,
        current_stage: ReadinessStage,
        message: str,
        route: ZoneRoute,
        provider: LLMProvider,
        deadline: Optional[float] = None,
    ) -> tuple[ReadinessStage, Optional[str]]:
        """Evaluate readiness stage transition for incoming message.

        Returns (new_stage, evidence) if a valid legal transition occurred,
        or (current_stage, None) if no transition happened.
        """
        # Transitions are ONLY evaluated on Zone 1 turns (ADR 06)
        if route not in ("zone_1_craving", "zone_1_contemplation"):
            return current_stage, None

        extractor_system_prompt = (
            "Kamu adalah sistem ekstraksi klinis tahap kesiapan berhenti merokok (MAPR Framework).\n"
            "Tugasmu: Analisis pesan pengguna dan tentukan apakah tahap kesiapan berubah.\n"
            "Tahap yang valid: precontemplation, contemplation, action, maintenance, relapse.\n"
            f"Tahap saat ini: {current_stage}\n\n"
            "Keluarkan HANYA format JSON valid:\n"
            '{"proposed_stage": "<stage>", "evidence": "<alasan/kutipan singkat pesan pengguna>"}'
        )

        res = provider.generate(
            system_prompt=extractor_system_prompt,
            messages=[{"role": "user", "content": message}],
            deadline=deadline,
        )

        proposed_stage, evidence = self._parse_proposal(res.text, current_stage)

        if proposed_stage != current_stage:
            is_valid = validate_mapr_transition(current_stage, proposed_stage, evidence)
            if is_valid:
                return proposed_stage, evidence
            logger.info(
                "Rejected illegal readiness transition %s -> %s (evidence: %s)",
                current_stage, proposed_stage, evidence
            )

        return current_stage, None

    def _parse_proposal(self, raw_text: str, current_stage: ReadinessStage) -> tuple[ReadinessStage, str]:
        """Safely parse structured JSON from LLM output."""
        try:
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                proposed = data.get("proposed_stage", "").strip().lower()
                evidence = data.get("evidence", "").strip()
                if proposed in ("precontemplation", "contemplation", "action", "maintenance", "relapse"):
                    return proposed, evidence  # type: ignore
        except Exception as exc:
            logger.warning("Failed to parse readiness JSON proposal: %s", exc)

        return current_stage, ""
