from __future__ import annotations
"""Run a bounded LIVE public Github research cycle, not installation/execution.

By default network is OFF. --live-public-github-read permits up to 10
unauthenticated read-only REST calls to pre-approved repo metadata+README.
No API tokens, subscriptions, model weights, videos or packages fetched.
"""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from cinefactory.studio.github_research_adapter_v194 import ResearchFetchPolicy
from cinefactory.studio.autonomous_source_research_v194 import AutonomousSourceResearchOrchestrator

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--live-public-github-read",action="store_true")
    parser.add_argument("--niches",nargs="+",default=[
        "preschool_3d_musical","long_slices_game","ai_family_drama"])
    parser.add_argument("--repo-cap",type=int,choices=(1,2,3,4,5),default=5)
    parser.add_argument("--no-readme",action="store_true")
    opts=parser.parse_args()
    policy=ResearchFetchPolicy(
        enable_public_https_network=opts.live_public_github_read,
        max_repos=opts.repo_cap,max_calls=10,
        timeout_seconds=10.,
    )
    engine=AutonomousSourceResearchOrchestrator(ROOT,policy=policy)
    r=engine.research(opts.niches,include_readme=not opts.no_readme)
    output=ROOT/"data"/"verification"/"v194_autonomous_research"
    output.mkdir(parents=True,exist_ok=True)
    default_niches=["preschool_3d_musical","long_slices_game","ai_family_drama"]
    canonical=(
        opts.live_public_github_read and opts.niches==default_niches
        and opts.repo_cap==5 and not opts.no_readme
    )
    if canonical:
        evidence_name="research_cycle_evidence_v194.json"
        summary_name="research_cycle_summary_v194.json"
    else:
        mode="live" if opts.live_public_github_read else "offline"
        safe_suffix="_".join(opts.niches)[:110]
        suffix=("_noreadme" if opts.no_readme else "")
        evidence_name=f"{mode}_{safe_suffix}{suffix}_evidence_v194.json"
        summary_name=f"{mode}_{safe_suffix}{suffix}_summary_v194.json"
    (output/evidence_name).write_text(
        r.model_dump_json(indent=2),encoding="utf-8")
    summary={
        "status":r.status,"live_github_public_read":r.network_read_authorized,
        "api_calls":r.fetch.api_calls,
        "fetched_repos":len(r.fetch.fetched),
        "failed_repos":r.fetch.failures,
        "repo_candidates":r.repository_candidates,
        "plans":r.decisions,
        "readme_keyword_research":{
            a.repo_slug:(a.readme_analysis.sanitized_signal_hits
                if a.readme_analysis else None)
            for a in r.observed_repo_assessments
        },
        "rights_cleared":False,"installed_anything":r.software_installed,
        "executed_model":r.source_code_executed,
        "production_qualified":r.production_qualified,
        "youtube_content_inspected":r.youtube_video_watched,
    }
    (output/summary_name).write_text(
        json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
if __name__=="__main__":main()
