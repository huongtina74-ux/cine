"""P1 daily runner acceptance with isolated canonical runner test double."""
from __future__ import annotations
import json
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from cinefactory.research_intelligence.daily_research import (
    execute_daily, daily_health, daily_preflight, MANDATORY_SNAPSHOT
)

FAKE_RUNNER = r'''
import argparse
import os
from pathlib import Path
import yaml
p = argparse.ArgumentParser()
p.add_argument("--run-slug", required=True)
p.add_argument("--run-id", required=True)
p.add_argument("--dry-run", action="store_true")
a, others = p.parse_known_args()
root = Path(__file__).resolve().parent.parent
run = root / "research" / "markets" / a.run_slug
run.mkdir(parents=True, exist_ok=False)
if a.dry_run:
    (run / "run_manifest.yaml").write_text(
        yaml.safe_dump({"run_status": "IN_PROGRESS", "decision_packet": {"final_verdict": "BLOCKED"}}), encoding="utf-8")
    print("dry-run complete")
    raise SystemExit(0)
outcome = os.getenv("P1_FIXTURE", "COMPLETE")
manifest = {
    "run_status": "COMPLETE" if outcome == "COMPLETE" else "BLOCKED",
    "coverage_gaps": [] if outcome == "COMPLETE" else ["Official verification missing"],
    "decision_packet": {
        "final_verdict": "NO_QUALIFIED_NICHE_FOUND" if outcome == "COMPLETE" else "BLOCKED",
        "candidate_count": 0,
    }
}
(run / "run_manifest.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
if outcome == "COMPLETE":
    (run / "processed").mkdir()
    (run / "reports").mkdir()
    (run / "artifact_index.csv").write_text("artifact_id,stage\n", encoding="utf-8")
    (run / "evidence_table.csv").write_text("id,source\n", encoding="utf-8")
    (run / "processed" / "market_coverage_matrix.csv").write_text(
        "query,coverage_status\nA,COMPLETE\nB,COMPLETE\n", encoding="utf-8")
    (run / "processed" / "channel_snapshot_official_api.csv").write_text(
        "channel_id,channel_url,channel_name,created_at,subscribers,evidence_status\n"
        "UCyoung,https://www.youtube.com/channel/UCyoung,Test Channel,2026-10-01T00:00:00Z,2200,VERIFIED_OFFICIAL_API\n",
        encoding="utf-8")
    (run / "processed" / "fresh_video_observations_clean_official_api.csv").write_text(
        "video_id,channel_id,video_url,title,published_at,duration_seconds,views,format_proxy,seed_cluster,evidence_status\n"
        "ABCdef12345,UCyoung,https://www.youtube.com/watch?v=ABCdef12345,Original test,2026-10-03T00:00:00Z,600,1234567,LONG_FORM,gaming,VERIFIED_AND_DERIVED\n",
        encoding="utf-8")
    (run / "raw").mkdir()
    from datetime import datetime,timedelta,timezone
    now=datetime.now(timezone.utc)
    cid="UC" + "a"*22
    ids=["ABCdef12345","GHIjkl67890"]
    packet={
        "generated_at":now.isoformat(),
        "channels":{cid:{"channel_id":cid,"created_at":(now-timedelta(days=10)).isoformat(),"evidence_status":"VERIFIED","channel_url":"https://youtube.com/channel/"+cid}},
        "catalogs":{cid:[{"video_id":vid,"channel_id":cid,"video_url":"https://www.youtube.com/watch?v="+vid,
                          "published_at":(now-timedelta(days=i+2)).isoformat(),
                          "views":1500000,"duration_seconds":600,
                          "format_proxy":"LONG_FORM","evidence_status":"VERIFIED"} for i,vid in enumerate(ids)]}}
    (run / "raw" / "official_api_integrated_scan.json").write_text(
        __import__("json").dumps(packet),encoding="utf-8")
    joined=(now-timedelta(days=10)).date().isoformat()
    surface={"generated_at":now.isoformat(),"observations":[
        {"channel_id":cid,"joined_date":joined,"channel_name":"Test Channel","query":"gaming"}
    ]}
    public_cat={"generated_at":now.isoformat(),"channels":[{
        "channel_id":cid,"collection_status":"VERIFIED",
        "videos":[{"video_id":vid,"video_url":"https://www.youtube.com/watch?v="+vid,
                   "title":"Original fictional gameplay","views":1400000,"views_text":"1.4M views",
                   "duration_seconds":600,"format_proxy":"LONG_FORM"} for vid in ids]
    }]}
    (run/"raw"/"lane_b_broad_market_surface.json").write_text(
        __import__("json").dumps(surface),encoding="utf-8")
    (run/"raw"/"lane_b_age_1_90_catalogs.json").write_text(
        __import__("json").dumps(public_cat),encoding="utf-8")
    (run / "reports" / "discovery_run_decision_packet.md").write_text(
        "# No qualified niche found", encoding="utf-8")
    print("completed valid runner")
else:
    print("blocked: missing official evidence")
raise SystemExit(0 if outcome in ("COMPLETE", "BLOCKED") else 2)
'''


