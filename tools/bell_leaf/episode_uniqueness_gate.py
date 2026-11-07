#!/usr/bin/env python3
"""Bell & Leaf proposal uniqueness gate. Text-only, deterministic and fail-closed.

This detects exact copying, repeated writing templates and high lexical overlap.
It does NOT prove semantic originality or establish any screenplay/media approval.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INDEX = ROOT / "docs/story/bell_leaf/slates/BELL_LEAF_1000_EPISODE_INDEX_PROPOSAL_20261107.csv"
DEFAULT_SLATE = ROOT / "docs/story/bell_leaf/slates/BELL_LEAF_1000_EPISODE_DEVELOPMENT_SLATE_UNAPPROVED_20261107.md"
HEADER = re.compile(r"(?m)^\*\*(BL-\d{4}) — (.*?)\*\* · POV (.*?) · (OLD|NEW|EARTH|MIXED) · (.*?)\s*$")
ID = re.compile(r"^BL-\d{4}$")


def normalize(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).casefold()
    return " ".join(re.findall(r"[^\W_]+", s, flags=re.UNICODE))


def extract(text: str, label: str, following: tuple[str, ...]) -> str:
    pos = text.find(label)
    if pos < 0:
        return ""
    tail = text[pos + len(label):]
    ends = [tail.find(x) for x in following if tail.find(x) >= 0]
    return tail[:min(ends) if ends else len(tail)].strip(" \n.*")


def parse_slate(path: Path) -> list[dict]:
    body = path.read_text(encoding="utf-8-sig")
    headers = list(HEADER.finditer(body))
    if not headers:
        raise ValueError(f"Not a Bell & Leaf card slate: {path}")
    cards = []
    for i, match in enumerate(headers):
        chunk = body[match.end():headers[i+1].start() if i + 1 < len(headers) else len(body)]
        result = {
            "episode_id": match.group(1),
            "title": match.group(2).strip(),
            "lead": match.group(3).strip(),
            "setting_class": match.group(4),
            "location": match.group(5).strip(),
            "hook": extract(chunk, "**Hook:**", ("**Ai cần giúp:**", "**Xung đột:**", "**Câu chuyện riêng:**", "**Dư âm:**", "\n*Continuity:*")),
            "goal": extract(chunk, "**Ai cần giúp:**", ("**Câu chuyện riêng:**", "**Xung đột:**", "**Dư âm:**", "\n*Continuity:*")),
            "conflict": extract(chunk, "**Xung đột:**", ("**Câu chuyện riêng:**", "**Dư âm:**", "\n*Continuity:*")),
            "resolution": extract(chunk, "**Câu chuyện riêng:**", ("**Dư âm:**", "\n*Continuity:*")),
            "twist": extract(chunk, "**Dư âm:**", ("\n*Continuity:*",)),
            "continuity_delta": extract(chunk, "*Continuity:*", ("\n\n",)),
        }
        cards.append(result)
    return cards


def read_index(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        items = list(csv.DictReader(f))
    if not items or not all(ID.fullmatch(x.get("episode_id", "")) for x in items):
        raise ValueError("Invalid or empty episode index")
    ids = [x["episode_id"] for x in items]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate episode IDs in index")
    return items


def load(index: Path = DEFAULT_INDEX, slate: Path = DEFAULT_SLATE) -> list[dict]:
    if not index.is_file() or not slate.is_file():
        raise FileNotFoundError("Missing required Bell & Leaf 1000-episode proposal index/slate")
    items, cards = read_index(index), parse_slate(slate)
    ids = {x["episode_id"] for x in cards}
    if len(ids) != len(cards) or ids != {x["episode_id"] for x in items}:
        raise ValueError("Index and slate IDs do not reconcile")
    if len(cards) != 1000:
        raise ValueError(f"Expected 1000 registered proposals; found {len(cards)}")
    for row, c in zip(items, cards):
        if row["episode_id"] != c["episode_id"]:
            raise ValueError(f"Ordering mismatch: {row['episode_id']} vs {c['episode_id']}")
    return cards


def profile(cards: list[dict]) -> dict:
    unique_titles = len({normalize(c["title"]) for c in cards})
    fields = {}
    for field in ("hook", "goal", "conflict", "resolution", "twist", "continuity_delta"):
        counts = Counter(normalize(c.get(field, "")) for c in cards if normalize(c.get(field, "")))
        repeated = [(s, n) for s, n in counts.most_common() if n > 1]
        fields[field] = {
            "nonempty": sum(bool(normalize(c.get(field, ""))) for c in cards),
            "unique_nonempty": len(counts),
            "largest_exact_reuse": max(counts.values(), default=0),
            "repeated_templates": len(repeated),
            "episodes_in_reused_templates": sum(n for _, n in repeated),
            "examples": [{"count": n, "text": s[:110]} for s, n in repeated[:3]],
        }
    flags = []
    if unique_titles != len(cards):
        flags.append("EXACT_TITLE_COLLISIONS")
    for field in ("hook", "conflict", "resolution", "twist", "continuity_delta"):
        if fields[field]["largest_exact_reuse"] >= 5:
            flags.append(f"REUSED_{field.upper()}_TEMPLATE")
    if fields["hook"]["nonempty"] < len(cards)-1:
        flags.append("MISSING_HOOK")
    if fields["conflict"]["nonempty"] < len(cards)-1:
        flags.append("MISSING_CONFLICT")
    if fields["resolution"]["nonempty"] < len(cards)-1:
        flags.append("MISSING_SPECIFIC_RESOLUTION")
    return {
        "series_id": "bell_leaf", "niche_id": "slow_english_a2",
        "scope": "1000 DEVELOPMENT PROPOSALS, NOT FINISHED SCREENPLAYS",
        "registered": len(cards), "unique_titles": unique_titles,
        "fields": fields, "flags": flags,
        "status": "REVIEW_REQUIRED" if flags else "NO_DETERMINISTIC_COLLISION_FOUND",
        "disclaimer": "Even a PASS cannot guarantee semantic originality; independent story editor and competitor-source rights review are mandatory.",
    }


def compare(candidate: dict, existing: list[dict]) -> dict:
    required = ("episode_id", "title", "lead", "setting_class", "hook",
                "goal", "conflict", "twist", "resolution", "continuity_delta")
    problems = []
    for field in required:
        if not isinstance(candidate.get(field), str) or not candidate[field].strip():
            problems.append(f"MISSING_{field.upper()}")
    if problems:
        return {"status": "BLOCKED", "problems": problems, "matches": [], "semantic_review": "NOT_PERFORMED"}
    if not ID.fullmatch(candidate["episode_id"]):
        problems.append("INVALID_EPISODE_ID")
    if candidate["setting_class"] not in ("EARTH", "OLD", "NEW", "MIXED"):
        problems.append("INVALID_SETTING")
    for field in ("hook", "goal", "conflict", "twist", "resolution", "continuity_delta"):
        if len(normalize(candidate[field]).split()) < 5:
            problems.append(f"UNDERDEVELOPED_{field.upper()}")
    matched = []
    for card in existing:
        if card["episode_id"] == candidate["episode_id"]:
            # An author can replace the unfinished card for this episode, but
            # copying the existing placeholder is not an originality clearance.
            if normalize(candidate["hook"]) == normalize(card.get("hook", "")) and normalize(candidate["resolution"]) == normalize(card.get("resolution", "")):
                problems.append("REUSED_OWN_UNFINISHED_PITCH")
            continue
        signals = []
        if normalize(candidate["title"]) == normalize(card["title"]):
            signals.append("TITLE_EXACT")
        for field in ("hook", "goal", "conflict", "resolution", "twist", "continuity_delta"):
            a, b = normalize(candidate[field]), normalize(card.get(field, ""))
            if not a or not b:
                continue
            if a == b:
                signals.append(field.upper()+"_EXACT")
            elif len(a) >= 50 and len(b) >= 50 and SequenceMatcher(None, a, b).ratio() >= 0.90:
                signals.append(field.upper()+"_NEAR_90")
        if signals:
            matched.append({"episode_id": card["episode_id"], "signals": signals})
    generic = ("continuity_delta", "resolution", "twist")
    # Text used across ≥5 slots cannot be a unique payoff or consequence.
    for field in generic:
        v = normalize(candidate[field])
        repeats = sum(normalize(x.get(field, "")) == v for x in existing if x["episode_id"] != candidate["episode_id"])
        if repeats >= 4:
            problems.append(f"NON_DISTINCT_{field.upper()}_{repeats}_PRIOR_USES")
    matched.sort(key=lambda m: ("TITLE_EXACT" in m["signals"], len(m["signals"])), reverse=True)
    severe = any("TITLE_EXACT" in m["signals"] or
                 sum(any(sig.startswith(f) for sig in m["signals"]) for f in ("HOOK", "CONFLICT", "RESOLUTION")) >= 2
                 for m in matched)
    if severe:
        problems.append("STRONG_NARRATIVE_OVERLAP")
    status = "BLOCKED" if problems else "MANUAL_NOVELTY_REVIEW_REQUIRED"
    return {
        "status": status, "candidate": candidate["episode_id"],
        "problems": sorted(set(problems)), "matches": matched[:30],
        "matches_total": len(matched),
        "semantic_review": "REQUIRED_HUMAN_REVIEW_NOT_AUTOMATICALLY_APPROVED",
        "research_evidence": "NOT_VERIFIED_BY_THIS_TOOL",
        "next_gate": "INDEPENDENT_STORY_EDITOR_AND_SOURCE_BASIS_SIGNOFF",
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["audit", "check"])
    p.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    p.add_argument("--slate", type=Path, default=DEFAULT_SLATE)
    p.add_argument("--candidate", type=Path, help="JSON episode pitch to test against all 1000 proposals")
    p.add_argument("--out", type=Path, help="Optional JSON audit report")
    args = p.parse_args(argv)
    try:
        cards = load(args.index, args.slate)
        if args.command == "audit":
            result = profile(cards)
        else:
            if not args.candidate:
                raise ValueError("--candidate is required for check")
            result = compare(json.loads(args.candidate.read_text(encoding="utf-8-sig")), cards)
    except (ValueError, OSError, json.JSONDecodeError) as e:
        result = {"status": "BLOCKED_DATA_ERROR", "error": str(e)}
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=True, indent=2))  # Windows cp1252-safe
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload+"\n", encoding="utf-8")
    return 2 if result.get("status") in {"BLOCKED", "BLOCKED_DATA_ERROR", "REVIEW_REQUIRED"} else 0


if __name__ == "__main__":
    sys.exit(main())
