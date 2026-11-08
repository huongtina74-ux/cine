#!/usr/bin/env python3
"""Bell & Leaf stylized 3D CGI image/I2V prompt compiler + non-bypassable draft QC.

Sources: locked owner face/hero sheets, location registry and EP001 270-shot bind.
Outputs are PROMPT DRAFTS, never an approved frame, media ID, voice, video or pass.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BIBLE="config/niches/slow_english_a2/OWNER_VISUAL_REFERENCE_BIBLE_20261108.json"
BINDINGS="docs/story/bell_leaf/ep001_screenplay/EP001_SHOT_VISUAL_REFERENCE_BINDINGS_v1.json"
CONTRACT="config/niches/slow_english_a2/stylized_3d_prompt_contract_v1.json"
VALID_TAGS=frozenset(["EVAN","MARA","JUNO","LIA","BIX","BUBU","ORIN","GRANDPA_EARTH","GRANDMA_EARTH","ELARA"])
PHASES=("setup_0_2","action_2_7","reaction_7_10")
BAD_INPUT=re.compile(r"\b(?:photorealistic(?:\s+(?:human|woman|man|skin))?|live[\s-]?action|human actress|real actor|real human|skin pores|hyperrealistic skin|hyperreal(?:istic)? people|turn into (?:a )?real|morph(?:s|ing)? into (?:a )?human)\b",re.I)
FOREIGN_CAST=re.compile(r"\b(?:Mia|Grandpa Walter|Biscuit)\b",re.I)
MULTI_SCENE=re.compile(r"\b(?:cuts? to|jump cuts?|montage|split screen|scene change|switch scenes|new scene|new location|collage|grid of|nine[\s-]?panel|3\s*x\s*3)\b",re.I)
BAD_CAMERA=re.compile(r"\b(?:orbit 360|360.degree|spin the camera|whip pan around the face)\b",re.I)
CAMERA_ONLY=re.compile(r"\b(?:zoom(?:s|ing)? in|push in|dolly in)\b",re.I)
MOTION=re.compile(r"\b(?:move|moves|moving|walk|walks|step|steps|lift|lifts|raise|raises|lower|lowers|turn|turns|tilt|tilts|blink|blinks|reach|reaches|touch|touches|hold|holds|gaze|gazes|nod|nods|breathe|breathes|clink|clinks|roll|rolls|fall|falls|sway|sways|flutter|flutters|drink|drinks|pause|pauses|stop|stops|open|opens|close|closes|shake|shakes|settle|settles)\b",re.I)


def json_obj(path:Path)->dict:
    o=json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(o,dict):raise ValueError("JSON_OBJECT_REQUIRED: "+str(path))
    return o


def clean_line(s:str,field:str,lo:int=8,hi:int=350)->str:
    if not isinstance(s,str):raise ValueError("FIELD_MUST_BE_STRING_"+field)
    x=" ".join(s.split())
    if not lo<=len(x)<=hi:raise ValueError(f"FIELD_LENGTH_{field}")
    if BAD_INPUT.search(x):raise ValueError("LIVE_ACTION_OR_PHOTOREAL_RECAST_"+field)
    if FOREIGN_CAST.search(x):raise ValueError("UNRELATED_SLOW_ENGLISH_CHARACTER_"+field)
    if MULTI_SCENE.search(x):raise ValueError("MULTI_SCENE_OR_COLLAGE_"+field)
    if BAD_CAMERA.search(x):raise ValueError("CAMERA_ANGLE_IDENTITY_RISK_"+field)
    return x.rstrip(" .,!;")+ "."


def get_shot(shot_id:str,data:dict)->dict:
    found=[x for x in data.get("shots",[]) if x.get("shot_id")==shot_id]
    if len(found)!=1:raise ValueError("UNKNOWN_OR_DUPLICATE_SHOT_ID_"+str(shot_id))
    x=found[0]
    if x.get("episode_id")!="BL-0001" or data.get("niche_id")!="magical_witch_family_stories":
        raise ValueError("WRONG_SERIES_OR_NICHE")
    return x


def file_evidence(root:Path,path:str,expected:str)->str:
    p=root/path
    if not p.is_file():return "MISSING_BINARY:"+path
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    return "HASH_MISMATCH:"+path if h!=expected else "SOURCE_SHA_OK"


def compile_one(entry:dict,root:Path=ROOT)->dict:
    bible=json_obj(root/BIBLE);refs=json_obj(root/BINDINGS);policy=json_obj(root/CONTRACT)
    if bible.get("niche_id")!="magical_witch_family_stories" or policy.get("series_id")!="bell_leaf":
        raise ValueError("NOT_BELL_LEAF_CGI_CONTRACT")
    shot=get_shot(entry.get("shot_id",""),refs)
    requested=entry.get("visible_cast")
    if not isinstance(requested,list) or len(requested)!=len(set(requested)):
        raise ValueError("VISIBLE_CAST_REQUIRED_UNIQUE_LIST")
    if not all(isinstance(t,str) and t in VALID_TAGS for t in requested):
        raise ValueError("UNAPPROVED_OR_FOREIGN_VISIBLE_CAST")
    known=shot.get("active_character_tags_candidate",[])
    if requested!=known:
        raise ValueError("CAST_NOT_EQUAL_TO_EP001_REFERENCE_BINDING_REVIEW_BEFORE_REMAP")
    if any(t in shot.get("characters_without_approved_visuals",[]) for t in requested):
        raise ValueError("MISSING_OWNER_APPROVED_CHARACTER")
    loc=shot.get("location_anchor_id")
    location=bible.get("locations",{}).get(loc)
    if not location:location_error="NO_OWNER_LOCATION_PLATE"
    elif location.get("spatial_status","").startswith("BLOCKED"):
        location_error="OWNER_LOCATION_SPATIAL_CONFLICT"
    else:location_error=None
    image=entry.get("image",{})
    video=entry.get("video",{})
    if not isinstance(image,dict) or not isinstance(video,dict):
        raise ValueError("IMAGE_AND_VIDEO_DIRECTION_OBJECT_REQUIRED")
    framing=clean_line(image.get("framing",""),"IMAGE_FRAMING")
    pose=clean_line(image.get("pose",""),"IMAGE_POSE")
    if not requested and re.search(r"\b(?:Mara|Evan|Juno|Lia|Bubu|Bix|Orin)\b",pose,re.I):
        raise ValueError("EMPTY_CAST_MUST_NOT_REQUEST_LOCKED_CHARACTER")
    camera=clean_line(video.get("camera",""),"VIDEO_CAMERA",5,170)
    beats=[clean_line(video.get(x,""),x,10,240) for x in PHASES]
    if all(not MOTION.search(x) for x in beats):
        raise ValueError("NO_VISIBLE_PHYSICAL_MOTION")
    if all(CAMERA_ONLY.search(x) for x in beats):
        raise ValueError("CAMERA_ONLY_MOTION")
    if len(" ".join(beats).split())>110:
        raise ValueError("OVERDIRECTED_TEN_SECOND_SHOT")
    if any("said" in x.lower() or "speaks" in x.lower() or "says" in x.lower() for x in beats):
        # prompt text alone doesn't lock character WAV and lip sync
        raise ValueError("VOICE_DIALOGUE_NEEDS_SEPARATE_APPROVED_WAV_CONTRACT")
    warnings=[];blockers=[]
    if shot.get("shot_cast_director_verification")!="APPROVED":
        blockers.append("DIRECTOR_VISIBLE_CAST_UNREVIEWED")
    if shot.get("camera_angle_multiview_QC")!="APPROVED":
        blockers.append("DIRECTOR_CAMERA_AND_GEOMETRY_UNREVIEWED")
    if location_error:blockers.append(location_error)
    elif not location.get("multiangle_production_approved"):
        blockers.append("LOCATION_MULTIVIEW_UNAPPROVED")
    if shot.get("reference_image_upload_state")!="VERIFIED_PROVIDER_MEDIA_IDS":
        blockers.append("PROVIDER_MEDIA_UPLOAD_NOT_VERIFIED")
    actors=[]
    for tag in requested:
        item=bible["characters"].get(tag)
        if not item:
            blockers.append("CANON_CHARACTER_NOT_REGISTERED_"+tag);continue
        face=shot["character_reference_paths"].get(tag,{})
        if face.get("sheet")!=item["canon_git_path"]:
            blockers.append("CAST_SOURCE_SHEET_MISMATCH_"+tag)
        evidence=file_evidence(root,item["canon_git_path"],item["canon_file_sha256"])
        if evidence!="SOURCE_SHA_OK":blockers.append(evidence)
        for kind in ("face","hero"):
            crop=face.get(kind)
            expected=item["refs"].get(kind,{})
            if not crop or crop!=expected.get("path"):
                blockers.append(f"CANON_{kind.upper()}_PATH_MISMATCH_{tag}")
            elif file_evidence(root,crop,expected["sha256"])!="SOURCE_SHA_OK":
                blockers.append(f"CANON_{kind.upper()}_BINARY_UNVERIFIED_{tag}")
        actors.append({"tag":tag,"source_sheet":item["canon_git_path"],"face":face.get("face"),"hero":face.get("hero")})
    if location and file_evidence(root,location["git_path"],location["sha256"])!="SOURCE_SHA_OK":
        blockers.append("LOCATION_SOURCE_SHA_NOT_VERIFIED")
    # Human first-frame approval belongs to the actual I2V stage, never here.
    blockers.append("FIRST_FRAME_NOT_CREATED_OR_HUMAN_APPROVED")
    blockers.append("REAL_10S_CGI_VIDEO_NOT_REVIEWED")
    tags="ACTIVE TAGS FOR THIS SHOT: ["+", ".join(requested)+"]"
    image_prompt=("Create exactly ONE independent full-bleed 16:9 still for an original premium "
      "stylized 3D CGI animated family film. Use ONLY the attached approved owner character "
      "face/body reference images for visible characters and the registered original location "
      "plate as the visual identity authorities. Preserve the exact original sculpted face "
      "geometry, eyes, hairstyle, character scale, wardrobe and stylized physically based CGI "
      "materials. Keep room geometry, doors, windows, table positions, fixed props and eyelines "
      "consistent with the verified view. "+framing+" "+pose+" Neutral D55 5500K daylight "
      "when the scene is daytime, clean natural whites, restrained CGI shading and soft shadows; "
      "cinematic 50mm lens character-focused composition with modest depth of field. "
      "One single shot, one image, no storyboards, no multiple panels, no text or subtitles, "
      "no unapproved extra people. "+tags)
    video_prompt=("Animate the exact human-reviewed 16:9 CGI FIRST FRAME as ONE continuous "
      "10.0-second stylized 3D animated-family-film shot. 0–2s: "+beats[0]+" "
      "2–7s: "+beats[1]+" 7–10s: "+beats[2]+" "+camera+" "
      "Preserve the original approved sculpted 3D character identity, proportions, "
      "costume, shaders and existing set geometry frame by frame; maintain cohesive animated "
      "character acting with real eye, head, hand or body movement, not camera-only zoom. "
      "One take, no edits or on-image text. "+tags)
    if "\n" in image_prompt or "\n" in video_prompt:raise ValueError("MULTILINE_PROMPT")
    return {
     "shot_id":shot["shot_id"],"scene_id":shot["scene_id"],"niche_id":"magical_witch_family_stories",
     "image_prompt":image_prompt,"video_prompt":video_prompt,"active_tags":requested,
     "character_references":actors,"location_reference":location["git_path"] if location else None,
     "location_reference_sha256":location["sha256"] if location else None,
     "image_status":"DRAFT_NOT_GENERATED","video_status":"DRAFT_NOT_GENERATED",
     "provider_account_verified":False,"human_canon_visual_approval":False,
     "production_authorized":False,"blockers":sorted(set(blockers)),"warnings":warnings,
     "status":"DRAFT_BLOCKED_PENDING_CANON_AND_PRODUCTION_QC"
    }


def compile_batch(brief:dict,root:Path=ROOT)->dict:
    if brief.get("series_id")!="bell_leaf" or brief.get("niche_id")!="magical_witch_family_stories" or brief.get("episode_id")!="BL-0001":
        raise ValueError("WRONG_NICHE_OR_EPISODE_NO_CROSS_NICHE_REUSE")
    arr=brief.get("shots")
    if not isinstance(arr,list) or not arr:raise ValueError("NO_SHOT_BRIEFS")
    ids=[x.get("shot_id") for x in arr if isinstance(x,dict)]
    if len(ids)!=len(arr) or len(set(ids))!=len(ids):
        raise ValueError("BAD_OR_DUPLICATE_SHOT_IDS")
    nums=[int(x[1:]) for x in ids if re.fullmatch(r"S\d{3}",x)]
    if len(nums)!=len(ids) or nums!=sorted(nums):
        raise ValueError("SHOTS_NOT_ORDERED_BY_EPISODE_TIMELINE")
    records=[compile_one(x,root=root) for x in arr]
    joined=lambda k:"\n\n".join(x[k] for x in records)+"\n"
    for key in ("image_prompt","video_prompt"):
        lines=joined(key).splitlines()
        if len(lines)!=2*len(records)-1 or any(lines[i] for i in range(1,len(lines),2)):
            raise ValueError("ONE_PROMPT_PER_LINE_EXACTLY_ONE_BLANK_BETWEEN_SHOTS")
    return {"schema":"cine.bell_leaf.stylized_3d_prompt_bundle.v1","status":"DRAFT_QC_PENDING",
            "episode_id":"BL-0001","count":len(records),"receipts":records,
            "images_txt":joined("image_prompt"),"videos_txt":joined("video_prompt"),
            "none_production_authorized":all(not r["production_authorized"] for r in records)}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--brief",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    args=p.parse_args(argv)
    try:
        result=compile_batch(json_obj(args.brief))
    except (ValueError,KeyError,TypeError,FileNotFoundError) as exc:
        print(json.dumps({"status":"BLOCKED_INVALID_BRIEF","error":str(exc)}))
        return 2
    args.out_dir.mkdir(parents=True,exist_ok=True)
    for name,key in (("FLOW_IMAGE_DRAFTS.txt","images_txt"),
                     ("MUSE_VIDEO_DRAFTS.txt","videos_txt")):
        (args.out_dir/name).write_text(result[key],encoding="utf-8")
    report={k:v for k,v in result.items() if not k.endswith("_txt")}
    (args.out_dir/"DRAFT_QC_RECEIPTS.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"shots":result["count"],
                      "out_dir":str(args.out_dir.resolve()),
                      "production_authorized":False},ensure_ascii=False))
    return 0


if __name__=="__main__":sys.exit(main())
