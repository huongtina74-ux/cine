"""Unit tests for the closed-loop tools in tools/ (policy check, research numbers, decision log, Director Cut)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import cf_decision  # noqa: E402
import cf_director_cut as dcmod  # noqa: E402
import cf_policy_check as policy  # noqa: E402
import cf_research_stats as stats  # noqa: E402


# ---------------------------------------------------------------- policy check

def _dc(*texts: str, synopsis: str = "") -> dict:
    return {"shots": [{"id": f"S{i:03d}", "vo": {"text": t}, "onscreen_text": None, "purpose": ""} for i, t in enumerate(texts, 1)],
            "source_episode": {"synopsis": synopsis}}


def test_title_that_matches_the_video_passes():
    pkg = {"title": "Finn the Fox Wins the Rainbow Slide Race | Zoomi", "description": "A slide race.",
           "tags": ["slide race", "fox"], "made_for_kids": True, "ai_disclosure_required": False}
    report = policy.check(pkg, _dc("Finn the fox wins the rainbow slide race!"), "", "", "")
    assert report["verdict"] == "PASS", report


def test_title_promising_what_the_video_never_shows_fails():
    pkg = {"title": "Dragon Battle Lava Volcano Explosion", "description": "", "tags": [],
           "made_for_kids": True, "ai_disclosure_required": False}
    report = policy.check(pkg, _dc("The pig slides down a rainbow slide."), "", "", "")
    assert report["verdict"] == "FAIL"


def test_missing_ai_decision_and_offplatform_cta_are_flagged():
    pkg = {"title": "Pig slide", "description": "Join my group on telegram", "tags": []}
    report = policy.check(pkg, _dc("Pig slide"), "", "", "")
    joined = " ".join(report["warnings"])
    assert "ai_disclosure_required" in joined and "telegram" in joined


def test_third_party_footage_without_license_fails():
    dc = _dc("pig slide")
    dc["shots"][0]["third_party"] = True
    report = policy.check({"title": "pig slide", "ai_disclosure_required": False}, dc, "", "", "")
    assert report["verdict"] == "FAIL"


def test_missing_subtitle_file_is_not_an_error(tmp_path):
    assert policy.srt_text(str(tmp_path / "none.srt")) == ""


# ---------------------------------------------------------------- research numbers

def test_outliers_are_relative_to_their_own_channel(tmp_path):
    rows = [{"channel": c, "title": f"{c} video {i}", "views": v, "published": "2026-10-01"}
            for c in ("A", "B") for i, v in enumerate([1000, 1200, 900, 15000])]
    src = tmp_path / "raw.json"
    src.write_text(json.dumps(rows), encoding="utf-8")
    a = stats.analyse(stats.load(src), stats.to_date("2026-10-15"), 3.0, 180)
    assert a["median"] == 1100
    assert len(a["outliers"]) == 2 and all(r["views"] == 15000 for r in a["outliers"])


def test_loose_field_names_and_dates_parse():
    assert stats.to_date("2026-1-5").isoformat() == "2026-01-05"
    assert stats.to_seconds("PT1H2M3S") == 3723
    assert stats.to_seconds("12:30") == 750


# ---------------------------------------------------------------- decision log

def test_observed_decisions_need_evidence(tmp_path):
    log = str(tmp_path / "d.jsonl")
    assert cf_decision.main(["--log", log, "add", "--kind", "topic", "--decision", "x", "--why", "y",
                             "--label", "OBSERVED"]) == 2
    assert cf_decision.main(["--log", log, "add", "--kind", "topic", "--decision", "x", "--why", "y",
                             "--label", "OBSERVED", "--evidence", "reports/r.md"]) == 0
    first = json.loads(Path(log).read_text(encoding="utf-8").splitlines()[0])
    assert cf_decision.main(["--log", log, "add", "--kind", "topic", "--decision", "z", "--why", "w",
                             "--label", "OWNER", "--supersedes", first["id"]]) == 0
    active = cf_decision.active(cf_decision.read(Path(log)))
    assert [r["decision"] for r in active] == ["z"]


# ---------------------------------------------------------------- Director Cut

def test_dissolve_overlaps_the_previous_shot():
    dc = dcmod.new_dc("EP", title="t", fps=24, width=1280, height=720)
    dc["shots"] = [dcmod.new_shot(1, "a.mp4", 0, 5, "hook"), dcmod.new_shot(2, "b.mp4", 0, 5, "race")]
    dc["shots"][1].update({"cut": "dissolve", "transition_seconds": 1.0})
    assert dcmod.total_seconds(dc) == 9.0
    assert [round(t, 2) for _, t in dcmod.timeline(dc)] == [0.0, 4.0]


def test_strict_validation_requires_emotion_and_purpose(tmp_path):
    dc = dcmod.new_dc("EP", title="t", fps=24, width=1280, height=720)
    clip = tmp_path / "a.mp4"
    clip.write_bytes(b"x")
    dc["shots"] = [dcmod.new_shot(1, str(clip), 0, 5, "hook")]
    path = tmp_path / "dc.json"
    errors, _ = dcmod.validate(dc, path, strict=True)
    assert any("emotion" in e for e in errors)
