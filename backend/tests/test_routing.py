"""Tests for ZoneRouter and stage-tailored routing."""
import unittest

from app.core.canonicalize import canonicalize_text
from app.services.routing import ZoneRouter


class TestZoneRouting(unittest.TestCase):
    def setUp(self):
        self.router = ZoneRouter()

    def test_refusal_script_tongkrongan(self):
        msg = "Gimana cara tolak ajakan rokok pas lagi nongkrong?"
        canonical = canonicalize_text(msg)
        res = self.router.route_message(canonical, readiness_stage="action")
        self.assertEqual(res.route, "refusal_script")
        self.assertEqual(res.intent, "social_refusal")
        self.assertEqual(res.suggested_tags.get("trigger"), "social_peer_pressure")

    def test_zone_1_craving_action_stage(self):
        msg = "Gue lagi craving rokok banget nih"
        canonical = canonicalize_text(msg)
        res = self.router.route_message(canonical, readiness_stage="action")
        self.assertEqual(res.route, "zone_1_craving")
        self.assertEqual(res.intent, "cessation_support")

    def test_zone_1_contemplation_stage(self):
        msg = "Aku pengin rokok tapi masih ragu apakah sanggup berhenti"
        canonical = canonicalize_text(msg)
        res = self.router.route_message(canonical, readiness_stage="contemplation")
        self.assertEqual(res.route, "zone_1_contemplation")
        self.assertEqual(res.intent, "contemplation_support")

    def test_zone_2_emotional_venting(self):
        msg = "Pusing banget stres kerjaan numpuk deadline besok"
        canonical = canonicalize_text(msg)
        res = self.router.route_message(canonical, readiness_stage="action")
        self.assertEqual(res.route, "zone_2_emotional")
        self.assertEqual(res.intent, "emotional_venting")
        self.assertEqual(res.suggested_tags.get("trigger"), "emotional_stress")

    def test_zone_3_out_of_scope(self):
        msg = "Berapa rumus luas lingkaran?"
        canonical = canonicalize_text(msg)
        res = self.router.route_message(canonical, readiness_stage="action")
        self.assertEqual(res.route, "zone_3_out_of_scope")
        self.assertEqual(res.intent, "out_of_scope")


if __name__ == "__main__":
    unittest.main()
