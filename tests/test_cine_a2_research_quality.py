"""CINE A2 research quality tests: prevent file receipts ≠ credible competitor research.

All synthetic records are only fixtures; no invented real YouTube AV review is claimed.
"""
import csv
import io
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import cf_a2_research_quality as qc

class A2ResearchQualityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.base=pathlib.Path(self.temp.name)
        self.folder=self.base/"01_research"
        self.folder.mkdir()
        self.sources=[{"url":"https://www.youtube.com/watch?v=TEST001",
                       "observed_at_utc":"2026-10-30T12:00:00Z",
                       "peer_group":"ADJACENT_SLOW_ENGLISH","evidence_type":"METADATA_ONLY",
                       "method":"TEST_FIXTURE_ONLY"}]
        self.write()

    def tearDown(self):self.temp.cleanup()

    def write(self):
        self._json("input_sources.json",{"subniche_id":"magical_witch_family_stories","sources":self.sources})
        self._json("evidence_register.json",{"items":self.sources,"direct_peer_coverage":0,
                  "direct_peer_status":"BLOCKED_INSUFFICIENT_DIRECT_EVIDENCE"})
        self._json("evidence.json",{"niche_id":"magical_witch_family_stories","sources":self.sources})
        (self.folder/"story_autopsy.md").write_text("status: BLOCKED\n"+("Metadata cannot verify actual stories or audiovisual hooks. "*12),encoding="utf-8")
        with (self.folder/"outlier_board.csv").open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=["url","views"]);w.writeheader();w.writerow({"url":self.sources[0]["url"],"views":100})

    def _json(self,n,v): (self.folder/n).write_text(json.dumps(v),encoding="utf-8")

    def test_metadata_only_cannot_advance_even_with_all_files(self):
        res=qc.inspect(self.base)
        self.assertEqual(res["status"],"BLOCKED")
        self.assertIn("NO_ORIGINAL_VIDEO_CONTENT_REVIEW_EVIDENCE",res["reasons"])
        self.assertIn("R05_STORY_AUTOPSY_ADMITTED_BLOCKED",res["reasons"])
        with self.assertRaisesRegex(ValueError,"A2_RESEARCH_QUALITY_BLOCKED"):
            qc.require_research_ready(self.base)

    def test_adjacent_cannot_be_direct_peer(self):
        res=qc.inspect(self.base)
        self.assertEqual(res["direct_peer_count"],0)
        self.assertTrue(any(x.startswith("INSUFFICIENT_DIRECT") for x in res["reasons"]))

    def test_source_url_not_in_input_must_block(self):
        reg=json.loads((self.folder/"evidence_register.json").read_text())
        reg["items"][0]["url"]="https://www.youtube.com/watch?v=UNKNOWN"
        self._json("evidence_register.json",reg)
        self.assertIn("R01_REGISTER_HAS_UNGROUNDED_SOURCE",qc.inspect(self.base)["reasons"])

    def test_modality_can_not_be_upgraded_by_writer(self):
        reg=json.loads((self.folder/"evidence_register.json").read_text())
        reg["items"][0]["evidence_type"]="FULL_AV_REVIEWED"
        self._json("evidence_register.json",reg)
        self.assertIn("R01_REGISTER_MODALITY_MISMATCH",qc.inspect(self.base)["reasons"])

    def test_factory_research_must_reference_same_source_set(self):
        ev=json.loads((self.folder/"evidence.json").read_text())
        ev["sources"][0]["url"]="https://example.invalid/new"
        self._json("evidence.json",ev)
        self.assertIn("FACTORY_EVIDENCE_NOT_SAME_SOURCES_AS_R01",qc.inspect(self.base)["reasons"])

    def test_outlier_url_must_come_from_evidence_register(self):
        (self.folder/"outlier_board.csv").write_text("url,views\nhttps://example.invalid/mystery,1000\n")
        self.assertIn("OUTLIER_BOARD_URL_NOT_IN_R01_SOURCES",qc.inspect(self.base)["reasons"])

    def test_current_real_pilot_is_clearly_blocked(self):
        pilot=ROOT/"data/script_factory/projects/bell_leaf_integration_pilot_20261030"
        if not pilot.is_dir():self.skipTest("Pilot not installed in CI")
        r=qc.inspect(pilot)
        self.assertEqual(r["direct_peer_count"],0)
        self.assertEqual(r["status"],"BLOCKED")
        self.assertFalse(r["actual_av_watch_proven"])
        self.assertFalse(r["production_authorized"])
if __name__=="__main__":unittest.main()
