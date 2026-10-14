"""CineFactory v225: Maizen-style real-gameplay departmental kickoff.

The studio has 26 unique *desk-work* receipts (research/script/shot/rights/QC
plans). This is not 26 paid LLM agent calls or actual Minecraft capture.
Safe local materialization only; no shell, game process, mods, OBS recording,
MCP installs, remote provider, upload, login, or publishing.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
from typing import Any

from .contracts import DepartmentId
from .minecraft_source_evidence_v224 import minecraft_g01_g02_evidence

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"config/niches/minecraft/maizen_studio_a_v225.json"
OUTPUT=ROOT/"data/verification/v225_maizen_studio_a_kickoff"
STATES=frozenset({"DRAFT_CREATED","PARTIAL_EVIDENCE","BLOCKED_EXTERNAL_DEPENDENCY"})
LANE="SCRIPTED_MINECRAFT_GAMEPLAY"
SCHEMA="cine.minecraft.maizen_department_kickoff.v225"


def load_maizen_studio_a() -> dict[str, Any]:
    obj=json.loads(SOURCE.read_text(encoding="utf8"))
    if obj.get("schema")!=SCHEMA or obj.get("project_id")!="MAI01_WATERFALL" or obj.get("lane")!=LANE:
        raise ValueError("MAIZEN_STUDIO_IDENTITY_MISMATCH")
    approvals=obj["auth"]
    if approvals.get("owner_selected_maizen_style") is not True or any(
        approvals.get(x) is not False
        for x in ("game_or_software_purchase","paid_cloud_call","download_or_install",
                  "release","auto_approve_claude_project_mcp")
    ):
        raise ValueError("MAIZEN_PROJECT_UNAUTHORIZED_ACTION")
    if obj["pilot"]["real_game_captured"] or obj["episode"]["actual_episode_video_exists"]:
        raise ValueError("MAIZEN_UNVERIFIED_FOOTAGE_CLAIM")
    from .minecraft_company_roadmap_v223 import load_minecraft_master_company_plan
    expected={d.value for d in DepartmentId}
    master=load_minecraft_master_company_plan()
    if len(master["departments"])!=26:
        raise ValueError("MINECRAFT_COMPANY_INCOMPLETE")
    dept=obj["all_26_departments"]
    if set(dept)!=expected or len(dept)!=26:
        raise ValueError("ALL_DEPARTMENTS_MUST_HAVE_DESK_WORK")
    if any(
        not r["deliverable"] or not isinstance(r["output"],dict) or not r["output"]
        or r["state"] not in STATES
        for r in dept.values()
    ):
        raise ValueError("DEPARTMENT_OUTPUT_MISSING")
    shots=obj["pilot"]["shots"]
    if len(shots)!=9 or [s["id"] for s in shots]!=["P"+str(i).zfill(2) for i in range(1,10)]:
        raise ValueError("MAIZEN_SHOT_COUNT")
    start=0
    for sh in shots:
        if sh["start"]!=start or sh["end"]<=start or not sh["dialogue"] or not sh["dependency"]:
            raise ValueError("MAIZEN_SHOT_SEQUENCE")
        start=sh["end"]
    if start!=obj["pilot"]["seconds"] or start!=45:
        raise ValueError("MAIZEN_PILOT_LENGTH")
    chapters=obj["episode"]["chapters"]
    if len(chapters)!=7:
        raise ValueError("MAIZEN_CHAPTER_COUNT")
    start=0
    for ch in chapters:
        if ch["start"]!=start or ch["end"]<=start or not ch["story_purpose"]:
            raise ValueError("MAIZEN_CHAPTER_CONTINUITY")
        start=ch["end"]
    if start!=obj["episode"]["duration_seconds"] or start!=840:
        raise ValueError("MAIZEN_EPISODE_DURATION")
    critical=obj["critical_dependencies"]
    if not critical or any(not isinstance(x,str) or not x for x in critical):
        raise ValueError("MAIZEN_CRITICAL_GATES_MISSING")
    return obj


def maizen_department_work(department: str) -> dict:
    if department not in {d.value for d in DepartmentId}:
        raise ValueError("UNKNOWN_DEPARTMENT")
    obj=load_maizen_studio_a()
    receipt=obj["all_26_departments"][department]
    from .maizen_full_video_gate_v227 import maizen_full_video_review_gate
    full_review=maizen_full_video_review_gate()
    return {
        "full_reference_review_required_before_department_conclusions":True,
        "full_reference_review_passed":full_review["cohort_gate_passed"],
        "may_promote_department_production_method_or_recipe":False,
        "schema":"cine.minecraft.maizen_department_work.v225",
        "project_id":obj["project_id"],"owner":department,
        "state":receipt["state"],"deliverable":receipt["deliverable"],
        "draft":receipt["output"],
        "does_not_mean_stage_approval":True,
        "production_execution_qualified":False,
    }


def maizen_studio_status() -> dict:
    d=load_maizen_studio_a()
    snapshot=minecraft_g01_g02_evidence()
    count=dict(Counter(x["state"] for x in d["all_26_departments"].values()))
    from .maizen_full_video_gate_v227 import maizen_full_video_review_gate
    research_gate=maizen_full_video_review_gate()
    return {
        "schema":"cine.minecraft.maizen_studio_status.v225",
        "project":d["project_id"],
        "selected_lifecycle":"ACTIVE_DESK_RESEARCH_AND_PREPRO_ONLY",
        "source_truth":LANE,
        "department_count":len(d["all_26_departments"]),
        "deliverable_count":len(d["all_26_departments"]),
        "department_states":count,
        "full_competitor_video_first_research_gate":research_gate,
        "seven_stage_production_method_conclusions_allowed":research_gate["cohort_gate_passed"],
        "all_department_v225_handoffs_are_only_preliminary_drafts":True,
        "pilot_shot_count":len(d["pilot"]["shots"]),
        "pilot_seconds":d["pilot"]["seconds"],
        "episode_planned_seconds":d["episode"]["duration_seconds"],
        "episode_chapter_count":len(d["episode"]["chapters"]),
        "working_title":d["episode"]["working_title"],
        "research_g01":snapshot["phase_g01_status"],
        "research_g02":snapshot["phase_g02_status"],
        "full_competitor_video_audio_watches":research_gate["full_verified_videos"],
        "blocking_dependencies":d["critical_dependencies"],
        "real_minecraft_capture_ready":False,
        "fully_rendered_pilot_exists":False,
        "all_departments_have_written_draft_or_blocker":True,
        "all_departments_completed_production":False,
        "credits_spent":0,"production_release_authorized":False,
        "video_published":False,
    }


def materialize_maizen_desk_receipts(output_dir: Path|None=None) -> dict:
    """Materialize deterministic departmental desk handoffs; never run media jobs.

    An output_dir parameter exists for isolated tests; the CLI only uses the
    fixed internal OUTPUT. Each file is first-party immutable-once-materialized
    data with recorded SHA256, not a completed 3D or gameplay result.
    """
    data=load_maizen_studio_a()
    output=(output_dir if output_dir is not None else OUTPUT).resolve()
    root=ROOT.resolve()
    if output_dir is None and not output.is_relative_to(root):
        raise ValueError("PROJECT_OUTPUT_OUTSIDE_REPOSITORY")
    if output.exists() and output.is_symlink():
        raise ValueError("UNTRUSTED_OUTPUT_SYMLINK")
    output.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for dept in DepartmentId:
        work=maizen_department_work(dept.value)
        receipt_text=json.dumps(work,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
        filename=dept.value.lower()+".json"
        destination=output/filename
        if destination.is_symlink():
            raise ValueError("SYMLINK_WORK_PRODUCT_BLOCKED")
        digest=sha256(receipt_text.encode("utf8")).hexdigest()
        # Prevent rewriting an independently edited product. Fail closed.
        if destination.exists():
            existing=destination.read_bytes()
            if sha256(existing).hexdigest()!=digest:
                raise ValueError("DEPARTMENT_HANDOFF_ALREADY_EDITED")
        else:
            destination.write_bytes(receipt_text.encode("utf8"))
        manifest.append({"owner":dept.value,"file":filename,
                         "sha256":digest,"state":work["state"]})
    status=maizen_studio_status()
    final={
        "schema":"cine.minecraft.maizen_studio_kickoff_receipts.v225",
        "project":data["project_id"],
        "receipt_count":len(manifest),
        "status":status,
        "receipts":manifest,
        "actual_video_capture_receipts":0,
        "approvals_modified":False,
        "remote_ai_calls":0,
    }
    target=output/"manifest.json"
    text=json.dumps(final,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if target.is_symlink():
        raise ValueError("SYMLINK_MANIFEST_BLOCKED")
    if target.exists() and target.read_bytes()!=text.encode("utf8"):
        raise ValueError("DEPARTMENT_MANIFEST_EDIT_CONFLICT")
    target.write_bytes(text.encode("utf8"))
    return {**status,"handoff_manifest":str(target),
            "verified_department_handoffs":len(manifest)}
