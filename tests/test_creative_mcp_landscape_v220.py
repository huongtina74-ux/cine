"""v220: source-backed read-only per-department Claude/MCP research catalog."""
import json
from typer.testing import CliRunner
import pytest
from cinefactory.cli import app
from cinefactory.studio.creative_mcp_landscape_v220 import (
    load_creative_software_mcp_landscape, plan_creative_mcp_for_niche
)
from cinefactory.studio.claude_mcp_gateway_v218 import build_server

def test_27_links_are_categorized_by_actual_connection_type_not_runtime():
    k=load_creative_software_mcp_landscape()
    assert k["registry_96_unchanged"] and k["no_auto_install"]
    assert k["no_auto_execute"] and k["no_spend"]
    assert len(k["items"])==27
    assert all(not x["installed_and_connected_to_cinefactory"]
               and not x["benchmarked"] and not x["production_approved"]
               for x in k["items"])
    types={x["connection_class"] for x in k["items"]}
    assert "OFFICIAL_NATIVE" in types and "COMMUNITY_MCP" in types
    assert "OFFICIAL_PRIVATE_PREVIEW" in types
    assert "NO_OFFICIAL_MCP_AS_OF_2026_06" in types

def test_ue_cinema_unity_silhouette_official_native_and_no_tracking_claim():
    x={r["id"]:r for r in load_creative_software_mcp_landscape()["items"]}
    for key in ("ue58_native","cinema4d_native","unity_cli_native","silhouette_native"):
        assert x[key]["connection_class"].startswith("OFFICIAL_NATIVE")
    assert x["flow_prod_tracking"]["connection_class"]=="NO_OFFICIAL_MCP_AS_OF_2026_06"
    assert x["comfy_partner_preview"]["connection_class"]=="OFFICIAL_PRIVATE_PREVIEW"
    assert x["runway_media_mcp"]["connection_class"]=="OFFICIAL_REMOTE_MCP"
    assert x["runway_dev_mcp"]["connection_class"]=="OFFICIAL_REMOTE_MCP"

def test_editor_audio_vfx_route_research_references_but_no_execution():
    x=plan_creative_mcp_for_niche("minecraft_story_adventure",department="VFX",limit=27)
    assert "ue58_native" in {r["id"] for r in x["options"]}
    assert "nuke_community" in {r["id"] for r in x["options"]}
    assert x["credits_spent"]==0 and x["auto_execute"] is False
    audio=plan_creative_mcp_for_niche("minecraft_story_adventure",department="AUDIO",limit=27)
    assert "reaper_audio" in {r["id"] for r in audio["options"]}
    assert "elevenlabs_remote" in {r["id"] for r in audio["options"]}
    assert all(not r["installed_in_company"] and not r["credit_spend_permission"] for r in audio["options"])

def test_unknown_niche_or_department_or_limit_are_blocked():
    with pytest.raises(ValueError,match="NICHE_REQUIRED"):
        plan_creative_mcp_for_niche("")
    with pytest.raises(ValueError,match="NICHE_NAME"):
        plan_creative_mcp_for_niche("../etc/passwd")
    with pytest.raises(ValueError,match="UNKNOWN_DEPARTMENT"):
        plan_creative_mcp_for_niche("minecraft_story_adventure",department="SUDO")
    with pytest.raises(ValueError,match="INVALID_RESULT_LIMIT"):
        plan_creative_mcp_for_niche("minecraft_story_adventure",limit=100)

def test_cli_and_mcp_offer_research_only():
    r=CliRunner().invoke(app,["creative-mcp-landscape","--minor-niche","minecraft_story_adventure","--department","EDITORIAL"])
    assert r.exit_code==0,str(r.exception)
    j=json.loads(r.output)
    assert j["verified_source_catalog_total"]==27
    assert j["production_permission"] is False
    s=build_server()
    assert "studio_software_mcp_research" in s._tool_manager._tools
