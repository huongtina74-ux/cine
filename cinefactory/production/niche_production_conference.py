"""Evidence-first research-to-production conference.

Approval of a niche TRIGGERS work, not automatic claims about unseen videos.
Combine Company YouTube evidence, video-level inspection worklists, official tool
candidate catalog and comparative pilot tests. Source-backed facts only.

All model/tool/benchmark scores are ADVISORY until independent quality and owner
approval. No third-party competitor video download or paid API calls.
"""
from __future__ import annotations
import hashlib
import json
import math
import statistics
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from cinefactory.production.studio_director import LANES, NICHE_BLUEPRINTS, _canon

VID=re.compile(r"^[A-Za-z0-9_-]{11}$")
DIMENSIONS=("story","acting_expression","identity_continuity","camera","world_art",
            "lighting_render","motion_stability","edit_pacing","sound","originality")
TOOL_CATALOG={
 "blender_character_animation":{
   "tools":["Blender Python + NLA","CharacterRigRegistry","ExpressionEngine","AnimationClipLibrary"],
   "official":"https://docs.blender.org/manual/en/latest/files/linked_libraries/library_overrides.html",
   "integration":"EXISTING_PARTIAL_LOCAL_WORKERS","license":"VERIFY_ASSET_RIG_AND_PLUGINS",
   "critical_tests":["persistent character identity across 3 shots","facial reaction/eyes/mouth",
                     "character-to-prop contact","camera/eye-line continuity"]},
 "unreal_realtime_cinematic":{
   "tools":["Unreal Engine","Sequencer","Control Rig","Movie Render Queue"],
   "official":"https://dev.epicgames.com/documentation/en-us/unreal-engine/",
   "integration":"CANDIDATE_NOT_EXECUTABLE_VERIFIED","license":"VERIFY_ENGINE_AND_ASSET_TERMS",
   "critical_tests":["original scene geometry","performance transfer","stable frame rate"]},
 "comfyui_controlled_ai_video":{
   "tools":["ComfyUI API","LTX-2.5","Wan2.2","Control/reference workflows"],
   "official":"https://docs.comfy.org/development/comfyui-server/comms_routes",
   "integration":"PARTIAL_COMPILER_AVAILABLE_MODEL_NOT_PROVEN","license":"MODEL_BY_MODEL_REVIEW_REQUIRED",
   "critical_tests":["character identity across cuts","temporal flicker","camera control",
                     "run-to-run reproducibility","model commercial rights"]},
 "game_engine_capture":{
   "tools":["Unity/Unreal/Godot scene runtime","rigged assets","physics obstacle templates"],
   "official":"https://docs.godotengine.org/en/stable/",
   "integration":"ENGINE_EXECUTABLE_UNVERIFIED","license":"VERIFY_ENGINE_ASSET_AND_PLUGIN_TERMS",
   "critical_tests":["collision outcome","asset consistency","camera follows obstacles"]},
 "physical_camera_capture":{
   "tools":["camera/field recorder","DaVinci Resolve","Fairlight"],
   "official":"https://www.blackmagicdesign.com/products/davinciresolve",
   "integration":"PHYSICAL_INPUT_NOT_VERIFIED","license":"OWNED_FOOTAGE_AND_AUDIO_REQUIRED",
   "critical_tests":["microphone noise floor","focus/exposure","authenticity","no jarring sounds"]},
 "audio_environment":{
   "tools":["owned/cleared audio stems","FFmpeg","Fairlight","loudness/loop QA"],
   "official":"https://ffmpeg.org/documentation.html",
   "integration":"FFMPEG_AVAILABLE_AUDIO_SOURCE_NOT_VERIFIED","license":"AUDIO_SOURCE_RIGHTS_REQUIRED",
   "critical_tests":["true loop seam","loudness consistency","speech/music license"]},
 "remotion_graphics":{
   "tools":["Remotion","FFmpeg","After Effects optional"],
   "official":"https://www.remotion.dev/docs/license/pricing",
   "integration":"PROCEDURAL_RENDER_UNVERIFIED","license":"COMPANY_AUTOMATION_LICENSE_CHECK_REQUIRED",
   "critical_tests":["accurate timings","typography","subtitles","cross-platform codec QC"]},
 "veo_cloud_video":{
   "tools":["Google Gemini video API/Veo","Google Flow user interface"],
   "official":"https://ai.google.dev/gemini-api/docs/video",
   "integration":"OPTIONAL_CLOUD_NOT_CONNECTED_OR_AUTHORIZED",
   "license":"CREDIT_COST_OUTPUT_RIGHTS_TERMS_REVIEW",
   "critical_tests":["first/last frame consistency","actor identity over shots",
                     "commercial terms","cost per accepted second"]},
 "resolve_master_finishing":{
   "tools":["DaVinci Resolve Edit","Fusion","Fairlight","Color","Deliver"],
   "official":"https://www.blackmagicdesign.com/products/davinciresolve",
   "integration":"CANDIDATE_UNVERIFIED_INSTALLED_RUNTIME",
   "license":"VALID_LICENSE_AND_AUDIO_ASSETS",
   "critical_tests":["timeline conform","multitrack dialogue/foley","color management",
                     "frame-accurate cut","audio loudness","4K master"]},
}
STAGES=(
 ("provenance","Verify niche approval, snapshot currency, exact IDs, competitor sample provenance"),
 ("sampling","Collect 3+ top, 3+ fresh and 2+ underperforming comparable long videos where possible"),
 ("annotation","Inspect whole source media/captions legally with timeline, hooks, character beats, cuts and audio"),
 ("pattern","Cross-video contrast: distinguish repeatable signal from founder age, luck and attribution"),
 ("creative","Generate ORIGINAL production premise, full beat sheet, character/world bibles, directional style DNA"),
 ("technical","Select and bench methods PER difficult shot rather than selecting one model for whole channel"),
 ("pilot","Render difficult acting, environment/camera, full edit/audio pilot with comparable timing and QC"),
 ("evaluation","Compare quality and accepted seconds/hour against measured targets; challenge failed takes"),
 ("post","Choose assembly/fine-cut, color, SFX/mix, packaging, format & 4K mastering from actual trial"),
 ("ownership","Human signoff and licensed assets; only then create a production pod"),
)


