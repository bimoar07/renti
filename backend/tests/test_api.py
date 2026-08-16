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

def test_chat_metadata_logging_structured_json(caplog):
    """Verifikasi bahwa setiap POST /api/v1/chat mencatat 1 baris log terstruktur JSON-lines ke stdout."""
    import json
    import logging

    caplog.set_level(logging.INFO)
    client = TestClient(app)

    # 1. Buat percakapan
    r_conv = client.post("/api/v1/conversations", json={"user_id": "u1", "readiness_stage": "action"})
    assert r_conv.status_code == 201
    cid = r_conv.json()["conversation_id"]

    # 2. Kirim pesan chat
    r_chat = client.post(
        "/api/v1/chat",
        json={
            "user_id": "u1",
            "conversation_id": cid,
            "message": "Gue lagi pengin ngerokok banget di warkop.",
            "client_context": {"location_chip": "warkop", "offline": False},
        },
    )
    assert r_chat.status_code == 200

    # 3. Cari baris log JSON-lines metadata untuk percakapan ini
    metadata_logs = []
    for record in caplog.records:
        msg = record.getMessage().strip()
        if msg.startswith("{") and msg.endswith("}"):
            try:
                data = json.loads(msg)
                if data.get("conversation_id") == cid:
                    metadata_logs.append(data)
            except json.JSONDecodeError:
                pass

    assert len(metadata_logs) == 1, f"Harus ada tepat 1 baris log JSON-lines metadata, ditemukan: {len(metadata_logs)}"
    meta = metadata_logs[0]

    # 4. Verifikasi seluruh 7 field metadata yang disyaratkan
    required_fields = [
        "conversation_id",
        "route",
        "readiness_stage",
        "policy_action",
        "provider",
        "latency_ms",
        "fallback_used",
    ]
    for field in required_fields:
        assert field in meta, f"Field '{field}' harus ada dalam baris log metadata"

    assert meta["conversation_id"] == cid
    assert meta["route"] == "zone_1_craving"
    assert meta["readiness_stage"] == "action"
    assert meta["policy_action"] == "ALLOW"
    assert isinstance(meta["provider"], str) and len(meta["provider"]) > 0
    assert isinstance(meta["latency_ms"], (int, float))
    assert meta["latency_ms"] >= 0
    assert isinstance(meta["fallback_used"], bool)

def test_chat_metadata_logging_privacy_strict(caplog):
    """PRIVASI KETAT: Uji bahwa baris log TIDAK memuat isi raw pesan pengguna dan TIDAK memuat API key."""
    import json
    import logging

    caplog.set_level(logging.INFO)
    client = TestClient(app)

    r_conv = client.post("/api/v1/conversations", json={"user_id": "u1", "readiness_stage": "contemplation"})
    assert r_conv.status_code == 201
    cid = r_conv.json()["conversation_id"]

    sensitive_raw_message = "SENSITIVE_SECRET_RAW_MESSAGE_TOKEN_XYZ_98765"
    sensitive_api_key = "AIzaSyFakeSecretApiKeyToNeverBeLogged12345"

    r_chat = client.post(
        "/api/v1/chat",
        json={
            "user_id": "u1",
            "conversation_id": cid,
            "message": f"Halo {sensitive_raw_message} secret key {sensitive_api_key}",
        },
    )
    assert r_chat.status_code == 200

    # Ambil baris log JSON-lines
    matching_records = [
        record.getMessage().strip()
        for record in caplog.records
        if cid in record.getMessage()
    ]
    assert len(matching_records) >= 1
    log_line = matching_records[-1]

    # Pastikan raw message & API key TIDAK ada sama sekali di string log
    assert sensitive_raw_message not in log_line, "Raw message pengguna tidak boleh ada di log!"
    assert sensitive_api_key not in log_line, "API key tidak boleh ada di log!"
    assert "gemini_api_key" not in log_line
    assert "groq_api_key" not in log_line

    # Pastikan keys dalam JSON-lines tepat 7 field metadata
    meta = json.loads(log_line)
    expected_fields = {
        "conversation_id",
        "route",
        "readiness_stage",
        "policy_action",
        "provider",
        "latency_ms",
        "fallback_used",
    }
    assert set(meta.keys()) == expected_fields

if __name__ == "__main__":
    unittest.main()
