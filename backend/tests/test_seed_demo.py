"""Tests untuk seeding data demo (T4 #15)."""
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

# Add scripts directory to sys.path
scripts_dir = Path(__file__).resolve().parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from seed_demo_data import seed_demo_data  # noqa: E402


class TestSeedDemoData(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_seed_demo_data_creates_two_conversations(self):
        result = seed_demo_data(user_id="demo-user-001", client=self.client)

        self.assertEqual(result["user_id"], "demo-user-001")
        conversations = result["conversations"]
        self.assertEqual(len(conversations), 2)

        # Conversation 1: Contemplation / Motivational Interviewing
        conv1 = conversations[0]
        self.assertEqual(conv1["readiness_stage"], "contemplation")
        self.assertEqual(conv1["route"], "zone_1_contemplation")
        self.assertEqual(conv1["policy_action"], "ALLOW")
        self.assertTrue(conv1["id"].startswith("conversation-"))
        self.assertTrue(len(conv1["reply"]) > 0)

        # Conversation 2: Action / Craving
        conv2 = conversations[1]
        self.assertEqual(conv2["readiness_stage"], "action")
        self.assertEqual(conv2["route"], "zone_1_craving")
        self.assertEqual(conv2["policy_action"], "ALLOW")
        self.assertTrue(conv2["id"].startswith("conversation-"))
        self.assertTrue(len(conv2["reply"]) > 0)


if __name__ == "__main__":
    unittest.main()
