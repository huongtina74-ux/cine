"""Bridge and approval contract acceptance tests: no live network, no paid models."""
from __future__ import annotations
import csv
import hashlib
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from cinefactory.research_intelligence.market_bridge import import_company_snapshot
from cinefactory.research_intelligence.niche_pod import activate_research_pod

NOW = datetime(2026, 10, 9, 12, tzinfo=timezone.utc)
REAL_COMPANY_ROOT = Path(r"C:\Users\ADMIN\Downloads\Company Youtube")
ID1, ID2 = "ABCdef12345", "GHIjkl67890"


def _write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=list(rows[0]))
        out.writeheader()
        out.writerows(rows)


def _when(days_ago=0):
    return (NOW - timedelta(days=days_ago)).isoformat()


def _review():
    sources = {
        "format-review": {"type": "format_review", "url": "https://youtube.com/watch?v=ABCdef12345"},
        "mature1": {"type": "mature_recent", "url": "https://youtube.com/watch?v=ABCdef12345",
                    "channel_id": "UColdone", "channel_created_at": _when(800),
                    "video_published_at": _when(10), "video_views": 240000},
        "mature2": {"type": "mature_recent", "url": "https://youtube.com/watch?v=GHIjkl67890",
                    "channel_id": "UColdtwo", "channel_created_at": _when(900),
                    "video_published_at": _when(7), "video_views": 180000},
        "rpm-scenario": {"type": "revenue_scenario", "url": "https://youtube.com/watch?v=ABCdef12345",
                         "rpm_usd": 3.0, "monthly_views_assumed": 1000000},
        "newchannel-example": {"type": "new_entrant", "url": "https://youtube.com/watch?v=GHIjkl67890",
                               "channel_id": "UCnew", "channel_created_at": _when(8),
                               "video_views": 1350000},
    }
    for source in sources.values():
        source.update({"status": "REVIEWED", "reviewed_by": "test_reviewer", "observed_at": _when()})
    return {
        "novelty": {"supported": True, "source_ids": ["format-review"], "differentiation": "Original structure"},
        "durable": {"supported": True, "source_ids": ["mature1", "mature2"]},
        "business": {"supported": True, "source_ids": ["rpm-scenario"]},
        "entry": {"supported": True, "source_ids": ["newchannel-example"]},
        "source_register": sources,
    }


@pytest.fixture
def company(tmp_path):
    root = tmp_path / "Company Youtube"
    root.mkdir()
    channel_csv = root / "channels.csv"
    video_csv = root / "videos.csv"
    _write_csv(channel_csv, [
        {"snapshot_at": _when(), "channel_id": "UCyoung", "created_at": _when(10),
         "channel_url": "https://youtube.com/channel/UCyoung", "evidence_status": "VERIFIED"}
    ])
    _write_csv(video_csv, [
        {"snapshot_at": _when(), "channel_id": "UCyoung", "video_id": ident,
         "video_url": f"https://www.youtube.com/watch?v={ident}", "published_at": _when(i + 1),
         "duration_seconds": "650", "format_proxy": "long-form", "views": "1350000",
         "topic_cluster": "Minecraft animation", "topic_fit": "DIRECT", "evidence_status": "VERIFIED"}
        for i, ident in enumerate((ID1, ID2))
    ])
    return root, channel_csv, video_csv


def _bridge(company, output, *, review=None, existing=None):
    root, channels, videos = company
    return import_company_snapshot(
        root, channels, videos, output, niche="Minecraft animation",
        format_key="custom-stage", review=review if review is not None else _review(),
        existing_niches=existing, as_of=_when())


def test_bridge_honors_two_distinct_million_views_and_read_only(company, tmp_path):
    root, channels, videos = company
    before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in (channels, videos)]
    packet = _bridge(company, tmp_path / "bridge.json")
    assert packet["triage"]["status"] == "AUDIT_READY"
    assert packet["triage"]["gates"]["two_1m_longform_on_new_channel"]
    assert len(packet["triage"]["qualifying_channels"][0]["videos"]) == 2
    assert packet["source_policy"] == "company_youtube_read_only"
    assert [hashlib.sha256(p.read_bytes()).hexdigest() for p in (channels, videos)] == before