def _digest(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _load(p:Path)->dict:
    obj=json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(obj,dict):raise ValueError("JSON object expected")
    return obj


def _freeze(path:Path)->dict:
    file=path.resolve(strict=True)
    return {"path":str(file),"sha256":_digest(file)}


def _require_same(p:dict):
    src=Path(p["path"]).resolve(strict=True)
    if _digest(src)!=p["sha256"]:raise ValueError("Source mutated: "+src.name)
    return src


def prepare_niche_conference(evidence_file:str|Path, deep_file:str|Path,
                             output_dir:str|Path, *, approved_niche:str,
                             owner_approval_ref:str, max_video_cases:int=18)->dict:
    """Transform verified-metadata public search into deep *tasks*, never fake observations."""
    if not 3<=len(approved_niche.strip())<=120 or not 8<=len(owner_approval_ref.strip())<=160:
        raise ValueError("Niche and explicit owner approval reference required")
    if not 3<=max_video_cases<=60:
        raise ValueError("Bounded research scope 3..60 required")
    from cinefactory.research_intelligence.deep_video_intelligence import verify_deep_video_review
    evidence_path=Path(evidence_file).resolve(strict=True)
    deep_path=Path(deep_file).resolve(strict=True)
    evidence=_load(evidence_path);deep=_load(deep_path)
    if evidence.get("schema")!="cine.research.automated_evidence.v1":
        raise ValueError("Canonical research evidence required")
    if evidence.get("niche")!=approved_niche or deep.get("niche")!=approved_niche:
        raise ValueError("Owner-approved niche and collected evidence mismatch")
    if evidence.get("state")!="PUBLIC_EVIDENCE_READY_FOR_REVIEW":
        raise ValueError("Incomplete collector cannot seed production")
    verify_deep_video_review(deep_path)
    if Path(deep["source_evidence"]["path"]).resolve()!=evidence_path:
        raise ValueError("Deep research does not belong to public source")
    for item in evidence["source_files"].values():
        _require_same(item)
    sources=[_freeze(evidence_path),_freeze(deep_path)]
    reference_video_ids={v["video_id"] for v in deep["videos"]}
    candidates={}
    for ch in evidence["channels"]:
        for v in ch.get("sample_longform_videos",[]):
            video_id=v.get("video_id")
            if not isinstance(video_id,str) or not VID.fullmatch(video_id):
                continue
            if v.get("topic_title_alignment")!="ALL_NICHE_TITLE_TOKENS_PRESENT":
                continue
            candidate=candidates.setdefault(video_id,{
                "video_id":video_id,"url":v["video_url"],"title":v["title"],
                "channel_id":ch["channel_id"],"channel_name":ch["channel_name"],
                "source_channel_category":ch.get("category","UNKNOWN"),
                "source_age_proxy_days":v["video_age_days_proxy"],
                "source_approx_views":v["approx_views"],"duration_seconds":v["duration_seconds"],
                "thumbnail_verified":video_id in reference_video_ids,
                "current_evidence":"PUBLIC_METADATA_OR_THUMBNAIL_NOT_FULL_VIDEO",
                "full_video_inspection":"NOT_DONE",
                "script_screenplay":"UNKNOWN","acting_expression":"UNKNOWN",
                "camera_lenses":"UNKNOWN","shot_timing":"UNKNOWN",
                "sound_design":"UNKNOWN","visual_continuity":"UNKNOWN",
                "rights":"NOT_CLEARED",
                "timeline_worklist":[
                    {"segment":"opening_hook","range_seconds":[0,min(30,v["duration_seconds"])],
                     "questions":["What visually happens at each beat?","What makes the viewer stay? Evidence/timecode?"]},
                    {"segment":"setup_and_stakes","range_seconds":"REQUIRES_ACTUAL_SCENE_SEGMENTATION",
                     "questions":["Which original characters, goals, conflict, causality and emotional setup?"]},
                    {"segment":"payoff_and_resolution","range_seconds":"REQUIRES_ACTUAL_SCENE_SEGMENTATION",
                     "questions":["Show setup/payoff, acting, staging, audio, scene transition, ending logic"]},
                ],
                "rubric":[
                    "logline/hook/story beats and original twist",
                    "character acting: eye contact, expression, pose, lip-sync and body language",
                    "camera: framing, screen direction, blocking, movement and coverage",
                    "world: assets, lighting, material, continuity, physics and visible texture",
                    "sound: voice, foley, ambiance, music beats, sync and edit",
                    "visual packaging: thumbnail, title, readable focal point and originality"],
            })
    # Cohort-balanced research: high performers, fresh videos, young entrants,
    # weak within-channel controls, mature leaders and diverse other channels.
    # This is sampling from a bounded public source, not a market-wide census.
    by_channel={}
    for candidate in candidates.values():
        by_channel.setdefault(candidate["channel_id"],[]).append(candidate["source_approx_views"])
    for candidate in candidates.values():
        peer=by_channel[candidate["channel_id"]]
        median=statistics.median(peer) if len(peer)>=3 else None
        candidate["relative_sample_views_ratio"]=round(candidate["source_approx_views"]/median,3) if median else None
        candidate["selection_reasons"]=[]
    ranked=list(candidates.values())
    buckets={
        "fresh_0_15d_million_signal":[x for x in ranked
          if isinstance(x["source_age_proxy_days"],(float,int))
          and 0<=x["source_age_proxy_days"]<=15 and x["source_approx_views"]>=1000000],
        "new_0_30d_channel_sample":[x for x in ranked
          if x["source_channel_category"]=="newcomer"],
        "established_leader":[x for x in ranked
          if x["source_channel_category"]=="mature_leader"],
        "relative_weak_control":[x for x in ranked
          if x["relative_sample_views_ratio"] is not None and x["relative_sample_views_ratio"]<=0.5],
        "other_evidence":[x for x in ranked],
    }
    for k in buckets:
        buckets[k].sort(key=lambda x:(-x["source_approx_views"],x["video_id"]))
    quotas={
        "fresh_0_15d_million_signal":4,
        "new_0_30d_channel_sample":4,
        "established_leader":4,
        "relative_weak_control":3,
        "other_evidence":max_video_cases,
    }
    chosen=[]
    seen=set()
    channel_count={}
    for kind in buckets:
        qty=0
        for v in buckets[kind]:
            if len(chosen)>=max_video_cases or qty>=quotas[kind]:break
            if v["video_id"] in seen:continue
            if channel_count.get(v["channel_id"],0)>=5:continue
            v["selection_reasons"].append(kind)
            chosen.append(v)
            seen.add(v["video_id"])
            channel_count[v["channel_id"]]=channel_count.get(v["channel_id"],0)+1
            qty+=1
    sampling={
        "policy":"BOUNDED_COHORT_BALANCED_NOT_MARKET_WIDE",
        "total_available":len(ranked),
        "selected":len(chosen),
        "independent_channels_selected":len(channel_count),
        "selected_by_first_reason":{k:sum(k in x["selection_reasons"] for x in chosen) for k in buckets},
        "weak_control_availability":len(buckets["relative_weak_control"]),
        "newcomer_availability":len(buckets["new_0_30d_channel_sample"]),
        "missing_controls_need_more_search":len(buckets["relative_weak_control"])<2,
        "no_causal_claims":True,
    }
    families=_canon(approved_niche)
    lanes=sorted(LANES.keys())
    tasks={
        "schema":"cine.studio.production_conference.v1",
        "state":"FULL_VIDEO_STUDIES_REQUIRED",
        "approved_niche":approved_niche,"owner_approval_ref":owner_approval_ref,
        "owner_approval_authenticated":False,
        "demonstration_only":owner_approval_ref.startswith("DEMO_ONLY"),
        "research_sources":sources,
        "canonical_issue_id":(deep.get("canonical_council_issue") or {}).get("issue_id"),
        "source_research_age":"SNAPSHOT_ONLY_NO_AUTO_VALIDITY",
        "niche_family":families or "CUSTOM",
        "video_cases":chosen,"video_case_count":len(chosen),
        "sampling_coverage":sampling,
        "required_stages":[{"id":stage,"deliverable":what,"state":"PENDING"} for stage,what in STAGES],
        "core_quality_dimensions":list(DIMENSIONS),
        "tool_candidates":[{
            "lane":lane,**meta,
            "state":"CANDIDATE_REQUIRES_RUNTIME_AND_PILOT_BENCHMARK"
        } for lane,meta in TOOL_CATALOG.items()],
        "hard_reference_rules":[
            "Full video annotation requires lawfully obtained, authorized footage and real frame timestamps",
            "Do not infer script/dialogue/camera from title, transcript alone or thumbnail",
            "Public views/age are approximate, private CTR/retention/RPM are UNKNOWN",
            "Pick separate leading AND weaker comparable videos; title ranking is not causal proof",
            "Derive production style and technique, not reproduce protected characters, dialogue, or script",
            "Test all short-listed tools on the SAME difficult scene with identical acceptance rubric",
            "Quality comparison without actual verified pilot renders is strictly NOT_PERFORMED"],
        "scene_trial_matrix":[
            {"scenario":"hero_expression_dialogue","primary":"blender_character_animation",
             "alternatives":["unreal_realtime_cinematic","comfyui_controlled_ai_video"],
             "hard_gates":["identity_continuity","acting_expression","camera","sound"]},
            {"scenario":"environment_transition_camera","primary":"comfyui_controlled_ai_video",
             "alternatives":["blender_character_animation","unreal_realtime_cinematic"],
             "hard_gates":["world_art","lighting_render","motion_stability","camera"]},
            {"scenario":"edited_30_second_sequence","primary":"resolve_master_finishing",
             "alternatives":["remotion_graphics"],"hard_gates":["edit_pacing","sound","story"]},
        ] if families in ("minecraft_animation","roblox_animation") else [],
        "method_selection_policy":"PILOT_EVIDENCE_QUALITY_GATE_THEN_OPTIMIZE_ACCEPTED_SECONDS_PER_HOUR",
        "quality_target":"MATCH_OR_SURPASS_OBSERVED_COMPETITOR_ON_UNITS_WITH_COMPARABLE_EVIDENCE",
        "source_rights_status":"UNVERIFIED",
        "deep_content_analysis_completed":False,
        "tool_benchmark_completed":False,
        "choice_approved":False,
        "production_permission":False,
    }
    target=Path(output_dir).resolve()
    if target.exists():raise FileExistsError("Immutable production conference destination exists")
    target.mkdir(parents=True)
    (target/"conference.json").write_text(json.dumps(tasks,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    # Editable researcher checklist is an artifact; NOT automatically reviewed.
    inspection={
        "schema":"cine.studio.inspection_sheet.v1",
        "niche":approved_niche,"state":"MANUAL_OR_MULTIMODAL_REVIEW_PENDING",
        "video_annotations":[],
        "instructions":"Only add FULL_VIDEO_DIRECT_OBSERVATION when video frames+sound were actually inspected with exact timecodes and source permission.",
        "cross_video_hypotheses":[],
        "unsolved_questions":["Why are exact videos outperforming cohort? Need comparable snapshots and actual inspected narratives."],
    }
    (target/"inspection_template.json").write_text(json.dumps(inspection,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return tasks


def _probe_actual_video(path:Path)->dict|None:
    """Confirm a real decodable moving-image stream; never trust filename alone."""
    if path.suffix.lower() not in (".mp4",".mov",".mkv",".webm"):
        return None
    try:
        completed=subprocess.run([
            "ffprobe","-v","error","-print_format","json",
            "-show_format","-show_streams",str(path)],
            capture_output=True,text=True,timeout=15,check=False)
        if completed.returncode!=0:return None
        payload=json.loads(completed.stdout)
        stream=next((x for x in payload.get("streams",[])
                     if x.get("codec_type")=="video" and x.get("width") and x.get("height")),None)
        if not stream:return None
        duration=float(stream.get("duration") or payload.get("format",{}).get("duration") or 0)
        return {"duration_seconds":duration,"width":int(stream["width"]),
                "height":int(stream["height"]),"codec":stream.get("codec_name","UNKNOWN")}
    except (OSError,ValueError,TypeError,subprocess.TimeoutExpired,json.JSONDecodeError):
        return None


def evaluate_comparable_pilots(conference_file:str|Path, trials_file:str|Path,
                               output_file:str|Path)->dict:
    """Advisory bake-off. Vague speed/model claims and missing media cannot win."""
    source=Path(conference_file).resolve(strict=True)
    trials=Path(trials_file).resolve(strict=True)
    conference=_load(source); data=_load(trials)
    if conference.get("schema")!="cine.studio.production_conference.v1" or data.get("schema")!="cine.studio.pilot_trials.v1":
        raise ValueError("Expected conference and pilot trial schemas")
    if data.get("conference_sha256")!=_digest(source):
        raise ValueError("Pilot trials do not match frozen conference revision")
    scenario_keys={x["scenario"] for x in conference["scene_trial_matrix"]}
    rows=[]; winners={}
    for candidate in data.get("trials",[]):
        if not isinstance(candidate,dict):raise ValueError("Malformed pilot trial")
        scenario=candidate.get("scenario")
        lane=candidate.get("lane")
        if scenario not in scenario_keys or lane not in TOOL_CATALOG:
            raise ValueError("Unknown scenario or tool lane")
        render=candidate.get("render_file")
        render_hash=candidate.get("render_sha256")
        measured=candidate.get("measured",{})
        source_media_verified=False
        decoded=None
        if isinstance(render,str) and isinstance(render_hash,str):
            p=Path(render).resolve(strict=True)
            if p.is_file() and _digest(p)==render_hash:
                source_media_verified=True
                decoded=_probe_actual_video(p)
            else:raise ValueError("Pilot render hash mismatch")
        values=measured.get("quality_scores",{})
        if not isinstance(values,dict):raise ValueError("Quality scores must be object")
        for k,v in values.items():
            if k not in DIMENSIONS or isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=1:
                raise ValueError("Invalid quality dimension or score")
        for name in ("render_wall_seconds","output_duration_seconds","human_rework_seconds"):
            x=measured.get(name)
            if x is not None and (isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x) or x<0):
                raise ValueError("Invalid timing measurement")
        hard=next((x["hard_gates"] for x in conference["scene_trial_matrix"] if x["scenario"]==scenario),[])
        qa=bool(measured.get("independent_quality_reviewed") and measured.get("rights_cleared"))
        valid_media=bool(decoded and decoded["width"]>=1280
                         and decoded["height"]>=720
                         and abs(decoded["duration_seconds"]-measured.get("output_duration_seconds",0))<=0.35)
        complete=(source_media_verified and valid_media and qa and all(g in values for g in hard)
                  and measured.get("output_duration_seconds",0)>0
                  and measured.get("render_wall_seconds",0)>0
                  and measured.get("human_rework_seconds") is not None)
        hard_pass=complete and all(values[g]>=0.85 for g in hard)
        if complete:
            total=measured["render_wall_seconds"]+measured["human_rework_seconds"]
            accepted_per_hr=round(3600*measured["output_duration_seconds"]/total,2) if total>0 else None
        else:accepted_per_hr=None
        record={
            "scenario":scenario,"lane":lane,
            "source_media_verified":source_media_verified,
            "video_stream_verified":bool(valid_media),
            "probed_video":decoded,
            "qa_and_rights_claim_declared":qa,
            "verification_note":"Reviewer identity and rights signoff still need authenticated provenance",
            "hard_gates":hard,
            "hard_gate_quality_pass":bool(hard_pass),
            "accepted_output_seconds_per_hour_proxy":accepted_per_hr if hard_pass else None,
            "status":"PILOT_CANDIDATE_FOR_HUMAN_REVIEW" if hard_pass
                     else "PILOT_INCOMPLETE_OR_HARD_GATE_FAILED",
            "model_or_tool_version":candidate.get("tool_version","UNKNOWN"),
            "rework_seconds":measured.get("human_rework_seconds"),
        }
        rows.append(record)
    for scenario in scenario_keys:
        eligible=[x for x in rows if x["scenario"]==scenario and x["hard_gate_quality_pass"]]
        if eligible:
            eligible.sort(key=lambda x:x["accepted_output_seconds_per_hour_proxy"] or 0,reverse=True)
            winners[scenario]={"advisory_fastest_meeting_quality":eligible[0]["lane"],
                               "needs_owner_review":True,
                               "runner_up_lanes":[x["lane"] for x in eligible[1:]]}
    result={
        "schema":"cine.studio.pilot_bakeoff.v1",
        "state":"PILOT_COMPARISON_ADVISORY" if winners else "NO_VERIFIED_ACCEPTABLE_PILOTS",
        "conference_path":str(source),"conference_sha256":_digest(source),
        "trial_path":str(trials),"trial_sha256":_digest(trials),
        "benchmarks":rows,"advisory_rankings":winners,
        "human_review_authenticated":False,
        "production_permission":False,
        "cannot_claim_competitor_superiority":True,
        "next_action":"Supply timecoded authorized competitor study, comparable original pilot renders, authenticated QA and decision.",
    }
    target=Path(output_file)
    if target.exists():raise FileExistsError("Immutable output exists")
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return result


def main()->int:
    import argparse
    parser=argparse.ArgumentParser(description="Evidence-first production research conference")
    sub=parser.add_subparsers(dest="cmd",required=True)
    p=sub.add_parser("prepare")
    p.add_argument("--evidence",required=True)
    p.add_argument("--deep-review",required=True)
    p.add_argument("--niche",required=True)
    p.add_argument("--owner-approval-ref",required=True)
    p.add_argument("--output-dir",required=True)
    p.add_argument("--max-video-cases",type=int,default=18)
    q=sub.add_parser("evaluate")
    q.add_argument("--conference",required=True)
    q.add_argument("--trials",required=True)
    q.add_argument("--output",required=True)
    args=parser.parse_args()
    if args.cmd=="prepare":
        res=prepare_niche_conference(args.evidence,args.deep_review,args.output_dir,
                                     approved_niche=args.niche,
                                     owner_approval_ref=args.owner_approval_ref,
                                     max_video_cases=args.max_video_cases)
        print(json.dumps({"state":res["state"],"video_cases":res["video_case_count"],
                          "tool_candidates":len(res["tool_candidates"]),
                          "deep_content_analysis_completed":res["deep_content_analysis_completed"],
                          "production_permission":False}))
    else:
        res=evaluate_comparable_pilots(args.conference,args.trials,args.output)
        print(json.dumps({"state":res["state"],"pilots":len(res["benchmarks"]),
                          "rankings":len(res["advisory_rankings"]),
                          "production_permission":False}))
    return 0


if __name__=="__main__":
    raise SystemExit(main())


def compile_conf_to_director(conference_file:str|Path, creative_brief_file:str|Path,
                             capability_registry_file:str|Path, output_file:str|Path,
                             *, bakeoff_file:str|Path|None=None)->dict:
    """Connect the ONE vetted research worklist to existing Studio Director.

    Conference planning does not auto-approve scripts, rigs, budgets or tools.
    """
    from cinefactory.production.studio_director import build_studio_production_plan
    conf=Path(conference_file).resolve(strict=True)
    conference=_load(conf)
    if conference.get("schema")!="cine.studio.production_conference.v1":
        raise ValueError("Canonical niche production conference required")
    brief_path=Path(creative_brief_file).resolve(strict=True)
    caps_path=Path(capability_registry_file).resolve(strict=True)
    brief=_load(brief_path)
    caps=_load(caps_path)
    if brief.get("niche")!=conference["approved_niche"]:
        raise ValueError("Director brief niche diverges from studied niche")
    if brief.get("competitor_research_revision")!=_digest(conf):
        raise ValueError("Director brief must cite the exact immutable conference revision")
    scored={}
    if bakeoff_file is not None:
        bakeoff=_load(Path(bakeoff_file).resolve(strict=True))
        if (bakeoff.get("schema")!="cine.studio.pilot_bakeoff.v1"
            or bakeoff.get("conference_sha256")!=_digest(conf)):
            raise ValueError("Pilot bake-off belongs to another conference")
        if bakeoff.get("state")=="PILOT_COMPARISON_ADVISORY":
            scored=bakeoff.get("advisory_rankings",{})
    output=Path(output_file)
    report=build_studio_production_plan(brief,caps,output)
    by_kind={"character_dialogue":"hero_expression_dialogue",
             "character_acting":"hero_expression_dialogue",
             "complex_interaction":"hero_expression_dialogue",
             "stylized_montage":"environment_transition_camera",
             "environment_insert":"environment_transition_camera",
             "cinematic_transition":"environment_transition_camera"}
    rows=[]
    for shot in report["shots"]:
        scenario=by_kind.get(shot["scene_kind"])
        alternative=scored.get(scenario)
        rows.append({
            "shot_id":shot["shot_id"],"scenario":scenario,
            "planned_lane":shot["primary_lane"],
            "bakeoff_advisory_lane":alternative.get("advisory_fastest_meeting_quality") if alternative else None,
            "research_vs_production_mismatch":"NOT_BENCHMARKED" if alternative is None else
                                               "ADVISORY_ONLY_NOT_ACTUATED",
            "must_validate_lipsync_expression_camera_and_identity":bool(shot["source_character_ids"]),
        })
    # Keep Studio Director schema and unapproved state; store companion source link.
    pack={
        "schema":"cine.studio.conference_director_link.v1",
        "state":"DIRECTOR_PLAN_AND_CONFERENCE_LINKED_REVIEW_PENDING",
        "conference_sha256":_digest(conf),"director_plan_sha256":_digest(output),
        "creative_brief_sha256":_digest(brief_path),
        "capability_registry_sha256":_digest(caps_path),
        "planning_state":report["state"],
        "shot_routes":rows,
        "owner_approval_authenticated":False,
        "production_permission":False,
        "quality_proven_against_competitors":False,
    }
    target=output.with_name(output.stem+"_research_link.json")
    if target.exists():raise FileExistsError("Research/director companion exists")
    target.write_text(json.dumps(pack,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return pack
