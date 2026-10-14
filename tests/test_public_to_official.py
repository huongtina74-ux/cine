"""Public discovery stays provisional; targeted official API verifies only selected IDs."""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest

from cinefactory.research_intelligence.public_prescreen import prescreen_company_public
from cinefactory.research_intelligence.targeted_official import verify_targeted_queue

CID="UC"+"a"*22
OTHER="UC"+"b"*22
V1="ABCdef12345"
V2="GHIjkl67890"


def when(days=0):
    return (datetime.now(timezone.utc)-timedelta(days=days)).isoformat()


@pytest.fixture
def collected(tmp_path):
    root=tmp_path/"Company Youtube"
    run=root/"research"/"markets"/"single_canonical_run"
    raw=run/"raw"
    raw.mkdir(parents=True)
    joined=(datetime.now(timezone.utc)-timedelta(days=10)).date().isoformat()
    observations=[
        {"channel_id":CID,"joined_date":joined,
         "channel_name":"Original Actor", "query":"animated creature stories"},
        {"channel_id":CID,"joined_date":joined,
         "channel_name":"Original Actor", "query":"animation"}]
    surface={"generated_at":when(),"status":"COMPLETE","observations":observations}
    def vid(ident, views):
        return {"video_id":ident,"views":views,"views_text":f"{views/1e6:.1f}M views",
                "video_url":"https://www.youtube.com/watch?v="+ident,
                "title":"Original animation","duration_seconds":610,"format_proxy":"LONG_FORM",
                "video_age_days":4}
    catalogs={"generated_at":when(),"channels":[
        {"channel_id":CID,"collection_status":"VERIFIED",
         "channel":"Original Actor","videos":[vid(V1,1300000),vid(V2,1100000)]}
    ]}
    (raw/"lane_b_broad_market_surface.json").write_text(json.dumps(surface),encoding="utf-8")
    (raw/"lane_b_age_1_90_catalogs.json").write_text(json.dumps(catalogs),encoding="utf-8")
    return root,run


def prescreen(collected,tmp_path):
    root,run=collected
    result_path=tmp_path/"prescreen.json"
    rep=prescreen_company_public(root,run,result_path)
    return rep,result_path


def test_real_date_uncertainty_kept_provisional(collected,tmp_path):
    rep,path=prescreen(collected,tmp_path)
    assert rep["state"]=="PROVISIONAL_QUEUE_READY"
    assert rep["fresh_for_daily"] is True
    assert rep["counts"]["two_display_million_channels"]==1
    assert rep["counts"]["queued_channels"]==1
    assert rep["qualified_niches"]==0
    assert rep["eligible_for_cinecouncil_approval"] is False
    row=rep["candidates"][0]
    assert row["verification_state"]=="PROVISIONAL_PUBLIC_SOURCE"
    assert row["level"]=="TWO_DISPLAY_MILLION"
    assert row["age_days_range_at_collection"][1]-row["age_days_range_at_collection"][0]==1
    assert all(v["views_are_exact"] is False for v in row["videos"])
    assert set(rep["requests_for_official_verification"][0]["video_ids"])=={V1,V2}


def test_unverified_catalog_cannot_join_official_queue(collected,tmp_path):
    _,run=collected
    p=run/"raw"/"lane_b_age_1_90_catalogs.json"
    packet=json.loads(p.read_text(encoding="utf-8"))
    packet["channels"][0]["collection_status"]="UNKNOWN"
    p.write_text(json.dumps(packet),encoding="utf-8")
    rep,_=prescreen(collected,tmp_path)
    assert rep["counts"]["queued_channels"]==0


def test_one_viral_video_is_not_enough(collected,tmp_path):
    _,run=collected
    p=run/"raw"/"lane_b_age_1_90_catalogs.json"
    packet=json.loads(p.read_text(encoding="utf-8"))
    packet["channels"][0]["videos"][1]["views"]=200000
    p.write_text(json.dumps(packet),encoding="utf-8")
    rep,_=prescreen(collected,tmp_path)
    assert rep["candidates"][0]["level"]=="SINGLE_DISPLAY_MILLION"
    assert not rep["requests_for_official_verification"]


