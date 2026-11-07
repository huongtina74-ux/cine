#!/usr/bin/env python3
"""Read-only historical CINE screenplay inventory and niche-specific duplicate check.

Includes legacy Script Factory projects which are NOT in the new approved ledger.
No automatic approval, no copying scripts to GitHub, no uncontrolled cross-niche
comparisons and no assumption that old agent-signed receipts are human consent.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "data/script_factory/projects"
AXES = ("hook", "goal", "central_conflict", "twist", "resolution",
        "emotional_change", "lasting_consequence")


def canon(s: object) -> str:
    if not isinstance(s, str):
        return ""
    return " ".join(re.findall(r"[^\W_]+", unicodedata.normalize("NFKC", s).casefold()))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_dict(path: Path) -> dict:
    o = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(o, dict):
        raise ValueError("Expected JSON object: " + str(path))
    return o


def fingerprint(story: dict, outline: dict) -> dict:
    # Accept the new story contract and earlier CINE's narrative contracts.
    if isinstance(story.get("story_fingerprint"), dict):
        raw = story["story_fingerprint"]
    else:
        raw = story
    spine = raw.get("causal_spine", [])
    if not isinstance(spine, list):
        spine = []
    pairs = raw.get("seeds_payoffs", [])
    if not isinstance(pairs, list):
        pairs = []
    chars = raw.get("characters", [])
    if not isinstance(chars, list):
        chars = []
    beats = outline.get("beats", [])
    if not isinstance(beats, list):
        beats = []
    first = next((b for b in beats if isinstance(b, dict)), {})
    last = next((b for b in reversed(beats) if isinstance(b, dict)), {})
    person = next((x for x in chars if isinstance(x, dict)), {})
    payoff = next((x for x in pairs if isinstance(x, dict)), {})
    result = {
        "title": raw.get("title") or raw.get("working_title") or first.get("title", ""),
        "hook": raw.get("hook") or first.get("goal") or (spine[0] if spine else ""),
        "goal": raw.get("goal") or person.get("want") or raw.get("audience_promise", ""),
        "central_conflict": raw.get("central_conflict") or raw.get("distinctive_value") or (spine[1] if len(spine) > 1 else ""),
        "twist": raw.get("twist") or payoff.get("payoff") or (spine[-2] if len(spine) > 1 else ""),
        "resolution": raw.get("resolution") or (spine[-1] if spine else "") or last.get("exit_condition", ""),
        "emotional_change": raw.get("emotional_change") or person.get("need") or raw.get("theme", ""),
        "lasting_consequence": raw.get("lasting_consequence") or last.get("exit_condition") or raw.get("theme", ""),
    }
    return {k: str(v) if v is not None else "" for k, v in result.items()}


def scan(niche_id: str, *, archive_root: Path = ARCHIVE,
         exclude_project_id: str | None = None) -> dict:
    """Enumerate EVERY local Script Factory manifest, but compare only exact niche."""
    if not re.fullmatch(r"[a-z][a-z0-9_-]{2,64}", niche_id):
        raise ValueError("Invalid research niche ID")
    if not archive_root.is_dir():
        return {"status": "ARCHIVE_NOT_MOUNTED", "niche_id": niche_id,
                "projects_seen": 0, "matching_niche": 0, "historical_records": [],
                "audit_provenance": "READ_ONLY_NO_APPROVAL"}
    records, scanned, matching = [], 0, 0
    for manifest in sorted(archive_root.glob("*/manifest.json")):
        if not manifest.resolve().is_relative_to(archive_root.resolve()):
            raise ValueError("Project manifest escapes archive")
        scanned += 1
        data = read_dict(manifest)
        if data.get("niche_id") != niche_id:
            continue
        matching += 1
        pid = data.get("project_id")
        if not isinstance(pid, str) or not pid or pid != manifest.parent.name:
            raise ValueError("Malformed matching-niche project ID in " + str(manifest))
        if pid == exclude_project_id:
            continue
        base = manifest.parent
        storyfile, outlinefile = base / "04_story/story_dna.json", base / "05_outline/beat_sheet.json"
        scriptfile = base / "08_final/final_script.md"
        if not scriptfile.is_file():
            scriptfile = base / "06_script/script.md"
        story = read_dict(storyfile) if storyfile.is_file() else {}
        outline = read_dict(outlinefile) if outlinefile.is_file() else {}
        if story.get("niche_id", niche_id) != niche_id or outline.get("niche_id", niche_id) != niche_id:
            raise ValueError("Cross-niche story or outline inside manifest " + pid)
        if not story and not scriptfile.is_file():
            continue  # initialized placeholder, not a written episode
        artifact_kind = "FULL_SCRIPT_PRESENT" if scriptfile.is_file() else "STORY_OUTLINE_ONLY"
        status = "HISTORICAL_STAGE_ATTESTATION_NOT_HUMAN_VERIFIED"
        approvals = data.get("approved_stages", {})
        if not isinstance(approvals, dict):
            raise ValueError("Malformed approved_stages in " + pid)
        script_sha = sha(scriptfile) if scriptfile.is_file() else None
        recorded = None
        if scriptfile.is_file():
            stage = "final" if scriptfile.name == "final_script.md" else "script"
            entry = approvals.get(stage, {})
            if isinstance(entry, dict):
                rel = "08_final/final_script.md" if stage == "final" else "06_script/script.md"
                recorded = entry.get("artifact_hashes", {}).get(rel) if isinstance(entry.get("artifact_hashes", {}), dict) else None
            if recorded is not None and recorded != script_sha:
                status = "STALE_SCRIPT_SHA_STAGE_ATTESTATION"
        records.append({
            "project_id": pid, "niche_id": niche_id,
            "series_id": data.get("series_id") or ("bell_leaf" if data.get("mode") == "A2_ANIMATED_SCREENPLAY" else "SERIES_NOT_RECORDED"),
            "status": status, "artifact_kind": artifact_kind,
            "story_fingerprint": fingerprint(story, outline),
            "script_path": str(scriptfile) if scriptfile.is_file() else None,
            "script_sha256": script_sha,
            "recorded_script_sha256": recorded,
            "old_factory_stages_recorded": sorted(approvals),
            "human_editor_signoff_authenticated": False,
        })
    return {"status": "READ_ONLY_NICHE_ARCHIVE_SCANNED", "niche_id": niche_id,
            "projects_seen": scanned, "matching_niche": matching,
            "historical_records": records, "audit_provenance": "READ_ONLY_NO_APPROVAL"}


def compare_plan(plan: dict, archive: dict) -> list[dict]:
    """Compare a proposed EP against source-derived historic story/outline fields."""
    found=[]
    current = plan.get("story", {})
    if not isinstance(current, dict):
        current = {}
    for old in archive["historical_records"]:
        past = old["story_fingerprint"]
        seen=[]
        for field in AXES:
            a,b=canon(current.get(field)),canon(past.get(field))
            if len(a) < 22 or len(b) < 22:
                continue
            if a==b:
                seen.append((field,1.0))
            elif len(a)>=48 and len(b)>=48:
                ratio=SequenceMatcher(None,a,b,autojunk=False).ratio()
                if ratio>=.84:
                    seen.append((field,round(ratio,3)))
        if seen:
            high=sum(k in {"central_conflict","resolution","goal","twist"} and v>=.91 for k,v in seen)
            result="BLOCK_HISTORICAL_STORY_COPY" if high>=2 else "EDITOR_REVIEW_HISTORICAL_PLOT"
            found.append({"project_id":old["project_id"],"level":result,
                          "matched_axes":[k for k,_ in seen],
                          "artifact_kind":old["artifact_kind"]})
    return sorted(found,key=lambda x:(x["level"]=="BLOCK_HISTORICAL_STORY_COPY",
                                     len(x["matched_axes"])),reverse=True)


def shingles(s: str, size: int = 7) -> set[tuple[str, ...]]:
    w=canon(s).split()
    return {tuple(w[i:i+size]) for i in range(max(0,len(w)-size+1))}


def compare_script(content: str, archive: dict, *,
                   min_common: int = 100) -> list[dict]:
    """Detect copied/repackaged dialogue across historical same-niche scripts."""
    current_shingles=shingles(content)
    matches=[]
    for old in archive["historical_records"]:
        raw=old.get("script_path")
        if not raw:
            continue
        body=Path(raw).read_text(encoding="utf-8-sig")
        old_shingles=shingles(body)
        common=len(current_shingles & old_shingles)
        if common < min_common or not current_shingles or not old_shingles:
            continue
        containment=common/min(len(current_shingles),len(old_shingles))
        level=("BLOCK_HISTORICAL_SCRIPT_COPY" if containment>=.60
               else "EDITOR_REVIEW_HISTORICAL_SCRIPT_SIMILARITY" if containment>=.15 else None)
        if level:
            matches.append({"project_id":old["project_id"],"level":level,
                "shared_seven_word_spans":common,"shorter_script_containment":round(containment,4),
                "old_script_sha256":old["script_sha256"],
                "historical_stages_not_human_verified":True})
    return sorted(matches,key=lambda x:x["shorter_script_containment"],reverse=True)


def main(argv=None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--niche", required=True)
    p.add_argument("--archive-root",type=Path,default=ARCHIVE)
    p.add_argument("--out",type=Path)
    args=p.parse_args(argv)
    try:
        report=scan(args.niche,archive_root=args.archive_root)
        result={
            "status":report["status"],"niche_id":args.niche,
            "projects_seen":report["projects_seen"],"matching_niche":report["matching_niche"],
            "story_or_script_archives":len(report["historical_records"]),
            "items":[{"project_id":r["project_id"],"artifact_kind":r["artifact_kind"],
                       "status":r["status"],"script_sha256":r["script_sha256"]}
                     for r in report["historical_records"]],
            "notice":"Archive observations are not owner-approved memory or copyright clearance."
        }
    except (ValueError,OSError,json.JSONDecodeError) as e:
        result={"status":"BLOCKED_DATA_ERROR","reason":str(e)}
    payload=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(payload,encoding="utf-8")
    print(json.dumps(result,ensure_ascii=True,indent=2))
    return 2 if result["status"]=="BLOCKED_DATA_ERROR" else 0


if __name__ == "__main__":
    sys.exit(main())
