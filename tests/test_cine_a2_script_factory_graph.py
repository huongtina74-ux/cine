"""Real deterministic checks for the single CINE 21-skill Bell & Leaf DAG.
No mocked YouTube video, generated screenplay, or claimed creative approval.
"""
from __future__ import annotations
import argparse
import contextlib
import copy
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import cf_script_factory as factory
import cf_a2_story_contract as graph

class A2StorySkillGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=factory.config()
        cls.result=graph.validate_graph(ROOT,cls.config)

    def test_21_real_skill_files(self):
        self.assertEqual(self.result["node_count"],21)
        self.assertEqual(self.result["status"],"SKILL_GRAPH_CONNECTED_SOURCE_ONLY")

    def test_dependency_dag_not_noop(self):
        self.assertGreaterEqual(self.result["edge_count"],35)
        self.assertGreaterEqual(self.result["output_file_count"],25)

    def test_all_outputs_bound_to_factory_stages(self):
        names=set()
        for stage in graph.STAGES:
            role_files=graph.required_artifacts(ROOT,stage)
            self.assertTrue(role_files,stage)
            for name in role_files:
                self.assertNotIn(name,names,name)
                names.add(name)
        self.assertIn("06_script/screenplay.fountain",names)
        self.assertIn("07_review/a2_review.json",names)
        self.assertIn("08_final/shot_handoff.json",names)

    def test_story_before_hook(self):
        roles={r["id"]:r for r in graph.read(ROOT)["nodes"]}
        self.assertIn("s02-character-bible",roles["s03-micro-hook-designer"]["requires"])
        self.assertEqual(roles["s03-micro-hook-designer"]["stage"],"outline")

    def test_anthology_explicit_opt_in(self):
        roles={r["id"]:r for r in graph.read(ROOT)["nodes"]}
        self.assertFalse(roles["s09-anthology-architect"]["enabled_by_default"])
        self.assertNotIn("05_outline/episode_map.md",graph.required_artifacts(ROOT,"outline"))

    def test_wrong_backward_dependency_rejected(self):
        g=copy.deepcopy(graph.read(ROOT))
        g["nodes"][0]["requires"]=["s14-script-lock-and-learning"]
        with mock.patch.object(graph,"read",return_value=g):
            with self.assertRaisesRegex(ValueError,"Dependency unavailable"):
                graph.validate_graph(ROOT)

    def test_wrong_subniche_rejected_by_init(self):
        with tempfile.TemporaryDirectory() as td:
            args=argparse.Namespace(id="bell_leaf_test_001",root=pathlib.Path(td),
                niche="slow_english_a2_story",mode="A2_ANIMATED_SCREENPLAY",
                minutes=40,writer="writer-01",language="en-US")
            with self.assertRaisesRegex(ValueError,"magical_witch_family_stories"):
                factory.initialize(args)

    def test_wrong_duration_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            args=argparse.Namespace(id="bell_leaf_test_001",root=pathlib.Path(td),
                niche="magical_witch_family_stories",mode="A2_ANIMATED_SCREENPLAY",
                minutes=60,writer="writer-01",language="en-US")
            with self.assertRaisesRegex(ValueError,"30-50"):
                factory.initialize(args)

    def test_real_init_scaffolds_21_skill_output_directories(self):
        with tempfile.TemporaryDirectory() as td:
            args=argparse.Namespace(id="bell_leaf_test_001",root=pathlib.Path(td),
                niche="magical_witch_family_stories",mode="A2_ANIMATED_SCREENPLAY",
                minutes=40,writer="writer-01",language="en-US")
            with contextlib.redirect_stdout(io.StringIO()):
                factory.initialize(args)
            base=pathlib.Path(td)/args.id
            self.assertTrue((base/"06_script").is_dir())
            self.assertTrue((base/"07_review").is_dir())
            self.assertEqual(json.loads((base/"manifest.json").read_text())["niche_id"],"magical_witch_family_stories")
            self.assertIn("06_script/screenplay.fountain",
                          factory.stage_files(base,self.config,{"id":"script","artifacts":["06_script/script.md"]}))
            current=factory.status(argparse.Namespace(id=args.id,root=pathlib.Path(td)))
            self.assertFalse(current["script_ready_for_production"])
            self.assertFalse(current["production_authorized"])
            with self.assertRaisesRegex(ValueError,"Missing required artifact"):
                factory.advance(argparse.Namespace(id=args.id,root=pathlib.Path(td),stage="research",actor="researcher-01"))

    def test_reject_no_evidence_cohort(self):
        with tempfile.TemporaryDirectory() as td:
            base=pathlib.Path(td)
            (base/"01_research").mkdir()
            (base/"01_research/evidence.json").write_text(json.dumps({
                "niche_id":"slow_english_a2_story","sources":[{"url":"https://youtube.com","observed_at_utc":"2026-10-30T00:00:00Z","evidence_type":"METADATA_ONLY"}]}))
            with self.assertRaisesRegex(ValueError,"different research subniche"):
                graph.validate_a2_stage(base,"research",{"mode":"A2_ANIMATED_SCREENPLAY","niche_id":"magical_witch_family_stories","target_minutes":40})

    def test_reject_missing_full_screenplay(self):
        with tempfile.TemporaryDirectory() as td:
            base=pathlib.Path(td)
            (base/"06_script").mkdir()
            (base/"06_script/screenplay.fountain").write_text("INT. WORKSHOP - DAY\nLIA\nHello Bubu.")
            with self.assertRaisesRegex(ValueError,"outline"):
                graph.validate_a2_stage(base,"script",{"mode":"A2_ANIMATED_SCREENPLAY","niche_id":"magical_witch_family_stories","target_minutes":40})

    def test_reject_narrator(self):
        with tempfile.TemporaryDirectory() as td:
            base=pathlib.Path(td)
            (base/"06_script").mkdir()
            (base/"06_script/screenplay.fountain").write_text("INT. BELL HOUSE\nNARRATOR: This is magic.\n" * 90)
            with self.assertRaisesRegex(ValueError,"no narrator"):
                graph.validate_a2_stage(base,"script",{"mode":"A2_ANIMATED_SCREENPLAY","niche_id":"magical_witch_family_stories","target_minutes":40})

    def test_reject_fake_human_review(self):
        with tempfile.TemporaryDirectory() as td:
            base=pathlib.Path(td)
            (base/"06_script").mkdir()
            (base/"06_script/script.md").write_text("a full screenplay content")
            (base/"07_review").mkdir()
            sha=graph._digest(base/"06_script/script.md")
            (base/"07_review/a2_review.json").write_text(json.dumps({"verdict":"PASS","reviewed_script_sha256":sha,"reviewer_id":"editor",
                "evidence_notes":["claimed reviewed"],"evidence_file":"missing.wav","evidence_sha256":"0"*64}))
            with self.assertRaisesRegex(ValueError,"Evidence file missing"):
                graph.validate_a2_stage(base,"review",{"mode":"A2_ANIMATED_SCREENPLAY","niche_id":"magical_witch_family_stories","target_minutes":40,"writer_id":"writer"})

    def test_no_automatic_approval(self):
        self.assertFalse(graph.validate_graph(ROOT)["model_execution_verified"])
        self.assertFalse(graph.validate_graph(ROOT)["independent_story_quality_qualified"])

if __name__=="__main__":
    unittest.main()
