"""Timestamped competitor-style scene studies grounded in AUTHORIZED media samples.

Frame measurement ≠ content comprehension. Editorial annotations require named
scene evidence, a constrained time range, and explicit observational status.
Multi-video commonalities are HYPOTHESES, never causal audience metrics.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from cinefactory.research_intelligence.scene_measurement import measure_sampled_frames

CATEGORIES={
 "script_hook","story_beats","character_expression","body_acting","camera_blocking",
 "lighting_art","set_props","sound_foley","voice_lipsync","editing_transitions",
 "thumbnail_packaging","visual_effects","pacing_reaction",
}


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path):
    x=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(x,dict):raise ValueError("Expected JSON object")
    return x


def prepare_timestamped_study(deep_video_manifest:str|Path, output:str|Path)->dict:
    """Create objective scene-review worklist from *actual* sampled frames/audio."""
    file=Path(deep_video_manifest).resolve(strict=True)
    data=_read(file)
    if data.get("schema")!="cine.research.authorized_deep_observation.v1":
        raise ValueError("Owned/licensed local video observation manifest required")
    obs=Path(data["observation_path"]).resolve(strict=True)
    measures=Path(data["scene_measurement_path"]).resolve(strict=True)
    original=_read(obs);stats=_read(measures)
    if stats.get("schema")!="cine.research.scene_measurement.v1" or stats["source_observation_path"]!=str(obs):
        raise ValueError("Scene measurement and observed footage provenance mismatch")
    if stats["observation_sha256"]!=_digest(obs):
        raise ValueError("Original observation modified")
    if stats["frame_count"]!=data.get("frames_observed"):
        raise ValueError("Frame count inconsistent")
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        computed=measure_sampled_frames(obs,Path(td)/"replay.json")
        if computed["samples"]!=stats["samples"]:
            raise ValueError("Scene pixel facts do not replay")
    media=Path(data["source_file"]).resolve(strict=True)
    if not media.is_file():
        raise ValueError("Authorized source media missing")
    frames=[]
    for point in stats["samples"]:
        frames.append({
            "sample_id":point["sample_id"],"second":point["second"],
            "image_sha256":point["sha256"],
            "brightness_0_255":point["mean_luminance_0_255"],
            "change_from_previous_0_1":point["change_from_previous_sample_0_1"],
            "visible_action":"UNKNOWN_REQUIRES_VISUAL_INSPECTION",
            "camera":"UNKNOWN_REQUIRES_VISUAL_INSPECTION",
            "sound_at_timestamp":"UNKNOWN_REQUIRES_AUDIO_INSPECTION",
        })
    result={
        "schema":"cine.studio.timestamped_scene_study.v1",
        "state":"OBSERVED_PIXELS_ANNOTATIONS_PENDING",
        "source_observation":str(obs),"observation_sha256":_digest(obs),
        "measurement":str(measures),"measurement_sha256":_digest(measures),
        "source_media":str(media),"source_media_sha256":_digest(media),
        "video_id":data["video_id"],"niche":data["niche"],
        "source_permission_declared":data["authorization_claim"],
        "source_rights_authenticated":False,
        "frame_evidence":frames,"human_annotations":[],
        "audit_questions_by_department":{
            "script":["What changes in character objective and stakes each beat?",
                      "What setup/payoff is visually/audibly supported?"],
            "director":["How do blocking, eye-line, camera distance and reaction shots serve emotion?",
                        "Does each cut clarify a new idea?"],
            "animation":["Which expression, pose timing, anticipation, secondary motion and lip-sync are visible?"],
            "art":["Do rig proportions, materials, locations, lighting, costume and props remain consistent?"],
            "audio":["Are voice, ambience, foley and music timed to actions? No claims from visuals alone."],
            "editorial":["Cut timings, hold lengths, sound bridges, time between reactions, rhythm changes"],
            "quality":["Which sampled frames fail continuity? What is genuinely unobserved?"],
        },
        "observed_full_video_story":False,
        "audio_semantics_understood":False,
        "causal_viral_success_proven":False,
        "eligible_for_production_strategy":False,
    }
    target=Path(output)
    if target.exists():raise FileExistsError("Immutable timestamped study already exists")
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return result


def validate_editorial_annotations(study_file:str|Path, annotation_file:str|Path,
                                   output_file:str|Path)->dict:
    """Reject invented frame references and unsupported full-video claims."""
    study_path=Path(study_file).resolve(strict=True)
    notes_path=Path(annotation_file).resolve(strict=True)
    study=_read(study_path);notes=_read(notes_path)
    if study.get("schema")!="cine.studio.timestamped_scene_study.v1":
        raise ValueError("Timestamped direct media evidence required")
    if notes.get("schema")!="cine.studio.direct_frame_annotations.v1":
        raise ValueError("Only direct frame annotations accepted")
    if notes.get("study_sha256")!=_digest(study_path):
        raise ValueError("Reviewer notes belong to different study revision")
    anchors={x["sample_id"]:x for x in study["frame_evidence"]}
    supported=[]
    for item in notes.get("observations",[]):
        if not isinstance(item,dict) or item.get("category") not in CATEGORIES:
            raise ValueError("Unknown category")
        key=item.get("sample_id")
        if key not in anchors or item.get("second")!=anchors[key]["second"]:
            raise ValueError("Invented or inconsistent video timestamp")
        value=item.get("description")
        if not isinstance(value,str) or not 15<=len(value.strip())<=600:
            raise ValueError("Meaningful direct visual observation required")
        if item.get("modality")!="VISIBLE_FRAME" or item.get("scope")!="DIRECT_OBSERVATION":
            raise ValueError("Sparse frames cannot prove audio or full-video narrative")
        supported.append({
            "sample_id":key,"second":item["second"],"category":item["category"],
            "description":value.strip(),"scope":"REVIEWER_DECLARED_DIRECT_VISIBLE",
            "image_sha256":anchors[key]["image_sha256"],
        })
    report={
        "schema":"cine.studio.scene_annotation_audit.v1",
        "state":"HUMAN_VISUAL_REVIEW_CLAIMS_UNAUTHENTICATED" if supported else "NO_DIRECT_SCENE_NOTES",
        "source_study_sha256":_digest(study_path),
        "video_id":study["video_id"],"niche":study["niche"],
        "annotations":supported,"annotation_count":len(supported),
        "narrative_understanding":"PARTIAL_FRAME_NOT_FULL_VIDEO",
        "independent_reviewer_authenticated":False,
        "multi_video_pattern_proven":False,
        "production_permission":False,
    }
    output=Path(output_file)
    if output.exists():raise FileExistsError("Do not rewrite scene evidence audit")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return report
