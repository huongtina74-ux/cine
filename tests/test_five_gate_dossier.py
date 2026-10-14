from __future__ import annotations
import json
from datetime import datetime,timedelta,timezone

import pytest

from cinefactory.research_intelligence.breakout_proof import audit_official_artifact
from cinefactory.research_intelligence.five_gate_dossier import build_five_gate_dossier
from cinefactory.research_intelligence.council import verify_registry

NOW=datetime(2026,10,9,12,tzinfo=timezone.utc)
YOUNG="UC"+"y"*22
MATURE1="UC"+"m"*22
MATURE2="UC"+"n"*22
NEW_ENTRANT="UC"+"e"*22
A,B,C,D,E="ABCdef12345","GHIjkl67890","QWErty12345","LKJhgf67890","MNBvcx12345"


def when(days=0):
    return (NOW-timedelta(days=days)).isoformat()


def entry(cid,age):
    return {"channel_id":cid,"created_at":when(age),
            "evidence_status":"VERIFIED","channel_url":"https://www.youtube.com/channel/"+cid}


def vid(cid,ident,views=1500000,published=2,title="Original fantasy animation"):
    return {"video_id":ident,"channel_id":cid,"title":title,
            "video_url":"https://www.youtube.com/watch?v="+ident,
            "published_at":when(published),"duration_seconds":900,"views":views,
            "format_proxy":"LONG_FORM","privacy_status":"public","evidence_status":"VERIFIED"}


def topic(ids):
    return {"video_ids":ids,"fit":"DIRECT","status":"REVIEWED",
            "why":"Reviewed same fantasy animation structure, original characters, and long-form format"}


@pytest.fixture
def evidence(tmp_path):
    official={"generated_at":when(),"source":"test_canonical_fixture","channels":{
        YOUNG:entry(YOUNG,10),MATURE1:entry(MATURE1,900),MATURE2:entry(MATURE2,1000),
        NEW_ENTRANT:entry(NEW_ENTRANT,15),
    },"catalogs":{
        YOUNG:[vid(YOUNG,A),vid(YOUNG,B)],
        MATURE1:[vid(MATURE1,C,views=450000,published=8)],
        MATURE2:[vid(MATURE2,D,views=185000,published=12)],
        NEW_ENTRANT:[vid(NEW_ENTRANT,E,views=175000,published=5)],
    }}
    source=tmp_path/"official.json"
    source.write_text(json.dumps(official),encoding="utf-8")
    audit=tmp_path/"breakout.json"
    audit_official_artifact(source,audit,observed_at=when())
    review={
        "niche":"Minecraft animation","format_key":"reaction-mystery-comedy-narrative",
        "reviewed_by":"fixture_review","reviewed_at":when(),
        "novelty":{"status":"REVIEWED",
                   "differentiation":"Distinct reactive mystery narrative versus standard Minecraft animations; needs independent review"},
        "topic_fit":{YOUNG:topic([A,B])},
        "evergreen":[{"channel_id":MATURE1,"video_id":C,**topic([C])},
                     {"channel_id":MATURE2,"video_id":D,**topic([D])}],
        "entry":{"channel_id":NEW_ENTRANT,"video_id":E,**topic([E])},
        "business":{"status":"REVIEWED","rpm_usd":4.0,"monthly_views_assumed":1200000,
                    "monthly_fixed_cost_usd":1000,"production_cost_usd_per_video":100,
                    "videos_per_month":10},
    }
    review_path=tmp_path/"review.json"
    review_path.write_text(json.dumps(review),encoding="utf-8")
    return source,audit,review_path


def dossier(evidence,tmp_path,name="dossier",as_of=None,portfolio=None):
    return build_five_gate_dossier(*evidence,tmp_path/name,as_of=as_of or when(),portfolio=portfolio)


def test_ready_for_cross_exam_but_never_approved(evidence,tmp_path):
    case=dossier(evidence,tmp_path)
    assert case["state"]=="READY_FOR_CINECOUNCIL_CROSS_EXAMINATION"
    assert set(case["gates"])=={"novelty","breakout","evergreen","business","entry"}
    assert all(g["state"]!="NEEDS_EVIDENCE" for g in case["gates"].values())
    assert case["gates"]["business"]["scenarios"][1]["profit_usd"]==2800
    assert case["gates"]["evergreen"]["channels"] and len(case["gates"]["evergreen"]["channels"])==2
    assert case["gates"]["breakout"]["topic_matched_channels"]==[YOUNG]
    assert not case["council_has_decided"]
    assert not case["production_permission"]
    assert not case["reviewer_identity_authenticated"]
    folder=tmp_path/"dossier"
    registry=json.loads((folder/"council_evidence_registry.json").read_text(encoding="utf-8"))
    assert len(verify_registry(registry))==3
    questions=json.loads((folder/"council_tasks.json").read_text(encoding="utf-8"))
    assert questions["state"]=="PENDING_EXPLICIT_REVIEW"
    assert "quality" in questions["questions"]
    assert json.loads((folder/"council_issue.json").read_text(encoding="utf-8"))["issue_id"].startswith(case["case_id"])