@pytest.fixture
def company(tmp_path):
    root = tmp_path / "Company Youtube"
    scripts = root / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "run_complete_niche_discovery.py").write_text(FAKE_RUNNER, encoding="utf-8")
    return root


def test_preflight_reports_api_capability_without_leaking_key(company, monkeypatch):
    monkeypatch.delenv("YOUTUBE_DATA_API_KEY", raising=False)
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    p = daily_preflight(company)
    assert p["blocked_if_no_official_proof"]
    monkeypatch.setenv("YOUTUBE_API_KEY", "VERY_PRIVATE_TEST_KEY")
    p = daily_preflight(company)
    assert p["api_key_present"]
    assert "VERY_PRIVATE_TEST_KEY" not in str(p)


def test_daily_complete_and_hash_snapshot_idempotency(company, tmp_path, monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "test_fake_key")
    root = tmp_path / "state"
    rec = execute_daily(company, root, day="2026-10-09")
    assert rec["state"] == "COMPLETE"
    assert rec["coverage"]["status"] == "COMPLETE"
    assert rec["qualified_niches"] is None
    assert rec["canonical_legacy_candidate_count"] == 0
    assert rec["native_adapter"]["status"] == "SCHEMA_READY_TOPIC_REVIEW_REQUIRED"
    assert rec["native_adapter"]["claimed_niches_qualified"] == 0
    assert not rec["owner_review_eligible"]
    # Strict witness is independent of the legacy scanner's broader niche verdict.
    assert rec["channel_breakout_audit"]["state"] == "CHANNEL_BREAKOUT_EVIDENCE_PRESENT"
    assert rec["channel_breakout_audit"]["witness_count"] == 1
    assert rec["public_prescreen"]["state"] == "PROVISIONAL_QUEUE_READY"
    assert rec["public_prescreen"]["official_verification_queue_count"] == 1
    assert rec["public_prescreen"]["auto_called_official_api"] is False
    assert rec["strict_0_30_two_1m_niche_gate"] == "CHANNEL_WITNESSES_ONLY_NOT_FULL_NICHE"
    witness = json.loads(Path(rec["channel_breakout_audit"]["report_path"]).read_text(encoding="utf-8"))
    assert witness["witness_channels"][0]["two_million_within_14d_proved"] is True
    assert witness["opportunity_niches_verified"] == 0
    assert set(MANDATORY_SNAPSHOT).issubset({x["relative_path"] for x in rec["snapshot"]})
    for f in rec["snapshot"]:
        archive = root / "daily" / "2026-10-09" / "attempt_001" / "snapshot" / f["relative_path"]
        assert archive.is_file()
        assert f["sha256"] == f["source_sha256"]
    assert not (root / "daily" / "2026-10-09" / "run.lock").exists()
    assert daily_health(root, now=rec["completed_at"])["status"] == "HEALTHY"
    with pytest.raises(FileExistsError):
        execute_daily(company, root, day="2026-10-09")
    again = execute_daily(company, root, day="2026-10-09", retry=True)
    assert again["attempt"] == 2
    assert (root / "daily" / "2026-10-09" / "attempt_001" / "daily_report.json").exists()


