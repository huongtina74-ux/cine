"""Evidence research integrates the SAME Company public collectors, without approval shortcuts."""
from __future__ import annotations
import json
from datetime import datetime,timedelta,timezone
from pathlib import Path
import pytest

from cinefactory.research_intelligence.evidence_research import (
    plan_research_channels, analyze_research_evidence, prepare_evidence_council,
)
from cinefactory.research_intelligence.council import verify_registry

NOW=datetime.now(timezone.utc).replace(microsecond=0)
NEW="UC"+"a"*22
LEADER="UC"+"b"*22
MATURE="UC"+"c"*22
V1,V2,V3,V4=("ABCdef12345","GHIjkl67890","QWErty12345","LKJhgf67890")

def when(days=0):
    return (NOW-timedelta(days=days)).isoformat()

def obs(cid, vid, age_days, subscribers, label):
    return {"channel_id":cid,"video_id":vid,"joined_date":(NOW-timedelta(days=age_days)).date().isoformat(),
            "subscriber_count_text":subscribers,"channel_name":label,"query":"minecraft animation story",
            "seed_cluster":"Minecraft animation","video_title":f"{label} story"}

def film(vid,views="1.3M",age=2,minutes=14):
    view={"1.3M":1300000,"130K":130000,"80K":80000}.get(views,4000000)
    return {"video_id":vid,"video_url":f"https://www.youtube.com/watch?v={vid}",
            "views_text":views,"views":view,"age_text":f"{age}d ago",
            "video_age_days":age,"duration_seconds":minutes*60,
            "format_proxy":"LONG_FORM","title":"Minecraft animation original story"}

@pytest.fixture
def fixtures(tmp_path):
    research=tmp_path/"capture"
    research.mkdir()
    search={"status":"COMPLETE","generated_at":when(),
            "successful_query_count":1,"query_count":1,
            "observations":[
                obs(NEW,V1,9,"2K subscribers","New entrant"),
                obs(NEW,V2,9,"2K subscribers","New entrant"),
                obs(LEADER,V3,1500,"1.7M subscribers","Mature leader"),
                obs(MATURE,V4,900,"123K subscribers","Mature peer"),
            ]}
    sp=research/"search.json"
    sp.write_text(json.dumps(search),encoding="utf-8")
    catalog={"generated_at":when(),"channels":[
        {"channel_id":NEW,"collection_status":"VERIFIED",
         "videos":[film(V1,"1.3M"),film(V2,"1.3M",4)]},
        {"channel_id":LEADER,"collection_status":"VERIFIED",
         "videos":[film(V3,"1.3M",7)]},
        {"channel_id":MATURE,"collection_status":"VERIFIED",
         "videos":[film(V4,"130K",5)]}
    ]}
    cp=research/"catalog.json"
    cp.write_text(json.dumps(catalog),encoding="utf-8")
    return sp,cp,search,catalog


def create(fixtures,tmp_path,*,as_of=None):
    sp,cp,_,_=fixtures
    plan=plan_research_channels(sp,tmp_path/"plan",niche="Minecraft animation",max_channels=3,as_of=as_of or when())
    report=analyze_research_evidence(tmp_path/"plan"/"plan.json",cp,tmp_path/"evidence.json",as_of=as_of or when())
    return plan,report


def test_source_backed_balanced_research_and_council(fixtures,tmp_path):
    plan,report=create(fixtures,tmp_path)
    assert plan["state"]=="COLLECT_CATALOGS"
    assert len(plan["selected"])==3
    assert {x["bucket"] for x in plan["selected"]}=={"newcomer","mature_leader","mature"}
    assert report["state"]=="PUBLIC_EVIDENCE_READY_FOR_REVIEW"
    assert report["counts"]["two_million_newcomer_proxies"]==1
    assert report["counts"]["mature_recent_demand_proxies"]==2
    assert report["counts"]["fresh_0_15d_million_view_proxies"]==3
    assert report["strict_breakout_witnesses"]==0
    assert report["five_gate_status"]=="NOT_EVALUATED"
    assert not report["eligible_for_owner_approval"]
    council=prepare_evidence_council(tmp_path/"evidence.json",tmp_path/"council")
    assert council["state"]=="PENDING_APPROVED_DEPARTMENT_REVIEW"
    reg=json.loads((tmp_path/"council"/"council_evidence_registry.json").read_text(encoding="utf-8"))
    sources=verify_registry(reg)
    assert len({s["independent_root"] for s in sources.values()})==1
    assert council["production_permission"] is False


