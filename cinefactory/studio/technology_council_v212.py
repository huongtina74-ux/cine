"""v212: common Research-to-department technology council for all CineFactory.

No new agent/plugin/model is auto-run. Format source truth first, then craft,
department and scene intent, then licensing and actual execution qualification.
"""
from __future__ import annotations
from collections import Counter

from .contracts import DepartmentId
from .technology_discovery_v211 import production_family, FAMILY
from .technology_radar_v210 import load_technology_radar
from .technology_watch_v212 import WATCH

# Only existing registry entries can be offered as pre-qualified CANDIDATES.
# Claude and MCP are administration / research tools, not cinematic renderers.
CORPORATE_TOOLS={
    "INTELLIGENCE":("github","huggingface","youtubeapi","semrush"),
    "EVIDENCE":("github","huggingface","youtubeapi"),
    "STUDIO_MANAGEMENT":("github","huggingface"),
    "PLANNING":("github","huggingface"),
    "CREATIVE_STRATEGY":("huggingface","github"),
    "RND":("github","huggingface","comfy_templates"),
    "RD_KNOWLEDGE":("github","huggingface","comfy_templates"),
    "OPERATIONS":("github","ffmpeg","blender"),
    "RIGHTS":("github","huggingface"),
    "QC":("ffmpeg","whisper","fasterwhisper"),
    "ANALYTICS":("youtubeapi","semrush"),
    "PACKAGING":("flux_klein4b","hyperframes","ffmpeg"),
    "TECHNICAL_DIRECTION":("comfyui","blender","ffmpeg"),
}
DEPT_CATEGORIES={
    "WRITERS_ROOM":{"audio","image"},
    "SCRIPT_LOGIC":{"research"},
    "PERFORMANCE":{"animation_motion","audio"},
    "PRODUCTION_DESIGN":{"image","3d"},
    "ASSETS":{"image","3d"},
    "DIRECTION":{"3d","animation_motion"},
    "CINEMATOGRAPHY":{"3d","video"},
    "PRODUCTION":{"video","3d","editorial"},
    "GENERATIVE_MEDIA":{"image","video"},
    "VFX":{"video","3d"},
    "AUDIO":{"audio"},
    "EDITORIAL":{"editorial"},
    "COLOR":{"editorial","image"},
}
STAGE_CAPABILITIES={
    "dialogue":("moss","qwen3tts","chatterbox","audio2face","ffmpeg"),
    "acting":("blender","unirig","audio2face","ffmpeg"),
    "camera":("blender","ffmpeg","comfyui"),
    "vfx":("blender","comfyui","wan22","ffmpeg"),
    "environment":("blender","flux_klein4b","comfyui","ffmpeg"),
    "music":("acestep","ffmpeg","moss"),
    "montage":("ffmpeg","hyperframes","remotion"),
    "captions":("ffmpeg","whisper","fasterwhisper","hyperframes"),
    "real_capture":("ffmpeg","whisper","fasterwhisper"),
}
ANIMATED_ONLY={"blender","unirig","audio2face","flux_klein4b","wan22"}
CAPTURE_ONLY={"GAME_CAPTURE","LIVE_CAPTURE","FIELD_CAPTURE","REAL_ASMR"}
CLAUDE_ADVISORY_KINDS={"INTELLIGENCE","EVIDENCE","RND","RD_KNOWLEDGE",
                       "OPERATIONS","STUDIO_MANAGEMENT","PLANNING",
                       "TECHNICAL_DIRECTION","WRITERS_ROOM","SCRIPT_LOGIC"}

def _candidate(row,*,rank:int,role:str):
    return {
        "id":row["id"],"name":row["name"],"rank":rank,
        "craft_role":role,"department":row["department"],
        "source":row["official_or_project_url"],
        "license_gate":row["commercial_gate"],
        "hardware_claim":row["rtx3060_fit"],
        "runtime_evidence":row["local_runtime"],
        "approval":"CANDIDATE_ONLY",
        "commercial_output_qualified":False,
        "owner_signed_execution_authority":False,
    }

def _allowed_ids_for_family(family:str,radar:dict)->set[str]:
    allowed=set(FAMILY.get(family,()))
    # Allow existing entries in exactly matching professional departments
    # only if they are in the format's established family. Do not infer a
    # gameplay backend from an animation video demo in the same large niche.
    return {x for x in allowed if any(r["id"]==x for r in radar["items"])}

