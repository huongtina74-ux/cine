"""Adversarial tests: agreement is not truth, dissent cannot be erased."""
from pathlib import Path
import copy
import pytest
from cinefactory.research_intelligence.council import (
    collect_evidence, verify_registry, decide_council, create_challenge_packets
)

ISSUE = {"issue_id": "minecraft-hook-001", "question": "Should CineFactory test an original shorter hook?"}


@pytest.fixture
def ledger(tmp_path):
    obs = tmp_path / "observation.json"
    obs.write_text('{"schema":"cine.research.observation.v1","frames":[{"second":3}]}', encoding="utf-8")
    metrics = tmp_path / "studio.json"
    metrics.write_text('{"schema":"cine.research.studio_csv.v1","rows":[{"video_id":"abcdefghijk"}]}', encoding="utf-8")
    return collect_evidence([
        {"evidence_id": "video-a", "kind": "observation", "path": str(obs), "independent_root": "reference-video-123", "verified_by": "local_machine"},
        {"evidence_id": "owned-b", "kind": "owned_analytics", "path": str(metrics), "independent_root": "owned-analytics-oct", "verified_by": "authorized_owner"},
    ], tmp_path / "ledger.json")


def opinion(role, stance="SUPPORT", *, evidence=("video-a",), round="initial", responds=()):
    return {"issue_id": ISSUE["issue_id"], "department": role, "round": round,
            "stance": stance, "evidence_ids": list(evidence),
            "rationale": "Evidence suggests testing, not blindly adopting format",
            "confidence": 0.7, "responds_to": list(responds)}


def test_cross_role_multisource_requires_real_cross_review(ledger):
    opening = [opinion("research"), opinion("quality", evidence=("owned-b",))]
    first = decide_council(ISSUE, ledger, opening)
    assert first["state"] == "NEEDS_CROSS_EXAM"
    second = [
        opinion("research", round="rebuttal", responds=("quality",)),
        opinion("quality", evidence=("owned-b",), round="rebuttal", responds=("research",)),
    ]
    out = decide_council(ISSUE, ledger, opening + second)
    assert out["state"] == "SUPPORTED_FOR_TEST"
    assert out["production_permission"] is False
    assert out["verification"] == "integrity_and_consistency_not_ground_truth"


def test_two_agree_one_source_not_independent(ledger):
    out = decide_council(ISSUE, ledger, [opinion("research"), opinion("quality")])
    assert out["state"] == "SINGLE_SOURCE"
    assert out["production_permission"] is False


def test_opposing_quality_blocks_even_if_outvoted(ledger):
    out = decide_council(ISSUE, ledger, [
        opinion("research"), opinion("story", evidence=("owned-b",)), opinion("quality", "OPPOSE", evidence=("owned-b",))
    ])
    assert out["state"] == "CONFLICT_UNRESOLVED"
    assert out["opposition"] == ["quality"]


def test_uncertainty_blocks_and_generates_cross_question(ledger, tmp_path):
    out = decide_council(ISSUE, ledger, [
        opinion("research"), opinion("quality", "UNKNOWN", evidence=())
    ])
    assert out["state"] == "CONFLICT_UNRESOLVED"
    packet = create_challenge_packets(out, tmp_path / "challenges.json")
    assert packet["tasks"][0]["challenger"] == "quality"
    assert packet["tasks"][0]["target_department"] == "research"
    assert packet["tasks"][0]["state"] == "pending_human_approved_agent_run"


def test_rebuttal_and_response_needed_to_close_challenge(ledger):
    original = [opinion("research"), opinion("quality", "OPPOSE", evidence=("owned-b",))]
    revised_quality = opinion("quality", "SUPPORT", evidence=("owned-b",), round="rebuttal", responds=("research",))
    out = decide_council(ISSUE, ledger, original + [revised_quality])
    assert out["state"] == "CHALLENGE_NOT_CLOSED"
    revised_research = opinion("research", "SUPPORT", evidence=("video-a",), round="rebuttal", responds=("quality",))
    out = decide_council(ISSUE, ledger, original + [revised_quality, revised_research])
    assert out["state"] == "SUPPORTED_FOR_TEST"


def test_challenge_rebuttal_cannot_silence_opposition(ledger):
    out = decide_council(ISSUE, ledger, [
        opinion("research"), opinion("quality", "OPPOSE", evidence=("owned-b",)),
        opinion("research", evidence=("video-a",), round="rebuttal", responds=("quality",)),
        opinion("quality", "OPPOSE", evidence=("owned-b",), round="rebuttal", responds=("research",)),
    ])
    assert out["state"] == "CONFLICT_UNRESOLVED"


def test_no_double_vote_and_unknown_reference(ledger):
    with pytest.raises(ValueError, match="Duplicate"):
        decide_council(ISSUE, ledger, [opinion("research"), opinion("research"), opinion("quality", evidence=("owned-b",))])
    with pytest.raises(ValueError, match="evidence IDs"):
        decide_council(ISSUE, ledger, [opinion("research", evidence=("fabricated",)), opinion("quality")])
    with pytest.raises(ValueError, match="Confidence"):
        decide_council(ISSUE, ledger, [dict(opinion("research"), confidence=99), opinion("quality")])


def test_tampered_evidence_rejected(ledger):
    Path(ledger["sources"][0]["path"]).write_text("tampered", encoding="utf-8")
    with pytest.raises(ValueError, match="tampered"):
        verify_registry(ledger)


def test_registrar_rejects_duplicate_files_and_missing_origin(tmp_path):
    source = tmp_path / "x.txt"
    source.write_text("facts", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        collect_evidence([
            {"evidence_id": "a", "path": str(source), "kind": "observation", "independent_root": "r1", "verified_by": "local_machine"},
            {"evidence_id": "a", "path": str(source), "kind": "observation", "independent_root": "r1", "verified_by": "local_machine"},
        ], tmp_path / "registry.json")
    with pytest.raises(ValueError, match="Independent root"):
        collect_evidence([{"evidence_id": "a", "path": str(source), "kind": "observation", "verified_by": "local_machine"}], tmp_path / "registry.json")


def test_missing_quality_cannot_claim_consensus(ledger):
    out = decide_council(ISSUE, ledger, [opinion("research"), opinion("story", evidence=("owned-b",))])
    assert out["state"] == "INSUFFICIENT_REVIEW"


def test_rebuttal_without_initial_rejected(ledger):
    with pytest.raises(ValueError, match="initial"):
        decide_council(ISSUE, ledger, [
            opinion("research"), opinion("quality", evidence=("owned-b",), round="rebuttal")
        ])
