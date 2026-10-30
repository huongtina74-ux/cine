#!/usr/bin/env python3
"""CINE script-factory deterministic artifact gates; no LLM or YouTube requests.
Never claim this runner verifies artistic truth, license authenticity or YouTube approval.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "config/story_factory/pipeline.json"
NICHES = ROOT / "config/research/per_niche/niches.json"
PROJECTS = ROOT / "data/script_factory/projects"
ID_RX = re.compile(r"^[a-z0-9][a-z0-9_-]{2,63}$")


def iso_now():
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name}: expected JSON object")
    return value


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".new")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def config():
    data = read_json(PIPELINE)
    ids = {s["id"] for s in data["stages"]}
    if len(ids) != len(data["stages"]):
        raise ValueError("Duplicate stage IDs")
    if "A2_ANIMATED_SCREENPLAY" in data["modes"]:
        from cf_a2_story_contract import validate_graph
        validate_graph(ROOT, data)
    return data


def project_dir(project_id, root=PROJECTS):
    if not ID_RX.fullmatch(project_id):
        raise ValueError("Project id must be 3-64 lowercase alphanumeric/_/- characters")
    return root / project_id


def initialize(args):
    settings = config()
    known = {n["id"] for n in read_json(NICHES)["niches"]}
    if args.niche not in known:
        raise ValueError("Unknown subniche: " + args.niche)
    if args.mode not in settings["modes"]:
        raise ValueError("Unknown script mode: " + args.mode)
    if args.mode == "A2_ANIMATED_SCREENPLAY":
        spec = settings["specializations"]["A2_ANIMATED_SCREENPLAY"]
        if args.niche != spec["niche_id"]:
            raise ValueError("Bell & Leaf research must use the magical_witch_family_stories subniche")
        if not spec["target_minutes"][0] <= args.minutes <= spec["target_minutes"][1]:
            raise ValueError("Bell & Leaf episode target must be 30-50 minutes")
    if not 8 <= args.minutes <= 360:
        raise ValueError("Target minutes must be 8 to 360")
    if not args.writer or not args.writer.strip():
        raise ValueError("Explicit writer id required")
    path = project_dir(args.id, args.root)
    path.mkdir(parents=True, exist_ok=False)
    manifest = {
        "project_id": args.id, "niche_id": args.niche,
        "mode": args.mode, "target_minutes": args.minutes,
        "writer_id": args.writer, "language": args.language,
        "created_utc": iso_now(), "workflow_version": settings["version"],
        "approved_stages": {},
        "notice": "Internal file attestation only, not AI execution or external approval"
    }
    write_json(path / "manifest.json", manifest)
    (path / "audit.jsonl").touch()
    for stage in settings["stages"]:
        for rel in stage["artifacts"]:
            (path / rel).parent.mkdir(parents=True, exist_ok=True)
    print(json.dumps({"status": "initialized", "project_dir": str(path),
                      "stages": [s["id"] for s in settings["stages"]]}, indent=2))


def stage_files(base, settings, stage):
    files = list(stage["artifacts"])
    if (stage["id"] == "review"
            and read_json(base / "manifest.json")["mode"] in settings["modes_require_claim_ledger"]):
        files.append("07_review/claim_ledger.json")
    if read_json(base / "manifest.json")["mode"] == "A2_ANIMATED_SCREENPLAY":
        from cf_a2_story_contract import required_artifacts
        files.extend(required_artifacts(ROOT, stage["id"]))
    return list(dict.fromkeys(files))


def inspect_file(base, rel):
    path = base / rel
    if not path.is_file():
        raise ValueError(f"Missing required artifact: {rel}")
    raw = path.read_bytes()
    if len(raw) < 10:
        raise ValueError(f"Empty/too-small artifact: {rel}")
    if path.suffix == ".json":
        obj = read_json(path)
        if not obj:
            raise ValueError(f"JSON artifact must not be empty: {rel}")
    elif path.suffix == ".md" and len(path.read_text(encoding="utf-8").strip()) < 150:
        raise ValueError(f"Text artifact has insufficient content: {rel}")
    return sha(path)


def validate_content(base, settings, stage):
    sid = stage["id"]
    manifest = read_json(base / "manifest.json")
    if manifest["mode"] == "A2_ANIMATED_SCREENPLAY":
        from cf_a2_story_contract import validate_a2_stage
        validate_a2_stage(base, sid, manifest)
    def doc(rel):
        return read_json(base / rel)
    if sid == "research":
        info = doc("01_research/evidence.json")
        if info.get("niche_id") != read_json(base / "manifest.json")["niche_id"]:
            raise ValueError("Research report niche does not match project")
        if not isinstance(info.get("sources"), list) or not info["sources"]:
            raise ValueError("Research requires actual source ledger; do not fabricate evidence")
    elif sid == "insights":
        v=doc("02_insights/audience_insights.json")
        if not isinstance(v.get("insights"), list) or not v["insights"]:
            raise ValueError("Audience insights missing")
    elif sid == "concepts":
        v=doc("03_concepts/portfolio.json")
        vals=v.get("concepts")
        if not isinstance(vals, list) or len(vals)<settings["constraints"]["min_unique_concepts"]:
            raise ValueError("Need >=5 original concept records")
        ids=[str(x.get("id","")).strip() for x in vals]
        if not all(ids) or len(set(ids))!=len(ids):
            raise ValueError("Concept IDs must be non-empty and distinct")
    elif sid == "story":
        v=doc("04_story/story_dna.json")
        for name in ("selected_concept_id","audience_promise","distinctive_value","originality_comparison"):
            if not v.get(name):
                raise ValueError(f"Story DNA missing {name}")
    elif sid == "outline":
        v=doc("05_outline/beat_sheet.json")
        if not isinstance(v.get("beats"), list) or len(v["beats"])<3:
            raise ValueError("Need >=3 substantial beat records")
    elif sid == "script":
        v=(base/"06_script/script.md").read_text(encoding="utf-8")
        if len(v.strip())<1200:
            raise ValueError("Draft too short for complete script; content quality still requires review")
    elif sid == "review":
        expected=sha(base/"06_script/script.md")
        manifest=read_json(base/"manifest.json")
        for rel in ("07_review/creative_review.json","07_review/compliance_review.json"):
            v=doc(rel)
            if v.get("verdict")!="PASS" or v.get("reviewed_script_sha256")!=expected:
                raise ValueError(f"{rel}: PASS verdict must reference exact current script SHA256")
            if not v.get("reviewer_id") or v["reviewer_id"]==manifest["writer_id"]:
                raise ValueError(f"{rel}: independent reviewer required, distinct from writer")
            if not isinstance(v.get("evidence_notes"), list) or not v["evidence_notes"]:
                raise ValueError(f"{rel}: evidence-backed reviewer notes required")
        if manifest["mode"] in settings["modes_require_claim_ledger"]:
            ledger=doc("07_review/claim_ledger.json")
            if not isinstance(ledger.get("claims"), list):
                raise ValueError("Nonfiction claim ledger must record claims, even if empty")
            for claim in ledger["claims"]:
                if claim.get("status")!="VERIFIED" or not claim.get("source"):
                    raise ValueError("Each published factual claim must be verified or removed")
    elif sid == "final":
        if sha(base/"08_final/final_script.md")!=sha(base/"06_script/script.md"):
            raise ValueError("Final script differs from reviewed draft: return to review")
        info=doc("08_final/audio_handoff.json")
        if not info.get("voice_direction") or not info.get("chapter_plan"):
            raise ValueError("Audio handoff requires voice_direction and chapter_plan")


def status(args):
    settings=config()
    base=project_dir(args.id,args.root)
    manifest=read_json(base/"manifest.json")
    verdicts={}
    all_good=True
    for stage in settings["stages"]:
        sid=stage["id"]
        passed=manifest.get("approved_stages",{}).get(sid)
        if not passed:
            verdicts[sid]="NOT_APPROVED"
            all_good=False
            continue
        try:
            for rel,digest in passed["artifact_hashes"].items():
                if sha(base/rel)!=digest:
                    raise ValueError("file changed: "+rel)
            for rel in stage_files(base,settings,stage):
                inspect_file(base,rel)
            validate_content(base,settings,stage)
            for d in stage["requires"]:
                if verdicts.get(d)!="PASS":
                    raise ValueError("upstream stage changed: "+d)
            verdicts[sid]="PASS"
        except (KeyError, ValueError, OSError) as e:
            verdicts[sid]="STALE: "+str(e)
            all_good=False
    return {"id":args.id,"niche":manifest["niche_id"],
            "script_ready_for_production":all_good if manifest["mode"] != "A2_ANIMATED_SCREENPLAY" else False,
            "structural_stage_gates_passed":all_good,
            "production_authorized":False,
            "stages":verdicts,
            "notice":"Structural checks and agent attestations ONLY; not independent validation of creative factual truth"}


def advance(args):
    settings=config()
    base=project_dir(args.id,args.root)
    manifest=read_json(base/"manifest.json")
    stages={s["id"]:s for s in settings["stages"]}
    if args.stage not in stages:
        raise ValueError("Invalid stage id")
    stage=stages[args.stage]
    current=status(args)
    for prereq in stage["requires"]:
        if current["stages"][prereq]!="PASS":
            raise ValueError("Upstream gate not PASS: "+prereq)
    if args.stage=="review" and args.actor==manifest["writer_id"]:
        raise ValueError("Writer cannot approve their own script")
    hashes={rel:inspect_file(base,rel) for rel in stage_files(base,settings,stage)}
    validate_content(base,settings,stage)
    manifest["approved_stages"][args.stage]={
        "actor_id": args.actor,"approved_at_utc":iso_now(),"artifact_hashes":hashes,
        "disclaimer":"Internal artifact/reviewer attestation; not an external YouTube approval"
    }
    write_json(base/"manifest.json",manifest)
    event={"event":"stage_approved","stage":args.stage,"actor":args.actor,
           "utc":iso_now(),"artifacts":hashes}
    with (base/"audit.jsonl").open("a",encoding="utf-8") as f:
        f.write(json.dumps(event,ensure_ascii=False)+"\n")
    print(json.dumps(status(args),indent=2,ensure_ascii=False))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=PROJECTS,
                   help="Project storage root; use temporary root for tests")
    sub=p.add_subparsers(dest="command",required=True)
    init=sub.add_parser("init")
    init.add_argument("--id",required=True)
    init.add_argument("--niche",required=True)
    init.add_argument("--mode",required=True)
    init.add_argument("--minutes",required=True,type=int)
    init.add_argument("--writer",required=True)
    init.add_argument("--language",default="en-US")
    stat=sub.add_parser("status")
    stat.add_argument("--id",required=True)
    adv=sub.add_parser("advance")
    adv.add_argument("--id",required=True)
    adv.add_argument("--stage",required=True)
    adv.add_argument("--actor",required=True)
    args=p.parse_args()
    try:
        if args.command=="init":initialize(args)
        elif args.command=="status":print(json.dumps(status(args),indent=2,ensure_ascii=False))
        else:advance(args)
    except (ValueError,FileNotFoundError,PermissionError,KeyError) as e:
        p.exit(2,"BLOCKED: "+str(e)+"\n")

if __name__=="__main__":
    main()
