"""Research -> original-studio handoff with independent source and signed owner gate.

This verifies immutable local source bytes, strict thresholds, niche identity and
Ed25519 signature from an explicitly trusted operator key. It does not magically
verify truth of external YouTube APIs; external snapshot provenance must still
be independently audited before issuing the key's approval.
"""
from __future__ import annotations
import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

def _hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def _json(path):
    return json.loads(Path(path).read_text(encoding="utf8"))

def _canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf8")

def _timestamp(s):
    val=datetime.fromisoformat(s.replace("Z","+00:00"))
    if val.tzinfo is None:raise ValueError("RESEARCH_TIMESTAMP_MISSING_TZ")
    return val.astimezone(timezone.utc)

def validate_breakout_evidence(bundle: dict, *, at: datetime | None=None):
    """Independent arithmetic/provenance gates; never trusts a derived success flag."""
    now=at or datetime.now(timezone.utc)
    if bundle.get("schema")!="cine.research.source_bundle.v205":
        raise ValueError("INVALID_RESEARCH_EVIDENCE_SCHEMA")
    if bundle.get("source_tier")!="OFFICIAL_API_ARCHIVED_AND_HUMAN_REVIEWED":
        raise ValueError("OFFICIAL_SOURCE_AND_REVIEW_EVIDENCE_MISSING")
    if not bundle.get("source_digest_sha256") or not bundle.get("reviewer_evidence_id"):
        raise ValueError("SOURCE_LINEAGE_OR_REVIEWER_EVIDENCE_MISSING")
    channel=bundle.get("breakout_channel") or {}
    cid=channel.get("channel_id","")
    if not (isinstance(cid,str) and cid.startswith("UC") and len(cid)==24):
        raise ValueError("INVALID_YOUTUBE_CHANNEL_ID")
    age=(now-_timestamp(channel["created_at"])).total_seconds()/86400
    if not (0<=age<=30):
        raise ValueError("BREAKOUT_CHANNEL_OUTSIDE_30_DAYS")
    vids=channel.get("videos",[])
    if len({x.get("video_id") for x in vids})<2:
        raise ValueError("TWO_DISTINCT_LONG_FORM_VIDEOS_REQUIRED")
    eligible_ids=set()
    for v in vids:
        if (v.get("duration_seconds",0)>=480
                and v.get("views",0)>=1_000_000
                and v.get("channel_id")==cid
                and 0<=(now-_timestamp(v["published_at"])).total_seconds()/86400<=14
                and v.get("evidence_status")=="VERIFIED_OFFICIAL_API"):
            eligible_ids.add(v["video_id"])
    if len(eligible_ids)<2:
        raise ValueError("TWO_BREAKOUTS_WITHIN_14D_NOT_PROVED")
    established=bundle.get("evergreen_witnesses",[])
    if not established or not all(
        isinstance(x.get("video_id"),str) and x["video_id"]
        and isinstance(x.get("channel_id"),str) and x["channel_id"]!=cid
        and x.get("recent_views",0)>=100_000
        and x.get("evidence_status")=="VERIFIED_OFFICIAL_API"
        and 0<=(now-_timestamp(x["published_at"])).total_seconds()/86400<=90
        for x in established
    ):
        raise ValueError("RECENT_ESTABLISHED_DEMAND_NOT_PROVED")
    return {"niche":bundle["niche"],"breakout_channel":cid,
            "channel_age_days":round(age,3),"verified_breakout_count":len(eligible_ids),
            "established_witness_count":len(established)}