def test_original_source_mutation_blocks_analysis(fixtures,tmp_path):
    sp,cp,search,_=fixtures
    plan_research_channels(sp,tmp_path/"plan",niche="Minecraft animation",as_of=when())
    sp.write_text(json.dumps(search,indent=2),encoding="utf-8")
    with pytest.raises(ValueError,match="mutated"):
        analyze_research_evidence(tmp_path/"plan"/"plan.json",cp,tmp_path/"report.json",as_of=when())


def test_untrusted_million_from_more_cannot_enter_audit(fixtures,tmp_path):
    sp,cp,_,cat=fixtures
    cat["channels"][0]["videos"][1]["views_text"]="Story Channel and 4 more"
    cat["channels"][0]["videos"][1]["views"]=4000000
    cp.write_text(json.dumps(cat),encoding="utf-8")
    _,report=create(fixtures,tmp_path)
    assert report["counts"]["two_million_newcomer_proxies"]==0
    assert not report["channels"][0]["two_million_display_proxy"]


def test_shorts_and_short_videos_not_counted(fixtures,tmp_path):
    sp,cp,_,cat=fixtures
    cat["channels"][0]["videos"][1]["duration_seconds"]=45
    cp.write_text(json.dumps(cat),encoding="utf-8")
    _,report=create(fixtures,tmp_path)
    assert report["counts"]["two_million_newcomer_proxies"]==0


def test_catalog_channel_swap_blocked(fixtures,tmp_path):
    sp,cp,_,cat=fixtures
    cat["channels"][0]["channel_id"]="UC"+"z"*22
    cp.write_text(json.dumps(cat),encoding="utf-8")
    plan_research_channels(sp,tmp_path/"plan",niche="Minecraft animation",as_of=when())
    with pytest.raises(ValueError,match="unexpected"):
        analyze_research_evidence(tmp_path/"plan"/"plan.json",cp,tmp_path/"report.json",as_of=when())


def test_same_video_across_channels_not_double_counted(fixtures,tmp_path):
    sp,cp,_,cat=fixtures
    cat["channels"][1]["videos"].append(film(V1))
    cp.write_text(json.dumps(cat),encoding="utf-8")
    _,report=create(fixtures,tmp_path)
    assert report["counts"]["cross_channel_video_id_conflicts"]==1
    assert report["counts"]["two_million_newcomer_proxies"]==0


def test_history_never_current_even_if_previously_viral(fixtures,tmp_path):
    late=(NOW+timedelta(days=7)).isoformat()
    plan,report=create(fixtures,tmp_path,as_of=late)
    assert plan["state"]=="HISTORICAL_ONLY"
    assert report["state"]=="HISTORICAL_ONLY"
    assert report["eligible_for_owner_approval"] is False


def test_partial_catalog_does_not_claim_complete(fixtures,tmp_path):
    sp,cp,_,cat=fixtures
    cat["channels"][0]["collection_status"]="UNKNOWN"
    cp.write_text(json.dumps(cat),encoding="utf-8")
    _,report=create(fixtures,tmp_path)
    assert report["state"]=="PARTIAL_EVIDENCE"
    assert report["counts"]["catalog_errors"]==1


def test_video_ages_unknown_are_not_fresh_breakout(fixtures,tmp_path):
    sp,cp,_,cat=fixtures
    cat["channels"][0]["videos"][0]["video_age_days"]=None
    cat["channels"][0]["videos"][1]["video_age_days"]=None
    cp.write_text(json.dumps(cat),encoding="utf-8")
    _,report=create(fixtures,tmp_path)
    assert report["counts"]["fresh_0_15d_million_view_proxies"]==1
    assert report["strict_breakout_witnesses"]==0


def test_niche_must_match_exact_collector_seed(fixtures,tmp_path):
    sp,cp,_,cat=fixtures
    plan=plan_research_channels(sp,tmp_path/"plan",niche="Fishing silent",as_of=when())
    assert plan["state"]=="NO_MATCHING_CHANNELS"
    assert not plan["selected"]


