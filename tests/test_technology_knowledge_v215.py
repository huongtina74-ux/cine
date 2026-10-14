"""v215: full 18-section ingestion is auditably research-only."""
import hashlib
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from cinefactory.cli import app
from cinefactory.studio.technology_knowledge_v215 import (
    ROOT, SOURCE, FULL_SOURCE, KINDS, load_company_knowledge,
    query_company_knowledge, department_knowledge_index,
)
from cinefactory.studio.niche_technology_strategy_v213 import (
    prepare_niche_technology_strategy,
)


def test_every_study_section_and_workflow_preserved_without_header_noise():
    kb = load_company_knowledge()
    assert kb["schema"] == "cine.company.technology_knowledge.v215"
    assert kb["sections"] == list(range(1, 19))
    assert kb["user_source_row_count"] == 363
    assert kb["baseline_count"] == 96
    assert kb["research_v214_count"] == 18
    assert len(kb["entries"]) == 477
    assert kb["workflow_count"] == len(kb["workflows"]) == 8
    assert all(len(flow["steps"]) >= 2 for flow in kb["workflows"])
    assert {x["id"] for x in kb["workflows"]} == {f"STUDY_WORKFLOW_{i:02d}" for i in range(1, 9)}
    assert not kb["owner_approved_installation"]
    assert not kb["paid_api_authorized"]
    assert kb["new_candidates_automatically_qualified"] == 0


def test_original_user_sources_are_bound_by_digests_and_line_numbers():
    kb = load_company_knowledge()
    assert kb["user_source_hashes"]["inventory_sha256"] == hashlib.sha256(
        SOURCE.read_bytes()).hexdigest()
    assert kb["user_source_hashes"]["encyclopedia_sha256"] == hashlib.sha256(
        FULL_SOURCE.read_bytes()).hexdigest()
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    for record in kb["entries"]:
        if record["source_id"].startswith("STUDY_"):
            assert 1 <= record["source_line"] <= len(lines)
            assert record["name"].split(" — ")[0] in lines[record["source_line"]-1]
            assert record["section_number"] in KINDS
            assert record["installed"] == "UNKNOWN"
            assert record["license"] == "NOT_CHECKED"
            assert record["benchmark"] == "NOT_RUN"
            assert record["production_permission"] is False


def test_proprietary_and_mcp_are_references_not_executables():
    kb = load_company_knowledge()
    proprietary = [x for x in kb["entries"] if x["kind"] ==
                   "PROPRIETARY_INHOUSE_REFERENCE_ONLY"]
    mcp = [x for x in kb["entries"] if x["kind"] ==
           "MCP_SERVER_IDEA_UNVERIFIED"]
    assert len(proprietary) == 12
    assert len(mcp) == 10
    assert all(not r["production_permission"] for r in proprietary + mcp)
    assert kb["no_proprietary_reference_execution"]


def test_source_software_aliases_link_to_known_registry():
    kb = load_company_knowledge()
    rows = {r["name"]: r for r in kb["entries"] if r["kind"] not in (
        "BASELINE_96", "PRO_STUDIO_RND_V214"
    )}
    assert "BASE_blender" in rows["Blender 4.2+ LTS"]["related_known_record_ids"]
    assert "BASE_comfyui" in rows["comfyanonymous/ComfyUI"]["related_known_record_ids"]
    assert "RND_opentimelineio" in rows["OpenTimelineIO (OTIO)"]["related_known_record_ids"]


def test_research_edit_audio_and_mcp_are_searchable_and_readonly():
    for kw, expected in [
        ("iZotope", "iZotope RX Advanced"),
        ("vfx-mcp", "vfx-mcp"),
        ("OpenUSD", "OpenUSD"),
        ("LangGraph", "LangGraph"),
    ]:
        result = query_company_knowledge(query=kw, limit=100)
        assert expected in {x["name"] for x in result["items"]}
        assert result["production_permission"] is False
        assert all(not x["automatically_approved"] for x in result["items"])


def test_all_26_departments_use_shared_reference_database():
    result = department_knowledge_index("minecraft_story_adventure")
    assert result["department_count"] == 26
    assert "EDITORIAL" in result["department_candidate_references"]
    assert "RND" in result["department_candidate_references"]
    assert result["recommendations_do_not_authorize_backend_execution"]


def test_unqualified_research_reaches_niche_strategy_without_granting_permission():
    strategy = prepare_niche_technology_strategy("long_slices_game")
    x = strategy["all_department_knowledge_references"]
    assert x["department_count"] == 26
    assert not strategy["production_permission"]
    assert strategy["registry_items"] == 96


def test_cli_search_and_department_summary():
    client = CliRunner()
    result = client.invoke(app, [
        "technology-knowledge", "--query", "reaper", "--department", "AUDIO"
    ])
    assert result.exit_code == 0, str(result.exception)
    data = json.loads(result.output)
    assert data["user_study_rows"] == 363
    assert data["base_registry_count"] == 96
    assert data["research_v214_count"] == 18
    assert data["reference_workflows"] == 8
    assert data["research_only"]
    report = client.invoke(app, [
        "technology-knowledge-summary", "--minor-niche", "asmr_sleep_hands_objects"
    ])
    assert report.exit_code == 0, str(report.exception)
    assert json.loads(report.output)["department_count"] == 26


def test_query_fail_closed_on_invalid_role_kind_or_limit():
    with pytest.raises(ValueError, match="UNKNOWN_DEPARTMENT"):
        query_company_knowledge(department="UNKNOWN")
    with pytest.raises(ValueError, match="UNKNOWN_KNOWLEDGE_KIND"):
        query_company_knowledge(kind="UNAPPROVED_SERVER")
    with pytest.raises(ValueError, match="QUERY_LIMIT"):
        query_company_knowledge(limit=1000)


def test_company_stage_dag_receives_readonly_refs_for_edit_and_research():
    from types import SimpleNamespace
    from cinefactory.studio.technology_council_v212 import (
        company_stage_technology_routing,
    )
    blueprint = SimpleNamespace(
        project=SimpleNamespace(niche="minecraft_story_adventure"),
        minecraft_route=None,
        stages=[
            SimpleNamespace(stage_id="INTELLIGENCE_RESEARCH", owner="INTELLIGENCE"),
            SimpleNamespace(stage_id="EDIT", owner="EDITORIAL"),
        ],
    )
    report = company_stage_technology_routing(blueprint)
    assert report["shared_studio_knowledge_departments"] == 26
    assert report["stage_count"] == 2
    for stage in report["stages"].values():
        assert "knowledge_reference_ids" in stage
        assert stage["knowledge_recommendations_require_qualification"] is True
        assert stage["backend_change_authorized"] is False
    assert report["existing_executor_and_rights_gates_preserved"] is True
