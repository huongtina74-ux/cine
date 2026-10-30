"""Cross-repo/reference and script→real CINE 10s director bridge tests.

The positive case mocks reference compilation, so it verifies routing only, NOT
real model writing, approved artwork, authorized voices or film production.
"""
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import cf_a2_director_bridge as bridge

class A2DirectorCrossBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=pathlib.Path(self.temp.name)
        self.store=self.root/"projects"
        self.episode=self.store/"bell_leaf_ep001"
        self.episode.mkdir(parents=True)
        (self.episode/"06_script").mkdir()
        (self.episode/"08_final").mkdir()
        (self.episode/"06_script/script.md").write_text("verified Bell Leaf fictional screenplay",encoding="utf-8")
        self.shots=self.episode/"08_final/director_shots.json"
        self.shots.write_text(json.dumps({
           "project_id":"slow_english_a2_bell_leaf",
           "shots":[{"shot_id":"EP001_S001","duration_seconds":10,"activeCharacterTags":["Lia"],"location_id":"BELL","space_id":"BH-EXT","location_view_id":"FORWARD"}]
        }),encoding="utf-8")
        self.handoff={
          "project_id":"slow_english_a2_bell_leaf",
          "subniche_id":"magical_witch_family_stories",
          "script_sha256":hashlib.sha256((self.episode/"06_script/script.md").read_bytes()).hexdigest(),
          "shots_sha256":hashlib.sha256(self.shots.read_bytes()).hexdigest(),
          "shots_file":"08_final/director_shots.json",
          "shot_count":1,
          "shot_duration_seconds":10,
          "narrator_allowed":False
        }
        self.write_handoff()
        (self.episode/"manifest.json").write_text(json.dumps({
         "project_id":"bell_leaf_ep001","mode":"A2_ANIMATED_SCREENPLAY",
         "niche_id":"magical_witch_family_stories"}),encoding="utf-8")
        self.good={"structural_stage_gates_passed":True,
         "stages":dict.fromkeys(["research","insights","concepts","story","outline","script","review","final"],"PASS")}
    def tearDown(self):self.temp.cleanup()
    def write_handoff(self):
        (self.episode/"08_final/shot_handoff.json").write_text(json.dumps(self.handoff),encoding="utf-8")
    def call(self):
        return bridge.prepare(ROOT,"bell_leaf_ep001",self.root/"output",self.store)
    def test_no_script_factory_gate_blocks_director(self):
        with mock.patch.object(bridge.factory,"status",return_value={"structural_stage_gates_passed":False,"stages":{}}):
            with mock.patch.object(bridge,"compile_shots") as engine:
                with self.assertRaisesRegex(ValueError,"stage gates not passed"):self.call()
                engine.assert_not_called()
    def test_wrong_series_blocks_director(self):
        m=json.loads((self.episode/"manifest.json").read_text());m["niche_id"]="slow_english_a2_story"
        (self.episode/"manifest.json").write_text(json.dumps(m))
        with self.assertRaisesRegex(ValueError,"Not an original Bell & Leaf"):self.call()
    def test_tampered_script_blocks(self):
        (self.episode/"06_script/script.md").write_text("modified after review")
        with mock.patch.object(bridge.factory,"status",return_value=self.good):
            with self.assertRaisesRegex(ValueError,"changed since script review"):self.call()
    def test_tampered_shots_blocks(self):
        self.shots.write_text(self.shots.read_text()+"\n")
        with mock.patch.object(bridge.factory,"status",return_value=self.good):
            with self.assertRaisesRegex(ValueError,"Shot map changed"):self.call()
    def test_wrong_10s_blocks(self):
        self.handoff["shot_duration_seconds"]=8
        self.write_handoff()
        with mock.patch.object(bridge.factory,"status",return_value=self.good):
            with self.assertRaisesRegex(ValueError,"10.0s"):self.call()
    def test_valid_handoff_invokes_existing_cine_compiler_only(self):
        response={"reference_preflight_status":"BLOCKED_FOR_PRODUCTION","shot_count":1}
        with mock.patch.object(bridge.factory,"status",return_value=self.good):
            with mock.patch.object(bridge,"compile_shots",return_value=response) as run:
                actual=self.call()
        run.assert_called_once()
        self.assertEqual(actual["director_reference_status"],"BLOCKED_FOR_PRODUCTION")
        self.assertFalse(actual["production_authorized"])
        self.assertEqual(actual["media_generated"],0)
        self.assertEqual(actual["shot_count"],1)
    def test_external_repos_are_optional_only(self):
        m=json.loads((ROOT/"config/story_factory/a2_bell_leaf_external_skill_sources.json").read_text(encoding="utf-8"))
        self.assertEqual(len(m["role_skill_references"]),21)
        self.assertEqual(len(m["repositories"]),2)
        self.assertEqual(m["repositories"][0]["license"],"MIT")
        self.assertTrue(all(not r["runtime_adapter_connected"] for r in m["repositories"]))
        self.assertTrue(all(not r["github_submodule_installed"] for r in m["repositories"]))
        names=set(json.loads((ROOT/"config/story_factory/a2_bell_leaf_skill_graph.json").read_text())["nodes"][i]["id"] for i in range(21))
        self.assertEqual(set(m["role_skill_references"]),names)
if __name__=="__main__":unittest.main()