def create_studio_work_order(pod_file, evidence_file, owner_event_file,
                             trusted_public_key, destination, *, now=None,
                             expected_project_id=None):
    pod_path=Path(pod_file).resolve(strict=True)
    evidence_path=Path(evidence_file).resolve(strict=True)
    approval_path=Path(owner_event_file).resolve(strict=True)
    pod=_json(pod_path)
    evidence=_json(evidence_path)
    event=_json(approval_path)
    if pod.get("schema")!="cine.niche.pod.v1":
        raise ValueError("APPROVED_POD_SCHEMA_REQUIRED")
    if pod.get("niche")!=evidence.get("niche") or event.get("niche")!=pod["niche"]:
        raise ValueError("NICHE_HANDOFF_MISMATCH")
    if pod.get("state")!="CONFIGURED_NOT_SCHEDULED" or not pod.get("approval_id"):
        raise PermissionError("SOURCE_POD_NOT_APPROVED_FOR_RESEARCH")
    if pod.get("owner_event_is_authenticated"):
        # A true source-authenticated event still requires a separate production authorization.
        pass
    # Confirm that the pod's immutable imported market bridge remains intact.
    bridge=Path(pod["bridge_source"]).resolve(strict=True)
    if _hash(bridge)!=pod["bridge_sha256"]:
        raise ValueError("APPROVED_POD_BRIDGE_HASH_DRIFT")
    measured=validate_breakout_evidence(evidence,at=now)
    if event.get("schema")!="cine.owner.production_authorization.v205":
        raise PermissionError("WRONG_OWNER_AUTHORIZATION_SCHEMA")
    signed=event.get("payload")
    if not isinstance(signed,dict):
        raise ValueError("APPROVAL_PAYLOAD_REQUIRED")
    if any((
        signed.get("pod_sha256")!=_hash(pod_path),
        signed.get("evidence_sha256")!=_hash(evidence_path),
        signed.get("bridge_sha256")!=pod["bridge_sha256"],
        signed.get("niche")!=pod["niche"],
        signed.get("decision")!="APPROVE_ORIGINAL_PILOT_PRODUCTION",
        signed.get("project_id") in (None,""),
    )):
        raise PermissionError("AUTHORIZATION_DOES_NOT_BIND_EXACT_SOURCES")
    issued=_timestamp(signed["issued_at"])
    moment=now or datetime.now(timezone.utc)
    if abs((moment-issued).total_seconds())>24*3600:
        raise PermissionError("OWNER_AUTHORIZATION_EXPIRED")
    key_bytes=Path(trusted_public_key).resolve(strict=True).read_bytes()
    key=serialization.load_pem_public_key(key_bytes)
    if not isinstance(key,Ed25519PublicKey):
        raise ValueError("OWNER_TRUST_KEY_MUST_BE_ED25519")
    key.verify(base64.b64decode(event["signature_b64"],validate=True),_canonical(signed))
    if signed.get("output_mode")!="LOCAL_NO_METERED_API":
        raise PermissionError("NO_METERED_API_POLICY_REQUIRED")
    if expected_project_id is not None and signed.get("project_id")!=expected_project_id:
        raise PermissionError("SIGNED_PROJECT_ID_DOES_NOT_MATCH_DESTINATION")
    packet={
        "schema":"cine.studio.signed_work_order.v205",
        "state":"OWNER_PRODUCTION_APPROVED_VERIFIED",
        "niche":pod["niche"],"project_id":signed["project_id"],
        "source_pod_path":str(pod_path),"pod_sha256":_hash(pod_path),
        "source_evidence_path":str(evidence_path),"evidence_sha256":_hash(evidence_path),
        "bridge_sha256":pod["bridge_sha256"],
        "owner_authorization":signed,
        "owner_signature_b64":event["signature_b64"],
        "trusted_public_key_path":str(Path(trusted_public_key).resolve()),
        "source_arithmetic_verification":measured,
        "production_permission":True,
        "scope":"ORIGINAL_PILOT_ONLY_NOT_AUTOMATIC_RELEASE",
    }
    out=Path(destination)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("x",encoding="utf8") as f:
        f.write(json.dumps(packet,ensure_ascii=False,indent=2)+"\n")
    return packet


def verify_studio_work_order(path, *, trusted_public_key):
    """Revalidate work order against an operator-configured trust key."""
    if not trusted_public_key:
        raise PermissionError("OWNER_TRUST_KEY_NOT_CONFIGURED")
    o=_json(path)
    if o.get("schema")!="cine.studio.signed_work_order.v205":
        raise ValueError("WORK_ORDER_SCHEMA_UNSUPPORTED")
    pod=Path(o["source_pod_path"]).resolve(strict=True)
    evidence=Path(o["source_evidence_path"]).resolve(strict=True)
    if _hash(pod)!=o["pod_sha256"] or _hash(evidence)!=o["evidence_sha256"]:
        raise ValueError("UPSTREAM_SOURCE_CHANGED")
    pod_data=_json(pod)
    bridge_path=Path(pod_data["bridge_source"]).resolve(strict=True)
    if (_hash(bridge_path)!=pod_data["bridge_sha256"]
            or pod_data["bridge_sha256"]!=o["bridge_sha256"]):
        raise ValueError("APPROVED_SOURCE_BRIDGE_CHANGED")
    verified=validate_breakout_evidence(_json(evidence))
    issued=_timestamp(o["owner_authorization"]["issued_at"])
    if abs((datetime.now(timezone.utc)-issued).total_seconds())>24*3600:
        raise PermissionError("OWNER_WORK_ORDER_AUTHORIZATION_EXPIRED")
    event={
        "schema":"cine.owner.production_authorization.v205",
        "niche":o["niche"],
        "payload":o["owner_authorization"],
        "signature_b64":o["owner_signature_b64"],
    }
    # Verify the signature and immutable binding again; avoid writing a second output.
    owner=o["owner_authorization"]
    if any((owner.get("evidence_sha256")!=o["evidence_sha256"],
            owner.get("pod_sha256")!=o["pod_sha256"],
            owner.get("niche")!=o["niche"],
            owner.get("project_id")!=o["project_id"],
            owner.get("bridge_sha256")!=o["bridge_sha256"],
            owner.get("output_mode")!="LOCAL_NO_METERED_API",
            owner.get("decision")!="APPROVE_ORIGINAL_PILOT_PRODUCTION")):
        raise ValueError("OWNER_APPROVAL_BINDING_CHANGED")
    key=serialization.load_pem_public_key(Path(trusted_public_key).resolve(strict=True).read_bytes())
    if not isinstance(key,Ed25519PublicKey):raise ValueError("UNSUPPORTED_SIGNATURE_ALGORITHM")
    key.verify(base64.b64decode(event["signature_b64"],validate=True),_canonical(owner))
    if (o.get("production_permission") is not True
            or o.get("state")!="OWNER_PRODUCTION_APPROVED_VERIFIED"
            or o.get("scope")!="ORIGINAL_PILOT_ONLY_NOT_AUTOMATIC_RELEASE"):
        raise PermissionError("NO_UNBOUNDED_PRODUCTION_AUTHORITY")
    return {"state":o["state"],"niche":o["niche"],
            "project_id":o["project_id"],"production_permission":True,
            "pilot_only":True,"evidence_summary":verified}
