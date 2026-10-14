"""v209 truthful, read-only company operations and release-readiness board.

Tracks separate meanings: CHARTER, CODED, CONNECTED, RUNNING, and MEDIA_QC.
Never promotes a department based on old worker healthy flags or empty paths.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3
from typing import Any

from .contracts import DepartmentId, MediaFormat
from .departments import DEFAULT_DEPARTMENTS
from .company import stage_blueprint
from .contract_integrity import audit_company_wiring
from .specialist_media_lanes_v205 import is_specialist_lane
from .department_charters_v205 import specialist_operational_readiness


NICHES={
    "minecraft":MediaFormat.ANIMATION,
    "roblox_animation":MediaFormat.ANIMATION,
    "long_slices_game":MediaFormat.ANIMATION,
    "asmr_sleep_hands_objects":MediaFormat.DOCUMENTARY,
    "audio_storytelling_seniors":MediaFormat.PODCAST,
    "fishing_silent":MediaFormat.DOCUMENTARY,
    "rain_sleep_white_noise":MediaFormat.DOCUMENTARY,
}
PRODUCTION_ROLES={
    "WRITERS_ROOM","SCRIPT_LOGIC","DIRECTION","PERFORMANCE","CINEMATOGRAPHY",
    "PRODUCTION_DESIGN","ASSETS","TECHNICAL_DIRECTION","PRODUCTION","GENERATIVE_MEDIA",
    "VFX","EDITORIAL","AUDIO","COLOR","QC","RIGHTS","PACKAGING",
}


def required_handler_gaps(stages,handlers)->list[str]:
    """Runtime registration, distinct from static stage artifact wiring."""
    return sorted(s.stage_id for s in stages
                  if s.required and handlers.get(s.stage_id) is None)


def _read_json(file:Path):
    try:
        return json.loads(file.read_text(encoding="utf8"))
    except (OSError,ValueError,TypeError):
        return None


def _turbo_worker_state(root:Path,now:datetime,heartbeat_fresh_minutes:int=10)->dict:
    db=root/"data"/"turbo.db"
    result={
        "database_exists":db.is_file(),"stored_workers":0,
        "active_fresh_workers":0,"stale_reported_healthy":0,
        "open_work_items":0,"historical_work_states":{},
        "status":"UNAVAILABLE",
    }
    if not db.is_file():
        return result
    try:
        uri="file:"+db.resolve().as_posix()+"?mode=ro"
        with sqlite3.connect(uri,uri=True,timeout=3) as conn:
            workers=conn.execute(
                "select worker_id,healthy,last_heartbeat from workers"
            ).fetchall()
            counts=dict(conn.execute(
                "select state,count(*) from work_items group by state"
            ).fetchall())
        fresh=0; stale_healthy=0
        for _,healthy,timestamp in workers:
            try:
                seen=datetime.fromisoformat(timestamp.replace("Z","+00:00"))
                age=(now-seen.astimezone(timezone.utc)).total_seconds()
                is_fresh=-120<=age<=heartbeat_fresh_minutes*60
            except (ValueError,TypeError,AttributeError):
                is_fresh=False
            if healthy and is_fresh:fresh+=1
            elif healthy:stale_healthy+=1
        result.update({
            "stored_workers":len(workers),
            "active_fresh_workers":fresh,
            "stale_reported_healthy":stale_healthy,
            "historical_work_states":counts,
            "open_work_items":sum(counts.get(s,0) for s in
                                  ("QUEUED","PENDING","RUNNING","CLAIMED")),
            "status":"FRESH_HEARTBEATS_PRESENT" if fresh
                     else "NO_VERIFIED_FRESH_RENDER_WORKER_HEARTBEAT",
        })
    except (sqlite3.DatabaseError,OSError) as exc:
        result["status"]="WORKER_DATABASE_READ_ERROR:"+type(exc).__name__
    return result


def _research_state(root:Path)->dict:
    runtime=root/"data"/"research_runtime"
    state=_read_json(runtime/"latest_health.json") or {}
    # Windows task code 0 is scheduler transport success, never proof that a
    # new niche has been independently verified or filmed.
    logs=root/"data"/"research"/"youtube_breakout"/"logs"
    daily_files=sorted(
        logs.glob("scheduled_cinefactory_*.log"),
        key=lambda x:x.stat().st_mtime,reverse=True
    ) if logs.is_dir() else []
    daily_status="NO_CURRENT_DAILY_SCOUT_LOG"
    branch1="NO_DAILY_BRANCH_VERDICT"
    if daily_files:
        try:
            raw=daily_files[0].read_bytes()
            if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
                decoded=raw.decode("utf-16",errors="replace")
            elif raw[:400].count(b"\x00")>30:
                decoded=raw.decode("utf-16-le",errors="replace")
            else:
                decoded=raw.decode("utf-8-sig",errors="replace")
            lines=decoded.splitlines()
            for line in reversed(lines):
                if "CINEFACTORY_REAL_DAILY_SCOUT_RESULT " in line and daily_status=="NO_CURRENT_DAILY_SCOUT_LOG":
                    daily_status=(json.loads(
                        line.split("CINEFACTORY_REAL_DAILY_SCOUT_RESULT ",1)[1]
                    ).get("status") or "MISSING_RUN_STATUS")
                if "CINEFACTORY_TWO_BRANCH_DAILY_REPORT " in line:
                    branch1=(json.loads(
                        line.split("CINEFACTORY_TWO_BRANCH_DAILY_REPORT ",1)[1]
                    ).get("branch1_status") or "MISSING_BRANCH_1_VERDICT")
                if daily_status!="NO_CURRENT_DAILY_SCOUT_LOG" and branch1!="NO_DAILY_BRANCH_VERDICT":
                    break
        except (ValueError,OSError):
            daily_status="SCOUT_LOG_INVALID"
    report_file=runtime/str(state.get("report_relative",""))
    if not state.get("report_relative") or not report_file.is_file():
        report=None
    else:
        report=_read_json(report_file)
    approved=runtime/"approved_pods"
    approved_files=[p for p in approved.glob("*.json") if p.is_file()] \
                   if approved.is_dir() else []
    source=_read_json(runtime/"pod_dispatch_daily"/"latest.json")
    return {
        "latest_state":state.get("state","NO_REPORT"),
        "daily_scout_state":daily_status,
        "new_niche_branch_status":branch1,
        "canonical_report_exists":bool(report),
        "canonical_report_state":(report or {}).get("state"),
        "research_to_studio_bridge_ready":bool(
            report and report.get("bridge_ready") is True
        ),
        "approved_pod_file_count":len(approved_files),
        "independently_verified_new_0_30d_niche":False,
        "strict_official_age_verification_enabled":bool(os.environ.get(
            "YOUTUBE_DATA_API_KEY"
        )),
        "pod_watch":(source or {}).get("state","NOT_CONFIRMED"),
    }


def audit_company_readiness(root:Path,*,now:datetime|None=None)->dict[str,Any]:
    root=Path(root).resolve()
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("AUDIT_CLOCK_TIMEZONE_REQUIRED")
    now=now.astimezone(timezone.utc)
    depts={}
    for department in DepartmentId:
        charter=DEFAULT_DEPARTMENTS.get(department)
        depts[department.value]={
            "charter_specified":charter is not None,
            "tools_declared":bool(charter and charter.tools),
            "mission_declared":bool(charter and charter.mission),
            "independent_executable_verified":False,
            "independent_art_quality_qualified":False,
            "qualification":"SPEC_ONLY_NO_INDEPENDENT_QA" if charter
                            else "MISSING_SPEC",
        }
    niches={}
    for name,media in NICHES.items():
        stages=stage_blueprint(
            media,False,professional_governance=True,professional_niche=name
        )
        wiring=audit_company_wiring(stages)
        niches[name]={
            "stage_count":len(stages),"wiring_pass":wiring.valid,
            "stage_contract_errors":wiring.blocker_codes(),
            "media_family":"SPECIALIST_ORIGINAL_SOURCE"
                           if is_specialist_lane(name) else "ANIMATED_MEDIA",
            "production_qualification":"NOT_YET_ATTESTED",
        }
    worker=_turbo_worker_state(root,now)
    research=_research_state(root)
    model_root=root/".tools"/"ComfyUI"/"models"
    model_entries=[p for p in model_root.rglob("*") if p.is_file()] \
                  if model_root.is_dir() else []
    placeholder_count=sum(p.stat().st_size==0 for p in model_entries)
    project_root=root/"data"/"projects"
    independent_reviews=list(project_root.glob(
        "*/inputs/independent_film_reviews.json"
    )) if project_root.is_dir() else []
    blockers=[]
    if any(not x["wiring_pass"] for x in niches.values()):
        blockers.append("STATIC_STAGE_ARTIFACT_WIRING_INVALID")
    if research["latest_state"]!="COMPLETE" or not research[
        "research_to_studio_bridge_ready"]:
        blockers.append("RESEARCH_VERIFIED_TO_STUDIO_HANDOFF_MISSING")
    if not worker["active_fresh_workers"]:
        blockers.append("NO_VERIFIED_ACTIVE_RENDER_WORKERS")
    if not independent_reviews:
        blockers.append("NO_AUTHENTIC_INDEPENDENT_FILM_REVIEWS_SUPPLIED")
    # Finding review-file names is not signature verification or film acceptance.
    blockers += [
        "REAL_ORIGINAL_FILM_8_TO_10_MIN_ACCEPTANCE_UNPROVEN",
        "OWNER_YOUTUBE_UPLOAD_AND_ANALYTICS_FLYWHEEL_UNPROVEN",
        "FILM_STORY_ACTING_SOUND_ART_INDEPENDENT_QC_PENDING",
    ]
    return {
        "schema":"cine.company.production_readiness.v209",
        "captured_at":now.isoformat(),
        "root":str(root),
        "production_ready":False,
        "verdict":"NOT_PRODUCTION_QUALIFIED",
        "departments":depts,
        "department_counts":{"specified":sum(bool(x["charter_specified"])
                                            for x in depts.values()),
                             "declared":len(depts)},
        "niches":niches,
        "research":research,
        "workers":worker,
        "model_inventory":{
            "entries":len(model_entries),
            "zero_byte_entries":placeholder_count,
            "model_commercial_use_qualified":False,
        },
        "film": {
            "review_manifest_file_count":len(independent_reviews),
            "accepted_verified_longform_count":0,
            "actual_master_signature_review_completed":False,
            "must_run_separate_per_file_signed_review":True,
        },
        "unresolved_gates":blockers,
        "zero_paid_media_api_default":True,
        "caveat":"Code and metadata inventories cannot approve art, rights or runtime.",
    }
