"""Read-only CineFactory company integrity/operations snapshot.

Never equate an installed tool, model placeholder or passing unit test with
commercial production quality or verified YouTube research.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cinefactory.studio.company import stage_blueprint
from cinefactory.studio.contract_integrity import audit_company_wiring
from cinefactory.studio.contracts import DepartmentId, MediaFormat
from cinefactory.studio.departments import DEFAULT_DEPARTMENTS
from cinefactory.studio.intake import NicheConfigStore
from cinefactory.research_intelligence.daily_research import daily_health

ROOT = Path(__file__).resolve().parents[1]
FORMATS = {
    "minecraft": MediaFormat.ANIMATION,
    "roblox_animation": MediaFormat.ANIMATION,
    "long_slices_game": MediaFormat.ANIMATION,
    "asmr_sleep_hands_objects": MediaFormat.DOCUMENTARY,
    "audio_storytelling_seniors": MediaFormat.PODCAST,
    "fishing_silent": MediaFormat.DOCUMENTARY,
    "rain_sleep_white_noise": MediaFormat.DOCUMENTARY,
}


def audit(root: Path = ROOT) -> dict:
    root = root.resolve()
    dept = {role.value for role in DepartmentId}
    configured = {role.value for role in DEFAULT_DEPARTMENTS}
    statuses = {}
    store = NicheConfigStore(root)
    for name, fmt in FORMATS.items():
        settings = root / "config" / "niches" / name
        if not settings.is_dir():
            statuses[name] = {"status": "CONFIG_NOT_FOUND"}
            continue
        readiness = store.readiness(name)
        blueprint = stage_blueprint(
            fmt, False, professional_governance=True,
            professional_niche=name,
        )
        wiring = audit_company_wiring(blueprint)
        statuses[name] = {
            "status": ("BLOCKED_STAGE_WIRING" if not wiring.valid
                       else "RESEARCH_AND_PRODUCTION_READINESS_PENDING"
                       if not readiness.production_greenlight_ready
                       else "TECHNICAL_READINESS_ONLY"),
            "assessed_media_format": fmt.value,
            "blueprint_stage_count": len(blueprint),
            "missing_wiring": wiring.blocker_codes(),
            "missing_niche_evidence": readiness.missing,
            "commercial_film_qualified": False,
        }
    research_path = root / "data" / "research_runtime"
    latest = research_path / "latest_health.json"
    research = daily_health(research_path) if latest.is_file() else {
        "status": "ALERT_NEVER_RAN"
    }
    model_root = root / ".tools" / "ComfyUI" / "models"
    models = [x for x in model_root.rglob("*") if x.is_file()] if model_root.is_dir() else []
    git = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, timeout=10,
    )
    return {
        "schema": "cine.company.operating_integrity.v204",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "canonical_root": str(root),
        "git_commit": git.stdout.strip() if git.returncode == 0 else None,
        "verdict": "PRODUCTION_NOT_YET_QUALIFIED",
        "departments": {
            "declared": len(dept),
            "specified": len(configured),
            "need_dedicated_spec": sorted(dept - configured),
            "qualification_caveat": (
                "A DepartmentSpec is not a qualified independent worker "
                "or a passed artistic/legal production acceptance."
            ),
        },
        "specialist_department_qualification": {
            role: "NOT_INDEPENDENTLY_QUALIFIED_BY_THIS_AUDIT"
            for role in sorted({
                "STUDIO_MANAGEMENT", "ASSETS", "PRODUCTION",
                "GENERATIVE_MEDIA", "VFX", "COLOR", "RIGHTS",
                "PACKAGING", "ANALYTICS", "RD_KNOWLEDGE", "OPERATIONS",
            })
        },
        "niches": statuses,
        "research": {
            "status": research.get("status"),
            "state": research.get("latest", {}).get("state"),
            "current_report": research.get("latest", {}).get("report"),
        },
        "media_runtime": {
            "comfyui_file_presence_only": model_root.is_dir(),
            "model_folder_files": len(models),
            "model_placeholder_count": sum(x.stat().st_size == 0 for x in models),
            "commercial_qualifications_claimed": 0,
        },
        "unresolved_company_gates": [
            "RESEARCH_SOURCE_AGE_AND_FULL_CATALOG_COVERAGE",
            "OWNER_APPROVED_RESEARCH_TO_PRODUCTION_HANDOFF",
            "MULTIFORMAT_ASSET_AND_SCENE_PRODUCTION",
            "REAL_FULL_LENGTH_FILM_INDEPENDENT_QC",
            "PUBLISHING_AND_OWNED_ANALYTICS_LEARNING",
            "HISTORIC_BLENDER_SHA_PROVENANCE_ACCEPTANCE",
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    result = audit(args.root)
    data = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(data, encoding="utf8")
    print(data)


if __name__ == "__main__":
    main()
