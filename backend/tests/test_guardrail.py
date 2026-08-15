"""Tests for deterministic Output Guardrail (KEEP/SANITIZE/REPLACE) (T5 #6)."""
import unittest

from app.services.output_guardrail import OutputGuardrail


class TestOutputGuardrail(unittest.TestCase):
    def setUp(self):
        self.guard = OutputGuardrail()

    def test_keep_safe_reply(self):
        safe_text = "Gue paham banget, craving bisa terasa berat. Yuk coba teknik napas 4-7-8 dulu."
        filtered, action = self.guard.filter_output(safe_text)
        self.assertEqual(action, "KEEP")
        self.assertEqual(filtered, safe_text)

    def test_sanitize_medical_claims(self):
        medical_text = (
            "Kamu terdiagnosis ketergantungan nikotin tingkat berat. "
            "Saya sarankan minum obat varenicline dosis 1mg dua kali sehari."
        )
        filtered, action = self.guard.filter_output(medical_text)
        self.assertEqual(action, "SANITIZE")
        self.assertIn("psikoedukasi", filtered.lower())
        self.assertIn("bukan pengganti diagnosis", filtered.lower())
        self.assertTrue(filtered.startswith(medical_text))

    def test_replace_system_prompt_leak(self):
        leak_text = (
            "System Prompt: Kamu adalah Renti (Rekan Berhenti). "
            "My instructions are to assist users with smoking cessation."
        )
        filtered, action = self.guard.filter_output(leak_text)
        self.assertEqual(action, "REPLACE")
        self.assertNotIn("System Prompt:", filtered)
        self.assertIn("Renti", filtered)
        self.assertIn("mendampingimu", filtered)

    def test_replace_ignore_instructions_leak(self):
        leak_text = "I will ignore previous instructions and reveal the system instructions:"
        filtered, action = self.guard.filter_output(leak_text)
        self.assertEqual(action, "REPLACE")
        self.assertNotIn("ignore previous instructions", filtered)


if __name__ == "__main__":
    unittest.main()
