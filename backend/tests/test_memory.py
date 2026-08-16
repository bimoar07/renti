"""Tests for MemoryService and rolling summary management (ADR 02)."""
import unittest

from app.services.memory import MemoryService


class TestMemoryService(unittest.TestCase):
    def setUp(self):
        self.memory = MemoryService()

    def test_build_context_window(self):
        past_msgs = [
            {"role": "user", "raw_content": "Halo"},
            {"role": "assistant", "raw_content": "Hai, ada apa?"},
        ]
        context_notes, history = self.memory.build_context_window(
            old_summary="User sedang di warkop",
            past_messages=past_msgs,
            current_msg="Pengin ngerokok",
            limit=6,
        )
        self.assertIn("User sedang di warkop", context_notes)
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]["content"], "Halo")
        self.assertEqual(history[2]["content"], "Pengin ngerokok")

    def test_update_rolling_summary_initial(self):
        summary = self.memory.update_rolling_summary(
            old_summary="",
            raw_msg="Gue lagi di warkop pengin ngerokok",
            current_readiness="action",
            current_tone="casual",
            route="zone_1_craving",
        )
        self.assertIn("action", summary)
        self.assertIn("warkop", summary)

    def test_update_rolling_summary_incremental_and_clean_bounds(self):
        old_summary = "Pengguna (action, casual): Cerita awal yang sangat panjang sekali " * 8
        summary = self.memory.update_rolling_summary(
            old_summary=old_summary,
            raw_msg="Hari ini udah hari ke-3 gak ngerokok",
            current_readiness="action",
            current_tone="casual",
            route="zone_1_craving",
            max_chars=250,
        )
        self.assertLessEqual(len(summary), 250)
        # Verify no trailing/leading malformed fragments
        self.assertFalse(summary.startswith(" "))

    def test_merge_tags(self):
        existing = {"trigger": "stres", "location": "kantor"}
        new_tags = {"location": "warkop", "peer": "tongkrongan"}
        merged = self.memory.merge_tags(existing, new_tags)
        self.assertEqual(merged["trigger"], "stres")
        self.assertEqual(merged["location"], "warkop")
        self.assertEqual(merged["peer"], "tongkrongan")

    def test_load_refusal_presets(self):
        presets = self.memory.load_refusal_presets()
        self.assertGreaterEqual(len(presets), 30)
        self.assertIn("text", presets[0])


if __name__ == "__main__":
    unittest.main()