def test_breakout_audit_source_tampering_fail_closed(evidence,tmp_path):
    source,audit,review=evidence
    source.write_text(source.read_text(encoding="utf-8")+" ",encoding="utf-8")
    with pytest.raises(ValueError,match="does not match"):
        build_five_gate_dossier(source,audit,review,tmp_path/"tamper",as_of=when())


def test_breakout_report_witness_forgery_detected(evidence,tmp_path):
    source,audit,review=evidence
    payload=json.loads(audit.read_text(encoding="utf-8"))
    payload["witness_channels"][0]["witness_count"]=99
    audit.write_text(json.dumps(payload),encoding="utf-8")
    with pytest.raises(ValueError,match="differs"):
        build_five_gate_dossier(source,audit,review,tmp_path/"forged",as_of=when())


def test_historical_source_kept_out_of_current_daily(evidence,tmp_path):
    case=dossier(evidence,tmp_path,as_of=when(-4))
    assert case["state"]=="WATCHLIST_RESEARCH_INCOMPLETE"
    assert case["gates"]["breakout"]["state"]=="NEEDS_EVIDENCE"
    assert case["gates"]["evergreen"]["state"]=="NEEDS_EVIDENCE"


def test_same_entrant_is_not_independent_competition(evidence,tmp_path):
    source,audit,review=evidence
    data=json.loads(review.read_text(encoding="utf-8"))
    data["entry"]["channel_id"]=YOUNG
    data["entry"]["video_id"]=A
    data["entry"]["video_ids"]=[A]
    review.write_text(json.dumps(data),encoding="utf-8")
    case=dossier(evidence,tmp_path)
    assert case["gates"]["entry"]["state"]=="NEEDS_EVIDENCE"
    assert case["state"]=="WATCHLIST_RESEARCH_INCOMPLETE"


def test_evergreen_needs_two_distinct_old_active_channels(evidence,tmp_path):
    source,audit,review=evidence
    data=json.loads(review.read_text(encoding="utf-8"))
    data["evergreen"][1]["channel_id"]=MATURE1
    review.write_text(json.dumps(data),encoding="utf-8")
    case=dossier(evidence,tmp_path)
    assert case["gates"]["evergreen"]["state"]=="NEEDS_EVIDENCE"


def test_profit_model_includes_costs_and_no_guarantee(evidence,tmp_path):
    source,audit,review=evidence
    data=json.loads(review.read_text(encoding="utf-8"))
    data["business"]["monthly_fixed_cost_usd"]=8000
    review.write_text(json.dumps(data),encoding="utf-8")
    case=dossier(evidence,tmp_path)
    assert case["gates"]["business"]["state"]=="NEEDS_EVIDENCE"
    assert not case["gates"]["business"]["expected_profit_is_guaranteed"]


def test_old_format_collision_blocks_novelty(evidence,tmp_path):
    case=dossier(evidence,tmp_path,portfolio=[{
        "niche":"Minecraft animation", "format_key":"reaction-mystery-comedy-narrative"
    }])
    assert case["gates"]["novelty"]["state"]=="NEEDS_EVIDENCE"


def test_rights_risk_for_full_movie_puts_review_on_hold(evidence,tmp_path):
    source,audit,review=evidence
    packet=json.loads(source.read_text(encoding="utf-8"))
    packet["catalogs"][YOUNG][0]["title"]="FULL MOVIE Hindi Dubbed"
    source.write_text(json.dumps(packet),encoding="utf-8")
    audit_official_artifact(source,audit,observed_at=when())
    case=dossier(evidence,tmp_path)
    assert case["state"]=="RIGHTS_REVIEW_HOLD"
    assert "hindi dubbed" in case["gates"]["breakout"]["rights_risk_markers"]


def test_missing_topic_review_is_not_automatic_niche_match(evidence,tmp_path):
    source,audit,review=evidence
    data=json.loads(review.read_text(encoding="utf-8"))
    del data["topic_fit"][YOUNG]
    review.write_text(json.dumps(data),encoding="utf-8")
    case=dossier(evidence,tmp_path)
    assert case["gates"]["breakout"]["metadata_witness_channels"]==[YOUNG]
    assert case["gates"]["breakout"]["topic_matched_channels"]==[]
    assert case["state"]=="WATCHLIST_RESEARCH_INCOMPLETE"


