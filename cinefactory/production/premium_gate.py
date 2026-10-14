"""Bind premium Autopilot execution to a source-locked production conference.

A plan is not a render, an owner's unverified local flag is not authentication,
and a successful MP4 is not commercial/creative certification.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _read(path: str) -> tuple[Path, dict, str]:
    target=Path(path).resolve(strict=True)
    data=target.read_bytes()
    obj=json.loads(data)
    if not isinstance(obj,dict):
        raise ValueError("Premium artifact must be a JSON object")
    return target,obj,hashlib.sha256(data).hexdigest()


def premium_preflight(req) -> dict | None:
    if req.production_mode not in ("slate","comfyui"):
        raise ValueError("Only slate/comfyui executors are implemented in Autopilot; Blender and Unreal require separate verified workers")
    if req.quality_tier=="diagnostic":
        if req.production_mode!="slate" and not req.visual_qc_command:
            raise PermissionError("GENERATIVE_VISUAL_QC_REQUIRED: no --allow-no-visual-qc escape")
        return None
    if req.quality_tier!="premium":
        raise ValueError("Unknown quality tier")
    if req.production_mode=="slate":
        raise PermissionError("PREMIUM_CANNOT_USE_SLATE: technical placeholder video is not finished footage")
    if not req.visual_qc_command:
        raise PermissionError("PREMIUM_VISUAL_QC_REQUIRED")
    if req.reasoning_mode=="scaffold":
        raise PermissionError("PREMIUM_SCRIPT_REQUIRES_REVIEWED_REASONING: deterministic scaffold is not a professional writer")
    if not req.studio_director_plan_file or not req.studio_conference_file:
        raise PermissionError("PREMIUM_NEEDS_DIRECTOR_AND_CONFERENCE")
    conf_path, conf, conf_sha=_read(req.studio_conference_file)
    plan_path, plan, plan_sha=_read(req.studio_director_plan_file)
    if conf.get("schema")!="cine.studio.production_conference.v1" or plan.get("schema")!="cine.studio.director_plan.v1":
        raise ValueError("Unknown conference or director plan")
    if plan.get("niche")!=conf.get("approved_niche"):
        raise PermissionError("Premium research and director niche mismatch")
    if (conf.get("deep_content_analysis_completed") is not True
        or conf.get("tool_benchmark_completed") is not True
        or conf.get("owner_approval_authenticated") is not True
        or conf.get("source_rights_status")!="CLEARED"):
        raise PermissionError("PREMIUM_RESEARCH_OR_RIGHTS_NOT_VERIFIED")
    if (plan.get("state")!="READY_FOR_DEPARTMENT_REVIEW_NOT_PRODUCTION"
        or type(plan.get("creative_missing_count")) is not int
        or plan["creative_missing_count"]!=0
        or type(plan.get("unbenchmarked_shot_count")) is not int
        or plan["unbenchmarked_shot_count"]!=0
        or not isinstance(plan.get("shots"),list)
        or not plan["shots"]):
        raise PermissionError("PREMIUM_DIRECTOR_PLAN_UNREADY")
    link=plan_path.with_name(plan_path.stem+"_research_link.json")
    if not link.is_file():
        raise PermissionError("Premium plan must be tied to an immutable research revision")
    _,source,_=_read(str(link))
    if (source.get("schema")!="cine.studio.conference_director_link.v1"
        or source.get("conference_sha256")!=conf_sha
        or source.get("director_plan_sha256")!=plan_sha):
        raise PermissionError("Premium director/conference frozen hashes mismatch")
    if conf.get("production_permission") is True or plan.get("production_permission") is True:
        # The plan/conference only give permission to a controlled TEST, never publish.
        raise PermissionError("Advisory plans cannot self-grant production/release")
    return {"plan_path":str(plan_path),"plan":plan,
            "plan_sha256":plan_sha,"conference_path":str(conf_path),
            "conference_sha256":conf_sha,"release_ready":False}


def premium_shot_gate(sources:dict|None, shots) -> dict:
    if sources is None:
        raise PermissionError("Premium preflight missing")
    planned=sources["plan"].get("shots")
    if not isinstance(planned,list) or not planned or any(
        not isinstance(item,dict) or not isinstance(item.get("shot_id"),str)
        or not item["shot_id"].strip() for item in planned
    ):
        raise PermissionError("PREMIUM_SHOT_MISMATCH: invalid planned shot IDs")
    planned_ids=[x["shot_id"] for x in planned]
    actual_shots=list(shots)
    actual_ids=[getattr(x,"shot_id",None) for x in actual_shots]
    if (len(set(planned_ids))!=len(planned_ids)
        or len(set(actual_ids))!=len(actual_ids)
        or len(planned_ids)!=len(actual_ids)
        or set(planned_ids)!=set(actual_ids)):
        raise PermissionError("PREMIUM_SHOT_MISMATCH: duplicate or missing planned/actual shot")
    expected={x["shot_id"]:x for x in planned}
    for shot in actual_shots:
        item=expected[shot.shot_id]
        if item.get("technical_route_state")!="CAPABILITY_BENCHMARKED" or item.get("missing"):
            raise PermissionError("PREMIUM_UNBENCHMARKED_SHOT: "+shot.shot_id)
        if item.get("primary_lane")!="comfyui_controlled_ai_video":
            raise PermissionError("PREMIUM_RENDERER_NOT_CONNECTED_FOR_LANE: "+str(item.get("primary_lane")))
        if item.get("duration_seconds")!=shot.duration_seconds:
            raise PermissionError("PREMIUM_DURATION_DRIFT: "+shot.shot_id)
    return {"schema":"cine.studio.premium_execution_binding.v1",
            "state":"CONTROLLED_PILOT_ELIGIBLE_NOT_CREATIVE_APPROVED",
            "source_director_sha256":sources["plan_sha256"],
            "source_conference_sha256":sources["conference_sha256"],
            "planned_shots":len(expected),"render_executor":"comfyui",
            "commercial_release_approved":False,"quality_certified":False}
