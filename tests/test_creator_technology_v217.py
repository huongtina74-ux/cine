"""v217 third-party creative services and Blender/Comfy MCP research only."""
import json
from typer.testing import CliRunner
import pytest

from cinefactory.cli import app
from cinefactory.studio.creator_technology_v217 import (
    load_creator_technology_research, suggest_creator_technologies
)
from cinefactory.studio.niche_technology_strategy_v213 import prepare_niche_technology_strategy

def test_original_96_stays_unchanged_and_no_paid_calls():
    d=load_creator_technology_research()
    assert d["baseline_96_unchanged"]
    assert d["no_auto_install"] and d["no_paid_calls"] and d["no_backend_switch"]
    assert d["credit_budget_usd"]==0
    assert len(d["candidates"])==17
    assert len(d["case_studies"])==6
    assert all(not r["installed_verified"] and not r["production_qualified"]
               for r in d["candidates"])

def test_blender_official_and_community_are_not_same_protocol():
    d=load_creator_technology_research()
    rows={r["id"]:r for r in d["candidates"]}
    assert "5.1" in rows["blender_official_mcp"]["gate"]
    assert "existing Cine 4.5" in rows["blender_official_mcp"]["gate"]
    assert "not the same protocol" in rows["blender_community_mcp"]["gate"].lower()

def test_credit_and_commercial_rights_are_not_silently_inferred():
    rows={r["id"]:r for r in load_creator_technology_research()["candidates"]}
    assert "NO commercial-use rights" in rows["piclumen"]["gate"]
    assert "ALWAYS deduct credits" in rows["higgsfield_mcp_cli"]["gate"]
    assert "CAN SPEND CREDITS" in rows["comfy_official_mcp"]["gate"]

def test_cinematography_and_editing_can_research_without_execution():
    r=suggest_creator_technologies("minecraft_story_adventure",department="EDITORIAL")
    assert r["candidate_catalog_total"]==17
    assert any(i["id"]=="openart_mcp" for i in r["items"])
    assert all(not i["execution_authorized"] and i["credit_budget_usd"]==0
               for i in r["items"])
    assert not r["production_permission"]
    strategy=prepare_niche_technology_strategy("minecraft_story_adventure")
    assert strategy["registry_items"]==96
    assert strategy["creator_2026_tool_research"]["candidate_catalog_total"]==17
    assert not strategy["production_permission"]

def test_long_slide_rnd_is_local_blender_orchestrator_first():
    r=suggest_creator_technologies("long_slices_game",department="RND")
    assert "blender_official_mcp" in {i["id"] for i in r["items"]}
    assert "magiclight" not in {i["id"] for i in r["items"]}

def test_cli_and_validation():
    result=CliRunner().invoke(app,["creator-tool-research",
        "--minor-niche","minecraft_story_adventure","--department","EDITORIAL"])
    assert result.exit_code==0,str(result.exception)
    x=json.loads(result.output)
    assert x["named_studio_case_studies"]==6
    assert not x["spend_authorized"]
    with pytest.raises(ValueError,match="UNKNOWN_DEPARTMENT"):
        suggest_creator_technologies("minecraft_story_adventure",department="WRONG")
    with pytest.raises(ValueError,match="LIMIT_OUT_OF_RANGE"):
        suggest_creator_technologies("minecraft_story_adventure",limit=100)
