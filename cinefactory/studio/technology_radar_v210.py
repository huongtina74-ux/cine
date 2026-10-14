"""v210 research-only media technology radar with fail-closed legal and runtime gates.

A link, README or vendor claim is neither an installed executable, model
rights nor film-quality acceptance. CLI is read-only. No auto-install, no API.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from urllib.parse import urlsplit
from typing import Any

REGISTRY = Path(__file__).resolve().parents[2] / "config" / "technology" / "ai_media_radar_20261010.json"
PRIORITIES = frozenset({"P0", "P1", "RND", "HOLD"})
SOURCE_STATES = frozenset({
    "PUBLIC_SOURCE_REVIEWED_2026_10_10", "CATALOG_LEAD_REQUIRES_SOURCE_RECHECK",
})
RESTRICTED = {
    "minimax_h3": "TERRITORY_RESTRICTED_OUTPUT",
    "freevideo": "TERRITORY_RESTRICTED_OUTPUT",
    "hunyuan3d21": "TERRITORY_RESTRICTED_OUTPUT",
    "qwen_image21": "NONCOMMERCIAL_WEIGHT",
    "qwen_turbo": "NONCOMMERCIAL_WEIGHT",
    "anigen": "DEPENDENCY_NONCOMMERCIAL",
}
MUST_HAVE = {
    "minimax_h3", "comfyui", "freevideo", "fastvideo", "comfy_templates",
    "flux_klein4b", "qwen_image21", "qwen_turbo", "wan22", "ltx2",
    "unirig", "trellis2", "anigen", "audio2face", "moss", "qwen3tts",
    "chatterbox", "acestep", "ffmpeg", "hyperframes", "remotion",
    "runway", "veo", "kling", "seedance",
}

def load_technology_radar(path: Path | None = None) -> dict[str, Any]:
    file = Path(path or REGISTRY).resolve(strict=True)
    doc = json.loads(file.read_text(encoding="utf-8"))
    if doc.get("schema") != "cine.technology_radar.v210":
        raise ValueError("UNKNOWN_TECHNOLOGY_REGISTRY_SCHEMA")
    rows = doc.get("items")
    if not isinstance(rows, list) or doc.get("entry_count") != len(rows):
        raise ValueError("TECHNOLOGY_REGISTRY_COUNT_MISMATCH")
    ids: set[str] = set()
    for row in rows:
        required = (
            "id", "name", "category", "department", "official_or_project_url",
            "priority", "commercial_gate", "rtx3060_fit", "evidence_state",
            "local_runtime", "deploy_approved",
        )
        if not isinstance(row, dict) or any(f not in row for f in required):
            raise ValueError("TECHNOLOGY_RECORD_INCOMPLETE")
        key = row["id"]
        if not isinstance(key, str) or not key or key in ids:
            raise ValueError("TECHNOLOGY_ID_DUPLICATE_OR_INVALID")
        ids.add(key)
        u = urlsplit(row["official_or_project_url"])
        if u.scheme != "https" or not u.netloc or u.username or u.password:
            raise ValueError("TECHNOLOGY_SOURCE_LINK_NOT_HTTPS")
        if row["priority"] not in PRIORITIES:
            raise ValueError("TECHNOLOGY_PRIORITY_INVALID")
        if row["evidence_state"] not in SOURCE_STATES:
            raise ValueError("TECHNOLOGY_PROVENANCE_INVALID")
        if row["deploy_approved"] is not False:
            raise ValueError("UNSUPPORTED_AUTOMATIC_MODEL_DEPLOYMENT_APPROVAL")
        if key in RESTRICTED and row["commercial_gate"] != RESTRICTED[key]:
            raise ValueError("RESTRICTED_MODEL_LICENSE_GATE_MISMATCH:" + key)
    if not MUST_HAVE <= ids:
        raise ValueError("MISSING_CRITICAL_AI_PRODUCTION_CAPABILITIES")
    for key in ("allowed_to_auto_install", "production_changes_performed"):
        if doc.get(key) is not False:
            raise ValueError("PRODUCTION_OR_AUTOINSTALL_SIDE_EFFECT")
    if (type(doc.get("paid_api_credits_used")) is not int
            or doc["paid_api_credits_used"] != 0
            or type(doc.get("model_installations_performed")) is not int
            or doc["model_installations_performed"] != 0):
        raise ValueError("NONZERO_API_CREDITS_OR_MODEL_INSTALLATIONS")
    return doc

def summarize_technology_radar(
    doc: dict[str, Any], *, category: str | None = None,
    priority: str | None = None, include_items: bool = False,
) -> dict[str, Any]:
    if priority is not None and priority not in PRIORITIES:
        raise ValueError("TECHNOLOGY_PRIORITY_INVALID")
    all_rows = doc["items"]
    all_categories = {r["category"] for r in all_rows}
    if category is not None and category not in all_categories:
        raise ValueError("UNKNOWN_TECHNOLOGY_CATEGORY")
    filtered = [
        row for row in all_rows
        if (category is None or row["category"] == category)
        and (priority is None or row["priority"] == priority)
    ]
    counts = Counter(row["category"] for row in filtered)
    states = Counter(row["evidence_state"] for row in filtered)
    gates = Counter(row["commercial_gate"] for row in filtered)
    report = {
        "schema": "cine.technology_radar.readout.v210",
        "snapshot_date": doc["snapshot_date"],
        "registry_total": len(all_rows),
        "filtered_total": len(filtered),
        "categories": dict(sorted(counts.items())),
        "evidence_states": dict(sorted(states.items())),
        "commercial_gate_types": dict(sorted(gates.items())),
        "gpu": doc["primary_machine"],
        "production_models_deployed_in_this_update": 0,
        "new_models_benchmarked_on_user_gpu": 0,
        "cleared_for_automatic_production": 0,
        "can_prove_all_repos_on_internet_checked": False,
        "new_model_install_requires_owner_and_qualification": True,
    }
    if include_items:
        report["entries"] = filtered
    return report
