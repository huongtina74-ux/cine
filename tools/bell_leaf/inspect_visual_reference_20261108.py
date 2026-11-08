"""CINE Bell & Leaf owner visual references — offline integrity and shot status gate."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BIBLE=ROOT/"config/niches/slow_english_a2/OWNER_VISUAL_REFERENCE_BIBLE_20261108.json"
CAST=ROOT/"config/niches/slow_english_a2/CHARACTER_VISUAL_CANON_LOCK_CURRENT.json"
BIND=ROOT/"docs/story/bell_leaf/ep001_screenplay/EP001_SHOT_VISUAL_REFERENCE_BINDINGS_v1.json"
LOC=ROOT/".claude/skills/cine-a2-muse-reference-anchoring/integration/config/LOCATION_CURRENT.json"

def digest(p:Path):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def inspect(require_assets=False):
    bible=json.loads(BIBLE.read_text(encoding="utf-8"))
    canon=json.loads(CAST.read_text(encoding="utf-8"))
    binding=json.loads(BIND.read_text(encoding="utf-8"))
    loc=json.loads(LOC.read_text(encoding="utf-8"))
    violations=[]
    missing=[]
    items=[]
    if bible["source_image_count"]!=23 or len(bible["characters"])!=11 or len(bible["locations"])!=9 or len(bible["multi_location_concept_boards"])!=3:
        violations.append("OWNER_IMAGE_INVENTORY_COUNT_MISMATCH")
    for tag,info in bible["characters"].items():
        path=ROOT/info["canon_git_path"]
        items.append((path,info["canon_file_sha256"]))
        if tag!="GROUP":
            if tag not in canon["characters"]:
                violations.append("UNKNOWN_CHARACTER_"+tag)
            for ref in info["refs"].values():
                items.append((ROOT/ref["path"],ref["sha256"]))
            if not info.get("canon_pixel_exact_to_owner"):
                violations.append("OWNER_ORIGINAL_PIXEL_UNVERIFIED_"+tag)
    for n,entry in bible["locations"].items():
        items.append((ROOT/entry["git_path"],entry["sha256"]))
        site=entry["site_id"];space=entry["space_id"]
        anchors=loc["locations"][site]["spaces"][space].get("owner_source_anchors_20261108",[])
        if not any(x["anchor_id"]==n and x["sha256"]==entry["sha256"] for x in anchors):
            violations.append("LOCATION_ANCHOR_NOT_CONNECTED_"+n)
        if entry.get("multiangle_production_approved") or entry.get("reverse_view_production_approved"):
            violations.append("FALSE_MULTIANGLE_APPROVAL_"+n)
    for n,entry in bible["multi_location_concept_boards"].items():
        items.append((ROOT/entry["git_path"],entry["sha256"]))
        if entry.get("geometry_lock"):violations.append("FALSE_BOARD_GEOMETRY_LOCK_"+n)
    ids=set()
    for i,shot in enumerate(binding["shots"],1):
        n=shot["shot_id"]
        if n!=f"S{i:03d}" or n in ids:violations.append("SHOTS_NOT_SEQUENTIAL_"+n)
        ids.add(n)
        if shot["episode_id"]!="BL-0001":violations.append("WRONG_EPISODE_"+n)
        if shot["referenceImageMediaIds"] or shot["image_video_final_canon_gate"]=="PASS":
            violations.append("FORGED_UPLOAD_OR_PRODUCTION_PASS_"+n)
        for tag,refs in shot["character_reference_paths"].items():
            if tag not in bible["characters"]:
                violations.append("UNVERIFIED_CAST_TAG_"+n+"_"+tag)
            elif refs.get("sheet")!=bible["characters"][tag]["canon_git_path"]:
                violations.append("FACE_REF_MISMATCH_"+n+"_"+tag)
        if any(tag=="AILA" for tag in shot["character_reference_paths"]):
            violations.append("AILA_FALSE_FACE_"+n)
        if shot["owner_location_plate_path"]:
            ref=bible["locations"].get(shot["location_anchor_id"])
            if not ref or ref["git_path"]!=shot["owner_location_plate_path"]:
                violations.append("WRONG_ROOM_ANCHOR_"+n)
        if not shot["active_tags_line"].startswith("ACTIVE TAGS FOR THIS SHOT: ["):
            violations.append("MISSING_ACTIVE_TAG_LINE_"+n)
    if len(binding["shots"])!=270:
        violations.append("NOT_270_SHOTS")
    for p,expected in items:
        if not p.is_file():
            missing.append(p.relative_to(ROOT).as_posix())
        elif digest(p)!=expected:
            violations.append("SHA_MISMATCH_"+p.relative_to(ROOT).as_posix())
    if require_assets and missing:
        violations.append("REQUIRED_OWNER_BINARY_ASSETS_MISSING")
    return {
      "status":"FAIL" if violations else ("ASSETS_MISSING_NOT_PRODUCTION_READY" if missing else "OWNER_ASSET_SOURCE_INTEGRITY_PASS_NOT_PRODUCTION_APPROVED"),
      "character_sheets_and_group":len(bible["characters"]),
      "location_owner_single_plates":len(bible["locations"]),
      "location_moodboards_concept_only":len(bible["multi_location_concept_boards"]),
      "shots":len(binding["shots"]),
      "shots_missing_cast_visual":sum(bool(s["characters_without_approved_visuals"]) for s in binding["shots"]),
      "shots_owner_location_single_plate":sum(s["owner_location_plate_path"] is not None for s in binding["shots"]),
      "shots_final_production_approved":0,
      "files_verified":len(items)-len(missing),
      "assets_missing":len(missing),
      "missing_sample":missing[:12],
      "violations":violations[:25],
      "note":"Source image integrity is distinct from multi-view and per-shot final QA. Never use these outputs as automatic owner approval."
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--require-assets",action="store_true")
    ap.add_argument("--shot",default=None)
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    report=inspect(args.require_assets)
    if args.shot:
        data=json.loads(BIND.read_text(encoding="utf-8"))
        shot=next((x for x in data["shots"] if x["shot_id"]==args.shot),None)
        if not shot:
            report["violations"].append("UNKNOWN_SHOT")
            report["status"]="FAIL"
        else:report["selected_shot"]=shot
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=True,indent=2))
    return 2 if report["status"] in ("FAIL","ASSETS_MISSING_NOT_PRODUCTION_READY") else 0

if __name__=="__main__":sys.exit(main())