def test_old_run_retained_for_audit_but_not_daily(collected,tmp_path):
    root,run=collected
    rep=prescreen_company_public(root,run,tmp_path/"old.json",as_of=when(-5))
    with pytest.raises(ValueError,match="future"):
        prescreen_company_public(root,run,tmp_path/"future.json",as_of=when(60))
    # An old-enough run should not be called current even with 2M videos.
    rep=prescreen_company_public(root,run,tmp_path/"historic.json",as_of=when(-10))
    assert rep["state"]=="HISTORICAL_ONLY"
    assert not rep["fresh_for_daily"]


def test_missing_key_fails_closed_zero_network(collected,tmp_path,monkeypatch):
    _,path=prescreen(collected,tmp_path)
    for k in ("YOUTUBE_DATA_API_KEY","YOUTUBE_API_KEY","GOOGLE_API_KEY"):
        monkeypatch.delenv(k,raising=False)
    rep=verify_targeted_queue(path,tmp_path/"verify")
    assert rep["state"]=="BLOCKED_NEEDS_OFFICIAL_API_KEY"
    assert rep["estimated_quota_units"]==2
    assert rep["actual_api_calls"]==0


def test_bounded_official_recheck_with_mocked_api(collected,tmp_path):
    _,path=prescreen(collected,tmp_path)
    calls=[]
    def fake(endpoint,ids,key):
        calls.append((endpoint,ids))
        assert key=="not-real-key"
        if endpoint=="channels":
            return {"items":[{"id":CID,"snippet":{"title":"Original Actor",
                                "publishedAt":when(10)},"statistics":{"subscriberCount":"2800"}}]}
        return {"items":[
            {"id":vid,"snippet":{"channelId":CID,"title":"Original story",
                                  "publishedAt":when(idx+2),"liveBroadcastContent":"none"},
             "contentDetails":{"duration":"PT10M1S"},"statistics":{"viewCount":"1450000"},
             "status":{"privacyStatus":"public"}} for idx,vid in enumerate(ids)]}
    out=verify_targeted_queue(path,tmp_path/"official",api_key="not-real-key",fetch_json=fake)
    assert out["state"]=="OFFICIAL_RECHECK_COMPLETE",out
    assert out["actual_api_calls"]==2
    assert out["strict_witness_channels"]==1
    assert len(calls)==2
    strict=json.loads((tmp_path/"official"/"strict_breakout_audit.json").read_text(encoding="utf-8"))
    assert strict["witness_channels"][0]["two_million_within_14d_proved"] is True
    assert out["niches_verified"]==0
    assert out["approved_to_produce"] is False
    assert "not-real-key" not in (tmp_path/"official"/"official_verification_report.json").read_text(encoding="utf-8")


def test_wrong_video_owner_rejected_even_when_public_candidate_matches(collected,tmp_path):
    _,path=prescreen(collected,tmp_path)
    def fake(endpoint,ids,key):
        if endpoint=="channels":
            return {"items":[{"id":CID,"snippet":{"publishedAt":when(10)}}]}
        return {"items":[{"id":v,"snippet":{"channelId":OTHER,"publishedAt":when(2)},
                          "contentDetails":{"duration":"PT10M"},"statistics":{"viewCount":"2000000"}} for v in ids]}
    rep=verify_targeted_queue(path,tmp_path/"official",api_key="not-real-key",fetch_json=fake)
    assert rep["strict_witness_channels"]==0


def test_quota_and_tamper_fail_closed(collected,tmp_path):
    _,path=prescreen(collected,tmp_path)
    rep=verify_targeted_queue(path,tmp_path/"smallbudget",max_requests=1,api_key="not-real-key")
    assert rep["state"]=="BLOCKED_QUOTA_BUDGET"
    surface=collected[1]/"raw"/"lane_b_broad_market_surface.json"
    surface.write_text(surface.read_text(encoding="utf-8")+" ",encoding="utf-8")
    with pytest.raises(ValueError,match="mutated"):
        verify_targeted_queue(path,tmp_path/"tampered",api_key="not-real-key")


