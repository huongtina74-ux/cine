"""CineCouncil: one evidence registry, structured cross-examination, fail-closed arbitration.

This is a deterministic coordination layer, NOT a model, nor proof of semantic truth.
Agent agreement is not independent verification. All recommendations require a
validated experiment and an authorized human decision before production promotion.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
from datetime import datetime, timezone
from .core import DEPARTMENTS, _write_json

ALLOWED_KINDS = {"observation", "owned_analytics", "public_metadata", "transcript", "human_review", "experiment"}
STANCES = {"SUPPORT", "OPPOSE", "UNKNOWN"}
ROUNDS = {"initial", "rebuttal"}
MAX_SOURCE_BYTES = 512 * 1024 * 1024


def _fingerprint(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _utc_time(s: str) -> datetime:
    when = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if when.tzinfo is None:
        raise ValueError("Timestamp without timezone")
    return when.astimezone(timezone.utc)


def collect_evidence(sources: list[dict], output: str | Path) -> dict:
    """Freeze local source files into a verifiable registry; no URL-only 'verified' claims."""
    if not sources:
        raise ValueError("At least one concrete evidence source is required")
    items: list[dict] = []
    ids: set[str] = set()
    hash_roots: dict[str, str] = {}
    for entry in sources:
        ident = entry.get("evidence_id")
        kind = entry.get("kind")
        if not isinstance(ident, str) or not ident.strip() or ident in ids or kind not in ALLOWED_KINDS:
            raise ValueError("Invalid or duplicate evidence_id/kind")
        ids.add(ident)
        filename = Path(entry["path"]).resolve(strict=True)
        if not filename.is_file() or not 0 < filename.stat().st_size <= MAX_SOURCE_BYTES:
            raise ValueError("Concrete evidence file required (limit 512 MiB)")
        raw = filename.read_bytes()
        # Root identity represents an independent observation lineage, not a file count.
        root_id = entry.get("independent_root")
        if not isinstance(root_id, str) or not root_id.strip():
            raise ValueError("Independent root identifier required")
        if entry.get("verified_by") not in ("local_machine", "authorized_owner", "human"):
            raise ValueError("Evidence provenance required")
        file_hash = _fingerprint(raw)
        if file_hash in hash_roots and hash_roots[file_hash] != root_id:
            raise ValueError("Identical evidence file cannot claim a different independent origin")
        hash_roots[file_hash] = root_id
        items.append({
            "evidence_id": ident, "kind": kind, "path": str(filename),
            "sha256": file_hash, "independent_root": root_id,
            "verified_by": entry["verified_by"], "scope": str(entry.get("scope", "unspecified")),
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "meaning": "file_integrity_verified_not_semantic_truth",
        })
    result = {"schema": "cine.council.evidence.v1", "sources": items}
    _write_json(Path(output), result)
    return result


def verify_registry(registry: dict) -> dict[str, dict]:
    if registry.get("schema") != "cine.council.evidence.v1":
        raise ValueError("Unsupported evidence registry")
    mapped: dict[str, dict] = {}
    hash_roots: dict[str, str] = {}
    for item in registry.get("sources", []):
        path = Path(item["path"]).resolve(strict=True)
        if not path.is_file() or path.stat().st_size > MAX_SOURCE_BYTES:
            raise ValueError("Evidence file unavailable/oversized")
        if _fingerprint(path.read_bytes()) != item["sha256"]:
            raise ValueError(f"Evidence tampered: {item['evidence_id']}")
        ident = item["evidence_id"]
        if ident in mapped or item.get("kind") not in ALLOWED_KINDS or not item.get("independent_root"):
            raise ValueError("Evidence registry invalid/duplicate")
        digest, root = item["sha256"], item["independent_root"]
        if digest in hash_roots and hash_roots[digest] != root:
            raise ValueError("Identical file cannot count as different independent evidence")
        hash_roots[digest] = root
        mapped[ident] = item
    if not mapped:
        raise ValueError("Empty evidence registry")
    return mapped


def _normalize_opinions(opinions: list[dict], evidence: dict[str, dict], issue_id: str) -> dict[tuple[str, str], dict]:
    """One signed position per role/round; never double-count agent restatements."""
    accepted = {}
    for opinion in opinions:
        if opinion.get("issue_id") != issue_id:
            raise ValueError("Opinion belongs to a different issue")
        dept, round_ = opinion.get("department"), opinion.get("round")
        if dept not in DEPARTMENTS or round_ not in ROUNDS or opinion.get("stance") not in STANCES:
            raise ValueError("Unknown role, round or stance")
        key = (dept, round_)
        if key in accepted:
            raise ValueError("Duplicate department vote in round")
        refs = opinion.get("evidence_ids")
        if not isinstance(refs, list) or len(refs) != len(set(refs)) or any(i not in evidence for i in refs):
            raise ValueError("All cited evidence IDs must exist and be unique")
        if opinion["stance"] != "UNKNOWN" and not refs:
            raise ValueError("Non-UNKNOWN positions require evidence")
        explanation = opinion.get("rationale")
        if not isinstance(explanation, str) or not explanation.strip():
            raise ValueError("Explicit reasoning summary required")
        confidence = opinion.get("confidence")
        if isinstance(confidence, bool) or not isinstance(confidence, (float, int)) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
            raise ValueError("Confidence must be 0..1")
        responds = opinion.get("responds_to", [])
        if not isinstance(responds, list) or any(s not in DEPARTMENTS for s in responds):
            raise ValueError("Invalid reviewed departments")
        accepted[key] = {
            "issue_id": issue_id, "department": dept, "round": round_,
            "stance": opinion["stance"], "evidence_ids": refs,
            "rationale": explanation, "confidence": confidence, "responds_to": responds,
            "proposed_test": str(opinion.get("proposed_test", "")),
        }
    return accepted


def decide_council(issue: dict, registry: dict, opinions: list[dict], *, min_departments: int = 2) -> dict:
    """Conservative arbiter; no silent tie breaking and never self-authorizes release."""
    issue_id = issue.get("issue_id")
    if not isinstance(issue_id, str) or not issue_id.strip() or not issue.get("question"):
        raise ValueError("Canonical issue_id and question required")
    if not 2 <= min_departments <= 9:
        raise ValueError("At least two independent roles required")
    evidence = verify_registry(registry)
    normalized = _normalize_opinions(opinions, evidence, issue_id)
    roles = sorted(set(dept for dept, _ in normalized))
    initial = {dept: v for (dept, round_), v in normalized.items() if round_ == "initial"}
    latest = dict(initial)
    for (dept, round_), vote in normalized.items():
        if round_ == "rebuttal":
            if dept not in initial:
                raise ValueError("Rebuttal requires initial opinion")
            latest[dept] = vote
    # A challenge is a disagreement or explicit uncertainty, not something majority vote erases.
    initial_opposition = {dept for dept, v in initial.items() if v["stance"] in ("OPPOSE", "UNKNOWN")}
    addressed = all(
        dept in latest and latest[dept]["round"] == "rebuttal"
        for dept in initial_opposition
    )
    all_informed = all(
        any(v["round"] == "rebuttal" and dept != v["department"] and dept in v["responds_to"] for v in latest.values())
        for dept in initial_opposition
    )
    support = sorted(d for d, v in latest.items() if v["stance"] == "SUPPORT")
    opposition = sorted(d for d, v in latest.items() if v["stance"] == "OPPOSE")
    unknown = sorted(d for d, v in latest.items() if v["stance"] == "UNKNOWN")
    roots = sorted({evidence[eid]["independent_root"] for v in latest.values() if v["stance"] == "SUPPORT" for eid in v["evidence_ids"]})
    has_cross_review = (
        ("quality", "rebuttal") in normalized
        and any((dept, "rebuttal") in normalized for dept in latest if dept != "quality")
        and all(
            any(peer != v["department"] and peer in latest for peer in v["responds_to"])
            for v in latest.values() if v["round"] == "rebuttal"
        )
    )
    challenges: list[dict] = []
    for dept in opposition + unknown:
        v = latest[dept]
        challenges.append({"from": dept, "stance": v["stance"], "reason": v["rationale"], "request": v["proposed_test"] or "Provide independent evidence that resolves this specific issue", "evidence_ids": v["evidence_ids"]})
    if len(initial) < min_departments or "quality" not in initial:
        state, why = "INSUFFICIENT_REVIEW", "Missing independent roles or mandatory quality reviewer"
    elif opposition or unknown:
        state, why = "CONFLICT_UNRESOLVED", "Opposition or uncertainty remains after available rounds"
    elif initial_opposition and not (addressed and all_informed):
        state, why = "CHALLENGE_NOT_CLOSED", "Initial dissent must be rebutted and explicitly considered"
    elif len(support) < min_departments:
        state, why = "INSUFFICIENT_REVIEW", "Not enough supporting departmental reviews"
    elif len(roots) < 2:
        state, why = "SINGLE_SOURCE", "Multiple agents citing one evidence lineage are not independent corroboration"
    elif not has_cross_review:
        state, why = "NEEDS_CROSS_EXAM", "Initial agreement still requires mutual peer critique and Quality rebuttal"
    else:
        state, why = "SUPPORTED_FOR_TEST", "Reviewed cross-role agreement and distinct evidence roots; empirical trial still required"
    return {
        "schema": "cine.council.decision.v1", "issue": {"issue_id": issue_id, "question": issue["question"]},
        "state": state, "reason": why,
        "positions": [latest[d] for d in sorted(latest)],
        "opposition": opposition, "unknown": unknown, "support": support,
        "independent_roots": roots, "challenges": challenges,
        "authority": "advisory_only", "production_permission": False,
        "verification": "integrity_and_consistency_not_ground_truth",
        "next_action": "design controlled original experiment and obtain authorized review" if state == "SUPPORTED_FOR_TEST" else "collect evidence and run another debate round",
    }


def create_challenge_packets(decision: dict, out: str | Path) -> dict:
    """Create structured cross-examination requests for other departments/Claude tasks."""
    if decision.get("schema") != "cine.council.decision.v1":
        raise ValueError("Council decision required")
    issue = decision["issue"]
    targets = []
    pending = decision["challenges"]
    if decision["state"] == "NEEDS_CROSS_EXAM":
        pending = [{"from": p["department"], "stance": p["stance"],
                    "reason": p["rationale"], "request": "Independently challenge assumptions and cite a different evidence root if possible",
                    "evidence_ids": p["evidence_ids"]} for p in decision["positions"]]
    for challenge in pending:
        for target in sorted(set(decision["support"] + ["quality"])):
            if target == challenge["from"]:
                continue
            targets.append({
                "schema": "cine.council.challenge.v1", "issue_id": issue["issue_id"],
                "target_department": target, "challenger": challenge["from"],
                "challenger_stance": challenge["stance"], "challenge_reason": challenge["reason"],
                "required_evidence_ids": challenge["evidence_ids"],
                "question": challenge["request"],
                "instructions": "Inspect shared evidence, respond to the challenge explicitly; UNKNOWN is acceptable. Do not change a claim merely to form consensus.",
                "state": "pending_human_approved_agent_run",
            })
    result = {"schema": "cine.council.challenge_pack.v1", "issue": issue, "tasks": targets}
    _write_json(Path(out), result)
    return result


def run_council(issue: dict, registry: dict, opinions: list[dict], output: str | Path) -> dict:
    outcome = decide_council(issue, registry, opinions)
    _write_json(Path(output), outcome)
    return outcome
