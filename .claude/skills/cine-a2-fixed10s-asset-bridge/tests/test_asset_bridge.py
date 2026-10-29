import unittest,sys, pathlib, json
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import audit_and_import
class TestAssetBridge(unittest.TestCase):
 def test_queue_total(self): self.assertEqual(len(audit_and_import.loadqueue()),1239)
 def test_room_prop_counts(self):
  a=audit_and_import.loadqueue();self.assertEqual([sum(x['type']==t for x in a) for t in ['location','prop']],[483,756])
 def test_unique_ids(self):
  a=audit_and_import.loadqueue();self.assertEqual(len({x['plate_id'] for x in a}),1239)
 def test_prompt_single_line(self):
  self.assertTrue(all('\n' not in x['prompt'] for x in audit_and_import.loadqueue()))
 def test_source_originals(self): self.assertEqual(audit_and_import.audit_characters()['verified_original'],10)
 def test_source_crop_hashes(self): self.assertEqual(audit_and_import.audit_characters()['verified_crop_hashes'],90)
 def test_location_sheet_count(self): self.assertEqual(audit_and_import.audit_locations()['sheets'],12)
 def test_none_approved(self): self.assertEqual(audit_and_import.audit_generated(ROOT)['approved_with_human_evidence'],0)
 def test_all_not_generated(self): self.assertEqual(audit_and_import.audit_generated(ROOT)['missing_images'],1239)
 def test_exact_10s_config(self):
  j=json.loads((ROOT/'config/CINE_A2_FIXED10S_REFERENCE_BINDING.json').read_text());self.assertEqual(j['shot_duration_seconds'],10.0)
 def test_all_10_tags(self):
  j=json.loads((ROOT/'config/CINE_A2_FIXED10S_REFERENCE_BINDING.json').read_text());self.assertEqual(len(j['character_tags']),10)
 def test_no_false_approved_location(self):
  for x in audit_and_import.loadqueue():self.assertEqual(x['status'],'PENDING_NOT_GENERATED')
if __name__=='__main__':unittest.main()