def test_missing_council_review_cannot_self_authorize(fixtures,tmp_path):
    create(fixtures,tmp_path)
    tasks=prepare_evidence_council(tmp_path/"evidence.json",tmp_path/"council")
    assert "quality" in tasks["roles"]
    assert not tasks["production_permission"]
    with pytest.raises(FileExistsError):
        prepare_evidence_council(tmp_path/"evidence.json",tmp_path/"council")


def test_one_command_live_pipeline_with_mocked_canonical_collectors(fixtures,tmp_path,monkeypatch):
    import shutil
    from cinefactory.research_intelligence.evidence_research import run_live_evidence_research
    from cinefactory.research_intelligence import daily_research
    company=tmp_path/"Company Youtube"
    scripts=company/"scripts"
    scripts.mkdir(parents=True)
    for name in ("collect_youtubejs_recent_search.mjs","collect_youtubejs_channel_catalogs.mjs"):
        (scripts/name).write_text("// mocked canonical collector",encoding="utf-8")
    yjs=tmp_path/"node_modules"/"youtubei.js"/"dist"/"src"/"platform"/"node.js"
    yjs.parent.mkdir(parents=True)
    yjs.write_text("// mock",encoding="utf-8")
    queries=tmp_path/"queries.json"
    queries.write_text(json.dumps([{"query":"minecraft animation story",
                                    "seed_cluster":"Minecraft animation"}]),encoding="utf-8")
    search,catalog=fixtures[0:2]
    calls=[]
    def runner(args,cwd,timeout_seconds):
        calls.append(args)
        path=Path(args[args.index("--output")+1])
        path.parent.mkdir(parents=True,exist_ok=True)
        if "recent_search" in args[1]:
            path.write_bytes(search.read_bytes())
        else:
            path.write_bytes(catalog.read_bytes())
        return "ok","",0,False
    monkeypatch.setattr("shutil.which",lambda _: "node")
    monkeypatch.setattr(daily_research,"_run_with_timeout_tree",runner)
    import io
    from PIL import Image
    def fake_thumb(vid):
        buf=io.BytesIO()
        Image.new("RGB",(320,180),(123,98,73)).save(buf,format="JPEG")
        return buf.getvalue()
    monkeypatch.setattr("cinefactory.research_intelligence.deep_video_intelligence._public_thumbnail",fake_thumb)
    result=run_live_evidence_research(company,queries,yjs,tmp_path/"run",
                                      niche="Minecraft animation",max_channels=3,deep_thumbnail_budget=2)
    assert result["state"]=="REVIEW_PACKET_CREATED"
    assert result["deep_intelligence"]["verified_thumbnail_integrity_count"]==2
    assert result["deep_intelligence"]["full_video_semantics_completed"] is False
    assert (tmp_path/"run"/"deep_intelligence"/"deep_review.json").is_file()
    assert len(calls)==2
    assert result["counts"]["two_million_newcomer_proxies"]==1
    assert (tmp_path/"run"/"council"/"council_issue.json").exists()
    assert (tmp_path/"run"/"live_run_manifest.json").exists()
    with pytest.raises(FileExistsError):
        run_live_evidence_research(company,queries,yjs,tmp_path/"run",
                                  niche="Minecraft animation")


def test_live_pipeline_timeout_never_promotes_provisional_data(fixtures,tmp_path,monkeypatch):
    from cinefactory.research_intelligence.evidence_research import run_live_evidence_research
    from cinefactory.research_intelligence import daily_research
    company=tmp_path/"Company Youtube"
    scripts=company/"scripts"
    scripts.mkdir(parents=True)
    for name in ("collect_youtubejs_recent_search.mjs","collect_youtubejs_channel_catalogs.mjs"):
        (scripts/name).write_text("mock",encoding="utf-8")
    yjs=tmp_path/"youtubei.js"/"node.js"
    yjs.parent.mkdir()
    yjs.write_text("mock",encoding="utf-8")
    queries=tmp_path/"queries.json"
    queries.write_text(json.dumps([{"query":"minecraft animation story",
                                    "seed_cluster":"Minecraft animation"}]),encoding="utf-8")
    monkeypatch.setattr("shutil.which",lambda _: "node")
    monkeypatch.setattr(daily_research,"_run_with_timeout_tree",
                        lambda *args: ("","timeout",-1,True))
    result=run_live_evidence_research(company,queries,yjs,tmp_path/"timedout",
                                      niche="Minecraft animation",max_channels=3)
    assert result["state"]=="FAILED_OR_INCOMPLETE"
    assert result["failure_stage"]=="search_COLLECTOR_TIMEOUT"
    assert result["production_permission"] is False
    assert not (tmp_path/"timedout"/"council").exists()


