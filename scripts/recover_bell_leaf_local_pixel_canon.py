#!/usr/bin/env python3
"""Recover Bell & Leaf originals from pixel-identical locally owned PNGs.

The local PNG compression differs from the author's source ZIP, but their
decoded RGBA pixels (including alpha) were independently compared against the
actual user-approved source archive. Never claim byte-identical canonical SHA.

Source anchors and source-only crops are NOT newly approved AI angles.
No automatic model redesign, face swapping or artistic approval.
"""
from __future__ import annotations
import hashlib,json,os,pathlib,shutil,sys,tempfile
from PIL import Image

ROOT=pathlib.Path(__file__).resolve().parents[1]
LOCK=ROOT/".claude/skills/cine-a2-muse-reference-anchoring/canon/CHARACTER_CURRENT_SOURCE_LOCK_V1_2.json"
QC=ROOT/".claude/skills/cine-a2-muse-reference-anchoring/canon/PIXEL_PROVENANCE_QC_V1_2.json"
ROOT_OUT=ROOT/"assets/canon/character_refs/slow_english_a2/bell_leaf/v1_2_user_source"

# Reference RGBA SHA-256, independently read from the authoritative user Library
# source ZIP. These digests are NOT hashes of the PNG container bytes.
ORIGINAL_RGBA={
 "bo":"86b850cdb9c8cbd5ad42a6e99a39fe71d761f97c74d7ae1d82a52fb82d8ecd98",
 "me":"71e5dfe839dac6ade52888d88cbaeaaaf4e29053dbc306118ad410b65b237ba6",
 "juno":"21be64b22249782169c7da23e89f33f6d64e03ab5c85c4be489cf2bbd2458435",
 "Lia":"1367b6629b57bb58c16d116465f3ca8fe52b16d4bfb08cd3424ef34c07d8bfeb",
 "bubu":"0166c9ea1a4fc1be3a7553974b34c393f393670b014e4f400567fbeb3c0d4ccd",
 "bix":"2acfb4d292b54e6419b97bdde521a3592deaf992e2f1985bb639f5ab3aef3cf6",
 "ongngoai":"8ee8403e6da36a23eb4abf11e838437617cea7d44ff46827ab8c0c0aef1d1fdb",
 "bangoai":"0fe1f0ce38793b766c459fdec7ae6d5be3470f4760ff8081500fd382b4cb18ea",
 "ongnoi":"2327f517b1678ab127fb4ee573c6e2b7a529b311df5809d85ad497ca21c8274f",
 "banoi":"13c40db6a0b884f84b3170e496479ffb0730984f8b88971d0351bb5486e4ebc8"}
MASTER_RGBA={
 "bo":"a66a99828646f86e434c6886ce40451a6f085a1e2983ddbf86538960f22d5b09",
 "me":"bbd2eb807c399fce8b8c3d45dc257e2b9545a34c014dd7b83f0e664a6f859689",
 "juno":"5dad9bcfa870f8386a2615d793840086c5fb595d2c3357b0890da4b476edb8e2",
 "Lia":"a6db0c67e70c38707a0b6b10b12a1abe45e9ecb714ebc698d81e1b39243b718f",
 "bubu":"876d1137e9b038f81c1f29fc2dec379609927abad181f3e1ac8d0941e81b4ebe",
 "bix":"601e25ee04dcf272b301dab2765bb6bc17004347e5411db7bf261ec3cb801ade",
 "ongngoai":"d77a618a14eb92c9095f7df3cc141e37ba7dc136beb32e6cfb5a626898801592",
 "bangoai":"013b5a840f6d24fee4d1cd5f03d40da1d5c1d888e94dc1481e4f42695099c7a6",
 "ongnoi":"884c898537369786c622b2fc62853461cddf657b210bf2a33da72135bd143bee",
 "banoi":"166470fb15349f56cdede52a9903e6b711fbb9187c00a0acd1752f878b53729a"}
BUBU_DETAIL_RGBA={
 "assets/masters/bubu_TAIL_SPARKLE_DETAIL_SOURCE.png":("6ac2bd4b964669c7090de4824d510ea04deaf4a5df13646081e392a4539b1126",(332,479)),
 "assets/masters/bubu_HERO_FACE_AND_BODY_SOURCE.png":("f4c8138ebf8928c1288fde4769a6e621269a66ba93c88af4576d5bdf678616c6",(390,646))}
