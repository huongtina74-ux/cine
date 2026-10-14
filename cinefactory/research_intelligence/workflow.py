"""Council/Claude handoff: every agent sees one canonical question and the peer record."""
from __future__ import annotations
import json
import re
from pathlib import Path

from .core import _write_json
from .triage import select_departments
from .council import verify_registry, _normalize_opinions, decide_council


def create_round_tasks(issue: dict, registry: dict, observation_path: str | Path,
                       destination: str | Path, *, niche: str, round: str = "initial",
                       previous_opinions: list[dict] | None = None,
                       approved: bool = False) -> dict:
    if round not in ("initial", "rebuttal"):
        raise ValueError("Invalid council round")
    evid = verify_registry(registry)
    obs_file = Path(observation_path).resolve(strict=True)
    observation = json.loads(obs_file.read_text(encoding="utf-8"))
    if observation.get("schema") != "cine.research.observation.v1":
        raise ValueError("Local observation evidence required")
    if not issue.get("issue_id") or not issue.get("question") or not niche.strip():
        raise ValueError("Shared issue and niche required")
    prior = previous_opinions or []
    if round == "rebuttal":
        if not prior:
            raise ValueError("Rebuttal needs actual earlier opinions")
        interim = decide_council(issue, registry, prior)
        if interim["state"] not in ("CONFLICT_UNRESOLVED", "CHALLENGE_NOT_CLOSED", "SINGLE_SOURCE", "NEEDS_CROSS_EXAM"):
            raise ValueError("Rebuttal is only needed for unresolved challenges")
        previous = interim["positions"]
        roles = [p["department"] for p in previous]
    else:
        if prior:
            raise ValueError("Initial round cannot contain peer opinions")
        previous = []
        roles = select_departments(niche)
        # Quality is required as an adversarial reviewer.
        if "quality" not in roles:
            roles.append("quality")
    out = Path(destination)
    _write_json(out / "registry.json", registry)
    shared_registry_path = str((out / "registry.json").resolve())
    tasks = []
    for role in roles:
        task = {
            "schema": "cine.research.task.v1",
            "task_id": f"{issue['issue_id']}:{role}:{round}",
            "department": role, "niche": niche,
            "reference_id": issue["issue_id"],
            "approval_status": "approved" if approved else "pending_approval",
            "evidence_path": str(obs_file),
            "council_registry_path": shared_registry_path,
            "council_issue": issue, "council_round": round,
            "shared_evidence_ids": sorted(evid),
            "peer_positions": [p for p in previous if p["department"] != role],
            "instructions": (
                "Respond to the SAME exact issue_id/question. Inspect the shared evidence files. "
                "Check other departments' citations and challenge unsupported assumptions. "
                "Produce one JSON object with issue_id, department, round, stance "
                "(SUPPORT/OPPOSE/UNKNOWN), evidence_ids, rationale, confidence (0..1), "
                "responds_to (department names) and proposed_test. "
                "Use independent analysis, not artificial consensus. No publishing or code edits."
            ),
        }
        tasks.append(task)
        _write_json(out / "tasks" / f"{role}_{round}.json", task)
    manifest = {"schema": "cine.council.round.v1", "issue": issue,
                "round": round, "tasks": tasks, "approval": "explicit_agent_run_only"}
    _write_json(out / "round.json", manifest)
    return manifest


def parse_claude_opinion(task: dict, claude_result: dict, registry: dict,
                         destination: str | Path) -> dict:
    """Fail closed on prose, malformed JSON, mismatched identity, absent citations."""
    if task.get("schema") != "cine.research.task.v1" or not task.get("council_issue"):
        raise ValueError("Council task required")
    if task.get("approval_status") != "approved":
        raise PermissionError("Approved council task required")
    if claude_result.get("schema") != "cine.research.claude_result.v1" or claude_result.get("task_id") != task["task_id"] or claude_result.get("exit_code") != 0:
        raise ValueError("Matching successful Claude CLI result required")
    raw = json.loads(claude_result["stdout"])
    if isinstance(raw, dict) and "result" in raw:
        raw = raw["result"]
    if isinstance(raw, str):
        raw = raw.strip()
        raw = re.sub(r"^\x60\x60\x60(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*\x60\x60\x60$", "", raw)
        raw = json.loads(raw)
    if not isinstance(raw, dict):
        raise ValueError("Structured JSON opinion required")
    if raw.get("department") != task["department"] or raw.get("round") != task["council_round"] or raw.get("issue_id") != task["council_issue"]["issue_id"]:
        raise ValueError("Agent changed canonical issue or identity")
    evidence = verify_registry(registry)
    normalized = _normalize_opinions([raw], evidence, task["council_issue"]["issue_id"])
    opinion = next(iter(normalized.values()))
    _write_json(Path(destination), opinion)
    return opinion