def test_council_registry_fails_if_reviewer_file_changed(evidence,tmp_path):
    case=dossier(evidence,tmp_path)
    folder=tmp_path/"dossier"
    reg=json.loads((folder/"council_evidence_registry.json").read_text(encoding="utf-8"))
    review=evidence[2]
    review.write_text(review.read_text(encoding="utf-8")+" ",encoding="utf-8")
    with pytest.raises(ValueError,match="tampered"):
        verify_registry(reg)


def test_single_council_case_with_absent_opinions_remains_not_approved(evidence,tmp_path):
    from cinefactory.research_intelligence.five_gate_dossier import finalize_five_gate_council
    build_five_gate_dossier(*evidence,tmp_path/"single",as_of=when())
    opinions=tmp_path/"no_opinions.json"
    opinions.write_text("[]",encoding="utf-8")
    result=finalize_five_gate_council(tmp_path/"single",opinions)
    assert result["council_state"]=="INSUFFICIENT_REVIEW"
    assert result["state"]=="CINECOUNCIL_DISAGREEMENT_OR_MISSING_REVIEW"
    assert result["production_permission"] is False
    assert json.loads((tmp_path/"single"/"case.json").read_text(encoding="utf-8"))["issue_id"]==result["issue_id"]


def test_council_refuses_tampered_dossier(evidence,tmp_path):
    from cinefactory.research_intelligence.five_gate_dossier import finalize_five_gate_council
    build_five_gate_dossier(*evidence,tmp_path/"case",as_of=when())
    path=tmp_path/"case"/"dossier.json"
    data=json.loads(path.read_text(encoding="utf-8"))
    data["state"]="READY_FOR_CINECOUNCIL_CROSS_EXAMINATION_FAKE"
    path.write_text(json.dumps(data),encoding="utf-8")
    opinions=tmp_path/"opinions.json"
    opinions.write_text("[]",encoding="utf-8")
    with pytest.raises(ValueError,match="changed"):
        finalize_five_gate_council(tmp_path/"case",opinions)


def test_rights_risk_cannot_be_hidden_by_missing_topic_review(evidence,tmp_path):
    source,audit,review=evidence
    packet=json.loads(source.read_text(encoding="utf-8"))
    packet["catalogs"][YOUNG][1]["title"]="Unauthorized Full Movie English Dubbed"
    source.write_text(json.dumps(packet),encoding="utf-8")
    audit_official_artifact(source,audit,observed_at=when())
    obj=json.loads(review.read_text(encoding="utf-8"))
    obj["topic_fit"]={}
    review.write_text(json.dumps(obj),encoding="utf-8")
    case=dossier(evidence,tmp_path)
    assert case["state"]=="RIGHTS_REVIEW_HOLD"
    assert "english dubbed" in case["gates"]["breakout"]["rights_risk_markers"]
    assert case["gates"]["breakout"]["topic_matched_channels"]==[]


def test_reviewer_claim_before_source_collection_not_valid(evidence,tmp_path):
    source,audit,review=evidence
    obj=json.loads(review.read_text(encoding="utf-8"))
    obj["reviewed_at"]=when(1)
    review.write_text(json.dumps(obj),encoding="utf-8")
    case=dossier(evidence,tmp_path)
    assert case["state"]=="WATCHLIST_RESEARCH_INCOMPLETE"
    assert case["gates"]["novelty"]["state"]=="NEEDS_EVIDENCE"


def test_review_prep_reuses_exact_official_channels_but_preapproves_nothing(evidence,tmp_path):
    from cinefactory.research_intelligence.five_gate_dossier import prepare_five_gate_review
    prepared=prepare_five_gate_review(evidence[0],evidence[1],tmp_path/"prepared.json",as_of=when())
    assert prepared["state"]=="MANUAL_REVIEW_REQUIRED"
    assert prepared["counts"]["breakout_witness_channels"]==1
    assert prepared["counts"]["mature_video_evidence_candidates"]==2
    assert prepared["counts"]["new_entrant_evidence_candidates"]==1
    assert prepared["topic_fit"][YOUNG]["status"]=="PENDING"
    assert prepared["entry"]["channel_id"]==NEW_ENTRANT
    assert all(v["fit"]=="UNKNOWN" for v in prepared["evergreen"])
    assert prepared["niche"]==""
    assert prepared["business"]["rpm_usd"] is None
    with pytest.raises(ValueError,match="Named niche review"):
        build_five_gate_dossier(evidence[0],evidence[1],tmp_path/"prepared.json",
                                tmp_path/"no_approval",as_of=when())


def test_review_prep_source_tampering_fails(evidence,tmp_path):
    from cinefactory.research_intelligence.five_gate_dossier import prepare_five_gate_review
    source=evidence[0]
    source.write_text(source.read_text(encoding="utf-8")+" ",encoding="utf-8")
    with pytest.raises(ValueError,match="revision mismatch"):
        prepare_five_gate_review(source,evidence[1],tmp_path/"invalid.json",as_of=when())
