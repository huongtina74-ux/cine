#!/usr/bin/env python3
"""Regenerate 90 EXACT PIXEL source crops from the 10 verified local originals.

Coordinates and the aggregated ordered RGBA hash were independently derived
from the owner-approved canonical ZIP. This DOES NOT generate new AI viewpoints
or approve new character designs. PNG file SHA can differ due to lossless encoding.
"""
from __future__ import annotations
import base64,hashlib,json,pathlib,shutil,struct,tempfile,sys
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.recover_bell_leaf_local_pixel_canon import ROOT_OUT,ORIGINAL_RGBA,sha_rgba
MANIFEST=ROOT/".claude/skills/cine-a2-muse-reference-anchoring/canon/ALL_90_SOURCE_CROPS_MANIFEST_V1_2.json"
MAP_B64=(
"AgCRABwB5QMXAqMCkgDFAL0CowKaAMUAYwGjAp0AxQBvA6MCoQDFACwBLQCPAO8BxAEtAJUA7wFjAi0AigDvAQMDLQCEAO8BAQCAAEYB1gMTAjIAkgC+ALoCMgCVAL4AawEyAJUAvgBcAzIApQC+AFgDOwGiADsBZQE7AaAAOwGuAjsBowA7AQoCOwGeADsBAgCAADAB4QJbAicAjgDEAMsBJwCLAMQA7QInAI8AxAA7AScAiwDEAIUDngNtADoBPgKeA28AOgEaA54DXwA6AaoCngNnADoBKADGAssAWQHpAjUAhgCNAHIDNQCfAI0AXwLnAIAAfABfAjUAhgCNAGgDnwFUAOAAWgKfAVYA4AANA58BVwDgALECnwFWAOAABQCiAtEAsgASAIoDwQCyAI8CigPIALIA5gCKA74AsgDDAYoDtgCyAKQCpALIAKsACgCkAsUAqwDDAaQC0wCrAOEApALUAKsAbgFGAJYCugGMApQDyQCkALgBlAO+AKQA7gCUA7AApAAYAJQDvQCkAJUCPwLVAAMBFAA/As0AAwHCAT8CzwADAeYAPwLaAAMBAgA2AF0BaAMnAy8BegDSAI8BLwGAANIAFwIvAX4A0gCdAi8BgQDSAAoDgQKHAGgBhwGBAnkAaAGKAoECeABoAQ8CgQJ2AGgBAQA8AEQBagMrAuUCmwDaAIsB5QKbANoAygLlAqAA2gBtA+UCoQDaAHYDIAGfAJcBlAEgAaUAlwHgAiABlACXAUACIAGfAJcBBAB7AHEBWQNfA/4CpwDeAH8B/gKcAN4AHwL+Ap0A3gC9Av4CmwDeAF8DLwGkAKwBdgEvAZwArAG9Ai8BmwCsARoCLwGaAKwBAgB+AFcBFANvAxgBoQDHABsCGAGkAMcAwwIYAaQAxwB2ARgBngDHAHMDAAKkANMBbQEAAqcA0wHIAgACpgDTARwCAAKoANMB"
)
MANIFEST_ORDER_SHA="93289db227ce85a0f09527940ba7ef6f17b2f6051e5500c5097ac9c97ab7e6b3"
PIXEL_HASH_ORDER_SHA="8c348f3fe45d132f8252a7e5ef3021782894cf6acf2edb6f28739a5f87f3b98b"
def shaf(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 j=json.loads(MANIFEST.read_text(encoding="utf-8"))
 arr=j["assets"]
 if len(arr)!=90:raise ValueError("90 source crops manifest mismatch")
 order="\n".join(x["tag"]+"|"+x["file"]+"|"+x["sha256"] for x in arr)
 if hashlib.sha256(order.encode()).hexdigest()!=MANIFEST_ORDER_SHA:
  raise ValueError("Source crop manifest changed; refuse coordinate binding")
 binary=base64.b64decode(MAP_B64)
 if len(binary)!=len(arr)*8:raise ValueError("Corrupted crop rectangle mapping")
 original={}
 for tag,digest in ORIGINAL_RGBA.items():
  f=ROOT_OUT/("assets/originals/"+tag+"_SOURCE_CANON.png")
  if not f.is_file():raise FileNotFoundError(str(f))
  with Image.open(f) as im:
   rgba=im.convert("RGBA")
  if sha_rgba(rgba)!=digest:raise ValueError("Source pixel identity mismatch "+tag)
  original[tag]=rgba
 records=[];pixel_hashes=[]
 target_meta=ROOT_OUT/"metadata/LOCAL_90_CROP_PIXEL_EQUIVALENCE_V1_2.json"
 if target_meta.exists():raise FileExistsError("90 crop pack already verified; refuse overwrite")
 with tempfile.TemporaryDirectory(prefix="cine_90_crops_") as tmp:
  stage=pathlib.Path(tmp)
  for i,row in enumerate(arr):
   x,y,w,h=struct.unpack_from("<4H",binary,i*8)
   src=original[row["tag"]]
   if x+w>src.width or y+h>src.height or not w or not h:raise ValueError("Invalid crop bounds")
   dest=stage/row["file"];dest.parent.mkdir(parents=True,exist_ok=True)
   clip=src.crop((x,y,x+w,y+h))
   clip.save(dest,"PNG")
   pix_sha=sha_rgba(clip)
   pixel_hashes.append(pix_sha)
   records.append({"tag":row["tag"],"file":row["file"],"crop_xywh":[x,y,w,h],
      "canonical_png_sha256":row["sha256"],"local_png_sha256":shaf(dest),
      "canonical_rgba_sha256":pix_sha,"provenance":"EXACT_SOURCE_PIXEL_CROP_NOT_NEW_VIEW"})
  digest=hashlib.sha256("\n".join(pixel_hashes).encode()).hexdigest()
  if digest!=PIXEL_HASH_ORDER_SHA:
   raise ValueError("At least one crop's pixels DIFFER from authoritative user Library source")
  # Each character gets a separate, collision-free directory, moved only after
  # ALL 90 pixels are checked.
  for tag in ORIGINAL_RGBA:
   src_dir=stage/"assets"/tag;out_dir=ROOT_OUT/"assets"/tag
   if out_dir.exists():raise FileExistsError("Existing crop directory; refuse overwrite "+str(out_dir))
   shutil.move(str(src_dir),str(out_dir))
  summary={"schema":"cine.source.crops.rgba_exact.v1.2","source":"owner_canon_archive_verified_pixel_rectangles",
    "originals_pixel_exact":10,"source_crops_pixel_exact":90,"new_generated_character_views_approved":0,
    "mode":"LOSSLESS_LOCAL_PNG_REENCODED_SAME_RGBA",
    "manifest_order_sha256":MANIFEST_ORDER_SHA,"pixel_order_sha256":PIXEL_HASH_ORDER_SHA,
    "crops":records}
  target_meta.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"status":"EXACT_SOURCE_CROPS_90_RGBA_VERIFIED",
   "characters":10,"crops":90,"generated_new_angles_approved":0,
   "metadata":str(target_meta)},ensure_ascii=False))
if __name__=="__main__":run()
