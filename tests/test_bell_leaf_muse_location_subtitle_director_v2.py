"""CINE Bell & Leaf @location, voice and caption plan must be durable and fail closed."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "tools/bell_leaf/muse_haohao_skill_gate.py"
spec = importlib.util.spec_from_file_location("bell_leaf_muse_haohao_gate_v2", GATE_PATH)
gate = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(gate)

VIDEO = (
    "EP001 S003, 10.0 seconds, 16:9, 24fps, "
    "ACTIVE TAGS FOR THIS SHOT: [juno,bix]; @Juno @BIX "
    "EXACT SOURCE LOCATION @BellKitchen_Day; premium stylized 3D "
    "cinematic family animation; speaker Juno; one 10-second take."
)
IMAGE = (
    "EP001 S003 FIRST FRAME, 16:9 full-bleed, "
    "@Juno @BIX EXACT SOURCE LOCATION @BellKitchen_Day; "
    "single approved stylized 3D image not collage."
)


def _fixture(base: Path, video: str = VIDEO, image: str = IMAGE,
             location: str = "BellKitchen_Day",
             location_matched: bool = True,
             caption: dict | None = None) -> tuple[Path, Path, Path]:
    video_file = base / "video.txt"
    image_file = base / "image.txt"
    manifest_file = base / "manifest.json"
    video_file.write_text(video + "\n", encoding="utf8")
    image_file.write_text(image + "\n", encoding="utf8")
    row = {
        "shot_id": "S003",
        "one_line_video_prompt": video,
        "video_prompt_sha256": hashlib.sha256(video.encode("utf8")).hexdigest(),
        "character_tags": ["JUNO", "BIX"],
        "location": location,
        "location_matched": location_matched,
        "voice_speakers": ["JUNO"],
        "voice_runtime_lines": ['@Juno [happy]: "Dad, I can help."'],
        "status": "PILOT_ONLY_REQUIRES_HUMAN_QC",
        "blockers": [],
    }
    if caption is not None:
        row["subtitle_plan"] = caption
    manifest_file.write_text(json.dumps([row], ensure_ascii=False), encoding="utf8")
    return video_file, image_file, manifest_file


class TestMuseShotDirectorV2(unittest.TestCase):
    def _run(self, video=VIDEO, image=IMAGE, **kwargs):
        with tempfile.TemporaryDirectory() as d:
            return gate.audit(*_fixture(Path(d), video=video, image=image, **kwargs))

    def test_valid_location_but_missing_caption_plan_is_not_ready_for_production(self):
        result = self._run()
        self.assertTrue(result["static_structure_pass"], result["errors"])
        self.assertEqual(result["spoken_shots_missing_subtitle_plan"], 1)
        self.assertFalse(result["production_authorized"])

    def test_valid_post_audio_caption_plan_is_recognized_but_not_art_approved(self):
        result = self._run(caption={
            "required": True,
            "source": "FINAL_ACCEPTED_AUDIO",
            "mode": "SRT_AND_BURNED_FINAL_MP4",
            "max_lines": 2,
        })
        self.assertTrue(result["static_structure_pass"], result["errors"])
        self.assertEqual(result["spoken_shots_with_documented_subtitle_plan"], 1)
        self.assertEqual(result["spoken_shots_missing_subtitle_plan"], 0)
        self.assertFalse(result["production_authorized"])

    def test_mismatched_video_location_is_rejected(self):
        text = VIDEO.replace("@BellKitchen_Day", "@MagicCastle_Day")
        result = self._run(video=text)
        self.assertFalse(result["static_structure_pass"])
        self.assertTrue(any("VIDEO_LOCATION_TAG_MISSING_OR_MISMATCH" in x for x in result["errors"]))

    def test_location_tag_must_not_match_prefix_of_unregistered_name(self):
        text = VIDEO.replace("@BellKitchen_Day", "@BellKitchen_Day_Alternate")
        result = self._run(video=text)
        self.assertFalse(result["static_structure_pass"])
        self.assertTrue(any("VIDEO_LOCATION_TAG_MISSING_OR_MISMATCH" in x for x in result["errors"]))

    def test_mismatched_first_frame_location_is_rejected(self):
        text = IMAGE.replace("@BellKitchen_Day", "@GrandpaHouse_Exterior")
        result = self._run(image=text)
        self.assertFalse(result["static_structure_pass"])
        self.assertTrue(any("FIRST_FRAME_LOCATION_TAG_MISSING_OR_MISMATCH" in x for x in result["errors"]))

    def test_unapproved_location_cannot_appear_as_pilot(self):
        result = self._run(location_matched=False)
        self.assertFalse(result["static_structure_pass"])
        self.assertTrue(any("UNAPPROVED_LOCATION_NOT_HELD" in x for x in result["errors"]))

    def test_queueable_gate_refuses_missing_caption_plan(self):
        with tempfile.TemporaryDirectory() as d:
            result = gate.audit(*_fixture(Path(d)), require_queueable=True)
        self.assertFalse(result["static_structure_pass"])
        self.assertTrue(any("QUEUE_REFUSED_MISSING_SUBTITLE_PLANS" in x for x in result["errors"]))

    def test_director_and_operating_standard_crosslink(self):
        sub = Path(".claude/skills/cine-bell-leaf-stylized-3d-prompt-director")
        director = ROOT / sub / "references/MUSE_BELL_LEAF_SHOT_DIRECTOR_V2_20261109.md"
        standard = ROOT / sub / "references/MUSE_HAOHAO_OPERATING_STANDARD_20261109.md"
        skill = ROOT / sub / "SKILL.md"
        for path in (director, standard, skill):
            self.assertTrue(path.exists(), str(path))
        self.assertIn("MUSE_BELL_LEAF_SHOT_DIRECTOR_V2_20261109.md", standard.read_text(encoding="utf8"))
        self.assertIn("MUSE_BELL_LEAF_SHOT_DIRECTOR_V2_20261109.md", skill.read_text(encoding="utf8"))
        guidance = director.read_text(encoding="utf8")
        for phrase in ("@Juno", "@BIX", "@BellKitchen_Day",
                       "10.0 seconds", "24fps", "SRT", "FINAL_ACCEPTED_AUDIO",
                       "voice_registry.json", "CINE", "HaoHao"):
            self.assertIn(phrase, guidance)

    def test_claude_codex_skill_and_reference_mirrors_identical(self):
        names = (
            "SKILL.md",
            "references/MUSE_HAOHAO_OPERATING_STANDARD_20261109.md",
            "references/MUSE_BELL_LEAF_SHOT_DIRECTOR_V2_20261109.md"
        )
        for name in names:
            with self.subTest(name=name):
                a = ROOT / ".claude/skills/cine-bell-leaf-stylized-3d-prompt-director" / name
                b = ROOT / ".agents/skills/cine-bell-leaf-stylized-3d-prompt-director" / name
                self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_legacy_ep001_export_does_not_falsely_pass_release(self):
        base = ROOT / "exports/bell_leaf/EP001_HAOHAO_10S_V22_20261109"
        result = gate.audit(
            base / "EP001_ALL_270_VIDEO_ONE_LINE.txt",
            base / "EP001_ALL_270_FIRST_FRAME_ONE_LINE.txt",
            base / "EP001_QC_MANIFEST.json"
        )
        self.assertTrue(result["static_structure_pass"], result["errors"][:5])
        self.assertEqual(result["video_count"], 270)
        self.assertEqual(result["hold_count"], 215)
        self.assertEqual(result["pilot_only_count"], 55)
        self.assertGreater(result["spoken_shots_missing_subtitle_plan"], 0)
        self.assertFalse(result["production_authorized"])


if __name__ == "__main__":
    unittest.main()
