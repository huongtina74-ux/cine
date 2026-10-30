"""Prevent Bell & Leaf being accidentally classified as the entire Slow English niche."""
import json
import pathlib
import unittest
import yaml

ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE=ROOT/"config/niches/slow_english_a2"
class BellLeafSubnicheClassification(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.prod=json.loads((BASE/"production.json").read_text("utf-8"))
  cls.voice=json.loads((BASE/"voice_registry.json").read_text("utf-8"))
  cls.niche=yaml.safe_load((BASE/"niche.yaml").read_text("utf-8"))
  cls.research=yaml.safe_load((BASE/"research.yaml").read_text("utf-8"))
 def test_one_cine_one_project_stable_ids(self):
  self.assertEqual(self.prod["project_id"],"slow_english_a2_bell_leaf")
  self.assertEqual(self.prod["niche_id"],"slow_english_a2")
  self.assertEqual(self.niche["project_id"],self.prod["project_id"])
 def test_parent_child_subniche_hierarchy(self):
  self.assertEqual(self.prod["niche_hierarchy"],["slow_english","slow_english_a2","magical_witch_family_stories","bell_leaf"])
  self.assertEqual(self.prod["learning_level"],"A2")
  self.assertEqual(self.prod["parent_niche_id"],self.niche["parent_niche_id"])
  self.assertEqual(self.prod["subniche_id"],self.niche["subniche_id"])
  self.assertEqual(self.prod["series_id"],self.niche["series_id"])
 def test_research_keeps_direct_peers_separate(self):
  self.assertTrue(self.research["do_not_mix_competitors_or_baselines"])
  self.assertEqual(self.research["baseline_scope"],"same_subniche_only")
  self.assertEqual(self.research["subniche_id"],self.prod["subniche_id"])
 def test_voice_scope_belongs_to_this_subniche(self):
  self.assertEqual(self.voice["subniche_id"],self.prod["subniche_id"])
  self.assertEqual(self.voice["series_id"],"bell_leaf")
  self.assertTrue(self.voice["no_narrator"])
  self.assertEqual(len(self.voice["voices"]),10)
  self.assertEqual(sum(v["approval_status"]=="APPROVED" for v in self.voice["voices"].values()),0)
 def test_canon_assets_reference_paths_stable(self):
  self.assertEqual(self.prod["room_plate_targets"],483)
  self.assertEqual(self.prod["prop_plate_targets"],756)
  self.assertIn("cine-a2-muse-reference-anchoring",self.prod["source_registries"]["characters"])
  self.assertIn("cine-bellfern-location-multiview-lock",self.prod["source_registries"]["sites"])
 def test_original_story_not_generic_slow_english(self):
  bible=(BASE/"SERIES_BIBLE.md").read_text("utf-8")
  self.assertIn("Gia đình phù thủy",bible)
  self.assertIn("Mara is a witch",bible)
  self.assertIn("Evan and paternal grandparents are normal Earth relatives",bible)
 def test_preflight_propagates_identity(self):
  source=(ROOT/"cinefactory/studio/slow_english_a2.py").read_text("utf-8")
  self.assertIn('"subniche_id":self.profile.get("subniche_id")',source)
if __name__=="__main__":
 unittest.main()
