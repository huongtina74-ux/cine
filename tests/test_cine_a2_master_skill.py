"""One CINE Master Skill: actual 21-role artifact handoff + stage QC tests."""
from __future__ import annotations
import argparse
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import cf_a2_master_skill as master
import cf_script_factory as factory

class A2MasterSkillIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.storage=pathlib.Path(self.tmp.name)
        self.pid="bell_leaf_ep001"
        self.base=self.storage/self.pid
        self.args=argparse.Namespace(id=self.pid,root=self.storage,
            niche="magical_witch_family_stories",mode="A2_ANIMATED_SCREENPLAY",
            minutes=40,writer="writer-01",language="en-US")
        with contextlib.redirect_stdout(io.StringIO()):
            factory.initialize(self.args)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self,rel,value):
        p=self.base/rel
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(value,encoding="utf-8")

    def research(self):
        self.write("01_research/evidence.json",json.dumps({
            "niche_id":"magical_witch_family_stories",
            "sources":[{"url":"https://example.com/public-video","observed_at_utc":"2026-10-30T00:00:00Z","evidence_type":"METADATA_ONLY"}]}))
        self.write("01_research/evidence_register.json",json.dumps({
            "items":[{"id":"EV-1","url":"https://example.com/public-video","observed_at_utc":"2026-10-30T00:00:00Z","confidence":"SUPPORTED_HYPOTHESIS"}]}))
        self.write("01_research/outlier_board.csv","video_id,views\nEV-1,100\n")
        self.write("01_research/story_autopsy.md","# Story autopsy (metadata only)\n"+"Metadata-only observations. No claims of actual full-video viewing. "*5)

    def test_one_master_is_existing_skill(self):
        text=(ROOT/".claude/skills/cine-script-factory/SKILL.md").read_text("utf-8")
        self.assertIn("ONE MASTER SKILL",text)
        self.assertIn("cf_a2_master_skill.py",text)

    def test_next_role_is_r01(self):
        result=master.scan(ROOT,self.pid,self.storage)
        self.assertEqual(result["total_specialist_skills"],21)
        self.assertEqual(result["mandatory_specialist_skills"],20)
        self.assertEqual(result["next"]["type"],"RUN_SKILL")
        self.assertEqual(result["next"]["skill_id"],"r01-source-evidence")
        self.assertFalse(result["production_authorized"])

    def test_no_fabricated_output_record(self):
        with self.assertRaisesRegex(ValueError,"Missing/empty skill output"):
            master.record(ROOT,self.pid,"r01-source-evidence","researcher-1",self.storage)

    def test_skill_handoff_is_sha_bound_and_does_not_approve_creative(self):
        self.research()
        first=master.record(ROOT,self.pid,"r01-source-evidence","researcher-1",self.storage)
        self.assertFalse(first["production_authorized"])
        self.assertEqual(master.scan(ROOT,self.pid,self.storage)["next"]["skill_id"],"r04-competitive-outlier")
        self.write("01_research/evidence_register.json",json.dumps({"items":[{"id":"CHANGED"}]}))
        result=master.scan(ROOT,self.pid,self.storage)
        self.assertEqual(result["skill_states"]["r01-source-evidence"]["status"],"STALE_OR_INVALID")
        self.assertEqual(result["next"]["skill_id"],"r01-source-evidence")

    def test_stage_cannot_approve_without_master_receipts(self):
        self.research()
        with self.assertRaisesRegex(ValueError,"Missing/stale master skill handoff"):
            factory.advance(argparse.Namespace(id=self.pid,root=self.storage,stage="research",actor="reviewer-2"))

    def test_full_research_stage_handoffs_then_stage_gate(self):
        self.research()
        for x in ("r01-source-evidence","r04-competitive-outlier","r05-competitor-story-autopsy"):
            master.record(ROOT,self.pid,x,"researcher-1",self.storage)
        state=master.scan(ROOT,self.pid,self.storage)
        self.assertEqual(state["next"]["type"],"STAGE_QC_GATE")
        self.assertEqual(state["next"]["stage"],"research")
        with contextlib.redirect_stdout(io.StringIO()):
            factory.advance(argparse.Namespace(id=self.pid,root=self.storage,stage="research",actor="reviewer-2"))
        new=master.scan(ROOT,self.pid,self.storage)
        self.assertEqual(new["stage_gates"]["research"],"PASS")
        self.assertEqual(new["next"]["skill_id"],"r02-audience-jtbd")
        self.assertFalse(new["production_authorized"])

    def test_upstream_change_stales_approved_stage(self):
        self.research()
        for x in ("r01-source-evidence","r04-competitive-outlier","r05-competitor-story-autopsy"):
            master.record(ROOT,self.pid,x,"researcher-1",self.storage)
        with contextlib.redirect_stdout(io.StringIO()):
            factory.advance(argparse.Namespace(id=self.pid,root=self.storage,stage="research",actor="reviewer-2"))
        self.write("01_research/evidence_register.json",json.dumps({"items":[{"id":"MUTATED"}]}))
        status=factory.status(argparse.Namespace(id=self.pid,root=self.storage))
        self.assertTrue(status["stages"]["research"].startswith("STALE: "))
        self.assertFalse(status["script_ready_for_production"])

    def test_wrong_subniche_refused(self):
        mf=json.loads((self.base/"manifest.json").read_text("utf-8"))
        mf["niche_id"]="slow_english_a2_story"
        self.write("manifest.json",json.dumps(mf))
        with self.assertRaisesRegex(ValueError,"Not the Bell & Leaf"):
            master.scan(ROOT,self.pid,self.storage)

    def test_21_roles_are_one_dag_no_new_factory(self):
        graph=json.loads((ROOT/"config/story_factory/a2_bell_leaf_skill_graph.json").read_text("utf-8"))
        self.assertEqual(len(graph["nodes"]),21)
        self.assertEqual(sum(len(n["requires"]) for n in graph["nodes"]),38)
        self.assertTrue(all(n["skill_file"].startswith(".claude/skills/") for n in graph["nodes"]))

if __name__=="__main__":
    unittest.main()
