"""v218 Claude Code project MCP is a real read-only protocol endpoint."""
import asyncio
import json
from pathlib import Path
import sys

import pytest

from cinefactory.studio.claude_mcp_gateway_v218 import (
    POLICY, ROOT, studio_status, search_technology, department_research,
    niche_production_brief, mcps_for_niche, studio_review_protocol,
    build_server,
)

EXPECTED={
    "studio_status","search_technology","department_research",
    "niche_production_brief","mcps_for_niche","studio_review_protocol",
    "comfyui_local_status","comfyui_local_capabilities",
    "comfyui_local_queue","claude_external_connector_plan",
    "studio_software_mcp_research",
    "company_connector_inventory","company_scene_connector_plan",
    "minecraft_research_conference","original_minecraft_pilot_storyboard",
    "minecraft_company_roadmap","minecraft_next_approved_step",
    "minecraft_g01_g02_evidence",
    "maizen_studio_status","maizen_department_work",
    "maizen_runtime_readiness",
    "maizen_production_method_audit","maizen_shot_method_options",
    "maizen_full_video_review_gate","maizen_full_video_review_template",
    "maizen_research_stage_gate",
    "competitor_full_review_gate","competitor_study_department_gate",
    "film_expert_adoption_audit",
    "maizen_vidiq_provider_evidence",
    "maizen_browser_source_study",
    "maizen_next_company_stage",
    "maizen_three_source_video_study",
    "maizen_second_pass_av_evidence",
}

def test_studio_dashboard_uses_actual_registries():
    data=studio_status()
    assert data["baseline_tools"] == 96
    assert data["knowledge_references"] == 477
    assert data["company_departments"] == 26
    assert data["fixed_technology_watch_sources"] >= 15
    assert data["approved_new_backend_count"] == 0
    assert data["policy"]["owner_credit_budget_usd"] == 0

def test_canonical_gate_is_hard_readonly():
    assert all(not value for key,value in POLICY.items()
               if key in ("external_mcp_execution","shell_exec","cloud_or_paid_api",
                          "model_download","write_modify_delete","automation_creation",
                          "approval_grant","arbitrary_python_or_bpy"))
    toolset=set(build_server()._tool_manager._tools)
    assert toolset==EXPECTED
    assert all(not any(op in name for op in
        ("execute","install","deploy","start_render","paid","call_model","delete"))
        for name in toolset)

def test_actual_advisory_respects_niche_and_dept():
    q=search_technology("ComfyUI","minecraft_story_adventure","EDITORIAL",limit=5)
    assert q["matched"]>=1
    assert not q["production_permission"]
    assert not q["credit_spend_permission"]
    dr=department_research("long_slices_game","RND")
    assert dr["reference_ids"]
    brief=niche_production_brief("minecraft_story_adventure")
    assert brief["baseline_technology_entries"]==96
    assert brief["research_competitor_evidence"]["full_videos_verified"]==0
    assert not brief["production_permission"]
    adv=mcps_for_niche("minecraft_story_adventure","TECHNICAL_DIRECTION")
    assert adv["read_only_reference_only"]
    assert not adv["third_party_spend_permitted"]
    assert studio_review_protocol()["mandatory_gates"]

def test_bad_inputs_and_unknown_department_fail_closed():
    with pytest.raises(ValueError,match="NICHE_NAME"):
        niche_production_brief("../../../etc/passwd")
    with pytest.raises(ValueError,match="UNKNOWN_DEPARTMENT"):
        mcps_for_niche("minecraft_story_adventure","SUDO")
    with pytest.raises(ValueError,match="SEARCH_QUERY_REQUIRED"):
        search_technology("", "minecraft_story_adventure", "EDITORIAL")
    with pytest.raises(ValueError,match="LIMIT"):
        search_technology("ComfyUI","minecraft_story_adventure","RND",limit=200)

def test_claude_code_project_config_is_single_local_readonly_stdio():
    j=json.loads((ROOT/".mcp.json").read_text(encoding="utf-8"))
    assert list(j["mcpServers"])==["cinefactory-studio"]
    x=j["mcpServers"]["cinefactory-studio"]
    assert x["type"]=="stdio"
    assert x["command"]=="python"
    assert x["args"]==["-m","cinefactory.studio.claude_mcp_gateway_v218"]
    assert "env" not in x
    assert not any("https:" in str(t) for t in x.values())

def test_claude_skills_agents_exist_without_unsafe_default_permissions():
    agents=list((ROOT/".claude"/"agents").glob("*.md"))
    skills=list((ROOT/".claude"/"skills").glob("*/SKILL.md"))
    assert len(agents)==4
    assert len(skills)==8
    for a in agents:
        txt=a.read_text(encoding="utf-8")
        assert "permissionMode: plan" in txt
        assert "disallowedTools:" in txt
    assert "read-only" in (ROOT/"CLAUDE.md").read_text(encoding="utf-8").lower()

def test_stdio_mcp_protocol_initialize_list_and_call():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    async def run():
        params=StdioServerParameters(
            command=sys.executable,
            args=["-m","cinefactory.studio.claude_mcp_gateway_v218"],
            cwd=str(ROOT),
        )
        async with stdio_client(params) as (reader,writer):
            async with ClientSession(reader,writer) as session:
                init=await session.initialize()
                assert init.serverInfo.name=="cinefactory-studio-readonly"
                listing=await session.list_tools()
                assert {t.name for t in listing.tools}==EXPECTED
                res=await session.call_tool("studio_status",{})
                assert not res.isError
                text=" ".join(c.text for c in res.content if c.type=="text")
                assert "cine.studio.mcp_status.v218" in text
                assert '"baseline_tools":96' in text.replace(" ","")
                adv=await session.call_tool("niche_production_brief",{"minor_niche":"minecraft_story_adventure"})
                assert not adv.isError
                assert "production_permission" in " ".join(c.text for c in adv.content if c.type=="text")
                local=await session.call_tool("comfyui_local_status",{})
                assert not local.isError
                local_text=" ".join(c.text for c in local.content if c.type=="text")
                assert "cine.company.comfy_local_status.v219" in local_text
                assert "allows_generation" in local_text
                catalog=await session.call_tool("claude_external_connector_plan",{})
                assert not catalog.isError
                assert "cine.company.claude_external_connector_plan.v219" in " ".join(c.text for c in catalog.content if c.type=="text")
                new_inventory=await session.call_tool("company_connector_inventory",{"local_probe":False})
                assert not new_inventory.isError
                txt=" ".join(c.text for c in new_inventory.content if c.type=="text")
                assert "cine.company.connector_inventory.v221" in txt
                assert "connector_count" in txt
                candidate=await session.call_tool("company_scene_connector_plan",{
                    "niche":"minecraft_story_adventure", "department":"VFX", "limit":5,
                })
                assert not candidate.isError
                assert "cine.company.scene_connector_plan.v221" in " ".join(c.text for c in candidate.content if c.type=="text")
    asyncio.run(run())