def test_missing_public_catalog_is_not_a_fake_empty_market(tmp_path):
    root=tmp_path/"Company Youtube"
    run=root/"research"/"markets"/"runner"
    run.mkdir(parents=True)
    rep=prescreen_company_public(root,run,tmp_path/"missing.json")
    assert rep["state"]=="NOT_COLLECTED"
    assert "missing" in rep


def test_mutated_verification_queue_cannot_request_foreign_ids(collected,tmp_path):
    _,path=prescreen(collected,tmp_path)
    packet=json.loads(path.read_text(encoding="utf-8"))
    packet["requests_for_official_verification"][0]["video_ids"]=[V1,"ZZZqqq12345"]
    path.write_text(json.dumps(packet),encoding="utf-8")
    with pytest.raises(ValueError,match="do not match"):
        verify_targeted_queue(path,tmp_path/"blocked",api_key="not-real-key")


def test_failed_api_attempt_counts_quota_but_never_exposes_key(collected,tmp_path):
    _,path=prescreen(collected,tmp_path)
    def reject(*args):
        raise RuntimeError("not-real-key must not appear in report")
    report=verify_targeted_queue(path,tmp_path/"failed",api_key="not-real-key",fetch_json=reject)
    assert report["state"]=="OFFICIAL_RECHECK_FAILED"
    assert report["actual_api_calls"]==1
    content=(tmp_path/"failed"/"official_verification_report.json").read_text(encoding="utf-8")
    assert "not-real-key" not in content


def test_bad_views_text_like_channel_name_cannot_generate_fake_million_lead(collected,tmp_path):
    _,run=collected
    p=run/"raw"/"lane_b_age_1_90_catalogs.json"
    data=json.loads(p.read_text(encoding="utf-8"))
    for i,v in enumerate(data["channels"][0]["videos"]):
        v["views_text"]=f"Original Actor and {i+4} more"
        v["views"]=4_000_000
    p.write_text(json.dumps(data),encoding="utf-8")
    report,_=prescreen(collected,tmp_path)
    assert report["counts"]["suspected_false_viral_view_labels"]==2
    assert report["counts"]["two_display_million_channels"]==0
    assert report["counts"]["queued_channels"]==0
    assert report["rejected_view_text_samples"][0]["raw_view_text"].endswith("more")


def test_view_text_numeric_mismatch_rejected(collected,tmp_path):
    _,run=collected
    p=run/"raw"/"lane_b_age_1_90_catalogs.json"
    data=json.loads(p.read_text(encoding="utf-8"))
    data["channels"][0]["videos"][0]["views_text"]="170K views"
    p.write_text(json.dumps(data),encoding="utf-8")
    report,_=prescreen(collected,tmp_path)
    assert report["counts"]["queued_channels"]==0
    assert report["counts"]["suspected_false_viral_view_labels"]>=1


def test_modern_bare_view_chip_must_share_video_age_context(collected,tmp_path):
    _,run=collected
    p=run/"raw"/"lane_b_age_1_90_catalogs.json"
    data=json.loads(p.read_text(encoding="utf-8"))
    for v in data["channels"][0]["videos"]:
        v["views_text"]="1.4M"
        v["views"]=1_400_000
        v["age_text"]="22h ago"
    p.write_text(json.dumps(data),encoding="utf-8")
    report,_=prescreen(collected,tmp_path)
    assert report["counts"]["queued_channels"]==1
    data["channels"][0]["videos"][1]["age_text"]=""
    p.write_text(json.dumps(data),encoding="utf-8")
    report=prescreen_company_public(collected[0],run,tmp_path/"badbare.json")
    assert report["counts"]["queued_channels"]==0


