"""Per-niche research and creator-policy routing regression tests (synthetic fixtures only)."""
import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = importlib.util.spec_from_file_location("per_niche_gate", ROOT / "tools/cf_creative_youtube_gate.py")
gate = importlib.util.module_from_spec(S)
S.loader.exec_module(gate)
PROFILES = gate.read_json(gate.POLICY)
REGISTRY = gate.read_json(gate.REGISTRY)


def source(niche, profile, idx, *, kind="DIRECT", mode="AUDIO_VIDEO_INSPECTED"):
    vid = "ABCdef1234" + str(idx)
    return {
        "niche_id": niche, "source_id": f"YT_TEST_{idx}", "cohort": kind,
        "direct_cohort_key": profile["direct_cohort_key"] if kind == "DIRECT" else "ADJACENT_ONLY",
        "channel_id": "UC_fixture_unverified",
        "video_id": vid,
        "video_url": "https://www.youtube.com/watch?v=" + vid,
        "observed_utc": "2026-11-01T00:00:00Z",
        "views": 100000, "views_captured_utc": "2026-11-01T00:00:00Z",
        "inspection_mode": mode,
        "inspected_intervals": [{"start_s": 0, "end_s": 45}] if mode != "METADATA_ONLY" else [],
        "mechanism": "An opening contradiction becomes clear through specific physical acting cues",
        "originality_difference": "Our episode uses unrelated roles, world, conflict, outcomes and original dialogue",
    }


def brief(niche="mom_grandma_family_original"):
    profile = PROFILES["profiles"][niche]
    return {
        "niche_id": niche,
        "research": {
            "baseline_niche_id": niche,
            "direct_cohort_key": profile["direct_cohort_key"],
            "sources": [source(niche, profile, 1), source(niche, profile, 2, mode="METADATA_ONLY")]
        },
        "creative": {
            "premise": "A grandmother's hand-written recipe becomes the starting point for a family reconciliation",
            "audience_value": "A specific emotionally satisfying drama with original character agency and real stakes",
            "hook": "A letter arrives from a person who cannot possibly remember last summer's story",
            "primary_conflict": "Family members have conflicting duties and no easy way to repair the broken promise",
            "distinctive_payoff": "One character gives up her inheritance to restore trust rather than winning everything",
            "originality_axes": [
                "A distinct material clue that changes the emotional stakes",
                "A family decision requiring an actual sacrifice",
                "An ending with an earned reconciliation and a changed home"
            ],
            "rights_inventory": [{"asset_id": "original_script", "origin": "owner_written",
                                  "license_or_right": "all_rights_owned",
                                  "evidence_location": "local/source_provenance_receipt.json"}],
        },
        "learning": [{
            "source_ids": ["YT_TEST_1"],
            "abstract_mechanism": "Set up an emotional question before explaining family history",
            "own_original_application": "Use a new letter and a different relationship conflict with original dialogue",
            "hypothesis_to_test": "Compare whether the viewer understands a character goal by the first minute"
        }],
        "youtube_policy_review": {
            "made_for_kids": {"decision": "NOT_MADE_FOR_KIDS", "reason": "Intended at an adult family fiction audience, evaluate title and animation context"},
            "altered_synthetic": {"decision": "NEEDS_REVIEW", "reason": "Voice and generated media disclosure are evaluated on actual output realism"},
            "reused_content": {"decision": "SUBSTANTIALLY_ORIGINAL", "reason": "Original written storyline and owned audio assets; human proof still required"},
            "inauthentic_mass_production": {"decision": "DISTINCT_EPISODE_VALUE", "reason": "Individual unique outcome and cast choices need independent review"},
            "copyright_rights": {"decision": "RIGHTS_CLEARED_DOCUMENTED", "reason": "Script is owned, supporting provenance still requires human verification"},
            "advertiser_suitability": {"decision": "NEEDS_REVIEW", "reason": "Need final asset and published metadata suitability audit"}
        }
    }


def blocked(b, reason):
    r = gate.assess(b, PROFILES, REGISTRY)
    assert r["status"] == "BLOCKED", r
    assert reason in r["blocking"], r
    assert r["release_authorized"] is False


def test_registered_niches_protected_and_all_extra_local_packages_block():
    r = gate.inventory(PROFILES, REGISTRY)
    assert r["ready_for_data_import"]
    assert len(r["registered_research_niches"]) == 10
    assert set(r["registered_research_niches"]) == set(r["creative_profiles"])
    assert len(r["unregistered_content_packages"]) >= 8
    assert "minecraft" in r["unregistered_content_packages"]
    assert "audio_storytelling_seniors" in r["unregistered_content_packages"]