def test_blocked_runner_keeps_gaps_and_never_certifies(company, tmp_path, monkeypatch):
    monkeypatch.setenv("P1_FIXTURE", "BLOCKED")
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    rec = execute_daily(company, tmp_path / "state", day="2026-10-09")
    assert rec["state"] == "BLOCKED"
    assert rec["qualified_niches"] is None
    assert not rec["owner_review_eligible"]
    assert rec["strict_0_30_two_1m_niche_gate"] == "NOT_EVALUATED_WITH_FULL_PROOF"
    assert daily_health(tmp_path / "state", now=rec["completed_at"])["status"] == "ALERT_INCOMPLETE"


def test_real_dry_run_contract_creates_no_qualified_claim(company, tmp_path):
    rec = execute_daily(company, tmp_path / "state", day="2026-10-09", dry_run=True)
    assert rec["state"] == "DRY_RUN"
    assert rec["qualified_niches"] is None
    assert rec["owner_review_eligible"] is False


def test_existing_lock_blocks_concurrent_attempt(company, tmp_path):
    folder = tmp_path / "state" / "daily" / "2026-10-09"
    folder.mkdir(parents=True)
    lock = folder / "run.lock"
    lock.write_text('{"pid":999}', encoding="utf-8")
    with pytest.raises(RuntimeError, match="running"):
        execute_daily(company, tmp_path / "state", day="2026-10-09")
    assert lock.exists()


def test_health_detects_absence_and_staleness(tmp_path):
    state = tmp_path / "state"
    assert daily_health(state)["status"] == "ALERT_NEVER_RAN"
    state.mkdir()
    old = datetime.now(timezone.utc) - timedelta(hours=50)
    (state / "latest_health.json").write_text(json.dumps({
        "updated_at": old.isoformat(), "state": "COMPLETE"
    }), encoding="utf-8")
    assert daily_health(state, max_age_hours=36)["status"] == "ALERT_STALE"


def test_invalid_budget_override_rejected_before_side_effect(company, tmp_path):
    with pytest.raises(ValueError, match="permitted"):
        execute_daily(company, tmp_path / "state", runner_extra=["--mode", "official"])
    assert not (tmp_path / "state").exists()


def test_native_adapter_real_historical_company_schema_is_not_trusted_as_current(tmp_path):
    """Integration on canonical archived public records, copying files into isolation."""
    import shutil
    from cinefactory.research_intelligence.native_adapter import normalize_company_run
    native = Path(r"C:\Users\ADMIN\Downloads\Company Youtube\research\markets\us_affiliate_multichannel_w1\processed")
    if not (native / "channel_snapshot_official_api.csv").is_file() or not (
        native / "fresh_video_observations_clean_official_api.csv").is_file():
        pytest.skip("Historical Company sample is absent on this machine")
    copied = tmp_path / "historical_copy" / "processed"
    copied.mkdir(parents=True)
    for name in ("channel_snapshot_official_api.csv", "fresh_video_observations_clean_official_api.csv"):
        shutil.copy2(native / name, copied / name)
    result = normalize_company_run(tmp_path / "historical_copy", observed_at="2026-08-16T00:00:00Z")
    assert result["status"] == "SCHEMA_READY_TOPIC_REVIEW_REQUIRED"
    assert result["channel_count"] > 100
    assert result["video_count"] > 100
    assert result["claimed_niches_qualified"] == 0
    with Path(result["videos"]["path"]).open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert all(row["topic_fit"] == "UNKNOWN" for row in rows)
    assert all(row["format_proxy"] in ("LONG_FORM", "SHORTS_OR_LIVE", "UNKNOWN") for row in rows)
    with pytest.raises(FileExistsError):
        normalize_company_run(tmp_path / "historical_copy", observed_at="2026-08-16T00:00:00Z")


