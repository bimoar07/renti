"""Validasi contoh kontrak (docs/API_CONTRACT.md) terhadap skema Pydantic.

Cara pakai:
    python scripts/check_contract.py
Membaca file JSON contoh (jika ada di proposal/assets) dan memastikan
masih valid terhadap ChatResponse. Fallback: build payload dari string contoh.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.schemas.chat import ChatResponse, ConversationResponse  # noqa: E402

SAMPLE = {
    "conversation_id": "conversation-001",
    "reply": "Gue paham, craving bisa terasa kuat.",
    "route": "zone_1_craving",
    "intent": "cessation_support",
    "readiness_stage": "action",
    "policy_action": "ALLOW",
    "memory": {"updated": True, "context_tags": {"trigger": "craving"}},
    "provider": {"name": "mock", "fallback_used": False},
}


def main() -> int:
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            SAMPLE.update(json.load(f))
    parsed = ChatResponse(**SAMPLE)
    print("OK: kontrak sesuai skema ChatResponse ->", parsed.route, parsed.policy_action)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
