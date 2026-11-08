#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CINE AUDIO portfolio: create-only parent -> 3 isolated research + production contracts.

CINE owns strategy/research/creative specification. Afanta owns physical audio,
media QC and release. Existing projects and compiled AfantaStudio.exe are untouched.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AFANTA_DEFAULT = ROOT.parents[1] / "AfantaStudio_Viettruyen" / "AfantaStudio_Viettruyen"
# One authoritative strategy payload. Code only READS the canon, never
# hardcodes a second list of three niches/stages/rules.
PORTFOLIO_SOURCE=ROOT/"config/audio/branch_registry_v1.json"
def _read_canonical():
    if not PORTFOLIO_SOURCE.is_file():
        raise FileNotFoundError("CANONICAL_CINE_AUDIO_REGISTRY_MISSING")
    data=json.loads(PORTFOLIO_SOURCE.read_text(encoding="utf-8-sig"))
    if (data.get("schema")!="cine-audio-portfolio-v1"
        or data.get("parent_niche_id")!="audio"
        or len(data.get("branches",[]))!=3
        or len({b["id"] for b in data["branches"]})!=3
        or len({b["afanta_slug"] for b in data["branches"]})!=3
        or len(data.get("common_stage_ids",[]))!=13
        or data.get("publish_authorized") is not False):
        raise ValueError("INVALID_CANONICAL_CINE_AUDIO_STRATEGY")
    return data
_CANON=_read_canonical()
VERSION=_CANON["schema"]
STAGES=_CANON["common_stage_ids"]
BRANCHES=_CANON["branches"]

def canonical(obj):
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
def sha(blob):
    return hashlib.sha256(blob).hexdigest()
def portfolio():
    return _read_canonical()

