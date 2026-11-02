"""Prevent legacy Slow English Mia/narrator production from contaminating Bell & Leaf.

These tests inspect real active loaders; no images or voices are declared approved.
"""
import pathlib,sys,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"tools"))
from cinefactory.slow_english_unified import audit,load,TAGS,PROJECT_ID
from cinefactory.prompt_pack import load_bible
from cinefactory.niche_tools import NicheToolkit
from cf_a2_external_craft import load_for_role

class UnifiedA2ProductionTests(unittest.TestCase):
 def test_profile_consistent_with_canon(self):
  s=audit(ROOT)
  self.assertEqual(s["logic_consistency"],"PASS",s["profile_failures"])
  self.assertEqual(s["canon_character_tags"],list(TAGS))
  self.assertEqual((s["site_count"],s["space_count"],s["prop_count"]),(12,69,108))
  self.assertFalse(s["production_authorized"])
 def test_no_legacy_characters_in_active_visual_loader(self):
  b=load_bible("slow_english_a2",ROOT)
  self.assertEqual(b["series_id"],"bell_leaf")
  self.assertEqual([c["id"] for c in b["characters"]],list(TAGS))
  self.assertFalse(b["typography"]["caption_box"])
  self.assertTrue(all("SOURCE_CANON.png" in r for c in b["characters"] for r in c["references"]))
  for forbidden in ("mia","grandpa","biscuit"):
   self.assertNotIn(forbidden,[c["id"] for c in b["characters"]])
 def test_no_legacy_motion_or_narrator_in_actual_tool_router(self):
  kit=NicheToolkit.load("slow_english_a2",ROOT)
  self.assertEqual(kit.targets["shot_duration_seconds"],10)
  self.assertTrue(kit.targets["no_narrator"])
  ids=[x["id"] for variants in kit.stages.values() for x in variants]
  self.assertNotIn("ken_burns",ids)
  self.assertNotIn("kokoro",ids)
  self.assertNotIn("piper",ids)
  self.assertNotIn("owner_clips",ids)
  self.assertFalse(any(x.production for x in kit.plan().values()))
 def test_originals_not_falsely_approved(self):
  state=audit(ROOT)
  self.assertEqual(state["approved_voice_count"],0)
  self.assertIn("INDEPENDENT_ROOM_PLATES_NOT_APPROVED",state["production_blockers"])
  self.assertIn("INDEPENDENT_PROP_PLATES_NOT_APPROVED",state["production_blockers"])
 def test_visual_loader_fail_closed_on_canon_conflict(self):
  with patch("cinefactory.slow_english_unified.audit",return_value={"logic_consistency":"FAIL","profile_failures":["LEGACY_CHARACTERS_IN_ACTIVE_VISUAL"]}):
   with self.assertRaisesRegex(ValueError,"Canon mismatch"):
    load_bible("slow_english_a2",ROOT)
 def test_toolkit_loader_fail_closed_on_canon_conflict(self):
  with patch("cinefactory.slow_english_unified.audit",return_value={"logic_consistency":"FAIL","profile_failures":["LEGACY_CAMERA_MOTION_ACTIVE"]}):
   with self.assertRaisesRegex(ValueError,"Canon mismatch"):
    NicheToolkit.load("slow_english_a2",ROOT)
 def test_real_external_story_skills_optional_but_mapped(self):
  result=load_for_role("s04-causal-beat-architect",ROOT)
  if result["status"]=="EXTERNAL_CRAFT_READ_ONLY_LOADED":
   self.assertEqual([x["skill"] for x in result["items"]],["plot-structure","scene-craft"])
   self.assertTrue(all(x["sha256"] and x["technique_excerpt"] for x in result["items"]))
   self.assertFalse(result["model_or_cli_executed_from_external_repo"])
  else:
   self.assertEqual(result["status"],"OPTIONAL_REPO_NOT_INSTALLED")
 def test_no_legacy_generic_prompt_pack_for_bell_leaf(self):
  from cinefactory.prompt_pack import write_pack,write_sheets,picture_prompt
  with self.assertRaisesRegex(ValueError,"exact 10s source-locked shots"):
   write_pack("slow_english_a2",{},ROOT,None,ROOT)
  with self.assertRaisesRegex(ValueError,"immutable"):
   write_sheets("slow_english_a2",ROOT)
  shot=picture_prompt(load_bible("slow_english_a2",ROOT),{},{"setting":"Bellfern school"},"Lia discovers a bell")
  self.assertIn("no embedded text or subtitles",shot)
  self.assertNotIn("empty space at the bottom for subtitles",shot)

 def test_source_shas_match_visual_links(self):
  p,c,l,v,b,t=load(ROOT)
  for ch in b["characters"]:
   tag=ch["id"]
   self.assertEqual(ch["original_sha256"],c["characters"][tag]["locked_identity_original"]["sha256"])
   self.assertEqual(ch["story_permission"],"ARC_REVEAL_ONLY" if tag=="bangoai" else "USE_ONLY_WHEN_ACTIVE_TAG_IN_SHOT")

if __name__=="__main__":unittest.main()
