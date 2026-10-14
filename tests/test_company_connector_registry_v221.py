"""v221 integration of all 27 creative software/MCPs with 26 departments."""
import json
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from cinefactory.cli import app
from cinefactory.studio.company_connector_registry_v221 import (
    company_connector_inventory, company_department_connector_index,
    company_scene_connector_plan,
)
from cinefactory.studio.niche_technology_strategy_v213 import (
    prepare_niche_technology_strategy,
)
from cinefactory.studio.technology_council_v212 import (
    company_stage_technology_routing,
)


def test_every_single_v220_connector_is_in_company_registry_without_activation():
    k=company_connector_inventory()
    assert k["schema"]=="cine.company.connector_inventory.v221"
    assert k["connector_count"]==27
    assert k["all_connectors_in_company_plan"]
    assert k["baseline_96_unchanged"]
    assert len({x["id"] for x in k["records"]})==27
    assert all(x["integration_activation"]=="NOT_CONNECTED_TO_CLAUDE_CODE"
               and x["production_execution"]=="DENIED_NO_QUALIFIED_CONNECTOR"
               and not x["auditable_external_commands_allowed"]
               for x in k["records"])
    assert k["external_connectors_enabled"]==0
    assert k["paid_provider_jobs_authorized"]==0
    assert k["production_backend_changes"]==0


def test_all_26_departments_inherit_27_catalog_not_27_executors():
    index=company_department_connector_index("minecraft_story_adventure",top_k=6)
    assert index["department_count"]==26
    assert index["catalog_total"]==27
    assert index["department_candidate_ids"]["VFX"]
    assert index["department_candidate_ids"]["AUDIO"]
    assert index["executors_changed"] is False
    assert index["all_candidates_require_validation"]


def test_company_stages_get_owner_specific_software_options():
    blueprint=SimpleNamespace(
        project=SimpleNamespace(niche="minecraft_story_adventure"),
        minecraft_route=None,
        stages=[SimpleNamespace(stage_id="VFX_STUDY",owner="VFX"),
                SimpleNamespace(stage_id="AUDIO_STUDY",owner="AUDIO"),
                SimpleNamespace(stage_id="EDIT",owner="EDITORIAL")],
    )
    x=company_stage_technology_routing(blueprint)
    assert x["creative_software_mcp_catalog_total"]==27
    assert x["stage_count"]==3
    assert "houdini_fx" in x["stages"]["VFX_STUDY"]["creative_software_mcp_candidate_ids"]
    assert "reaper_audio" in x["stages"]["AUDIO_STUDY"]["creative_software_mcp_candidate_ids"]
    assert x["existing_executor_and_rights_gates_preserved"]
    assert all(not row["backend_change_authorized"] for row in x["stages"].values())
    assert all(row["creative_software_mcp_candidates_not_executors"] for row in x["stages"].values())


def test_niche_report_includes_pilot_plan_but_no_auto_switch():
    d=prepare_niche_technology_strategy("minecraft_story_adventure")
    assert d["registry_items"]==96
    assert d["creative_software_mcp_department_routes"]["catalog_total"]==27
    assert d["creative_software_mcp_staging"]["connected_company_catalog_count"]==27
    assert d["creative_software_mcp_staging"]["all_unapproved_backend_execution_denied"]
    assert d["production_permission"] is False
    assert d["automatic_backend_switch"] is False


def test_selected_mcp_cloud_and_preview_require_actual_approval():
    d=company_scene_connector_plan("minecraft_story_adventure",limit=27)
    q={x["id"]:x for x in d["options"]}
    assert q["runway_media_mcp"]["mcp_status"]=="NOT_CONNECTED_TO_CLAUDE_CODE"
    assert q["runway_media_mcp"]["execution_status"]=="DENIED_NO_QUALIFIED_CONNECTOR"
    assert q["comfy_official_local"]["mcp_status"]=="NOT_CONNECTED_TO_CLAUDE_CODE"
    assert q["comfy_official_local"]["underlying_local_comfyui"] is None
    assert d["decision"]=="STAGE_PILOT_REQUIRES_EXPLICIT_APPROVAL"


def test_safe_local_probe_does_not_misrepresent_comfy_mcp(monkeypatch):
    import cinefactory.studio.local_ai_connector_v219 as local
    monkeypatch.setattr(local,"comfyui_local_status",lambda:{
        "connection":"RESPONDING","comfy_version":"0.38.0"
    })
    d=company_connector_inventory(local_probe=True)
    matched={x["id"]:x for x in d["records"]}
    assert matched["comfy_official_local"]["underlying_local_comfyui"]["connection"]=="RESPONDING"
    assert matched["comfy_official_local"]["underlying_local_comfyui"]["local_get_bridge_available"]
    assert matched["comfy_official_local"]["underlying_local_comfyui"]["official_comfy_mcp_connected"] is False
    assert d["external_connectors_enabled"]==0


def test_cli_inventory_and_research_route():
    cli=CliRunner()
    x=cli.invoke(app,["company-connectors","--inventory"])
    assert x.exit_code==0,str(x.exception)
    assert len(json.loads(x.output)["records"])==27
    y=cli.invoke(app,["company-connectors","--minor-niche","minecraft_story_adventure",
                       "--department","AUDIO"])
    assert y.exit_code==0,str(y.exception)
    data=json.loads(y.output)
    assert data["department"]=="AUDIO"
    assert data["connected_company_catalog_count"]==27
    assert any(row["id"]=="reaper_audio" for row in data["options"])


def test_invalid_department_niche_and_limit_rejected():
    with pytest.raises(ValueError,match="UNKNOWN_DEPARTMENT"):
        company_scene_connector_plan("minecraft_story_adventure",department="NONEXISTENT")
    with pytest.raises(ValueError,match="NICHE_NAME"):
        company_scene_connector_plan("../../etc",limit=2)
    with pytest.raises(ValueError,match="LIMIT_OUT_OF_RANGE"):
        company_scene_connector_plan("minecraft_story_adventure",limit=50)
    with pytest.raises(ValueError,match="TOP_K_OUT_OF_RANGE"):
        company_department_connector_index("minecraft_story_adventure",top_k=20)
