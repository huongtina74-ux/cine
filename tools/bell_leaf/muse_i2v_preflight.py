#!/usr/bin/env python3
"""Bell & Leaf 3D CGI I2V preflight, prompt compiler, and human QC template.

A producer-side safety/identity validator, NOT a Muse API client.
Never generates videos or claims identity accuracy from a text prompt.
Provider capability claims are document-backed, but access and exact account
support are unverified and MUST be independently proven before execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BIND=ROOT/"docs/story/bell_leaf/ep001_screenplay/EP001_SHOT_VISUAL_REFERENCE_BINDINGS_v1.json"
BIBLE=ROOT/"config/niches/slow_english_a2/OWNER_VISUAL_REFERENCE_BIBLE_20261108.json"
CONTRACTS=ROOT/"config/niches/slow_english_a2/i2v_provider_contracts_20261108.json"
SUSPICIOUS=re.compile(r"\b(Mia|Grandpa Walter|Biscuit)\b",re.I)
STYLE_LOCK=("Preserve the EXACT source first frame as a stylized 3D CGI animated-family film, "
            "with the SAME original sculpted faces, eyes, body silhouettes, costumes, "
            "shaders, room geometry and character scale across all frames. "
            "Do not reinterpret animated characters as real photographed people.")
NEGATIVE=("live-action; human actors; real-person recast; photoreal skin pores; "
          "new face; altered eyes; different age or height; identity morphing; "
          "new wardrobe; altered set geometry; extra characters; split screen; "
          "9-panel grid; captions; subtitles; brand logos; image flicker; "
          "zoom-only animation; duplicate limb or tail")
QC_TIMES=[0.0,2.0,5.0,8.0,9.8]
ONLY_TAGS={"MARA","EVAN","JUNO","LIA","BIX","BUBU","ORIN",
           "GRANDPA_EARTH","GRANDMA_EARTH","ELARA"}


def read_obj(path:Path)->dict:
    o=json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(o,dict):raise ValueError("MUST_BE_JSON_OBJECT:"+str(path))
    return o


def digest(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()


def valid_first_frame(path:Path)->dict:
    from PIL import Image
    with Image.open(path) as im:
        width,height=im.size
        if min(width,height)<512 or abs(width/height-16/9)>.018:
            raise ValueError("FIRST_FRAME_MUST_BE_SINGLE_FULL_16_9_AT_LEAST_512PX")
        if im.format not in ("PNG","JPEG","WEBP"):
            raise ValueError("FIRST_FRAME_UNSUPPORTED_FORMAT")
        return {"path":str(path.resolve()),"sha256":digest(path),
                "dimensions":[width,height],"format":im.format}


def compile_shot(shot_id:str,provider_id:str,action:str,
                 *,first_frame:Path|None=None,project_root:Path=ROOT)->dict:
    """Compile only; intentionally never authorize Muse API or video production."""
    binding=read_obj(project_root/BIND.relative_to(ROOT))
    bible=read_obj(project_root/BIBLE.relative_to(ROOT))
    contracts=read_obj(project_root/CONTRACTS.relative_to(ROOT))
    blockers=[];warnings=[]
    if provider_id not in contracts["providers"]:
        blockers.append("MUSE_PROVIDER_NOT_IDENTIFIED")
        provider=contracts["providers"]["unknown_muse"]
        provider_id="unknown_muse"
    else:provider=contracts["providers"][provider_id]
    if provider_id=="unknown_muse" or provider["provider_verified_for_account"] is not True:
        blockers.append("PROVIDER_ACCOUNT_AND_MODEL_NOT_VERIFIED")
    if provider.get("supports_i2v") is not True or provider.get("supports_10s_16_9") is not True:
        blockers.append("MODEL_10S_16_9_I2V_CAPABILITY_NOT_CONFIRMED")
    if provider.get("known_first_frame_style_anchoring") is not True:
        blockers.append("FIRST_FRAME_STYLE_ANCHOR_NOT_CONFIRMED")
    matches=[x for x in binding["shots"] if x["shot_id"]==shot_id]
    if len(matches)!=1:raise ValueError("UNKNOWN_OR_DUPLICATE_SHOT_ID")
    shot=matches[0]
    if shot.get("episode_id")!="BL-0001" or binding.get("niche_id")!="magical_witch_family_stories":
        blockers.append("WRONG_NICHE_OR_EPISODE")
    if not isinstance(action,str) or len(action.strip())<12:
        blockers.append("ACTION_TOO_VAGUE")
        action=""
    if len(action)>900:blockers.append("ACTION_OVERDESCRIBED_FOR_I2V")
    if SUSPICIOUS.search(action):blockers.append("LEGACY_NON_BELL_LEAF_CHARACTER_TEMPLATE")
    if re.search(r"\b(change|replace|redesign|transform|morph|age up)\b.{0,45}\b(face|character|person|actor|wardrobe|style)\b",action,re.I):
        blockers.append("ACTION_REQUESTS_IDENTITY_RECAST")
    if re.search(r"\b(photo(realistic)?|live.?action|real actor|actual human)\b",action,re.I):
        blockers.append("ACTION_REQUESTS_LIVE_ACTION")
    if re.search(r"\b(scene change|cut to|jump cut|montage|switch scene)\b",action,re.I):
        blockers.append("MULTI_SCENE_IN_ONE_10S_TAKE")
    if not shot.get("active_tags_line","").startswith("ACTIVE TAGS FOR THIS SHOT: ["):
        blockers.append("ACTIVE_CHARACTER_TAG_LINE_MISSING")
    tags=shot.get("active_character_tags_candidate",[])
    if any(x not in ONLY_TAGS and x!="AILA" for x in tags):
        blockers.append("UNKNOWN_BELL_LEAF_CHARACTER_TAG")
    if shot.get("characters_without_approved_visuals"):
        blockers.append("UNAPPROVED_CHARACTER_IN_SHOT")
    if shot.get("shot_cast_director_verification")!="APPROVED":
        blockers.append("SHOT_CAST_VISIBLE_VOICE_ONLY_UNVERIFIED")
    refs=[]
    for name,item in shot.get("character_reference_paths",{}).items():
        if name not in ONLY_TAGS:
            blockers.append("UNKNOWN_REFERENCE_CHARACTER:"+name);continue
        source=bible["characters"].get(name)
        if not source:
            blockers.append("CANON_CHARACTER_SOURCE_NOT_REGISTERED:"+name);continue
        sheet=item.get("sheet")
        if sheet!=source["canon_git_path"]:
            blockers.append("CANON_REFERENCE_PATH_MISMATCH:"+name);continue
        file=project_root/sheet
        if not file.is_file():
            blockers.append("CANON_CHARACTER_IMAGE_NOT_MOUNTED:"+name);continue
        if digest(file)!=source["canon_file_sha256"]:
            blockers.append("CANON_CHARACTER_SOURCE_SHA_MISMATCH:"+name);continue
        refs.append({"tag":name,"canonical_path":str(file.resolve()),"sha256":source["canon_file_sha256"]})
    if not refs and tags:
        warnings.append("NO_REFERENCE_IMAGES_RESOLVED_FOR_VISIBLE_CAST")
    locid=shot.get("location_anchor_id")
    location=bible["locations"].get(locid) if locid else None
    if not location:
        blockers.append("LOCATION_OWNER_PLATE_MISSING")
    else:
        file=project_root/location["git_path"]
        if not file.is_file() or digest(file)!=location["sha256"]:
            blockers.append("LOCATION_PLATE_NOT_PRESENT_OR_HASH_BAD")
        if location["spatial_status"].startswith("BLOCKED"):
            blockers.append("LOCATION_GEOMETRY_CONFLICT")
        if not location.get("multiangle_production_approved"):
            blockers.append("LOCATION_ANGLE_OR_VIEW_NOT_APPROVED")
    if shot.get("camera_angle_multiview_QC")!="APPROVED":
        blockers.append("SHOT_CAMERA_ANGLE_NOT_APPROVED")
    if first_frame is None:
        blockers.append("APPROVED_16_9_CGI_FIRST_FRAME_MISSING")
        start=None
    else:
        try:start=valid_first_frame(first_frame)
        except (OSError,ValueError) as exc:
            blockers.append(str(exc));start=None
    if shot.get("reference_image_upload_state")!="VERIFIED_PROVIDER_MEDIA_IDS":
        warnings.append("NO_VERIFIED_REMOTE_ASSET_UPLOAD_IDS")
    if provider.get("first_frame_slot_used_for_character_grid") is True:
        blockers.append("PROVIDER_FIRST_FRAME_GRID_COLLIDES_WITH_SINGLE_SCENE_FRAME_POLICY")
    # No literal camera or character re-description to destabilize actual first frame.
    cleaned=" ".join(action.strip().split())
    prompt=(f"ANIMATE THIS EXACT SINGLE 16:9 FIRST FRAME for ONE continuous 10.0-second take. "
            f"{cleaned} Use subtle visible character body motion, eye focus, breathing and expression "
            f"appropriate to the action; keep a stable camera with no zoom-only substitute. "
            f"{STYLE_LOCK} No on-screen text. "
            f"{shot['active_tags_line']}")
    result={
      "schema":"cine.bell_leaf.i2v_preflight.v1",
      "episode_id":"BL-0001","shot_id":shot_id,"provider_id":provider_id,
      "provider_engine":provider.get("engine"),"provider_documentation":provider.get("documentation_url"),
      "provider_account_tested":False,"model_version_tested":False,"real_generation_attempted":False,
      "generation_status":"NOT_STARTED",
      "first_frame":start,"reference_characters":refs,
      "location_id":locid,"location_source":location.get("git_path") if location else None,
      "duration_seconds_requested":10,"aspect_ratio_requested":"16:9",
      "shot_character_tags":tags,
      "single_shot_motion_prompt":prompt,
      "negative_prompt_if_supported":NEGATIVE,
      "voice_policy":"EXTERNAL_APPROVED_WAV_ONLY_UNTIL_MODEL_VOICE_REFERENCE_AND_SYNC_VERIFIED",
      "qc_required_times_seconds":QC_TIMES,
      "human_review_fields":["first_frame_matches_render","stylized_3d_cgi_all_frames","no_real_human_conversion",
          "original_face_and_eye_geometry","same_age_and_body_scale","outfit_and_materials_unchanged",
          "location_topology_unchanged","actual_character_acting_not_zoom_only","no_extra_cast",
          "bubu_one_bell_and_sparkling_spiral_tail_if_visible","bix_no_bell_if_visible",
          "fixed_character_voice_audio_and_lipsync_if_dialogue"],
      "warnings":sorted(set(warnings)),"blockers":sorted(set(blockers)),
      "status":"BLOCKED" if blockers else "PREFLIGHT_ONLY_EXTERNAL_PROVIDER_QC_REQUIRED",
      "production_authorized":False
    }
    return result


def main(argv=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--shot",required=True)
    p.add_argument("--provider",required=True)
    p.add_argument("--motion",required=True,help="One physical action, not visual re-description")
    p.add_argument("--first-frame",type=Path)
    p.add_argument("--out",type=Path)
    p.add_argument("--txt",type=Path,help="Optional import-ready ONE-LINE prompt file")
    args=p.parse_args(argv)
    result=compile_shot(args.shot,args.provider,args.motion,first_frame=args.first_frame)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if args.txt:
        args.txt.parent.mkdir(parents=True,exist_ok=True)
        args.txt.write_text(result["single_shot_motion_prompt"]+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["status"]=="PREFLIGHT_ONLY_EXTERNAL_PROVIDER_QC_REQUIRED" else 2


if __name__=="__main__":sys.exit(main())
