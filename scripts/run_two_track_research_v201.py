"""CineFactory v1.6.41 daily two-branch report and optional frontier.

No automatic approval. No Claude Code invoked, no paid API by default.
Run after the existing saved-snapshot daily discovery scan, not instead of it.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from cinefactory.studio.two_track_research_v201 import (
    DualResearchStore,generate_two_track_daily,LANE_TO_NICHE,
)
from cinefactory.studio.research_frontier_v201 import find_frontier
from cinefactory.studio.channel_provenance_v201 import official_channel_refresh
from cinefactory.studio.approved_niche_keyword_scan_v201 import search_approved_formats

def write_owner_briefs(report:dict,frontier:dict|None,deep:dict|None)->dict:
    """ASCII-safe Markdown in the remote Windows environment."""
    directory=ROOT/"data/research/youtube_breakout/two_track_reports"
    directory.mkdir(parents=True,exist_ok=True)
    stamp=Path(report["report_path"]).stem.removeprefix("two_track_")
    b1=report["branch_1_global_new_niche_scan"]
    b2=report["branch_2_approved_niche_studies"]
    frontier_rows=(frontier or {}).get("candidate_videos",[])
    branch1=[
        "# BRANCH 1 - DAILY GLOBAL NEW NICHE OPPORTUNITY RESEARCH",
        "",
        "**Status:** "+b1["status"],
        "**Verified 0-30 day old channels:** "+str(b1["verified_born_0_30d_channels_in_ledger"]),
        "",
        "## Non-negotiable evidence gates",
        "",
        "1. Truly different niche or independently documented different production method.",
        "2. YouTube channel created 0-30 days ago with credible date evidence.",
        "3. SAME new channel has 2+ DISTINCT long-form videos of 8+ minutes, EACH with 1,000,000+ views.",
        "4. Established same-format channels (age >=365 days) still receive >=100,000 views on recent long videos.",
        "5. Low copyright and reuse risk, production scalability, ability for new channels to compete.",
        "6. Monthly revenue of $1k to $1m is an UNVERIFIED business hypothesis, not proven from competitor views.",
        "",
        "## Current evidence-checked proposed novel formats",
    ]
    if not b1["candidate_fingerprint_proposals"]:
        branch1.append("- None have been independently classified as a verified new format.")
    for item in b1["candidate_fingerprint_proposals"]:
        branch1.append(f"- {item['fingerprint']}: {item['status']}")
        for reason in item["missing_evidence"]:
            branch1.append("  - Missing: "+reason)
    branch1.extend(["","## Open-ended discovery backlog: NOT confirmed niches"])
    if not frontier_rows:
        branch1.append("- No frontier video in the current cycle.")
    for row in frontier_rows[:15]:
        title=row["title"].replace("|","/").replace("\n"," ")[:95]
        branch1.append(
            f"- [{title}]({row['url']}): {row['public_view_count']:,} views, "
            f"{row['published_utc_day']} {row['format_status']}. "
            "CHANNEL BIRTH, 2x1M and mature demand NOT VERIFIED.")
    branch1.extend(["","NO niche will be auto-approved for content production.",""])
    first=directory/("BRANCH_1_GLOBAL_OPPORTUNITIES_"+stamp+".md")
    first.write_text("\n".join(branch1)+"\n",encoding="utf-8")
    branch2=[
        "# BRANCH 2 - CONTINUOUS DEEP RESEARCH FOR USER APPROVED FORMATS",
        "",
        "**Status:** "+b2["status"],
        "**Approved formats:** "+str(b2["approved_format_count"]),
        "Per approved format: A) market leaders and popular/recent outliers; "
        "B) emerging channels born <=30 days; "
        "C) same-format 1M+ long videos published <=15 days ago.",
        "",
    ]
    if not b2["approved_research"]:
        branch2.append("No owner approval exists. Deep research of unapproved niches stays OFF.")
    packet_dir=ROOT/"data/research/youtube_breakout/approved_agent_handoffs"
    packet_dir.mkdir(parents=True,exist_ok=True)
    packet_paths=[]
    for scoped in b2["approved_research"]:
        niche,fmt=scoped["niche_id"],scoped["format_id"]
        branch2.extend([
            f"## {niche} / {fmt}",
            "### Cohort A: established leaders, popular videos and recent outliers",
        ])
        if not scoped["cohort_A_leaders"]:
            branch2.append("- No sufficient source-verified leader and historical baseline.")
        for leader in scoped["cohort_A_leaders"]:
            branch2.append(
                f"- {leader['channel']}: {len(leader['popular_videos'])} sampled popular, "
                f"{len(leader['recent_uploads'])} recent, "
                f"{len(leader['recent_outperformance_vs_same_channel_median'])} outlier uploads.")
        branch2.append("### Cohort B: newly created channels <=30 days")
        if not scoped["cohort_B_new_channels"]:
            branch2.append("- No age-verified recent new channel with a >=1M video.")
        for candidate in scoped["cohort_B_new_channels"]:
            branch2.append(
                f"- {candidate['channel']}: {len(candidate['over_1m_videos'])} 1M+ videos; "
                f"two-million-view-videos gate: {candidate['two_million_videos_condition_met']}.")
        branch2.append("### Cohort C: new viral uploads 0-15 days, 1M+ views")
        if not scoped["cohort_C_trends_0_15d_million"]:
            branch2.append("- No 1M+ trend clips observed within the bounded source sample.")
        for v in scoped["cohort_C_trends_0_15d_million"][:15]:
            branch2.append(
                f"- [{v['title'][:90]}]({v['url']}), "
                f"views={v['views']:,}, age_days={v['age_days_from_utc_day']}.")
        branch2.extend([
            "### Creative production handoff",
            "Research verified repeated format patterns; build only ORIGINAL scripts, "
            "characters, assets, voice and music. Evaluate niche-appropriate tools, "
            "models, render/capture runtimes, scripts, thumbnails, SEO, cost and rights.",
            "Create a pilot, QC actual video/audio, then measure owned-channel CTR, "
            "retention, views and cost per accepted minute. No guaranteed virality.",
        ])
        packet={
            "schema":"CineFactory-Approved-Niche-Research-Handoff-v1.6.41",
            "niche_id":niche,"format_id":fmt,"evidence":scoped,
            "authorized_scope":"RESEARCH_ONLY_ON_USER_APPROVED_FORMAT",
            "research_departments":["INTELLIGENCE","YOUTUBE_GROWTH_SEO",
                "DATA_ANALYTICS","CREATIVE_STRATEGY","PLANNING","DIRECTION",
                "WRITERS_ROOM","PRODUCTION_DESIGN","TECHNICAL_DIRECTION",
                "AUDIO","EDITORIAL","QC","RIGHTS","RND"],
            "required_questions":[
                "Which patterns repeatedly distinguish popular videos?",
                "Which new uploads overperform against recent channel baselines?",
                "Which new channels had real 0-30 day ages and 1M+ clips?",
                "What original short-lived trends are adaptable or too risky?",
                "What original production method is best after measured benchmarks?",
                "What did our own first-party CTR/retention show and what should change?"
            ],
            "model_or_tool_invoked":False,"can_publish":False,
            "full_video_playback_not_proven":True,
        }
        pp=packet_dir/(niche+"_"+fmt+"_"+stamp+".json")
        pp.write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding="utf-8")
        packet_paths.append(str(pp))
    second=directory/("BRANCH_2_APPROVED_NICHES_"+stamp+".md")
    second.write_text("\n".join(branch2)+"\n",encoding="utf-8")
    return {"branch_1_markdown":str(first),"branch_2_markdown":str(second),
            "approved_niche_agent_packets":packet_paths}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--with-frontier",action="store_true",
                        help="Bounded additional public searches beyond the 14 known niche formats")
    parser.add_argument("--scan-approved",action="store_true",
                        help="Scan extra format-specific keywords ONLY for user-approved niche formats")
    parser.add_argument("--discover-technologies",action="store_true",
                        help="Public bounded GitHub research; pending evidence only, never install models")
    parser.add_argument("--refresh-channel-facts-if-key-present",action="store_true",
                        help="Optional YouTube Data API read-only channels.list if env key is configured")
    parser.add_argument("--approve-niche",nargs=2,metavar=("NICHE","FORMAT"),
                        help="ONLY interactive user request, requires exact confirmation phrase")
    parser.add_argument("--pause-niche",nargs=2,metavar=("NICHE","FORMAT"))
    parser.add_argument("--confirmation",type=str,default="",
                        help="For authorized explicit approval; never added to scheduler")
    parser.add_argument("--propose-format",nargs=4,
                        metavar=("NAME","FINGERPRINT","PARENT_NICHE","DIFFERENCE"),
                        help="Explicit hypothesis entry, NOT proof new niche or permission")
    args=parser.parse_args()
    path=ROOT/"data/research/youtube_breakout/cinefactory_breakout.sqlite3"
    store=DualResearchStore(path)
    timestamp=dt.datetime.now(dt.timezone.utc).isoformat()
    if args.approve_niche:
        niche,fmt=args.approve_niche
        if args.confirmation!=f"DUYET {niche} {fmt}":
            raise PermissionError("USER_MUST_EXPLICITLY_CONFIRM_APPROVAL_PHRASE")
        store.approve(niche,fmt,actor="USER_EXPLICIT_APPROVAL",
                      note="User personally requested activation of per-niche research",
                      at=timestamp)
        print("NICHE_DEEP_RESEARCH_USER_APPROVED",niche,fmt)
        # Approval is an explicit user selection: immediately collect public
        # format-scoped rivals/videos instead of silently waiting for tomorrow.
        # All evidence stays research-only; no media production or publication.
        args.scan_approved=True
    if args.pause_niche:
        niche,fmt=args.pause_niche
        if args.confirmation!=f"DUNG {niche} {fmt}":
            raise PermissionError("USER_MUST_EXPLICITLY_CONFIRM_PAUSE_PHRASE")
        store.pause(niche,fmt,actor="USER_EXPLICIT_APPROVAL")
        print("NICHE_RESEARCH_PAUSED",niche,fmt)
        return
    if args.propose_format:
        name,fingerprint,parent,difference=args.propose_format
        pid=store.propose_format(name,fingerprint,parent,difference,timestamp)
        print("NOVEL_FORMAT_UNVERIFIED_PROPOSAL_CREATED",pid)
        return
    proof={"status":"NO_KEY_AGES_REMAIN_UNKNOWN","channels_updated":0}
    if args.refresh_channel_facts_if_key_present:
        # No configured key? Refuse to infer date from the upload timestamp.
        with store._db() as db:
            ids=[r[0] for r in db.execute("SELECT DISTINCT channel_id FROM videos WHERE channel_id IS NOT NULL ORDER BY first_seen DESC LIMIT 25").fetchall()]
            ids.extend(r[0] for r in db.execute("SELECT channel_id FROM channels LIMIT 5").fetchall())
        proof=official_channel_refresh(store,list(dict.fromkeys(ids))[:30])
    frontier=None
    if args.with_frontier:
        frontier=find_frontier(root=ROOT,queries=4,limit_per_query=3,max_watch=8)
    approved_scan=None
    if args.scan_approved:
        approved_scan=search_approved_formats(root=ROOT,per_niche_keywords=4,
                                            per_query=20,max_total_metadata=48)
    report=generate_two_track_daily(ROOT)
    owner_reports=write_owner_briefs(report,frontier,approved_scan)
    # The broad rival catalogue is separately ranked and does not conflate
    # keyword-search order with popularity or pretend to be full AV review.
    catalog=None
    if args.scan_approved:
        from cinefactory.studio.approved_minecraft_rival_catalog_v256 import (
            compile_approved_minecraft_catalog)
        catalog=compile_approved_minecraft_catalog(ROOT)
        if catalog.get("format_reports") and catalog.get("unique_metadata_videos_90d_before_format_gate",0)>0:
            with Path(owner_reports["branch_2_markdown"]).open("a",encoding="utf-8") as out:
                out.write("\\n## WIDER PUBLIC VIDEO CATALOGUE (provisional candidates, not full media audit)\\n")
                for block in catalog["format_reports"]:
                    out.write(f"### {block['format_id']}\\n")
                    out.write(f"- {block['matching_video_count_90d']} matching 90-day candidate videos; "+
                              f"{len(block['rival_channel_candidates'])} channel candidates; "+
                              f"{block['breakouts_1m_within_14d_snapshot_count']} verified-by-age breakout snapshots.\\n")
                    for vid in block["confirmed_current_snapshot_million_14d"][:10]:
                        out.write(f"- [{vid['title'][:90]}]({vid['url']}): "+
                                  f"{vid['views_observed']:,} views, observed {vid['observed_on']}; "+
                                  "title/metadata only, awaiting source A/V review.\\n")
    watch_report=None
    watch_refresh=None
    if args.scan_approved:
        from cinefactory.studio.niche_continuous_watch_v258 import NicheCompetitorWatch
        watch=NicheCompetitorWatch(ROOT)
        if catalog and catalog.get("format_reports"):
            watch.seed_from_catalog(catalog)
        if approved_scan:
            watch.seed_from_keyword_scan(approved_scan,observed_at=approved_scan.get("observed_at",timestamp))
        watch_refresh=watch.refresh_followed(max_channels=80,max_metadata=160)
        watch_report=watch.report()
    technology_scan={"status":"NOT_REQUESTED","reports":[]}
    if args.discover_technologies:
        from cinefactory.studio.technology_discovery_v211 import (
            run_technology_discovery,
        )
        # Rotate through all configured approved-for-research production
        # markets each day, even if no YouTube channel passed the breakout
        # evidentiary gates. This is R&D only and does NOT approve a niche.
        scan_cycle=(
            ("minecraft_story_adventure","minecraft"),
            ("minecraft_school_comedy","minecraft"),
            ("minecraft_recorded_survival","minecraft"),
            ("minecraft_live_gameplay","minecraft"),
            ("roblox_animation","roblox_animation"),
            ("long_slide_game","long_slices_game"),
            ("asmr_sleep","asmr_sleep_hands_objects"),
            ("audio_storytelling_seniors","audio_storytelling_seniors"),
            ("fishing_silent","fishing_silent"),
            ("rain_sleep_white_noise","rain_sleep_white_noise"),
        )
        start=dt.datetime.now(dt.timezone.utc).timetuple().tm_yday % len(scan_cycle)
        options=[scan_cycle[(start+i)%len(scan_cycle)] for i in range(2)]
        findings=[]
        for minor,major in options:
            findings.append(run_technology_discovery(
                ROOT,minor_niche=minor,major_niche=major,
                discover_public=True,max_queries=1,
            ))
        tech_dir=ROOT/"data/research/technology_discovery/daily"
        tech_dir.mkdir(parents=True,exist_ok=True)
        dst=tech_dir/(
            dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")+".json"
        )
        technology_scan={
            "schema":"cine.research.daily_technology_scan.v211",
            "status":"PUBLIC_DISCOVERY_COMPLETED_OR_ERRORS_RECORDED",
            "new_candidate_count":sum(
                len(x["pending_queue"]["pending_additions"])+
                len(x["model_pending_queue"]["pending_additions"])
                for x in findings),
            "public_search_errors":sum(len(x["source_errors"]) for x in findings),
            "source_context":"ROTATING_EXISTING_CINEFACTORY_FORMATS_NOT_PROVEN_TRENDS",
            "model_installations":0,"paid_api_calls":0,"production_approvals":0,
            "reports":findings,
        }
        technology_scan["report_path"]=str(dst)
        # v212 whole-company watch: official software/AI releases, Anthropic
        # Claude/Agent SDK/plugins, SaaS sites and MCP Registry metadata.
        # Fixed list, 4 sources/day (rotated); model permissions remain off.
        from cinefactory.studio.technology_watch_v212 import watch_public_sources
        technology_scan["whole_company_source_watch"]=watch_public_sources(
            ROOT,max_sources=4,
        )
        # Persist the official-source watch result together with niche R&D,
        # not just in transient stdout and independent SHA evidence receipts.
        with dst.open("x",encoding="utf8") as fp:
            fp.write(json.dumps(technology_scan,ensure_ascii=False,indent=2)+"\n")
    branch1=report["branch_1_global_new_niche_scan"]
    branch2=report["branch_2_approved_niche_studies"]
    output={
        "branch1_status":branch1["status"],
        "branch1_newborn_channels_proven":branch1["verified_born_0_30d_channels_in_ledger"],
        "branch1_new_proposals_checked":len(branch1["candidate_fingerprint_proposals"]),
        "branch2_status":branch2["status"],
        "branch2_approved_formats":branch2["approved_format_count"],
        "approved_keyword_scan":approved_scan["status"] if approved_scan else "NOT_REQUESTED",
        "approved_keyword_metadata_checks":approved_scan.get("full_metadata_checks",0) if approved_scan else 0,
        "continuous_watchlist_channels":watch_report["tracked_channels"] if watch_report else None,
        "continuous_watchlist_videos":watch_report["tracked_videos"] if watch_report else None,
        "continuous_watchlist_report":watch_report.get("report_path") if watch_report else None,
        "watchlist_refresh_status":watch_refresh["status"] if watch_refresh else "NOT_REQUESTED",
        "watchlist_refresh_metadata_attempted":watch_refresh["metadata_attempted"] if watch_refresh else 0,
        "watchlist_new_same_format_video_candidates":watch_refresh["new_same_format_video_candidates"] if watch_refresh else 0,
        "public_frontier_unknown_count":frontier["unclassified_count"] if frontier else None,
        "official_channel_birth_verification":proof,
        "historical_public_video_snapshots":report["data_sources"]["public_video_snapshots"],
        "full_videos_watched":False,
        "claude_code_auto_used":False,
        "report_file":report["report_path"],
        "branch1_owner_markdown":owner_reports["branch_1_markdown"],
        "branch2_owner_markdown":owner_reports["branch_2_markdown"],
        "approved_niche_agent_packets":len(owner_reports["approved_niche_agent_packets"]),
        "scoped_minecraft_catalog_status":catalog["status"] if catalog else "NOT_REQUESTED",
        "scoped_minecraft_catalog_path":catalog.get("report_path") if catalog else None,
        "scoped_minecraft_format_counts":([
            {"format_id":f["format_id"],"candidate_videos_90d":f["matching_video_count_90d"],
             "candidate_rival_channels":len(f["rival_channel_candidates"]),
             "million_14d":f["breakouts_1m_within_14d_snapshot_count"]}
            for f in catalog.get("format_reports",[])] if catalog else []),
        "technology_discovery":technology_scan["status"],
        "technology_new_pending":technology_scan.get("new_candidate_count",0),
        "technology_source_errors":technology_scan.get("public_search_errors",0),
        "technology_research_report":technology_scan.get("report_path"),
        "technology_watch_sources_checked":len(
            technology_scan.get("whole_company_source_watch",{}).get("sources_requested",[])
        ),
        "technology_watch_source_errors":len(
            technology_scan.get("whole_company_source_watch",{}).get("source_errors",[])
        ),
        "claude_or_mcp_auto_invoked":False,
    }
    print("CINEFACTORY_TWO_BRANCH_DAILY_REPORT",json.dumps(output,ensure_ascii=False))
if __name__=="__main__":main()
