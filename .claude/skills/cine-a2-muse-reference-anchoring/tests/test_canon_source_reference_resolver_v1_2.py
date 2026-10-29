import unittest,tempfile,pathlib,shutil,sys
from resolve_canon_source_references import resolve,CanonSourceError
ROOT=pathlib.Path(__file__).resolve().parents[1]

class LockedCharacterSources(unittest.TestCase):
 def test_lia_and_bubu_only(self):
  x=resolve(ROOT,['Lia','bubu'])
  self.assertEqual(x['reference_count'],3)
  self.assertEqual([t['tag'] for t in x['character_references']],['Lia','bubu','bubu'])
  self.assertTrue(any('TAIL_SPARKLE' in e['local_path'] for e in x['character_references']))
  self.assertTrue(all(e['attachment_media_id'] is None for e in x['character_references']))
 def test_zero_character_shot(self):self.assertEqual(resolve(ROOT,[])['reference_count'],0)
 def test_unknown_tag_fails(self):
  with self.assertRaises(CanonSourceError):resolve(ROOT,['unknown'])
 def test_duplicate_tag_fails(self):
  with self.assertRaises(CanonSourceError):resolve(ROOT,['Lia','Lia'])
 def test_all_ten_locked_sources(self):self.assertEqual(resolve(ROOT,['bo','me','juno','Lia','bubu','bix','ongngoai','bangoai','ongnoi','banoi'])['reference_count'],11)
 def test_missing_source_blocks(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);(r/'metadata').mkdir();shutil.copy(ROOT/'metadata/CHARACTER_CURRENT_SOURCE_LOCK.json',r/'metadata/CHARACTER_CURRENT_SOURCE_LOCK.json')
   with self.assertRaises(CanonSourceError):resolve(r,['Lia'])
 def test_original_reference_hash(self):
  x=resolve(ROOT,['Lia','bubu'],include_original=True)
  self.assertEqual(x['reference_count'],5)
 def test_bad_reference_type(self):
  with self.assertRaises(CanonSourceError):resolve(ROOT,'Lia')

if __name__=='__main__':unittest.main()