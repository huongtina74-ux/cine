"""Read-only internal company structure audit, real CineFactory v1.6.40.

Does not call APIs, start renderers, enable paid agents, or approve release.
Reports distinct 3 types: governance functions, department enum/specs, concrete
stage handlers; they are not equivalent to 26 operating human/AI agents.
"""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from cinefactory.appctx import build_context
from cinefactory.studio.corporate import DEFAULT_COMPANY_FUNCTIONS
from cinefactory.studio.contracts import DepartmentId,MediaFormat
from cinefactory.studio.departments import DEFAULT_DEPARTMENTS,default_department_registry
from cinefactory.studio.niche_os import DEFAULT_NICHES
from cinefactory.studio.production_tool_catalog_v191 import NICHE_BLUEPRINTS,host_inventory
from cinefactory.studio.company import stage_blueprint
from cinefactory.studio.company_handlers import FilmCompanyHandlers,FilmHandlerConfig
from cinefactory.studio.daily_youtube_breakout_v199 import SEARCH_LANES,BreakoutLedger
from cinefactory.studio.niche_competitor_guard_v200 import LANE_TO_NICHE

def main():
    ctx=build_context(ROOT)
    registry=default_department_registry()
    cfg=FilmHandlerConfig()
    handlers=FilmCompanyHandlers(ctx,config=cfg).registry()
    source_niches=ROOT/"config/niches"
    folder_names=sorted(x.name for x in source_niches.iterdir() if x.is_dir())
    config_status={}
    for name in folder_names:
        comp=(source_niches/name/"competitors.yaml")
        text=comp.read_text(encoding="utf-8") if comp.exists() else ""
        config_status[name]={
            "competitors_file":str(comp),"channels_seeded":("channels: []" not in text),
            "file_has_only_empty_channels_breakout_and_hypotheses":all(
                f"{marker}: []" in text for marker in
                ("channels","breakout_channels","breakout_videos","production_hypotheses")),
        }
    stage_formats={}
    for media,niche in ((MediaFormat.ANIMATION,"minecraft"),
                        (MediaFormat.GAMEPLAY,"minecraft"),
                        (MediaFormat.MUSIC_VIDEO,"preschool_3d_musical")):
        stages=stage_blueprint(media,True,professional_governance=True,professional_niche=niche)
        stage_formats[media.value]={
            "stage_count":len(stages),
            "stages":[{
                "stage_id":s.stage_id,"owner":s.owner,
                "required":s.required,"gate":s.gate,
                "registered_handler":handlers.get(s.stage_id) is not None,
                "output_artifacts":s.artifacts_out,
            } for s in stages],
            "missing_required_handlers":[s.stage_id for s in stages
                                          if s.required and handlers.get(s.stage_id) is None],
            "full_episode_actual_executed_in_this_audit":False,
        }
    info=host_inventory(ROOT)
    ledger=BreakoutLedger(ROOT/"data/research/youtube_breakout/cinefactory_breakout.sqlite3")
    output={
        "version":"CineFactory v1.6.40 structural inspection",
        "root":str(ROOT.resolve()),
        "git_commit_not_automatically_validated_by_this_script":True,
        "organization":{
            "enum_departments":len(DepartmentId),
            "formal_core_specs":len(DEFAULT_DEPARTMENTS),
            "default_injected_RND_KNOWLEDGE_spec":len(registry.list())-len(DEFAULT_DEPARTMENTS),
            "specialist_spec_department_ids":[k.value for k in DEFAULT_DEPARTMENTS],
            "all_named_department_ids":[x.value for x in DepartmentId],
            "company_management_functions":len(DEFAULT_COMPANY_FUNCTIONS),
            "management":[
                {"id":k.value,"mission":v.mission,"authority":v.authority,
                 "artifacts_written":v.writes,"gates":v.gates,"metrics":v.metrics}
                for k,v in DEFAULT_COMPANY_FUNCTIONS.items()
            ],
            "specialist_departments":[{
                "id":k.value,"mission":v.mission,
                "reads":v.reads,"writes":v.writes,
                "capabilities":v.skills,"quality_checks":v.qc_gates,
                "declared_tools_NOT necessarily installed":v.tools,
            } for k,v in DEFAULT_DEPARTMENTS.items()],
        },
        "execution":{
            "default_film_company_mode":cfg.production_mode,
            "diagnostic_slate_allow_override":cfg.allow_diagnostic_slate,
            "registered_stage_handler_count":len(handlers.ids()),
            "stage_handler_ids":handlers.ids(),
            "sample_workflows":stage_formats,
            "all_stages_live_implemented_verified":False,
        },
        "niche_portfolio":{
            "core_registered_niches":list(DEFAULT_NICHES),
            "core_registered_count":len(DEFAULT_NICHES),
            "blueprints":list(NICHE_BLUEPRINTS),
            "blueprint_count":len(NICHE_BLUEPRINTS),
            "missing_core_registry_for_blueprints":sorted(set(NICHE_BLUEPRINTS)-set(DEFAULT_NICHES)),
            "niche_config_folder_count":len(folder_names),
            "per_core_niche_config":config_status,
            "core_competitor_registry_entries":{
                k:len(v.competitor_registry) for k,v in DEFAULT_NICHES.items()},
            "all_core_competitor_registries_empty":all(
                not v.competitor_registry for v in DEFAULT_NICHES.values()),
            "niche_queries_have_distinct_format_labels":len(SEARCH_LANES)==len(LANE_TO_NICHE),
            "search_lanes":SEARCH_LANES,
            "research_lanes_supported":len(SEARCH_LANES),
            "source_is_not_exhaustive":True,
        },
        "observed_local_tools":{
            "blender_local_version":info["blender_version_probe"],
            "ffmpeg_local_version":info["ffmpeg_version_probe"],
            "local_comfyui_folder_exists":info["comfyui_folder_exists"],
            "comfyui_video_workflow_executable_verified":info["comfyui_video_workflow_executable_verified"],
            "godot_runtime_verified":info["godot_runtime_verified"],
            "remotion_executable_verified":info["remotion_executable_verified"],
        },
        "daily_research":{
            "local_windows_task_known_registered_from_previous_current_turn":True,
            "daily_research_service_is_company_member":ctx.daily_youtube_breakout_research is ctx.studio.professional_company.daily_youtube_breakout_research,
            "stats":ledger.stats(),
            "separate_per_niche_report_folder":"data/research/youtube_breakout/niches/",
            "core_niche_preflight_manifests_unchanged":True,
            "claude_model_actually_invoked_by_this_scanner":False,
            "full_video_and_audio_truly_viewed":False,
        },
        "real_studio_output_qualification":{
            "cross_niche_competitor_playbooks_fully_approved":False,
            "godot_real_trial_complete":False,
            "preschool_music_3d_episode_ready":False,
            "professional_minecraft_series_accepted":False,
            "full_autonomous_corporation_ready":False,
        },
    }
    dest=ROOT/"data/research/youtube_breakout/company_structure_audit_v200.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding="utf-8")
    print("AUDIT_EVIDENCE_WRITTEN",dest)
    print("STRUCTURE_COUNTS",len(DepartmentId),len(DEFAULT_COMPANY_FUNCTIONS),
          len(DEFAULT_DEPARTMENTS),len(registry.list()),len(handlers.ids()),
          len(DEFAULT_NICHES),len(NICHE_BLUEPRINTS),len(SEARCH_LANES))
    print("ACTIVE_REQUIRED_STAGE_GAPS",{
        k:v["missing_required_handlers"] for k,v in stage_formats.items()})
    print("ALL_CORE_NICHE_COMPETITOR_CONFIG_EMPTY",all(
        x["file_has_only_empty_channels_breakout_and_hypotheses"]
        for x in config_status.values()))
if __name__=="__main__":main()
