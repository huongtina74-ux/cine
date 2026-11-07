"""Actual 1000-card Bell & Leaf uniqueness evidence: do not confuse ID uniqueness with story novelty."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/bell_leaf/episode_uniqueness_gate.py"
SPEC = importlib.util.spec_from_file_location("bell_leaf_uniq_gate", PATH)
gate = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(gate)


def test_1000_cards_registered_no_false_approvals():
    cards = gate.load()
    ids = [c["episode_id"] for c in cards]
    assert len(cards) == len(set(ids)) == 1000
    assert ids[0] == "BL-0001" and ids[-1] == "BL-1000"
    assert "NOT_SCREENPLAY" in (ROOT / "docs/story/bell_leaf/slates/BELL_LEAF_1000_EPISODE_INDEX_PROPOSAL_20261107.csv").read_text(encoding="utf-8-sig")
    assert "NOT AN APPROVED" in gate.DEFAULT_SLATE.read_text(encoding="utf-8-sig").splitlines()[0]
    assert len({gate.normalize(c["title"]) for c in cards}) == 1000


def test_audit_finds_template_repetition_and_fails_closed():
    result = gate.profile(gate.load())
    assert result["status"] == "REVIEW_REQUIRED"
    assert result["registered"] == 1000
    assert result["unique_titles"] == 1000
    assert result["fields"]["continuity_delta"]["largest_exact_reuse"] >= 899
    assert result["fields"]["resolution"]["episodes_in_reused_templates"] >= 800
    assert result["fields"]["twist"]["episodes_in_reused_templates"] >= 800
    assert "REUSED_CONTINUITY_DELTA_TEMPLATE" in result["flags"]


def test_duplicate_candidate_blocks_even_with_distinct_id():
    c = gate.load()[110]
    candidate = {
        "episode_id": "BL-9000", "title": c["title"], "lead": c["lead"],
        "setting_class": c["setting_class"], "hook": c["hook"],
        "goal": "A local resident needs an honest choice about their home's safety",
        "conflict": c["conflict"], "twist": c["twist"],
        "resolution": c["resolution"], "continuity_delta": c["continuity_delta"],
    }
    report = gate.compare(candidate, gate.load())
    assert report["status"] == "BLOCKED"
    assert "STRONG_NARRATIVE_OVERLAP" in report["problems"]
    assert any(m["episode_id"] == c["episode_id"] for m in report["matches"])


def test_incomplete_candidate_fails_closed():
    r = gate.compare({"episode_id": "BL-0234", "title": "Too little information"}, gate.load())
    assert r["status"] == "BLOCKED"
    assert any(s.startswith("MISSING_") for s in r["problems"])


def test_new_distinct_pitch_gets_review_not_automatic_approval():
    c = {
        "episode_id": "BL-0009",
        "title": "The Tidal Observatory and the Missing Tidekeeper",
        "lead": "MARA", "setting_class": "OLD",
        "hook": "An observatory's carefully timed tide clock stops just as the rescue boats approach",
        "goal": "Mara helps a harbour apprentice restore safe passage for a returning medical crew",
        "conflict": "The gate station's legal access permit is invalid and the captain refuses to enter",
        "twist": "The regulator is sound but the outdated water table mismatches the tidal cycle",
        "resolution": "The harbour council checks three real tide readings and authorizes a temporary escorted route",
        "continuity_delta": "The harbour council now keeps a verified tide ledger for future repair crews",
    }
    r = gate.compare(c, gate.load())
    assert r["status"] in {"MANUAL_NOVELTY_REVIEW_REQUIRED", "BLOCKED"}
    assert r["semantic_review"] == "REQUIRED_HUMAN_REVIEW_NOT_AUTOMATICALLY_APPROVED"
    assert r["research_evidence"] == "NOT_VERIFIED_BY_THIS_TOOL"


def test_missing_baseline_blocks():
    never = ROOT / "__MISSING_BELL_LEAF_NO_SUCH_DIRECTORY_20261107"
    try:
        gate.load(never / "missing.csv", never / "missing.md")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("A missing registry must never be accepted as zero overlap")


def test_cli_audit_returns_review_required():
    p = subprocess.run([sys.executable, str(PATH), "audit"],
                       cwd=ROOT, text=True, capture_output=True, check=False)
    assert p.returncode == 2, p.stderr
    r = json.loads(p.stdout)
    assert r["status"] == "REVIEW_REQUIRED"


def test_writers_room_requires_uniqueness_preflight():
    skill = (ROOT / ".claude/skills/cine-bell-leaf-writers-room/SKILL.md").read_text(encoding="utf-8-sig")
    sop = (ROOT / "docs/story/bell_leaf/BELL_LEAF_WRITERS_ROOM_SOP_V1_20261107.md").read_text(encoding="utf-8-sig")
    assert "episode_uniqueness_gate.py check" in skill
    assert "episode_uniqueness_gate.py check" in sop
    assert "NO_AUTOMATIC_APPROVAL" in skill
