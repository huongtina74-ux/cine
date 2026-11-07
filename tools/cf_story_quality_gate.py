#!/usr/bin/env python3
"""CINE Story Quality Gate: causal writing, continuity and cross-episode memory.

Strict, deterministic preflight only. Does NOT write screenplays, authenticate
reviewers, certify story originality, approve copyright, or release YouTube video.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "config/research/per_niche/niches.json"
PROFILES = ROOT / "config/story_factory/story_quality_profiles_v1.json"
LEDGER_ROOT = ROOT / "data/story_quality"
ID_RX = re.compile(r"^[a-z0-9_][a-z0-9_-]{2,80}$")
EP_RX = re.compile(r"^(?:BL-\d{4}|[A-Za-z][\w-]{2,64})$")
TOKEN_RX = re.compile(r"[^\W_]+", re.UNICODE)


def textnorm(s: str) -> str:
    return " ".join(TOKEN_RX.findall(unicodedata.normalize("NFKC", s).casefold()))


def tokens(s: str) -> set[str]:
    return set(textnorm(s).split())


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    o = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(o, dict):
        raise ValueError("Required JSON object at " + str(path))
    return o


def fail_code(msg: str) -> dict:
    return {"status": "BLOCKED", "blocking": [msg], "production_authorized": False,
            "editorial_approval": False}


def load_profiles() -> dict:
    d = read_json(PROFILES)
    known = {x["id"] for x in read_json(REGISTER)["niches"]}
    if set(d["niches"]) != known:
        raise ValueError("Story quality profiles and CINE research niche IDs are not equal")
    if len(d["niches"]) != len(known):
        raise ValueError("Duplicate/missing niche quality profiles")
    return d


def _valid_id(value: object) -> bool:
    return isinstance(value, str) and bool(ID_RX.fullmatch(value))


def _enough(value: object, n: int = 30) -> bool:
    return isinstance(value, str) and len(textnorm(value)) >= n


def ledger_file(niche_id: str, series_id: str, root: Path = LEDGER_ROOT) -> Path:
    if not _valid_id(niche_id) or not _valid_id(series_id):
        raise ValueError("Invalid niche_id or series_id for canonical ledger path")
    return root / niche_id / series_id / "approved_episodes.jsonl"


def load_ledger(niche_id: str, series_id: str, root: Path = LEDGER_ROOT) -> list[dict]:
    path = ledger_file(niche_id, series_id, root)
    if not path.exists():
        return []
    entries, seen = [], set()
    for no, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            raise ValueError(f"Blank/partial ledger record line {no}")
        o = json.loads(line)
        if o.get("niche_id") != niche_id or o.get("series_id") != series_id:
            raise ValueError(f"Cross-niche record in {path.name} line {no}")
        key = o.get("episode_id")
        if key in seen:
            raise ValueError(f"Duplicate approved episode in ledger: {key}")
        if o.get("status") != "EDITORIAL_SIGNOFF_RECORDED":
            raise ValueError("Non-approved data in approved-episode ledger")
        seen.add(key)
        entries.append(o)
    return entries


def _phrase_overlap(a: str, b: str) -> float:
    aa, bb = tokens(a), tokens(b)
    if not aa or not bb:
        return 0.0
    return len(aa & bb) / max(1, len(aa | bb))


def compare_episodes(plan: dict, entries: list[dict]) -> list[dict]:
    target = plan["story"]
    matches = []
    compare_fields = ("hook", "goal", "central_conflict", "twist", "resolution",
                      "emotional_change", "lasting_consequence")
    for entry in entries:
        if entry["episode_id"] == plan["episode_id"]:
            # Existing record must be re-edited with a versioned new ledger,
            # not silently overwritten by another episode with same ID.
            matches.append({"episode_id": entry["episode_id"], "level": "EXISTING_APPROVED_ID",
                            "matched_axes": ["EPISODE_ID"], "risk_score": 1.0})
            continue
        prior = entry.get("story_fingerprint") or {}
        pairs = []
        for field in compare_fields:
            a, b = textnorm(target.get(field, "")), textnorm(prior.get(field, ""))
            if not a or not b:
                continue
            if a == b:
                pairs.append((field, 1.0))
            elif len(a) >= 50 and len(b) >= 50:
                sim = max(_phrase_overlap(a, b),
                          SequenceMatcher(None, a, b, autojunk=False).ratio())
                if sim >= 0.82:
                    pairs.append((field, round(sim, 4)))
        # A single shared genre or word is NOT sufficient to label duplicate.
        if pairs:
            weight = {"central_conflict": 3, "resolution": 3, "twist": 2, "goal": 2,
                      "hook": 2, "emotional_change": 1, "lasting_consequence": 1}
            score = sum(weight[k] * v for k, v in pairs) / sum(weight.values())
            high = sum(1 for k, v in pairs if k in {"central_conflict", "resolution", "twist", "goal"} and v >= .90)
            level = ("BLOCK_DUPLICATE" if high >= 2 or (high >= 1 and score >= .32)
                     else "EDITOR_REVIEW_SIMILARITY")
            matches.append({"episode_id": entry["episode_id"], "level": level,
                            "matched_axes": [k for k, _ in pairs], "risk_score": round(score, 4)})
    return sorted(matches, key=lambda r: (r["level"] == "BLOCK_DUPLICATE",
                                         r["level"] == "EXISTING_APPROVED_ID",
                                         r["risk_score"]), reverse=True)


def _legacy_archive_module(project_root: Path):
    # Test harnesses also load this module by explicit file location.
    import importlib.util
    src = project_root / "tools/cf_story_archive_scan.py"
    if not src.is_file():
        raise ValueError("Legacy screenplay scanner missing from CINE")
    spec = importlib.util.spec_from_file_location("cine_story_archive_scan", src)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def evaluate(plan: dict, *, ledger_root: Path = LEDGER_ROOT,
             check_bell_leaf_proposals: bool = True,
             project_root: Path = ROOT,
             historical_root: Path | None = None,
             exclude_project_id: str | None = None) -> dict:
    """Evaluate structural story logic and prior episodes; no editorial PASS asserted."""
    errors, warnings = [], []
    p = load_profiles()
    niche, series = plan.get("niche_id"), plan.get("series_id")
    profile = p["niches"].get(niche)
    if not profile:
        return fail_code("Niche not registered: no cross-niche inheritance permitted")
    if not _valid_id(series):
        return fail_code("Missing or invalid series_id; stable series memory key mandatory")
    episode_id = plan.get("episode_id")
    if not isinstance(episode_id, str) or not EP_RX.fullmatch(episode_id):
        errors.append("INVALID_EPISODE_ID")
    if niche == "magical_witch_family_stories":
        if series != "bell_leaf" or not re.fullmatch(r"BL-\d{4}", str(episode_id)):
            errors.append("BELL_LEAF_WRONG_SERIES_OR_EPISODE_TAG")
        source = plan.get("canon") or {}
        if source.get("owner_source_lock") != "FOUR_OWNER_TEXTS_20261107":
            errors.append("BELL_LEAF_OWNER_LOCK_NOT_ATTESTED")
        if not source.get("visual_canon_reference"):
            errors.append("BELL_LEAF_VISUAL_CANON_SOURCE_MISSING")
        if source.get("canon_mutations") not in ([], None):
            errors.append("BELL_LEAF_UNAPPROVED_CANON_MUTATION")
    elif series == "bell_leaf":
        errors.append("BELL_LEAF_MUST_USE_MAGICAL_WITCH_FAMILY_NICHE")
    story = plan.get("story")
    required_story = ("title", "hook", "goal", "central_conflict", "stakes", "theme",
                      "twist", "resolution", "emotional_change", "lasting_consequence",
                      "why_this_episode", "originality_difference")
    if not isinstance(story, dict):
        story = {}
    for key in required_story:
        if not _enough(story.get(key), 27):
            errors.append("STORY_UNDERDEVELOPED_" + key.upper())
    # Audit authorship of cause/effect beats, NOT mere titles.
    beats = plan.get("beats")
    if not isinstance(beats, list) or len(beats) < 12:
        errors.append("MIN_12_SUBSTANTIAL_BEATS_REQUIRED")
        beats = beats if isinstance(beats, list) else []
    ids, last_end, unique_kinds = set(), 0, set()
    for i, b in enumerate(beats):
        if not isinstance(b, dict):
            errors.append(f"BEAT_{i}_NOT_OBJECT")
            continue
        name = b.get("beat_id")
        if not isinstance(name, str) or not re.fullmatch(r"B\d{2,3}", name) or name in ids:
            errors.append(f"BEAT_{i}_INVALID_OR_DUPLICATE_ID")
        start, end = b.get("start_s"), b.get("end_s")
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)) or start != last_end or end <= start:
            errors.append(f"BEAT_{i}_BAD_TIMING_OR_GAP")
        if isinstance(end, (int, float)):
            last_end = end
        kind = b.get("kind")
        unique_kinds.add(kind) if isinstance(kind, str) else None
        if not all(_enough(b.get(k), 16) for k in ("visible_action", "obstacle", "character_choice",
                                                 "immediate_consequence")):
            errors.append(f"BEAT_{i}_INCOMPLETE_ACTION_LOGIC")
        if i and (not isinstance(b.get("caused_by"), list) or not b["caused_by"] or
                  not all(x in ids for x in b["caused_by"])):
            errors.append(f"BEAT_{i}_LACKS_PREVIOUS_CAUSAL_TRIGGER")
        if not _enough(b.get("because"), 14):
            errors.append(f"BEAT_{i}_NO_CAUSAL_JUSTIFICATION")
        if isinstance(name, str):
            ids.add(name)
    if len(unique_kinds & {"HOOK", "GOAL", "DISCOVERY", "REVERSAL", "CRISIS", "CLIMAX",
                           "RESOLUTION", "AFTERMATH"}) < 6:
        errors.append("BEAT_ARC_LACKS_SIX_DISTINCT_FUNCTIONS")
    # A 45-minute episode needs genuinely distinct story progression, not 12
    # copies of the same character choice with numbered labels.
    for field in ("obstacle", "character_choice", "immediate_consequence"):
        distinct = Counter(textnorm(b.get(field, "")) for b in beats if isinstance(b, dict))
        if distinct and max(distinct.values()) >= 4:
            errors.append("REPEATED_BEAT_" + field.upper() + "_TEMPLATE")
    target = plan.get("target_minutes")
    lo, hi = profile["duration_minutes"]
    if (not isinstance(target, (int, float)) or isinstance(target, bool) or
            not lo <= target <= hi or last_end != round(target * 60)):
        errors.append("DURATION_OR_BEAT_TOTAL_OUTSIDE_NICHE_FORMAT")
    # Independent, concrete scene cards and character decision arcs:
    # a beat list alone is not a full 45-minute screenplay architecture.
    scenes = plan.get("scenes")
    min_scenes = min(30, max(6, int(target * .4))) if isinstance(target, (float,int)) and not isinstance(target, bool) else 6
    if not isinstance(scenes, list) or len(scenes) < min_scenes:
        errors.append("MIN_" + str(min_scenes) + "_SCENE_CARDS_REQUIRED")
        scenes = scenes if isinstance(scenes, list) else []
    scene_last_end, scene_ids = 0, set()
    for i, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            errors.append(f"SCENE_{i}_INVALID")
            continue
        scene_id = scene.get("scene_id")
        if (not isinstance(scene_id,str) or not re.fullmatch(r"SC-\d{3,4}",scene_id)
                or scene_id in scene_ids):
            errors.append(f"SCENE_{i}_DUPLICATE_OR_INVALID_ID")
        else:
            scene_ids.add(scene_id)
        start,end = scene.get("start_s"),scene.get("end_s")
        if (not isinstance(start,(int,float)) or not isinstance(end,(int,float))
                or start != scene_last_end or end <= start):
            errors.append(f"SCENE_{i}_TIMING_GAP_OR_OVERLAP")
        if isinstance(end,(int,float)):
            scene_last_end = end
        if scene.get("beat_id") not in ids:
            errors.append(f"SCENE_{i}_NOT_CONNECTED_TO_BEAT")
        for field in ("location","scene_purpose","observable_character_action",
                      "new_information_or_change"):
            if not _enough(scene.get(field), 16):
                errors.append(f"SCENE_{i}_MISSING_" + field.upper())
    if isinstance(target,(float,int)) and not isinstance(target,bool) and scene_last_end != round(target * 60):
        errors.append("SCENE_TIMELINE_DOES_NOT_COVER_EPISODE")
    character_arcs = plan.get("character_arcs")
    if not isinstance(character_arcs,list) or not character_arcs:
        errors.append("MISSING_CHARACTER_DECISION_ARC")
        character_arcs = []
    for i, arc in enumerate(character_arcs):
        if not isinstance(arc,dict):
            errors.append(f"CHARACTER_ARC_{i}_INVALID")
            continue
        if not arc.get("character") or arc.get("turning_beat") not in ids:
            errors.append(f"CHARACTER_ARC_{i}_UNSUPPORTED_TURN")
        for field in ("initial_state","internal_need","costly_decision","final_state"):
            if not _enough(arc.get(field),18):
                errors.append(f"CHARACTER_ARC_{i}_MISSING_" + field.upper())
        if textnorm(str(arc.get("initial_state",""))) == textnorm(str(arc.get("final_state",""))):
            errors.append(f"CHARACTER_ARC_{i}_NO_CHANGE")

    payoffs = plan.get("setup_payoffs")
    if not isinstance(payoffs, list) or len(payoffs) < 3:
        errors.append("MIN_3_SEEDED_SETUP_PAYOFF_PAIRS")
        payoffs = payoffs if isinstance(payoffs, list) else []
    beat_order = {b.get("beat_id"): i for i, b in enumerate(beats) if isinstance(b, dict)}
    for i, item in enumerate(payoffs):
        if not isinstance(item, dict):
            errors.append(f"PAYOFF_{i}_INVALID")
            continue
        setup, payoff = item.get("setup_beat"), item.get("payoff_beat")
        if setup not in beat_order or payoff not in beat_order or beat_order[setup] >= beat_order[payoff]:
            errors.append(f"PAYOFF_{i}_UNSEEDED_OR_BACKWARDS")
        if not _enough(item.get("specific_clue"), 22) or not _enough(item.get("earned_resolution"), 22):
            errors.append(f"PAYOFF_{i}_LACKS_CLUE_AND_EARNED_ACTION")
    changes = plan.get("continuity_deltas")
    if not isinstance(changes, list) or len(changes) < 2:
        errors.append("MIN_2_REAL_CONTINUITY_CHANGES")
        changes = changes if isinstance(changes, list) else []
    for i, c in enumerate(changes):
        if not isinstance(c, dict):
            errors.append(f"DELTA_{i}_INVALID")
            continue
        if not c.get("entity_id") or c.get("after") == c.get("before") or not _enough(c.get("after"), 12):
            errors.append(f"DELTA_{i}_NO_STATE_CHANGE")
        if c.get("caused_by") not in beat_order:
            errors.append(f"DELTA_{i}_NO_PROVEN_CAUSE")
    if not isinstance(plan.get("editorial_questions"), list) or len(plan["editorial_questions"]) < 3:
        errors.append("MISSING_INDEPENDENT_EDITORIAL_CHALLENGES")
    if not isinstance(plan.get("creative_axes"), list) or len({
        textnorm(x) for x in plan["creative_axes"] if isinstance(x, str) and _enough(x, 12)
    }) < 3:
        errors.append("THREE_ORIGINALITY_AXES_REQUIRED")
    if niche == "magical_witch_family_stories":
        legal = {"EVAN", "MARA", "JUNO", "LIA", "BIX", "BUBU", "ORIN",
                 "GRANDPA_EARTH", "GRANDMA_EARTH", "ELARA"}
        cast = plan.get("approved_character_tags") or []
        if not cast or any(x not in legal for x in cast):
            errors.append("BELL_LEAF_CAST_NOT_OWNER_VERIFIED")
        for i, beat in enumerate(beats):
            if not isinstance(beat, dict):
                continue
            travel = beat.get("travel")
            if travel is None:
                continue
            if not isinstance(travel, dict):
                errors.append(f"BEAT_{i}_INVALID_GATE_OBJECT")
                continue
            route = travel.get("route")
            if route == "OLD":
                if travel.get("mechanism") != "REPAIRED_FIXED_STATION" or not travel.get("verified_route"):
                    errors.append(f"BEAT_{i}_OLD_WORLD_MUST_USE_REPAIRED_STATION")
            elif route == "NEW":
                if travel.get("mechanism") != "BUBU_ECHO" or not travel.get("specific_echo"):
                    errors.append(f"BEAT_{i}_UNKNOWN_WORLD_REQUIRES_ECHO")
                if travel.get("exit_safety") is None:
                    errors.append(f"BEAT_{i}_NO_SAFE_EXIT_PLAN")
            elif route not in {"EARTH", "NONE"}:
                errors.append(f"BEAT_{i}_ARBITRARY_TELEPORT_NOT_ALLOWED")
    try:
        entries = load_ledger(niche, series, ledger_root)
    except (ValueError, OSError, json.JSONDecodeError) as e:
        errors.append("APPROVED_EPISODE_LEDGER_CORRUPT_" + str(e))
        entries = []
    # Verify episode-to-episode factual state: a person, object or gate
    # cannot silently revert to its earlier state in the next script.
    latest_state = {}
    for prior in entries:
        for state in prior.get("continuity_deltas", []):
            if isinstance(state, dict) and state.get("entity_id") and isinstance(state.get("after"), str):
                latest_state[state["entity_id"]] = state["after"]
    for i, delta in enumerate(changes):
        if not isinstance(delta, dict):
            continue
        entity = delta.get("entity_id")
        if entity in latest_state and textnorm(str(delta.get("before", ""))) != textnorm(latest_state[entity]):
            errors.append(f"CONTINUITY_STATE_CONTRADICTS_APPROVED_HISTORY_{i}_{entity}")
    dependencies = plan.get("depends_on_approved_episodes", [])
    if not isinstance(dependencies, list):
        errors.append("EPISODE_DEPENDENCIES_MUST_BE_A_LIST")
        dependencies = []
    known_episodes = {item["episode_id"] for item in entries}
    if any(not isinstance(key, str) or key not in known_episodes for key in dependencies):
        errors.append("EPISODE_DEPENDS_ON_UNAPPROVED_OR_MISSING_EPISODE")
    matches = compare_episodes(plan, entries) if not any(x.startswith("INVALID_EPISODE") for x in errors) else []
    if any(x["level"] in {"EXISTING_APPROVED_ID", "BLOCK_DUPLICATE"} for x in matches):
        errors.append("DUPLICATES_PRIOR_APPROVED_EPISODE")
    archive_matches = []
    archive_count = 0
    archive_status = "NOT_SCANNED"
    try:
        old = _legacy_archive_module(project_root)
        archive = old.scan(niche, archive_root=historical_root or
                           (project_root / "data/script_factory/projects"),
                           exclude_project_id=exclude_project_id)
        archive_status = archive["status"]
        archive_count = len(archive["historical_records"])
        archive_matches = old.compare_plan(plan, archive)
        if any(x["level"] == "BLOCK_HISTORICAL_STORY_COPY" for x in archive_matches):
            errors.append("DUPLICATES_HISTORICAL_PROJECT_OUTLINE")
        if archive_status == "ARCHIVE_NOT_MOUNTED":
            warnings.append("HISTORICAL_SCRIPT_ARCHIVE_NOT_MOUNTED")
        for entry in archive["historical_records"]:
            if entry["status"] == "STALE_SCRIPT_SHA_STAGE_ATTESTATION":
                warnings.append("HISTORICAL_PROJECT_SHA_STALE_" + entry["project_id"])
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as e:
        errors.append("HISTORICAL_PROJECT_ARCHIVE_UNREADABLE_" + str(e))
    proposal_status = "NOT_APPLICABLE"
    if niche == "magical_witch_family_stories" and check_bell_leaf_proposals and not errors:
        import importlib.util
        path = project_root / "tools/bell_leaf/episode_uniqueness_gate.py"
        if not path.is_file():
            errors.append("BELL_LEAF_1000_IDEA_REGISTRY_NOT_AVAILABLE")
        else:
            spec = importlib.util.spec_from_file_location("bell_leaf_duplicate", path)
            module = importlib.util.module_from_spec(spec)
            assert spec.loader
            spec.loader.exec_module(module)
            candidate = {
                "episode_id": str(episode_id), "title": story.get("title", ""),
                "lead": (plan.get("approved_character_tags") or [""])[0],
                "setting_class": plan.get("setting_class", ""),
                "hook": story.get("hook", ""), "goal": story.get("goal", ""),
                "conflict": story.get("central_conflict", ""),
                "twist": story.get("twist", ""), "resolution": story.get("resolution", ""),
                "continuity_delta": story.get("lasting_consequence", ""),
            }
            try:
                outcome = module.compare(candidate, module.load(
                    project_root / "docs/story/bell_leaf/slates/BELL_LEAF_1000_EPISODE_INDEX_PROPOSAL_20261107.csv",
                    project_root / "docs/story/bell_leaf/slates/BELL_LEAF_1000_EPISODE_DEVELOPMENT_SLATE_UNAPPROVED_20261107.md"))
            except (OSError, ValueError) as e:
                errors.append("BELL_LEAF_IDEA_REGISTRY_UNAVAILABLE_" + str(e))
            else:
                proposal_status = outcome["status"]
                if proposal_status == "BLOCKED":
                    errors.append("BELL_LEAF_PROPOSAL_NOVELTY_COLLISION")
                if outcome.get("matches_total"):
                    warnings.append("REVIEW_SIMILAR_PROPOSALS_" + str(outcome["matches_total"]))
    return {
        "status": "BLOCKED" if errors else "INDEPENDENT_STORY_EDITOR_REVIEW_REQUIRED",
        "niche_id": niche, "series_id": series, "episode_id": episode_id,
        "blocking": sorted(set(errors)), "warnings": sorted(set(warnings)),
        "similar_approved_episodes": matches[:20],
        "legacy_project_matches": archive_matches[:20],
        "historical_script_archive_count": archive_count,
        "historical_archive_scan_status": archive_status,
        "approved_ledger_count": len(entries),
        "bell_leaf_proposal_gate": proposal_status,
        "automated_story_approval": False, "youtube_release_authorized": False,
        "disclaimer": "Structural/lexical checks only. A human must evaluate plausibility, inspiration, emotion, originality, continuity and script quality.",
    }


def _writer_review(path: Path, manifest: dict) -> None:
    reviewer = read_json(path)
    if reviewer.get("reviewer_id") in (None, "", manifest.get("writer_id")):
        raise ValueError("STORY_EDITOR_NOT_INDEPENDENT_FROM_WRITER")
    script = path.parent.parent / "06_script/script.md"
    if not script.is_file() or reviewer.get("reviewed_script_sha256") != digest(script):
        raise ValueError("STORY_REVIEW_SCRIPT_SHA_STALE")
    if reviewer.get("verdict") != "PASS" or not isinstance(reviewer.get("evidence_notes"), list) or len(reviewer["evidence_notes"]) < 3:
        raise ValueError("STORY_EDITOR_REVIEW_REQUIRED_WITH_THREE_EVIDENCE_NOTES")
    fields = reviewer.get("checklist") or {}
    for key in ("causality", "character_agency", "setup_payoff", "originality",
                "continuity", "distinct_emotional_resolution", "niche_fit"):
        if fields.get(key) != "PASS":
            raise ValueError("STORY_REVIEW_INCOMPLETE_" + key.upper())


def require_factory_stage(base: Path, manifest: dict, stage: str,
                          project_root: Path = ROOT) -> None:
    if manifest.get("story_quality_contract_version") != "1":
        raise ValueError("NEW_EPISODE_MISSING_STORY_QUALITY_CONTRACT")
    if stage not in {"outline", "script", "review", "final"}:
        return
    path = base / "05_outline/episode_quality_plan.json"
    if not path.is_file():
        raise ValueError("MISSING_EPISODE_QUALITY_PLAN")
    plan = read_json(path)
    if plan.get("niche_id") != manifest.get("niche_id") or plan.get("target_minutes") != manifest.get("target_minutes"):
        raise ValueError("STORY_QUALITY_PROJECT_ID_OR_FORMAT_MISMATCH")
    if manifest.get("mode") not in load_profiles()["niches"][manifest["niche_id"]]["allowed_factory_modes"]:
        raise ValueError("STORY_QUALITY_WRONG_SCRIPT_MODE_FOR_NICHE")
    if manifest.get("episode_id") and plan.get("episode_id") != manifest["episode_id"]:
        raise ValueError("STORY_QUALITY_EPISODE_ID_MISMATCH")
    result = evaluate(plan, project_root=project_root,
                      exclude_project_id=manifest.get("project_id"))
    if result["status"] == "BLOCKED":
        raise ValueError("STORY_QUALITY_BLOCKED_" + "|".join(result["blocking"][:8]))
    if stage in {"script", "review", "final"}:
        script = base / "06_script/script.md"
        if not script.is_file():
            raise ValueError("STORY_SCREENPLAY_MISSING")
        body = script.read_text(encoding="utf-8-sig")
        # Native screenplay may use Fountain scene headings, but a new
        # episode must expose explicit beat IDs for machine traceability.
        ids = {b["beat_id"] for b in plan["beats"]}
        referenced = {bid for bid in ids if re.search(r"\b"+re.escape(bid)+r"\b", body)}
        if len(referenced) < min(10, len(ids)):
            raise ValueError("SCRIPT_MISSING_OUTLINE_BEAT_TRACE_IDS")
        scene_ids = {s["scene_id"] for s in plan["scenes"]}
        missing_scenes = [x for x in scene_ids if not re.search(r"\b"+re.escape(x)+r"\b", body)]
        if missing_scenes:
            raise ValueError("SCRIPT_SCENE_TRACE_MISSING_" + ",".join(missing_scenes[:5]))
        minimum_words = max(450, int(manifest["target_minutes"] * 42))
        if len(body) < 6000 or len(body.split()) < minimum_words:
            raise ValueError("FULL_SCRIPT_UNDERDEVELOPED_NOT_ENOUGH_WORDS_FOR_TARGET_RUNTIME")
        lines = [textnorm(x) for x in body.splitlines() if len(textnorm(x)) >= 40]
        if lines and max(Counter(lines).values()) > 5:
            raise ValueError("REPEATED_SCREENPLAY_SCENE_OR_DIALOGUE_TEMPLATE")
    if stage in {"review", "final"}:
        _writer_review(base / "07_review/story_quality_review.json", manifest)


def offer_ideas(niche_id: str, series_id: str, count: int = 10,
                ledger_root: Path = LEDGER_ROOT, slot: str = "initial") -> dict:
    """Offer compositional *directions*, never 10 automatic repetitive scripts."""
    p = load_profiles()
    if niche_id not in p["niches"] or not _valid_id(series_id):
        return fail_code("UNKNOWN_NICHE_OR_SERIES")
    if niche_id == "magical_witch_family_stories" and series_id != "bell_leaf":
        return fail_code("BELL_LEAF_REQUIRED_SERIES")
    profile = p["niches"][niche_id]
    axes = profile["idea_axes"]
    old = load_ledger(niche_id, series_id, ledger_root)
    blocked = {o.get("seed_signature") for o in old if o.get("seed_signature")}
    directions, seen = [], set()
    # Reproducible broad rotation. Deterministic, not a viral/story generator.
    slot = slot.casefold() if isinstance(slot, str) else ""
    if not _valid_id(slot):
        return fail_code("INVALID_IDEA_DEVELOPMENT_SLOT")
    salt = int(hashlib.sha256((niche_id+"|"+series_id+"|"+slot).encode()).hexdigest()[:8], 16)
    shift = salt % len(axes["conflict"])
    for k in range(count * 12 + 300):
        character = axes["perspective"][(k * 3 + k // 7 + salt//11) % len(axes["perspective"])]
        world = axes["setting"][(k * 3 + k // 11 + salt//17) % len(axes["setting"])]
        conflict = axes["conflict"][(k + shift) % len(axes["conflict"])]
        cost = axes["choice_cost"][(k * 7 + k // 13 + salt//19) % len(axes["choice_cost"])]
        genre = axes["emotion"][(k * 11 + k // 5 + salt//23) % len(axes["emotion"])]
        signature = hashlib.sha256(("|".join((character,world,conflict,cost,genre))).encode()).hexdigest()[:16]
        if signature in blocked or signature in seen:
            continue
        seen.add(signature)
        directions.append({
            "seed_signature": signature, "status": "IDEA_SEED_ONLY_NOT_SCREENPLAY",
            "perspective": character, "setting": world, "conflict": conflict,
            "hard_choice_or_cost": cost, "emotional_mode": genre,
            "writer_must_determine": ["unique inciting event", "physical causal chain",
                                       "specific witnesses/clues", "earned solution",
                                       "specific independent emotional change",
                                       "canon timeline and continuity consequences",
                                       "niche source evidence and originality review"],
        })
        if len(directions) == count:
            break
    return {
        "status": "IDEA_SEEDS_NEED_WRITER_DEVELOPMENT" if len(directions) == count else "IDEA_BANK_EXHAUSTED_OR_MISSING_VARIETY",
        "niche_id": niche_id, "series_id": series_id, "development_slot": slot,
        "known_approved_episode_count": len(old), "directions": directions,
        "not_a_script": True, "youtube_release_authorized": False,
    }


def append_reviewed_episode(plan_path: Path, review_path: Path,
                            ledger_root: Path = LEDGER_ROOT,
                            project_root: Path = ROOT) -> dict:
    """Explicit human-recording CLI only; never called by normal script generation."""
    plan, receipt = read_json(plan_path), read_json(review_path)
    report = evaluate(plan, ledger_root=ledger_root, project_root=project_root)
    if report["status"] != "INDEPENDENT_STORY_EDITOR_REVIEW_REQUIRED":
        raise ValueError("CANNOT_REGISTER_STORY_WITH_BLOCKING_QC")
    if receipt.get("verdict") != "PASS" or not receipt.get("reviewer_id") or not receipt.get("author_id"):
        raise ValueError("INDEPENDENT_REVIEW_NOT_DOCUMENTED")
    if receipt["reviewer_id"] == receipt["author_id"] or receipt.get("plan_sha256") != digest(plan_path):
        raise ValueError("UNVERIFIED_REVIEWER_OR_STALE_PLAN")
    if len(receipt.get("evidence_notes", [])) < 3 or not receipt.get("owner_approval_reference"):
        raise ValueError("MISSING_EDITORIAL_EVIDENCE_OR_OWNER_APPROVAL_REFERENCE")
    evidence = receipt.get("evidence_file")
    if not evidence or not Path(evidence).is_file() or receipt.get("evidence_sha256") != digest(Path(evidence)):
        raise ValueError("MISSING_INDEPENDENT_EVIDENCE_FILE_HASH")
    ledger = ledger_file(plan["niche_id"], plan["series_id"], ledger_root)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    lock = ledger.with_suffix(".lock")
    try:
        handle = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as e:
        raise ValueError("LEDGER_LOCKED_BY_ANOTHER_WRITER") from e
    try:
        os.close(handle)
        # Race excluded for cooperating processes via O_EXCL.
        prior = load_ledger(plan["niche_id"], plan["series_id"], ledger_root)
        if any(x["episode_id"] == plan["episode_id"] for x in prior):
            raise ValueError("EXISTING_EPISODE_CANNOT_BE_OVERWRITTEN")
        final = evaluate(plan, ledger_root=ledger_root, project_root=project_root)
        if final["status"] == "BLOCKED":
            raise ValueError("STORY_CHANGED_DURING_REGISTER")
        o = {
            "niche_id": plan["niche_id"], "series_id": plan["series_id"],
            "episode_id": plan["episode_id"], "title": plan["story"]["title"],
            "status": "EDITORIAL_SIGNOFF_RECORDED", "plan_sha256": digest(plan_path),
            "review_sha256": digest(review_path),
            "reviewer_id": receipt["reviewer_id"], "owner_approval_reference": receipt["owner_approval_reference"],
            "seed_signature": plan.get("seed_signature"),
            "story_fingerprint": {k: plan["story"].get(k, "") for k in
                                  ("hook", "goal", "central_conflict", "twist",
                                   "resolution", "emotional_change", "lasting_consequence")},
            "continuity_deltas": plan["continuity_deltas"],
            "source_qualified": False, "real_reviewer_identity_authenticated": False,
        }
        with ledger.open("a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(o, ensure_ascii=False, separators=(",", ":")) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return {"status": "EDITORIAL_RECORD_APPENDED", "episode_id": plan["episode_id"],
                "approved_ledger_count": len(prior)+1,
                "notice": "Receipts structurally verified, reviewer identity not authenticated by CLI."}
    finally:
        lock.unlink(missing_ok=True)


def cli(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=("ideas", "check", "register"))
    ap.add_argument("--niche", default="magical_witch_family_stories")
    ap.add_argument("--series", default="bell_leaf")
    ap.add_argument("--count", type=int, default=12)
    ap.add_argument("--slot", default="initial", help="unique planned episode/season slot for fresh deterministic idea seeds")
    ap.add_argument("--plan", type=Path)
    ap.add_argument("--review", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--ledger-root", type=Path, default=LEDGER_ROOT)
    args = ap.parse_args(argv)
    try:
        if args.command == "ideas":
            if not 1 <= args.count <= 50:
                raise ValueError("Idea seed count must be 1..50")
            result = offer_ideas(args.niche, args.series, args.count, args.ledger_root, args.slot)
        elif args.command == "check":
            if not args.plan:
                raise ValueError("--plan required")
            result = evaluate(read_json(args.plan), ledger_root=args.ledger_root)
        else:
            if not args.plan or not args.review:
                raise ValueError("--plan and --review required")
            result = append_reviewed_episode(args.plan, args.review, args.ledger_root)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        result = fail_code("INVALID_INPUT_OR_EVIDENCE_" + str(exc))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 2 if result["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    sys.exit(cli())
