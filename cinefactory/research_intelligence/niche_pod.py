"""Owner-approved niche activation; respects Company's existing portfolio gate.

A Research Pod is a durable work specification, NOT a running scheduler.
No existing company decisions, sources, or production files are altered.
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .core import _write_json
from .market_bridge import verify_imported_company_sources


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _utc(s: str) -> datetime:
    value = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("Owner approval timestamp must have timezone")
    return value.astimezone(timezone.utc)


def _key(value: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", str(value).lower().replace("_", "-")).strip("-")


def _company_gate(company_root: Path, request_file: Path) -> dict:
    validator = company_root / "scripts" / "validate_promotion_gate.py"
    rules = company_root / "05_portfolio" / "promotion_gate_rules.yaml"
    if not validator.is_file() or not rules.is_file():
        raise FileNotFoundError("Canonical Company Youtube promotion gate missing")
    proc = subprocess.run(
        [sys.executable, str(validator), "--rules", str(rules),
         "--request", str(request_file), "--json"],
        capture_output=True, text=True, timeout=30, check=False, cwd=str(company_root)
    )
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Company gate failed without parseable JSON") from exc
    if proc.returncode != 0 or result.get("valid") is not True:
        raise PermissionError("Canonical Company promotion gate rejected request: " +
                              "; ".join(result.get("errors", ["no explanation"])))
    import yaml  # reuse the already-installed validation dependency
    request = yaml.safe_load(request_file.read_text(encoding="utf-8"))
    if not isinstance(request, dict):
        raise ValueError("Malformed promotion request")
    if request.get("current_status") != "WATCHLIST" or request.get("requested_status") != "TEST_WITH_10_VIDEOS":
        raise PermissionError("Wrong promotion transition for new Research Pod")
    return request


def activate_research_pod(company_root: str | Path, bridge_file: str | Path,
                          gate_request: str | Path, owner_event_file: str | Path,
                          pod_root: str | Path, *, as_of: str | None = None) -> dict:
    """Create exactly one approved niche pod, with no automatic YouTube/Claude execution."""
    root = Path(company_root).resolve(strict=True)
    bridge_path = Path(bridge_file).resolve(strict=True)
    request_path = Path(gate_request).resolve(strict=True)
    owner_path = Path(owner_event_file).resolve(strict=True)
    if not request_path.is_relative_to(root):
        raise ValueError("Promotion request must originate inside Company Youtube")
    bridge_raw = bridge_path.read_bytes()
    request_raw = request_path.read_bytes()
    bridge = json.loads(bridge_raw)
    event = json.loads(owner_path.read_text(encoding="utf-8"))
    if bridge.get("schema") != "cine.bridge.company_snapshot.v1" or Path(bridge.get("source_project", "")).resolve() != root:
        raise ValueError("Only imported Company snapshot is supported")
    if bridge.get("triage", {}).get("status") != "AUDIT_READY" or not all(bridge["triage"].get("gates", {}).values()):
        raise PermissionError("Niche does not satisfy strict five-gate evidence audit")
    for source_key in ("channel_source", "video_source"):
        source = bridge.get(source_key) or {}
        path = Path(source.get("path", "")).resolve(strict=True)
        if not path.is_relative_to(root) or _hash_bytes(path.read_bytes()) != source.get("sha256"):
            raise ValueError("Company market sources changed since triage")
    # Do not trust a forged AUDIT_READY bridge merely because its source hashes still match.
    verify_imported_company_sources(bridge)
    request = _company_gate(root, request_path)
    if event.get("schema") != "cine.owner_approval.v1" or event.get("approved") is not True:
        raise PermissionError("Explicit owner approval event required")
    if not event.get("approval_id") or not event.get("approved_by") or not event.get("candidate_id"):
        raise ValueError("Approval identity/decision reference missing")
    if event["candidate_id"] != request.get("candidate_id"):
        raise ValueError("Candidate ID does not match promotion gate")
    if event.get("niche") != bridge["niche"] or event.get("format_key") != bridge["format_key"]:
        raise ValueError("Approval applies to a different niche or format")
    if event.get("bridge_sha256") != _hash_bytes(bridge_raw) or event.get("gate_sha256") != _hash_bytes(request_raw):
        raise ValueError("Approval does not match the reviewed evidence/gate revision")
    now = _utc(as_of) if as_of else datetime.now(timezone.utc)
    approval_time = _utc(event["approved_at"])
    age = (now - approval_time).total_seconds()
    if not 0 <= age <= 7 * 86400:
        raise PermissionError("Owner approval event is future-dated or older than 7 days")
    market_age = (now - _utc(bridge["as_of"])).total_seconds()
    if not 0 <= market_age <= 3 * 86400:
        raise PermissionError("Approval requires a fresh market research snapshot")
    slug = _key(bridge["niche"]) + "--" + _key(bridge["format_key"])
    if not slug or ".." in slug:
        raise ValueError("Invalid niche/format identifier")
    target = Path(pod_root).resolve() / slug
    plan = [
        {"job_id": "market-discovery", "owner": "research", "cadence": "daily",
         "purpose": "Preserve strict 0-30d channels, two distinct >=1M long-form videos and demand proof"},
        {"job_id": "leader-watch", "owner": "research", "cadence": "daily",
         "purpose": "Track established same-niche competitor uploads and age-normalized outliers"},
        {"job_id": "newcomer-watch", "owner": "research", "cadence": "daily",
         "purpose": "Find fresh independent 0-30d channel entrants and multiple breakout videos"},
        {"job_id": "fresh-video-watch", "owner": "research", "cadence": "daily",
         "purpose": "Check genuinely recent 0-15d million-view long-form videos; identify trend life-cycle"},
        {"job_id": "video-analysis", "owner": "visual_story_audio", "cadence": "on_verified_case",
         "purpose": "Evidence-grounded transcript, scene, sound, packaging; route to CineCouncil"},
        {"job_id": "production-feedback", "owner": "quality_growth", "cadence": "after_owned_publish",
         "purpose": "Link each CineFactory edit/QC to owner-authorized Analytics and experimental evidence"},
    ]
    manifest = {
        "schema": "cine.niche.pod.v1", "niche_id": slug,
        "niche": bridge["niche"], "format_key": bridge["format_key"],
        "candidate_id": request["candidate_id"],
        "approval_id": event["approval_id"], "approved_at": event["approved_at"],
        "source_company": str(root),
        "bridge_source": str(bridge_path), "bridge_sha256": _hash_bytes(bridge_raw),
        "promotion_request": str(request_path), "gate_sha256": _hash_bytes(request_raw),
        "watch_plan": plan, "work_items_total": len(plan),
        "state": "CONFIGURED_NOT_SCHEDULED",
        "owner_event_is_authenticated": False,
        "explanation": "Local approval record and gate valid; no UI identity attestation, scheduler, autonomous monitoring or paid model run",
        "claude_automatic_execution": False, "youtube_upload_enabled": False,
        "allowed_auto_policy_changes": False,
        "production_conference": {
            "schema": "cine.studio.pod_production_conference.v1",
            "state": "REQUIRES_VIDEO_SCENE_INSPECTION_AND_TOOL_BAKEOFF",
            "entrypoint": "cinefactory.production.niche_production_conference",
            "policy": "ONE_APPROVED_NICHE_ONE_SOURCE_RESEARCH_DOSSIER",
            "studies_required": [
                "popular longform leader videos",
                "recent leader outliers compared to their own age-normalized history",
                "newcomer breakout videos",
                "matched underperformer controls",
                "timecoded story/directing/acting/camera/sound/edit observations",
            ],
            "pilot_scenarios": [
                "difficult acting/identity continuity",
                "controlled cinematic environment/camera",
                "edited sequence with sound and color",
            ],
            "selection_rule": "HARD_QUALITY_AND_RIGHTS_FIRST_THEN_ACCEPTED_SECONDS_PER_HOUR",
            "schedule_state": "NOT_SCHEDULED",
            "tool_runtime_proven": False,
            "independent_quality_accepted": False,
            "production_permission": False,
        },
        "jobs": [{"job_id": job["job_id"], "status": "NOT_SCHEDULED"} for job in plan],
    }
    file = target / "pod.json"
    if file.exists():
        old = json.loads(file.read_text(encoding="utf-8"))
        immutable = ("schema", "niche_id", "approval_id", "bridge_sha256", "gate_sha256")
        if any(old.get(field) != manifest[field] for field in immutable):
            raise FileExistsError("Pod already exists with a different owner decision; use reviewed migration")
        return old
    _write_json(file, manifest)
    return manifest
