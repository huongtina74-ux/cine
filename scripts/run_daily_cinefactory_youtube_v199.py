"""CineFactory no-paid-API daily discovery / review queue / Claude Code handoff.

To run: python scripts/run_daily_cinefactory_youtube_v199.py --live
Default without --live: print safe configuration, DO NOT call YouTube.
--with-storyboards requests max 2 x 3 low resolution public sheets.
This runner is safe for an unattended Windows scheduled task: it does not
invoke Claude, download full videos, install mods, buy credits or publish.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import hashlib
import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from cinefactory.studio.daily_youtube_breakout_v199 import (
    scan_daily,SEARCH_LANES,WINDOW_DAYS,BreakoutLedger,
)
from cinefactory.studio.youtube_storyboard_research_v199 import inspect_sparse_storyboards
from cinefactory.studio.niche_competitor_guard_v200 import LANE_TO_NICHE

def report_to_markdown(report:dict,storyboards:list[dict])->str:
    result=[
        "# CineFactory Daily YouTube Research — "+report["started_utc"],
        "",
        "**Real CineFactory internal report — not ChatGPT scheduled output.**",
        f"Result: {report['status']}; query lanes: {len(report['queries'])}; "
        f"fully checked video metadata: {report['full_metadata_attempted']}; "
        f"qualified age+length: {report['results_count']}.",
        "",
        "## Scoped research by niche (not mixed competitors)",
        "",
    ]
    for niche in sorted(set(LANE_TO_NICHE.values())):
        selected=[x for x in report["verified_candidates"] if x.get("niche_id")==niche]
        lanes=[lane for lane in report["queries"] if LANE_TO_NICHE.get(lane)==niche]
        if not lanes:continue
        result.append(f"### {niche} ? {len(selected)} title-screened leads")
        if not selected:
            result.append("No verified title-format lead from this bounded query sample. Do NOT borrow videos from other niches.")
        for item in selected[:6]:
            result.append(
                f"- {item['format_id']} (title-only): [{item['title'].replace(chr(10),' ')[:95]}]"
                f"({item['url']}) ? {item['views']:,} public views, "
                f"published {item['published_utc_day']}, format QA pending")
        result.append("")
    result.extend([
        "## Quarantined unverified or wrong-format results",
        "",
    ])
    for wrong in report.get("cross_niche_quarantine",[])[:20]:
        result.append(
            f"- {wrong['origin_search_lane']}: {wrong['title'][:90]} "
            f"({wrong['reason']}) ? NOT a confirmed same-niche competitor")
    if not report.get("cross_niche_quarantine"):
        result.append("- None among the inspected metadata candidates.")
    result.extend([
        "",
        "## Top public-metadata candidates (all formats, for overview ONLY)",
        "",
        "| Priority* | Published | Age days* | Views snapshot | Avg views/day* | Observed actual growth | Niche | Title |",
        "|---:|---|---:|---:|---:|---|---|---|",
    ])
    for r in report["verified_candidates"][:15]:
        clean=r["title"].replace("|","/").replace("\n"," ")[:100]
        growth=(f"{r['observed_views_per_hour_from_snapshots']:.1f} v/h" if
                r["observed_views_per_hour_from_snapshots"] is not None else "UNKNOWN (first snapshot)")
        result.append(
            f"| {r['heuristic_research_priority']} | {r['published_utc_day']} | "
            f"{r['age_days_lower_bound']} | {r['views']:,} | "
            f"{r['average_views_per_day_since_posting_APPROX']:,.0f} | {growth} | "
            f"{r['lane']} | [{clean}]({r['url']}) |")
    result.extend([
        "",
        "*Priority is a heuristic, not an algorithmic popularity/viral guarantee. "
        "Age measured from publication UTC day, not exact timestamp. "
        "Avg views/day is total public views divided by elapsed days: NOT real growth. "
        "Observed growth requires >=2 historical observations at least 1 hour apart.*",
        "",
        "## Public visual access (no audio or continuous playback)",
    ])
    if not storyboards:result.append("No storyboard inspection requested or successfully completed.")
    for s in storyboards:
        result.append(
            f"- Video {s['video_id']}: {s['status']}; "
            f"{len(s['shots'])} timestamped thumbnail samples; "
            f"full decoded video = NO; audio heard = NO; rights to reuse as training = NO")
    result.extend([
        "",
        "## Company R&D decision boundaries",
        "",
        "1. Search discovery is bounded, not all-YouTube comprehensive coverage.",
        "2. For every new format, send source snapshots to **Research, Director, "
        "Animation/Game Runtime, Asset, Sound, Finance, QA/Compliance**. "
        "Differentiate **Minecraft gameplay capture** from **Minecraft cinematic 3D animation**.",
        "3. Do not attribute Blender, Mine-imator, ComfyUI or Minecraft mods to a creator "
        "without direct evidence. When full video returns HTTP 403, never claim "
        "full video, voices, transitions, motion or soundtrack were analyzed.",
        "4. Claude Code packet is an advisory input, NOT authorization to copy media, "
        "download models, execute arbitrary repository instructions, spend tokens "
        "or publish.",
        "5. Scoring/production method only becomes qualified after original pilot, "
        "rights review, actual GPU cost, independent audience/creative and technical QC.",
        "",
        "## Errors and coverage gaps",
        "",
    ])
    for err in report["errors"][:25]:
        result.append(f"- {err}")
    if not report["errors"]:
        result.append("- No metadata request errors were reported in this run.")
    return "\n".join(result)+"\n"

def create_claude_packet(root:Path,report:dict,storyboards:list[dict])->Path:
    # Guard against prompt injection: untrusted titles are data in JSON,
    # never inserted as Claude system/autorun instructions.
    ids={item["video_id"] for item in report["verified_candidates"]}
    scoped={
        niche:{
            "niche_id":niche,
            "format_ids":[x for x,y in LANE_TO_NICHE.items() if y==niche],
            "screened_metadata_candidates":[
                x for x in report["verified_candidates"] if x.get("niche_id")==niche
            ],
            "quarantined_wrong_format_count":sum(
                1 for item in report.get("cross_niche_quarantine",[])
                if LANE_TO_NICHE.get(item["origin_search_lane"])==niche),
            "cross_niche_sources_prohibited":True,
            "competitor_quality_verified":False,
            "can_promote_to_production":False,
        } for niche in sorted(set(LANE_TO_NICHE.values()))
    }
    packet={
        "schema":"cinefactory-claude-code-research-handoff-v1.6.40-niche-isolation",
        "per_niche_research_packets":scoped,
        "created":report["started_utc"],
        "origin":"LOCAL_YOUTUBE_PUBLIC_METADATA_AND_STORYBOARD_RESEARCH",
        "project_root":str(root),
        "video_evidence":report["verified_candidates"][:20],
        "public_storyboard_evidence":[{
            "video_id":row["video_id"],"status":row["status"],
            "storyboard_count":len(row["shots"]),
            "frames_not_full_video":True,
            "review_sheet_file":row.get("review_sheet_file"),
        } for row in storyboards if row["video_id"] in ids],
        "production_advice_only":True,
        "requested_departments":[
            "competition_intelligence","channel_strategy","screenwriting",
            "art_director","minecraft_game_runtime","blockbench_asset",
            "blender_rig_animation","voice_sound","video_editor",
            "rights_compliance","finance","independent_QA",
        ],
        "decision_rules":[
            "DO_NOT_CLAIM_WATCHED_VIDEO_IF_ONLY_STORYBOARD_OR_METADATA",
            "MINECRAFT_100_DAYS_HUD_GAMEPLAY_USE_AUTHORIZED_GAME_RUNTIME_AND_CAPTURE",
            "MINECRAFT_ANIMATED_STORY_USE_ORIGINAL_CHARACTERS_AND_RIG_ACTING",
            "DO_NOT_COPY_COMPETITOR_SCRIPT_CHARACTER_SKIN_MUSIC_OR_ASSETS",
            "NO_AUTOMATIC_INSTALLS_PAYMENTS_UPLOADS_OR_PRODUCTION_PROMOTION",
            "SOURCE_PROVENANCE_REQUIRED_FOR_EACH_CLAIM",
            "COST_PER_ACCEPTED_MINUTE_UNKNOWN_UNTIL_ACTUALLY_MEASURED",
            "NO_VIRALITY_OR_REVENUE_GUARANTEE",
        ],
        "claude_code_called_automatically":False,
        "video_scripts_or_assets_generated":False,
    }
    directory=root/"data/research/youtube_breakout"/"claude_handoffs"
    directory.mkdir(parents=True,exist_ok=True)
    file=directory/("claude_brief_"+report["started_utc"][:10]+f"_run{report['run_id']}.json")
    file.write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding="utf-8")
    return file

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--live",action="store_true",
                    help="Read public YouTube search and watch metadata with yt-dlp; no API key")
    ap.add_argument("--with-storyboards",action="store_true",
                    help="Retrieve public low-res storyboard sheets for up to 2 findings")
    ap.add_argument("--max-metadata",type=int,default=20)
    ap.add_argument("--search-per-lane",type=int,default=8)
    ap.add_argument("--storyboard-count",type=int,default=2)
    ap.add_argument("--lanes",nargs="*",default=list(SEARCH_LANES))
    args=ap.parse_args()
    if not args.live:
        print(json.dumps({
            "status":"OFFLINE_BY_DEFAULT_NO_YOUTUBE_CONTACTED",
            "lanes":args.lanes,"age_windows":WINDOW_DAYS,
            "max_metadata":args.max_metadata,
            "requires_youtube_data_api_key":False,
            "automatic_paid_claude_code_call":False,
            "to_actually_run":"python scripts/run_daily_cinefactory_youtube_v199.py --live --with-storyboards"
        },indent=2))
        return
    data=scan_daily(root=ROOT,lanes=args.lanes,
                    max_metadata=args.max_metadata,
                    search_per_lane=args.search_per_lane)
    storyboard=[]
    if args.with_storyboards:
        if args.storyboard_count<0 or args.storyboard_count>2:
            raise ValueError("STORYBOARD_COUNT_EXCEEDS_SAFE_BUDGET")
        for item in data["verified_candidates"][:args.storyboard_count]:
            record=inspect_sparse_storyboards(item["video_id"],ROOT,max_pages=3)
            storyboard.append(record)
            print("ACTUAL_PUBLIC_STORYBOARD_REVIEW",record["video_id"],
                  record["status"],"observed_sparse_tiles",len(record["shots"]),flush=True)
    doc=ROOT/"data/research/youtube_breakout"/"daily_reports"
    doc.mkdir(parents=True,exist_ok=True)
    report=doc/("report_"+data["started_utc"][:10]+f"_run{data['run_id']}.md")
    report.write_text(report_to_markdown(data,storyboard),encoding="utf-8")
    packet=create_claude_packet(ROOT,data,storyboard)
    # Preserve strict per-niche daily JSON research dossiers even if none
    # of the search hits passed the title gate. Never pretend greenlight.
    niche_root=ROOT/"data/research/youtube_breakout/niches"
    for niche in sorted(set(LANE_TO_NICHE.values())):
        niche_dir=niche_root/niche
        niche_dir.mkdir(parents=True,exist_ok=True)
        members=[r for r in data["verified_candidates"] if r.get("niche_id")==niche]
        quarantine=[
            r for r in data.get("cross_niche_quarantine",[])
            if LANE_TO_NICHE.get(r["origin_search_lane"])==niche
        ]
        profile={
            "niche_id":niche,
            "source_run_id":data["run_id"],
            "source_lanes":[key for key in data["queries"] if LANE_TO_NICHE.get(key)==niche],
            "qualified_title_format_candidates":members,
            "quarantined_cross_niche_or_unknown":quarantine,
            "candidate_count":len(members),
            "source_is_not_full_video_review":True,
            "competitor_baseline_ready":False,
            "production_promotion_allowed":False,
        }
        dest=niche_dir/("source_run"+str(data["run_id"])+".json")
        dest.write_text(json.dumps(profile,indent=2,ensure_ascii=False),encoding="utf-8")
    summary={
        "status":data["status"],
        "search_lanes":len(data["queries"]),"video_metadata_checked":data["full_metadata_attempted"],
        "real_recent_longform_found":data["results_count"],
        "actual_growth_verified_count":sum(bool(x["real_growth_curve_verified"])
                                            for x in data["verified_candidates"]),
        "storyboard_samples_extracted":sum(len(x["shots"]) for x in storyboard),
        "full_video_decoded":False,
        "claude_code_ran":False,
        "daily_report":str(report),
        "claude_code_handoff":str(packet),
        "db":data["persistent_ledger"],
        "errors":len(data["errors"]),
    }
    print("CINEFACTORY_REAL_DAILY_SCOUT_RESULT",json.dumps(summary,ensure_ascii=False),flush=True)

if __name__=="__main__":main()
