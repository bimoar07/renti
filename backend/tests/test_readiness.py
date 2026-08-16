"""Tests for Hybrid Readiness detection and MAPR transition validator (T3 #7)."""
import unittest

from app.schemas.chat import ReadinessStage
from app.services.llm_provider import RecordingProvider
from app.services.readiness import ReadinessService, validate_mapr_transition


class TestReadiness(unittest.TestCase):
    def setUp(self):
        self.service = ReadinessService()

    def test_validate_mapr_legal_transitions(self):
        # Legal transitions with evidence
        self.assertTrue(validate_mapr_transition("precontemplation", "contemplation", "Mulai kepikiran berhenti"))
        self.assertTrue(validate_mapr_transition("contemplation", "action", "Udah 2 hari gak ngerokok"))
        self.assertTrue(validate_mapr_transition("action", "maintenance", "Udah 6 bulan bebas rokok"))
        self.assertTrue(validate_mapr_transition("action", "relapse", "Kemarin khilaf ngerokok sebatang"))
        self.assertTrue(validate_mapr_transition("relapse", "action", "Hari ini komitmen mulai lagi"))
        self.assertTrue(validate_mapr_transition("relapse", "contemplation", "Masih ragu mau mulai kapan"))

    def test_validate_mapr_illegal_transitions_blocked(self):
        # Illegal skips/jumps
        self.assertFalse(validate_mapr_transition("precontemplation", "action", "Mau langsung action"))
        self.assertFalse(validate_mapr_transition("precontemplation", "maintenance", "Langsung maintenance"))
        self.assertFalse(validate_mapr_transition("contemplation", "maintenance", "Lewati action"))

    def test_validate_mapr_empty_evidence_blocked(self):
        # No evidence provided
        self.assertFalse(validate_mapr_transition("contemplation", "action", ""))
        self.assertFalse(validate_mapr_transition("contemplation", "action", "   "))

    def test_evaluate_transition_in_zone_1_legal(self):
        rec_provider = RecordingProvider(
            canned_response='{"proposed_stage": "action", "evidence": "Pengguna menyatakan sudah 2 hari berhenti merokok."}'
        )
        new_stage, evidence = self.service.evaluate_transition(
            current_stage="contemplation",
            message="Gue udah 2 hari ini gak ngerokok sama sekali bro.",
            route="zone_1_craving",
            provider=rec_provider,
        )
        self.assertEqual(new_stage, "action")
        self.assertIsNotNone(evidence)
        self.assertIn("2 hari", evidence)

    def test_evaluate_transition_in_non_zone_1_ignored(self):
        rec_provider = RecordingProvider(
            canned_response='{"proposed_stage": "action", "evidence": "Pengguna menyatakan berhenti."}'
        )
        # In zone_2 or zone_3, transition must NOT be evaluated
        new_stage, evidence = self.service.evaluate_transition(
            current_stage="contemplation",
            message="Gue lagi pusing kerjaan kantor.",
            route="zone_2_emotional",
            provider=rec_provider,
        )
        self.assertEqual(new_stage, "contemplation")
        self.assertIsNone(evidence)
        self.assertEqual(len(rec_provider.history), 0)

    def test_evaluate_transition_illegal_proposal_retained(self):
        # Provider proposes illegal jump from precontemplation to action
        rec_provider = RecordingProvider(
            canned_response='{"proposed_stage": "action", "evidence": "Pengguna lompat tahap."}'
        )
        new_stage, evidence = self.service.evaluate_transition(
            current_stage="precontemplation",
            message="Aku belum mau berhenti tapi mau langsung aksi.",
            route="zone_1_contemplation",
            provider=rec_provider,
        )
        self.assertEqual(new_stage, "precontemplation")
        self.assertIsNone(evidence)


if __name__ == "__main__":
    unittest.main()
