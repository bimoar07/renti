"""Tests for SQLiteStore persistence, tone tracking, and readiness events (T4 #5)."""
import os
import tempfile
import unittest

from app.storage.sqlite_store import SQLiteStore


class TestSQLiteStore(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "test_renti.db")
        self.store = SQLiteStore(db_path=self.db_path)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_create_and_get_conversation(self):
        conv = self.store.create_conversation("c-1", "u-1", "action", tone="casual")
        self.assertEqual(conv["conversation_id"], "c-1")
        self.assertEqual(conv["readiness_stage"], "action")
        self.assertEqual(conv["tone"], "casual")

        fetched = self.store.get_conversation("c-1")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["user_id"], "u-1")
        self.assertEqual(fetched["readiness_stage"], "action")
        self.assertEqual(fetched["tone"], "casual")
        self.assertTrue(self.store.conversation_exists("c-1"))

    def test_update_readiness(self):
        self.store.create_conversation("c-2", "u-2", "contemplation")
        self.store.update_readiness("c-2", "action")
        fetched = self.store.get_conversation("c-2")
        self.assertEqual(fetched["readiness_stage"], "action")

    def test_update_tone(self):
        self.store.create_conversation("c-tone", "u-tone", "contemplation", tone="standard")
        self.store.update_tone("c-tone", "casual")
        fetched = self.store.get_conversation("c-tone")
        self.assertEqual(fetched["tone"], "casual")

    def test_readiness_events_lifecycle(self):
        self.store.create_conversation("c-events", "u-events", "contemplation")
        event1 = self.store.record_readiness_event(
            conversation_id="c-events",
            from_stage="contemplation",
            to_stage="action",
            evidence="Pengguna mengatakan sudah 2 hari tidak merokok.",
        )
        self.assertIn("id", event1)
        self.assertEqual(event1["from_stage"], "contemplation")
        self.assertEqual(event1["to_stage"], "action")
        self.assertIn("2 hari", event1["evidence"])

        event2 = self.store.record_readiness_event(
            conversation_id="c-events",
            from_stage="action",
            to_stage="relapse",
            evidence="Pengguna merokok saat stres lembur.",
        )
        self.assertEqual(event2["to_stage"], "relapse")

        events = self.store.get_readiness_events("c-events")
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["from_stage"], "contemplation")
        self.assertEqual(events[0]["to_stage"], "action")
        self.assertEqual(events[1]["from_stage"], "action")
        self.assertEqual(events[1]["to_stage"], "relapse")

    def test_add_and_retrieve_messages(self):
        self.store.create_conversation("c-3", "u-3", "action")
        self.store.add_message(
            conversation_id="c-3",
            role="user",
            raw_content="Pengin rokok",
            canonical_content="pengin rokok",
            route="zone_1_craving",
            policy_action="ALLOW",
        )
        self.store.add_message(
            conversation_id="c-3",
            role="assistant",
            raw_content="Tarik napas 4-7-8",
            canonical_content="tarik napas 4-7-8",
            route="zone_1_craving",
            policy_action="ALLOW",
        )

        msgs = self.store.get_messages("c-3")
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0]["role"], "user")
        self.assertEqual(msgs[0]["raw_content"], "Pengin rokok")
        self.assertEqual(msgs[1]["role"], "assistant")

    def test_update_summary_and_tags(self):
        self.store.create_conversation("c-4", "u-4", "action")
        self.store.update_summary_and_tags("c-4", "User craving di warkop", {"trigger": "craving", "location": "warkop"})
        fetched = self.store.get_conversation("c-4")
        self.assertEqual(fetched["summary"], "User craving di warkop")
        self.assertEqual(fetched["context_tags"]["location"], "warkop")


if __name__ == "__main__":
    unittest.main()
