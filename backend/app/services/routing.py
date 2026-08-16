"""Zone and Intent Routing Service (ADR 10).

Routes incoming safe messages into 3 operational zones and contextual scripts:
- Zone 1: Cessation & Craving (or Contemplation)
- Zone 2: Emotional Venting & Stress Triggers
- Zone 3: Out-of-Scope Topics
- Refusal Script: Social peer pressure & refusal in warkop/tongkrongan
"""
from dataclasses import dataclass
from typing import Optional

from app.schemas.chat import ReadinessStage, ZoneRoute

REFUSAL_KEYWORDS = (
    "tolak",
    "ajakan",
    "disuruh",
    "nongkrong",
    "ditawarin",
    "temen ngerokok",
    "dikasih rokok",
    "ngajak ngerokok",
    "bujuk",
    "gak enak nolak",
)

CRAVING_KEYWORDS = (
    "ngerokok",
    "rokok",
    "vape",
    "craving",
    "ngidam",
    "hisap",
    "pod",
    "liquid",
    "kebul",
    "tarikan",
    "pengin ngisap",
    "candu",
    "nikotin",
)

EMOTIONAL_KEYWORDS = (
    "stres",
    "stress",
    "capek",
    "marah",
    "sedih",
    "anxiety",
    "cemas",
    "panik",
    "pusing kerjaan",
    "lelah",
    "kecewa",
    "frustasi",
)


@dataclass
class RoutingDecision:
    route: ZoneRoute
    intent: str
    suggested_tags: dict[str, str]


class ZoneRouter:
    def route_message(
        self,
        canonical_text: str,
        readiness_stage: ReadinessStage = "action",
        location_chip: Optional[str] = None,
    ) -> RoutingDecision:
        tags: dict[str, str] = {}
        if location_chip:
            tags["location"] = location_chip

        # 1. Social refusal script in tongkrongan / warkop
        if any(kw in canonical_text for kw in REFUSAL_KEYWORDS):
            tags["trigger"] = "social_peer_pressure"
            return RoutingDecision(
                route="refusal_script",
                intent="social_refusal",
                suggested_tags=tags,
            )

        # 2. Zone 1: Cessation / Craving (Stage-tailored)
        if any(kw in canonical_text for kw in CRAVING_KEYWORDS):
            tags["trigger"] = "craving"
            if readiness_stage in ("contemplation", "precontemplation"):
                return RoutingDecision(
                    route="zone_1_contemplation",
                    intent="contemplation_support",
                    suggested_tags=tags,
                )
            return RoutingDecision(
                route="zone_1_craving",
                intent="cessation_support",
                suggested_tags=tags,
            )

        # 3. Zone 2: Emotional Venting & Stress Triggers
        if any(kw in canonical_text for kw in EMOTIONAL_KEYWORDS):
            tags["trigger"] = "emotional_stress"
            return RoutingDecision(
                route="zone_2_emotional",
                intent="emotional_venting",
                suggested_tags=tags,
            )

        # 4. Zone 3: Out-of-Scope (General conversation / non-smoking topics)
        return RoutingDecision(
            route="zone_3_out_of_scope",
            intent="out_of_scope",
            suggested_tags=tags,
        )
