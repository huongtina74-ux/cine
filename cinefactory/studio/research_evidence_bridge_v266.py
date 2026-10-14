"""v266: read-only research evidence handoff for explicitly selected Maizen pilot.

Carries source citations/metadata and source G02 uncertainty into the company
project. Does NOT convert tentative competitors into film certified expertise,
G02 into PASS, or rights into an approval. Source hashes enforce provenance.
"""
from __future__ import annotations
import hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCES={
 "public_video_metadata":"data/research/youtube_breakout/approved_deep_research/maizen_keyword_fresh_probe_v259.json",
 "public_about_observations":"data/research/youtube_breakout/approved_deep_research/maizen_canonical_about_join_v259.json",
 "unsigned_g02_review":"data/verification/v263_maizen_full_story_assets/g02_unsigned_independent_review_queue.json",
}
def _obj(p:Path)->dict:
 obj=json.loads(p.read_text(encoding="utf-8-sig"))
 if not isinstance(obj,dict):raise ValueError("NOT_OBJECT")
 return obj
def _hash(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()

def build(root:Path,project_id:str,*,write:bool=True)->dict:
 if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{1,99}",project_id):
  raise ValueError("INVALID_PROJECT_ID")
 observed={}
 hashes={}
 for key,rel in SOURCES.items():
  path=root/rel
  if not path.is_file():raise FileNotFoundError("RESEARCH_SOURCE_MISSING:"+rel)
  observed[key]=_obj(path);hashes[rel]=_hash(path)
 g02=observed["unsigned_g02_review"]
 meta=observed["public_video_metadata"]
 about=observed["public_about_observations"]
 if g02.get("original_review_windows")!=120 or g02.get("reviewer_signoff")!="NOT_SIGNED":
  raise ValueError("G02_REVIEW_INVARIANT_CHANGED")
 if meta.get("candidate_ids",0)<50 or meta.get("metadata_attempted",0)<50:
  raise ValueError("PUBLIC_VIDEO_COVERAGE_INSUFFICIENT_FOR_PRIOR_SNAPSHOT")
 if about.get("strict_new_channel_two_distinct_million_verified") is not False:
  raise ValueError("UNSUPPORTED_NEWBORN_WINNER_PROMOTION")
 videos=[]
 for x in meta.get("results",[]):
  if not isinstance(x,dict) or not x.get("id"):continue
  video_id=x["id"]
  if not re.fullmatch(r"[A-Za-z0-9_-]{11}",video_id):continue
  videos.append({"video_id":video_id,"url":"https://www.youtube.com/watch?v="+video_id,
    "views_source_snapshot":x.get("views"),"channel_id":x.get("channel_id"),
    "title_public":str(x.get("title") or "")[:220],
    "is_film_semantically_verified":False})
 reviews=sorted({w["video_id"] for w in g02["pending_reviewer_windows"]})
 bundle={
  "schema":"cine.research.company_handoff.v266",
  "project_id":project_id,
  "niche":"minecraft","scoped_formats":["minecraft_gameplay","minecraft_animation"],
  "generated_at":datetime.now(timezone.utc).isoformat(),
  "source_sha256":hashes,
  "source_files":SOURCES,
  "reported_public_metadata_candidates":len(videos),
  "public_candidate_sample":videos[:80],
  "source_video_ids_pending_independent_review":reviews,
  "source_30second_window_count":g02["original_review_windows"],
  "source_rechecked_1x_window_count":g02["reopened_source_windows"],
  "g02_status":"PENDING_INDEPENDENT_NATIVE_SEMANTIC_QC",
  "source_approval":False,"production_permission":False,
  "copyright_clearance":False,"format_identity_human_verified":False,
  "competitor_profiles_certified_count":0,
  "baseline_proven":False,
  "source_verified_software_stack":False,
  "discovery_not_exhaustive":True,
  "no_youtube_retention_ctr_or_rpm_claims":True,
  "expected_research_stage":"EVIDENCE_INTEGRITY_PENDING_NOT_AUTO_PASS",
 }
 if write:
  dst=root/"data/projects"/project_id/"company/research_handoff.json"
  dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():
   old=_obj(dst)
   if old.get("project_id")!=project_id or old.get("schema")!=bundle["schema"]:
    raise ValueError("REFUSE_OVERWRITE_UNRELATED_RESEARCH")
   # Only update sources when existing prior handoff is not tampered.
   for rel,digest in old.get("source_sha256",{}).items():
    if rel in SOURCES.values() and _hash(root/rel)!=digest:
     raise ValueError("SOURCE_HASH_CHANGED_SINCE_HANDOFF_REQUIRE_NEW_VERSION")
  dst.write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 return bundle
def load(root:Path,project_id:str)->dict|None:
 p=root/"data/projects"/project_id/"company/research_handoff.json"
 if not p.is_file():return None
 obj=_obj(p)
 if obj.get("schema")!="cine.research.company_handoff.v266" or obj.get("project_id")!=project_id:
  raise ValueError("PROJECT_RESEARCH_HANDOFF_SCOPE_MISMATCH")
 if obj.get("g02_status")!="PENDING_INDEPENDENT_NATIVE_SEMANTIC_QC" or obj.get("production_permission") is not False:
  raise ValueError("RESEARCH_NOT_AUTHORIZED_TO_SELF_CERTIFY")
 if obj.get("competitor_profiles_certified_count")!=0 or obj.get("source_approval") is not False:
  raise ValueError("RESEARCH_SOURCE_NOT_CERTIFIED")
 if obj.get("source_files")!=SOURCES:raise ValueError("RESEARCH_SOURCE_MAPPING_CHANGED")
 if len(obj.get("source_sha256",{}))!=len(SOURCES):raise ValueError("RESEARCH_SOURCE_HASH_MISSING")
 for rel in SOURCES.values():
  if not (root/rel).is_file() or _hash(root/rel)!=obj["source_sha256"].get(rel):
   raise ValueError("RESEARCH_HANDOFF_SOURCE_MISMATCH:"+rel)
 expected=build(root,project_id,write=False)
 for key in ("reported_public_metadata_candidates","public_candidate_sample",
             "source_video_ids_pending_independent_review",
             "source_30second_window_count","source_rechecked_1x_window_count",
             "baseline_proven","copyright_clearance"):
  if obj.get(key)!=expected.get(key):
   raise ValueError("RESEARCH_HANDOFF_DERIVED_CONTENT_TAMPERED:"+key)
 return obj
if __name__=="__main__":
 import argparse
 a=argparse.ArgumentParser();a.add_argument("--project-id",required=True)
 args=a.parse_args()
 print(json.dumps(build(ROOT,args.project_id),ensure_ascii=True,indent=2))
