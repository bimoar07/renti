"""Tests for LLMProvider and fallback Zero-Crash (Gemini -> Groq -> template)."""
import unittest
from unittest.mock import MagicMock, patch

from app.services.llm_provider import LLMProvider, ProviderResult, RecordingProvider


class TestProviderFallback(unittest.TestCase):
    def test_gemini_success_primary(self):
        provider = LLMProvider(
            gemini_api_key="test-gemini-key",
            groq_api_key="test-groq-key",
        )
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Jawaban Gemini"))]

        with patch("app.services.llm_provider.completion", return_value=mock_response) as mock_comp:
            res = provider.generate(
                system_prompt="You are Renti",
                messages=[{"role": "user", "content": "Halo Renti"}],
            )
            self.assertIsInstance(res, ProviderResult)
            self.assertEqual(res.text, "Jawaban Gemini")
            self.assertEqual(res.provider_name, "gemini")
            self.assertFalse(res.fallback_used)
            mock_comp.assert_called_once()

    def test_gemini_failure_groq_success(self):
        provider = LLMProvider(
            gemini_api_key="test-gemini-key",
            groq_api_key="test-groq-key",
        )
        mock_groq_resp = MagicMock()
        mock_groq_resp.choices = [MagicMock(message=MagicMock(content="Jawaban Groq"))]

        def fake_completion(*args, **kwargs):
            model = kwargs.get("model", "")
            if "gemini" in model:
                raise RuntimeError("Gemini 429 Quota Exceeded")
            return mock_groq_resp

        with patch("app.services.llm_provider.completion", side_effect=fake_completion):
            res = provider.generate(
                system_prompt="You are Renti",
                messages=[{"role": "user", "content": "Halo Renti"}],
            )
            self.assertEqual(res.text, "Jawaban Groq")
            self.assertEqual(res.provider_name, "groq")
            self.assertTrue(res.fallback_used)

    def test_both_fail_template_fallback_never_raises(self):
        provider = LLMProvider(
            gemini_api_key="test-gemini-key",
            groq_api_key="test-groq-key",
        )
        with patch("app.services.llm_provider.completion", side_effect=RuntimeError("Network Error")):
            res = provider.generate(
                system_prompt="You are Renti",
                messages=[{"role": "user", "content": "Pengin ngerokok"}],
            )
            self.assertIsInstance(res, ProviderResult)
            self.assertTrue(len(res.text) > 0)
            self.assertEqual(res.provider_name, "template")
            self.assertTrue(res.fallback_used)

    def test_no_keys_graceful_template_degradation(self):
        provider = LLMProvider(gemini_api_key="", groq_api_key="")
        res = provider.generate(
            system_prompt="You are Renti",
            messages=[{"role": "user", "content": "Gue lagi di warkop"}],
        )
        self.assertIsInstance(res, ProviderResult)
        self.assertEqual(res.provider_name, "template")
        self.assertTrue(res.fallback_used)
        self.assertTrue(len(res.text) > 0)

    def test_recording_provider_records_calls(self):
        rec = RecordingProvider(canned_response="Canned reply")
        res = rec.generate(
            system_prompt="Prompt system",
            messages=[{"role": "user", "content": "User msg"}],
        )
        self.assertEqual(res.text, "Canned reply")
        self.assertEqual(len(rec.history), 1)
        self.assertEqual(rec.history[0]["system_prompt"], "Prompt system")
        self.assertEqual(rec.history[0]["messages"][0]["content"], "User msg")


if __name__ == "__main__":
    unittest.main()
