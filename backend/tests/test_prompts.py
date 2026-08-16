"""Tests for adaptive prompt library and deterministic tone classifier (T2 #4)."""
import unittest

from app.prompts.companion import build_system_prompt, detect_tone
from app.prompts.refusal import build_refusal_prompt


class TestPromptsAndTone(unittest.TestCase):
    def test_tone_classifier_casual(self):
        self.assertEqual(detect_tone("Gue lagi pengin ngerokok banget nih bro"), "casual")
        self.assertEqual(detect_tone("santai aja cuy, wkwk"), "casual")
        self.assertEqual(detect_tone("lu ada saran gak gan?"), "casual")

    def test_tone_classifier_formal(self):
        self.assertEqual(detect_tone("Selamat pagi, saya ingin menanyakan perihal program berhenti merokok."), "formal")
        self.assertEqual(detect_tone("Mohon bantuan Anda untuk memberikan saran."), "formal")

    def test_tone_classifier_standard(self):
        self.assertEqual(detect_tone("Bagaimana cara mengatasi rasa ingin merokok?"), "standard")
        self.assertEqual(detect_tone("Hari ini sudah tidak merokok."), "standard")

    def test_build_system_prompt_zone_1_craving(self):
        prompt = build_system_prompt(
            route="zone_1_craving",
            readiness_stage="action",
            tone="casual",
        )
        self.assertIn("Renti", prompt)
        self.assertIn("craving", prompt.lower())
        self.assertIn("casual", prompt.lower())
        self.assertIn("action", prompt.lower())

    def test_build_system_prompt_zone_1_contemplation(self):
        prompt = build_system_prompt(
            route="zone_1_contemplation",
            readiness_stage="contemplation",
            tone="standard",
        )
        self.assertIn("Renti", prompt)
        self.assertIn("motivational interviewing", prompt.lower())
        self.assertIn("contemplation", prompt.lower())

    def test_build_system_prompt_zone_2_emotional(self):
        prompt = build_system_prompt(
            route="zone_2_emotional",
            readiness_stage="action",
            tone="casual",
        )
        self.assertIn("emosi", prompt.lower())
        self.assertIn("jembatan", prompt.lower())

    def test_build_system_prompt_zone_3_out_of_scope(self):
        prompt = build_system_prompt(
            route="zone_3_out_of_scope",
            readiness_stage="action",
            tone="standard",
        )
        self.assertIn("out-of-scope", prompt.lower())
        self.assertIn("renti", prompt.lower())

    def test_build_refusal_prompt(self):
        prompt = build_refusal_prompt(readiness_stage="action", tone="casual")
        self.assertIn("penolakan", prompt.lower())
        self.assertIn("3", prompt)


if __name__ == "__main__":
    unittest.main()
