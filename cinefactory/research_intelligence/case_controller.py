"""One authoritative per-issue case manifest, not parallel department reports."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from .core import _write_json
from .council import decide_council, create_challenge_packets
from .council_learning import build_joint_experiment

def _digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

def consolidate_case(issue: dict, registry: dict, opinions: list[dict], output_dir: str | Path,
                     *, feedback: dict | None = None, technical_qc: dict | None = None) -> dict:
    """Only one canonical decision packet is authoritative for this exact evidence revision."""
    if (feedback is None) != (technical_qc is None):
        raise ValueError("Feedback and QC must be supplied together")
    root = Path(output_dir)
    revision = _digest({"issue": issue, "registry": registry, "opinions": opinions,
                        "feedback": feedback, "quality": technical_qc})
    snapshot_dir = root / "revisions" / revision[:16]
    decision = decide_council(issue, registry, opinions)
    _write_json(snapshot_dir / "decision.json", decision)
    if decision["state"] == "SUPPORTED_FOR_TEST":
        experiment = (build_joint_experiment(decision, feedback, technical_qc, registry, snapshot_dir / "experiment.json")
                      if feedback is not None else None)
        next_step = "EXPERIMENT_DESIGN_PENDING_APPROVAL" if experiment else "OWNED_FEEDBACK_AND_QC_REQUIRED"
        challenge_count = 0
    else:
        challenge = create_challenge_packets(decision, snapshot_dir / "challenges.json")
        experiment = None
        challenge_count = len(challenge["tasks"])
        next_step = "COLLECT_MORE_EVIDENCE" if decision["state"] == "SINGLE_SOURCE" else "CROSS_EXAMINATION_REQUIRED"
    manifest = {
        "schema": "cine.council.case.v1",
        "issue": decision["issue"],
        "revision": revision,
        "source_registry_hash": _digest(registry),
        "authoritative_decision": str((snapshot_dir / "decision.json").resolve()),
        "decision_state": decision["state"], "next_step": next_step,
        "challenge_count": challenge_count,
        "experiment": str((snapshot_dir / "experiment.json").resolve()) if experiment else None,
        "releases_permitted": False,
        "semantic_truth_certified": False,
    }
    _write_json(root / "case.json", manifest)
    return manifest
