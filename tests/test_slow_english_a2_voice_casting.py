import json, pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE=ROOT/"config/niches/slow_english_a2"
TAGS={"bo","me","juno","Lia","bubu","bix","ongngoai","bangoai","ongnoi","banoi"}
class VoiceCastingContract(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=json.loads((BASE/"voice_registry.json").read_text(encoding="utf-8"))
 def test_ten_exact_tags(self):self.assertEqual(set(self.d["voices"]),TAGS)
 def test_no_narrator(self):self.assertTrue(self.d["no_narrator"]);self.assertNotIn("narrator",self.d["voices"])
 def test_ten_proposed_profiles(self):
  self.assertEqual({v["display_name"] for v in self.d["voices"].values()}, {"Evan","Mara","Juno","Lia","Bubu","Bix","Orin","Maternal Grandmother","Paternal Grandfather","Paternal Grandmother"})
 def test_complete_direction(self):
  for tag,v in self.d["voices"].items():
   for key in ("personality","voice_timbre","delivery_direction","distinguish_from","voice_casting_prompt"):
    self.assertTrue(v.get(key),f"{tag} missing {key}")
 def test_no_fictitious_audio(self):
  for v in self.d["voices"].values():
   self.assertEqual(v["approval_status"],"PENDING_WAV_AND_RIGHTS_APPROVAL")
   self.assertIsNone(v["voice_id"]);self.assertIsNone(v["sample_wav"]);self.assertIsNone(v["sample_sha256"])
  self.assertEqual(self.d["approved_voice_count"],0)
 def test_distinct_profile_keys(self):
  self.assertEqual(len({v["voice_profile_key"] for v in self.d["voices"].values()}),10)
 def test_conditional_maternal_grandmother(self):
  self.assertEqual(self.d["voices"]["bangoai"]["conditional_story_permission"],"REQUIRE_VEYLORA_ARC_APPROVAL")
 def test_paces_not_invented(self):
  self.assertTrue(all(v["target_wpm"] is None for v in self.d["voices"].values()))
 def test_prompts_one_line_each(self):
  s=(BASE/"voice_casting_prompts.txt").read_text(encoding="utf-8")
  self.assertEqual(len(s.strip().split("\n\n")),10)
  self.assertTrue(all("\n" not in p for p in s.strip().split("\n\n")))
 def test_project_voice_readiness_blocked(self):
  prod=json.loads((BASE/"production.json").read_text(encoding="utf-8"))
  self.assertEqual(prod["readiness"]["voice_samples_approved"],0)
  self.assertEqual(prod["source_registries"]["voices"],"config/niches/slow_english_a2/voice_registry.json")
if __name__=="__main__":unittest.main()
