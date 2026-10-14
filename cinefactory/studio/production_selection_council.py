from __future__ import annotations
"""v1.6.31: evidence-first selection of production methods by niche and stage.

Proposals are not certifications: actual executable, scoped benchmark, rights
and per-unit cost evidence are mandatory for automatic production routing.
This council advises existing SceneConference + MethodSwitch; never bypasses
their policies or triggers a render/installation/payment by itself.
"""
from enum import StrEnum
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field, model_validator


class Stage(StrEnum):
    RESEARCH = "RESEARCH"
    SCRIPT = "SCRIPT"
    MUSIC = "MUSIC"
    VOICE = "VOICE"
    CHARACTER_RIG = "CHARACTER_RIG"
    ANIMATION = "ANIMATION"
    GAME_RUNTIME = "GAME_RUNTIME"
    AI_VIDEO = "AI_VIDEO"
    GRAPHICS_2D = "GRAPHICS_2D"
    CAPTURE = "CAPTURE"
    AUDIO_POST = "AUDIO_POST"
    EDITORIAL = "EDITORIAL"
    FINAL_QC = "FINAL_QC"


class ToolState(StrEnum):
    DISCOVERED = "DISCOVERED"
    PRESENT = "PRESENT"
    EXECUTABLE = "EXECUTABLE"
    BENCHMARKED = "BENCHMARKED"
    QUALIFIED_FOR_SCOPE = "QUALIFIED_FOR_SCOPE"


class ToolEvidence(BaseModel):
    method_id: str
    tool_id: str
    stage: Stage
    supported_niches: set[str] = Field(default_factory=lambda: {"*"})
    capability_tags: set[str] = Field(default_factory=set)
    state: ToolState = ToolState.DISCOVERED
    is_local: bool = True
    paid_api_required: bool = False
    license_approved: bool = False
    license_source_url: str | None = None
    license_note: str = "LICENSE_NOT_REVIEWED_FOR_SCOPE"
    executable_evidence: str | None = None
    benchmark_evidence: str | None = None
    actual_measured_quality: float | None = Field(default=None, ge=0., le=1.)
    actual_cost_usd_per_finished_minute: float | None = Field(default=None, ge=0.)
    actual_elapsed_minutes_per_finished_minute: float | None = Field(default=None, gt=0.)
    actual_peak_vram_gb: float | None = Field(default=None, ge=0.)
    scope_verified: bool = False
    is_existing_media_reuse: bool = False
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def no_unbacked_measurements_or_license(self):
        metrics=(
            self.actual_measured_quality,self.actual_cost_usd_per_finished_minute,
            self.actual_elapsed_minutes_per_finished_minute,self.actual_peak_vram_gb
        )
        if any(x is not None for x in metrics) and not self.benchmark_evidence:
            raise ValueError("MEASURED_METRICS_REQUIRE_BENCHMARK_EVIDENCE")
        if self.state in {ToolState.EXECUTABLE,ToolState.BENCHMARKED,ToolState.QUALIFIED_FOR_SCOPE} and not self.executable_evidence:
            raise ValueError("EXE_STATE_REQUIRES_EXECUTABLE_EVIDENCE")
        if self.state in {ToolState.BENCHMARKED,ToolState.QUALIFIED_FOR_SCOPE} and not self.benchmark_evidence:
            raise ValueError("BENCHMARK_STATE_REQUIRES_BENCHMARK_EVIDENCE")
        if self.state==ToolState.QUALIFIED_FOR_SCOPE and not self.scope_verified:
            raise ValueError("QUALIFIED_STATE_REQUIRES_SCOPE_VERIFICATION")
        if self.license_approved and not self.license_source_url:
            raise ValueError("APPROVED_LICENSE_NEEDS_SOURCE")
        return self


class ShotToolRequest(BaseModel):
    project_id: str
    niche_id: str
    shot_id: str
    stage: Stage
    required_capabilities: set[str] = Field(default_factory=set)
    quality_floor: float = Field(default=.80, ge=0., le=1.)
    max_cost_usd_per_finished_minute: float | None = Field(default=None, ge=0.)
    max_elapsed_minutes_per_finished_minute: float | None = Field(default=None, gt=0.)
    max_vram_gb: float | None = Field(default=12., ge=0.)
    local_only: bool = True
    allow_paid_api: bool = False
    rights_cleared_for_input_assets: bool = False
    child_safety_review_approved: bool = False
    is_made_for_kids: bool = False
    # Client must request PRODUCTION if they intend to auto-execute.
    intent: Literal["RESEARCH","PRODUCTION"] = "RESEARCH"


