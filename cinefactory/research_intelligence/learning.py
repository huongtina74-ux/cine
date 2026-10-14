"""Verified research feedback and safe learning gates."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from .core import _write_json, DEPARTMENTS

def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

def ingest_department_result(task: dict, payload: dict, destination: str | Path) -> dict:
    """Only structured, timestamp-grounded findings can enter the review queue."""
    if task.get("schema") != "cine.research.task.v1" or task.get("approval_status") != "approved":
        raise PermissionError("Approved department task required")
    if task.get("department") not in DEPARTMENTS:
        raise ValueError("Unknown department")
    findings = payload.get("findings")
    if not isinstance(findings, list) or not findings:
        raise ValueError("Findings required")
    validated = []
    for finding in findings:
        if not isinstance(finding, dict) or finding.get("status") not in ("VERIFIED", "HYPOTHESIS", "UNKNOWN"):
            raise ValueError("Evidence status required")
        if not isinstance(finding.get("claim"), str) or not finding["claim"].strip():
            raise ValueError("Claim required")
        evidence = finding.get("evidence", [])
        if not isinstance(evidence, list):
            raise ValueError("Evidence array required")
        if finding["status"] == "VERIFIED" and not evidence:
            raise ValueError("Verified claim requires evidence")
        if not all(isinstance(item, dict) and (("timestamp_seconds" in item and isinstance(item["timestamp_seconds"], (int, float)) and item["timestamp_seconds"] >= 0) or "path" in item) for item in evidence):
            raise ValueError("Evidence must contain timestamp or path")
        validated.append({"claim": finding["claim"], "status": finding["status"], "evidence": evidence, "confidence": finding.get("confidence")})
    report = {"schema": "cine.research.review.v1", "task_id": task["task_id"], "department": task["department"], "findings": validated, "state": "needs_human_review", "created_at": datetime.now(timezone.utc).isoformat(), "input_hash": _digest(payload)}
    _write_json(Path(destination), report)
    return report

def propose_learning(feedback: dict, reviews: list[dict], destination: str | Path) -> dict:
    """Proposals are never promoted into production policy automatically."""
    if feedback.get("schema") != "cine.research.feedback.v1":
        raise ValueError("Measured feedback required")
    if not reviews or any(r.get("schema") != "cine.research.review.v1" or r.get("state") != "needs_human_review" for r in reviews):
        raise ValueError("Unreviewed research reports required")
    suggestions = []
    for report in reviews:
        for item in report["findings"]:
            if item["status"] != "UNKNOWN":
                suggestions.append({"department": report["department"], "claim": item["claim"], "evidence_status": item["status"], "proposed_action": "Design original A/B experiment and compare owned video metrics", "decision": "pending_validation"})
    result = {"schema": "cine.research.learning.v1", "state": "awaiting_experiment_and_human_approval", "reference_source": feedback["reference_source"], "produced_source": feedback["produced_source"], "metrics": feedback["owned_metrics"], "proposals": suggestions, "revision_hash": _digest({"feedback": feedback, "reviews": reviews})}
    _write_json(Path(destination), result)
    return result