def test_timeout_terminates_bounded_child_process(tmp_path):
    import sys
    from cinefactory.research_intelligence.daily_research import _run_with_timeout_tree
    stdout, stderr, code, timed_out = _run_with_timeout_tree(
        [sys.executable, "-c", "import time; time.sleep(12)"], tmp_path, 0.25
    )
    assert timed_out is True
    assert code == -1
    assert "CANONICAL_RUNNER_TIMEOUT_TREE_TERMINATED" in stderr


@pytest.mark.skipif(__import__("os").name != "nt", reason="Windows process-tree kill acceptance")
def test_timeout_terminates_spawned_grandchild(tmp_path):
    import sys
    import subprocess
    import time
    from cinefactory.research_intelligence.daily_research import _run_with_timeout_tree
    spawned_file = tmp_path / "grandchild.pid"
    script = tmp_path / "parent.py"
    script.write_text(
        "import subprocess,sys,time,pathlib\n"
        "child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(20)'])\n"
        "pathlib.Path(sys.argv[1]).write_text(str(child.pid), encoding='utf-8')\n"
        "time.sleep(20)\n",
        encoding="utf-8",
    )
    _, stderr, code, timed_out = _run_with_timeout_tree(
        [sys.executable, str(script), str(spawned_file)], tmp_path, 1.5
    )
    assert timed_out and code == -1
    assert spawned_file.exists()
    child_pid = int(spawned_file.read_text(encoding="utf-8"))
    time.sleep(0.1)
    status = subprocess.run(
        ["tasklist", "/FI", f"PID eq {child_pid}", "/FO", "CSV"],
        text=True, capture_output=True, check=False, timeout=8
    )
    assert str(child_pid) not in status.stdout, f"Orphan child survived timeout: PID={child_pid}"
    assert "CANONICAL_RUNNER_TIMEOUT_TREE_TERMINATED" in stderr


def test_timeout_is_reported_and_never_eligible(company, tmp_path, monkeypatch):
    from cinefactory.research_intelligence import daily_research
    monkeypatch.setattr(
        daily_research, "_run_with_timeout_tree",
        lambda argv, root, timeout: ("", "CANONICAL_RUNNER_TIMEOUT_TREE_TERMINATED", -1, True)
    )
    report = execute_daily(company, tmp_path / "state", day="2026-10-09")
    assert report["runner_timed_out"] is True
    assert report["canonical_runner_exit_code"] == -1
    assert report["state"] in ("FAILED", "PARTIAL")
    assert any("TIMEOUT" in reason for reason in report["gaps"])
    assert report["qualified_niches"] is None
    assert report["owner_review_eligible"] is False


def test_focused_canonical_budget_accepts_only_bounded_safe_switches(company,tmp_path,monkeypatch):
    monkeypatch.setenv("P1_FIXTURE","BLOCKED")
    rec=execute_daily(company,tmp_path/"state",day="2026-10-10",
        runner_extra=["--queries-per-market","1",
                      "--max-queries-per-window","2",
                      "--skip-recursive-expansion"])
    assert rec["state"]=="BLOCKED"
    assert rec["qualified_niches"] is None
    assert not rec["owner_review_eligible"]


def test_focus_budget_rejects_duplicate_flag_or_untrusted_mode(company,tmp_path):
    with pytest.raises(ValueError,match="Duplicate"):
        execute_daily(company,tmp_path/"dup",
            runner_extra=["--skip-recursive-expansion","--skip-recursive-expansion"])
    with pytest.raises(ValueError,match="permitted"):
        execute_daily(company,tmp_path/"unsafe",
            runner_extra=["--mode","official"])
