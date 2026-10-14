from __future__ import annotations
"""Safety and best-evidenced option selection, not fake automatic readiness."""
import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from cinefactory.studio.production_selection_council import (
    ToolEvidence,ToolState,Stage,ShotToolRequest,ProductionSelectionCouncil)
from cinefactory.studio.production_tool_catalog_v191 import (
    NICHE_BLUEPRINTS,host_inventory,candidate_catalog,
    niche_recommendations)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"verification"/"v191_production_council"

def method(name="good",quality=.93,cost=.1,vram=8.,approved=True,paid=False,**kw):
    return ToolEvidence(method_id=name,tool_id=name,stage=Stage.ANIMATION,
        supported_niches={"minecraft"},capability_tags={"voxel_rig"},
        state=ToolState.QUALIFIED_FOR_SCOPE,
        executable_evidence="fixture:binary",benchmark_evidence="fixture:real_benchmark",
        scope_verified=True,license_approved=approved,
        license_source_url="https://godotengine.org/license/" if approved else None,
        actual_measured_quality=quality,
        actual_cost_usd_per_finished_minute=cost,
        actual_elapsed_minutes_per_finished_minute=1.,
        actual_peak_vram_gb=vram,paid_api_required=paid,**kw)

def request(**kw):
    params=dict(project_id="quality",niche_id="minecraft",shot_id="01",
        stage=Stage.ANIMATION,required_capabilities={"voxel_rig"},
        rights_cleared_for_input_assets=True,intent="PRODUCTION",
        quality_floor=.80,max_vram_gb=12.,
        max_cost_usd_per_finished_minute=1.)
    params.update(kw)
    return ShotToolRequest(**params)

def test_13_niches_including_preschool_and_original_asrm():
    assert len(NICHE_BLUEPRINTS)>=13
    assert {"minecraft","preschool_3d_musical","long_slices_game",
            "audio_storytelling_seniors","rain_sleep_white_noise",
            "asmr_sleep_hands_objects","roblox_animation","daily_english"}<=set(NICHE_BLUEPRINTS)

def test_preschool_domain_requires_distinct_music_rig_and_safety():
    n=NICHE_BLUEPRINTS["preschool_3d_musical"]
    tags=set.union(*(s.must_have for s in n.stage_sequence))
    assert n.children_audience
    assert {"original_song","beat_timeline","organic_face_rig",
            "lip_viseme_singing","education_accuracy","child_safety_review","music_rights"}<=tags

def test_real_inventory_distinguishes_present_from_working():
    h=host_inventory(ROOT)
    assert h["blender_version_probe"]
    assert h["ffmpeg_version_probe"]
    assert h["comfyui_folder_exists"]
    assert not h["comfyui_video_workflow_executable_verified"]
    assert h["path_executables"]["godot"] is None

def test_catalog_observation_not_niche_quality():
    items=candidate_catalog(ROOT)
    b=next(t for t in items if t.method_id=="blender.voxel.render")
    c=next(t for t in items if t.method_id=="comfy.video.workflow")
    assert b.state==ToolState.EXECUTABLE and b.benchmark_evidence is None
    assert c.state==ToolState.PRESENT and c.benchmark_evidence is None
    assert not c.scope_verified and not c.license_approved

def test_cannot_invent_quality_metrics_without_benchmark():
    with pytest.raises(ValidationError,match="MEASURED_METRICS_REQUIRE_BENCHMARK_EVIDENCE"):
        ToolEvidence(method_id="fake",tool_id="x",stage=Stage.ANIMATION,
            actual_measured_quality=.99)

def test_cannot_claim_executable_without_evidence():
    with pytest.raises(ValidationError,match="EXE_STATE_REQUIRES_EXECUTABLE_EVIDENCE"):
        ToolEvidence(method_id="fake",tool_id="x",stage=Stage.EDITORIAL,
            state=ToolState.EXECUTABLE)

def test_cannot_claim_qualified_without_scope_check():
    with pytest.raises(ValidationError,match="QUALIFIED_STATE_REQUIRES_SCOPE_VERIFICATION"):
        ToolEvidence(method_id="fake",tool_id="x",stage=Stage.EDITORIAL,
            state=ToolState.QUALIFIED_FOR_SCOPE,
            executable_evidence="x",benchmark_evidence="b")

def test_duplicate_method_fails():
    with pytest.raises(ValueError,match="DUPLICATE_METHOD_IDS"):
        ProductionSelectionCouncil([method(),method()])

def test_bad_quality_cheapest_is_rejected():
    r=ProductionSelectionCouncil([method("bad",quality=.5,cost=0.),
      method("good",quality=.95,cost=.2)]).advise(request(quality_floor=.9))
    assert r.production_method_id=="good"
    assert "MEASURED_QUALITY_BELOW_FLOOR" in r.reviews[0].blockers
    assert not r.execution_authorized

