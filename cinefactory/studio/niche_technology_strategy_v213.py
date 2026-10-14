"""Evidence-first niche technology strategy for all CineFactory departments.

Matches the complete 96-item registry to niche/media requirements; it cannot
pretend that a competitor video was watched or that a candidate was benchmarked.
A study and a production decision are different artifacts.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from cinefactory.studio.technology_council_v212 import (
    STAGE_CAPABILITIES, counsel_for_all_departments,
)
from cinefactory.studio.technology_radar_v210 import load_technology_radar
from cinefactory.studio.technology_watch_v212 import WATCH, latest_watch_status
from cinefactory.studio.universal_competitor_review_v228 import competitor_full_review_gate


def _load_artifact(path: str | Path) -> tuple[Path, dict, str]:
    p = Path(path).resolve(strict=True)
    raw = p.read_bytes()
    obj = json.loads(raw)
    if not isinstance(obj, dict):
        raise ValueError("STRATEGY_ARTIFACT_MUST_BE_JSON_OBJECT")
    return p, obj, sha256(raw).hexdigest()


def prepare_niche_technology_strategy(
    minor_niche: str,
    *,
    major_niche: str | None = None,
    conference_file: str | Path | None = None,
    bakeoff_file: str | Path | None = None,
    company_root: str | Path | None = None,
) -> dict:
    """Produce an advisory, not a tool install, paid API call or render."""
    if not isinstance(minor_niche, str) or not minor_niche.strip():
        raise ValueError("NICHE_REQUIRED")
    radar = load_technology_radar()
    company = counsel_for_all_departments(minor_niche, major_niche, radar=radar)
    family = company["media_family"]
    inventory = {}
    for item in radar["items"]:
        inventory.setdefault(item["category"], []).append(item["id"])
    included = [i for ids in inventory.values() for i in ids]
    if len(included) != len(set(included)) or len(included) != radar["entry_count"]:
        raise ValueError("TECHNOLOGY_INVENTORY_MISMATCH")

    conference = None
    con_path = None
    con_sha = None
    competitor = {
        "status": "NO_COMPETITOR_VIDEO_CONFERENCE",
        "catalogued_cases": 0,
        "full_videos_verified": 0,
        "deep_review_authenticated": False,
        "competitor_stack_verified": False,
        "public_views_not_retention_or_rpm": True,
        "required_evidence": [
            "Channel age and dated long-form catalogue, leaders AND weaker controls",
            "Lawfully accessible video and sound, timecoded full-video inspection",
            "Hook, scene/shot pacing, camera, assets, character, motion, lighting, audio, edit",
            "Observed claims separated from hypotheses and private-metric unknowns",
            "Copyright, originality and reused-content risk analysis",
        ],
    }
    if conference_file is not None:
        con_path, conference, con_sha = _load_artifact(conference_file)
        if conference.get("schema") != "cine.studio.production_conference.v1":
            raise ValueError("CONFERENCE_SCHEMA_INVALID")
        if conference.get("approved_niche") != minor_niche:
            raise ValueError("COMPETITOR_CONFERENCE_NICHE_MISMATCH")
        cases = conference.get("video_cases")
        if not isinstance(cases, list) or len(cases) != conference.get("video_case_count"):
            raise ValueError("COMPETITOR_CASE_COUNT_MISMATCH")
        ids = [x.get("video_id") for x in cases if isinstance(x, dict)]
        if len(ids) != len(cases) or len(ids) != len(set(ids)):
            raise ValueError("COMPETITOR_VIDEO_IDS_INVALID")
        # A mutable checkbox, screenshot or thumbnail does not prove that a
        # human/multimodal reviewer inspected complete frames and soundtrack.
        competitor.update({
            "status": "FULL_VIDEO_AUTHENTICATED_REVIEW_REQUIRED",
            "conference_file": str(con_path),
            "conference_sha256": con_sha,
            "catalogued_cases": len(cases),
            "full_video_inspection_self_reports": sum(
                x.get("full_video_inspection") == "DONE" for x in cases
            ),
            "full_videos_verified": 0,
            "deep_review_authenticated": False,
            "source_rights_claim": conference.get("source_rights_status", "UNKNOWN"),
        })

    bakeoff = {"status": "NO_COMPARABLE_PILOTS", "quality_passed_scenarios": {},
               "advisory_only": True}
    if bakeoff_file is not None:
        if con_sha is None:
            raise ValueError("BAKEOFF_REQUIRES_COMPETITOR_CONFERENCE")
        p, data, digest = _load_artifact(bakeoff_file)
        if data.get("schema") != "cine.studio.pilot_bakeoff.v1":
            raise ValueError("PILOT_BAKEOFF_SCHEMA_INVALID")
        if data.get("conference_sha256") != con_sha:
            raise ValueError("BAKEOFF_CONFERENCE_REVISION_MISMATCH")
        # Pilot comparison is already evidence-gated by its source evaluator,
        # but never converts an advisory ranking into execution authority.
        bakeoff = {
            "status": data.get("state", "UNKNOWN"),
            "file": str(p), "sha256": digest,
            "quality_passed_scenarios": data.get("advisory_rankings", {}),
            "advisory_only": True,
            "authenticated_owner_signoff": False,
        }

    # The same 96 entries must remain available for R&D, even when most do
    # not match this particular production format.
    scene_trials = {}
    for intent in STAGE_CAPABILITIES:
        scoped = counsel_for_all_departments(
            minor_niche, major_niche, scene_intent=intent, radar=radar
        )
        for dept in ("PRODUCTION", "AUDIO", "EDITORIAL", "TECHNICAL_DIRECTION"):
            proposals = scoped["all_departments"].get(dept, {}).get(
                "technology_candidates", []
            )
            scene_trials.setdefault(intent, {})[dept] = [
                x["id"] for x in proposals
            ]
    watch = {"tracked_fixed_sources": len(WATCH),
             "sources_with_any_observed_snapshot": 0,
             "source_snapshots_total": 0}
    if company_root is not None:
        watch = latest_watch_status(Path(company_root))
    blockers = []
    if family == "UNRESOLVED":
        blockers.append("CLASSIFY_VIDEO_FORMAT_BEFORE_ROUTING")
    if competitor["full_videos_verified"] == 0:
        blockers.append("FULL_COMPETITOR_VIDEO_AUDIO_STUDY_NOT_AUTHENTICATED")
    if not bakeoff["quality_passed_scenarios"]:
        blockers.append("QUALITY_AND_ACCEPTED_SECONDS_PER_HOUR_NOT_BENCHMARKED")
    blockers.append("SIGNED_RIGHTS_AND_OWNER_PRODUCTION_APPROVAL_REQUIRED")

    from cinefactory.studio.technology_knowledge_v215 import department_knowledge_index
    knowledge_routes = department_knowledge_index(minor_niche, top_k=5)
    from cinefactory.studio.agentic_research_v216 import advise_agentic_tools
    new_agentic_research = advise_agentic_tools(minor_niche, limit=8)
    from cinefactory.studio.creator_technology_v217 import suggest_creator_technologies
    latest_creator_tools = suggest_creator_technologies(minor_niche, limit=10)
    from cinefactory.studio.company_connector_registry_v221 import (
        company_department_connector_index, company_scene_connector_plan,
    )
    all_creative_mcp_routes = company_department_connector_index(minor_niche, top_k=6)
    creative_mcp_pilot_plan = company_scene_connector_plan(minor_niche, limit=12)
    # Only original Minecraft animated-film lanes inherit this artwork baseline.
    # Authentic gameplay/machinima must instead prove actual game runtime media.
    original_mc_animation = minor_niche in {
        "minecraft_story_adventure", "minecraft_school_comedy",
        "minecraft_monster_fantasy", "minecraft_animated_challenge",
    }
    minecraft_art_study = None
    if original_mc_animation:
        from cinefactory.studio.minecraft_production_research_v222 import (
            minecraft_research_conference,
        )
        minecraft_art_study = minecraft_research_conference()
    mc_animation_names = {
        "minecraft_story_adventure", "minecraft_school_comedy",
        "minecraft_monster_fantasy", "minecraft_animated_challenge",
        "minecraft_challenge_survival",
    }
    mc_gameplay_names = {
        "minecraft_recorded_survival", "minecraft_gameplay_tutorial",
        "minecraft_scripted_machinima",
    }
    minecraft_company_roster = None
    if minor_niche in mc_animation_names | mc_gameplay_names:
        from cinefactory.studio.minecraft_company_roadmap_v223 import (
            minecraft_company_roadmap,
        )
        mc_lane = ("AUTHORED_VOXEL_3D_ANIMATION"
                   if minor_niche in mc_animation_names
                   else "SCRIPTED_MINECRAFT_GAMEPLAY")
        minecraft_company_roster = minecraft_company_roadmap(lane=mc_lane)

    selected_competitor_ids=(
        [v["video_id"] for v in conference["video_cases"]]
        if conference is not None else None
    )
    full_competitor_gate=competitor_full_review_gate(minor_niche,selected_competitor_ids)
    return {
        "schema": "cine.company.niche_technology_strategy.v213",
        "niche": minor_niche, "major_niche": major_niche,
        "format_family": family,
        "registry_items": len(included),
        "registry_by_category": {k: sorted(v) for k, v in sorted(inventory.items())},
        "all_departments_count": company["department_count"],
        "department_technology_advisory": company["all_departments"],
        "all_department_knowledge_references": knowledge_routes,
        "agentic_2026_technology_research": new_agentic_research,
        "creator_2026_tool_research": latest_creator_tools,
        "creative_software_mcp_department_routes": all_creative_mcp_routes,
        "creative_software_mcp_staging": creative_mcp_pilot_plan,
        "minecraft_original_animation_research": minecraft_art_study,
        "minecraft_two_lane_company_roadmap": minecraft_company_roster,
        "competitor_video_research": competitor,
        "universal_full_video_audio_first_gate": full_competitor_gate,
        "deep_competitor_evidence_gate_passed":full_competitor_gate["deep_full_episode_analysis_allowed"],
        "competitor_method_and_backend_auto_approval":False,
        "per_scene_pilot_candidates": scene_trials,
        "measured_pilot_evidence": bakeoff,
        "quality_speed_rule": (
            "First pass rights, character identity, visual continuity, "
            "story/audio and per-shot quality gates; ONLY THEN maximize "
            "accepted finished seconds per hour and minimize real rework/cost "
            "on the same comparable scenes and machine."
        ),
        "evaluation_dimensions": [
            "identity_consistency", "character_acting", "lighting_materials",
            "camera_motion", "temporal_stability", "sound_and_lipsync",
            "story_and_retention_hypotheses", "accepted_seconds_per_hour",
            "human_rework", "VRAM", "license_and_total_cost",
        ],
        "update_policy": {
            "source_watch": watch,
            "watch_source_ids": sorted(WATCH),
            "discovery_on_each_niche_research": "GITHUB_AND_HUGGINGFACE_OPT_IN",
            "review_new_claude_code_claude_agent_sdk_mcp_plugins": True,
            "never_autoinstall_or_run_untrusted_repository": True,
            "never_call_paid_api_without_owner_authorization": True,
            "new_source_is_NOT_new_qualified_backend": True,
        },
        "decision": "RESEARCH_AND_PILOT_PLAN_ONLY",
        "blockers": blockers,
        "automatic_backend_switch": False,
        "production_permission": False,
        "competitor_methods_are_hypotheses_not_proven_tool_usage": True,
    }
