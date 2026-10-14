"""Opt-in mechanical full-video intake for owner/rights-authorized local media.

No third-party downloads. The caller must supply media with an explicit
permission declaration and expected SHA256. No automatic approval/release.
"""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path

from .media_mechanics import prepare_media_mechanics
from .deep_video_intelligence import observe_authorized_footage
from cinefactory.production.scene_study import prepare_timestamped_study

VID=re.compile(r"^[A-Za-z0-9_-]{11}$")
PERMISSIONS={"OWNED","LICENSED","SOURCE_OWNER_PERMISSION"}
MAX_MEDIA_BYTES=32*1024**3  # Upper input bound; expensive full-media QC remains deliberate.

def file_sha(path:Path):
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()


def process_niche_media(work_orders_file:str|Path, manifest_file:str|Path,
                        output_dir:str|Path, *, max_videos:int=3,
                        max_scan_seconds:int=600)->dict:
    if not 1<=max_videos<=20 or not 5<=max_scan_seconds<=3600:
        raise ValueError("Bounded local media inspection required")
    source=Path(work_orders_file).resolve(strict=True)
    manifest=Path(manifest_file).resolve(strict=True)
    jobs=json.loads(source.read_text(encoding="utf-8"))
    data=json.loads(manifest.read_text(encoding="utf-8"))
    if jobs.get("schema")!="cine.niche.work_orders.v1" or data.get("schema")!="cine.niche.authorized_media_manifest.v1":
        raise ValueError("Canonical research work orders and explicit local media manifest required")
    cases=data.get("cases")
    if not isinstance(cases,list) or len(cases)>60:raise ValueError("Bounded manifest required")
    wanted={x["video_id"] for x in jobs["lane_tasks"]}
    ordered=[];seen=set()
    for item in cases:
        if not isinstance(item,dict) or not isinstance(item.get("video_id"),str) or not VID.fullmatch(item["video_id"]):
            raise ValueError("Media entry must identify a real video ID")
        vid=item["video_id"]
        if vid in seen:raise ValueError("Duplicate media attachment")
        seen.add(vid)
        if vid not in wanted:continue
        if item.get("authorization") not in PERMISSIONS:
            raise PermissionError("No rights statement for attached video")
        if (not isinstance(item.get("permission_reference"),str)
            or len(item["permission_reference"].strip())<8):
            raise PermissionError("Meaningful permission audit reference required")
        path=Path(item.get("media_path","")).resolve(strict=True)
        if not path.is_file():
            raise ValueError("Media entry must reference a local regular file")
        if not 0<path.stat().st_size<=MAX_MEDIA_BYTES:
            raise ValueError("Media source has invalid size or exceeds bounded research budget")
        if file_sha(path)!=item.get("sha256"):
            raise ValueError("Local footage differs from declared source hash")
        ordered.append((vid,path,item))
    target=Path(output_dir).resolve()
    if target.exists():raise FileExistsError("Media intake output must be new and immutable")
    target.mkdir(parents=True)
    completed=[]
    for vid,path,item in ordered[:max_videos]:
        sub=target/vid
        analysis=prepare_media_mechanics(path,sub/"mechanics",permission=item["authorization"],
                                         max_scan_seconds=max_scan_seconds)
        # Detect replacement between first preflight hash and the FFmpeg probe;
        # do not let a different file proceed into frame extraction.
        if analysis.get("source_sha256")!=item["sha256"] or file_sha(path)!=item["sha256"]:
            raise RuntimeError("MEDIA_SOURCE_CHANGED_DURING_ANALYSIS")
        declared=("USER_PROVIDED_WITH_PERMISSION" if item["authorization"]=="SOURCE_OWNER_PERMISSION"
                  else item["authorization"])
        observed=observe_authorized_footage(
            path,sub/"frames",niche=str(jobs.get("niche_id") or "Unassigned research niche"),
            video_id=vid,authorization=declared,max_frames=12)
        study=prepare_timestamped_study(sub/"frames"/"deep_video_manifest.json",
                                         sub/"frame_study.json")
        if file_sha(path)!=item["sha256"]:
            raise RuntimeError("MEDIA_SOURCE_CHANGED_DURING_ANALYSIS")
        completed.append({"video_id":vid,"state":"MECHANICS_AND_SAMPLED_FRAMES_REVIEW_PENDING",
                          "mechanics_file":str(sub/"mechanics"/"media_mechanics.json"),
                          "timeline_sha256":analysis["timeline_sha256"],
                          "frame_study_file":str(sub/"frame_study.json"),
                          "frames_observed":len(study["frame_evidence"]),
                          "department_task_count":observed["department_task_count"],
                          "rights_claim_only":True,
                          "semantic_understanding_complete":False})
    result={
        "schema":"cine.niche.media_intake.v1",
        "state":"MECHANICS_READY_HUMAN_AND_VLM_REVIEW_PENDING" if completed else "NO_MATCHING_AUTHORIZED_MEDIA",
        "source_work_orders_sha256":file_sha(source),
        "media_manifest_sha256":file_sha(manifest),
        "candidate_video_ids":sorted(wanted),
        "matching_authorized_media":len(ordered),
        "mechanically_analyzed_video_count":len(completed),
        "video_analysis":completed,
        "source_rights_authenticated":False,
        "full_video_multimodal_semantics_complete":False,
        "independent_scene_reviewer_authenticated":False,
        "production_permission":False,
    }
    (target/"media_intake.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return result
