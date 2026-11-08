#!/usr/bin/env python3
"""Bell & Leaf read-only memory bootstrap: authoritative sources, not a duplicate Canon.

Use --stage story/script for 30-scene EP001 treatment; --stage image/video --shot S001
for original shot cast/media binding; --stage next --episode BL-0002 for prior
continuity and protected events. Never signs off source/production, never reads
or exports owner's private showrunner scripts.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path("config/series/bell_leaf/memory_manifest_v1.json")
STAGES = frozenset(("research","story","script","image","video","next"))

def fail(message: str) -> None:
    raise ValueError(message)

def get_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        fail("UNSAFE_SOURCE_PATH")
    path = (root / relative).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        fail("OUTSIDE_CINE_ROOT")
    if not path.is_file():
        fail("MISSING_REQUIRED_CANON_SOURCE:" + relative)
    return path

def read_json(root: Path, relative: str) -> dict:
    data = json.loads(get_path(root, relative).read_text(encoding="utf-8-sig"))
    if not isinstance(data,dict):fail("INVALID_CANON_JSON:"+relative)
    return data

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def select_episode(manifest: dict, episode_id: str, stage: str) -> tuple[str,dict]:
    registry=manifest["episode_registry"]
    if stage=="next":
        if episode_id in registry:fail("NEXT_EPISODE_ID_ALREADY_REGISTERED")
        if not re.fullmatch(r"BL-\d{4}",episode_id):fail("BAD_EPISODE_ID")
        earlier=sorted((ep for ep in registry if ep<episode_id),reverse=True)
        if not earlier:fail("NO_PRIOR_EPISODE_MEMORY")
        return earlier[0], registry[earlier[0]]
    if episode_id not in registry:fail("EPISODE_NOT_REGISTERED_STOP_NO_INVENTED_SCREENPLAY")
    return episode_id,registry[episode_id]

def load(root: Path=ROOT, episode_id: str="BL-0001", stage: str="story", shot_id: str|None=None,
         include_story_text: bool=True) -> dict:
    if stage not in STAGES:fail("BAD_STAGE")
    if stage in ("image","video") and not shot_id:fail("SHOT_ID_REQUIRED")
    if shot_id and stage not in ("image","video"):fail("SHOT_ID_NOT_VALID_FOR_STAGE")
    manifest=read_json(root, str(MANIFEST).replace("\\","/"))
    if manifest["series_id"]!="bell_leaf" or manifest["niche_id"]!="magical_witch_family_stories":
        fail("WRONG_SERIES_OR_NICHE")
    prev_id,ep_cfg=select_episode(manifest,episode_id,stage)
    private_root=root/manifest["owner_private_local_only"]
    private_present=private_root.is_dir() and any(f.is_file() for f in private_root.iterdir())
    sources=manifest["source_files"]
    # All source-of-truth references must exist; no local/private source text is exported.
    receipts={}
    for key,rel in sources.items():
        p=get_path(root,rel)
        receipts[key]={"source_path":rel,"sha256":sha256(p)}
    ep_receipts={}
    for key,rel in ep_cfg.items():
        if key.endswith("_script") or key in ("story_treatment","continuity","quality_plan","shot_bindings"):
            p=get_path(root,rel)
            ep_receipts[key]={"source_path":rel,"sha256":sha256(p)}
    index=read_json(root,sources["episode_memory_index"])
    lock=read_json(root,ep_cfg["continuity"])
    visual=read_json(root,sources["visual_bible"])
    charcanon=read_json(root,sources["visual_canon"])
    mapping=read_json(root,ep_cfg["shot_bindings"])
    if index["series_id"]!=manifest["series_id"] or index["niche_id"]!=manifest["niche_id"]:
        fail("EPISODE_MEMORY_INDEX_WRONG_SERIES")
    if lock["episode_id"]!=prev_id or lock["series_id"]!=manifest["series_id"]:
        fail("WRONG_EPISODE_LOCK")
    if lock["status"].startswith("APPROVED"):fail("FALSELY_APPROVED_LOCK_STATUS")
    if mapping["episode_id"]!=prev_id or len(mapping["shots"])!=270:
        fail("SHOT_MAP_MISMATCH_EPISODE_OR_LENGTH")
    registered={x["episode_id"]:x for x in index["plot_registry"]}
    if prev_id not in registered or registered[prev_id]["reference_file"]!=ep_cfg["continuity"]:
        fail("UNINDEXED_EPISODE_LOCK")
    scenes=lock["scene_cards"]
    if len(scenes)!=lock["timing"]["scene_count"] or len(scenes)!=30:
        fail("MISSING_STORY_SCENES")
    seen_events=[]
    for i,s in enumerate(scenes):
        if s["scene_id"]!=f"SC-{i+1:03d}" or s["start_s"]!=i*90 or s["end_s"]!=(i+1)*90:
            fail("SCENE_TIMELINE_DRIFT")
        seen_events.append(s["original_event_id"])
    if len(set(seen_events))!=30 or seen_events!=registered[prev_id]["locked_event_ids"]:
        fail("EPISODE_EVENTS_OUT_OF_SYNC")
    if [x["shot_id"] for x in mapping["shots"]] != [f"S{i+1:03d}" for i in range(270)]:
        fail("SHOT_ID_DRIFT")
    if visual["series_id"]!="bell_leaf" or len(visual["locations"])<9 or len(visual["characters"])<9:
        fail("VISUAL_BIBLE_INVALID")
    if len(charcanon["primary_tags"])!=9:fail("CHARACTER_PRIMARY_TAGS_NOT_NINE")
    skills={}
    missing_skill_paths=[]
    for key,names in manifest["stage_skill_contracts"].items():
        if key not in STAGES:fail("UNKNOWN_SKILL_STAGE")
        skill_files=[]
        for name in names:
            p=f".claude/skills/{name}/SKILL.md"
            if (root/p).is_file():
                skill_files.append(p)
            elif key==stage:
                missing_skill_paths.append(p)
        skills[key]=skill_files
    out={
        "schema":"cine.bell_leaf.resolved_context.v1",
        "series_id":"bell_leaf","niche_id":"magical_witch_family_stories",
        "requested_episode_id":episode_id,"source_episode_id":prev_id,
        "stage":stage,"memory_manifest":str(MANIFEST).replace("\\","/"),
        "source_receipts":receipts,"episode_source_receipts":ep_receipts,
        "loaded_skill_paths":skills[stage],
        "unavailable_skill_paths":missing_skill_paths,
        "canon_priority":manifest["priority"],
        "public_series_canon":get_path(root,sources["series_story"]).read_text(encoding="utf-8-sig"),
        "public_owner_contract":get_path(root,sources["owner_contract"]).read_text(encoding="utf-8-sig"),
        "episode_story_revision":lock["story_reference_revision"],
        "episode_story_status":lock["status"],
        "story_first_rule":lock["story_first_rule"],
        "creative_hard_locks":lock["creative_hard_locks"],
        "state_at_beginning":lock["state_at_beginning"],
        "state_at_end":lock["state_at_end"],
        "unresolved_puzzles":lock["unresolved_puzzles"],
        "protected_events":registered[prev_id]["locked_event_ids"],
        "anti_repeat":lock["anti_repeat"],
        "characters":["MARA","EVAN","JUNO","LIA","BIX","BUBU","ORIN","GRANDPA_EARTH","GRANDMA_EARTH"],
        "visual_registry_status":"OWNER_SHEETS_LOCKED_NOT_MODEL_TRAINED_OR_I2V_QC",
        "visual_canon_path":sources["visual_canon"],
        "location_canon_path":sources["visual_bible"],
        "private_source_policy":"LOCAL_ONLY: Do not export owner's original four private texts, spoiler identity, keys or private paths outside authorized local workflow.",
        "private_owner_sources_present_on_this_checkout":bool(private_present),
        "production_authorized":False,
        "human_story_approval":False,
        "warnings":["EP001_V2_TREATMENT_NOT_270_SHOT_V2_SCREENPLAY","EP001_V1_1_SHOTS_HISTORICAL_ONLY","MEDIA_AND_VOICE_QC_NOT_IMPLIED"] + (["PRIVATE_OWNER_SOURCE_NOT_MOUNTED_PUBLIC_ONLY"] if not private_present else []) + ["SKILL_FILE_MISSING:"+s for s in missing_skill_paths],
    }
    if stage=="next":
        out["proposed_episode_state"]="NEW_PITCH_ONLY_NOT_WRITTEN_OR_APPROVED"
        out["continuity_start_from_previous_episode"]=lock["state_at_end"]
        out["prior_episode_id"]=prev_id
        out["collision_warning"]=registered[prev_id].get("collision_warning_with_unapproved_1000_slate")
        out["next_episode_mandatory_steps"]=[
            "Read previous state and ALL locked events",
            "Choose materially new cause/goal/obstacle/twist/payoff not the copper suitcase replay",
            "Run Bell Leaf episode_uniqueness_gate and CINE story_quality_gate",
            "Independently review semantic plot novelty and Canon",
            "Register approved episode memory ONLY after genuine editor and owner signoff",
        ]
        return out
    if stage in ("story","script","research"):
        out["all_30_scene_cards"]=scenes
        if include_story_text:
            out["complete_30_scene_treatment"]=get_path(root,ep_cfg["story_treatment"]).read_text(encoding="utf-8-sig")
        out["editorial_status"]="WRITERS_REFERENCE_NOT_APPROVED_SCREENPLAY"
        return out
    shot=next((x for x in mapping["shots"] if x["shot_id"]==shot_id),None)
    if not shot:fail("SHOT_NOT_FOUND_IN_REGISTERED_EPISODE")
    scene=next((s for s in scenes if s["scene_id"]==shot["scene_id"]),None)
    if not scene:fail("SHOT_SCENE_MISSING")
    shot_num=int(shot_id[1:])
    if not ((int(scene["shot_slot_range"][0][1:]) <= shot_num <= int(scene["shot_slot_range"][1][1:]))):
        fail("SHOT_SCENE_BOUNDARY_MISMATCH")
    selected=[]
    warnings=list(out["warnings"])
    cast=shot.get("active_character_tags_candidate",[])
    if len(cast)!=len(set(cast)):fail("DUPLICATE_SHOT_ACTIVE_TAGS")
    for tag in cast:
        if tag not in visual["characters"]:
            warnings.append("CHARACTER_MISSING_VISUAL_CANON:"+tag)
            continue
        character=visual["characters"][tag]
        src=character["refs"]
        faces={}
        for typ in ("face","hero"):
            rel=src[typ]["path"]
            p=root/rel
            observed=sha256(p) if p.is_file() else None
            approved_hash=src[typ]["sha256"]
            if observed!=approved_hash:
                warnings.append(f"OWNER_{typ.upper()}_MEDIA_UNAVAILABLE_OR_SHA_DRIFT:{tag}")
            faces[typ]={"source":rel,"expected_sha256":approved_hash,"local_sha256":observed,
                        "media_verified":observed==approved_hash}
        selected.append({"tag":tag,"original_sheet":character["canon_git_path"],"refs":faces})
    anchor=shot.get("location_anchor_id")
    plate=visual["locations"].get(anchor) if anchor else None
    if plate is None:
        warnings.append("LOCATION_REFERENCE_NOT_REGISTERED")
    else:
        source=plate["git_path"]
        observed=sha256(root/source) if (root/source).is_file() else None
        if observed!=plate["sha256"]:
            warnings.append("OWNER_LOCATION_PLATE_UNAVAILABLE_OR_SHA_DRIFT")
        if plate.get("multiangle_production_approved") is not True:
            warnings.append("MULTIVIEW_NOT_APPROVED")
    out["scene_card"]=scene
    out["shot_binding"]={
        "shot_id":shot_id,"scene_id":scene["scene_id"],"timecode":shot["timecode"],
        "active_character_tags":cast,"audio_only_tags":shot.get("audio_only_character_tags_candidate",[]),
        "director_cast_status":shot.get("shot_cast_director_verification"),
        "camera_status":shot.get("camera_angle_multiview_QC"),
        "image_video_status":shot.get("image_video_final_canon_gate"),
        "no_external_media_ids_authorized":True
    }
    out["character_media"]=selected
    out["location_media"]={
        "anchor_id":anchor,"original_plate":plate["git_path"] if plate else None,
        "expected_sha256":plate["sha256"] if plate else None,
        "verified_local":bool(plate and observed==plate["sha256"]),
        "multiview_approved":bool(plate and plate.get("multiangle_production_approved")),
    }
    out["shot_status"]="UNVERIFIED_V1_1_VISUAL_BINDING_NOT_APPROVED_V2_PRODUCTION"
    out["warnings"]=list(dict.fromkeys(warnings))
    return out

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--episode",default="BL-0001")
    p.add_argument("--stage",choices=sorted(STAGES),default="story")
    p.add_argument("--shot")
    p.add_argument("--out",type=Path)
    p.add_argument("--verify",action="store_true",help="validate source contracts without exporting private data")
    args=p.parse_args()
    try:
        out=load(episode_id=args.episode,stage=args.stage,shot_id=args.shot,include_story_text=not args.verify)
    except (ValueError,KeyError,FileNotFoundError,json.JSONDecodeError) as e:
        print("BLOCKED:",str(e))
        raise SystemExit(2)
    if args.verify:
        print(json.dumps({"status":"SOURCE_STRUCTURE_PASS_NOT_PRODUCTION_APPROVAL","episode":args.episode,
            "stage":args.stage,"shot":args.shot,"source_count":len(out["source_receipts"]),
            "skill_count":len(out["loaded_skill_paths"]),"warnings":out["warnings"],
            "production_authorized":False},ensure_ascii=False,indent=2))
    elif args.out:
        # Refuse accidentally overwriting an editor's review; cache is explicit and replaceable by caller only.
        if args.out.exists():
            print("BLOCKED:DESTINATION_ALREADY_EXISTS");raise SystemExit(2)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print("CONTEXT_WRITTEN",args.out, "PRODUCTION_AUTHORIZED=False")
    else:
        print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
