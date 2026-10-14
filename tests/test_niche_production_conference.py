from __future__ import annotations
import hashlib
import json
import subprocess
from pathlib import Path
import pytest

from cinefactory.production.niche_production_conference import (
    prepare_niche_conference,evaluate_comparable_pilots,TOOL_CATALOG,
)

VIDS=("W7R8k10Kjfk","qtWfSIqNfdU","7wQK-YJOu4o")
CID="UC"+"b"*22

def hash_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(p,record):
    p.write_text(json.dumps(record,indent=2),encoding="utf-8")

@pytest.fixture
def evidence(tmp_path,monkeypatch):
    search,plan,catalog=[tmp_path/(s+".json") for s in ("search","plan","catalog")]
    for p in (search,plan,catalog):save(p,{"fixture_file":p.stem})
    video=[
        {"video_id":x,"video_url":"https://www.youtube.com/watch?v="+x,
         "title":"Minecraft animation original chapter", "video_age_days_proxy":3,
         "approx_views":1300000,"duration_seconds":600,
         "topic_title_alignment":"ALL_NICHE_TITLE_TOKENS_PRESENT"}
        for x in VIDS]
    packet={
        "schema":"cine.research.automated_evidence.v1",
        "state":"PUBLIC_EVIDENCE_READY_FOR_REVIEW",
        "niche":"Minecraft animation",
        "source_files":{key:{"path":str(p),"sha256":hash_file(p)}
                        for key,p in zip(("search","plan","catalog"),(search,plan,catalog))},
        "channels":[{"channel_id":CID,"channel_name":"MSToons",
                     "sample_longform_videos":video}]
    }
    e=tmp_path/"evidence.json"
    save(e,packet)
    deep=tmp_path/"deep.json"
    save(deep,{"schema":"cine.research.deep_video_review.v1",
        "niche":"Minecraft animation",
        "source_evidence":{"path":str(e),"sha256":hash_file(e)},
        "videos":[{"video_id":VIDS[0],"thumbnail_status":"THUMBNAIL_UNAVAILABLE",
                   "title":video[0]["title"],"channel_id":CID,
                   "thumbnail_path":None,"story_hook_status":"UNKNOWN",
                   "actual_video_frames_status":"NOT_OBSERVED",
                   "analysis_status":"PENDING_MULTIMODAL_REVIEW",
                   "video_url":video[0]["video_url"]}],
        "selected_count":1,"production_permission":False,"council_decided":False,
        "no_automatic_semantic_claims":True})
    # Unit test only: rest of deep_review integrity is covered by other suite.
    monkeypatch.setattr("cinefactory.research_intelligence.deep_video_intelligence.verify_deep_video_review",
                        lambda p:{"state":"UNIT_FIXTURE_INTEGRITY_OK"})
    return e,deep

def prepare(evidence,tmp_path):
    e,deep=evidence
    return prepare_niche_conference(e,deep,tmp_path/"work",approved_niche="Minecraft animation",
               owner_approval_ref="TEST_ONLY_NO_REAL_OWNER_APPROVAL")

def test_research_conference_cannot_invent_video_story_or_tool_quality(evidence,tmp_path):
    report=prepare(evidence,tmp_path)
    assert report["state"]=="FULL_VIDEO_STUDIES_REQUIRED"
    assert report["video_case_count"]==3
    assert len(report["tool_candidates"])>=7
    assert report["deep_content_analysis_completed"] is False
    assert not report["production_permission"]
    for video in report["video_cases"]:
        assert video["camera_lenses"]=="UNKNOWN"
        assert video["shot_timing"]=="UNKNOWN"
        assert video["full_video_inspection"]=="NOT_DONE"
        assert len(video["timeline_worklist"])==3
    assert len(report["scene_trial_matrix"])==3
    assert not report["tool_benchmark_completed"]

def test_source_tamper_detected(evidence,tmp_path):
    e,deep=evidence
    video=json.loads(e.read_text(encoding="utf-8"))
    video["source_files"]["catalog"]["sha256"]="bad"
    save(e,video)
    new=json.loads(deep.read_text(encoding="utf-8"))
    new["source_evidence"]["sha256"]=hash_file(e)
    save(deep,new)
    with pytest.raises(ValueError,match="mutated"):
        prepare(evidence,tmp_path)

def test_no_niche_alias_mix_or_missing_approval_reference(evidence,tmp_path):
    e,deep=evidence
    with pytest.raises(ValueError,match="mismatch"):
        prepare_niche_conference(e,deep,tmp_path/"wrong",approved_niche="Roblox animation",
                                  owner_approval_ref="TEST_ONLY_NOT_APPROVED")
    with pytest.raises(ValueError,match="approval"):
        prepare_niche_conference(e,deep,tmp_path/"missing",approved_niche="Minecraft animation",
                                  owner_approval_ref="")

def test_comparable_trial_no_actual_render_is_blocked(evidence,tmp_path):
    prepare(evidence,tmp_path)
    path=tmp_path/"work"/"conference.json"
    trials=tmp_path/"trial.json"
    save(trials,{"schema":"cine.studio.pilot_trials.v1",
                 "conference_sha256":hash_file(path),
                 "trials":[{"scenario":"hero_expression_dialogue",
                            "lane":"blender_character_animation",
                            "measured":{"quality_scores":{"identity_continuity":0.99,
                                                          "acting_expression":0.99}}}]})
    out=evaluate_comparable_pilots(path,trials,tmp_path/"evaluation.json")
    assert out["state"]=="NO_VERIFIED_ACCEPTABLE_PILOTS"
    assert not out["benchmarks"][0]["hard_gate_quality_pass"]
    assert not out["production_permission"]

