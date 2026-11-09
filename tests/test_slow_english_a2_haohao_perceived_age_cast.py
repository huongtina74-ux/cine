"""Prevent silent or ungrounded voice recasts for Bell & Leaf."""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/niches/slow_english_a2/voice_registry.json"
EXPECTED = {
    "juno": ("1182", "Teenager", 0.70),
    "Lia": ("1851", "Teenager", 0.86),
    "me": ("7525", "Adult", 0.70),
    "bo": ("7553", "Adult", 0.84),
    "ongngoai": ("594", "Senior", 0.70),
    "ongnoi": ("6499", "Senior", 0.70),
    "banoi": ("8300", "Senior", 0.72),
    "bangoai": ("1066", "Senior", 0.72),
    "bubu": ("5029", "Teenager", 0.88),
    "bix": ("1335", "Adult", 0.82),
}


class TestPerceivedAgeCast(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf8"))

    def test_mapping_exactly_ten_unique_ids(self):
        self.assertEqual(set(self.registry["voices"]), set(EXPECTED))
        voices = [v["haohao_audition_20261109"]["local_catalog_voice_id"] for v in self.registry["voices"].values()]
        self.assertEqual(len(voices), len(set(voices)), "Never accidentally share a speaker identity")

    def test_every_role_expected_perceived_age_and_pace(self):
        for tag, (speaker, age, pace) in EXPECTED.items():
            record = self.registry["voices"][tag]["haohao_audition_20261109"]
            with self.subTest(tag=tag):
                self.assertEqual(record["local_catalog_voice_id"], f"tts:emotive:{speaker}")
                self.assertEqual(record["perceived_age"], age)
                self.assertAlmostEqual(record["speed_factor"], pace)
                self.assertTrue(record["perceptual_source_url"].startswith("https://"))
                self.assertTrue(record["status"].endswith("NOT_HUMAN_APPROVED"))
                self.assertFalse(record["human_voice_approval"])
                self.assertGreaterEqual(record["audition_wpm"], 120)
                self.assertLessEqual(record["audition_wpm"], 145)
                self.assertGreaterEqual(record["audition_asr_similarity"], 0.99)

    def test_canon_is_not_auto_approved(self):
        self.assertEqual(self.registry["approved_voice_count"], 0)
        for tag, item in self.registry["voices"].items():
            with self.subTest(tag=tag):
                self.assertEqual(item["approval_status"], "PENDING_WAV_AND_RIGHTS_APPROVAL")
                for key in ("voice_id", "sample_wav", "sample_sha256", "reference_wav_path"):
                    self.assertIsNone(item[key])

    def test_muse_conversion_is_not_claimed_to_slow_video(self):
        meta = self.registry["haohao_audition_sync"]
        self.assertIn("NOT independently guarantee Muse-generated speech pace", meta["muse_speed_caveat"])
        self.assertIn("No actual speaker ages verified", meta["age_metadata_caveat"])


if __name__ == "__main__":
    unittest.main()
