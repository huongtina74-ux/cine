"""Bounded once-per-day READ-ONLY dispatcher for locally approved niche pods.

The scheduler/user supplies up-to-date canonical bridge snapshots; this module
does not fetch YouTube, call a model, self-authenticate approval or render.
Only native, hash-verified Company imports may advance an observation report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .market_bridge import verify_imported_company_sources
from .pod_watch import watch_niche
from .niche_work_orders import create_niche_work_orders
from .niche_media_intake import process_niche_media


def _parse_utc(v):
    result=datetime.fromisoformat(str(v).replace("Z","+00:00"))
    if result.tzinfo is None:raise ValueError("Timezone-aware observation required")
    return result.astimezone(timezone.utc)


def dispatch_pods_once(pod_root, bridges_root, output_root, *, as_of=None, max_pods=50,
                       authorized_media_manifest=None, max_media_videos=3):
    if not 1<=max_pods<=200:raise ValueError("Pod budget 1..200")
    at=_parse_utc(as_of) if as_of else datetime.now(timezone.utc)
    pods=Path(pod_root).resolve(strict=True)
    bridges=Path(bridges_root).resolve(strict=True)
    dest=Path(output_root).resolve()
    if dest.exists():raise FileExistsError("Immutable dispatch destination; use a unique day/attempt")
    snapshots={}
    conflicting_snapshot_keys=set()
    source_files=sorted(bridges.rglob("*.json"))
    if len(source_files)>2000:
        raise ValueError("More than 2000 bridge JSON files; narrow input directory before dispatch")
    for file in source_files:
        if not file.is_file() or file.stat().st_size>10_000_000:continue
        try:
            item=json.loads(file.read_text(encoding="utf-8"))
            if not isinstance(item,dict):continue
            if item.get("schema")!="cine.bridge.company_snapshot.v1":continue
            age=(at-_parse_utc(item["as_of"])).total_seconds()/3600
            if not 0<=age<=168:continue
            if not verify_imported_company_sources(item):continue
            key=(item.get("niche"),item.get("format_key"),item.get("source_project"))
            snapshots.setdefault(key,[]).append((item["as_of"],file,item))
        except (OSError,ValueError,KeyError,TypeError):
            continue
    for key, rows in snapshots.items():
        rows.sort(key=lambda x:_parse_utc(x[0]),reverse=True)
        # Two exports at the same instant are one snapshot only if identical.
        # Different content at identical time is conflicting evidence, not a
        # view-velocity measurement or an arbitrary previous snapshot.
        seen_at={}
        unique=[]
        for recorded,file,item in rows:
            instant=_parse_utc(recorded)
            if instant in seen_at:
                if seen_at[instant]!=item:
                    conflicting_snapshot_keys.add(key)
                continue
            seen_at[instant]=item
            unique.append((recorded,file,item))
        snapshots[key]=unique
    paths=sorted(pods.rglob("pod.json"))
    if len(paths)>max_pods:
        raise ValueError("More pods than max_pods; refuse incomplete silent traversal")
    tasks=[]
    dest.mkdir(parents=True)
    for path in paths:
        try:
            pod=json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(pod,dict):
                raise ValueError("Malformed pod configuration")
            if pod.get("schema")!="cine.niche.pod.v1" or pod.get("state")!="CONFIGURED_NOT_SCHEDULED":
                raise ValueError("Pod not in approved local configuration state")
            key=(pod["niche"],pod["format_key"],pod["source_company"])
            if key in conflicting_snapshot_keys:
                raise ValueError("Conflicting same-time snapshots require source reconciliation")
            matched=snapshots.get(key,[])
            if not matched:raise FileNotFoundError("No verified recent Company snapshot for pod")
            current=matched[0][2]
            hours=(at-_parse_utc(current["as_of"])).total_seconds()/3600
            if hours>48:raise ValueError("Latest verified snapshot too old for a daily watch")
            previous=matched[1][2] if len(matched)>1 else None
            safe=hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:16]
            target=dest/("pod_"+safe)
            target.mkdir(parents=True,exist_ok=True)
            result=watch_niche(pod,current,target/"watch.json",previous=previous,as_of=at.isoformat())
            research=create_niche_work_orders(target/"watch.json",target/"research_work_orders.json")
            media=None
            if authorized_media_manifest:
                media=process_niche_media(
                    target/"research_work_orders.json",authorized_media_manifest,
                    target/"authorized_media_review",max_videos=max_media_videos)
            task={"niche_id":pod["niche_id"],"state":"READ_ONLY_WATCH_COMPLETE",
                  "authorized_media_intake":str(target/"authorized_media_review"/"media_intake.json") if media else None,
                  "authorized_media_state":media["state"] if media else "NO_AUTHORIZED_MEDIA_ATTACHED",
                  "semantic_research_complete":False,
                  "research_work_orders":str(target/"research_work_orders.json"),
                  "research_lane_counts":research["lane_counts"],
                  "multimodal_analysis_state":research["state"],
                  "watch_report":str(target/"watch.json"),
                  "video_records":len(result["videos"]),
                  "alerts":len(result["alerts"]),
                  "next_steps":["Timestamped licensed-media scene study",
                                "Leader/newcomer trend review and independent Quality challenge"],
                  "production_permission":False,
                  "automated_models_executed":False}
        except (OSError,ValueError,KeyError,TypeError) as exc:
            task={"niche_id":path.parent.name,"state":"BLOCKED_NO_VERIFIED_CURRENT_INPUT",
                  "reason":str(exc)[:300],"production_permission":False}
        tasks.append(task)
    states={x["state"] for x in tasks}
    state=("NO_PODS" if not tasks else
           "WATCHES_COMPLETE" if states=={"READ_ONLY_WATCH_COMPLETE"} else
           "PARTIAL_BLOCKED" if "READ_ONLY_WATCH_COMPLETE" in states else "BLOCKED")
    summary={
        "schema":"cine.niche.pod_dispatch.v1",
        "as_of":at.isoformat(),"state":state,"pods_discovered":len(tasks),
        "watch_reports_created":sum(x["state"]=="READ_ONLY_WATCH_COMPLETE" for x in tasks),
        "tasks":tasks,
        "external_model_calls":0,"youtube_api_calls":0,
        "owner_event_authenticated_by_this_runner":False,
        "scheduled_task_installed_by_this_runner":False,
        "full_video_research_complete":False,
        "automated_production_or_upload":False}
    (dest/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return summary


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--pods-root",required=True)
    cli.add_argument("--bridges-root",required=True)
    cli.add_argument("--output-root",required=True)
    cli.add_argument("--as-of")
    cli.add_argument("--max-pods",type=int,default=50)
    cli.add_argument("--authorized-media-manifest")
    cli.add_argument("--max-media-videos",type=int,default=3)
    args=cli.parse_args()
    result=dispatch_pods_once(args.pods_root,args.bridges_root,args.output_root,
                              as_of=args.as_of,max_pods=args.max_pods,
                              authorized_media_manifest=args.authorized_media_manifest,
                              max_media_videos=args.max_media_videos)
    print(json.dumps({"state":result["state"],"pods_discovered":result["pods_discovered"],
                      "watch_reports_created":result["watch_reports_created"],
                      "summary":str(Path(args.output_root).resolve()/"summary.json")},ensure_ascii=False))


if __name__=="__main__":
    main()