def test_over_budget_is_rejected():
    r=ProductionSelectionCouncil([method("expensive",cost=20.)]).advise(request())
    assert r.production_method_id is None
    assert "MEASURED_COST_EXCEEDS_BUDGET" in r.reviews[0].blockers

def test_unlicensed_model_does_not_win():
    r=ProductionSelectionCouncil([method("licensed",quality=.86),
      method("unlicensed",quality=1.,cost=0.,approved=False)]).advise(request())
    assert r.production_method_id=="licensed"
    assert "LICENSE_NOT_CLEARED" in next(x for x in r.reviews if x.method_id=="unlicensed").blockers

def test_paid_api_rejected_without_approval():
    r=ProductionSelectionCouncil([method(paid=True)]).advise(request())
    assert r.production_method_id is None
    assert "PAID_API_NOT_AUTHORIZED" in r.reviews[0].blockers

def test_vram_limit_enforced():
    r=ProductionSelectionCouncil([method(vram=24.)]).advise(request())
    assert "MEASURED_VRAM_EXCEEDS_HARDWARE" in r.reviews[0].blockers

def test_rights_rejection_even_for_high_quality():
    r=ProductionSelectionCouncil([method()]).advise(
        request(rights_cleared_for_input_assets=False))
    assert "INPUT_ASSET_RIGHTS_NOT_CLEARED" in r.reviews[0].blockers

def test_preschool_kids_editorial_veto():
    r=ProductionSelectionCouncil([method()]).advise(
        request(is_made_for_kids=True,child_safety_review_approved=False))
    assert "CHILD_SAFETY_EDITORIAL_REVIEW_MISSING" in r.reviews[0].blockers

def test_unknown_capability_requires_acquisition():
    r=ProductionSelectionCouncil([method()]).advise(
        request(stage=Stage.MUSIC))
    assert r.status=="BLOCKED_NO_CANDIDATES"
    assert any("ACQUISITION" in s for s in r.recommendations)

def test_no_measured_cost_cannot_be_certified():
    m=method().model_copy(update={"actual_cost_usd_per_finished_minute":None})
    r=ProductionSelectionCouncil([m]).advise(request())
    assert not r.reviews[0].production_eligible
    assert "COST_PER_FINISHED_MINUTE_NOT_MEASURED" in r.reviews[0].missing_evidence

def test_even_qualified_best_method_never_triggers_auto_execution():
    r=ProductionSelectionCouncil([method()]).advise(request())
    assert r.status=="PRODUCTION_METHOD_SELECTED"
    assert r.production_method_id=="good"
    assert r.requires_separate_final_release_gate
    assert not r.execution_authorized

def test_research_request_cannot_execute():
    r=ProductionSelectionCouncil([method()]).advise(request(intent="RESEARCH"))
    assert r.status=="RESEARCH_ONLY"
    assert r.production_method_id is None

def test_unknown_niche_is_blocked():
    r=niche_recommendations(ROOT,"unknown_2030_genre")
    assert r["status"]=="BLOCKED_UNKNOWN_NICHE"
    assert not r["production_authorized"]

def test_preschool_plan_requires_unbuilt_music():
    r=niche_recommendations(ROOT,"preschool_3d_musical")
    assert len(r["stage_decisions"])==7
    assert r["unverified_stage_count"]==7
    assert not r["production_authorized"]
    song=next(x for x in r["stage_decisions"] if x["stage"]=="MUSIC")
    assert song["selection"]["production_method_id"] is None

def test_portfolio_advisor_wired_to_existing_company():
    from cinefactory.appctx import build_context
    app=build_context(ROOT)
    assert app.production_portfolio_advisor is app.studio.professional_company.production_portfolio_advisor

def test_machine_readable_7_real_niche_research_reports():
    x=json.loads((OUT/"tool_inventory_v191.json").read_text(encoding="utf-8"))
    assert len(x["tool_candidates"])>=15
    assert not x["production_release_scope_verified"]
    summary=json.loads((OUT/"niche_summary_v191.json").read_text(encoding="utf-8"))
    assert len(summary)==7
    assert all(not v["production_authorized"] for v in summary.values())
    assert all(v["unqualified_stages"]==v["stages"] for v in summary.values())


def test_measured_pareto_reports_quality_cost_speed_tradeoffs():
    top=method("highest_quality",quality=.98,cost=.5)
    cheap=method("lowest_cost",quality=.84,cost=.01)
    dominated=method("dominated",quality=.82,cost=.6)
    r=ProductionSelectionCouncil([top,cheap,dominated]).advise(request())
    assert r.quality_leader_method_id=="highest_quality"
    assert r.lowest_cost_valid_method_id=="lowest_cost"
    assert set(r.pareto_frontier_method_ids)=={"highest_quality","lowest_cost"}
    assert "dominated" not in r.pareto_frontier_method_ids
    assert not r.execution_authorized