def test_one_video_or_unverified_metadata_does_not_pass(company, tmp_path):
    root, channels, videos = company
    rows = list(csv.DictReader(videos.open(encoding="utf-8")))
    rows[1]["views"] = "950000"
    _write_csv(videos, rows)
    report = _bridge(company, tmp_path / "watchlist.json")
    assert report["triage"]["status"] == "WATCHLIST"
    rows[1]["views"] = "1350000"
    rows[1]["evidence_status"] = "UNKNOWN"
    _write_csv(videos, rows)
    assert _bridge(company, tmp_path / "watchlist2.json")["triage"]["status"] == "WATCHLIST"


def test_shorts_live_old_channels_and_stale_files_fail_closed(company, tmp_path):
    root, channels, videos = company
    video_rows = list(csv.DictReader(videos.open(encoding="utf-8")))
    for bad_format in ("Shorts", "Live"):
        video_rows[1]["format_proxy"] = bad_format
        _write_csv(videos, video_rows)
        assert _bridge(company, tmp_path / f"{bad_format}.json")["triage"]["status"] == "WATCHLIST"
    video_rows[1]["format_proxy"] = "long-form"
    _write_csv(videos, video_rows)
    channel_rows = list(csv.DictReader(channels.open(encoding="utf-8")))
    channel_rows[0]["created_at"] = _when(31)
    _write_csv(channels, channel_rows)
    assert _bridge(company, tmp_path / "old.json")["triage"]["status"] == "WATCHLIST"
    channel_rows[0]["snapshot_at"] = _when(10)
    _write_csv(channels, channel_rows)
    with pytest.raises(ValueError, match="No fresh"):
        _bridge(company, tmp_path / "stale.json")


def test_duplicate_format_requires_real_differentiation(company, tmp_path):
    overlap = [{"niche": "Minecraft animation", "format_key": "custom-stage"}]
    report = _bridge(company, tmp_path / "overlap.json", existing=overlap)
    assert report["triage"]["status"] == "WATCHLIST"
    assert "distinct_niche_or_format" in report["triage"]["missing"]


def test_missing_external_evidence_keeps_watchlist(company, tmp_path):
    packet = _bridge(company, tmp_path / "unproven.json", review={})
    assert packet["triage"]["status"] == "WATCHLIST"
    assert "durable_recent_demand" in packet["triage"]["missing"]


@pytest.mark.skipif(not (REAL_COMPANY_ROOT / "scripts" / "validate_promotion_gate.py").is_file(),
                    reason="Company Youtube canonical gate checkout not available")
def test_owner_approval_creates_idempotent_pod_without_scheduling(company, tmp_path):
    root, channels, videos = company
    (root / "scripts").mkdir()
    (root / "05_portfolio").mkdir()
    shutil.copy2(REAL_COMPANY_ROOT / "scripts" / "validate_promotion_gate.py",
                 root / "scripts" / "validate_promotion_gate.py")
    shutil.copy2(REAL_COMPANY_ROOT / "05_portfolio" / "promotion_gate_rules.yaml",
                 root / "05_portfolio" / "promotion_gate_rules.yaml")
    request = root / "05_portfolio" / "approved.yaml"
    shutil.copy2(REAL_COMPANY_ROOT / "05_portfolio" / "promotion_gate_request.template.yaml", request)
    bridge_path = tmp_path / "bridge.json"
    _bridge(company, bridge_path)
    event_file = tmp_path / "approval.json"
    event = {
        "schema": "cine.owner_approval.v1", "approved": True,
        "approval_id": "owner-review-001", "approved_by": "owner-local",
        "candidate_id": "CANDIDATE-001",
        "niche": "Minecraft animation", "format_key": "custom-stage",
        "approved_at": _when(),
        "bridge_sha256": hashlib.sha256(bridge_path.read_bytes()).hexdigest(),
        "gate_sha256": hashlib.sha256(request.read_bytes()).hexdigest(),
    }
    event_file.write_text(json.dumps(event), encoding="utf-8")
    first = activate_research_pod(root, bridge_path, request, event_file, tmp_path / "pods", as_of=_when())
    assert first["state"] == "CONFIGURED_NOT_SCHEDULED"
    assert first["work_items_total"] == 6
    assert first["jobs"][0]["status"] == "NOT_SCHEDULED"
    assert first["owner_event_is_authenticated"] is False
    assert first["production_conference"]["state"] == "REQUIRES_VIDEO_SCENE_INSPECTION_AND_TOOL_BAKEOFF"
    assert first["production_conference"]["production_permission"] is False
    assert first["production_conference"]["schedule_state"] == "NOT_SCHEDULED"
    assert activate_research_pod(root, bridge_path, request, event_file, tmp_path / "pods", as_of=_when()) == first
    event["approval_id"] = "other-approval"
    event_file.write_text(json.dumps(event), encoding="utf-8")
    with pytest.raises(FileExistsError):
        activate_research_pod(root, bridge_path, request, event_file, tmp_path / "pods", as_of=_when())


