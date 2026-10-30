#!/usr/bin/env python3
"""Single CINE project entrypoint: Slow English A2 Bell & Leaf source preflight.

Compiles separate one-line Flow prompts and blocking QC results from a shot list.
Does not render images, invent approvals, synthesize voice, or publish videos.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from cinefactory.studio.slow_english_a2 import BellLeafCanon, CanonError

def run(repo_root: Path, script_file: Path, out: Path):
    bible = BellLeafCanon(repo_root)
    script = json.loads(script_file.read_text(encoding="utf-8"))
    if script.get("project_id") != "slow_english_a2_bell_leaf":
        raise CanonError("Input belongs to a different CINE project")
    shots = script.get("shots")
    if not isinstance(shots, list) or not shots:
        raise CanonError("A2 production requires a nonempty shots list")
    ids = [s.get("shot_id") for s in shots]
    if not all(ids) or len(ids) != len(set(ids)):
        raise CanonError("Every shot must have a distinct shot_id")
    manifest=[];flow_prompts=[];video_prompts=[]
    for i,shot in enumerate(shots):
        result=bible.resolve_shot(shot)
        result["timeline_start_seconds"] = i * 10
        result["timeline_end_seconds"] = (i+1) * 10
        manifest.append(result)
        flow_prompts.append(bible.flow_prompt(shot))
        action = " ".join(str(shot.get("action","")).split())
        video_prompts.append(
            f"{shot['shot_id']} — one uninterrupted 10.0-second Bell & Leaf CGI animation, "
            f"starting from the separately approved first-frame image; {action}; "
            "0-2s situation, 2-7s natural body/eye/facial movement and meaningful action, "
            "7-10s follow-through and reaction; keep exact original faces and fixed set, "
            "real acting not camera-only zoom, preserve Bubu tail sparkles; "
            "use approved per-character WAV and real lip sync only where verified; "
            "no embedded subtitles, 16:9 full frame, neutral D55 white balance."
        )
    out.mkdir(parents=True,exist_ok=True)
    for name,prompts in [("FLOW_IMAGE_PROMPTS_ONE_LINE.txt",flow_prompts),("MUSE_VIDEO_PROMPTS_ONE_LINE.txt",video_prompts)]:
        (out/name).write_text("\n\n".join(prompts)+"\n",encoding="utf-8")
    status = "BLOCKED_FOR_PRODUCTION" if any(r["blockers"] for r in manifest) else "REFERENCES_VERIFIED_PROVIDER_UPLOAD_AND_MEDIA_QC_REQUIRED"
    report = {"project_id":"slow_english_a2_bell_leaf","shot_count":len(shots),
              "planned_duration_seconds":len(shots)*10,"reference_preflight_status":status,
              "approved_media_rendered_by_this_tool":0,"muse_video_e2e_verified":False,"shots":manifest}
    (out/"REFERENCE_PREFLIGHT_QC.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--shots",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report=run(a.repo,a.shots,a.out)
    print(json.dumps({k:v for k,v in report.items() if k!="shots"},ensure_ascii=False))
