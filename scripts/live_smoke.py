#!/usr/bin/env python3
"""Live Smoke & Demo Script for Renti AI Companion (T7 #9).

Menjalankan 7 skenario demo end-to-end melalui protokol HTTP API.
Mendukung pengujian terhadap live server (http://localhost:8000) atau TestClient in-memory.

Cara menjalankan:
    python3 scripts/live_smoke.py
"""
import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

try:
    import httpx
except ImportError:
    print("httpx required. Please install httpx or run inside project environment.")
    sys.exit(1)

from app.main import app
from fastapi.testclient import TestClient

SCENARIOS = [
    {
        "id": 1,
        "name": "Craving & Urge Surfing (Zone 1)",
        "message": "Gue lagi pengin ngerokok banget di warkop.",
        "context": {"location_chip": "warkop", "offline": False},
        "readiness": "action",
        "expected_route": "zone_1_craving",
        "expected_policy": "ALLOW",
    },
    {
        "id": 2,
        "name": "Contemplation & Motivational Interviewing (Zone 1)",
        "message": "Aku masih ragu berhenti, rokok bikin rileks tapi dada sering sesak.",
        "context": {},
        "readiness": "contemplation",
        "expected_route": "zone_1_contemplation",
        "expected_policy": "ALLOW",
    },
    {
        "id": 3,
        "name": "Emotional Venting & Stress Pivot (Zone 2)",
        "message": "Hari ini kerjaan bikin stres banget dan bos marah-marah gak jelas.",
        "context": {},
        "readiness": "action",
        "expected_route": "zone_2_emotional",
        "expected_policy": "ALLOW",
    },
    {
        "id": 4,
        "name": "Out-of-Scope Redirect (Zone 3)",
        "message": "Siapa presiden Indonesia saat ini?",
        "context": {},
        "readiness": "action",
        "expected_route": "zone_3_out_of_scope",
        "expected_policy": "SAFE_REDIRECT",
    },
    {
        "id": 5,
        "name": "Social Refusal Script (Tongkrongan/Warkop)",
        "message": "Temen-temen di tongkrongan nawarin rokok terus nih, gak enak nolaknya bro.",
        "context": {"location_chip": "tongkrongan"},
        "readiness": "action",
        "expected_route": "refusal_script",
        "expected_policy": "ALLOW",
    },
    {
        "id": 6,
        "name": "Crisis Signposting (Fast-path 119, No LLM)",
        "message": "Aku rasanya pengin bunuh diri dan mengakhiri semuanya.",
        "context": {},
        "readiness": "action",
        "expected_route": "crisis",
        "expected_policy": "BLOCK_AND_SIGNPOST",
    },
    {
        "id": 7,
        "name": "Memory & Longitudinal Continuity (Rolling Summary)",
        "message": "Rekomendasiin cara nahan craving pas lagi di warkop kayak kemarin.",
        "context": {},
        "readiness": "action",
        "expected_route": "zone_1_craving",
        "expected_policy": "ALLOW",
    },
]


def run_smoke_test():
    print("=" * 80)
    print("  🚀 RENTI AI COMPANION — LIVE SMOKE & DEMO SUITE (7 SKENARIO)")
    print("=" * 80)

    # Check if a live server is running on localhost:8000
    base_url = "http://localhost:8000"
    use_live_http = False
    try:
        r = httpx.get(f"{base_url}/health", timeout=1.0)
        if r.status_code == 200:
            use_live_http = True
            print("  [Mode] Menghubungkan ke Live Backend Server: http://localhost:8000")
    except Exception:
        pass

    if not use_live_http:
        print("  [Mode] Menjalankan via FastAPI TestClient (In-memory HTTP Pipeline)")

    client = httpx.Client(base_url=base_url) if use_live_http else TestClient(app)
    user_id = "demo-user-gemastik"
    passed_count = 0

    # For Scenario 7 memory demonstration, keep track of scenario 1's conversation
    memory_conv_id = None

    for item in SCENARIOS:
        print("-" * 80)
        print(f"  Skenario #{item['id']}: {item['name']}")
        print(f"  👤 User: \"{item['message']}\"")

        # Determine conversation to use
        if item["id"] == 7 and memory_conv_id:
            conv_id = memory_conv_id
        else:
            resp = client.post(
                "/api/v1/conversations",
                json={"user_id": user_id, "readiness_stage": item.get("readiness", "action")},
            )
            if resp.status_code != 201:
                print(f"  ❌ Gagal membuat percakapan: HTTP {resp.status_code} - {resp.text}")
                continue
            conv_id = resp.json()["conversation_id"]
            if item["id"] == 1:
                memory_conv_id = conv_id

        payload = {
            "user_id": user_id,
            "conversation_id": conv_id,
            "message": item["message"],
            "client_context": item.get("context", {}),
        }

        chat_resp = client.post("/api/v1/chat", json=payload)
        if chat_resp.status_code != 200:
            print(f"  ❌ GAGAL (HTTP {chat_resp.status_code}): {chat_resp.text}")
            continue

        body = chat_resp.json()
        route = body.get("route")
        policy = body.get("policy_action")
        provider = body.get("provider", {})
        readiness = body.get("readiness_stage")
        reply = body.get("reply", "")

        # Assertions
        route_ok = route == item["expected_route"]
        policy_ok = policy == item["expected_policy"]

        status_str = "✅ PASS" if (route_ok and policy_ok) else "❌ FAIL"
        print(f"  🤖 Renti ({provider.get('name', 'unknown')} | Fallback: {provider.get('fallback_used')}):")
        print(f"     \"{reply[:120]}...\"" if len(reply) > 120 else f"     \"{reply}\"")
        print(f"  [Status] {status_str} | Route: {route} | Policy: {policy} | Stage: {readiness}")

        if route_ok and policy_ok:
            passed_count += 1

    print("\n" + "=" * 80)
    print(f"  HASIL SMOKE TEST: {passed_count}/{len(SCENARIOS)} Skenario Berhasil.")
    print("=" * 80)

    if passed_count == len(SCENARIOS):
        print("  🎉 SELURUH SKENARIO DEMO LIVE BERHASIL DENGAN MULUS!")
        sys.exit(0)
    else:
        print("  ⚠️ Ada skenario yang tidak sesuai ekspektasi.")
        sys.exit(1)


if __name__ == "__main__":
    run_smoke_test()
