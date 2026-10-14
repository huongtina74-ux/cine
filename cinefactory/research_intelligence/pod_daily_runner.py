"""Durable, idempotent-once-per-attempt daily pod watch scheduler entrypoint.

Only processes owner-configured pods & verified Company snapshots. Does NOT
perform searches itself, run cloud agents, publish videos or grant approval.
"""
from __future__ import annotations
import argparse,json,os
from datetime import datetime,timezone
from pathlib import Path

from .pod_dispatch import dispatch_pods_once


def run_pod_daily(pods_root,bridges_root,state_root,*,day=None,max_pods=50):
    when=day or datetime.now().astimezone().date().isoformat()
    if datetime.strptime(when,"%Y-%m-%d").strftime("%Y-%m-%d")!=when:
        raise ValueError("Exact YYYY-MM-DD partition required")
    root=Path(state_root).resolve()
    root.mkdir(parents=True,exist_ok=True)
    partition=root/when;partition.mkdir(parents=True,exist_ok=True)
    lock=partition/".dispatcher.lock"
    # Only one daily dispatcher process for that partition. No unsafe stale lock removal.
    fd=None
    try:
        fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        os.write(fd,str(os.getpid()).encode());os.close(fd);fd=None
    except FileExistsError as exc:
        raise RuntimeError("Pod dispatcher already running or stale lock needs manual review") from exc
    try:
        dirs=sorted(p for p in partition.glob("attempt_*") if p.is_dir())
        attempt=1+max((int(p.name.split("_")[1]) for p in dirs
                       if p.name.split("_")[1].isdigit()),default=0)
        path=partition/f"attempt_{attempt:03d}"
        try:
            payload=dispatch_pods_once(pods_root,bridges_root,path,
                                       max_pods=max_pods)
            result={"schema":"cine.niche.daily_dispatch_run.v1","date":when,
                    "attempt":attempt,"state":payload["state"],
                    "pod_count":payload["pods_discovered"],
                    "watch_reports":payload["watch_reports_created"],
                    "summary_path":str(path/"summary.json"),
                    "production_permission":False,
                    "external_model_calls":0}
        except (OSError,ValueError,KeyError,TypeError,RuntimeError) as exc:
            path.mkdir(exist_ok=True)
            # Do not leak source path/permissions or misleading partial results.
            result={"schema":"cine.niche.daily_dispatch_run.v1","date":when,
                    "attempt":attempt,"state":"BLOCKED_DISPATCH_ERROR",
                    "error_type":type(exc).__name__,
                    "partial_artifacts_may_exist":True,"pod_count":None,
                    "watch_reports":None,"summary_path":str(path/"summary.json"),
                    "production_permission":False,"external_model_calls":0}
            (path/"summary.json").write_text(
                json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        # Atomic replacement keeps latest_run.json readable across crashes.
        latest_tmp=partition/".latest_run.json.tmp"
        latest_tmp.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        os.replace(latest_tmp,partition/"latest_run.json")
        return result
    finally:
        if fd is not None:os.close(fd)
        lock.unlink(missing_ok=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--pods-root",required=True)
    parser.add_argument("--bridges-root",required=True)
    parser.add_argument("--state-root",required=True)
    parser.add_argument("--day")
    parser.add_argument("--max-pods",type=int,default=50)
    args=parser.parse_args()
    result=run_pod_daily(args.pods_root,args.bridges_root,args.state_root,
                         day=args.day,max_pods=args.max_pods)
    print(json.dumps(result))
    if result["state"] not in ("NO_PODS","WATCHES_COMPLETE"):
        raise SystemExit(2)
