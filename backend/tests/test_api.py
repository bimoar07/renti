"""Tests untuk endpoint & kontrak API (unittest, tanpa LLM sungguhan)."""
import unittest

from fastapi.testclient import TestClient

from app.main import app


class ChatApiTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def _make_conversation(self, readiness="action"):
        r = self.client.post("/api/v1/conversations", json={"user_id": "u1", "readiness_stage": readiness})
        self.assertEqual(r.status_code, 201)
        return r.json()["conversation_id"]

    def test_health(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "ok")

    def test_chat_craving_returns_zone_1(self):
        cid = self._make_conversation()
        r = self.client.post(
            "/api/v1/chat",
            json={
                "user_id": "u1",
                "conversation_id": cid,
                "message": "Gue lagi pengin ngerokok banget di warkop.",
                "client_context": {"location_chip": "warkop", "offline": False},
            },
        )
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["route"], "zone_1_craving")
        self.assertEqual(body["policy_action"], "ALLOW")
        self.assertIn("conversation_id", body)
        self.assertIn("reply", body)

    def test_chat_crisis_blocks_and_signposts(self):
        cid = self._make_conversation()
        r = self.client.post(
            "/api/v1/chat",
            json={"user_id": "u1", "conversation_id": cid, "message": "Aku mau bunuh diri."},
        )
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["policy_action"], "BLOCK_AND_SIGNPOST")
        self.assertEqual(body["route"], "crisis")

    def test_chat_out_of_scope_redirects(self):
        cid = self._make_conversation()
        r = self.client.post(
            "/api/v1/chat",
            json={"user_id": "u1", "conversation_id": cid, "message": "Berapa hasil 2+2?"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["route"], "zone_3_out_of_scope")
        self.assertEqual(r.json()["policy_action"], "SAFE_REDIRECT")

    def test_chat_requires_existing_conversation(self):
        r = self.client.post(
            "/api/v1/chat",
            json={"user_id": "u1", "conversation_id": "nope", "message": "halo"},
        )
        self.assertEqual(r.status_code, 404)

    def test_invalid_payload_returns_422(self):
        r = self.client.post("/api/v1/chat", json={"user_id": ""})
        self.assertEqual(r.status_code, 422)


if __name__ == "__main__":
    unittest.main()
