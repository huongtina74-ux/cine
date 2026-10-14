from __future__ import annotations
"""v1.6.34: actual read-only GitHub research -> v193 critical reasoning loop.

Discovered metadata is supplier evidence of repository existence, not measured
VRAM, licence, artistic quality, cost or readiness. The report and source
snapshots are inert data for a future, separately authorized research agent.
"""
import json
from datetime import date
from pathlib import Path
from typing import Literal
from pydantic import BaseModel,Field

from .evidence_reasoning_v193 import (
    CitedResearchSource,ClaimObservation,ClaimDimension,
    ClaimFinding,SourceKind,
)
from .github_research_adapter_v194 import (
    PublicGitHubResearchAdapter, ResearchFetchPolicy,
    RepoSourceSnapshot,ResearchFetchOutcome,NICHE_REPOSITORY_BLUEPRINT,
)
from .reasoning_agent_bridge_v193 import ReasoningAgentBridge
from .strategic_reasoning_v193 import (
    DecisionReasoningReport,StrategicResearchReasoner,ReasoningRequest,
)




class ReadmeResearchSignals(BaseModel):
    repo_slug:str
    readme_sha256:str
    sanitized_signal_hits:dict[str,int]
    scanned_lines:int
    inspected_readme_content:bool=True
    feature_verified_in_executable:bool=False
    source_text_must_never_execute:bool=True
    candidate_workflow_qualified:bool=False


_SUGGESTION_VOCABULARY={
    "workflow":("workflow","node graph","pipeline"),
    "video":("video","animation","render"),
    "audio_music":("midi","music","audio","sound"),
    "physics":("physics","rigid body","collision","2d","3d"),
    "api_automation":("api","command line","python"),
    "commercial_license":("license","licence","commercial"),
}
class RepoResearchAssessment(BaseModel):
    repo_slug:str
    source_id:str
    niche_ids:list[str]
    capability_claim_type:Literal["MAINTAINER_REPOSITORY_EXISTS_ONLY"]="MAINTAINER_REPOSITORY_EXISTS_ONLY"
    observed_license_spdx:str|None
    observed_archived:bool
    verified_snapshot_sha256:str
    README_is_untrusted_source_material:bool=True
    vendor_feature_claims_not_benchmark_verified:bool=True
    exact_weight_license_unverified:bool=True
    no_execution_proof:bool=True
    actionable_next_steps:list[str]
    readme_analysis:ReadmeResearchSignals|None=None
    rights_status:Literal["LICENSE_REVIEW_REQUIRED"]="LICENSE_REVIEW_REQUIRED"


class AutonomousResearchCycleResult(BaseModel):
    status:Literal["SOURCE_RESEARCH_COMPLETE_PRODUCTION_BLOCKED",
                   "OFFLINE_RESEARCH_QUEUED",
                   "PARTIAL_SOURCE_RESEARCH_PRODUCTION_BLOCKED"]
    network_read_authorized:bool
    repository_candidates:list[str]
    fetch:ResearchFetchOutcome
    observed_repo_assessments:list[RepoResearchAssessment]
    source_ids:list[str]
    saved_reports:dict[str,str]
    decisions:dict[str,str]
    production_qualified:bool=False
    external_llm_was_invoked:bool=False
    youtube_video_watched:bool=False
    paid_apis_invoked:bool=False
    source_code_executed:bool=False
    software_installed:bool=False
    estimated_or_measured_creative_quality:bool=False
    blockers:list[str]=Field(default_factory=list)


