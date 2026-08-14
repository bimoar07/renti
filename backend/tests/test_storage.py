"""Tests for SQLiteStore persistence and conversation tracking."""
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
        conv = self.store.create_conversation("c-1", "u-1", "action")
        self.assertEqual(conv["conversation_id"], "c-1")
        self.assertEqual(conv["readiness_stage"], "action")

        fetched = self.store.get_conversation("c-1")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["user_id"], "u-1")
        self.assertEqual(fetched["readiness_stage"], "action")
        self.assertTrue(self.store.conversation_exists("c-1"))

    def test_update_readiness(self):
        self.store.create_conversation("c-2", "u-2", "contemplation")
        self.store.update_readiness("c-2", "action")
        fetched = self.store.get_conversation("c-2")
        self.assertEqual(fetched["readiness_stage"], "action")

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
