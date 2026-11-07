#!/usr/bin/env python3
"""CINE per-niche Research->Creative->YouTube preflight. No invented approvals.

Reads explicit dated source evidence and original-creative decisions. Fails closed
for missing, mislabeled, cross-niche or incomplete research. Never clears YouTube
monetization, copyright, youth audience, synthetic disclosure or ad suitability.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config/research/per_niche/creative_youtube_risk_profiles_v1.json"
REGISTRY = ROOT / "config/research/per_niche/niches.json"
PACKAGES = ROOT / "config/niches"
REQ_DECISIONS = {
    "made_for_kids": {"MADE_FOR_KIDS", "NOT_MADE_FOR_KIDS", "NEEDS_REVIEW"},
    "altered_synthetic": {"DISCLOSE", "NOT_REQUIRED_JUSTIFIED", "NEEDS_REVIEW"},
    "reused_content": {"SUBSTANTIALLY_ORIGINAL", "NEEDS_REVIEW", "BLOCKED"},
    "inauthentic_mass_production": {"DISTINCT_EPISODE_VALUE", "NEEDS_REVIEW", "BLOCKED"},
    "copyright_rights": {"RIGHTS_CLEARED_DOCUMENTED", "NEEDS_REVIEW", "BLOCKED"},
    "advertiser_suitability": {"CLEARED_WITH_REVIEW", "NEEDS_REVIEW", "BLOCKED"},
}
REVIEW_VALUES = {"NEEDS_REVIEW", "BLOCKED"}
SOURCE_MODES = {"METADATA_ONLY", "TRANSCRIPT_INSPECTED", "AUDIO_VIDEO_INSPECTED"}


def read_json(path: Path) -> dict:
    result = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(result, dict):
        raise ValueError(f"{path}: object required")
    return result


def valid_time(s: object) -> bool:
    if not isinstance(s, str) or not s:
        return False
    try:
        x = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return x.tzinfo is not None and x <= datetime.now(timezone.utc)
    except ValueError:
        return False


def video_id_from_url(url: str) -> str | None:
    if not isinstance(url, str):
        return None
    u = urlparse(url)
    if u.scheme != "https":
        return None
    host = (u.hostname or "").lower()
    if host in {"www.youtube.com", "youtube.com", "m.youtube.com"} and u.path == "/watch":
        return parse_qs(u.query).get("v", [None])[0]
    if host == "youtu.be":
        return u.path.lstrip("/").split("/")[0]
    return None


def nonempty(value: object, min_chars: int = 15) -> bool:
    return isinstance(value, str) and len(value.strip()) >= min_chars


def inventory(policy: dict, registry: dict, packages: Path = PACKAGES) -> dict:
    profiles = policy["profiles"]
    known = {x["id"] for x in registry["niches"]}
    package_names = {x.name for x in packages.iterdir() if x.is_dir() and not x.name.startswith("_")}
    mapped = {"slow_english_a2": "magical_witch_family_stories"}
    expected_missing = package_names - set(mapped) - (set(profiles) & package_names)
    unmatched = expected_missing - set(policy["missing_registry_packages"])
    return {
        "registered_research_niches": sorted(known),
        "creative_profiles": sorted(profiles),
        "unregistered_content_packages": sorted(expected_missing),
        "unregistered_without_fail_closed_profile": sorted(unmatched),
        "registry_profiles_missing": sorted(known - set(profiles)),
        "profile_not_in_registry": sorted(set(profiles) - known),
        "locked_package_routes": mapped,
        "registered_niche_routes_valid": not (unmatched or known - set(profiles) or set(profiles)-known),
        "all_content_packages_research_registered": not expected_missing,
        "ready_for_data_import": not (unmatched or known - set(profiles) or set(profiles)-known or expected_missing),
        "status": "PARTIAL_CONTENT_ROUTING" if expected_missing else "REGISTERED_ROUTES_VALID",
        "note": "Configuration coverage only; no live research or creative quality is proved."
    }


def assess(brief: dict, policy: dict | None = None, registry: dict | None = None) -> dict:
    policy = policy if policy is not None else read_json(POLICY)
    registry = registry if registry is not None else read_json(REGISTRY)
    failures, warnings = [], []
    name = brief.get("niche_id")
    profile = policy["profiles"].get(name)
    known = {x["id"] for x in registry["niches"]}
    if not profile or name not in known:
        return {"status": "BLOCKED", "niche_id": name, "blocking": ["UNREGISTERED_OR_INCORRECT_NICHE_ROUTE"],
                "needs_human_review": True, "release_authorized": False}
    if name == "magical_witch_family_stories":
        if brief.get("series_id") != "bell_leaf":
            failures.append("BELL_LEAF_SERIES_ID_REQUIRED")
        if not brief.get("owner_canon_version") or not brief.get("character_canon_reference"):
            failures.append("BELL_LEAF_OWNER_CANON_AND_CHARACTER_ASSETS_MUST_BE_REFERENCED")
    elif name == "slow_english_a2_story" and brief.get("series_id") == "bell_leaf":
        failures.append("BELL_LEAF_MUST_NOT_BE_ROUTED_TO_GENERIC_SLOW_ENGLISH")
    research = brief.get("research") or {}
    if research.get("baseline_niche_id") != name:
        failures.append("CROSS_NICHE_BASELINE_FORBIDDEN")
    if research.get("direct_cohort_key") != profile["direct_cohort_key"]:
        failures.append("WRONG_DIRECT_COMPETITOR_COHORT")
    records = research.get("sources") or []
    if not isinstance(records, list):
        records = []
        failures.append("RESEARCH_SOURCES_NOT_LIST")
    source_ids, direct, inspected = [], [], []
    for i, row in enumerate(records):
        if not isinstance(row, dict):
            failures.append(f"SOURCE_{i}_NOT_OBJECT")
            continue
        sid = row.get("source_id")
        if not nonempty(sid, 3) or sid in source_ids:
            failures.append(f"SOURCE_{i}_ID_MISSING_OR_DUPLICATED")
        source_ids.append(sid)
        if row.get("niche_id") != name:
            failures.append(f"SOURCE_{i}_CROSS_NICHE")
        cohort = row.get("cohort")
        if cohort not in {"DIRECT", "ADJACENT"}:
            failures.append(f"SOURCE_{i}_COHORT_UNCLASSIFIED")
        if cohort == "DIRECT":
            if row.get("direct_cohort_key") != profile["direct_cohort_key"]:
                failures.append(f"SOURCE_{i}_DIRECT_KEY_MISMATCH")
            direct.append(row)
        if not valid_time(row.get("observed_utc")):
            failures.append(f"SOURCE_{i}_NO_DATED_EVIDENCE")
        vid = video_id_from_url(row.get("video_url"))
        if vid is None or vid != row.get("video_id") or not re.fullmatch(r"[\w-]{11}", str(vid)):
            failures.append(f"SOURCE_{i}_INVALID_VIDEO_URL_OR_ID")
        if not nonempty(row.get("channel_id"), 3):
            failures.append(f"SOURCE_{i}_MISSING_CHANNEL_ID")
        if not nonempty(row.get("mechanism"), 30) or not nonempty(row.get("originality_difference"), 30):
            failures.append(f"SOURCE_{i}_NO_ABSTRACT_LEARNING_OR_CREATIVE_DIFFERENCE")
        mode = row.get("inspection_mode")
        if mode not in SOURCE_MODES:
            failures.append(f"SOURCE_{i}_INSPECTION_UNPROVEN")
        if mode in {"TRANSCRIPT_INSPECTED", "AUDIO_VIDEO_INSPECTED"}:
            intervals = row.get("inspected_intervals") or []
            if not isinstance(intervals, list) or not intervals or not all(
                isinstance(x, dict) and isinstance(x.get("start_s"), (int,float))
                and isinstance(x.get("end_s"), (int,float))
                and 0 <= x["start_s"] < x["end_s"] for x in intervals
            ):
                failures.append(f"SOURCE_{i}_INSPECTION_INTERVALS_MISSING")
            elif cohort == "DIRECT":
                inspected.append(row)
        if any(k in row for k in ("ctr", "rpm", "retention", "estimated_revenue")) and not row.get("authorized_private_evidence"):
            failures.append(f"SOURCE_{i}_UNVERIFIED_PRIVATE_COMPETITOR_METRICS")
        if row.get("views") is not None and (not isinstance(row["views"], int) or row["views"] < 0 or not valid_time(row.get("views_captured_utc"))):
            failures.append(f"SOURCE_{i}_VIEWS_WITHOUT_TIMESTAMP")
    if len({r.get("video_id") for r in direct}) < 2:
        failures.append("LESS_THAN_TWO_DISTINCT_DIRECT_PEER_VIDEOS")
    if not inspected:
        failures.append("NO_DEEP_INSPECTED_DIRECT_PEER")
    creative = brief.get("creative") or {}
    for field in policy["required_creative_fields"]:
        value = creative.get(field)
        if field == "originality_axes":
            if not isinstance(value, list) or len({str(x).strip().casefold() for x in value if nonempty(x, 8)}) < 3:
                failures.append("THREE_DISTINCT_ORIGINALITY_AXES_REQUIRED")
        elif field == "rights_inventory":
            if not isinstance(value, list) or not value or any(
                not isinstance(x, dict) or not x.get("asset_id") or
                not x.get("origin") or not x.get("license_or_right") or
                not x.get("evidence_location") for x in value
            ):
                failures.append("UNVERIFIED_ASSET_AND_AUDIO_RIGHTS")
        elif not nonempty(value, 22):
            failures.append("CREATIVE_FIELD_MISSING_" + field.upper())
    for signal in ("competitor_script_copied", "competitor_dialogue_paraphrased", "characters_traced_from_competitor", "repeat_template_as_entire_episode"):
        if creative.get(signal) is True:
            failures.append("UNORIGINAL_COPYING_RISK_" + signal.upper())
    learning = brief.get("learning") or []
    if not isinstance(learning, list) or not learning:
        failures.append("NO_RESEARCH_TO_ORIGINAL_CREATIVE_LEARNING")
    else:
        for i, h in enumerate(learning):
            if not isinstance(h, dict):
                failures.append(f"LEARNING_{i}_INVALID")
                continue
            linked = h.get("source_ids") or []
            if not linked or not set(linked).issubset({x for x in source_ids if isinstance(x, str)}):
                failures.append(f"LEARNING_{i}_SOURCE_PROVENANCE_INVALID")
            if not all(nonempty(h.get(x), 20) for x in ("abstract_mechanism", "own_original_application", "hypothesis_to_test")):
                failures.append(f"LEARNING_{i}_EMPTY_MECHANISM_APPLICATION_EXPERIMENT")
    platform = brief.get("youtube_policy_review") or {}
    for field, options in REQ_DECISIONS.items():
        d = platform.get(field)
        if not isinstance(d, dict) or d.get("decision") not in options or not nonempty(d.get("reason"), 25):
            failures.append("MISSING_POLICY_DECISION_" + field.upper())
        elif d["decision"] in REVIEW_VALUES:
            warnings.append("OWNER_REVIEW_REQUIRED_" + field.upper())
    if profile["requires_source_evidence"]:
        cited = creative.get("independent_factual_sources") or []
        if not isinstance(cited, list) or len(set(str(x) for x in cited)) < 2:
            failures.append("TWO_INDEPENDENT_FACT_SOURCES_REQUIRED")
    if profile["niche_mode"] == "FINANCE_EDUCATION" and not all(nonempty(creative.get(x), 2) for x in ("jurisdiction", "facts_as_of_utc")):
        failures.append("FINANCE_JURISDICTION_AND_ASOF_REQUIRED")
    if name == "magical_witch_family_stories":
        receipt = brief.get("bell_leaf_novelty_receipt") or {}
        if receipt.get("candidate") != brief.get("episode_id") or receipt.get("status") != "MANUAL_NOVELTY_REVIEW_REQUIRED":
            failures.append("BELL_LEAF_EPISODE_UNIQUENESS_GATE_NOT_ATTESTED")
    result = {
        "status": "BLOCKED" if failures else "INDEPENDENT_EDITORIAL_REVIEW_REQUIRED",
        "niche_id": name,
        "direct_peer_count": len({x.get("video_id") for x in direct}),
        "deep_inspected_direct_peer_count": len(inspected),
        "source_count": len(records),
        "blocking": sorted(set(failures)),
        "review_items": sorted(set(warnings)),
        "needs_human_review": True,
        "release_authorized": False,
        "production_authorized": False,
        "assurance": "Structural evidence checks only. Not YouTube, copyright, age or monetization approval.",
        "research_scope": "DIRECT peers isolated; ADJACENT sources excluded from direct baseline"
    }
    return result




def assess_learning_update(event: dict, policy: dict | None = None,
                           registry: dict | None = None) -> dict:
    """Validate OWNED analytics experiment before considering an editorial skill update.

    Does not fetch YouTube Studio, establish causal impact, or mutate skills.
    A formally valid record always remains human-review only.
    """
    policy = policy if policy is not None else read_json(POLICY)
    registry = registry if registry is not None else read_json(REGISTRY)
    niche = event.get("niche_id")
    problems = []
    if niche not in policy["profiles"] or niche not in {x["id"] for x in registry["niches"]}:
        problems.append("UNKNOWN_OR_UNROUTED_NICHE")
    if event.get("baseline_niche_id") != niche:
        problems.append("CROSS_NICHE_ANALYTICS_COMPARISON")
    if event.get("evidence_origin") != "OWNED_YOUTUBE_STUDIO":
        problems.append("OWNED_ANALYTICS_SOURCE_REQUIRED")
    for k in ("hypothesis", "experiment_id", "intervention", "confounders",
              "analysis_summary", "source_receipt_path", "reproducible_measurement_method"):
        if not nonempty(event.get(k), 20 if k != "experiment_id" else 4):
            problems.append("MISSING_LEARNING_FIELD_" + k.upper())
    if not valid_time(event.get("experiment_started_utc")):
        problems.append("MISSING_EXPERIMENT_START_DATE")
    if event.get("measurement_metric") not in {
        "INTRO_30S_RETENTION", "AVERAGE_VIEW_DURATION_SECONDS", "RETENTION_AT_CHAPTER",
        "RETURNING_VIEWER_RATE", "CTR_OWNED"}:
        problems.append("INVALID_OWNED_VIDEO_MEASUREMENT")
    baseline = event.get("baseline_videos") or []
    treatment = event.get("treatment_video") or {}
    if not isinstance(baseline, list) or len(baseline) < 5:
        problems.append("AT_LEAST_FIVE_SAME_FORMAT_BASELINE_VIDEOS_REQUIRED")
        baseline = []
    ids = [x.get("video_id") for x in baseline if isinstance(x, dict)]
    if len(ids) != len(set(ids)) or not all(isinstance(v, str) and len(v) == 11 for v in ids):
        problems.append("BASELINE_VIDEO_ID_DUPLICATE_OR_INVALID")
    if not isinstance(treatment, dict) or not treatment.get("video_id"):
        problems.append("MISSING_TREATMENT_VIDEO")
        treatment = {}
    if treatment.get("video_id") in ids:
        problems.append("TREATMENT_VIDEO_MUST_BE_OUTSIDE_BASELINE")
    duration = treatment.get("duration_seconds")
    if not isinstance(duration, (float, int)) or duration <= 0:
        problems.append("TREATMENT_DURATION_REQUIRED")
    all_rows = baseline + [treatment]
    for idx, row in enumerate(all_rows):
        if not isinstance(row, dict):
            problems.append(f"METRIC_{idx}_INVALID_OBJECT")
            continue
        if row.get("niche_id") != niche:
            problems.append(f"METRIC_{idx}_CROSS_NICHE")
        if row.get("owned_channel_id") != event.get("owned_channel_id") or not row.get("owned_channel_id"):
            problems.append(f"METRIC_{idx}_CROSS_CHANNEL_OR_UNKNOWN_CHANNEL")
        if not valid_time(row.get("captured_utc")):
            problems.append(f"METRIC_{idx}_UNVERIFIED_SNAPSHOT_DATE")
        val = row.get("value")
        if not isinstance(val, (int, float)) or val < 0:
            problems.append(f"METRIC_{idx}_INVALID_VALUE")
        elif event.get("measurement_metric") in {"INTRO_30S_RETENTION", "RETURNING_VIEWER_RATE", "RETENTION_AT_CHAPTER", "CTR_OWNED"} and val > 1:
            problems.append(f"METRIC_{idx}_PERCENT_MUST_BE_FRACTION_0_TO_1")
        d = row.get("duration_seconds")
        if not isinstance(d, (float, int)) or d <= 0:
            problems.append(f"METRIC_{idx}_MISSING_DURATION")
        elif isinstance(duration, (float, int)) and duration > 0 and abs(d-duration) / duration > 0.2:
            problems.append(f"METRIC_{idx}_NOT_SIMILAR_FORMAT_LENGTH")
    change = event.get("proposed_skill_change") or {}
    if not isinstance(change, dict) or not nonempty(change.get("reason"), 25) or not change.get("rollback_reference"):
        problems.append("SKILL_CHANGE_REASON_AND_ROLLBACK_REQUIRED")
    elif not str(change.get("file", "")).startswith((".claude/skills/", ".agents/skills/")):
        problems.append("LEARNING_SKILL_CHANGE_PATH_NOT_ALLOWED")
    if not nonempty(event.get("reviewer_id"), 3) or event.get("reviewer_id") == event.get("researcher_id"):
        problems.append("INDEPENDENT_LEARNING_REVIEWER_REQUIRED")
    return {
        "status": "BLOCKED" if problems else "INDEPENDENT_LEARNING_REVIEW_REQUIRED",
        "niche_id": niche,
        "blocking": sorted(set(problems)),
        "baseline_count": len(baseline),
        "release_authorized": False,
        "skill_auto_update_authorized": False,
        "note": "Self-declared analytics source and reviewer are not externally authenticated. Independent analysis, owner approval and rollback verification required.",
    }

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("inventory", "preflight", "learning"))
    parser.add_argument("--brief", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "inventory":
            result = inventory(read_json(POLICY), read_json(REGISTRY))
        elif not args.brief:
            result = {"status": "BLOCKED", "blocking": ["MISSING_BRIEF"], "release_authorized": False}
        elif args.command == "learning":
            result = assess_learning_update(read_json(args.brief))
        else:
            result = assess(read_json(args.brief))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result = {"status": "BLOCKED_DATA_ERROR", "reason": str(exc), "release_authorized": False}
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True, indent=2))  # Windows cp1252 safe
    if result.get("status") in {"BLOCKED", "BLOCKED_DATA_ERROR"} or result.get("ready_for_data_import") is False:
        return 2
    # Zero only means structurally ready for independent review, never publish-ready.
    return 0


if __name__ == "__main__":
    sys.exit(main())
