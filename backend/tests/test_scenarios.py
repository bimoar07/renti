"""Tests for 7 Vertical Integration Demo Scenarios (T6 #8)."""
import os
import tempfile
import unittest

from app.schemas.chat import ChatRequest, ClientContext
from app.services.llm_provider import RecordingProvider
from app.services.orchestrator import Orchestrator
from app.storage.sqlite_store import SQLiteStore


class TestDemoScenarios(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "test_scenarios.db")
        self.store = SQLiteStore(db_path=self.db_path)
        self.provider = RecordingProvider()
        self.orchestrator = Orchestrator(store=self.store, provider=self.provider)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def _create_conv(self, conv_id: str, stage: str = "action", tone: str = "casual"):
        self.orchestrator.create_conversation(
            conversation_id=conv_id,
            user_id="demo-user",
            readiness=stage,
            tone=tone,
        )

    def test_scenario_1_craving(self):
        conv_id = "conv-craving"
        self._create_conv(conv_id, stage="action", tone="casual")
        req = ChatRequest(
            user_id="demo-user",
            conversation_id=conv_id,
            message="Gue lagi pengin ngerokok banget di warkop.",
            client_context=ClientContext(location_chip="warkop"),
        )
        res = self.orchestrator.process(req)
        self.assertEqual(res.route, "zone_1_craving")
        self.assertEqual(res.intent, "cessation_support")
        self.assertEqual(res.policy_action, "ALLOW")
        self.assertTrue(len(res.reply) > 0)
        self.assertIn("urge", res.reply.lower() + self.provider.history[-1]["system_prompt"].lower())

    def test_scenario_2_contemplation(self):
        conv_id = "conv-contemplation"
        self._create_conv(conv_id, stage="contemplation", tone="standard")
        req = ChatRequest(
            user_id="demo-user",
            conversation_id=conv_id,
            message="Aku masih ragu berhenti, rokok bikin rileks tapi dada sering sesak.",
        )
        res = self.orchestrator.process(req)
        self.assertEqual(res.route, "zone_1_contemplation")
        self.assertEqual(res.intent, "contemplation_support")
        self.assertEqual(res.policy_action, "ALLOW")
        self.assertTrue(len(res.reply) > 0)

    def test_scenario_3_emotional(self):
        conv_id = "conv-emotional"
        self._create_conv(conv_id, stage="action", tone="casual")
        req = ChatRequest(
            user_id="demo-user",
            conversation_id=conv_id,
            message="Hari ini kerjaan bikin stres banget dan bos marah-marah gak jelas.",
        )
        res = self.orchestrator.process(req)
        self.assertEqual(res.route, "zone_2_emotional")
        self.assertEqual(res.intent, "emotional_venting")
        self.assertEqual(res.policy_action, "ALLOW")
        self.assertTrue(len(res.reply) > 0)

    def test_scenario_4_out_of_scope(self):
        conv_id = "conv-oos"
        self._create_conv(conv_id, stage="action", tone="standard")
        req = ChatRequest(
            user_id="demo-user",
            conversation_id=conv_id,
            message="Siapa presiden Indonesia saat ini?",
        )
        res = self.orchestrator.process(req)
        self.assertEqual(res.route, "zone_3_out_of_scope")
        self.assertEqual(res.intent, "out_of_scope")
        self.assertEqual(res.policy_action, "SAFE_REDIRECT")
        self.assertTrue(len(res.reply) > 0)

    def test_scenario_5_refusal_script(self):
        conv_id = "conv-refusal"
        self._create_conv(conv_id, stage="action", tone="casual")
        req = ChatRequest(
            user_id="demo-user",
            conversation_id=conv_id,
            message="Temen-temen di tongkrongan nawarin rokok terus nih, gak enak nolaknya bro.",
        )
        res = self.orchestrator.process(req)
        self.assertEqual(res.route, "refusal_script")
        self.assertEqual(res.intent, "social_refusal")
        self.assertEqual(res.policy_action, "ALLOW")
        self.assertTrue(len(res.reply) > 0)

    def test_scenario_6_crisis_fastpath_no_llm(self):
        conv_id = "conv-crisis"
        self._create_conv(conv_id, stage="action", tone="standard")
        initial_call_count = len(self.provider.history)

        req = ChatRequest(
            user_id="demo-user",
            conversation_id=conv_id,
            message="Aku rasanya pengin bunuh diri dan mengakhiri semuanya sekarang.",
        )
        res = self.orchestrator.process(req)
        self.assertEqual(res.route, "crisis")
        self.assertEqual(res.intent, "crisis_support")
        self.assertEqual(res.policy_action, "BLOCK_AND_SIGNPOST")
        self.assertIn("119", res.reply)
        # Fast-path guarantee: zero LLM provider calls made
        self.assertEqual(len(self.provider.history), initial_call_count)
        self.assertEqual(res.provider.name, "policy_fallback")
        self.assertTrue(res.provider.fallback_used)

    def test_scenario_7_memory_rolling_summary(self):
        conv_id = "conv-memory"
        self._create_conv(conv_id, stage="action", tone="casual")

        # Turn 1
        req1 = ChatRequest(
            user_id="demo-user",
            conversation_id=conv_id,
            message="Kemarin gue pusing kerjaan dan nongkrong di warkop.",
            client_context=ClientContext(location_chip="warkop"),
        )
        res1 = self.orchestrator.process(req1)
        self.assertEqual(res1.policy_action, "ALLOW")

        # Verify summary was updated in storage
        conv_data = self.store.get_conversation(conv_id)
        self.assertTrue(len(conv_data["summary"]) > 0)

        # Turn 2
        req2 = ChatRequest(
            user_id="demo-user",
            conversation_id=conv_id,
            message="Rekomendasiin cara nahan craving di tempat kemarin.",
        )
        res2 = self.orchestrator.process(req2)
        self.assertEqual(res2.policy_action, "ALLOW")

        # Check recorded context on turn 2 provider call
        last_call = self.provider.history[-1]
        system_prompt = last_call["system_prompt"]
        messages = last_call["messages"]

        # Memory verification: rolling summary in system prompt / context notes
        self.assertIn("Konteks riwayat/memori", system_prompt)
        # Context window includes previous raw messages (<=6)
        user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
        self.assertTrue(any("warkop" in msg for msg in user_msgs) or "warkop" in system_prompt)


if __name__ == "__main__":
    unittest.main()