def test_valid_synthetic_brief_is_only_ready_for_human_review():
    r = gate.assess(brief(), PROFILES, REGISTRY)
    assert r["status"] == "INDEPENDENT_EDITORIAL_REVIEW_REQUIRED", r
    assert r["direct_peer_count"] == 2
    assert r["deep_inspected_direct_peer_count"] == 1
    assert not r["release_authorized"] and not r["production_authorized"]


def test_blocks_cross_niche_baseline_and_wrong_direct_cohort():
    b = brief()
    b["research"]["baseline_niche_id"] = "cozy_bedtime_fiction"
    b["research"]["sources"][0]["direct_cohort_key"] = "cozy_bedtime_fiction_DIRECT_VERIFICATION_REQUIRED"
    blocked(b, "CROSS_NICHE_BASELINE_FORBIDDEN")
    blocked(b, "SOURCE_0_DIRECT_KEY_MISMATCH")


def test_adjacent_sources_do_not_count_as_direct_research():
    b = brief()
    b["research"]["sources"][1] = source(
        b["niche_id"], PROFILES["profiles"][b["niche_id"]], 2, kind="ADJACENT")
    blocked(b, "LESS_THAN_TWO_DISTINCT_DIRECT_PEER_VIDEOS")


def test_cannot_claim_audio_video_without_timecodes():
    b = brief()
    b["research"]["sources"][0]["inspected_intervals"] = []
    blocked(b, "SOURCE_0_INSPECTION_INTERVALS_MISSING")


def test_copy_from_competitor_is_blocked_even_if_idea_changes_name():
    b = brief()
    b["creative"]["competitor_dialogue_paraphrased"] = True
    blocked(b, "UNORIGINAL_COPYING_RISK_COMPETITOR_DIALOGUE_PARAPHRASED")


def test_missing_kids_or_synthetic_decision_is_blocked():
    b = brief()
    b["youtube_policy_review"]["made_for_kids"]["decision"] = "WE_WANT_HIGH_RPM_NOT_KIDS"
    blocked(b, "MISSING_POLICY_DECISION_MADE_FOR_KIDS")
    b = brief()
    del b["youtube_policy_review"]["altered_synthetic"]
    blocked(b, "MISSING_POLICY_DECISION_ALTERED_SYNTHETIC")


def test_unknown_or_unregistered_package_never_inherits_wrong_niche():
    blocked({"niche_id": "minecraft"}, "UNREGISTERED_OR_INCORRECT_NICHE_ROUTE")
    blocked({"niche_id": "something_not_in_registry"}, "UNREGISTERED_OR_INCORRECT_NICHE_ROUTE")


def test_bell_leaf_not_generic_a2_and_requires_its_canon():
    b = brief("slow_english_a2_story")
    b["series_id"] = "bell_leaf"
    blocked(b, "BELL_LEAF_MUST_NOT_BE_ROUTED_TO_GENERIC_SLOW_ENGLISH")
    b = brief("magical_witch_family_stories")
    b["series_id"] = "bell_leaf"
    b["episode_id"] = "BL-0010"
    blocked(b, "BELL_LEAF_OWNER_CANON_AND_CHARACTER_ASSETS_MUST_BE_REFERENCED")
    blocked(b, "BELL_LEAF_EPISODE_UNIQUENESS_GATE_NOT_ATTESTED")


def test_fact_based_niche_requires_sources_and_finance_region():
    b = brief("senior_retirement_finance")
    blocked(b, "TWO_INDEPENDENT_FACT_SOURCES_REQUIRED")
    blocked(b, "FINANCE_JURISDICTION_AND_ASOF_REQUIRED")


def test_unverified_competitor_retention_not_allowed():
    b = brief()
    b["research"]["sources"][0]["retention"] = 0.89
    blocked(b, "SOURCE_0_UNVERIFIED_PRIVATE_COMPETITOR_METRICS")


def test_no_auto_publish_from_procedural_gate():
    assert PROFILES["publish_release"] == "NOT_AUTOMATICALLY_AUTHORIZED"
    for niche in REGISTRY["niches"]:
        b = brief(niche["id"])
        r = gate.assess(b, PROFILES, REGISTRY)
        assert not r["release_authorized"]
        assert r["needs_human_review"]