def sha_bytes(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sha_rgba(im):return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()
def get_local_dir():
 explicit=os.environ.get("CINE_BELL_LEAF_ORIGINAL_IMAGES_DIR")
 if explicit:
  folder=pathlib.Path(explicit).expanduser()
  if not (folder.is_dir() and (folder/"bo.png").is_file()):
   raise FileNotFoundError("CINE_BELL_LEAF_ORIGINAL_IMAGES_DIR must contain approved bo.png")
  return folder
 d=pathlib.Path.home()/"Downloads"
 if not d.is_dir():raise FileNotFoundError("Local Downloads directory not available")
 matches=[p for p in d.iterdir() if p.is_dir() and p.name.startswith("SLOW NGLISH")]
 if len(matches)!=1:raise ValueError("Original local image folder is missing or ambiguous; set CINE_BELL_LEAF_ORIGINAL_IMAGES_DIR")
 return matches[0]
def recover():
 lock=json.loads(LOCK.read_text(encoding="utf-8"))
 qc=json.loads(QC.read_text(encoding="utf-8"))
 crop_info={x["tag"]:x for x in qc["items"]}
 if len(crop_info)!=10 or len(lock["characters"])!=10:
  raise ValueError("Unexpected canon count; abort")
 local=get_local_dir()
 if ROOT_OUT.exists():raise FileExistsError("Canonical source already installed; refuse overwrite")
 # Verify every input before writing; no pixel tolerance or perceived-similarity
 # threshold. Both the 4 channels and the size must match byte-for-byte in RAM.
 data={}
 for tag,entry in lock["characters"].items():
  source=local/(tag+".png")
  if not source.is_file():raise FileNotFoundError(str(source))
  with Image.open(source) as image:
   im=image.convert("RGBA")
  if sha_rgba(im)!=ORIGINAL_RGBA[tag] or tuple(im.size)!=tuple(crop_info[tag]["source_size"]):
   raise ValueError("Not exact Canon RGBA pixels: "+tag)
  data[tag]=(source,im)
 records={}
 ROOT_OUT.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix="cine_a2_pixel_exact_") as temp:
  stage=pathlib.Path(temp)
  for tag,entry in lock["characters"].items():
   src,im=data[tag]
   original=entry["locked_identity_original"]
   rel=original["path"]
   dst=stage/rel;dst.parent.mkdir(parents=True,exist_ok=True)
   shutil.copy2(src,dst)
   records[rel]={"canonical_png_sha256":original["sha256"],
                 "local_png_sha256":sha_bytes(dst),
                 "canonical_rgba_sha256":ORIGINAL_RGBA[tag],
                 "dimensions":list(im.size),"role":"ORIGINAL_IDENTITY_PIXELS",
                 "source_existing_user_file":str(src)}
   crop=entry["source_master_crop"]
   rel=crop["path"];xy=crop["source_xy"];wh=crop_info[tag]["crop_size"]
   view=im.crop((xy[0],xy[1],xy[0]+wh[0],xy[1]+wh[1]))
   if sha_rgba(view)!=MASTER_RGBA[tag]:raise ValueError("Exact master pixels mismatch "+tag)
   dst=stage/rel;dst.parent.mkdir(parents=True,exist_ok=True)
   view.save(dst,"PNG")
   records[rel]={"canonical_png_sha256":crop["sha256"],"local_png_sha256":sha_bytes(dst),
                 "canonical_rgba_sha256":MASTER_RGBA[tag],"dimensions":list(wh),
                 "role":"SOURCE_PIXEL_CROP_NOT_A_NEW_ANGLE"}
  im=data["bubu"][1]
  bubu=lock["characters"]["bubu"]
  for cue in bubu["mandatory_visual_cues"]:
   rel=cue["file"];digest,wh=BUBU_DETAIL_RGBA[rel]
   x,y=cue["origin_xy"]
   view=im.crop((x,y,x+wh[0],y+wh[1]))
   if sha_rgba(view)!=digest:raise ValueError("Bubu magical tail/face pixels mismatch")
   dst=stage/rel;dst.parent.mkdir(parents=True,exist_ok=True)
   view.save(dst,"PNG")
   records[rel]={"canonical_png_sha256":cue["sha256"],"local_png_sha256":sha_bytes(dst),
                 "canonical_rgba_sha256":digest,"dimensions":list(wh),
                 "role":"SOURCE_BUBU_SPARKLE_CUE"}
  meta=stage/"metadata/LOCAL_PIXEL_EQUIVALENCE_V1_2.json"
  meta.parent.mkdir(parents=True,exist_ok=True)
  status={"schema":"CINE_LOCAL_RGBA_PIXEL_EQUIVALENCE_V1_2",
          "origin":"USER_APPROVED_ORIGINAL_LOCAL_PNGS_AND_INDEPENDENT_LIBRARY_RGBA_REFERENCE",
          "canon_version":"v1_2","bytes_identical_to_library_png":False,
          "rgba_pixels_identical_to_library":True,"original_images_verified":10,
          "source_master_crops_rebuilt_from_identical_pixels":10,
          "bubu_required_cues_rebuilt_from_identical_pixels":2,
          "generated_new_angles_approved":0,
          "media_provider_uploads_completed":False,
          "files":records}
  meta.write_text(json.dumps(status,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
  # Strong full-tree post-write verification before atomic directory rename.
  for rel,row in records.items():
   f=stage/rel
   if sha_bytes(f)!=row["local_png_sha256"]:raise RuntimeError("Copy mismatch "+rel)
   with Image.open(f) as p:
    if sha_rgba(p)!=row["canonical_rgba_sha256"]:raise RuntimeError("Pixels mismatch "+rel)
  shutil.move(str(stage),str(ROOT_OUT))
 print(json.dumps({"status":"10_ORIGINAL_RGBA_CANON_SOURCE_ANCHORS_INSTALLED",
                   "destination":str(ROOT_OUT),"source_pixel_matched":10,
                   "source_only_crops":12,"new_ai_angles_approved":0,
                   "note":"PNG file bytes differ from library, but 4-channel pixel digests match exact original"},
                  ensure_ascii=False))
if __name__=="__main__":recover()