@pytest.mark.skipif(not (REAL_COMPANY_ROOT / "scripts" / "validate_promotion_gate.py").is_file(),
                    reason="Company Youtube canonical gate checkout not available")
def test_pod_rejects_fake_owner_and_mutated_snapshot(company, tmp_path):
    root, _, videos = company
    (root / "scripts").mkdir()
    (root / "05_portfolio").mkdir()
    shutil.copy2(REAL_COMPANY_ROOT / "scripts" / "validate_promotion_gate.py", root / "scripts" / "validate_promotion_gate.py")
    shutil.copy2(REAL_COMPANY_ROOT / "05_portfolio" / "promotion_gate_rules.yaml", root / "05_portfolio" / "promotion_gate_rules.yaml")
    request = root / "05_portfolio" / "approved.yaml"
    shutil.copy2(REAL_COMPANY_ROOT / "05_portfolio" / "promotion_gate_request.template.yaml", request)
    bridge_path = tmp_path / "bridge.json"
    _bridge(company, bridge_path)
    event_file = tmp_path / "event.json"
    event_file.write_text(json.dumps({"schema": "cine.owner_approval.v1", "approved": False}), encoding="utf-8")
    with pytest.raises(PermissionError, match="approval"):
        activate_research_pod(root, bridge_path, request, event_file, tmp_path / "pods", as_of=_when())
    original = videos.read_text(encoding="utf-8")
    videos.write_text(original + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="sources changed"):
        activate_research_pod(root, bridge_path, request, event_file, tmp_path / "pods", as_of=_when())


def test_video_link_must_match_id_and_publish_after_channel_creation(company, tmp_path):
    root, channels, videos = company
    original = list(csv.DictReader(videos.open(encoding="utf-8")))
    rows = [dict(item) for item in original]
    rows[1]["video_url"] = f"https://www.youtube.com/watch?v={ID1}"
    _write_csv(videos, rows)
    assert _bridge(company, tmp_path / "wrongurl.json")["triage"]["status"] == "WATCHLIST"
    rows[1]["video_url"] = f"https://www.youtube.com/watch?v={ID2}"
    rows[1]["published_at"] = _when(20)
    _write_csv(videos, rows)
    assert _bridge(company, tmp_path / "before-creation.json")["triage"]["status"] == "WATCHLIST"


def test_evergreen_and_earnings_claims_fail_without_concrete_validated_scenarios(company, tmp_path):
    review = _review()
    review["source_register"]["mature2"]["video_views"] = 50000
    assert _bridge(company, tmp_path / "low-demand.json", review=review)["triage"]["status"] == "WATCHLIST"
    review = _review()
    review["source_register"]["rpm-scenario"]["rpm_usd"] = 1.0
    review["source_register"]["rpm-scenario"]["monthly_views_assumed"] = 10000
    packet = _bridge(company, tmp_path / "low-revenue.json", review=review)
    assert not packet["triage"]["gates"]["business_case_documented"]


def test_source_registry_must_link_reviewed_proof(company, tmp_path):
    review = _review()
    review["source_register"].pop("mature1")
    report = _bridge(company, tmp_path / "missing_review.json", review=review)
    assert report["triage"]["status"] == "WATCHLIST"
    review = _review()
    review["source_register"]["mature1"]["status"] = "UNKNOWN"
    assert _bridge(company, tmp_path / "unknown_review.json", review=review)["triage"]["status"] == "WATCHLIST"


