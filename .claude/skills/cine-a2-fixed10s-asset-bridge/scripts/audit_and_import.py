#!/usr/bin/env python3
"""Strict audit of CINE A2 FIXED10S reference images. Safe-by-default, no auto approvals."""
import argparse, csv, hashlib, json, pathlib, zipfile, re, shutil
from collections import Counter
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parent.parent
QUEUE=ROOT/'queue/ALL_1239_ASSET_WORK_ORDERS.jsonl'
CHAR_ARCHIVE=ROOT/'source_archives/CINE_BELL_LEAF_CANON_SOURCE_LOCK_V1_2_FINAL.zip'
CONCEPT_ARCHIVE=ROOT/'source_archives/CINE_BELLFERN_12_LOCATION_CONCEPT_SHEETS_DRAFT.zip'
TAGS=['bo','me','juno','Lia','bubu','bix','ongngoai','bangoai','ongnoi','banoi']

def checksum(data):return hashlib.sha256(data).hexdigest()
def loadqueue():
 import build_asset_queue
 # Always rebuild the queue from the authoritative CINE registry, not stale duplicates.
 build_asset_queue.main()
 return [json.loads(l) for l in QUEUE.read_text('utf-8').splitlines() if l.strip()]
def audit_characters():
 errors=[];info={}
 if not CHAR_ARCHIVE.is_file():return {'status':'MISSING','verified_original':0,'verified_crop':0,'errors':['Source character archive missing']}
 with zipfile.ZipFile(CHAR_ARCHIVE) as z:
  prefix='CINE_BELL_LEAF_CANON_SOURCE_LOCK_V1_2/'
  manifest=json.loads(z.read(prefix+'metadata/CHARACTER_CURRENT_SOURCE_LOCK.json'))
  prov=json.loads(z.read(prefix+'reports/ALL_90_SOURCE_CROPS_QC.json'))
  verified_original=0;verified_crop=0
  for tag in TAGS:
   c=manifest['characters'].get(tag)
   if not c:errors.append('Missing character '+tag);continue
   orig=c['locked_identity_original']
   name=prefix+orig['path']
   if name not in z.namelist() or checksum(z.read(name))!=orig['sha256']:
    errors.append('Original image SHA mismatch '+tag);continue
   verified_original+=1
  # Provenance record is a historical check of crop equality; here verify each crop file hash
  candidate_images=[s for s in z.namelist() if '/assets/' in s and '/angles/' in s or '/expressions/' in s or '/masters/' in s]
  # External manifest in this archive holds crop sha and original origin xy
  crop_manifest=json.loads(z.read(prefix+'metadata/ALL_90_SOURCE_CROPS_MANIFEST.json'))
  # Flexible manifest introspection below
  records=crop_manifest if isinstance(crop_manifest,list) else crop_manifest.get('assets',crop_manifest.get('items',[]))
  for asset in records:
   path=asset.get('path') or asset.get('file') or asset.get('native_image')
   expected=asset.get('sha256') or asset.get('native_sha256')
   if path and expected:
    target=prefix+path.lstrip('/')
    if target not in z.namelist() or checksum(z.read(target))!=expected:errors.append('Crop hash mismatch '+str(path))
    else:verified_crop+=1
  info={'verified_original':verified_original,'verified_crop_hashes':verified_crop,'reported_crop_provenance_from_previous_QC':prov.get('verified_count'), 'error_count':len(errors),'errors':errors,'status':'SOURCE_IDENTITY_VERIFIED_ONLY' if not errors and verified_original==10 else 'FAILED'}
 return info

def audit_locations():
 if not CONCEPT_ARCHIVE.exists():return {'status':'MISSING','sheets':0}
 with zipfile.ZipFile(CONCEPT_ARCHIVE) as z:
  j=json.loads(z.read('MANIFEST_12_DRAFT_NOT_APPROVED.json'))
  items=j.get('sites',[])
  bad=[]
  for x in items:
   if x['file'] not in z.namelist() or checksum(z.read(x['file']))!=x['sha256']:bad.append(x['site_id'])
  return {'sheets':len(items),'bad_hashes':bad,'status':'12_DRAFT_COMPOSITE_SHEETS_NOT_INDEPENDENT_PLATES' if not bad and len(items)==12 else 'FAILED'}

def audit_generated(output_root):
 jobs=loadqueue();done=[];invalid=[];review_pending=[];accepted=[];unseen=[];hash_seen={}
 for j in jobs:
  relpath=pathlib.PurePosixPath(j['output_relpath'])
  if relpath.is_absolute() or '..' in relpath.parts:raise ValueError('Invalid output path')
  file=output_root.joinpath(*relpath.parts)
  if not file.exists():unseen.append(j['plate_id']);continue
  try:
   with Image.open(file) as im:
    im.verify()
   with Image.open(file) as im:w,h=im.size
   if w<1280 or h<720 or abs(w/h-16/9)>0.012:
    invalid.append({'id':j['plate_id'],'cause':'NOT_NATIVE_16_9_720P_MINIMUM','size':[w,h]});continue
   hash=checksum(file.read_bytes())
   if hash in hash_seen:
    invalid.append({'id':j['plate_id'],'cause':'DUPLICATE_EXACT_IMAGE','other':hash_seen[hash]});continue
   hash_seen[hash]=j['plate_id']
   review_file=output_root/'review'/(j['plate_id']+'.json')
   if not review_file.exists():review_pending.append(j['plate_id']);continue
   report=json.loads(review_file.read_text('utf-8'))
   required=['reviewer','reviewed_at_utc','image_sha256','visual_identity_match','true_camera_view','spatial_topology_match','single_frame_no_text','neutral_color_qc','approved']
   if any(k not in report for k in required) or report['image_sha256']!=hash or not all(report[k] is True for k in ['visual_identity_match','true_camera_view','spatial_topology_match','single_frame_no_text','neutral_color_qc','approved']) or not report['reviewer']:
    invalid.append({'id':j['plate_id'],'cause':'REVIEW_FILE_INCOMPLETE_OR_REJECTED'});continue
   accepted.append(j['plate_id'])
  except Exception as exc:invalid.append({'id':j['plate_id'],'cause':'READ_OR_QC_ERROR','info':str(exc)})
 return {'expected':len(jobs),'missing_images':len(unseen),'present_unreviewed':len(review_pending),'invalid':len(invalid),'approved_with_human_evidence':len(accepted),'production_ready':len(accepted)==len(jobs) and not invalid,'sample_invalid':invalid[:12]}

def main():
 a=argparse.ArgumentParser();a.add_argument('--render-root',type=pathlib.Path,default=ROOT);a.add_argument('--out',type=pathlib.Path,default=ROOT/'docs'/'CURRENT_READINESS_REPORT.json');opts=a.parse_args()
 r={'series':'Bell & Leaf / Slow English A2 STRICT10S','character_source_audit':audit_characters(),'concept_location_audit':audit_locations(),'independent_plates':audit_generated(opts.render_root),'approved_voice_wav':'NOT_PROVIDED_OR_VERIFIED','muse_video_real_10s_e2e':'NOT_VERIFIED','locked_time_seconds_per_shot':10,'final_production_status':'NOT_READY'}
 opts.out.parent.mkdir(exist_ok=True,parents=True);opts.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False,indent=2))
if __name__=='__main__':main()