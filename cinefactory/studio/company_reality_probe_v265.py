"""v265 independent company reality-check grader. Fail-closed, never approves publish.
Checks real stage ledger, source evidence, executable probe and decoded media QA.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime,timezone
from .runtime_route_grounding_v265 import backend_executable_probe
ROOT=Path(__file__).resolve().parents[2]
def _load(path:Path)->dict:
    data=path.read_bytes()
    return json.loads(data.decode("utf-16") if data.startswith((b"\xff\xfe",b"\xfe\xff"))
                      else data.decode("utf-8-sig"))
def grade(readiness:dict,run:dict,media:dict,routes:dict)->dict:
    workers=readiness.get("workers",{})
    departments=readiness.get("departments",{})
    records=run.get("ledger",{}).get("records",[])
    byid={r["stage_id"]:r for r in records}
    actual={x:byid.get(x,{}).get("state","UNKNOWN") for x in (
        "PROJECT_INTAKE","PORTFOLIO_GREENLIGHT","INTELLIGENCE","EVIDENCE",
        "CORPORATE_PREFLIGHT","CREATIVE_STRATEGY","PLANNING","WRITING",
        "LOGIC","DIRECTION","ASSET_BUILD","PREVIS","TECHNICAL_DIRECTION",
        "PRODUCTION","EDITORIAL","AUDIO","FINAL_QC","PUBLISHING")}
    def b(cond):return bool(cond)
    checks={
        "R1_INTELLIGENCE_BOOTSTRAPPED":b(actual["INTELLIGENCE"]=="SUCCEEDED"),
        "R2_SOURCE_AV_EVIDENCE_REVIEW":False,
        "R3_CORPORATE_PREFLIGHT":b(actual["CORPORATE_PREFLIGHT"]=="SUCCEEDED"),
        "R4_SCRIPT_ROOM_RUNNER_EXECUTED":b(actual["WRITING"]=="SUCCEEDED"),
        "R5_DIRECTOR_REAL_SHOT_PACKET":b(actual["DIRECTION"]=="SUCCEEDED"),
        "R6_ASSET_WORKER_EXECUTED":b(actual["ASSET_BUILD"]=="SUCCEEDED"),
        "R7_REAL_3D_ENGINE_VERSIONED":b(routes.get("blender.local",{}).get("available") is True),
        "R8_FFMPEG_NATIVE_VERSIONED":b(routes.get("ffmpeg.editorial",{}).get("available") is True),
        "R9_ACTIVE_RENDER_WORKER":b(workers.get("active_fresh_workers",0)>0),
        "R10_ACTUAL_MOVING_AND_AUDIBLE_RND_MEDIA":b(media.get("actual_playable_video_audio")
                       and media.get("full_file_decode_QA")),
        "R11_1080P_3D_SCENE_QUALITY":False,
        "R12_FULL_OUTPUT_MOVING_IMAGE_SIGNOFF":False,
        "R13_COMPANY_EPISODE_END_TO_END":b(run.get("complete")),
        "R14_REAL_RELEASE_AUTHORIZED":False,
    }
    unsafe=[];
    if readiness.get("production_ready") is True and not checks["R11_1080P_3D_SCENE_QUALITY"]:
        unsafe.append("DECLARED_PRODUCTION_READY_WITHOUT_REAL_CINEMATIC_ACCEPTANCE")
    if actual["EVIDENCE"]=="SKIPPED" and actual["INTELLIGENCE"]=="SUCCEEDED":
        unsafe.append("NEW_PROJECT_REFERENCE_RESEARCH_NOT_BOUND_TO_EVIDENCE_STAGE")
    if not checks["R7_REAL_3D_ENGINE_VERSIONED"]:
        unsafe.append("BLENDER_EXECUTABLE_UNVERIFIED")
    if workers.get("stale_reported_healthy",0)>0 and not checks["R9_ACTIVE_RENDER_WORKER"]:
        unsafe.append("STALE_WORKER_HEALTH_MUST_NOT_BE_CONSIDERED_ACTIVE")
    if run.get("complete") and not checks["R3_CORPORATE_PREFLIGHT"]:
        unsafe.append("RUNNER_BYPASSED_CORPORATE_PREFLIGHT")
    made=sum(checks.values())
    return {
        "schema":"cine.v265.company_actual_run_acceptance",
        "project_id":run.get("project_id"),
        "overall_verdict":"NOT_CINEMATICALLY_PRODUCTION_QUALIFIED",
        "actual_production_line_complete":False,
        "trial_isolation":"ORIGINAL_IP_ONLY_NO_OAUTH_NO_PUBLISH",
        "claims_policy":"RND_PREVIEW_PASS_IS_NOT_3D_PRODUCTION_PASS",
        "automated_test_checks_passed":made,
        "automated_test_checks_total":len(checks),
        "checks":checks,"runner_stages":actual,
        "runner_cycles":run.get("cycles"),
        "runner_errors":run.get("errors"),
        "department_count":len(departments),
        "departments_independently_executable_verified":sum(
            1 for x in departments.values() if x.get("independent_executable_verified")),
        "departments_independently_art_quality_verified":sum(
            1 for x in departments.values() if x.get("independent_art_quality_qualified")),
        "worker_state":workers,"runtime_probes":routes,
        "RND_15_second_media":{"playable":media.get("actual_playable_video_audio"),
           "file":media.get("media_path"),"duration_sec":media.get("media_duration_sec"),
           "dimensions":media.get("dimensions"),
           "scratch_tts":media.get("offline_TTS"),
           "render_wall_sec":media.get("render_wall_sec"),
           "true_voxel_3d":media.get("camera_3D"),
           "quality":"FAIL_FOR_PROFESSIONAL_3D;PASS_FOR_BASIC_EDITORIAL_TRANSCODE"},
        "findings":unsafe,
        "critical_priority":[
            {"id":"P0-RESEARCH-BRIDGE","problem":"Existing sourced A-D and G02 packets not bound to new company project. EVIDENCE skipped; corporate preflight lacks competitor evidence","fix":"Versioned, provenance-checked import of Company Youtube niche report & CineFactory G02 source ledger into project blackboard. No auto G02 promotion.","acceptance":"new project sees original video IDs/shot evidence and marks source G02 only with real completed semantics, rejects metadata-only inputs"},
            {"id":"P0-BACKEND-TRUTH","problem":"Capability registry optimistic Blender executable even without probed binary","fix":"Ground professional routing against local executable --version. Implemented in v265; ongoing proof for other providers required","acceptance":"missing Blender route non-executable with explicit blocker; FFmpeg validated available"},
            {"id":"P0-WORKER-HEALTH","problem":"8 stale healthy worker rows, 0 fresh active heartbeats","fix":"Require fresh process heartbeats and confirmed GPU/CPU task execution; archive stale rows","acceptance":"1 worker launches an actual scene shot and receives nonempty render receipt"},
            {"id":"P1-SCRIPT-SCENE-QUALITY","problem":"82 storyboard drawings and 27 static OBJ parts are NOT functioning character rigs or final cinematic boards","fix":"New rig/expressions/bone-safe animation, camera movement design and original VO readthrough before script lock","acceptance":"one approved original 3D 15–45s clip with visible character acting and motion"},
            {"id":"P1-AUDIO-EDITORIAL","problem":"15s sound and offline voice works, but no character-specific casting, timing, foley mixing or sound designer review","fix":"Cue/timing/phoneme pipeline, dialogue loudness checks, music and ambience licensing, editorial audit","acceptance":"audio reviewer verifies timing and clarity of full 45s 1080p pilot"},
            {"id":"P1-AV-REVIEW","problem":"120 G02 source windows not independently semantically heard and watched","fix":"Separate AI visual+audio agent second pass over lawful native source and human signoff where required","acceptance":"timecoded review coverage and disagreements resolved, G02 never self-signed"},
            {"id":"P2-CINEMATIC-ACCEPTANCE","problem":"Media decoder PASS but art quality fails","fix":"Independent visual QA, shot continuity, motion, cinematography, full audio and per-scene defect classification","acceptance":"1080p24 original moving film meets scorecard; no passing on encode alone"}
        ],
    }
def evaluate(root:Path=ROOT,write:bool=False)->dict:
    base=root/"data/verification"
    ready=_load(base/"v265_company_reality_check_readiness.json")
    run=_load(base/"v265_company_run_probe.json")
    media=_load(base/"v265_company_e2e_reality/rnd_animatic_15s_qa.json")
    routes={k:backend_executable_probe(k) for k in ("blender.local","ffmpeg.editorial")}
    report=grade(ready,run,media,routes)
    report["measured_at"]=datetime.now(timezone.utc).isoformat()
    if write:
        file=base/"v265_company_e2e_reality/company_reality_scorecard.json"
        file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        report["file"]=str(file)
    return report
if __name__=="__main__":
    v=evaluate(write=True)
    print(json.dumps({"score":f"{v['automated_test_checks_passed']}/{v['automated_test_checks_total']}",
      "real_runner_complete":v["actual_production_line_complete"],
      "stages":v["runner_stages"],
      "findings":v["findings"],"file":v["file"]},ensure_ascii=False,indent=2))
