import pathlib,sys,json,unittest
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import build_asset_queue,audit_and_import
class CanonicalAssetQueueTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  build_asset_queue.main()
  cls.jobs=audit_and_import.loadqueue()
 def test_all_jobs(self):self.assertEqual(len(self.jobs),1239)
 def test_room_count(self):self.assertEqual(sum(x['type']=='location' for x in self.jobs),483)
 def test_prop_count(self):self.assertEqual(sum(x['type']=='prop' for x in self.jobs),756)
 def test_12_sites(self):self.assertEqual(len(set(x['site_id'] for x in self.jobs)),12)
 def test_no_duplicate_plate(self):self.assertEqual(len(set(x['plate_id'] for x in self.jobs)),1239)
 def test_single_line(self):self.assertTrue(all('\n' not in x['prompt'] for x in self.jobs))
 def test_separate_one_blank_line(self):
  self.assertEqual(len((ROOT/'queue/FLOW_483_LOCATION_ONE_LINE_BLANK.txt').read_text().strip().split('\n\n')),483)
 def test_no_fake_approval(self):self.assertTrue(all(x['status']=='PENDING_NOT_GENERATED' for x in self.jobs))
 def test_d55(self):self.assertTrue(all('D55' in x['prompt'] for x in self.jobs))
 def test_real_reverse(self):self.assertTrue(any('NEVER mirror' in x['prompt'] for x in self.jobs if x['view']=='REVERSE_TRUE'))
 def test_missing_images_still_block(self):self.assertEqual(audit_and_import.audit_generated(ROOT)['approved_with_human_evidence'],0)
 def test_10s_config(self):
  c=json.loads((ROOT/'config/CINE_A2_FIXED10S_REFERENCE_BINDING.json').read_text())
  self.assertEqual(c['shot_duration_seconds'],10.0)
if __name__=='__main__':unittest.main()