def counsel_for_all_departments(
    minor_niche:str|None,major_niche:str|None=None,
    *,scene_intent:str|None=None,radar:dict|None=None,
) ->dict:
    radar=radar or load_technology_radar()
    family=production_family(minor_niche,major_niche)
    if scene_intent and scene_intent not in STAGE_CAPABILITIES:
        raise ValueError("UNKNOWN_SCENE_INTENT")
    by_id={x["id"]:x for x in radar["items"]}
    allowed=_allowed_ids_for_family(family,radar)
    scene_allowed=set(STAGE_CAPABILITIES.get(scene_intent,()))
    if family in CAPTURE_ONLY:
        scene_allowed-=ANIMATED_ONLY
    if family=="UNRESOLVED":
        allowed=set()
        scene_allowed=set()
    # A scene specialization can only choose from its format's safe
    # conceptual family, not silently expand to unsupported media.
    selected=allowed & scene_allowed if scene_intent else allowed
    departments={}
    for dept in DepartmentId:
        role=dept.value
        raw=list(CORPORATE_TOOLS.get(role,()))
        categories=DEPT_CATEGORIES.get(role,set())
        if categories:
            raw.extend(x for x in FAMILY.get(family,()) if
                       x in selected and x in by_id and
                       by_id[x]["category"] in categories)
        # A production team without media-specialist tokens uses general
        # original family entries but not arbitrary tools of other niches.
        if role in {"TECHNICAL_DIRECTION","PRODUCTION","OPERATIONS"}:
            raw.extend(x for x in FAMILY.get(family,()) if x in selected)
        unique=list(dict.fromkeys(
            x for x in raw if x in by_id and (
                (x in selected) or
                (x in CORPORATE_TOOLS.get(role,()) and
                 role not in {"PRODUCTION","GENERATIVE_MEDIA","VFX"})
            )
        ))
        if family in CAPTURE_ONLY and role in {
            "PRODUCTION","TECHNICAL_DIRECTION","OPERATIONS"}:
            unique=[x for x in unique if x not in ANIMATED_ONLY]
        proposals=[_candidate(by_id[x],rank=i+1,role=role)
                   for i,x in enumerate(unique[:10])]
        watch_ids=(
            [k for k,(_,_,c) in WATCH.items() if
             c in {"CLAUDE_AGENT","CLAUDE_PLUGIN","CLAUDE_MODEL_PLATFORM",
                   "MCP_PROTOCOL","MCP_SERVER"}][:12]
            if role in CLAUDE_ADVISORY_KINDS else []
        )
        departments[role]={
            "advisory_status":"RESEARCH_ONLY_UNQUALIFIED",
            "format_family":family,
            "scene_intent":scene_intent,
            "technology_candidates":proposals,
            "claude_mcp_update_watch_ids":watch_ids,
            "ready_new_backend_count":0,
            "may_install_mcp_server":False,
            "may_invoke_claude_paid_api":False,
            "may_switch_production_backend":False,
            "new_tool_requires_timecoded_competitor_video_audio_review":True,
            "entire_reference_film_and_original_audio_required_before_method_conclusion":True,
            "ten_second_sample_or_thumbnails_never_sufficient":True,
            "competitor_specific_method_conclusions_automatically_authorized":False,
            "new_tool_requires_original_scoped_quality_speed_pilot":True,
            "qualified_quality_floor_precedes_speed_optimization":True,
        }
    return {
        "schema":"cine.company.technology_council.v212",
        "minor_niche":minor_niche,
        "major_niche":major_niche,
        "media_family":family,"scene_intent":scene_intent,
        "all_departments":departments,
        "department_count":len(departments),
        "base_technology_inventory_count":len(radar["items"]),
        "advised_new_backends_automatically_qualified":0,
        "current_production_executor_mutated":False,
        "all_recommendations_require_separate_rights_security_benchmark":True,
        "unresolved_niche_requires_classification":family=="UNRESOLVED",
    }

def company_stage_technology_routing(blueprint,*,radar:dict|None=None)->dict:
    """Attach actual scene/department advisory to the entire company DAG."""
    niche=blueprint.project.niche
    route=blueprint.minecraft_route
    minor=route.subniche_id if route is not None else niche
    council=counsel_for_all_departments(minor,niche,radar=radar)
    # Every company stage can cite the whole studio knowledge inventory
    # through its owner department, without promoting a candidate to an executor.
    from .technology_knowledge_v215 import department_knowledge_index
    kb_routes=department_knowledge_index(minor,top_k=5)
    from .company_connector_registry_v221 import company_department_connector_index
    # Legacy blueprints may have no niche yet; remain resumable and
    # do not invent a media family or grant executors for unknown input.
    creative_connectors=company_department_connector_index(minor or "UNRESOLVED",top_k=6)
    mapping={}
    for stage in blueprint.stages:
        owner=stage.owner
        dept=council["all_departments"].get(owner,{
            "technology_candidates":[],"advisory_status":"NO_MATCHING_DEPARTMENT",
        })
        mapping[stage.stage_id]={
            "stage_owner":owner,
            "candidate_ids":[x["id"] for x in dept["technology_candidates"]],
            "claude_mcp_sources_to_watch":dept.get("claude_mcp_update_watch_ids",[]),
            "knowledge_reference_ids":kb_routes["department_candidate_references"].get(owner,[]),
            "knowledge_recommendations_require_qualification":True,
            "creative_software_mcp_candidate_ids":creative_connectors["department_candidate_ids"].get(owner,[]),
            "creative_software_mcp_candidates_not_executors":True,
            "handler_qualified_by_this_advisory":False,
            "backend_change_authorized":False,
            "competitor_video_audio_study_required_for_new_method":True,
            "mandatory_complete_film_and_original_audio_before_competitor_method_conclusion":True,
            "short_excerpts_cannot_substitute_entire_reference":True,
            "quality_pass_before_speed_choice_required":True,
        }
    return {
        "schema":"cine.company.stage_technology_routing.v212",
        "family":council["media_family"],"department_count":council["department_count"],
        "stage_count":len(mapping),"stages":mapping,
        "shared_studio_knowledge_router":kb_routes["schema"],
        "shared_studio_knowledge_departments":kb_routes["department_count"],
        "creative_software_mcp_registry":creative_connectors["schema"],
        "creative_software_mcp_catalog_total":creative_connectors["catalog_total"],
        "existing_executor_and_rights_gates_preserved":True,
    }
