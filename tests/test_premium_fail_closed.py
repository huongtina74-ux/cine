"""Regressions: diagnostic source ≠ quality-certified cinema."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from cinefactory.autopilot.contracts import AutopilotRequest
from cinefactory.production.asset_factory import AssetFactory
from cinefactory.production.storyboard import StoryboardGate
from cinefactory.production.video_factory import VideoFactory
from cinefactory.production.premium_gate import premium_preflight,premium_shot_gate

def _req(**values):
    return AutopilotRequest(prompt="Test original cinematic script",**values)

def test_slate_is_diagnostic_and_does_not_require_paid_model():
    r=_req(production_mode="slate",quality_tier="diagnostic")
    assert premium_preflight(r) is None

def test_premium_slate_refused_before_render():
    with pytest.raises(PermissionError,match="PREMIUM_CANNOT_USE_SLATE"):
        premium_preflight(_req(production_mode="slate",quality_tier="premium"))

def test_comfy_cannot_bypass_visual_qc_even_when_flag_false():
    with pytest.raises(PermissionError,match="GENERATIVE_VISUAL_QC_REQUIRED"):
        premium_preflight(_req(production_mode="comfyui",quality_tier="diagnostic",require_visual_qc=False))

def test_premium_requires_director_and_multimodal_conference():
    with pytest.raises(PermissionError,match="PREMIUM_NEEDS_DIRECTOR_AND_CONFERENCE"):
        premium_preflight(_req(production_mode="comfyui",quality_tier="premium",
                               visual_qc_command="python reviewer.py",reasoning_mode="file"))

def test_no_qc_means_no_perfect_asset_score():
    gate=AssetFactory(SimpleNamespace(),visual_qc=None)
    assert gate._score_visual(Path("not_a_file.png"),{})==(False,0.0,["VISUAL_QC_MISSING_FAIL_CLOSED"])
    with pytest.raises(RuntimeError,match="VISUAL_QC_MISSING_FAIL_CLOSED"):
        gate.build("p",SimpleNamespace(),Path("."),mode="comfyui")

def test_no_qc_means_no_perfect_storyboard_score():
    gate=StoryboardGate(SimpleNamespace(),visual_qc=None)
    assert gate._review(Path("missing.png"),SimpleNamespace())==(False,0.0,["VISUAL_QC_MISSING_FAIL_CLOSED"])

def test_no_qc_means_no_perfect_video_score():
    ctx=SimpleNamespace(workflows=None,repair_memory=None,turbo_store=None)
    gate=VideoFactory(ctx)
    passed,scores,findings=gate._visual_review(Path("nothing.mp4"),SimpleNamespace())
    assert passed is False
    assert max(scores.values())==0
    assert findings==["VISUAL_QC_MISSING_FAIL_CLOSED"]

def test_unreviewed_slate_remains_explicitly_diagnostic():
    a=AssetFactory(SimpleNamespace(),diagnostic_slate=True)
    assert a._score_visual(Path("fake.png"),{})[2]==["DIAGNOSTIC_SLATE_NOT_VISUALLY_REVIEWED"]
    s=StoryboardGate(SimpleNamespace(),diagnostic_slate=True)
    assert s._review(Path("fake.png"),SimpleNamespace())[2]==["DIAGNOSTIC_SLATE_NOT_VISUALLY_REVIEWED"]

def _frozen(path,obj):
    path.write_text(json.dumps(obj),encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()

def test_fake_premium_research_flags_block(tmp_path):
    conference=tmp_path/"conference.json"
    plan=tmp_path/"plan.json"
    cs=_frozen(conference,{"schema":"cine.studio.production_conference.v1",
                          "approved_niche":"Minecraft animation",
                          "deep_content_analysis_completed":False,
                          "tool_benchmark_completed":False,"owner_approval_authenticated":False,
                          "source_rights_status":"UNVERIFIED"})
    ps=_frozen(plan,{"schema":"cine.studio.director_plan.v1",
                     "niche":"Minecraft animation","state":"READY_FOR_DEPARTMENT_REVIEW_NOT_PRODUCTION",
                     "creative_missing_count":0,"unbenchmarked_shot_count":0,
                     "shots":[]})
    _frozen(tmp_path/"plan_research_link.json",
           {"schema":"cine.studio.conference_director_link.v1",
            "conference_sha256":cs,"director_plan_sha256":ps})
    with pytest.raises(PermissionError,match="PREMIUM_RESEARCH_OR_RIGHTS_NOT_VERIFIED"):
        premium_preflight(_req(production_mode="comfyui",quality_tier="premium",
            reasoning_mode="file",visual_qc_command="python reviewer.py",
            studio_director_plan_file=str(plan),studio_conference_file=str(conference)))

def test_planned_blender_lane_is_not_silently_rendered_through_comfy():
    sources={"plan":{"shots":[{"shot_id":"S1","primary_lane":"blender_character_animation",
                                 "technical_route_state":"CAPABILITY_BENCHMARKED","missing":[],
                                 "duration_seconds":5}]},"plan_sha256":"a","conference_sha256":"b"}
    with pytest.raises(PermissionError,match="PREMIUM_RENDERER_NOT_CONNECTED_FOR_LANE"):
        premium_shot_gate(sources,[SimpleNamespace(shot_id="S1",duration_seconds=5)])

def test_premium_shot_id_drift_refused():
    sources={"plan":{"shots":[{"shot_id":"S1","primary_lane":"comfyui_controlled_ai_video",
                                 "technical_route_state":"CAPABILITY_BENCHMARKED","missing":[],
                                 "duration_seconds":5}]},"plan_sha256":"a","conference_sha256":"b"}
    with pytest.raises(PermissionError,match="PREMIUM_SHOT_MISMATCH"):
        premium_shot_gate(sources,[SimpleNamespace(shot_id="S2",duration_seconds=5)])


def _source_plan(shots):
    return {"plan":{"shots":shots},"plan_sha256":"a","conference_sha256":"b"}

def _source_shot(ident):
    return {"shot_id":ident,"primary_lane":"comfyui_controlled_ai_video",
            "technical_route_state":"CAPABILITY_BENCHMARKED",
            "missing":[],"duration_seconds":5}

def test_repeated_planned_shot_id_blocks_premium_render():
    src=_source_plan([_source_shot("S1"),_source_shot("S1")])
    with pytest.raises(PermissionError,match="PREMIUM_SHOT_MISMATCH"):
        premium_shot_gate(src,[SimpleNamespace(shot_id="S1",duration_seconds=5)])

def test_repeated_actual_shot_id_blocks_premium_render():
    src=_source_plan([_source_shot("S1"),_source_shot("S2")])
    with pytest.raises(PermissionError,match="PREMIUM_SHOT_MISMATCH"):
        premium_shot_gate(src,[SimpleNamespace(shot_id="S1",duration_seconds=5),
                               SimpleNamespace(shot_id="S1",duration_seconds=5)])

def test_string_true_flags_never_count_as_authenticated_research(tmp_path):
    conf=tmp_path/"conference.json"
    plan=tmp_path/"plan.json"
    cs=_frozen(conf,{"schema":"cine.studio.production_conference.v1",
                      "approved_niche":"Minecraft animation",
                      "deep_content_analysis_completed":"true",
                      "tool_benchmark_completed":True,"owner_approval_authenticated":True,
                      "source_rights_status":"CLEARED"})
    ps=_frozen(plan,{"schema":"cine.studio.director_plan.v1","niche":"Minecraft animation",
                     "state":"READY_FOR_DEPARTMENT_REVIEW_NOT_PRODUCTION",
                     "creative_missing_count":0,"unbenchmarked_shot_count":0,
                     "shots":[_source_shot("S1")]})
    _frozen(tmp_path/"plan_research_link.json",
            {"schema":"cine.studio.conference_director_link.v1",
             "conference_sha256":cs,"director_plan_sha256":ps})
    with pytest.raises(PermissionError,match="PREMIUM_RESEARCH_OR_RIGHTS_NOT_VERIFIED"):
        premium_preflight(_req(production_mode="comfyui",quality_tier="premium",
          visual_qc_command="python reviewer.py",reasoning_mode="file",
          studio_conference_file=str(conf),studio_director_plan_file=str(plan)))

def test_premium_missing_counters_cannot_be_treated_as_zero(tmp_path):
    conf=tmp_path/"conference.json"
    plan=tmp_path/"plan.json"
    cs=_frozen(conf,{"schema":"cine.studio.production_conference.v1",
                      "approved_niche":"Minecraft animation",
                      "deep_content_analysis_completed":True,
                      "tool_benchmark_completed":True,"owner_approval_authenticated":True,
                      "source_rights_status":"CLEARED"})
    ps=_frozen(plan,{"schema":"cine.studio.director_plan.v1","niche":"Minecraft animation",
                     "state":"READY_FOR_DEPARTMENT_REVIEW_NOT_PRODUCTION",
                     "shots":[_source_shot("S1")]})
    _frozen(tmp_path/"plan_research_link.json",
            {"schema":"cine.studio.conference_director_link.v1",
             "conference_sha256":cs,"director_plan_sha256":ps})
    with pytest.raises(PermissionError,match="PREMIUM_DIRECTOR_PLAN_UNREADY"):
        premium_preflight(_req(production_mode="comfyui",quality_tier="premium",
          visual_qc_command="python reviewer.py",reasoning_mode="file",
          studio_conference_file=str(conf),studio_director_plan_file=str(plan)))
