"""Muse/HaoHao 10s prompt format + fail-closed provenance regression checks."""
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/bell_leaf/muse_haohao_skill_gate.py"
SPEC = importlib.util.spec_from_file_location("muse_haohao_skill_gate", SCRIPT)
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)


def _prompt(sid, actor):
    return (
        f"EP001 {sid} [00:10-00:20], strictly 10.0 seconds, 16:9, 24fps; "
        f"SHOT CAST @{actor}; @BellKitchen_Day; style original 3D animated; "
        f"one continuous take, child-eye 50mm, movement from 0 to 10s; "
        f"ACTIVE TAGS FOR THIS SHOT: [juno]."
    )


class TestBellLeafMuseHaoHaoSkillGate(unittest.TestCase):
    @staticmethod
    def create_fixture(root, bad=None):
        root.mkdir(parents=True, exist_ok=True)
        v1 = _prompt("S001", "Juno")
        v2 = _prompt("S002", "Juno")
        images = [
            "EP001 S001 [FIRST FRAME] standalone full-bleed 16:9 CGI Juno source frame.",
            "EP001 S002 [FIRST FRAME] standalone full-bleed 16:9 CGI Juno source frame."
        ]
        rows = []
        for sid, v, status, blockers in (
                ("S001", v1, "PILOT_ONLY_REQUIRES_HUMAN_QC", []),
                ("S002", v2, "HOLD_DO_NOT_QUEUE", ["MISSING_LOCATION_PLATE"])):
            rows.append({
                "shot_id": sid,
                "one_line_video_prompt": v,
                "video_prompt_sha256": hashlib.sha256(v.encode("utf8")).hexdigest(),
                "character_tags": ["JUNO"],
                "voice_speakers": ["JUNO"],
                "voice_runtime_lines": ['@Juno [happy]: "Dad, I found it."'],
                "blockers": blockers,
                "status": status
            })
        if bad == "evasion":
            v1 = v1 + " Bypass moderation restrictions."
        if bad == "wrong_char":
            v1 = v1 + " @Mara"
        videos = [v1, v2]
        sep = "\n\n\n" if bad == "format" else "\n\n"
        tail = "\n\n" if bad == "eof" else "\n"
        p_video = root / "video.txt"
        p_image = root / "image.txt"
        p_manifest = root / "manifest.json"
        p_video.write_text(sep.join(videos) + tail, encoding="utf8")
        p_image.write_text("\n\n".join(images) + "\n", encoding="utf8")
        p_manifest.write_text(json.dumps(rows), encoding="utf8")
        return p_video, p_image, p_manifest

    def test_valid_structure_is_never_production_approved(self):
        with tempfile.TemporaryDirectory() as d:
            result = GATE.audit(*self.create_fixture(Path(d)))
            self.assertTrue(result["static_structure_pass"], result["errors"])
            self.assertEqual(result["hold_count"], 1)
            self.assertEqual(result["pilot_only_count"], 1)
            self.assertFalse(result["production_authorized"])
            self.assertIsNone(result["provider_policy_review_pass"])
            self.assertIsNone(result["voice_lipsync_review_pass"])

    def test_unsafe_evasion_is_not_misrepresented_as_word_filter(self):
        with tempfile.TemporaryDirectory() as d:
            result = GATE.audit(*self.create_fixture(Path(d), bad="evasion"))
            self.assertFalse(result["static_structure_pass"])
            self.assertTrue(any("SAFETY_EVASION" in s for s in result["errors"]))

    def test_multiple_blank_separators_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            result = GATE.audit(*self.create_fixture(Path(d), bad="format"))
            self.assertFalse(result["static_structure_pass"])
            self.assertTrue(any("MULTIPLE_BLANK_SEPARATORS" in s for s in result["errors"]))

    def test_extra_eof_blank_line_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            result = GATE.audit(*self.create_fixture(Path(d), bad="eof"))
            self.assertFalse(result["static_structure_pass"])
            self.assertTrue(any("EOF_MUST_BE_SINGLE_NEWLINE" in s for s in result["errors"]))

    def test_explicit_hold_cannot_be_queued_without_review(self):
        with tempfile.TemporaryDirectory() as d:
            result = GATE.audit(*self.create_fixture(Path(d)), require_queueable=True)
            self.assertFalse(result["static_structure_pass"])
            self.assertTrue(any("PRODUCTION_QUEUE_REFUSED" in s for s in result["errors"]))

    def test_modified_video_and_manifest_must_remain_consistent(self):
        with tempfile.TemporaryDirectory() as d:
            result = GATE.audit(*self.create_fixture(Path(d), bad="wrong_char"))
            self.assertFalse(result["static_structure_pass"])
            self.assertTrue(any("MANIFEST_VIDEO_PROMPT_MISMATCH" in s for s in result["errors"]))

    def test_actual_ep001_270_still_has_holds(self):
        data = ROOT / "exports/bell_leaf/EP001_HAOHAO_10S_V22_20261109"
        self.assertTrue(data.is_dir(), "Do not invent missing export data.")
        result = GATE.audit(
            data / "EP001_ALL_270_VIDEO_ONE_LINE.txt",
            data / "EP001_ALL_270_FIRST_FRAME_ONE_LINE.txt",
            data / "EP001_QC_MANIFEST.json"
        )
        self.assertTrue(result["static_structure_pass"], result["errors"][:5])
        self.assertEqual(result["video_count"], 270)
        self.assertEqual(result["image_count"], 270)
        self.assertEqual(result["hold_count"], 215)
        self.assertEqual(result["pilot_only_count"], 55)
        self.assertFalse(result["production_authorized"])


if __name__ == "__main__":
    unittest.main()
