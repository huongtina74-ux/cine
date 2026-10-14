"""v209 actual-master admission for strict film production.

Only independent externally trusted Ed25519 signers and the actual ffprobe
master can admit a movie. Test JSON and diagnostic slate never promote a film.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .longform_acceptance_v205 import independent_film_acceptance, probe_film

def review_original_master(
    project_dir: Path, movie: str | Path, *, duration_target: int | None,
    trusted_key_map_file: str | Path | None = None,
) -> dict[str, Any]:
    project_dir = Path(project_dir).resolve(strict=True)
    master = Path(movie).resolve(strict=True)
    inputs = (project_dir/"inputs").resolve()
    review_file = inputs/"independent_film_reviews.json"
    expected_pilot = bool(duration_target and 30 <= duration_target <= 60)
    expected_longform = bool(duration_target and 480 <= duration_target <= 720)
    if not (expected_pilot or expected_longform):
        return {"status":"BLOCKED_UNSUPPORTED_RELEASE_DURATION",
                "release_permission":False,
                "target_seconds":duration_target,
                "required_duration_classes":["ORIGINAL_PILOT_30_60","ORIGINAL_FILM_480_720"]}
    min_secs,max_secs=(30,60) if expected_pilot else (480,720)
    try:
        media=probe_film(master,min_seconds=min_secs,max_seconds=max_secs,
                         min_width=1920,min_height=1080)
    except (OSError, ValueError, RuntimeError) as exc:
        return {"status":"BLOCKED_MASTER_TECHNICAL_PROBE",
                "release_permission":False,"reason":type(exc).__name__}
    if not media["technical_pass"]:
        return {"status":"BLOCKED_MASTER_TECHNICAL_QC",
                "release_permission":False,"media_evidence":media}
    if not review_file.is_file():
        return {"status":"WAITING_SIGNED_INDEPENDENT_FILM_REVIEWS",
                "release_permission":False,"media_evidence":media}
    # Trust is configured independently of project-owned files; no trust-on-first-use.
    trust_file = trusted_key_map_file or os.environ.get(
        "CINEFACTORY_FILM_REVIEWER_KEYS_FILE"
    )
    if not trust_file:
        return {"status":"EXTERNAL_REVIEWER_TRUST_ROOT_REQUIRED",
                "release_permission":False,"media_evidence":media}
    try:
        trusted_path=Path(trust_file).resolve(strict=True)
        # A review may not install its own reviewer trust policy.
        if trusted_path.is_relative_to(project_dir):
            raise PermissionError("TRUST_ROOT_CANNOT_BE_INSIDE_PROJECT")
        keys=json.loads(trusted_path.read_text(encoding="utf8"))
        reviews=json.loads(review_file.read_text(encoding="utf8"))
        if not isinstance(keys,dict) or not isinstance(reviews,dict):
            raise ValueError("INVALID_REVIEW_ROOT")
        acceptance=independent_film_acceptance(media,reviews,keys)
    except (OSError, ValueError, TypeError, KeyError, PermissionError) as exc:
        return {"status":"FILM_REVIEW_PROVENANCE_REJECTED",
                "release_permission":False,"reason":type(exc).__name__,
                "media_evidence":media}
    return {
        **acceptance,
        "scope":"ORIGINAL_PILOT" if expected_pilot else "ORIGINAL_LONGFORM",
        "release_permission":acceptance.get("release_permission") is True,
        "master_sha256":media["sha256"],
        "master_path":str(master),
        "independent_reviewer_source":"EXTERNALLY_TRUSTED_SIGNATURES",
    }
