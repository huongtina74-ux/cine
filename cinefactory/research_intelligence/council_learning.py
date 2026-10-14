"""Single approved advice path from evidence council to owned-video experiments."""
from pathlib import Path
from datetime import date
import re
from .core import _write_json
from .council import verify_registry

def build_joint_experiment(decision: dict, feedback: dict, technical_qc: dict, registry: dict, output: str | Path) -> dict:
    if decision.get("schema") != "cine.council.decision.v1" or feedback.get("schema") != "cine.research.feedback.v1" or technical_qc.get("schema") != "cine.research.production_qc.v1":
        raise ValueError("Council decision, measured feedback and QC reports required")
    if decision.get("state") != "SUPPORTED_FOR_TEST" or decision.get("production_permission") is not False:
        raise PermissionError("Only advisory council consensus is eligible for an experiment proposal")
    if technical_qc.get("source") != feedback.get("produced_source") or not technical_qc.get("passed"):
        raise ValueError("Owned video technical QC must pass for the same source")
    provenance = feedback.get("owned_analytics_provenance", {})
    video_id = feedback.get("owned_video_id")
    if not isinstance(video_id, str) or re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id) is None:
        raise ValueError("Exact owned YouTube video ID required")
    if not isinstance(provenance, dict) or not provenance.get("channel_id") or not provenance.get("sha256"):
        raise ValueError("Owned Analytics provenance required")
    try:
        start = date.fromisoformat(provenance["period_start"])
        end = date.fromisoformat(provenance["period_end"])
    except (ValueError, TypeError, KeyError) as exc:
        raise ValueError("Invalid owned-analytics reporting period") from exc
    if start > end:
        raise ValueError("Owned-analytics reporting period reversed")
    evidence = verify_registry(registry)
    if not any(e["kind"] == "owned_analytics" and e["sha256"] == provenance["sha256"] for e in evidence.values()):
        raise ValueError("Owned analytics does not match a frozen source in the same council evidence registry")
    values = feedback.get("owned_metrics", {})
    if not values or not any(k in values for k in ("views", "ctr", "watch_time_hours", "average_view_duration_seconds")):
        raise ValueError("Measured owned-channel outcomes required")
    valid_metrics = {k: values[k] for k in ("views", "ctr", "watch_time_hours", "average_view_duration_seconds") if k in values}
    packet = {
        "schema": "cine.council.experiment.v1",
        "issue": decision["issue"],
        "state": "WAITING_FOR_EXPERIMENT_DESIGN_AND_AUTHORIZATION",
        "source_decision": decision["state"],
        "evidence_roots": decision["independent_roots"],
        "baseline": {"owned_video": feedback["produced_source"], "video_id": video_id,
                     "channel_id": provenance["channel_id"], "period_start": provenance["period_start"],
                     "period_end": provenance["period_end"], "metrics": valid_metrics,
                     "analytics_source_sha256": provenance["sha256"]},
        "technical_qc_passed": True,
        "hypothesis": "Council proposal is unproven; evaluate an ORIGINAL variant against a comparable control cohort",
        "required_design": ["pre-register one measurable outcome", "compare comparable video ages/audience windows", "specify minimum practical improvement", "capture confounders and adverse outcomes", "human approval prior to production changes"],
        "release_approved": False,
        "learned_policy_applied": False,
    }
    _write_json(Path(output), packet)
    return packet