def test_niche_watcher_checks_real_company_file_hashes(company, tmp_path):
    from cinefactory.research_intelligence.pod_watch import watch_niche
    root, channels, videos = company
    bridge = _bridge(company, tmp_path / "current.json")
    pod = {"schema": "cine.niche.pod.v1", "state": "CONFIGURED_NOT_SCHEDULED",
           "niche": bridge["niche"], "format_key": bridge["format_key"],
           "niche_id": "minecraft-animation--custom-stage", "source_company": str(root.resolve())}
    report = watch_niche(pod, bridge, tmp_path / "watch.json", as_of=_when())
    assert report["fresh_15d_million_videos"] == 2
    assert report["newcomer_channels_observed"] == 1
    videos.write_text(videos.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="changed"):
        watch_niche(pod, bridge, tmp_path / "tampered.json", as_of=_when())


def test_bridge_rejects_forged_views_even_when_source_csv_hash_still_matches(company,tmp_path):
    from cinefactory.research_intelligence.market_bridge import verify_imported_company_sources
    from cinefactory.research_intelligence.pod_watch import watch_niche
    payload=_bridge(company,tmp_path/"original_bridge.json")
    assert verify_imported_company_sources(payload)
    tampered=json.loads(json.dumps(payload))
    tampered["candidates"][0]["channels"][0]["videos"][0]["views"]=97000000
    with pytest.raises(ValueError,match="Bridge video metadata"):
        verify_imported_company_sources(tampered)
    pod={"schema":"cine.niche.pod.v1","state":"CONFIGURED_NOT_SCHEDULED",
         "niche":payload["niche"],"format_key":payload["format_key"],
         "niche_id":"minecraft-animation--custom-stage","source_company":str(company[0].resolve())}
    with pytest.raises(ValueError,match="Bridge video metadata"):
        watch_niche(pod,tampered,tmp_path/"forged_watch.json",as_of=_when())
    assert not (tmp_path/"forged_watch.json").exists()


def test_bridge_rejects_forged_triage_gates_and_changed_review_flags(company,tmp_path):
    from cinefactory.research_intelligence.market_bridge import verify_imported_company_sources
    payload=_bridge(company,tmp_path/"original_bridge.json")
    changed=json.loads(json.dumps(payload))
    changed["triage"]["gates"]["two_1m_longform_on_new_channel"]=False
    with pytest.raises(ValueError,match="triage/approval gates"):
        verify_imported_company_sources(changed)
    changed=json.loads(json.dumps(payload))
    changed["candidates"][0]["newcomer_evidence"]=False
    with pytest.raises(ValueError,match="review evidence flags"):
        verify_imported_company_sources(changed)


def test_bridge_rejects_same_video_appearing_twice(company,tmp_path):
    from cinefactory.research_intelligence.market_bridge import verify_imported_company_sources
    payload=_bridge(company,tmp_path/"original_bridge.json")
    changed=json.loads(json.dumps(payload))
    changed["candidates"][0]["channels"][0]["videos"].append(
        dict(changed["candidates"][0]["channels"][0]["videos"][0]))
    with pytest.raises(ValueError,match="Duplicate video ID"):
        verify_imported_company_sources(changed)


def test_activation_rejects_forged_bridge_even_with_matching_fake_local_approval(company,tmp_path,monkeypatch):
    from cinefactory.research_intelligence import niche_pod
    root=company[0]
    request=root/"owner_request.yaml"
    request.write_text("candidate_id: CANDIDATE-001\n",encoding="utf-8")
    bridge_file=tmp_path/"bridge.json"
    packet=_bridge(company,bridge_file)
    packet["candidates"][0]["channels"][0]["videos"][0]["views"]=75000000
    bridge_file.write_text(json.dumps(packet),encoding="utf-8")
    event_file=tmp_path/"owner_event.json"
    event_file.write_text(json.dumps({
        "schema":"cine.owner_approval.v1","approved":True,
        "approval_id":"spoofed-event","approved_by":"local-file-not-authenticated",
        "candidate_id":"CANDIDATE-001","niche":packet["niche"],
        "format_key":packet["format_key"],"approved_at":_when(),
        "bridge_sha256":hashlib.sha256(bridge_file.read_bytes()).hexdigest(),
        "gate_sha256":hashlib.sha256(request.read_bytes()).hexdigest()}),encoding="utf-8")
    monkeypatch.setattr(niche_pod,"_company_gate",
                        lambda *args:{"candidate_id":"CANDIDATE-001"})
    with pytest.raises(ValueError,match="Bridge video metadata"):
        niche_pod.activate_research_pod(root,bridge_file,request,event_file,
                                        tmp_path/"pods",as_of=_when())
    assert not (tmp_path/"pods").exists()
