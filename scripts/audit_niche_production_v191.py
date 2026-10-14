from __future__ import annotations
"""Offline evidence inventory + niche production studies, no auto-execution."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from cinefactory.studio.production_tool_catalog_v191 import (
    NICHE_BLUEPRINTS,ProductionPortfolioAdvisor,
    candidate_catalog,host_inventory,
)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--niches",nargs="+",default=[
        "preschool_3d_musical","minecraft","long_slices_game",
        "asmr_sleep_hands_objects","audio_storytelling_seniors",
        "ai_family_drama","daily_english",
    ])
    a=ap.parse_args()
    target=ROOT/"data"/"verification"/"v191_production_council"
    target.mkdir(parents=True,exist_ok=True)
    inventory=host_inventory(ROOT)
    records=[x.model_dump(mode="json") for x in candidate_catalog(ROOT,inventory)]
    (target/"tool_inventory_v191.json").write_text(json.dumps({
        "status":"OBSERVED_TOOL_STATE_NOT_AUTOMATIC_PRODUCTION_READINESS",
        "host":inventory,"tool_candidates":records,
        "production_release_scope_verified":False,
    },indent=2),encoding="utf-8")
    advisor=ProductionPortfolioAdvisor(ROOT)
    summary={}
    for niche in a.niches:
        if niche not in NICHE_BLUEPRINTS:
            raise ValueError("UNKNOWN_NICHE:"+niche)
        # Single host inventory snapshot for consistency within this report.
        results=advisor.niche_report(niche)
        (target/(niche+"_plan.json")).write_text(
            json.dumps(results,indent=2,ensure_ascii=False),encoding="utf-8"
        )
        summary[niche]={
            "stages":len(results["stage_decisions"]),
            "unqualified_stages":results["unverified_stage_count"],
            "trial_options":{
                step["stage"]:step["selection"]["suggested_trial_method_id"]
                for step in results["stage_decisions"]
            },
            "production_authorized":results["production_authorized"],
        }
    (target/"niche_summary_v191.json").write_text(
        json.dumps(summary,indent=2),encoding="utf-8"
    )
    print(json.dumps({
        "status":"V191_OFFLINE_NICHE_STUDIES_PASS_BUT_NO_PRODUCTION_AUTHORIZED",
        "tool_candidates_count":len(records),
        "niche_blueprints_available":len(NICHE_BLUEPRINTS),
        "niches_studied":len(summary),
        "plans":summary,
        "evidence_path":str(target)
    },indent=2,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