def test_pilot_has_objective_bytes_but_not_invented_qa(evidence,tmp_path):
    prepare(evidence,tmp_path)
    path=tmp_path/"work"/"conference.json"
    fake_mp4=tmp_path/"pilot.mp4"
    fake_mp4.write_bytes(b"synthetic-smoke-only-no-visual-review")
    data={"schema":"cine.studio.pilot_trials.v1","conference_sha256":hash_file(path),
          "trials":[{"scenario":"hero_expression_dialogue",
                     "lane":"blender_character_animation",
                     "render_file":str(fake_mp4),"render_sha256":hash_file(fake_mp4),
                     "measured":{"output_duration_seconds":5,
                         "render_wall_seconds":15,"human_rework_seconds":2,
                         "quality_scores":{g:0.97 for g in ("identity_continuity","acting_expression","camera","sound")},
                         "independent_quality_reviewed":False,"rights_cleared":False}}]}
    trials=tmp_path/"trial.json";save(trials,data)
    out=evaluate_comparable_pilots(path,trials,tmp_path/"eval.json")
    assert out["state"]=="NO_VERIFIED_ACCEPTABLE_PILOTS"
    assert out["benchmarks"][0]["source_media_verified"]
    assert out["benchmarks"][0]["status"]=="PILOT_INCOMPLETE_OR_HARD_GATE_FAILED"

def test_high_quality_with_timings_remains_advisory_without_authenticated_proof(evidence,tmp_path):
    prepare(evidence,tmp_path)
    path=tmp_path/"work"/"conference.json"
    render=tmp_path/"pilot.mp4"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
                    "-f","lavfi","-i","testsrc2=size=1280x720:duration=2:rate=12",
                    "-c:v","mpeg4","-q:v","12",str(render)],check=True,timeout=30)
    trials=tmp_path/"trial.json"
    save(trials,{"schema":"cine.studio.pilot_trials.v1","conference_sha256":hash_file(path),
        "trials":[{"scenario":"hero_expression_dialogue",
                  "lane":"blender_character_animation",
                  "render_file":str(render),"render_sha256":hash_file(render),
                  "measured":{"output_duration_seconds":2,
                      "render_wall_seconds":30,"human_rework_seconds":10,
                      "quality_scores":{g:0.95 for g in ("identity_continuity","acting_expression","camera","sound")},
                      "independent_quality_reviewed":True,"rights_cleared":True}}]})
    result=evaluate_comparable_pilots(path,trials,tmp_path/"eval.json")
    assert result["state"]=="PILOT_COMPARISON_ADVISORY"
    assert result["advisory_rankings"]["hero_expression_dialogue"]["needs_owner_review"]
    assert result["benchmarks"][0]["accepted_output_seconds_per_hour_proxy"]==180
    assert result["benchmarks"][0]["video_stream_verified"] is True
    assert result["human_review_authenticated"] is False
    assert result["cannot_claim_competitor_superiority"]

def test_duplicate_output_immutable(evidence,tmp_path):
    prepare(evidence,tmp_path)
    with pytest.raises(FileExistsError):
        prepare(evidence,tmp_path)

def test_registry_lists_real_tool_types_without_pretending_executables(evidence,tmp_path):
    packet=prepare(evidence,tmp_path)
    indexed={x["lane"]:x for x in packet["tool_candidates"]}
    assert "comfyui_controlled_ai_video" in indexed
    assert "resolve_master_finishing" in indexed
    assert "LTX-2.5" in indexed["comfyui_controlled_ai_video"]["tools"]
    assert indexed["resolve_master_finishing"]["state"]=="CANDIDATE_REQUIRES_RUNTIME_AND_PILOT_BENCHMARK"
    assert all(x["state"].startswith("CANDIDATE") for x in packet["tool_candidates"])


def test_locked_conference_feeds_existing_studio_director_without_passing_qa(evidence,tmp_path):
    from runpy import run_path
    from cinefactory.production.niche_production_conference import compile_conf_to_director
    prepare(evidence,tmp_path)
    conference=tmp_path/"work"/"conference.json"
    brief=run_path(str(Path(__file__).with_name("test_studio_director.py")))["brief"]()
    brief["competitor_research_revision"]=hash_file(conference)
    brief_path=tmp_path/"director_brief.json"
    save(brief_path,brief)
    cap=tmp_path/"caps.json"
    save(cap,{"schema":"cine.studio.capability_registry.v1","lanes":{}})
    result=compile_conf_to_director(conference,brief_path,cap,tmp_path/"director_plan.json")
    assert result["state"]=="DIRECTOR_PLAN_AND_CONFERENCE_LINKED_REVIEW_PENDING"
    assert result["shot_routes"][0]["planned_lane"]=="blender_character_animation"
    assert result["shot_routes"][0]["scenario"]=="hero_expression_dialogue"
    assert not result["production_permission"]
    assert (tmp_path/"director_plan_research_link.json").is_file()


def test_wrong_conference_revision_cannot_drive_director(evidence,tmp_path):
    from runpy import run_path
    from cinefactory.production.niche_production_conference import compile_conf_to_director
    prepare(evidence,tmp_path)
    conference=tmp_path/"work"/"conference.json"
    brief=run_path(str(Path(__file__).with_name("test_studio_director.py")))["brief"]()
    brief["competitor_research_revision"]="unrelated_old_revision"
    bp=tmp_path/"brief.json"
    save(bp,brief)
    caps=tmp_path/"caps.json"
    save(caps,{"schema":"cine.studio.capability_registry.v1","lanes":{}})
    with pytest.raises(ValueError,match="immutable conference"):
        compile_conf_to_director(conference,bp,caps,tmp_path/"not_created.json")
    assert not (tmp_path/"not_created.json").exists()
