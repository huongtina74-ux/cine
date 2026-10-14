"""v243: full 26-department original CineFactory desk work, not a false gate pass."""
from hashlib import sha256
import json
import pytest
from typer.testing import CliRunner

from cinefactory.cli import app
from cinefactory.studio.contracts import DepartmentId
from cinefactory.studio.maizen_company_next_v243 import (
    load_original_preproduction,maizen_next_company_stage,
    director_pilot_shots,materialize_original_preproduction,
)
from cinefactory.studio.claude_mcp_gateway_v218 import build_server

def test_21_original_beats_cover_exactly_seven_chapters_and_full_14_min():
    p=load_original_preproduction()
    assert p["duration_seconds"]==840
    assert len(p["chapters"])==7
    assert len(p["beats"])==21
    assert p["beats"][0]["start"]==0 and p["beats"][-1]["end"]==840
    for i,b in enumerate(p["beats"]):
        assert b["end"]>b["start"]
        assert b["dialogue"] and b["action"] and b["audio"] and b["continuity"]
        assert b["creative_status"]=="ORIGINAL_WORKING_DRAFT_NOT_SOURCE_CONCLUSION"
        if i:assert b["start"]==p["beats"][i-1]["end"]
    assert all(sum(b["chapter"]==ch["id"] for b in p["beats"])==3 for ch in p["chapters"])

def test_original_assets_rights_and_rival_backend_uncertainty():
    p=load_original_preproduction()
    assert not any(p["original_rights"][k] for k in (
        "copy_Maizen_characters","copy_Maizen_dialogue","copy_Maizen_music",
        "copy_reference_assets"))
    assert {x["id"] for x in p["characters"]}=={"NOVA","PIP"}
    assert len(p["asset_requirements"])>=10
    assert set(p["technical_candidates"])=={"GAME_ENGINE_STAGED","BLENDER_AUTHORED","SCENE_HYBRID"}

def test_pilot_has_nine_consecutive_unrendered_shots():
    shots=director_pilot_shots()
    assert len(shots)==9
    assert shots[0]["start"]==0
    assert shots[-1]["end"]==45
    assert all(sh["end"]-sh["start"]==5 for sh in shots)
    assert all(sh["media_source"]=="NO_REAL_FRAMES_EXIST" for sh in shots)
    assert all(sh["execution_gate"]=="HOLD_G02_INDEPENDENT_FULL_REFERENCE_STUDY" for sh in shots)

def test_all_26_department_packets_are_drafts_with_research_pending():
    x=maizen_next_company_stage()
    assert x["company_department_count"]==26
    assert {r["department"] for r in x["per_department_status"]}=={d.value for d in DepartmentId}
    assert x["script_draft_beats"]==21
    assert x["draft_45sec_pilot_shots"]==9
    assert not x["source_full_video_qc_pass"]
    assert not x["can_execute_render_or_stage_G03_to_G28"]
    assert set(x["source_videos_still_missing_approval"])=={
        "ZmT0ITUGUII","zhPBXzHsLuo","oX6Azwe5QLg",
    }
    assert not x["full_pilot_media_created"]
    assert not x["publish_approved"]
    assert all(not d["autonomous_agent_completed_task"] and
               not d["actual_media_completed"]
               for d in x["per_department_status"])

def test_materialization_generates_sha_bound_drafts_idempotently_and_fails_closed(tmp_path):
    result=materialize_original_preproduction(tmp_path)
    assert result["work_products_created_or_verified"]==31
    assert result["department_receipts"]==26
    assert not result["any_render_started"]
    assert not result["source_research_cohort_gate_approved"]
    manifest=json.loads((tmp_path/"manifest.json").read_text(encoding="utf8"))
    assert len(manifest["artifacts"])==31
    for item in manifest["artifacts"]:
        blob=(tmp_path/item["file"]).read_bytes()
        assert sha256(blob).hexdigest()==item["sha256"]
    board=json.loads((tmp_path/"company_stage_board.json").read_text(encoding="utf8"))
    assert not board["can_execute_render_or_stage_G03_to_G28"]
    result2=materialize_original_preproduction(tmp_path)
    assert result2["manifest_sha256"]==result["manifest_sha256"]
    file=tmp_path/"department_audio.json"
    file.write_bytes(file.read_bytes()+b"\nALTERED")
    with pytest.raises(ValueError,match="EXISTING_PREPRO_ASSET_MODIFIED"):
        materialize_original_preproduction(tmp_path)

def test_mcp_readonly_cli_and_no_accidental_media_jobs():
    assert "maizen_next_company_stage" in build_server()._tool_manager._tools
    runner=CliRunner()
    run=runner.invoke(app,["maizen-company-next"])
    assert run.exit_code==0,str(run.exception)
    d=json.loads(run.output)
    assert d["stage"]=="DESK_PREPRO_WORK_PRODUCTS_ONLY"
    assert not d["can_execute_render_or_stage_G03_to_G28"]
    assert "materialization" not in d