class AutonomousSourceResearchOrchestrator:
    def __init__(self,root:Path,*,policy:ResearchFetchPolicy|None=None):
        self.root=Path(root).resolve()
        self.policy=policy or ResearchFetchPolicy()
        self.output=self.root/"data"/"verification"/"v194_autonomous_research"
        self.adapter=PublicGitHubResearchAdapter(self.output/"github",self.policy)
        self.brain=StrategicResearchReasoner(self.root)
        self.bridge=ReasoningAgentBridge()

    def _analyze_readme(self,s:RepoSourceSnapshot)->ReadmeResearchSignals|None:
        if not s.readme_snapshot_file or not s.readme_sha256:
            return None
        if not self.adapter.validate_snapshot(s):
            raise ValueError("READ_ME_BEFORE_VERIFYING_SHA_FORBIDDEN")
        f=Path(s.readme_snapshot_file)
        raw=f.read_text(encoding="utf-8",errors="replace")
        # Does not execute embedded commands or let prose authorize production.
        lines=raw.lower().splitlines()[:2200]
        hits={name:sum(any(word in ln for word in words) for ln in lines)
              for name,words in _SUGGESTION_VOCABULARY.items()}
        return ReadmeResearchSignals(
            repo_slug=s.repo_slug,readme_sha256=s.readme_sha256,
            sanitized_signal_hits=hits,scanned_lines=len(lines),
        )

    def _repo_sources(self,snapshots:list[RepoSourceSnapshot])->list[CitedResearchSource]:
        records=[]
        for s in snapshots:
            if not self.adapter.validate_snapshot(s):
                raise ValueError("SNAPSHOT_INTEGRITY_NOT_VERIFIED:"+s.repo_slug)
            records.append(CitedResearchSource(
                source_id="GH_"+s.repo_slug.replace("/","__").replace("-","_").replace(".","_"),
                kind=SourceKind.MAINTAINER_REPOSITORY,
                locator=s.repo_url,
                publisher_or_owner=s.repo_slug.split("/")[0],
                observed_on=date.fromisoformat(s.fetched_at_utc[:10]),
                source_sha256=s.metadata_sha256,
                scope="PUBLIC_GITHUB_REPOSITORY_METADATA_ONLY",
                retrieved_and_inspected=True,
                independently_verified=False,
                license_approved_for_commercial_use=False,
            ))
        return records

    def _claims(self,repo_sources:list[CitedResearchSource],
                snapshots:list[RepoSourceSnapshot],
                niche:str)->list[ClaimObservation]:
        claims=[]
        lookup={s.source_id:s for s in repo_sources}
        for s in snapshots:
            sid="GH_"+s.repo_slug.replace("/","__").replace("-","_").replace(".","_")
            if sid not in lookup:
                raise RuntimeError("MISSING_REPOSITORY_SOURCE")
            question="GitHub public metadata reports a non-archived repository for "+s.repo_slug
            claims.append(ClaimObservation(
                claim_id="REPO_STATUS_"+niche+"_"+sid,
                subject_method_id="candidate_repo:"+s.repo_slug,
                niche_id=niche,stage=self._stage_for_niche(niche),
                dimension=ClaimDimension.FUNCTIONALITY,
                finding=ClaimFinding.CONTRADICTS if s.observed_archived or s.observed_disabled else ClaimFinding.SUPPORTS,
                source_ids=[sid],
                description=("Repository metadata present; observed archived="+str(s.observed_archived)
                             +"; licence SPDX="+str(s.observed_license_spdx)
                             +". No runtime/video/AI model output tested."),
                exact_scoped_question=question,observed_scope=question,
                direct_empirical_measurement=False,
            ))
        return claims

    @staticmethod
    def _stage_for_niche(niche:str):
        from .production_selection_council import Stage
        if niche=="preschool_3d_musical":return Stage.MUSIC
        if niche=="long_slices_game":return Stage.GAME_RUNTIME
        if niche in {"ai_family_drama"}:return Stage.AI_VIDEO
        if niche in {"2d_cartoon","daily_english"}:return Stage.GRAPHICS_2D
        if niche in {"audio_storytelling_seniors","rain_sleep_white_noise"}:return Stage.AUDIO_POST
        return Stage.ANIMATION

    def research(self,niches:list[str],*,include_readme:bool=True)->AutonomousResearchCycleResult:
        if not niches or len(niches)>4 or len(niches)!=len(set(niches)):
            raise ValueError("INVALID_NICHE_BATCH")
        for niche in niches:
            if niche not in NICHE_REPOSITORY_BLUEPRINT:
                raise ValueError("UNKNOWN_NICHE_NEEDS_RESEARCH_CONFERENCE_FIRST")
        # Fair round-robin ensures a scarce call budget covers every niche
        # before adding the second candidate of any niche.
        max_repos=min(self.policy.max_repos,self.policy.max_calls//(2 if include_readme else 1))
        if not max_repos:
            raise RuntimeError("NOT_ENOUGH_NETWORK_RESEARCH_BUDGET")
        plans={niche:NICHE_REPOSITORY_BLUEPRINT[niche] for niche in niches}
        slugs=[]
        for rank in range(max(len(x) for x in plans.values())):
            for niche in niches:
                if rank<len(plans[niche]) and plans[niche][rank] not in slugs:
                    slugs.append(plans[niche][rank])
                if len(slugs)>=max_repos:break
            if len(slugs)>=max_repos:break
        fetch=self.adapter.scan(slugs,include_readme=include_readme)
        source_list=self._repo_sources(fetch.fetched)
        assessments=[]
        for s in fetch.fetched:
            sourceid="GH_"+s.repo_slug.replace("/","__").replace("-","_").replace(".","_")
            assessments.append(RepoResearchAssessment(
                repo_slug=s.repo_slug,source_id=sourceid,
                niche_ids=[n for n in niches if s.repo_slug in plans[n]],
                observed_license_spdx=s.observed_license_spdx,
                observed_archived=s.observed_archived,
                verified_snapshot_sha256=s.metadata_sha256,
                readme_analysis=self._analyze_readme(s),
                actionable_next_steps=[
                    "REVIEW_EXACT_REPOSITORY_AND_MODEL_WEIGHTS_LICENSE",
                    "FIND_AND_QUALIFY_INSTALLED_EXECUTABLE_AND_REQUIRED_ADAPTER",
                    "RENDER_REPRESENTATIVE_ORIGINAL_SAMPLE_ON_ACTUAL_GPU",
                    "MEASURE_QUALITY_COST_SPEED_VRAM_AND_HUMAN_REVIEW",
                ],
            ))
        if self.policy.enable_public_https_network:
            self.output.mkdir(parents=True,exist_ok=True)
        saved={}
        decisions={}
        for niche in niches:
            selected=[s for s in fetch.fetched if s.repo_slug in plans[niche]]
            rel_source=[s for s in source_list if s.source_id in {
                "GH_"+r.repo_slug.replace("/","__").replace("-","_").replace(".","_")
                for r in selected
            }]
            claims=self._claims(rel_source,selected,niche)
            report=self.brain.deliberate(
                ReasoningRequest(
                    project_id="REAL_SOURCE_DISCOVERY_V194_"+niche,
                    niche_id=niche,source_rights_cleared=False,
                    made_for_kids=niche=="preschool_3d_musical",
                    max_research_tasks=9,
                    max_paid_api_usd=0,
                ),sources=rel_source,claims=claims,
            )
            decisions[niche]=report.status
            if self.policy.enable_public_https_network:
                f=self.output/"plans"/(niche+"_live_source_research.json")
                f.parent.mkdir(parents=True,exist_ok=True)
                f.write_text(report.model_dump_json(indent=2),encoding="utf-8")
                saved[niche]=str(f.resolve())
                if report.experiment_priority_queue:
                    packet=self.bridge.make_packet(
                        report,rel_source,
                        project_brief="Compare licensed tools and approved workflows to produce ORIGINAL "+niche+" video with max 12GB GPU. Repository metadata alone cannot certify media quality.")
                    packet_path=self.output/"agent_packets"/(niche+"_research_packet.json")
                    packet_path.parent.mkdir(parents=True,exist_ok=True)
                    packet_path.write_text(packet.model_dump_json(indent=2),encoding="utf-8")
                    saved[niche+":agent_packet"]=str(packet_path.resolve())
        if not self.policy.enable_public_https_network:
            status="OFFLINE_RESEARCH_QUEUED"
        elif fetch.failures or len(fetch.fetched)<len(slugs):
            status="PARTIAL_SOURCE_RESEARCH_PRODUCTION_BLOCKED"
        else:status="SOURCE_RESEARCH_COMPLETE_PRODUCTION_BLOCKED"
        return AutonomousResearchCycleResult(
            status=status,network_read_authorized=self.policy.enable_public_https_network,
            repository_candidates=slugs,fetch=fetch,
            observed_repo_assessments=assessments,
            source_ids=[s.source_id for s in source_list],
            saved_reports=saved,decisions=decisions,
            blockers=[
                "SOURCE_METADATA_IS_NOT_ARTISTIC_QUALITY_OR_HARDWARE_BENCHMARK",
                "MUST_REVIEW_EACH_REPO_AND_WEIGHTS_COMMERCIAL_LICENSE",
                "NO_YOUTUBE_VIDEO_CONTENT_HAS_BEEN_INSPECTED_IN_THIS_CYCLE",
                "SAME_SHOT_MULTI_ENGINE_MEDIA_AB_HUMAN_QC_PENDING",
                "EXTERNAL_REASONING_MODEL_NOT_CONNECTED_TO_AUTORUN",
                "RESEARCH_ONLY_NO_PRODUCTION_EXECUTION",
            ],
        )
