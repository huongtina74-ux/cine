"""Quality/safety invariants for EP001 270-shot multi-account Muse director drafts."""
from __future__ import annotations
import importlib.util
import json
import re
import tempfile
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"tools/bell_leaf/build_haohao_ep001_director_batch_v3.py"
PREFLIGHT=ROOT/"tools/bell_leaf/muse_haohao_skill_gate.py"
builder_spec=importlib.util.spec_from_file_location("director_batch_v3",SCRIPT)
builder=importlib.util.module_from_spec(builder_spec)
assert builder_spec and builder_spec.loader
builder_spec.loader.exec_module(builder)
gate_spec=importlib.util.spec_from_file_location("director_gate_v3",PREFLIGHT)
gate=importlib.util.module_from_spec(gate_spec)
assert gate_spec and gate_spec.loader
gate_spec.loader.exec_module(gate)


class TestBellLeafDirectorV3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix="ep001_director_v3_")
        cls.path=Path(cls.temp.name)
        cls.summary=builder.make(cls.path)
        cls.rows=json.loads((cls.path/"EP001_QC_MANIFEST.json").read_text(encoding="utf8"))
        cls.plan=json.loads((cls.path/"EP001_4_ACCOUNT_REVIEW_DISPATCH_PLAN.json").read_text(encoding="utf8"))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_batch_size_and_format(self):
        self.assertEqual(len(self.rows),270)
        self.assertEqual([r["shot_id"] for r in self.rows],[f"S{i:03}" for i in range(1,271)])
        for name in ("EP001_ALL_270_FIRST_FRAME_ONE_LINE.txt","EP001_ALL_270_VIDEO_ONE_LINE.txt"):
            data=(self.path/name).read_text(encoding="utf8")
            self.assertFalse(data.endswith("\n\n"))
            self.assertNotIn("\n\n\n",data)
            self.assertEqual(len(data.rstrip("\n").split("\n\n")),270)

    def test_gate_and_4_lanes_without_auto_submission(self):
        result=gate.audit(self.path/"EP001_ALL_270_VIDEO_ONE_LINE.txt",self.path/"EP001_ALL_270_FIRST_FRAME_ONE_LINE.txt",self.path/"EP001_QC_MANIFEST.json")
        self.assertTrue(result["static_structure_pass"], result["errors"][:10])
        self.assertEqual(result["video_count"],270)
        self.assertEqual(result["spoken_shots_missing_subtitle_plan"],0)
        self.assertFalse(result["production_authorized"])
        self.assertFalse(self.plan["production_authorized"])
        self.assertTrue(self.plan["no_submission_performed"])
        self.assertEqual(len(self.plan["lanes"]),4)
        ids=[s for l in self.plan["lanes"] for s in l["review_queue"]]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(len(ids),self.plan["pilot_review_count"])
        counts=[len(l["review_queue"]) for l in self.plan["lanes"]]
        self.assertLessEqual(max(counts)-min(counts),1)
        self.assertEqual(sum(counts),self.plan["pilot_review_count"])
        self.assertTrue(all(l["max_parallel_streams"]==1 for l in self.plan["lanes"]))

    def test_historical_teaser_then_current_breakfast(self):
        self.assertEqual(self.rows[0]["story_timeline"],"VEYLORA_PAST")
        for i in range(1,18):
            row=self.rows[i]
            self.assertEqual(row["story_timeline"],"EARTH_PRESENT_SAME_MORNING")
        self.assertTrue(all(self.rows[i]["status"].startswith("HOLD") for i in range(2,18)))
        self.assertIn("@BellKitchen_Day",self.rows[2]["one_line_video_prompt"])
        self.assertNotIn("@EVAN",self.rows[0]["one_line_video_prompt"])

    def test_bix_and_bubu_invariants(self):
        for r in self.rows:
            if "BIX" in r["character_tags"]:
                self.assertIn("NO bell",r["one_line_video_prompt"])
            if "BUBU" in r["character_tags"]:
                self.assertIn("spiral tail",r["one_line_video_prompt"])

    def test_exact_source_location_in_both_prompts(self):
        for r in self.rows:
            target="@"+r["location"]
            for field in ("one_line_video_prompt","one_line_image_prompt"):
                self.assertIn(target,r[field])
                self.assertNotIn("\n",r[field])
            if r["status"].startswith("PILOT"):
                self.assertTrue(r["location_matched"])
                self.assertFalse(r["blockers"])

    def test_spoken_text_not_invented(self):
        for r in self.rows:
            vid=r["one_line_video_prompt"]
            for line in r["dialogue_plan"]:
                self.assertIn(line["text"],vid)
            self.assertEqual(r["subtitle_plan"]["required"],bool(r["voice_speakers"]))
            if r["voice_speakers"]:
                self.assertEqual(r["subtitle_plan"]["source"],"FINAL_ACCEPTED_AUDIO")
                self.assertEqual(r["subtitle_plan"]["status"],"PLANNED_UNTIMED_NOT_RENDERED")

    def test_sound_and_direction_not_identical_for_every_shot(self):
        beats=[r["director_intent"]["screenplay_beat"] for r in self.rows]
        cameras=[tuple(r["director_intent"]["camera"]) for r in self.rows]
        self.assertGreater(len(set(beats)),250)
        self.assertGreater(len(set(cameras)),5)
        self.assertGreater(len(set(r["director_intent"]["sound"] for r in self.rows)),4)

    def test_no_account_or_proxy_credentials_exported(self):
        content="\n".join(p.read_text(encoding="utf8") for p in self.path.rglob("*.json"))
        for needle in ("proxyPassword","proxy_password","cookie","session_token","2fa_secret"):
            self.assertNotIn(needle,content)
        self.assertNotRegex(content,r"\b\d{1,3}(?:\.\d{1,3}){3}:\d{4,5}:[^:\\s]+:[^:\\s]+")


if __name__=="__main__":
    unittest.main()
