"""Fail-closed Bell & Leaf editorial canon/integration tests. No media and no owner signoff."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "config/niches/slow_english_a2/bell_leaf_writer_contract_v1.json"
SKILL = ROOT / ".claude/skills/cine-bell-leaf-writers-room/SKILL.md"
SOURCES = ROOT / "data/story/bell_leaf/owner_sources_private/20261107"


def load():
    data = json.loads(JSON.read_text(encoding="utf-8-sig"))
    assert data["schema"] == "cine.bell_leaf.writer_contract.v1"
    assert data["niche_id"] == "slow_english_a2"
    assert data["series_id"] == "bell_leaf"
    assert data["release_status"] == "STORY_DEVELOPMENT_ONLY"
    return data


def test_authority_and_immutable_owner_sources():
    c = load()
    assert len(c["owner_source_ids"]) == 4
    assert all(not s["git_publish"] for s in c["owner_source_ids"])
    assert c["source_authority"] == "FOUR_OWNER_DOCUMENTS_LOCKED_UNLESS_EXPLICIT_USER_CHANGE"
    assert c["required_gate_on_owner_conflict"] == "OWNER_DECISION_REQUIRED"
    assert all("owner_sources_private" in s["private_local_path"] for s in c["owner_source_ids"])


def test_family_cast_and_visual_identity_protection():
    c = load()
    assert len(c["core_characters"]) == 9
    assert len(set(c["core_characters"])) == 9
    assert c["supporting_source_character"] == "ELARA"
    v = c["protected_character_rules"]
    assert "NO_BELL" in v["BIX"]
    assert "SPARKLING_SPIRAL_PURPLE_TAIL" in v["BUBU"]
    assert "BOY" in v["JUNO"] and "GIRL" in v["LIA"]
    assert "ARTHUR_BELL" in v["GRANDPA_EARTH"]
    assert "ROSE_BELL" in v["GRANDMA_EARTH"]


def test_owner_story_precedence_and_gate_mechanics():
    c = load()
    mix = c["planning"]["main_setting_mix_percent_trial_only"]
    assert mix == {"old": 35, "new": 30, "earth": 25, "mixed": 10}
    assert sum(mix.values()) == 100
    assert c["macro_canon"]["vey_life_cycle_declined_before_sabotage"]
    assert c["macro_canon"]["earth_initial_status"] == "UNMAPPED_NO_PREEXISTING_EARTH_STATION"
    assert c["macro_canon"]["earth_station"] == "BUILT_AFTER_ACCIDENTAL_ARRIVAL"
    assert "FIXED_STATION_BELL" in c["macro_canon"]["known_world_travel"]
    assert "ECHO_TRIGGERED" in c["macro_canon"]["unknown_world_travel"]
    assert "SMALL_GROUP" in c["macro_canon"]["bubu_earth_return"]
    assert c["macro_canon"]["mara_primary"] == "FAMILY_FIRST_OLD_AND_NEW_AND_EARTH"


def test_episode_format_not_confused_with_completed_movie():
    c = load()
    p = c["planning"]
    assert (p["episode_minutes_min"], p["episode_minutes_max"]) == (40, 50)
    assert p["shot_seconds"] == 10
    assert p["fps"] == 24 and p["frame_count"] == 240
    assert p["aspect_ratio"] == "16:9"
    assert "NOT_WRITTEN" in p["episode_full_screenplay_status"]
    assert "TREATMENT" in p["ep001_status"]
    assert c["real_muse_i2v_state"] == "INDEPENDENT_E2E_REQUIRED"


def test_public_writers_room_files_present_and_showrunner_secret_excluded():
    c = load()
    docs = [ROOT / p for p in c["public_documents"]] + [SKILL, JSON]
    assert all(p.is_file() for p in docs), [str(p) for p in docs if not p.is_file()]
    t = "\n".join(p.read_text(encoding="utf-8-sig") for p in docs)
    assert "OWNER_DECISION_REQUIRED" in t
    assert "35%" in t and "30%" in t
    assert "04_ISEL" not in t
    assert "PRIVATE" in t
    assert len(c["plot_conflict_register_ids"]) == 20
    register = (ROOT / c["public_documents"][2]).read_text(encoding="utf-8-sig")
    assert all(f"BL-C{i:02d}" in register for i in range(1, 21))


def test_local_owner_source_archive_is_private_when_present():
    c = load()
    paths = [ROOT / r["private_local_path"] for r in c["owner_source_ids"]]
    if not any(p.exists() for p in paths):
        pytest.skip("Public CI checkout intentionally omits ignored owner documents.")
    assert all(p.is_file() for p in paths)
    assert all(p.stat().st_size >= 4000 for p in paths)
    for p in paths:
        check = subprocess.run(
            ["git", "-C", str(ROOT), "check-ignore", "-q", str(p)],
            capture_output=True, check=False,
        )
        assert check.returncode == 0, f"Owner-only source is not ignored: {p}"
    # Derive the hidden identity from PRIVATE material, rather than embedding it in public tests.
    hidden = paths[3].read_text(encoding="utf-8-sig")
    m = re.search(r"(?m)^##\s+([A-Z][A-Z ]{3,})\s*$", hidden)
    assert m, "Expected named secret record in local-only source"
    full_name = m.group(1).strip()
    public = "\n".join((ROOT / p).read_text(encoding="utf-8-sig") for p in c["public_documents"])
    public += SKILL.read_text(encoding="utf-8-sig") + JSON.read_text(encoding="utf-8-sig")
    assert full_name.casefold() not in public.casefold(), "Private real identity leaked into public writer docs"
