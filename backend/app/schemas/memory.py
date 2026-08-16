"""Memory and domain state schemas (ADR 02, 06, 10)."""
from typing import Literal, Optional
from pydantic import BaseModel, Field

ReadinessStage = Literal["precontemplation", "contemplation", "action", "maintenance", "relapse"]
PolicyAction = Literal["ALLOW", "SAFE_REDIRECT", "CLARIFY", "BLOCK_AND_SIGNPOST"]
ZoneRoute = Literal[
    "zone_1_craving",
    "zone_1_contemplation",
    "zone_2_emotional",
    "zone_3_out_of_scope",
    "refusal_script",
    "crisis",
]


class ClientContext(BaseModel):
    location_chip: Optional[str] = None
    offline: bool = False


class MemoryInfo(BaseModel):
    updated: bool
    context_tags: dict[str, str] = Field(default_factory=dict)


class RollingSummary(BaseModel):
    summary: str = ""
    context_tags: dict[str, str] = Field(default_factory=dict)
    updated_at: Optional[str] = None