def package_data(b):
    id=b["id"]; factual=b["mode"]=="factual_sleep"
    niche={
        "niche": id, "niche_id":id, "parent_niche_id":"audio", "label":b["name"],
        "display_name":b["name"],"status":"pilot","owner_greenlight":{"by":None,"at":None},
        "identity":{"language":"en-US","audience":b["audience"],"promise":b["promise"],
                    "made_for_kids":None,"format":{"length_seconds":[b["target_minutes"]*60*3//4,b["target_minutes"]*60*5//4],
                    "cadence_per_week":1,"aspect":"16:9"}},
        "research":{"updated":None,"sources":[],"competitors":[],"outliers_studied":[],
                    "audience_evidence":[],"saturated":[],"gaps":[]},
        "format_grammar":{"hook":"No fabricated source facts; establish character need or quiet curiosity immediately",
                         "beats":b["structure"],"narration_wpm":sum(b["wpm"])//2,
                         "no_characters":True,"character_policy":"Each episode has its own cast; no shared canon cast across unrelated episodes.",
                         "avg_shot_seconds":15 if id=="mom_grandma_family_original" else 24,
                         "pattern_interrupt_seconds":None,
                         "title_pattern":"Specific question / narrative tension, truthful non-sensational",
                         "thumbnail_pattern":"One original focal subject; readable mobile typography"},
        "kpi":{"baseline":{"views_per_day_median":None,"ctr_pct":None,"avg_view_pct":None},
               "target":{"views_per_day_median":None,"ctr_pct":None,"avg_view_pct":None}},
        "policy":{"ai_disclosure":None,"ai_disclosure_reason":"Decide for each real production under current policy",
                  "originality_axes":(["people and goals","setting and event cause","choice consequences","ending emotional meaning"]
                                    if not factual else ["source question","time and place","evidence path","structure of explanation"]),
                  "forbidden":["copyrighted read-aloud source text","unlicensed music/images",
                               "mass-produced identical templates","unsupported fact claims"],
                  "inauthentic_risk_notes":"Each episode needs separately reviewed original contribution; no auto-publish."},
        "risks":["Unverified audio-only competitor research","Actual audience RPM unknown",
                 "Channel not created","Human rights and policy review required"],
    }
    bible={"niche":id,"parent_niche_id":"audio","presentation":"audio_first_16_9",
           "visuals":b["graphics"],"voice_bible":{"wpm_range":b["wpm"],"voice_lock":"PENDING_HUMAN_AUDITION",
           "mastered_audio":"PENDING_REAL_WAV","script_mode":"source_checked_nonfiction" if factual else "wholly_original_fiction"},
           "story_structure":b["structure"],"sound_rules":b["sound"],
           "style":"Audio-led cinematic 16:9 visual context with independently licensed imagery, restrained movement, coherent originals and no repetitive low-effort slideshow.",
           "palette":{"deep_navy":"#17263C","slate":"#6584A1","mist":"#B6C6D4","white":"#F1F4F6"},
           "lighting":"Low-stimulation clean balanced neutral light. No sudden exposure shifts, flashing titles or misleading simulated archival/telescope images.",
           "camera":{"shot_sizes":["WS","MS","CU","INSERT"],
                     "rules":["Establish each genuinely new context before relevant historical/scientific detail or emotional object closeup.",
                              "Change an image only when narrative information changes; no random zoom or duplicate reframe."]},
           "direction":{"playbook":"audio_led_story","pipeline":"pictures","shot_cards_required":True,
                        "rules":["Every shot supports verifiable factual context or a distinct story beat.",
                                 "Keep transitions slow and readable, matching the narration rather than forcing novelty."]},
           "characters":[],
           "color_palette":["#17263C","#6584A1","#B6C6D4","#F1F4F6"],
           "visual_claims":"All footage/photos/illustrations must have documented provenance."}
    toolkit={"niche":id,"parent_niche_id":"audio","execution_owner":"Afanta Studio sidecar",
             "stages":{stage:[{"id":"afanta_manual_gate_"+stage,
                          "kind":"manual","license":"Requires episode-specific commercial-use and rights review",
                          "commercial":False,"production":False,"requires":[],
                          "notes":"External Afanta execution. Do NOT mark production-qualified until real reviewed media and evidence exist."}]
                       for stage in STAGES},
             "targets":{"audio_first":True,"resolution":"1920x1080","content_scope":id},
             "hold":[],"afanta_slug":b["afanta_slug"],"afanta_niche":b["afanta_niche"],
             "commands":{
                 "research":"python tools/afanta_studio.py scan --niche "+b["afanta_niche"]+" --max 8 --out research_candidates.json",
                 "research_verified":"python tools/afanta_studio.py ingest --slug "+b["afanta_slug"]+" --file vetted_audio_research.json",
                 "writer_brief":"python tools/afanta_studio.py brief --slug "+b["afanta_slug"],
                 "draft":"python tools/afanta_studio.py draft-local --slug "+b["afanta_slug"]+" --model qwen3:8b",
                 "tts":"python tools/afanta_studio.py tts --slug "+b["afanta_slug"]+" --voice REVIEWED_VOICE --rights-evidence LICENSE_EVIDENCE",
                 "audio_qc":"python tools/afanta_studio.py audio-qc --slug "+b["afanta_slug"]+" --file mastered_audio.wav",
                 "render":"python tools/afanta_studio.py render --slug "+b["afanta_slug"]+" --cover cover.png --audio mastered_audio.wav",
                 "video_qc":"python tools/afanta_studio.py video-qc --slug "+b["afanta_slug"]+" --file release_video.mp4",
                 "release":"python tools/afanta_studio.py release --slug "+b["afanta_slug"],
             },"note":"Commands are a planned interface, not an execution or media acceptance report."}
    learn={"niche":id,"parent_niche_id":"audio","analytics_source":"own verified YouTube Studio only",
           "hypotheses":[],"approved_learnings":[],"unverified_assumptions":[]}
    research={"niche":id,"audience_questions":[b["audience"],b["promise"]],
              "competitor_questions":["Only exact audio-led English peers with verified join dates, video ages, and comparable 20m+ durations",
                                      "5+ age-matched video baselines and independent 2+ million-view flags"],
              "trend_sources":["YouTube public metadata with provenance","Reddit topics as broad needs only",
                               "Goodreads reviews as genre feedback only"],
              "production_forensics_questions":["Can we sustain distinctive storytelling/verified nonfiction?",
                                              "Actual creator costs and rights evidence per 30-120m episode?"]}
    readme="# "+b["name"]+"\n\nParent: **audio**. Mode: **"+b["mode"]+"**. Afanta slug: `"+b["afanta_slug"]+"`.\n\n"+b["promise"]+"\n\n## Series lanes\n"+ "".join("- "+x+"\n" for x in b["subtopics"])+"\n## Release posture\nConfiguration only, research and media approvals required. Never publish by default.\n"
    return {
        "niche.yaml":canonical(niche),"visual_bible.yaml":canonical(bible),
        "toolkit.yaml":canonical(toolkit),"learnings.yaml":canonical(learn),
        "research.yaml":canonical(research),"README.md":readme.encode("utf-8"),
    }
def required_files(root,afanta):
    p=portfolio()
    blob=canonical(p)
    files={
        root/"config/audio/branch_registry_v1.json":blob,
        afanta/"studio_os/audio_portfolio_contract_v1.json":blob,
    }
    for b in BRANCHES:
        for name,body in package_data(b).items():
            files[root/"config"/"niches"/b["id"]/name]=body
        project={
            "schema":"cine-afanta-audio-channel-v1","parent_niche_id":"audio",
            "branch_id":b["id"],"channel_key":b["key"],
            "afanta_niche":b["afanta_niche"],"afanta_slug":b["afanta_slug"],
            "portfolio_sha256":sha(blob),"stage_ids":STAGES,
            "production_status":"RESEARCH_AND_QC_PENDING",
            "youtube_created":False,"automatic_release_authorized":False,
        }
        files[afanta/"output/audio_studio"/b["afanta_slug"]/"cine_audio_branch_contract.json"]=canonical(project)
    return files
def preflight(root,afanta):
    data=json.loads((root/"config/research/per_niche/niches.json").read_text(encoding="utf-8-sig"))
    research_ids={r["id"] for r in data["niches"]}
    if len(BRANCHES)!=3 or len({b["id"] for b in BRANCHES})!=3 or len({b["key"] for b in BRANCHES})!=3:
        raise ValueError("EXACTLY_THREE_UNIQUE_CHILD_BRANCHES_REQUIRED")
    for b in BRANCHES:
        if b["id"] not in research_ids:raise ValueError("MISSING_EXISTING_RESEARCH_SCOPE:"+b["id"])
        folder=afanta/"output/audio_studio"/b["afanta_slug"]
        state=json.loads((folder/"studio_state.json").read_text(encoding="utf-8-sig"))
        plan=json.loads((folder/"channel_plan.json").read_text(encoding="utf-8-sig"))
        if state.get("slug")!=b["afanta_slug"] or state.get("niche")!=b["afanta_niche"]:
            raise ValueError("AFANTA_NICHE_SCOPE_MISMATCH:"+b["id"])
        if plan.get("channel_key")!=b["key"] or plan.get("niche")!=b["afanta_niche"]:
            raise ValueError("AFANTA_CHANNEL_PLAN_MISMATCH:"+b["id"])
        if state.get("release",{}).get("privacy")!="private" or state.get("release",{}).get("remote_upload_enabled"):
            raise ValueError("EXISTING_PROJECT_RELEASE_STATE_NEEDS_REVIEW:"+b["id"])
    if not (afanta/"studio_os/core.py").is_file():raise ValueError("AFANTA_SIDECAR_NOT_FOUND")
    return True
def install(root,afanta):
    root,afanta=root.resolve(),afanta.resolve()
    preflight(root,afanta)
    files=required_files(root,afanta)
    # Safe preflight across BOTH roots: any modified contract blocks all writes.
    for path,payload in files.items():
        if path.exists() and path.read_bytes()!=payload:
            raise FileExistsError("CONTRACT_EXISTS_WITH_DIFFERENT_CONTENT:"+str(path))
    created=[]
    for path,body in files.items():
        if path.exists():continue
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open("xb") as fh:fh.write(body)
        created.append(str(path))
    return {"status":"LOCAL_AUDIO_PORTFOLIO_CONFIGURED_RELEASE_HOLD",
            "parent":"audio","children":len(BRANCHES),"files_created":created,
            "files_verified":len(files),"portfolio_sha256":sha(canonical(portfolio())),
            "preserves_existing_afanta_exe":True,"youtube_accounts_created":0,"uploads":0}
def audit(root,afanta):
    preflight(root,afanta)
    files=required_files(root,afanta)
    issues=[str(p) for p,body in files.items() if not p.is_file() or p.read_bytes()!=body]
    rows=[]
    for b in BRANCHES:
        state=json.loads((afanta/"output/audio_studio"/b["afanta_slug"]/"studio_state.json").read_text(encoding="utf-8-sig"))
        evidence=state.get("evidence") or {}
        rows.append({"branch":b["id"],"parent":"audio","afanta_slug":b["afanta_slug"],
                     "mode":b["mode"],"project_phase":state["phase"],
                     "research_verified":bool(evidence.get("research")),
                     "audio_asset_present":bool(evidence.get("audio")),
                     "video_asset_present":bool(evidence.get("video")),
                     "youtube_created_by_this_work":False,"release_authorized_by_this_work":False,
                     "next_action":"Independent evidence, script, human voice/rights review, media QC and explicit release approvals"})
    return {"status":"CONTRACTS_VALID_RESEARCH_QC_RELEASE_PENDING" if not issues else "CONTRACT_MISMATCH",
            "issues":issues,"branches":rows,"portfolio_sha256":sha(canonical(portfolio())),
            "note":"CONFIGURATION != full E2E success, verified audio or publication."}
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("command",choices=["install","audit","show"])
    p.add_argument("--afanta-root",type=Path,default=AFANTA_DEFAULT)
    args=p.parse_args(argv)
    if args.command=="show":out=portfolio()
    elif args.command=="install":out=install(ROOT,args.afanta_root)
    else:out=audit(ROOT,args.afanta_root)
    print(json.dumps(out,ensure_ascii=False,indent=2))
    return 2 if out.get("issues") else 0
if __name__=="__main__":raise SystemExit(main())
