"""CineFactory v218 project MCP gateway for Claude Code (READ ONLY).

Owns no token, GPU, filesystem writes, shell subprocess, network operation,
model download, job submission or third-party MCP forwarding. Its tools only
read previously-reviewed local registries and return research advisories.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import re

from cinefactory.studio.technology_radar_v210 import load_technology_radar
from cinefactory.studio.technology_knowledge_v215 import (
    load_company_knowledge, query_company_knowledge,
    department_knowledge_index,
)
from cinefactory.studio.niche_technology_strategy_v213 import (
    prepare_niche_technology_strategy,
)
from cinefactory.studio.creator_technology_v217 import suggest_creator_technologies
from cinefactory.studio.agentic_research_v216 import advise_agentic_tools
from cinefactory.studio.technology_watch_v212 import WATCH

ROOT = Path(__file__).resolve().parents[2]
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _:-]{0,119}$")
SAFE_TEXT = re.compile(r"^[^\x00-\x1f]{1,120}$")
DEPARTMENT_NAMES = frozenset((
    "INTELLIGENCE", "EVIDENCE", "STUDIO_MANAGEMENT", "PLANNING",
    "CREATIVE_STRATEGY", "RND", "RD_KNOWLEDGE", "OPERATIONS", "RIGHTS",
    "QC", "ANALYTICS", "PACKAGING", "TECHNICAL_DIRECTION",
    "WRITERS_ROOM", "SCRIPT_LOGIC", "PERFORMANCE", "PRODUCTION_DESIGN",
    "ASSETS", "DIRECTION", "CINEMATOGRAPHY", "PRODUCTION",
    "GENERATIVE_MEDIA", "VFX", "AUDIO", "EDITORIAL", "COLOR"
))
POLICY = {
    "mode": "READ_ONLY_LOCAL",
    "external_mcp_execution": False,
    "arbitrary_python_or_bpy": False,
    "shell_exec": False,
    "model_download": False,
    "write_modify_delete": False,
    "automation_creation": False,
    "cloud_or_paid_api": False,
    "approval_grant": False,
    "assume_video_watched": False,
    "assume_model_benchmarked": False,
    "owner_credit_budget_usd": 0,
    "fidelity_first": True,
    "selected_method_must_pass_rights_and_quality_before_speed": True,
}

def _niche(value: str) -> str:
    if not isinstance(value, str) or not SAFE_NAME.fullmatch(value.strip()):
        raise ValueError("NICHE_NAME_MUST_BE_PLAIN_AND_NONEMPTY")
    return value.strip()

def _dept(value: str) -> str:
    if not isinstance(value, str) or value not in DEPARTMENT_NAMES:
        raise ValueError("UNKNOWN_DEPARTMENT")
    return value

def _limit(value: int, max_allowed: int = 12) -> int:
    if type(value) is not int or not 1 <= value <= max_allowed:
        raise ValueError("LIMIT_OUT_OF_RANGE")
    return value

def studio_status() -> dict:
    base = load_technology_radar()
    kb = load_company_knowledge()
    source_ids = [r["id"] for r in base["items"]]
    assert len(source_ids) == len(set(source_ids)) == 96
    return {
        "schema": "cine.studio.mcp_status.v218",
        "repository": "cinefactory-os",
        "baseline_tools": len(base["items"]),
        "knowledge_references": len(kb["entries"]),
        "source_study_records": kb["user_source_row_count"],
        "source_workflows": kb["workflow_count"],
        "company_departments": len(DEPARTMENT_NAMES),
        "approved_new_backend_count": sum(bool(x["deploy_approved"]) for x in base["items"]),
        "fixed_technology_watch_sources": len(WATCH),
        "human_approval_required": True,
        "policy": POLICY,
        "not_verified": [
            "External MCP servers installed/connected",
            "Vendor benchmarks on RTX 3060 12GB",
            "Full competitor video-and-audio observations for this request",
            "Commercial rights to unreviewed model weights and SaaS outputs",
        ],
    }

def search_technology(query: str, minor_niche: str,
                      department: str, limit: int = 8) -> dict:
    _niche(minor_niche)
    _dept(department)
    _limit(limit, 30)
    if not isinstance(query, str) or not SAFE_TEXT.fullmatch(query.strip()):
        raise ValueError("SEARCH_QUERY_REQUIRED")
    report = query_company_knowledge(
        query=query.strip(), minor_niche=minor_niche,
        department=department, limit=limit,
    )
    return {
        "schema": "cine.studio.mcp_technology_search.v218",
        "matched": report["matching_records"],
        "items": report["items"],
        "rights_verification_pending": True,
        "production_permission": False,
        "credit_spend_permission": False,
    }

def department_research(minor_niche: str, department: str) -> dict:
    minor_niche = _niche(minor_niche)
    department = _dept(department)
    report = department_knowledge_index(minor_niche, top_k=8)
    return {
        "schema": "cine.studio.mcp_department_advisory.v218",
        "niche": minor_niche, "department": department,
        "reference_ids": report["department_candidate_references"][department],
        "all_company_departments": report["department_count"],
        "tool_selection_verified": False, "production_permission": False,
    }

def niche_production_brief(minor_niche: str) -> dict:
    niche = _niche(minor_niche)
    x = prepare_niche_technology_strategy(niche)
    return {
        "schema": "cine.studio.mcp_niche_production_brief.v218",
        "niche": niche, "format": x["format_family"],
        "departments": x["all_departments_count"],
        "baseline_technology_entries": x["registry_items"],
        "research_competitor_evidence": {
            k: x["competitor_video_research"].get(k)
            for k in ("status", "catalogued_cases", "full_videos_verified")
        },
        "research_missing": x["blockers"],
        "quality_speed_rule": x["quality_speed_rule"],
        "cost_and_quality_requirements": x["evaluation_dimensions"],
        "editorial_reference_ids": x["all_department_knowledge_references"][
            "department_candidate_references"]["EDITORIAL"],
        "rnd_reference_ids": x["all_department_knowledge_references"][
            "department_candidate_references"]["RND"],
        "scene_intents": list(x["per_scene_pilot_candidates"]),
        "production_permission": False,
        "unsupported_claims_cannot_be_promoted": True,
    }

def mcps_for_niche(minor_niche: str, department: str,
                   limit: int = 8) -> dict:
    niche = _niche(minor_niche)
    dept = _dept(department)
    _limit(limit, 20)
    local = advise_agentic_tools(niche, department=dept, limit=limit)
    cloud = suggest_creator_technologies(niche, department=dept, limit=limit)
    return {
        "schema": "cine.studio.mcp_candidate_advisory.v218",
        "niche": niche, "department": dept,
        "community_research": local["candidates"],
        "studio_service_research": cloud["items"],
        "read_only_reference_only": True,
        "not_an_mcp_install_command": True,
        "third_party_spend_permitted": False,
        "tool_execution_permitted": False,
    }

def studio_review_protocol() -> dict:
    return {
        "schema": "cine.studio.mcp_review_protocol.v218",
        "mandatory_gates": [
            "Research niche, actual competitor channel catalogue, new/old winner controls",
            "Inspect authorized full competitor visual frames and sound with timecoded notes",
            "Separate observed shot mechanics from guessed tools and private analytics",
            "Write original creative bible and shot-level quality/method requirements",
            "Evaluate no-credit local approach first, then optional commercial alternatives",
            "Check dependencies, security, rights, license and RTX3060 12GB realism",
            "Benchmark same-scene quality, continuity and audio, then speed/rework/VRAM",
            "Require explicit owner approval before installations, charge, switching backend",
            "Verify release quality, provenance and regression/rollback for production",
        ],
        "priority": [
            "1 source and license integrity",
            "2 identity + story + audio + visual acceptance",
            "3 accepted finished seconds per hour",
            "4 cost and GPU efficiency under the quality floor",
        ],
        "read_only_gateway": True,
        "production_permission": False,
        "owner_credit_budget_usd": 0,
    }

def build_server():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError(
            "Optional MCP SDK missing: install pip install -e '.[claude]'"
        ) from exc
    app = FastMCP(
        name="cinefactory-studio-readonly",
        instructions=(
            "Official local CineFactory research gateway. Every tool returns "
            "read-only recommendations. NEVER claim competitor footage was "
            "watched, performance benchmarked, or production approved. "
            "Do not install/run other MCP servers via this gateway."
        ),
        log_level="ERROR",
    )
    app.tool(name="studio_status")(studio_status)
    app.tool(name="search_technology")(search_technology)
    app.tool(name="department_research")(department_research)
    app.tool(name="niche_production_brief")(niche_production_brief)
    app.tool(name="mcps_for_niche")(mcps_for_niche)
    app.tool(name="studio_review_protocol")(studio_review_protocol)
    # Live localhost ComfyUI introspection (read-only HTTP GET whitelist only).
    # No partner_generate, workflow run, model download, or arbitrary host.
    from .local_ai_connector_v219 import (
        comfyui_local_status, comfyui_local_capabilities,
        comfyui_local_queue, claude_external_connector_plan,
    )
    app.tool(name="comfyui_local_status")(comfyui_local_status)
    app.tool(name="comfyui_local_capabilities")(comfyui_local_capabilities)
    app.tool(name="comfyui_local_queue")(comfyui_local_queue)
    app.tool(name="claude_external_connector_plan")(claude_external_connector_plan)
    from .creative_mcp_landscape_v220 import plan_creative_mcp_for_niche
    app.tool(name="studio_software_mcp_research")(plan_creative_mcp_for_niche)
    from .company_connector_registry_v221 import (
        company_connector_inventory, company_scene_connector_plan,
    )
    app.tool(name="company_connector_inventory")(company_connector_inventory)
    app.tool(name="company_scene_connector_plan")(company_scene_connector_plan)
    from .minecraft_production_research_v222 import (
        minecraft_research_conference, original_minecraft_pilot_storyboard,
    )
    app.tool(name="minecraft_research_conference")(minecraft_research_conference)
    app.tool(name="original_minecraft_pilot_storyboard")(original_minecraft_pilot_storyboard)
    from .minecraft_company_roadmap_v223 import (
        minecraft_company_roadmap, minecraft_next_approved_step,
    )
    app.tool(name="minecraft_company_roadmap")(minecraft_company_roadmap)
    app.tool(name="minecraft_next_approved_step")(minecraft_next_approved_step)
    from .minecraft_source_evidence_v224 import minecraft_g01_g02_evidence
    app.tool(name="minecraft_g01_g02_evidence")(minecraft_g01_g02_evidence)
    from .maizen_studio_kickoff_v225 import (
        maizen_studio_status, maizen_department_work,
    )
    app.tool(name="maizen_studio_status")(maizen_studio_status)
    app.tool(name="maizen_department_work")(maizen_department_work)
    from .maizen_runtime_preflight_v225 import maizen_runtime_readiness
    app.tool(name="maizen_runtime_readiness")(maizen_runtime_readiness)
    from .maizen_method_review_v226 import (
        maizen_production_method_audit, maizen_shot_method_options,
    )
    app.tool(name="maizen_production_method_audit")(maizen_production_method_audit)
    app.tool(name="maizen_shot_method_options")(maizen_shot_method_options)
    from .maizen_full_video_gate_v227 import (
        maizen_full_video_review_gate, draft_full_review_template,
    )
    app.tool(name="maizen_full_video_review_gate")(maizen_full_video_review_gate)
    app.tool(name="maizen_full_video_review_template")(draft_full_review_template)
    from .maizen_full_video_gate_v227 import maizen_research_stage_gate
    app.tool(name="maizen_research_stage_gate")(maizen_research_stage_gate)
    from .universal_competitor_review_v228 import (
        competitor_full_review_gate, competitor_study_department_gate,
    )
    app.tool(name="competitor_full_review_gate")(competitor_full_review_gate)
    app.tool(name="competitor_study_department_gate")(competitor_study_department_gate)
    from .film_expert_adoption_v229 import film_expert_adoption_audit
    app.tool(name="film_expert_adoption_audit")(film_expert_adoption_audit)
    from .maizen_vidiq_provider_v230 import maizen_vidiq_provider_evidence
    app.tool(name="maizen_vidiq_provider_evidence")(maizen_vidiq_provider_evidence)
    from .maizen_browser_source_review_v237 import maizen_browser_source_study
    app.tool(name="maizen_browser_source_study")(maizen_browser_source_study)
    from .maizen_company_next_v243 import maizen_next_company_stage
    app.tool(name="maizen_next_company_stage")(maizen_next_company_stage)
    from .maizen_three_source_study_v248 import maizen_three_source_video_study
    app.tool(name="maizen_three_source_video_study")(maizen_three_source_video_study)
    from .maizen_second_pass_av_v251 import maizen_second_pass_av_evidence
    app.tool(name="maizen_second_pass_av_evidence")(maizen_second_pass_av_evidence)
    return app

def main() -> None:
    build_server().run(transport="stdio")

if __name__ == "__main__":
    main()