def test_empty_collected_catalog_is_unknown_not_negative_market_claim(collected,tmp_path):
    _,run=collected
    path=run/"raw"/"lane_b_age_1_90_catalogs.json"
    packet=json.loads(path.read_text(encoding="utf-8"))
    packet["channels"]=[]
    path.write_text(json.dumps(packet),encoding="utf-8")
    result,_=prescreen(collected,tmp_path)
    assert result["state"]=="INSUFFICIENT_CATALOG_COVERAGE"
    assert result["coverage_status"]=="INSUFFICIENT_PUBLIC_VIDEO_CATALOGS"
    assert result["counts"]["catalog_channels"]==0
    assert result["counts"]["verified_catalog_channels"]==0
    assert result["qualified_niches"]==0
    assert not result["eligible_for_cinecouncil_approval"]


def test_only_unverified_catalog_is_insufficient_not_clean_negative(collected,tmp_path):
    _,run=collected
    path=run/"raw"/"lane_b_age_1_90_catalogs.json"
    data=json.loads(path.read_text(encoding="utf-8"))
    data["channels"][0]["collection_status"]="ERROR"
    path.write_text(json.dumps(data),encoding="utf-8")
    result,_=prescreen(collected,tmp_path)
    assert result["state"]=="INSUFFICIENT_CATALOG_COVERAGE"


def test_limited_about_lookup_coverage_is_transparent(collected,tmp_path):
    _,run=collected
    source=run/"raw"/"lane_b_broad_market_surface.json"
    packet=json.loads(source.read_text(encoding="utf-8"))
    packet["unique_channel_count"]=201
    packet["about_lookup_channel_count"]=12
    source.write_text(json.dumps(packet),encoding="utf-8")
    result,_=prescreen(collected,tmp_path)
    assert result["counts"]["unique_channel_count"]==201
    assert result["counts"]["about_lookup_channels"]==12
    assert result["counts"]["about_lookup_coverage_fraction"]==round(12/201,4)
    assert any("unexamined channel ages" in limitation
               for limitation in result["limitations"])


def test_unknown_age_catalog_sidecar_never_promotes_and_rejects_tampering(collected,tmp_path):
    import hashlib
    root,run=collected
    raw=run/"raw"
    processed=run/"processed"
    processed.mkdir()
    triage_file=processed/"lane_b_unknown_age_catalog_triage.json"
    catalog_file=raw/"lane_b_unknown_age_catalogs.json"
    about_file=raw/"lane_b_unknown_age_after_catalog_about.json"
    review_file=processed/"lane_b_unknown_age_catalog_age_review.json"
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    catalog_file.write_text(json.dumps({"channels":[{"channel_id":OTHER,"videos":[]}]}),encoding="utf-8")
    about_file.write_text(json.dumps({"rows":[]}),encoding="utf-8")
    triage_file.write_text(json.dumps({"schema":"cine.company.unknown_age_catalog_triage.v1",
        "catalog_sha256":sha(catalog_file),"triage":[]}),encoding="utf-8")
    review_file.write_text(json.dumps({
        "schema":"cine.company.unknown_age_catalog_age_review.v1",
        "triage_sha256":sha(triage_file),"about_sha256":sha(about_file),
        "official_data_api_verified":False,"qualified_niches":0,
        "owner_approval_allowed":False,
        "candidate_public_two_million_and_age_window":0,
        "channels":[{"channel_id":OTHER,"status":"PUBLIC_AGE_OVER_30D;NOT_NEW_CHANNEL",
                     "two_million_longform_proxy":True}]}),encoding="utf-8")
    rep=prescreen_company_public(root,run,tmp_path/"reviewed.json")
    assert rep["counts"]["unknown_age_catalog_review_channels"]==1
    assert rep["counts"]["unknown_age_two_million_proxy_channels"]==1
    assert rep["unknown_age_research_watchlist"][0]["owner_approval_eligible"] is False
    assert rep["qualified_niches"]==0
    triage_file.write_text(triage_file.read_text(encoding="utf-8")+" ",encoding="utf-8")
    with pytest.raises(ValueError,match="Untrusted unknown-age"):
        prescreen_company_public(root,run,tmp_path/"tampered.json")
