"""v225 hands off concrete original Maizen-style desk-work to all 26 departments."""
import json
from hashlib import sha256
from pathlib import Path

import pytest
from typer.testing import CliRunner

from cinefactory.cli import app
from cinefactory.studio.contracts import DepartmentId
from cinefactory.studio.maizen_studio_kickoff_v225 import (
    load_maizen_studio_a,maizen_studio_status,maizen_department_work,
    materialize_maizen_desk_receipts,
)
from cinefactory.studio.minecraft_company_roadmap_v223 import minecraft_company_roadmap
from cinefactory.studio.claude_mcp_gateway_v218 import build_server


def test_entire_department_cast_has_individual_nonempty_actual_work_products():
    data=load_maizen_studio_a()
    assert len(data["all_26_departments"])==26
    assert set(data["all_26_departments"])=={x.value for x in DepartmentId}
    assert len({row["deliverable"] for row in data["all_26_departments"].values()})==26
    assert all(isinstance(row["output"],dict) and row["output"]
               for row in data["all_26_departments"].values())
    assert data["auth"]["owner_selected_maizen_style"]
    assert not any(data["auth"][x] for x in (
        "paid_cloud_call","download_or_install",
        "release","game_or_software_purchase",
        "auto_approve_claude_project_mcp"
    ))


def test_first_original_pilot_nine_shots_are_executable_spec_not_fake_video():
    project=load_maizen_studio_a()
    scene=project["pilot"]
    assert scene["seconds"]==45 and len(scene["shots"])==9
    assert not scene["real_game_captured"]
    assert scene["shots"][0]["start"]==0
    assert scene["shots"][-1]["end"]==45
    assert all(x["end"]-x["start"]==5 and x["dialogue"]
               for x in scene["shots"])
    assert not project["all_26_departments"]["PRODUCTION"]["output"]["raw_video_exists"]


def test_14_minute_episode_has_seven_nonpadding_original_story_chapters():
    x=load_maizen_studio_a()["episode"]
    assert x["duration_seconds"]==840
    assert len(x["chapters"])==7
    assert sum(x["end"]-x["start"] for x in x["chapters"])==840
    assert not x["actual_episode_video_exists"]
    assert "behind" in x["working_title"].lower()


def test_every_department_can_report_its_work_and_blocker():
    out=maizen_studio_status()
    assert out["department_count"]==26
    assert out["deliverable_count"]==26
    assert out["pilot_shot_count"]==9
    assert out["episode_chapter_count"]==7
    assert out["all_departments_have_written_draft_or_blocker"]
    assert not out["all_departments_completed_production"]
    assert not out["real_minecraft_capture_ready"]
    assert out["credits_spent"]==0
    assert maizen_department_work("AUDIO")["draft"]["recorded_voice_exists"] is False
    assert maizen_department_work("PRODUCTION")["state"]=="BLOCKED_EXTERNAL_DEPENDENCY"
    assert maizen_department_work("RIGHTS")["draft"]["game_license_unverified"]


def test_kickoff_writes_exact_26_hash_bound_receipts_is_idempotent(tmp_path):
    a=materialize_maizen_desk_receipts(tmp_path)
    b=materialize_maizen_desk_receipts(tmp_path)
    assert a["verified_department_handoffs"]==b["verified_department_handoffs"]==26
    manifest=json.loads((tmp_path/"manifest.json").read_text(encoding="utf8"))
    assert manifest["receipt_count"]==26
    assert manifest["actual_video_capture_receipts"]==0
    assert manifest["remote_ai_calls"]==0
    assert len(list(tmp_path.glob("*.json")))==27
    for entry in manifest["receipts"]:
        payload=(tmp_path/entry["file"]).read_bytes()
        assert sha256(payload).hexdigest()==entry["sha256"]
        assert json.loads(payload)["owner"]==entry["owner"]


def test_modified_handoff_cannot_be_silently_overwritten(tmp_path):
    materialize_maizen_desk_receipts(tmp_path)
    (tmp_path/"audio.json").write_text('{"edited":"human"}',encoding="utf8")
    with pytest.raises(ValueError,match="ALREADY_EDITED"):
        materialize_maizen_desk_receipts(tmp_path)


def test_company_roadmap_considers_selected_maizen_pipeline_not_bigschool():
    gameplay=minecraft_company_roadmap(lane="SCRIPTED_MINECRAFT_GAMEPLAY")
    kickoff=gameplay["maizen_selected_studio_a_kickoff"]
    assert kickoff["project"]=="MAI01_WATERFALL"
    assert kickoff["department_count"]==26
    assert not kickoff["production_release_authorized"]
    other=minecraft_company_roadmap(lane="AUTHORED_VOXEL_3D_ANIMATION")
    assert other["maizen_selected_studio_a_kickoff"] is None


def test_cli_and_mcp_are_readonly_unless_user_runs_explicit_start():
    cli=CliRunner()
    check=cli.invoke(app,["maizen-studio"])
    assert check.exit_code==0,str(check.exception)
    assert json.loads(check.output)["project"]=="MAI01_WATERFALL"
    audio=cli.invoke(app,["maizen-studio","--department","AUDIO"])
    assert audio.exit_code==0,str(audio.exception)
    assert json.loads(audio.output)["draft"]["recorded_voice_exists"] is False
    assert "maizen_studio_status" in build_server()._tool_manager._tools
    assert "maizen_department_work" in build_server()._tool_manager._tools


def test_invalid_department_and_no_authorized_external_exec():
    with pytest.raises(ValueError,match="UNKNOWN_DEPARTMENT"):
        maizen_department_work("SUDO")
    x=load_maizen_studio_a()
    assert x["auth"]["paid_cloud_call"] is False
    assert x["auth"]["download_or_install"] is False
    assert x["auth"]["release"] is False


def test_runtime_preflight_reads_installed_paths_without_launch(monkeypatch):
    from cinefactory.studio import maizen_runtime_preflight_v225 as runtime
    class SocketDeny:
        def __enter__(self): return self
        def __exit__(self,*_): return False
    monkeypatch.setattr(runtime.socket, "create_connection",
                        lambda *a,**k: (_ for _ in ()).throw(OSError("closed")))
    data=runtime.maizen_runtime_readiness()
    assert data["schema"]=="cine.minecraft.maizen_runtime_readiness.v225"
    assert not data["obs_websocket_port_4455_listening"]
    assert not data["obs_websocket_authenticated"]
    assert not data["game_license_verified"]
    assert not data["capture_pipeline_live"]
    assert not data["external_spend_authorized"]
    assert data["install_or_launch_performed"] is False


def test_runtime_cli():
    cli=CliRunner()
    x=cli.invoke(app,["maizen-runtime"])
    assert x.exit_code==0,str(x.exception)
    d=json.loads(x.output)
    assert "obs_studio_binary_found" in d
    assert not d["game_license_verified"]
    assert "maizen_runtime_readiness" in build_server()._tool_manager._tools
