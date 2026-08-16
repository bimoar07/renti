"""Tests for LLMProvider and fallback Zero-Crash (Gemini -> Groq -> template) with timeout budget."""
import unittest
from unittest.mock import MagicMock, patch

from app.services.llm_provider import LLMProvider, ProviderResult, RecordingProvider


class TestProviderFallback(unittest.TestCase):
    def test_default_timeouts_and_deadlines(self):
        provider = LLMProvider()
        self.assertEqual(provider.per_provider_timeout, 7.0)
        self.assertEqual(provider.total_deadline, 12.0)
        self.assertEqual(provider.timeout, 7.0)

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
            call_kwargs = mock_comp.call_args[1]
            self.assertAlmostEqual(call_kwargs.get("timeout"), 7.0, places=1)

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

    def test_groq_timeout_capped_by_remaining_deadline_budget(self):
        """When Gemini consumes time, Groq timeout must be capped by remaining budget."""
        provider = LLMProvider(
            gemini_api_key="test-gemini-key",
            groq_api_key="test-groq-key",
            per_provider_timeout=7.0,
            total_deadline=12.0,
        )
        mock_groq_resp = MagicMock()
        mock_groq_resp.choices = [MagicMock(message=MagicMock(content="Jawaban Groq setelah Gemini lama"))]

        time_values = [0.0, 0.0, 8.0, 8.0, 9.0, 10.0]
        time_iter = iter(time_values)

        def fake_time():
            return next(time_iter, 10.0)

        recorded_timeouts = []

        def fake_completion(*args, **kwargs):
            recorded_timeouts.append(kwargs.get("timeout"))
            model = kwargs.get("model", "")
            if "gemini" in model:
                raise TimeoutError("Gemini timed out after 8s")
            return mock_groq_resp

        with patch("app.services.llm_provider.time.monotonic", side_effect=fake_time), \
             patch("app.services.llm_provider.completion", side_effect=fake_completion):
            res = provider.generate(
                system_prompt="You are Renti",
                messages=[{"role": "user", "content": "Halo"}],
            )
            self.assertEqual(res.text, "Jawaban Groq setelah Gemini lama")
            self.assertEqual(res.provider_name, "groq")
            self.assertEqual(len(recorded_timeouts), 2)
            self.assertAlmostEqual(recorded_timeouts[0], 7.0, places=1)
            self.assertAlmostEqual(recorded_timeouts[1], 4.0, places=1)

    def test_total_deadline_exhausted_skips_groq_to_template(self):
        """If total budget is exhausted after Gemini, Groq is skipped and deterministic template is returned."""
        provider = LLMProvider(
            gemini_api_key="test-gemini-key",
            groq_api_key="test-groq-key",
            per_provider_timeout=7.0,
            total_deadline=12.0,
        )

        time_values = [0.0, 0.0, 13.0, 13.0, 13.0]
        time_iter = iter(time_values)

        def fake_time():
            return next(time_iter, 15.0)

        calls = []

        def fake_completion(*args, **kwargs):
            calls.append(kwargs.get("model"))
            raise TimeoutError("Gemini timeout")

        with patch("app.services.llm_provider.time.monotonic", side_effect=fake_time), \
             patch("app.services.llm_provider.completion", side_effect=fake_completion):
            res = provider.generate(
                system_prompt="You are Renti",
                messages=[{"role": "user", "content": "Pengin ngerokok"}],
            )
            self.assertEqual(len(calls), 1)  # Only Gemini was attempted
            self.assertEqual(res.provider_name, "template")
            self.assertTrue(res.fallback_used)
            self.assertTrue(len(res.text) > 0)

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

    def test_both_providers_timeout_never_raises(self):
        provider = LLMProvider(
            gemini_api_key="test-gemini-key",
            groq_api_key="test-groq-key",
        )
        with patch("app.services.llm_provider.completion", side_effect=TimeoutError("Request timed out")):
            res = provider.generate(
                system_prompt="You are Renti",
                messages=[{"role": "user", "content": "Lagi craving parah"}],
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

    def test_custom_timeout_and_deadline_configuration(self):
        provider = LLMProvider(
            per_provider_timeout=3.5,
            total_deadline=8.0,
        )
        self.assertEqual(provider.per_provider_timeout, 3.5)
        self.assertEqual(provider.total_deadline, 8.0)
        self.assertEqual(provider.timeout, 3.5)

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
