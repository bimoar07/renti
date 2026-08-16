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
        self.assertEqual(body["memory"]["context_tags"]["location"], "warkop")

    def test_chat_contemplation_stage_routing(self):
        cid = self._make_conversation(readiness="contemplation")
        r = self.client.post(
            "/api/v1/chat",
            json={
                "user_id": "u1",
                "conversation_id": cid,
                "message": "Pengin ngerokok lagi tapi masih galau.",
            },
        )
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["route"], "zone_1_contemplation")
        self.assertEqual(body["policy_action"], "ALLOW")

    def test_chat_emotional_venting(self):
        cid = self._make_conversation()
        r = self.client.post(
            "/api/v1/chat",
            json={
                "user_id": "u1",
                "conversation_id": cid,
                "message": "Stres banget hari ini banyak masalah.",
            },
        )
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["route"], "zone_2_emotional")
        self.assertEqual(body["policy_action"], "ALLOW")

    def test_chat_refusal_script(self):
        cid = self._make_conversation()
        r = self.client.post(
            "/api/v1/chat",
            json={
                "user_id": "u1",
                "conversation_id": cid,
                "message": "Gimana cara tolak ajakan rokok di tongkrongan?",
            },
        )
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["route"], "refusal_script")
        self.assertEqual(body["intent"], "social_refusal")
        self.assertEqual(body["policy_action"], "ALLOW")

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
        self.assertIn("119", body["reply"])

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
        body = r.json()
        self.assertIn("detail", body)
        self.assertIsInstance(body["detail"], dict)
        self.assertEqual(body["detail"]["code"], "not_found")
        self.assertIn("message", body["detail"])

    def test_invalid_payload_returns_422(self):
        r = self.client.post("/api/v1/chat", json={"user_id": ""})
        self.assertEqual(r.status_code, 422)
        body = r.json()
        self.assertIn("detail", body)

    def test_bad_request_returns_structured_400(self):
        from unittest.mock import patch
        from fastapi import HTTPException

        cid = self._make_conversation()
        with patch("app.api.routes_chat._orchestrator.process", side_effect=HTTPException(status_code=400, detail="bad request payload")):
            r = self.client.post(
                "/api/v1/chat",
                json={"user_id": "u1", "conversation_id": cid, "message": "halo"},
            )
            self.assertEqual(r.status_code, 400)
            body = r.json()
            self.assertIn("detail", body)
            self.assertIsInstance(body["detail"], dict)
            self.assertEqual(body["detail"]["code"], "bad_request")
            self.assertEqual(body["detail"]["message"], "bad request payload")

    def test_unhandled_exception_returns_structured_500(self):
        from unittest.mock import patch

        cid = self._make_conversation()
        with patch("app.api.routes_chat._orchestrator.process", side_effect=RuntimeError("secret db connection failure")):
            client = TestClient(app, raise_server_exceptions=False)
            r = client.post(
                "/api/v1/chat",
                json={"user_id": "u1", "conversation_id": cid, "message": "halo"},
            )
            self.assertEqual(r.status_code, 500)
            body = r.json()
            self.assertIn("detail", body)
            self.assertIsInstance(body["detail"], dict)
            self.assertEqual(body["detail"]["code"], "internal_error")
            self.assertIn("message", body["detail"])
            # Pastikan pesan raw/sensitif tidak bocor ke client
            self.assertNotIn("secret db connection failure", r.text)


if __name__ == "__main__":
    unittest.main()
