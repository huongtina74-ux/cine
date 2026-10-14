"""v229 validates that the user's expert Agent Leap report was ingested accurately."""
import json
import pytest
from typer.testing import CliRunner
from cinefactory.cli import app
from cinefactory.studio.film_expert_adoption_v229 import (
    film_expert_adoption_audit,load_film_expert_intake
)
from cinefactory.studio.claude_mcp_gateway_v218 import build_server

def test_existing_user_agent_leap_and_encyclopedia_files_were_already_present():
    d=load_film_expert_intake()
    assert d["user_source"]=="config/technology/agent_leap_user_study_20261010.md"
    assert d["other_study"].endswith("cinematography_studio_user_encyclopedia_202510.md")
    assert len(d["technologies"])==15
    assert len(d["stages"])==8

def test_unverified_claims_not_misrepresented_as_working_installed_software():
    r=film_expert_adoption_audit()
    by={t["id"]:t for t in r["technology_statuses"]}
    assert by["ayon_noya_mcp"]["status"]=="NOT_VERIFIED_NOT_CONNECTED"
    assert by["ue6_scene_aware_ai"]["priority"]=="HOLD"
    assert by["gaussian_splatting"]["status"].endswith("UNSUPPORTED")
    assert by["render_farm_savings"]["priority"]=="HOLD"
    assert by["official_comfy_mcp"]["status"]=="OFFICIAL_AVAILABLE_NOT_CONNECTED_TO_COMPANY"
    assert by["openusd"]["status"]=="SOURCE_RESEARCHED_NO_END_TO_END_USD_INTERCHANGE_TEST"
    assert not r["full_production_studio_autonomy_proven"]
    assert not r["new_software_installed_by_this_adoption"]
    assert not r["new_mcp_providers_connected_by_this_adoption"]
    assert r["paid_credits_spent_by_this_adoption"]==0

def test_department_scope_is_constrained_to_existing_company_roles():
    r=film_expert_adoption_audit("TECHNICAL_DIRECTION")
    assert r["department"]=="TECHNICAL_DIRECTION"
    assert r["technology_records"]>3
    assert all("TECHNICAL_DIRECTION" in t["maps_to"] for t in r["technology_statuses"])
    with pytest.raises(ValueError,match="UNKNOWN_FILM_STUDIO_DEPARTMENT"):
        film_expert_adoption_audit("FAKE_DEPARTMENT")

def test_mcp_and_cli_expose_readonly_report():
    assert "film_expert_adoption_audit" in build_server()._tool_manager._tools
    runner=CliRunner()
    x=runner.invoke(app,["film-expert-adoption"])
    assert x.exit_code==0,str(x.exception)
    o=json.loads(x.stdout)
    assert o["source_user_study_exists"]
    assert o["technology_records"]==15
    assert not o["new_software_installed_by_this_adoption"]
