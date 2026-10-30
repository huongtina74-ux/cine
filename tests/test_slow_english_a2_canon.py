import json, tempfile, csv, hashlib
from pathlib import Path
import unittest
from cinefactory.studio.slow_english_a2 import BellLeafCanon,CanonError
class SlowEnglishCanonTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  self.p={"project_id":"slow_english_a2_bell_leaf","active_tags":["Lia","bubu"],"source_registries":{"sites":"site.json","characters":"char.json","room_views":"room.csv","prop_views":"prop.csv","voices":"voice.json","physical_character_files":"sources"}}
  def write(path,data):
   p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data))
  write("config/niches/slow_english_a2/production.json",self.p)
  write("site.json",{"sites":[{"site_id":"BELL"}],"spaces":[{"site_id":"BELL","space_id":"BH-EXT"}],"props":[]})
  write("char.json",{"characters":{"Lia":{"locked_identity_original":{"path":"Lia.png","sha256":"f"*64}},"bubu":{"locked_identity_original":{"path":"bubu.png","sha256":"f"*64},"mandatory_visual_cues":[{"path":"tail.png","sha256":"f"*64},{"path":"hero.png","sha256":"f"*64}]}}})
  write("voice.json",{"voices":{"Lia":{"approval_status":"PENDING_VOICE_WAV"}}})
  for name,rows in (("room.csv",[{"plate_id":"a","site_id":"BELL","space_id":"BH-EXT","view":"FORWARD","approval_status":"PENDING_NOT_GENERATED","human_approved":"NO","geometry_verified":"NO","d55_review":"NO","image_file":"","image_sha256":""}]),("prop.csv",[{"plate_id":"p","site_id":"BELL","space_id":"BH-EXT","prop_id":"door","view":"FRONT","approval_status":"PENDING_NOT_GENERATED","human_approved":"NO","scale_verified":"NO","d55_review":"NO","image_file":"","image_sha256":""}])):
   with (self.root/name).open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
  self.c=BellLeafCanon(self.root);self.shot={"shot_id":"1","duration_seconds":10,"activeCharacterTags":["Lia"],"location_id":"BELL","space_id":"BH-EXT","location_view_id":"FORWARD"}
 def tearDown(self):self.temp.cleanup()
 def test_no_fabricated_approval(self):self.assertIn("LOCATION_VIEW_NOT_APPROVED:a",self.c.resolve_shot(self.shot)["blockers"])
 def test_one_visible(self):self.assertEqual(self.c.resolve_shot(self.shot)["activeCharacterTags"],["Lia"])
 def test_zero_characters(self):self.assertEqual(self.c.resolve_shot({**self.shot,"activeCharacterTags":[]})["character_refs"],[])
 def test_wrong_case(self):
  with self.assertRaises(CanonError):self.c.resolve_shot({**self.shot,"activeCharacterTags":["lia"]})
 def test_duration(self):
  with self.assertRaises(CanonError):self.c.resolve_shot({**self.shot,"duration_seconds":8})
 def test_speaker_blocks(self):self.assertIn("VOICE_WAV_NOT_APPROVED:Lia",self.c.resolve_shot({**self.shot,"dialogue":[{"speaker_tag":"Lia","text":"Hello"}]})["blockers"])
 def test_bubu_detail(self):self.assertIn("CHARACTER_SOURCE_MISSING_OR_CHANGED:bubu",self.c.resolve_shot({**self.shot,"activeCharacterTags":["bubu"]})["blockers"])
 def test_one_line(self):self.assertNotIn("\n",self.c.flow_prompt(self.shot))
 def test_no_narrator(self):
  with self.assertRaises(CanonError):self.c.resolve_shot({**self.shot,"dialogue":[{"speaker_tag":"narrator","text":"Hello"}]})
if __name__=="__main__":unittest.main()
