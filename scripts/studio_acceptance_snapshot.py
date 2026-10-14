"""Evidence-backed CineFactory audit snapshot; never certify animation by test count.

Provides machine-readable proof of discovered blockers for the TWO branches
and the media company. It is read-only apart from writing the new report.
"""
from __future__ import annotations
import argparse
import json
import subprocess
from datetime import datetime,timezone
from pathlib import Path


def load_optional(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,ValueError):
        return None


def run(repo, company, daily, output):
    root=Path(repo).resolve(strict=True)
    src=Path(company).resolve(strict=True)
    state=Path(daily).resolve(strict=True)
    report=Path(output).resolve()
    if report.exists():raise FileExistsError("Acceptance snapshot is immutable")
    def git(*args):
        p=subprocess.run(["git",*args],cwd=root,capture_output=True,text=True,timeout=15)
        return p.stdout.strip() if p.returncode==0 else "UNKNOWN"
    index=load_optional(state/"latest_health.json") or {}
    daily_path=Path(index.get("report","")) if index.get("report") else None
    current=load_optional(daily_path) if daily_path else None
    submitted=list((root/"data"/"projects").glob("*/autopilot_manifest.json"))
    sampled=[]
    for manifest in submitted[-40:]:
        obj=load_optional(manifest)
        if obj:
            sampled.append({"path":str(manifest),
                            "success":obj.get("success"),
                            "quality_certified":obj.get("quality_certified"),
                            "release_ready":obj.get("release_ready"),
                            "warnings":obj.get("warnings",[])[:2]})
    watch_reports=list(state.rglob("watch.json"))
    whole_review_files=list((root/"data"/"projects").rglob("whole_film_visual_qc.json"))
    bound_premium=list((root/"data"/"projects").rglob("premium_director_binding.json"))
    repo_pods=list((root/"data").rglob("pod.json"))
    company_root_exist=(src/"scripts"/"run_complete_niche_discovery.py").is_file()
    branch1={
        "state":current.get("state") if current else "NO_EVIDENCE",
        "last_run_id":current.get("run_id") if current else None,
        "latest_run_report":str(daily_path) if daily_path else None,
        "query_coverage":current.get("coverage") if current else None,
        "public_prescreen":current.get("public_prescreen") if current else None,
        "channel_breakout_gate":current.get("strict_0_30_two_1m_niche_gate") if current else "NOT_PROVEN",
        "qualified_niche_evidence":"NOT_VERIFIED",
        "company_scanner_present":company_root_exist,
        "operational_acceptance":False,
        "limitations":["Verified official 0-30d channel age/2x million evidence not complete",
                       "Daily scheduler hasn't demonstrated repeated successful canonical reports",
                       "Evergreen, entry, monetization and novelty still require multi-source review"],
    }
    branch2={
        "state":"WORKFLOWS_CODED_NOT_FULLY_ACTIVATED",
        "pod_configs_found":len(repo_pods),
        "watched_reports_found":len(watch_reports),
        "full_length_multi_video_semantic_review_passed":False,
        "actual_tool_comparative_pilots_passed":False,
        "production_approval_automated":False,
        "limitations":["Approved pod scheduling not proven",
                       "Actual competitor footage/captions/audio evidence incomplete",
                       "Independent cine-department review and authenticated owner permission not complete"],
    }
    production={
        "state":"DIAGNOSTIC_MEDIA_WORKFLOWS_EXIST_PREMIUM_NOT_CERTIFIED",
        "autopilot_manifests_found":len(submitted),
        "recent_manifest_samples":sampled[-6:],
        "whole_film_visual_review_records_found":len(whole_review_files),
        "premium_director_bindings_found":len(bound_premium),
        "default_visual_review_policy":"FAIL_CLOSED_WITH_DECLARED_DIAGNOSTIC_SLATE_EXCEPTION",
        "premium_release_approved":False,
        "disney_parity_or_competitor_superiority_proven":False,
        "limitations":["No independent approved long-form pilot side-by-side benchmark",
                       "Professional actor continuity, character expressions and soundtrack not certified",
                       "External Blender/Unreal/Resolve toolchains not fully connected to main Autopilot",
                       "ComfyUI real model workflow quality depends on installed approved pipeline"],
    }
    record={
        "schema":"cine.studio.acceptance_snapshot.v1",
        "observed_at_utc":datetime.now(timezone.utc).isoformat(),
        "repo":str(root),"git_head":git("rev-parse","--short","HEAD"),
        "git_worktree_status":git("status","--short"),
        "company_root":str(src),"daily_root":str(state),
        "branch_1":branch1,"branch_2":branch2,"production":production,
        "company_ready_for_unattended_commercial_release":False,
        "release_automation_enabled_by_audit":False,
        "external_model_or_gpu_process_started_by_audit":False,
        "next_release_gate":"Demonstrate real full-video competitor research + matched original film pilot + independently reviewed quality and throughput",
    }
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"state":"AUDIT_WRITTEN","repo_rev":record["git_head"],
                      "branch_1":branch1["state"],"branch_2":branch2["state"],
                      "production":production["state"],"report":str(report)}))
    return record


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo",required=True)
    parser.add_argument("--company-root",required=True)
    parser.add_argument("--state-root",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    run(args.repo,args.company_root,args.state_root,args.output)
