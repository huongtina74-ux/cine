"""v216 Agentic technology research must never become execution authority."""
import json
from typer.testing import CliRunner
import pytest
from cinefactory.cli import app
from cinefactory.studio.agentic_research_v216 import (
    load_agentic_research, advise_agentic_tools,
)
from cinefactory.studio.niche_technology_strategy_v213 import prepare_niche_technology_strategy

def test_archive_citations_and_catalog_are_bounded():
    kb=load_agentic_research()
    assert len(kb["source_sha256"])==64
    assert kb["registry_96_preserved"] is True
    assert kb["candidate_count"]==24
    assert kb["claim_count"]==10
    assert kb["source_github_reference_count"]>=13
    assert kb["auto_install"] is False
    assert kb["auto_authorize_paid_api"] is False
    assert kb["auto_switch_backend"] is False
    assert all(x["installed"] is False and x["benchmarked"] is False and not x["commercially_cleared"] for x in kb["candidates"])

def test_sora_flux3_ue6_and_splatting_claims_not_mixed():
    c={c["id"]:c for c in load_agentic_research()["claims"]}
    assert c["sora_shutdown"]["state"]=="OFFICIALLY_CONFIRMED"
    assert c["flux3"]["state"]=="OFFICIALLY_CONFIRMED_EARLY_ACCESS_NOT_LOCAL"
    assert c["unreal6"]["state"]=="MISSTATED_AS_AVAILABLE"
    assert c["gaussian_extension"]["state"]=="OVERSTATED_4D_STANDARD"
    assert c["agentic_electricity"]["state"]=="UNSUPPORTED_QUANTIFIED_SAVINGS"

def test_forced_auto_update_mcp_is_held():
    rows={r["id"]:r for r in load_agentic_research()["candidates"]}
    assert rows["blender_mcp_forced_update"]["priority"]=="HOLD"
    assert "replaces code" in rows["blender_mcp_forced_update"]["gates"].lower()
    assert rows["blender_mcp_218"]["priority"]=="HOLD"

def test_niche_and_editor_use_agentic_options_without_authorization():
    report=advise_agentic_tools("minecraft_story_adventure",department="EDITORIAL")
    assert report["media_family"]=="FILM_3D"
    assert report["matching_count"]>=1
    assert not report["production_permission"]
    assert all(not r["mcp_permission_to_execute"] and not r["production_qualified"] for r in report["candidates"])
    strategy=prepare_niche_technology_strategy("minecraft_story_adventure")
    assert strategy["registry_items"]==96
    assert strategy["agentic_2026_technology_research"]["candidate_catalog_count"]==24
    assert strategy["production_permission"] is False

def test_cli_review_includes_rnd_and_does_not_run_candidates():
    response=CliRunner().invoke(app,["agentic-technology-review","--minor-niche","minecraft_story_adventure","--department","RND"])
    assert response.exit_code==0,str(response.exception)
    obj=json.loads(response.output)
    assert obj["candidate_catalog_count"]==24
    assert obj["model_credit_spent"]==0
    assert obj["auto_install"] is False

def test_reject_unknown_department_and_invalid_limit():
    with pytest.raises(ValueError, match="UNKNOWN_DEPARTMENT"):
        advise_agentic_tools("minecraft_story_adventure",department="BAD")
    with pytest.raises(ValueError, match="LIMIT_OUT_OF_RANGE"):
        advise_agentic_tools("minecraft_story_adventure",limit=100)
