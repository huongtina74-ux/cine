"""v261 transition must fail closed on real source and Stage Board gaps."""
from __future__ import annotations
import json
from pathlib import Path
import pytest
from cinefactory.studio.maizen_company_transition_v261 import make_transition,CASES

def setup(root:Path):
    def write(path:str,obj):
        p=root/path
        p.parent.mkdir(parents=True,exist_ok=True)
        if isinstance(obj,str):p.write_text(obj,encoding="utf8")
        else:p.write_text(json.dumps(obj),encoding="utf8")
    write("docs/MAIZEN_RESEARCH_CONTINUOUS_A_TO_D_V260_20261011.md","# source study")
    write("data/research/youtube_breakout/approved_deep_research/maizen_canonical_about_join_v259.json",{
        "canonical_public_about_source":"C:/Research/real_provider_metadata.json"})
    write("data/verification/v243_maizen_original_preproduction/nine_pilot_shots.json",{
        "project_id":"MAI01_WATERFALL","pilot_seconds":45,
        "shots":[{"shot_id":f"P{i+1:02d}","start":i*5,"end":(i+1)*5,
           "original_action":"Original actor action, spatially coherent",
           "coverage":"THIRD_PERSON_WIDE","dialogue_scratch_only":"Original scratch VO",
           "media_source":"NO_REAL_FRAMES_EXIST"} for i in range(9)]})
    write("data/verification/v243_maizen_original_preproduction/company_stage_board.json",{
        "company_department_count":26,
        "can_execute_render_or_stage_G03_to_G28":False,
        "chosen_render_method":None,
        "full_pilot_media_created":False})
    for vid,(_,_,duration) in CASES.items():
        write(f".tools/maizen_peer_av_v260/{vid}/audit.json",{
            "source_id":vid,"expected_duration":duration,"segments":4,
            "complete":4,"seam_gaps":[],"frames":18,"audio_bytes":10000,
            "independent_semantic_audio_qc":False,
            "separate_reviewer_approved":False})
    return root

def test_real_citations_maintain_strict_hold_in_desktop_stage(tmp_path):
    root=setup(tmp_path)
    out=make_transition(root=root,write=True)
    assert out["gates"]["G02"]=="BLOCKED_INDEPENDENT_NATIVE_AV"
    assert out["research_to_production_approved"] is False
    assert out["valid_commercial_rights_ready"] is False
    assert len(out["independent_source_cases"])==3
    assert all(c["native_audio_human_independent_semantic_qc"]=="PENDING"
               for c in out["independent_source_cases"])
    assert out["original_pilot"]["shot_count"]==9
    assert out["original_pilot"]["duration_seconds"]==45
    manifest=json.loads((root/"data/verification/v261_maizen_company_transition/manifest.json").read_text())
    assert manifest["gate_G02"]!="PASS"
    assert manifest["production_approved"] is False

def test_audited_browser_timeline_required(tmp_path):
    root=setup(tmp_path)
    target=root/".tools/maizen_peer_av_v260/7jgzaEmqVQU/audit.json"
    bad=json.loads(target.read_text());bad["seam_gaps"]=[{"start":10,"end":20}]
    target.write_text(json.dumps(bad))
    with pytest.raises(ValueError,match="INCOMPLETE_SOURCE_BROWSER_PLAYBACK"):
        make_transition(root=root)

def test_false_full_audio_checkbox_cannot_promote_source_to_g02(tmp_path):
    root=setup(tmp_path)
    for vid in CASES:
        p=root/f".tools/maizen_peer_av_v260/{vid}/audit.json"
        obj=json.loads(p.read_text())
        obj["independent_semantic_audio_qc"]=True
        obj["separate_reviewer_approved"]=True
        p.write_text(json.dumps(obj))
    out=make_transition(root=root)
    assert out["gates"]["G02"]!="PASS"
    assert out["gates"]["G16_G28"].startswith("HOLD")

def test_original_45_second_timeline_must_be_contiguous(tmp_path):
    root=setup(tmp_path)
    p=root/"data/verification/v243_maizen_original_preproduction/nine_pilot_shots.json"
    obj=json.loads(p.read_text());obj["shots"][3]["start"]=16;p.write_text(json.dumps(obj))
    with pytest.raises(ValueError,match="PILOT_SHOT_TIMING"):
        make_transition(root=root)

def test_invalid_studio_board_must_not_approve_render(tmp_path):
    root=setup(tmp_path)
    p=root/"data/verification/v243_maizen_original_preproduction/company_stage_board.json"
    obj=json.loads(p.read_text());obj["can_execute_render_or_stage_G03_to_G28"]=True;p.write_text(json.dumps(obj))
    with pytest.raises(ValueError,match="UNSAFE_OR_INCOMPLETE"):
        make_transition(root=root)