def test_live_query_niche_mismatch_before_side_effect(fixtures,tmp_path):
    from cinefactory.research_intelligence.evidence_research import run_live_evidence_research
    company=tmp_path/"Company Youtube"
    scripts=company/"scripts"
    scripts.mkdir(parents=True)
    for name in ("collect_youtubejs_recent_search.mjs","collect_youtubejs_channel_catalogs.mjs"):
        (scripts/name).write_text("mock",encoding="utf-8")
    yjs=tmp_path/"youtubei.js"/"node.js"
    yjs.parent.mkdir()
    yjs.write_text("mock",encoding="utf-8")
    queries=tmp_path/"wrong.json"
    queries.write_text(json.dumps([{"query":"roblox animation", "seed_cluster":"Roblox"}]),
                       encoding="utf-8")
    with pytest.raises(ValueError,match="share one niche"):
        run_live_evidence_research(company,queries,yjs,tmp_path/"should_not_exist",
                                  niche="Minecraft animation")
    assert not (tmp_path/"should_not_exist").exists()


def test_cross_topic_viral_video_excluded_from_niche_trend(fixtures,tmp_path):
    sp,cp,_,catalog=fixtures
    catalog["channels"][1]["videos"][0]["title"]="POPPY PLAYTIME vs THE PLAYER (Poppy Playtime Animation)"
    cp.write_text(json.dumps(catalog),encoding="utf-8")
    _,report=create(fixtures,tmp_path)
    assert report["counts"]["fresh_0_15d_million_view_proxies"]==2
    assert report["counts"]["excluded_cross_topic_fresh_million_view_proxies"]==1
    leader=next(x for x in report["channels"] if x["channel_id"]==LEADER)
    assert leader["fresh_0_15d_million_proxy_ids"]==[]
    assert leader["excluded_cross_topic_fresh_million_video_ids"]==[V3]
    assert leader["sample_longform_videos"][0]["topic_title_alignment"]=="NOT_TITLE_ALIGNED"


def test_work_packets_have_exact_video_ids_without_semantic_autoapproval(fixtures,tmp_path):
    _,report=create(fixtures,tmp_path)
    tasks=report["per_video_work_packets"]
    assert len(tasks["leader_review"])==1
    assert tasks["leader_review"][0]["video_id"]==V3
    assert len(tasks["newcomer_review"])==1
    assert set(tasks["newcomer_review"][0]["candidate_video_ids"])=={V1,V2}
    assert {x["video_id"] for x in tasks["fresh_million_review"]}=={V1,V2,V3}
    assert not tasks["cross_topic_qa"]
    assert all(x["status"].startswith("PENDING") for x in tasks["fresh_million_review"])
    assert report["five_gate_status"]=="NOT_EVALUATED"


def test_cross_topic_viral_video_is_queued_for_quality_only(fixtures,tmp_path):
    sp,cp,_,catalog=fixtures
    catalog["channels"][1]["videos"][0]["title"]="POPPY PLAYTIME vs THE PLAYER (Animation)"
    cp.write_text(json.dumps(catalog),encoding="utf-8")
    _,report=create(fixtures,tmp_path)
    tasks=report["per_video_work_packets"]
    assert V3 not in {x["video_id"] for x in tasks["fresh_million_review"]}
    assert V3 in {x["video_id"] for x in tasks["cross_topic_qa"]}


def test_human_readable_evidence_report_does_not_claim_verified_niche(fixtures,tmp_path):
    _,report=create(fixtures,tmp_path)
    markdown=(tmp_path/"evidence.md").read_text(encoding="utf-8")
    assert "Public Evidence Research" in markdown
    assert "NOT niche certification" in markdown
    assert "No proof of actual YouTube recommendation traffic" in markdown
    assert "Top established channels" in markdown
    assert report["strict_breakout_witnesses"]==0
