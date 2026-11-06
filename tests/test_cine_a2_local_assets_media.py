"""Offline unit tests for Bell & Leaf secure asset, voice and media gates."""
from __future__ import annotations
import hashlib, importlib.util, json, pathlib, shutil, subprocess, sys, tempfile, unittest, wave
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.cf_a2_media_release_gate import inspection, probe
from tools.cf_a2_voxcpm_cast import create_plan,LINES
from scripts.install_a2_source_bundle import install_bundle

class BellLeafLocalIntegrationTests(unittest.TestCase):
 def setUp(self):
  self.profile=json.loads((ROOT/"config/niches/slow_english_a2/production.json").read_text(encoding="utf-8"))
  self.voices=json.loads((ROOT/"config/niches/slow_english_a2/voice_registry.json").read_text(encoding="utf-8"))["voices"]
  self.shot=json.loads((ROOT/"examples/slow_english_a2_ep001_preflight.json").read_text(encoding="utf-8"))["shots"][0]
 def test_cast_all_exact_ten_tags(self):
  self.assertEqual(set(self.voices),set(LINES))
  plan=create_plan(self.voices,list(self.voices))
  self.assertEqual(len(plan),10)
  self.assertTrue(all(x["candidate_text"].startswith("(") for x in plan))
  self.assertTrue(all(x["status"]=="PENDING_CANDIDATE_AUDIO_NOT_APPROVED" for x in plan))
 def test_voice_metadata_cannot_fake_approval(self):
  self.assertEqual(sum(x.get("approval_status")=="APPROVED" for x in self.voices.values()),0)
  self.assertTrue(all(x.get("sample_wav") is None for x in self.voices.values()))
 def test_fixed_ten_second_shot(self):
  self.assertEqual(self.shot["duration_seconds"],10)
  report=inspection(ROOT,self.shot)
  self.assertEqual(report["status"],"BLOCKED")
  self.assertIn("REAL_MUSE_MP4_MISSING",report["blockers"])
  self.assertIn("APPROVED_DIALOGUE_WAV_MISSING",report["blockers"])
  self.assertIn("LIP_SYNC_CUES_MISSING",report["blockers"])
  self.assertIn("HUMAN_ART_LIPSYNC_QC_MISSING",report["blockers"])
 def test_reject_wrong_duration(self):
  shot=dict(self.shot,duration_seconds=8)
  report=inspection(ROOT,shot)
  self.assertTrue(any("INVALID_SHOT:" in x for x in report["blockers"]))
 def test_importer_does_not_create_fake_assets(self):
  with self.assertRaises(FileNotFoundError):
   install_bundle(ROOT/"MISSING_SOURCE_ZIP_NEVER_CREATED.zip",ROOT)
 def test_bubu_sparkle_and_bix_bell_canon(self):
  canon=json.loads((ROOT/".claude/skills/cine-a2-muse-reference-anchoring/canon/CHARACTER_CURRENT_SOURCE_LOCK_V1_2.json").read_text(encoding="utf-8"))
  self.assertGreaterEqual(len(canon["characters"]["bubu"]["mandatory_visual_cues"]),2)
  self.assertIn("NO BELL",canon["characters"]["bix"]["visual_canon_important"])
 def test_media_ffprobe_detects_fps_and_frames(self):
  if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):self.skipTest("FFmpeg absent")
  with tempfile.TemporaryDirectory() as td:
   video=pathlib.Path(td)/"synthetic_not_muse.mp4"
   cmd=["ffmpeg","-hide_banner","-loglevel","error","-f","lavfi","-i","color=c=black:s=640x360:r=24:d=1","-frames:v","24","-c:v","mpeg4","-y",str(video)]
   r=subprocess.run(cmd,capture_output=True,text=True,timeout=35)
   self.assertEqual(r.returncode,0,r.stderr)
   meta=probe(video,True)
   self.assertEqual(int(meta["streams"][0]["nb_read_frames"]),24)
   report=inspection(ROOT,self.shot,video=video)
   self.assertIn("VIDEO_NOT_EXACT_240_FRAMES_24FPS_10S",report["blockers"])
   self.assertIn("VIDEO_NOT_16_9_MIN_720P",report["blockers"])
   self.assertEqual(report["status"],"BLOCKED")
 def test_dialogue_worker_never_falls_back_to_random_voice(self):
  from tools.cf_a2_voxcpm_dialogue import plan_shot
  x=plan_shot(ROOT,self.shot)
  self.assertEqual(x["status"],"BLOCKED")
  self.assertTrue(any(z.startswith("VOICE_NOT_HUMAN_APPROVED:Lia") for z in x["blockers"]))
  self.assertFalse(x["voice_approved_in_this_run"])
  self.assertEqual(x["orders"][0]["tag"],"Lia")
 def test_a2_preview_has_pitch_preserving_tempo_chaining(self):
  from tools.cf_a2_voice_audition_qc import atempo_chain
  self.assertIn("atempo=0.5",atempo_chain(.30))
  self.assertIn("atempo=0.600000",atempo_chain(.30))
 def test_ten_character_voice_source_identity(self):
  self.assertEqual(len(self.voices),10)
  self.assertEqual(self.voices["bubu"]["voice_profile_key"],"CINE_BELL_LEAF_BUBU")
  self.assertEqual(self.voices["Lia"]["voice_profile_key"],"CINE_BELL_LEAF_LIA")

 def test_all_ten_exact_character_source_pixels_when_installed(self):
  from cinefactory.studio.slow_english_a2 import BellLeafCanon
  from scripts.recover_bell_leaf_local_pixel_canon import ROOT_OUT
  if not ROOT_OUT.exists():
   self.skipTest("Exact RGBA local Canon source not installed")
  sample=dict(self.shot,activeCharacterTags=list(self.voices),dialogue=[])
  x=BellLeafCanon(ROOT).resolve_shot(sample)
  self.assertEqual(len(x["character_refs"]),12)
  self.assertFalse(any(b.startswith("CHARACTER_SOURCE_MISSING_OR_CHANGED") for b in x["blockers"]))
  self.assertTrue(any(z["tag"]=="bubu" for z in x["character_refs"]))
  self.assertEqual(x["status"],"BLOCKED_FOR_PRODUCTION")  # no approved room plate
 def test_pixel_canon_manifest_and_sha_are_pinned(self):
  from cinefactory.studio.slow_english_a2 import _verify_character_source
  from scripts.recover_bell_leaf_local_pixel_canon import ROOT_OUT, ORIGINAL_RGBA
  if not ROOT_OUT.exists():
   self.skipTest("Canon source not installed")
  m=json.loads((ROOT_OUT/"metadata/LOCAL_PIXEL_EQUIVALENCE_V1_2.json").read_text(encoding="utf-8"))
  self.assertEqual(m["original_images_verified"],10)
  self.assertEqual(m["generated_new_angles_approved"],0)
  name="assets/originals/Lia_SOURCE_CANON.png"
  entry=m["files"][name]
  self.assertEqual(entry["canonical_rgba_sha256"],ORIGINAL_RGBA["Lia"])
  self.assertNotEqual(entry["local_png_sha256"],entry["canonical_png_sha256"])
  self.assertIsNotNone(_verify_character_source(ROOT_OUT,name,entry["canonical_png_sha256"]))
  with tempfile.TemporaryDirectory() as td:
   from PIL import Image
   d=pathlib.Path(td)
   p=d/name;p.parent.mkdir(parents=True)
   with Image.open(ROOT_OUT/name) as im:
    im=im.convert("RGBA");im.putpixel((0,0),(19,31,43,255));im.save(p)
   meta=d/"metadata";meta.mkdir()
   invalid=dict(m);invalid["files"]=dict(m["files"])
   invalid["files"][name]=dict(entry)
   invalid["files"][name]["local_png_sha256"]=hashlib.sha256(p.read_bytes()).hexdigest()
   (meta/"LOCAL_PIXEL_EQUIVALENCE_V1_2.json").write_text(json.dumps(invalid),encoding="utf-8")
   self.assertIsNone(_verify_character_source(d,name,entry["canonical_png_sha256"]))

 def test_90_source_crops_are_only_exact_original_pixels(self):
  from scripts.recover_bell_leaf_90_source_crops import ROOT_OUT,PIXEL_HASH_ORDER_SHA
  from PIL import Image
  p=ROOT_OUT/"metadata/LOCAL_90_CROP_PIXEL_EQUIVALENCE_V1_2.json"
  if not p.exists():self.skipTest("Verified 90 local source crops not installed")
  rows=json.loads(p.read_text(encoding="utf-8"))
  self.assertEqual(rows["source_crops_pixel_exact"],90)
  self.assertEqual(rows["new_generated_character_views_approved"],0)
  digests=[]
  for x in rows["crops"]:
   image=ROOT_OUT/x["file"]
   self.assertTrue(image.is_file(),x["file"])
   self.assertEqual(hashlib.sha256(image.read_bytes()).hexdigest(),x["local_png_sha256"])
   with Image.open(image) as view:
    digests.append(hashlib.sha256(view.convert("RGBA").tobytes()).hexdigest())
   self.assertEqual(digests[-1],x["canonical_rgba_sha256"])
  self.assertEqual(hashlib.sha256("\n".join(digests).encode()).hexdigest(),PIXEL_HASH_ORDER_SHA)

 def test_character_ref_upload_sha_is_actual_file_bytes_when_installed(self):
  from cinefactory.studio.slow_english_a2 import BellLeafCanon
  from scripts.recover_bell_leaf_local_pixel_canon import ROOT_OUT
  if not ROOT_OUT.exists():self.skipTest("Owner original PNGs not installed in CI")
  shot=dict(self.shot,activeCharacterTags=["Lia","bubu"],dialogue=[])
  state=BellLeafCanon(ROOT).resolve_shot(shot)
  self.assertEqual(len(state["character_refs"]),4)
  expected=json.loads((ROOT/".claude/skills/cine-a2-muse-reference-anchoring/canon/CHARACTER_CURRENT_SOURCE_LOCK_V1_2.json").read_text(encoding="utf-8"))["characters"]
  for row in state["character_refs"]:
   file=pathlib.Path(row["path"])
   self.assertEqual(row["sha256"],hashlib.sha256(file.read_bytes()).hexdigest())
   self.assertEqual(len(row["canonical_source_sha256"]),64)
   self.assertIn(row["image_identity_provenance"],("EXACT_ORIGINAL_PNG_BYTES","PINNED_RGBA_PIXEL_EQUIVALENT"))
  lia=next(x for x in state["character_refs"] if x["tag"]=="Lia")
  self.assertEqual(lia["canonical_source_sha256"],expected["Lia"]["locked_identity_original"]["sha256"])

if __name__=="__main__":unittest.main()
