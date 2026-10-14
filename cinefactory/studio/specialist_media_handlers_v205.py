"""Dedicated media handler adapters: real owner media only, no generated placeholders."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from .company_runner import StageHandlerResult
from .contracts import ArtifactState, DepartmentId
from .specialist_media_lanes_v205 import LANES


def _studio(ctx):
    runtime = ctx.kernel
    return runtime.studio if hasattr(runtime, "studio") else runtime


def _root(ctx):
    if ctx.project_root is None:
        raise ValueError("SOURCE_MANIFEST_REQUIRES_PROJECT_DIRECTORY")
    return ctx.project_root.resolve()


def _write(ctx, key, value):
    s = _studio(ctx)
    project_id = ctx.blueprint.project.studio_project_id
    owner = DepartmentId(ctx.stage.owner)
    try:
        if s.blackboard.get(project_id, key).get("payload") == value:
            return
    except KeyError:
        pass
    s.blackboard.put(project_id, key, owner, value,
                     state=ArtifactState.VALIDATED)


def _read(ctx, key):
    return _studio(ctx).blackboard.get(
        ctx.blueprint.project.studio_project_id, key)["payload"]


def _blocked(message):
    return StageHandlerResult(ok=False, error=message)


def _ok(ctx, *keys, detail=None):
    return StageHandlerResult(ok=True, produced_artifacts=list(keys),
                              checkpoint_ref="blackboard://" + ctx.stage.stage_id,
                              detail=detail)


def _owned_path(root: Path, string: str):
    base = (root / "inputs").resolve()
    path = (base / string).resolve(strict=True)
    if not path.is_relative_to(base) or not path.is_file():
        raise PermissionError("ONLY_OWNED_PROJECT_INPUT_PATHS")
    return path


def _hash(path):
    digest=hashlib.sha256()
    with Path(path).open("rb") as stream:
        while data:=stream.read(1024*1024):
            digest.update(data)
    return digest.hexdigest()


def _ffprobe(path):
    p = subprocess.run(
        ["ffprobe","-v","error","-show_entries",
         "format=duration:stream=codec_type,width,height,channels",
         "-of","json",str(path)],capture_output=True,text=True,timeout=25,
    )
    if p.returncode:
        raise ValueError("MEDIA_PROBE_FAILED:" + p.stderr[-160:])
    return json.loads(p.stdout)


def niche_project_intake(ctx):
    name = ctx.blueprint.project.niche or ""
    if name not in LANES:
        return _blocked("UNKNOWN_MEDIA_LANE")
    project = ctx.blueprint.project
    _write(ctx, "niche_project_brief", {
        "niche": name, "project_id": project.studio_project_id,
        "purpose": project.prompt, "mode": "OWNED_MEDIA_ONLY",
        "production_permission": False,
    })
    return _ok(ctx, "niche_project_brief")


def niche_research_review(ctx):
    # The only recognized input is an immutable, separately approved work order.
    path = _root(ctx) / "inputs" / "approved_studio_work_order.json"
    if not path.is_file():
        return _blocked("MISSING_APPROVED_RESEARCH_TO_STUDIO_WORK_ORDER")
    from .research_studio_handoff_v205 import verify_studio_work_order
    import os
    owner_key = os.environ.get("CINEFACTORY_OWNER_TRUST_PUBKEY")
    if not owner_key:
        return _blocked("AUTHENTICATED_OWNER_TRUST_KEY_NOT_CONFIGURED")
    try:
        result = verify_studio_work_order(path, trusted_public_key=owner_key)
    except (ValueError, OSError, KeyError, PermissionError) as exc:
        return _blocked("APPROVAL_VERIFICATION_FAILED:" + str(exc)[:120])
    if not result["production_permission"]:
        return _blocked("WORK_ORDER_NOT_AUTHORIZED:" + result["state"])
    if result["niche"] != ctx.blueprint.project.niche:
        return _blocked("WORK_ORDER_NICHE_MISMATCH")
    if result["project_id"] != ctx.blueprint.project.studio_project_id:
        return _blocked("WORK_ORDER_PROJECT_ID_MISMATCH")
    if (result["pilot_only"] is not True or not ctx.blueprint.pilot_only
            or (ctx.blueprint.project.duration_seconds or 0) not in range(30,61)):
        return _blocked("SIGNED_FULL_EPISODE_APPROVAL_REQUIRED_AFTER_PILOT")
    if _hash(path)!=ctx.blueprint.approved_pilot_work_order_sha256:
        return _blocked("SIGNED_PILOT_WORKORDER_CHANGED_AFTER_BLUEPRINT")
    _write(ctx, "verified_niche_dossier", result)
    return _ok(ctx, "verified_niche_dossier")


def niche_format_direction(ctx):
    name = ctx.blueprint.project.niche
    evidence = _read(ctx, "verified_niche_dossier")
    if evidence.get("state") != "OWNER_PRODUCTION_APPROVED_VERIFIED":
        return _blocked("RESEARCH_NOT_VERIFIED")
    _write(ctx, "original_format_plan", {
        "niche": name, "media_intent": LANES[name]["content"],
        "media_required": LANES[name]["media"],
        "technical_gates": LANES[name]["technical"],
        "independent_human_gates": LANES[name]["human"],
        "reuse_competitor_expression": False,
        "ready_for_filming": False,
    })
    return _ok(ctx, "original_format_plan")


def _signed_decision(event: dict, trusted_public_key: str, expected: dict) -> bool:
    """Validate exact owner/reviewer decision without accepting self-nominated keys."""
    import base64
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.hazmat.primitives import serialization
    from cryptography.exceptions import InvalidSignature
    if not trusted_public_key:
        raise PermissionError("TRUSTED_INDEPENDENT_REVIEW_KEY_NOT_CONFIGURED")
    payload=event.get("payload")
    if not isinstance(payload,dict) or any(payload.get(k)!=v for k,v in expected.items()):
        raise PermissionError("DECISION_NOT_BOUND_TO_EXACT_SOURCE")
    key=serialization.load_pem_public_key(Path(trusted_public_key).resolve(strict=True).read_bytes())
    if not isinstance(key,Ed25519PublicKey):
        raise ValueError("ONLY_ED25519_REVIEW_KEYS_ACCEPTED")
    key.verify(base64.b64decode(event["signature_b64"],validate=True),
               json.dumps(payload,sort_keys=True,separators=(",",":"),
                          ensure_ascii=False).encode("utf8"))
    return True


def niche_rights_and_sources(ctx):
    base = _root(ctx)
    path = base / "inputs" / "media_manifest.json"
    if not path.is_file():
        return _blocked("ORIGINAL_MEDIA_MANIFEST_MISSING")
    try:
        obj = json.loads(path.read_text(encoding="utf8"))
        if obj.get("schema") != "cine.owner_media.v205":
            raise ValueError("UNSUPPORTED_SOURCE_SCHEMA")
        if obj.get("niche") != ctx.blueprint.project.niche:
            raise ValueError("SOURCE_NICHE_MISMATCH")
        clips = obj.get("clips")
        if not isinstance(clips,list) or not clips:
            raise ValueError("NO_SOURCE_CLIPS")
        normalized = []
        for item in clips:
            p = _owned_path(base,item["file"])
            if p.suffix.lower() not in (".mp4",".mov",".mkv"):
                raise ValueError("NOT_VIDEO_SOURCE")
            if _hash(p) != item["sha256"]:
                raise ValueError("SOURCE_HASH_MISMATCH")
            rights = _owned_path(base,item["rights_evidence"])
            if _hash(rights) != item["rights_sha256"]:
                raise ValueError("RIGHTS_EVIDENCE_HASH_MISMATCH")
            if item.get("license_scope") not in ("OWNED_ORIGINAL","LICENSED_COMMERCIAL"):
                raise ValueError("COMMERCIAL_LICENSE_NOT_STATED")
            info = _ffprobe(p)
            if not any(s.get("codec_type") == "video" for s in info.get("streams",[])):
                raise ValueError("SOURCE_NO_VIDEO")
            if not any(s.get("codec_type") == "audio" for s in info.get("streams",[])):
                raise ValueError("SOURCE_NO_AUDIO")
            normalized.append({"file":str(p),"sha256":item["sha256"],
                               "rights":str(rights),"rights_sha256":item["rights_sha256"],
                               "license_scope":item["license_scope"],
                               "duration_seconds":float(info["format"]["duration"])})
        certificate=base/"inputs"/"rights_authorization.json"
        if not certificate.is_file():
            return _blocked("INDEPENDENT_RIGHTS_REVIEW_PENDING")
        from os import environ
        review_key=environ.get("CINEFACTORY_RIGHTS_TRUST_PUBKEY","")
        review=json.loads(certificate.read_text(encoding="utf8"))
        if review.get("schema")!="cine.rights.signed_clearance.v205":
            raise ValueError("INVALID_INDEPENDENT_RIGHTS_CERTIFICATE")
        _signed_decision(review,review_key,{
            "manifest_sha256":_hash(path),
            "niche":ctx.blueprint.project.niche,
            "project_id":ctx.blueprint.project.studio_project_id,
            "decision":"CLEAR_ORIGINAL_LOCAL_PRODUCTION",
            "scope":"PROJECT_ONLY",
        })
        _write(ctx, "media_source_manifest", {
            "schema":"cine.source_verified_local.v205","clips":normalized,
            "manifest_sha256":_hash(path)})
        _write(ctx, "source_clearance", {
            "state":"INDEPENDENTLY_CLEARED",
            "clips_checked":len(normalized),"production_permission":True,
            "rights_status":"SIGNED_INDEPENDENT_MANIFEST_REVIEW",
            "source_hash":_hash(path)})
        return _ok(ctx,"source_clearance","media_source_manifest")
    except (ValueError,KeyError,PermissionError,OSError,subprocess.TimeoutExpired) as ex:
        return _blocked("SOURCE_REVIEW_FAILED:" + str(ex)[:160])


def niche_media_assembly(ctx):
    clearance = _read(ctx,"source_clearance")
    if clearance.get("state") != "INDEPENDENTLY_CLEARED":
        return _blocked("SOURCE_RIGHTS_NOT_INDEPENDENTLY_CLEARED")
    media=_read(ctx,"media_source_manifest")
    clips=media.get("clips",[])
    if not clips or not ctx.blueprint.portfolio_greenlight.approved_for_production:
        return _blocked("NICHE_NOT_GREENLIT_FOR_PRODUCTION")
    for row in clips:
        if _hash(row["file"])!=row["sha256"] or _hash(row["rights"])!=row["rights_sha256"]:
            return _blocked("SOURCE_FILE_CHANGED_AFTER_RIGHTS_REVIEW")
    project_root=_root(ctx)
    output=project_root/"master"/"niche_original_assembly.mp4"
    if output.exists():
        return _blocked("OUTPUT_EXISTS_REQUIRES_VERSIONED_NEW_RUN")
    output.parent.mkdir(parents=True,exist_ok=True)
    # Build a real contiguous media movie from the exact user-owned clips.
    # No loop, stock replacement, synthetic padding, or metered cloud API.
    cmd=["ffmpeg","-nostdin","-v","error","-n"]
    for row in clips:
        cmd.extend(["-i",row["file"]])
    filters=[]
    for i in range(len(clips)):
        filters.append(f"[{i}:v:0]scale=1920:1080:force_original_aspect_ratio=decrease,"
                       f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=24,setsar=1,"
                       f"format=yuv420p[v{i}]")
        filters.append(f"[{i}:a:0]aresample=48000,"
                       f"aformat=sample_fmts=fltp:channel_layouts=stereo[a{i}]")
    inputs="".join(f"[v{i}][a{i}]" for i in range(len(clips)))
    filters.append(inputs+f"concat=n={len(clips)}:v=1:a=1[v][a]")
    cmd.extend(["-filter_complex",";".join(filters),"-map","[v]","-map","[a]",
                "-c:v","libx264","-preset","veryfast","-crf","20",
                "-c:a","aac","-b:a","192k","-movflags","+faststart",str(output)])
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=14400)
        if p.returncode!=0 or not output.is_file():
            return _blocked("ORIGINAL_ASSEMBLY_FAILED:"+p.stderr[-170:])
        from .longform_acceptance_v205 import probe_film
        result=probe_film(output,min_seconds=1,max_seconds=24*3600)
        _write(ctx,"dailies",{"path":str(output),"sha256":result["sha256"],
                               "source_manifest_sha256":media["manifest_sha256"]})
        _write(ctx,"assembly_report",{
            "state":"REAL_SOURCE_ENCODED_PENDING_FILM_REVIEW",
            "clips":len(clips),"technical_probe":result,
            "reused_competitor_footage":False,"synthetic_padding":False})
        return _ok(ctx,"dailies","assembly_report",detail="REAL_MEDIA_FROM_APPROVED_OWNED_CLIPS")
    except (OSError,subprocess.TimeoutExpired,ValueError) as ex:
        return _blocked("ASSEMBLY_EXECUTION_FAILED:"+str(ex)[:150])


def niche_sound_quality(ctx):
    source=_read(ctx,"dailies")
    if _hash(source["path"])!=source["sha256"]:
        return _blocked("AUDIO_SOURCE_VIDEO_HASH_CHANGED")
    probe=_ffprobe(source["path"])
    audio=next((s for s in probe.get("streams",[]) if s["codec_type"]=="audio"),None)
    if not audio:return _blocked("SOUND_STREAM_ABSENT")
    _write(ctx,"sound_qc",{
        "state":"TECHNICAL_AUDIO_STREAM_PRESENT",
        "master_sha256":source["sha256"],
        "audio_channels":audio.get("channels"),
        "independent_subjective_listening":"PENDING",
        "pass_artistic_sound":False,
    })
    return _ok(ctx,"sound_qc")


def niche_film_qc(ctx):
    from os import environ
    from .longform_acceptance_v205 import probe_film,independent_film_acceptance
    source=_read(ctx,"dailies")
    declared=ctx.blueprint.project.duration_seconds
    target=float(declared or 540)
    # Real episode length must correspond to approved creative duration;
    # avoid 8 minutes of repeated filler just to pass timecode.
    min_secs=max(1,target*0.95)
    max_secs=target*1.10
    film=probe_film(source["path"],min_seconds=min_secs,max_seconds=max_secs)
    if source["sha256"]!=film["sha256"]:
        return _blocked("POST_ASSEMBLY_MASTER_TAMPERED")
    root=_root(ctx)
    reviews_path=root/"inputs"/"independent_film_reviews.json"
    trusted_path=environ.get("CINEFACTORY_FILM_REVIEW_TRUST_STORE")
    if not reviews_path.is_file() or not trusted_path:
        _write(ctx,"film_qc_report",film)
        return _blocked("SIX_SIGNED_INDEPENDENT_FILM_REVIEWS_REQUIRED")
    reviews=json.loads(reviews_path.read_text(encoding="utf8"))
    keys=json.loads(Path(trusted_path).resolve(strict=True).read_text(encoding="utf8"))
    acceptance=independent_film_acceptance(film,reviews,keys)
    _write(ctx,"film_qc_report",{"technical":film,"independent":acceptance})
    if not acceptance.get("release_permission"):
        return _blocked("FILM_INDEPENDENT_QC_NOT_APPROVED:"+acceptance["status"])
    _write(ctx,"approved_master",{
        "path":source["path"],"sha256":source["sha256"],
        "acceptance":acceptance,
    })
    return _ok(ctx,"film_qc_report","approved_master")


def niche_packaging(ctx):
    master=_read(ctx,"approved_master")
    if master.get("acceptance",{}).get("release_permission") is not True:
        return _blocked("INDEPENDENTLY_ACCEPTED_FILM_REQUIRED")
    path=_root(ctx)/"inputs"/"release_metadata.json"
    if not path.is_file():return _blocked("OWNER_RELEASE_METADATA_MISSING")
    meta=json.loads(path.read_text(encoding="utf8"))
    if (not meta.get("title") or not meta.get("description")
            or meta.get("visibility")!="private" or
            not meta.get("channel_id")
            or type(meta.get("made_for_kids")) is not bool):
        return _blocked("OWNER_METADATA_OR_PRIVATE_FIRST_REQUIRED")
    _write(ctx,"release_package",{"metadata":meta,
                                  "master":master,
                                  "status":"READY_FOR_AUTHENTICATED_PRIVATE_UPLOAD"})
    return _ok(ctx,"release_package")


def niche_publishing(ctx):
    release=_read(ctx,"release_package")
    from os import environ
    # Independent signed film quality decisions must remain valid at the
    # publication boundary, not merely at the earlier QC stage.
    master=release["master"]
    report=_read(ctx,"film_qc_report")
    film_evidence=report.get("technical") if isinstance(report,dict) else None
    if not isinstance(film_evidence,dict):
        return _blocked("MISSING_ORIGINAL_FILM_TECHNICAL_EVIDENCE")
    if (_hash(master["path"])!=master["sha256"]
            or film_evidence.get("sha256")!=master["sha256"]
            or film_evidence.get("technical_pass") is not True):
        return _blocked("MASTER_CHANGED_OR_FAILED_TECHNICAL_QC")
    trust_store=environ.get("CINEFACTORY_FILM_REVIEW_TRUST_STORE")
    review_file=_root(ctx)/"inputs"/"independent_film_reviews.json"
    if not trust_store or not review_file.is_file():
        return _blocked("SIGNED_FILM_RELEASE_REVIEW_UNAVAILABLE")
    try:
        from .longform_acceptance_v205 import independent_film_acceptance
        keys=json.loads(Path(trust_store).resolve(strict=True).read_text(encoding="utf8"))
        reviews=json.loads(review_file.read_text(encoding="utf8"))
        accepted=independent_film_acceptance(film_evidence,reviews,keys)
        if accepted.get("release_permission") is not True:
            return _blocked("SIGNED_FILM_REVIEW_NO_LONGER_VALID")
    except (OSError,ValueError,KeyError,TypeError):
        return _blocked("FILM_SIGNED_REVIEW_VERIFICATION_FAILED")
    key=environ.get("CINEFACTORY_OWNER_TRUST_PUBKEY")
    if not key:return _blocked("AUTHENTICATED_OWNER_TRUST_KEY_NOT_CONFIGURED")
    approval_path=_root(ctx)/"inputs"/"owner_private_upload_approval.json"
    if not approval_path.is_file():
        return _blocked("OWNER_PRIVATE_UPLOAD_APPROVAL_MISSING")
    transport=getattr(ctx.kernel,"youtube_oauth_transport",None)
    if transport is None:
        if environ.get("CINEFACTORY_ALLOW_PRIVATE_YT_UPLOAD")!="EXPLICIT_OWNER_OPT_IN":
            return _blocked("PRIVATE_YOUTUBE_UPLOAD_NOT_EXPLICITLY_ENABLED")
        token=environ.get("CINEFACTORY_GOOGLE_OAUTH_TOKEN")
        if not token:return _blocked("OWNED_YOUTUBE_OAUTH_TOKEN_NOT_CONFIGURED")
        from .youtube_oauth_transport_v205 import GoogleYouTubePrivateTransport
        try:
            transport=GoogleYouTubePrivateTransport(token)
        except Exception as ex:
            return _blocked("OWNED_OAUTH_CONNECTION_FAILED:"+type(ex).__name__)
        if transport.owned_channel_id!=release["metadata"]["channel_id"]:
            return _blocked("OAUTH_CHANNEL_DIFFERS_FROM_OWNER_RELEASE_TARGET")
    from .distribution_learning_v205 import build_release_intent,upload_private_with_approval
    master=release["master"]
    meta=release["metadata"]
    intent=build_release_intent(master["path"],meta["channel_id"],
                                meta,master["acceptance"])
    try:
        receipt=upload_private_with_approval(
            intent,json.loads(approval_path.read_text(encoding="utf8")),
            transport,trusted_owner_public_key=key,
            idempotency_reservation=(
                _root(ctx)/"company"/"private_upload_attempt_reservation.json"))
    except Exception as ex:
        return _blocked("AUTHORIZED_UPLOAD_FAILED:"+type(ex).__name__)
    _write(ctx,"publication_receipt",receipt)
    return _ok(ctx,"publication_receipt")


def niche_learning(ctx):
    receipt=_read(ctx,"publication_receipt")
    analytics=getattr(ctx.kernel,"youtube_analytics_transport",None)
    if analytics is None:
        from os import environ
        token=environ.get("CINEFACTORY_GOOGLE_ANALYTICS_OAUTH_TOKEN")
        if environ.get("CINEFACTORY_ENABLE_OWNED_ANALYTICS")!="EXPLICIT_OWNER_OPT_IN" or not token:
            return _blocked("OWNED_YOUTUBE_ANALYTICS_NOT_CONNECTED")
        from .youtube_oauth_transport_v205 import GoogleYouTubeOwnedAnalyticsTransport
        try:
            analytics=GoogleYouTubeOwnedAnalyticsTransport(
                token,receipt["channel_id"])
        except Exception as ex:
            return _blocked("OWNED_ANALYTICS_CONNECTION_FAILED:"+type(ex).__name__)
    try:
        source=analytics.fetch_owned_video_metrics(
            receipt["channel_id"],receipt["video_id"])
        from .distribution_learning_v205 import ingest_owned_analytics
        observations=ingest_owned_analytics(
            receipt,source["metrics"],source["provenance"])
    except Exception as ex:
        return _blocked("OWNED_METRICS_NOT_VERIFIED:"+type(ex).__name__)
    _write(ctx,"observations",observations)
    _write(ctx,"hypotheses",{"status":"AWAITING_CONTROLLED_EXPERIMENT",
                             "source_video":receipt["video_id"]})
    _write(ctx,"learning_candidates",{
        "status":"REVIEW_REQUIRED","promotable":False,
        "automatically_edited_company_rules":False,
    })
    return _ok(ctx,"observations","hypotheses","learning_candidates")


def register_specialist_handlers(registry):
    for key, method in {
        "NICHE_PROJECT_INTAKE":niche_project_intake,
        "NICHE_RESEARCH_REVIEW":niche_research_review,
        "NICHE_FORMAT_DIRECTION":niche_format_direction,
        "NICHE_RIGHTS_AND_SOURCES":niche_rights_and_sources,
        "NICHE_MEDIA_ASSEMBLY":niche_media_assembly,
        "NICHE_SOUND_QUALITY":niche_sound_quality,
        "NICHE_FILM_QC":niche_film_qc,
        "NICHE_PACKAGING":niche_packaging,
        "PUBLISHING":niche_publishing,
        "ANALYTICS_LEARNING":niche_learning,
    }.items():
        registry.register(key,method)
    return registry
