from __future__ import annotations
"""Materialize department-specific production research and codec experiment.

No internet, paid APIs, software installation, renderer or publication.
The encoder A/B actually produces local media artifacts and quality metrics.
"""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from cinefactory.studio.niche_research_conference_v192 import (
    DEPARTMENT_PLAYBOOK,OFFICIAL_SOURCE_SNAPSHOT,NicheResearchConference,
)
from cinefactory.studio.production_tool_catalog_v191 import NICHE_BLUEPRINTS
from cinefactory.studio.codec_ab_experiment_v192 import run_codec_experiment
from cinefactory.studio.external_tool_research_v192 import research_candidate_snapshot

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--skip-encode",action="store_true")
    ap.add_argument("--niches",nargs="+",default=sorted(NICHE_BLUEPRINTS))
    opts=ap.parse_args()
    out=ROOT/"data"/"verification"/"v192_department_research"
    out.mkdir(parents=True,exist_ok=True)
    capture={
        "status":"RESEARCH_SOPS_COMPILED_NOT_LIVE_AUTONOMOUS_WEB_RESEARCH",
        "source_status":"CURATED_OFFICIAL_REFERENCE_SNAPSHOT_NOT_SCOPE_CERTIFIED",
        "departments":{k:r.model_dump(mode="json")
                       for k,r in DEPARTMENT_PLAYBOOK.items()},
        "references":{k:r.model_dump(mode="json")
                      for k,r in OFFICIAL_SOURCE_SNAPSHOT.items()},
        "production_qualified":False,
        "ready_to_auto_execute":False,
    }
    (out/"department_playbook_v192.json").write_text(
        json.dumps(capture,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"external_tool_research_v192.json").write_text(
        json.dumps(research_candidate_snapshot(),indent=2),encoding="utf-8")
    room=NicheResearchConference(ROOT)
    research_index={}
    for niche in opts.niches:
        report=room.convene(niche,project_id="CINEFACTORY_STUDIO_RESEARCH")
        folder=out/"niche_research"
        folder.mkdir(parents=True,exist_ok=True)
        (folder/(niche+".json")).write_text(
            report.model_dump_json(indent=2),encoding="utf-8")
        research_index[niche]={
            "departments":len(report.department_reviews),
            "experiment_plans":len(report.experiments),
            "unqualified_stages":report.blocked_stages,
            "human_review_pending":not report.creative_quality_human_approved,
            "production_qualified":report.production_qualified,
            "source_refs":len(report.source_ledger),
        }
    (out/"niche_research_summary_v192.json").write_text(
        json.dumps(research_index,indent=2),encoding="utf-8")
    print("DEPARTMENT_RESEARCH_PASS",len(DEPARTMENT_PLAYBOOK),"roles",
          len(OFFICIAL_SOURCE_SNAPSHOT),"official refs",
          len(research_index),"niches",sum(x["experiment_plans"] for x in research_index.values()),
          "unexecuted A/B designs",flush=True)
    if not opts.skip_encode:
        source=ROOT/"data"/"verification"/"v185_alignment_reid"/"two_actors_speech_audible.mp4"
        if not source.is_file():raise FileNotFoundError(source)
        result=run_codec_experiment(
            source=source,output_dir=out/"codec_ab")
        assert result.status=="CODEC_AB_OBSERVED_NO_AUTOMATIC_PROMOTION"
        assert len(result.candidates)==3
    print("V192_RND_EVIDENCE",out,flush=True)

if __name__=="__main__":main()