class MethodReview(BaseModel):
    method_id: str
    tool_id: str
    preview_candidate: bool
    production_eligible: bool
    score: float | None = None
    blockers: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)


class SelectionDecision(BaseModel):
    status: Literal["PRODUCTION_METHOD_SELECTED","RESEARCH_ONLY","BLOCKED_NO_CANDIDATES"]
    project_id: str
    niche_id: str
    shot_id: str
    stage: Stage
    production_method_id: str | None = None
    suggested_trial_method_id: str | None = None
    qualified_fallback_method_id: str | None = None
    quality_leader_method_id: str | None = None
    lowest_cost_valid_method_id: str | None = None
    fastest_valid_method_id: str | None = None
    pareto_frontier_method_ids: list[str] = Field(default_factory=list)
    reviews: list[MethodReview] = Field(default_factory=list)
    # Advisory cannot approve an external operation even if method is eligible.
    # Existing ProductionMethodSwitch + final policy gate must authorize it.
    execution_authorized: bool = False
    requires_separate_final_release_gate: bool = True
    cannot_guarantee_best: bool = True
    recommendations: list[str] = Field(default_factory=list)


class ProductionSelectionCouncil:
    """Quality must meet a floor before cost/speed optimization can occur.

    Production selection only for methods proven on the SAME requested scope.
    Preview candidates may be presented for R&D but are never runnable via
    this service; the caller must separately use existing lab/adapters.
    """
    def __init__(self,methods: list[ToolEvidence] | None = None):
        self.methods=list(methods or [])
        ids=[x.method_id for x in self.methods]
        if len(ids)!=len(set(ids)):
            raise ValueError("DUPLICATE_METHOD_IDS")

    def advise(self,req:ShotToolRequest)->SelectionDecision:
        assessments=[]
        candidates=[]
        for candidate in self.methods:
            if candidate.stage!=req.stage:
                continue
            if "*" not in candidate.supported_niches and req.niche_id not in candidate.supported_niches:
                continue
            errors=[]
            missing=[]
            if not req.required_capabilities.issubset(candidate.capability_tags):
                errors.append("REQUIRED_SHOT_CAPABILITIES_UNSUPPORTED")
            if req.local_only and not candidate.is_local:
                errors.append("NONLOCAL_TOOL_FORBIDDEN")
            if not req.allow_paid_api and candidate.paid_api_required:
                errors.append("PAID_API_NOT_AUTHORIZED")
            if not candidate.license_approved:
                errors.append("LICENSE_NOT_CLEARED")
            if not req.rights_cleared_for_input_assets:
                errors.append("INPUT_ASSET_RIGHTS_NOT_CLEARED")
            if req.is_made_for_kids and not req.child_safety_review_approved:
                errors.append("CHILD_SAFETY_EDITORIAL_REVIEW_MISSING")
            if candidate.state!=ToolState.QUALIFIED_FOR_SCOPE or not candidate.scope_verified:
                errors.append("NOT_QUALIFIED_FOR_THIS_PRODUCTION_SCOPE")
            if not candidate.executable_evidence:
                errors.append("EXECUTABLE_EVIDENCE_MISSING")
            if not candidate.benchmark_evidence:
                errors.append("SCOPED_BENCHMARK_MISSING")
            quality=candidate.actual_measured_quality
            cost=candidate.actual_cost_usd_per_finished_minute
            speed=candidate.actual_elapsed_minutes_per_finished_minute
            if quality is None:
                missing.append("QUALITY_NOT_MEASURED")
            elif quality<req.quality_floor:
                errors.append("MEASURED_QUALITY_BELOW_FLOOR")
            if cost is None:
                missing.append("COST_PER_FINISHED_MINUTE_NOT_MEASURED")
            elif req.max_cost_usd_per_finished_minute is not None and cost>req.max_cost_usd_per_finished_minute:
                errors.append("MEASURED_COST_EXCEEDS_BUDGET")
            if speed is None:
                missing.append("ELAPSED_TIME_PER_FINISHED_MINUTE_NOT_MEASURED")
            elif req.max_elapsed_minutes_per_finished_minute is not None and speed>req.max_elapsed_minutes_per_finished_minute:
                errors.append("ELAPSED_TIME_EXCEEDS_BUDGET")
            if req.max_vram_gb is not None and candidate.actual_peak_vram_gb is not None and candidate.actual_peak_vram_gb>req.max_vram_gb:
                errors.append("MEASURED_VRAM_EXCEEDS_HARDWARE")
            elif req.max_vram_gb is not None and candidate.actual_peak_vram_gb is None and req.stage in {Stage.ANIMATION,Stage.AI_VIDEO,Stage.GAME_RUNTIME}:
                missing.append("PEAK_VRAM_NOT_MEASURED")
            ready=not errors and not missing
            preview=(
                "REQUIRED_SHOT_CAPABILITIES_UNSUPPORTED" not in errors
                and "NONLOCAL_TOOL_FORBIDDEN" not in errors
                and "PAID_API_NOT_AUTHORIZED" not in errors
                and candidate.state in {ToolState.PRESENT,ToolState.EXECUTABLE,ToolState.BENCHMARKED,ToolState.QUALIFIED_FOR_SCOPE}
            )
            # Score only genuinely comparable, benchmarked tools. Never
            # invent quality or cost estimates to produce a ranking.
            score=None
            if ready:
                assert quality is not None and cost is not None and speed is not None
                # Quality dominates. Cost and speed tie-break within floor.
                score=round(.65*quality + .25/(1.+cost)+.10/(1.+speed),6)
            record=MethodReview(method_id=candidate.method_id,tool_id=candidate.tool_id,
                preview_candidate=preview,production_eligible=ready,score=score,
                blockers=sorted(set(errors)),missing_evidence=sorted(set(missing)))
            assessments.append(record)
            if ready:candidates.append(record)
        assessments.sort(key=lambda a:a.method_id)
        candidates.sort(key=lambda a:(-(a.score or 0.),a.method_id))
        # Preview candidates are observational suggestions only, prioritizing
        # runnable local tools over folders over unverified discoveries.
        preview=sorted(
            (r for r in assessments if r.preview_candidate),
            key=lambda r:(
                -(list(ToolState).index(next(x.state for x in self.methods if x.method_id==r.method_id))),
                r.method_id,
            ),
        )
        primary=candidates[0].method_id if candidates else None
        fallback=candidates[1].method_id if len(candidates)>1 else None
        by_id={m.method_id:m for m in self.methods}
        qualified=[by_id[r.method_id] for r in candidates]
        quality_leader=max(qualified,key=lambda x:(x.actual_measured_quality,-x.actual_cost_usd_per_finished_minute,x.method_id)).method_id if qualified else None
        cheapest=min(qualified,key=lambda x:(x.actual_cost_usd_per_finished_minute,-x.actual_measured_quality,x.method_id)).method_id if qualified else None
        fastest=min(qualified,key=lambda x:(x.actual_elapsed_minutes_per_finished_minute,-x.actual_measured_quality,x.method_id)).method_id if qualified else None
        frontier=[]
        for x in qualified:
            dominated=False
            for y in qualified:
                if x.method_id==y.method_id:continue
                no_worse=(y.actual_measured_quality>=x.actual_measured_quality
                          and y.actual_cost_usd_per_finished_minute<=x.actual_cost_usd_per_finished_minute
                          and y.actual_elapsed_minutes_per_finished_minute<=x.actual_elapsed_minutes_per_finished_minute)
                strictly_better=(y.actual_measured_quality>x.actual_measured_quality
                          or y.actual_cost_usd_per_finished_minute<x.actual_cost_usd_per_finished_minute
                          or y.actual_elapsed_minutes_per_finished_minute<x.actual_elapsed_minutes_per_finished_minute)
                if no_worse and strictly_better:
                    dominated=True
                    break
            if not dominated:frontier.append(x.method_id)
        research=preview[0].method_id if preview else None
        if primary and req.intent=="PRODUCTION":
            status="PRODUCTION_METHOD_SELECTED"
        else:
            status="RESEARCH_ONLY" if assessments else "BLOCKED_NO_CANDIDATES"
        rec=[]
        if status!="PRODUCTION_METHOD_SELECTED":
            rec.append("NO_AUTOMATIC_PRODUCTION_EXECUTION: acquire scoped executable, license, rights, quality, elapsed time, cost and hardware evidence")
        if not assessments:
            rec.append("CAPABILITY_ACQUISITION_REQUIRED: no tool supports the requested niche/stage")
        return SelectionDecision(
            status=status,project_id=req.project_id,niche_id=req.niche_id,
            shot_id=req.shot_id,stage=req.stage,
            production_method_id=primary if status=="PRODUCTION_METHOD_SELECTED" else None,
            suggested_trial_method_id=research,
            qualified_fallback_method_id=fallback if status=="PRODUCTION_METHOD_SELECTED" else None,
            quality_leader_method_id=quality_leader,
            lowest_cost_valid_method_id=cheapest,
            fastest_valid_method_id=fastest,
            pareto_frontier_method_ids=frontier,
            reviews=assessments,execution_authorized=False,
            recommendations=rec,
        )
