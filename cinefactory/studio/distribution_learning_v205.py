"""Authorized YouTube release/analytics contracts, owner-safe by default."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .longform_acceptance_v205 import sha256_stream


def build_release_intent(master_path, channel_id, metadata, independent_qc):
    movie=Path(master_path).resolve(strict=True)
    if not channel_id or not str(channel_id).startswith("UC"):
        raise ValueError("OWNED_CHANNEL_ID_REQUIRED")
    digest=sha256_stream(movie)
    if independent_qc.get("release_permission") is not True:
        return {"state":"BLOCKED_INDEPENDENT_QC","upload_authorized":False,
                "master_sha256":digest,"channel_id":channel_id}
    if independent_qc.get("master_sha256")!=digest:
        raise PermissionError("QC_DOES_NOT_MATCH_MASTER_HASH")
    if not metadata.get("title") or not metadata.get("description"):
        raise ValueError("TRUTHFUL_RELEASE_METADATA_REQUIRED")
    if metadata.get("visibility")!="private":
        raise PermissionError("MANDATORY_PRIVATE_FIRST_UPLOADING")
    if type(metadata.get("made_for_kids")) is not bool:
        raise PermissionError("EXPLICIT_YOUTUBE_KIDS_AUDIENCE_DECLARATION_REQUIRED")
    metadata_digest=hashlib.sha256(json.dumps(
        metadata,sort_keys=True,separators=(",",":"),
        ensure_ascii=False).encode("utf8")).hexdigest()
    return {"schema":"cine.youtube.release_intent.v205",
            "state":"AWAITING_OWNER_AUTHENTICATION",
            "upload_authorized":False,
            "master_path":str(movie),"master_sha256":digest,
            "channel_id":channel_id,"metadata":dict(metadata),
            "metadata_sha256":metadata_digest}


def upload_private_with_approval(intent, owner_approval, transport, *,
                                 trusted_owner_public_key,
                                 idempotency_reservation=None):
    """Transport must implement upload_private and fetch_video using owned OAuth.

    A caller-supplied 'approved' boolean is NOT trusted. The gateway must
    validate signed approval independently before supplying an object with
    cryptographically authenticated authority and exact-content binding.
    """
    if intent.get("schema")!="cine.youtube.release_intent.v205":
        raise PermissionError("RELEASE_NOT_QC_QUALIFIED")
    if intent.get("state")!="AWAITING_OWNER_AUTHENTICATION":
        raise PermissionError("NOT_READY_FOR_OWNER_APPROVAL")
    # Never trust a caller-provided cryptographically_verified=True flag.
    # Verify the original owner's Ed25519 signature inside this boundary.
    if not isinstance(owner_approval,dict):
        raise PermissionError("SIGNED_OWNER_APPROVAL_REQUIRED")
    event=owner_approval
    data=event.get("payload",{})
    if event.get("schema")!="cine.owner.youtube_private_upload.v205":
        raise PermissionError("OWNER_RELEASE_SIGNATURE_SCHEMA_REQUIRED")
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.hazmat.primitives import serialization
    import base64
    public_key=serialization.load_pem_public_key(
        Path(trusted_owner_public_key).resolve(strict=True).read_bytes()
    )
    if not isinstance(public_key,Ed25519PublicKey):
        raise PermissionError("OWNER_SIGNATURE_ALGORITHM_NOT_ED25519")
    signed_bytes=json.dumps(data,sort_keys=True,separators=(",",":"),
                            ensure_ascii=False).encode("utf8")
    public_key.verify(base64.b64decode(event["signature_b64"],validate=True),signed_bytes)
    from datetime import datetime,timezone
    canonical_metadata_hash=hashlib.sha256(json.dumps(
        intent["metadata"],sort_keys=True,separators=(",",":"),
        ensure_ascii=False).encode("utf8")).hexdigest()
    if (canonical_metadata_hash!=intent.get("metadata_sha256")
            or data.get("metadata_sha256")!=canonical_metadata_hash
            or data.get("master_sha256")!=intent["master_sha256"]
            or data.get("channel_id")!=intent["channel_id"]
            or data.get("scope")!="UPLOAD_PRIVATE_ONLY"
            or data.get("decision")!="APPROVED"):
        raise PermissionError("APPROVAL_SCOPE_DOES_NOT_MATCH_VIDEO")
    try:
        at=datetime.fromisoformat(data["issued_at"].replace("Z","+00:00"))
        if at.tzinfo is None:
            raise ValueError("NAIVE_OWNER_RELEASE_TIMESTAMP")
        delta=abs((datetime.now(timezone.utc)-at).total_seconds())
    except (KeyError,ValueError,TypeError) as exc:
        raise PermissionError("OWNER_RELEASE_TIMESTAMP_NOT_VERIFIABLE") from exc
    if delta>3600:
        raise PermissionError("OWNER_PRIVATE_UPLOAD_APPROVAL_EXPIRED")
    if sha256_stream(intent["master_path"])!=intent["master_sha256"]:
        raise ValueError("FILM_CHANGED_AFTER_APPROVAL")
    # YouTube video inserts are non-idempotent. Reserve an immutable local
    # attempt BEFORE network I/O; on timeout/crash, reconcile using YouTube
    # before any retry rather than uploading an accidental duplicate.
    if idempotency_reservation is None:
        raise PermissionError("PERSISTED_ONCE_ONLY_UPLOAD_RESERVATION_REQUIRED")
    reservation=Path(idempotency_reservation).resolve()
    reservation.parent.mkdir(parents=True,exist_ok=True)
    with reservation.open("x",encoding="utf8") as stream:
        stream.write(json.dumps({
            "schema":"cine.youtube.upload_attempt_reserved.v205",
            "master_sha256":intent["master_sha256"],
            "metadata_sha256":intent["metadata_sha256"],
            "channel_id":intent["channel_id"],
            "state":"MAY_HAVE_BEEN_SENT_MANUAL_RECONCILIATION_REQUIRED",
        },ensure_ascii=False)+"\\n")
    if getattr(transport, "owned_channel_id", intent["channel_id"]) != intent["channel_id"]:
        raise PermissionError("OAUTH_TRANSPORT_CHANNEL_MISMATCH")
    video_id=transport.upload_private(intent["master_path"],intent["metadata"])
    if not video_id:
        raise RuntimeError("YOUTUBE_DID_NOT_RETURN_VIDEO_ID")
    receipt=transport.fetch_video(video_id)
    if (receipt.get("id")!=video_id or
            receipt.get("channel_id")!=intent["channel_id"] or
            receipt.get("privacy_status")!="private"):
        raise RuntimeError("YOUTUBE_PRIVATE_UPLOAD_VERIFICATION_FAILED")
    verified={
        "schema":"cine.youtube.private_upload_verified.v205",
        "video_id":video_id,"channel_id":intent["channel_id"],
        "privacy_status":"private","master_sha256":intent["master_sha256"],
        "metadata_sha256":intent["metadata_sha256"],
        "state":"UPLOADED_PRIVATE_VERIFIED",
        "published_publicly":False,
        "verified_at":datetime.now(timezone.utc).isoformat(),
        "source":"LIVE_AUTHORIZED_YOUTUBE_API_READBACK",
    }
    # Durable receipt is independent of the stage ledger: a crash between
    # provider readback and blackboard persistence cannot erase upload proof.
    receipt_file=reservation.with_suffix(".verified_receipt.json")
    with receipt_file.open("x",encoding="utf8") as stream:
        stream.write(json.dumps(verified,ensure_ascii=False,indent=2)+"\n")
    return verified


def ingest_owned_analytics(receipt, metrics_export, provenance):
    """Do not hallucinate CTR/retention/RPM; owner API reads must attest identity."""
    if (receipt.get("schema")!="cine.youtube.private_upload_verified.v205"
            or receipt.get("state")!="UPLOADED_PRIVATE_VERIFIED"):
        raise PermissionError("VERIFIED_OWNED_PUBLICATION_REQUIRED")
    if (not provenance.get("authenticated_provider_readback")
            or provenance.get("channel_id")!=receipt.get("channel_id")
            or provenance.get("video_id")!=receipt.get("video_id")
            or provenance.get("provider")!="YOUTUBE_ANALYTICS_API"):
        raise PermissionError("OWNED_CHANNEL_ANALYTICS_PROVENANCE_MISSING")
    if metrics_export.get("video_id")!=receipt["video_id"]:
        raise ValueError("ANALYTICS_VIDEO_ID_MISMATCH")
    allowed={"views","watch_minutes","estimated_revenue_usd",
             "impressions","impressions_ctr","average_view_duration_seconds"}
    if not isinstance(metrics_export.get("window_start"),str) or not isinstance(metrics_export.get("window_end"),str):
        raise ValueError("METRICS_DATE_WINDOW_REQUIRED")
    stats={}
    for name in allowed:
        val=metrics_export.get(name)
        if val is not None:
            if not isinstance(val,(int,float)) or isinstance(val,bool) or val<0:
                raise ValueError("INVALID_PLATFORM_METRIC:" + name)
            stats[name]=val
    return {
        "schema":"cine.youtube.owned_observations.v205",
        "channel_id":receipt["channel_id"],"video_id":receipt["video_id"],
        "master_sha256":receipt["master_sha256"],
        "window_start":metrics_export["window_start"],
        "window_end":metrics_export["window_end"],
        "metrics":stats,"status":"OBSERVED_NEEDS_CONTROLLED_INTERPRETATION",
        "learning_promoted":False,
        "source_provenance":dict(provenance),
    }
