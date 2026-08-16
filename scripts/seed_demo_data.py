#!/usr/bin/env python3
"""Seed Demo Data Script for Renti AI Companion (T4 #15).

Membuat user contoh demo-user-001 dengan 1-2 percakapan siap pakai via HTTP API:
1. Percakapan stage 'contemplation' (adegan Motivational Interviewing)
2. Percakapan stage 'action' (adegan craving & urge surfing di warkop)

Dapat dijalankan langsung terhadap server yang aktif atau digunakan di test suite.
"""
import argparse
import sys
from typing import Any, Dict, Optional

try:
    import httpx
except ImportError:
    print("httpx required. Please install httpx or activate backend .venv.")
    sys.exit(1)


def seed_demo_data(
    base_url: str = "http://127.0.0.1:8000",
    user_id: str = "demo-user-001",
    client: Optional[Any] = None,
) -> Dict[str, Any]:
    """Seed demo user and conversations via HTTP API."""
    should_close = False
    if client is None:
        client = httpx.Client(base_url=base_url, timeout=15.0)
        should_close = True

    try:
        # 1. Health check verification
        health_resp = client.get("/health")
        if health_resp.status_code != 200:
            raise RuntimeError(f"Server health check failed: HTTP {health_resp.status_code}")

        results = {
            "user_id": user_id,
            "conversations": [],
        }

        # 2. Percakapan 1: Adegan Motivational Interviewing (Contemplation)
        conv1_resp = client.post(
            "/api/v1/conversations",
            json={"user_id": user_id, "readiness_stage": "contemplation"},
        )
        if conv1_resp.status_code != 201:
            raise RuntimeError(f"Gagal membuat conversation 1: HTTP {conv1_resp.status_code} - {conv1_resp.text}")
        conv1_id = conv1_resp.json()["conversation_id"]

        chat1_msg = "Aku masih ragu berhenti, rokok bikin rileks tapi dada sering sesak."
        chat1_resp = client.post(
            "/api/v1/chat",
            json={
                "user_id": user_id,
                "conversation_id": conv1_id,
                "message": chat1_msg,
                "client_context": {},
            },
        )
        if chat1_resp.status_code != 200:
            raise RuntimeError(f"Gagal mengirim pesan chat 1: HTTP {chat1_resp.status_code} - {chat1_resp.text}")
        chat1_data = chat1_resp.json()

        results["conversations"].append({
            "id": conv1_id,
            "scene": "Motivational Interviewing (Contemplation)",
            "readiness_stage": "contemplation",
            "prompt": chat1_msg,
            "reply": chat1_data.get("reply", ""),
            "route": chat1_data.get("route", ""),
            "policy_action": chat1_data.get("policy_action", ""),
        })

        # 3. Percakapan 2: Adegan Craving & Urge Surfing (Action)
        conv2_resp = client.post(
            "/api/v1/conversations",
            json={"user_id": user_id, "readiness_stage": "action"},
        )
        if conv2_resp.status_code != 201:
            raise RuntimeError(f"Gagal membuat conversation 2: HTTP {conv2_resp.status_code} - {conv2_resp.text}")
        conv2_id = conv2_resp.json()["conversation_id"]

        chat2_msg = "Gue lagi pengin ngerokok banget di warkop."
        chat2_resp = client.post(
            "/api/v1/chat",
            json={
                "user_id": user_id,
                "conversation_id": conv2_id,
                "message": chat2_msg,
                "client_context": {"location_chip": "warkop", "offline": False},
            },
        )
        if chat2_resp.status_code != 200:
            raise RuntimeError(f"Gagal mengirim pesan chat 2: HTTP {chat2_resp.status_code} - {chat2_resp.text}")
        chat2_data = chat2_resp.json()

        results["conversations"].append({
            "id": conv2_id,
            "scene": "Craving & Urge Surfing (Action)",
            "readiness_stage": "action",
            "prompt": chat2_msg,
            "reply": chat2_data.get("reply", ""),
            "route": chat2_data.get("route", ""),
            "policy_action": chat2_data.get("policy_action", ""),
        })

        return results

    finally:
        if should_close:
            client.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed demo user and conversations for Renti demo.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Base URL of backend server")
    parser.add_argument("--user-id", default="demo-user-001", help="Demo user ID")
    args = parser.parse_args()

    print("=" * 70)
    print(f"  🌱 SEEDING DATA CONTOH DEMO RENTI (User: {args.user_id})")
    print("=" * 70)
    print(f"  Target Server: {args.base_url}")

    try:
        data = seed_demo_data(base_url=args.base_url, user_id=args.user_id)
    except Exception as e:
        print(f"  ❌ Gagal seeding data demo: {e}")
        return 1

    print("\n  ✅ Berhasil membuat 2 percakapan siap pakai untuk demo:")
    for idx, conv in enumerate(data["conversations"], 1):
        print(f"\n  [Percakapan #{idx}] {conv['scene']}")
        print(f"    • Conversation ID : {conv['id']}")
        print(f"    • Readiness Stage : {conv['readiness_stage']}")
        print(f"    • Route           : {conv['route']} ({conv['policy_action']})")
        print(f"    • Pesan User      : \"{conv['prompt']}\"")
        reply_preview = conv['reply'][:100] + "..." if len(conv['reply']) > 100 else conv['reply']
        print(f"    • Balasan AI      : \"{reply_preview}\"")

    print("\n" + "=" * 70)
    print("  🎉 DATA DEMO SIAP DIGUNAKAN DI MOBILE / DEMO SESSION!")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
