from __future__ import annotations
"""CineFactory v1.6.33 — bounded multi-perspective R&D decision cycle.

The reasoning cycle derives falsifiable hypotheses, adversarial objections,
experiment priorities and R&D handoffs from actual claim evidence. It does NOT
use a remote LLM, claim human-like thinking, touch a paid API, install or
execute external tools. Its outputs are research suggestions, not permissions.
"""
from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Literal
from pydantic import BaseModel,Field

from .evidence_reasoning_v193 import (
    CitedResearchSource,ClaimObservation,ClaimVerdict,ClaimDimension,
    ReviewerPerspective,AdversarialChallenge,EvidenceAuditor,adversarial_review,
)
from .niche_research_conference_v192 import NicheResearchConference
from .production_selection_council import Stage
from .production_tool_catalog_v191 import NICHE_BLUEPRINTS


class TaskType(StrEnum):
    RESOLVE_CONFLICT="RESOLVE_CONFLICT"
    MEASURE_PERFORMANCE="MEASURE_PERFORMANCE"
    VERIFY_LICENSE="VERIFY_LICENSE"
    HUMAN_CREATIVE_REVIEW="HUMAN_CREATIVE_REVIEW"
    TEST_UNKNOWN_METHOD="TEST_UNKNOWN_METHOD"
    INVENTORY_CAPABILITIES="INVENTORY_CAPABILITIES"
    DISCOVER_NEW_NICHE="DISCOVER_NEW_NICHE"


class ReasoningRequest(BaseModel):
    project_id:str
    niche_id:str
    project_brief:str = ""
    script_text:str = ""
    reference_video_urls:list[str] = Field(default_factory=list)
    source_rights_cleared:bool = False
    made_for_kids:bool = False
    max_vram_gb:float = Field(default=12.,gt=0.)
    max_research_tasks:int = Field(default=8,ge=1,le=40)
    max_paid_api_usd:float = Field(default=0.,ge=0.)
    budget_usd_for_experiments:float|None=Field(default=None,ge=0.)
    daily_gpu_minutes_budget:float|None=Field(default=None,ge=0.)
    human_review_available:bool = False


class ReasoningTask(BaseModel):
    task_id:str
    kind:TaskType
    owner_department:str
    stage:Stage
    question:str
    competing_hypotheses:list[str] = Field(min_length=2)
    experiment_design:str
    requested_artifacts:list[str] = Field(min_length=1)
    expected_information_gain: Literal["HIGH","MEDIUM","UNKNOWN"]
    heuristic_priority:int = Field(ge=0,le=100)
    source_verdict_ids:list[str] = Field(default_factory=list)
    requires_human:bool = False
    requires_explicit_paid_api_approval:bool = False
    estimated_gpu_minutes:float|None = Field(default=None,ge=0.)
    measured_cost_usd:float|None = Field(default=None,ge=0.)
    budget_proven_feasible:bool = False
    execution_authorized:bool = False
    reviewed:bool = False
    production_eligible:bool = False


class DecisionReasoningReport(BaseModel):
    schema_version:str = "v1.6.33"
    project_id:str
    niche_id:str
    status:Literal["RND_PLAN_AVAILABLE","UNKNOWN_NICHE_REQUIRES_DISCOVERY"]
    experimental_claim_verdicts:list[ClaimVerdict]
    specialists:list[AdversarialChallenge]
    experiment_priority_queue:list[ReasoningTask]
    postponed_task_ids:list[str]
    niche_stage_blockers:list[str]
    required_human_signoffs:list[str]
    uncertainty_register:list[str]
    decision_notices:list[str]
    final_production_method:str|None=None
    production_qualified:bool = False
    active_model_reasoner_connected:bool = False
    live_internet_research_performed:bool = False
    last_authority_gate_passed:bool = False


class StrategicResearchReasoner:
    """One deterministic, auditable iteration of Generate -> Critique -> Test.

    Deterministic heuristics are used for prioritizing future experiments.
    Scores are NOT empirical model confidence or money/time estimates. As
    much as possible reuse niche R&D, SourceEvidence and LearningPolicy.
    """
    def __init__(self,root:str|Path,*,today:date|None=None):
        self.root=Path(root).resolve()
        self.today=today or date.today()
        self.auditor=EvidenceAuditor(today=self.today,verified_artifact_root=self.root)
        self.research=NicheResearchConference(self.root)

    @staticmethod
    def _task(id,kind,owner,stage,question,hypotheses,design,artifacts,
              priority,refs=None,requires_human=False,gain="HIGH"):
        return ReasoningTask(
            task_id=id,kind=kind,owner_department=owner,stage=stage,
            question=question,competing_hypotheses=hypotheses,
            experiment_design=design,requested_artifacts=artifacts,
            expected_information_gain=gain,heuristic_priority=priority,
            source_verdict_ids=refs or [],requires_human=requires_human,
        )

    def deliberate(self,request:ReasoningRequest,*,
                   sources:list[CitedResearchSource]|None=None,
                   claims:list[ClaimObservation]|None=None)->DecisionReasoningReport:
        sources=sources or []
        claims=claims or []
        permitted_niche=set(NICHE_BLUEPRINTS)
        if any(c.niche_id!=request.niche_id for c in claims):
            raise ValueError("CROSS_NICHE_CLAIMS_CANNOT_BE_SILENTLY_REUSED")
        verdicts=self.auditor.audit(sources,claims)
        unknown=request.niche_id not in permitted_niche
        if not unknown:
            stage_report=self.research.convene(
                request.niche_id,project_id=request.project_id,
                context={
                    "project_brief":request.project_brief,
                    "script_text":request.script_text,
                    "reference_video_urls":request.reference_video_urls,
                    "source_media_rights_confirmed":request.source_rights_cleared,
                    "allow_external_api_cost":request.max_paid_api_usd>0,
                },
            )
            stages=stage_report.blocked_stages
            is_kids=NICHE_BLUEPRINTS[request.niche_id].children_audience
        else:
            stage_report=None
            stages=["RESEARCH"]
            is_kids=request.made_for_kids
        critics=adversarial_review(
            is_child_content=is_kids,stage=Stage.RESEARCH,
            verdicts=verdicts,
            benchmark_measured=any(c.direct_empirical_measurement for c in claims),
            input_rights_confirmed=request.source_rights_cleared,
        )
        tasks=[]
        for v in verdicts:
            ref=v.contributing_claim_ids
            if v.status=="CONFLICT_REQUIRES_TEST":
                tasks.append(self._task(
                    "CONFLICT_"+v.subject_method_id+"_"+v.dimension.value,
                    TaskType.RESOLVE_CONFLICT,"rnd_security",v.stage,
                    "Which conflicting claim survives the exact scoped controlled trial?",
                    ["H1: method meets the stated scoped requirement",
                     "H2: version/hardware/data provenance invalidates the first claim"],
                    "Hold source assets, versions, renderer, GPU and fixed seed; perform counterbalanced A/B with separate QA",
                    ["source snapshots","sealed benchmark report","negative controls",
                     "same-input media output"],100,ref))
            elif v.status=="STALE_REQUIRES_REFRESH":
                tasks.append(self._task(
                    "REFRESH_"+v.subject_method_id+"_"+v.dimension.value,
                    TaskType.VERIFY_LICENSE if v.dimension==ClaimDimension.COMMERCIAL_RIGHTS else TaskType.INVENTORY_CAPABILITIES,
                    "rnd_security",v.stage,"Has the vendor changed the exact-version claim?",
                    ["H1: old claim still applies","H2: newer documentation supersedes it"],
                    "Fetch new official source and snapshot SHA; compare exact version and scope",
                    ["dated vendor source","source hash","human rights review if license"],91,ref))
            elif v.status in {"INSUFFICIENT_EVIDENCE","CONTRADICTED_WITH_SCOPE_LIMITS"}:
                needs_license=v.dimension==ClaimDimension.COMMERCIAL_RIGHTS
                tasks.append(self._task(
                    "PROVE_"+v.subject_method_id+"_"+v.dimension.value,
                    TaskType.VERIFY_LICENSE if needs_license else TaskType.MEASURE_PERFORMANCE,
                    "rnd_security",v.stage,
                    "Can the proposed method satisfy the requested outcome?",
                    ["H1: correct model and workflow meet the quality floor",
                     "H2: method is missing a required capability or licence"],
                    "Create a paired reference shot and inspect official exact-version licence before any external execution",
                    ["versioned model card","benchmarked sample","rights ledger"],89 if needs_license else 83,ref,
                    requires_human=needs_license))
            elif v.status=="SUPPORTED_WITH_SCOPE_LIMITS":
                tasks.append(self._task(
                    "GENERALIZE_"+v.subject_method_id+"_"+v.dimension.value,
                    TaskType.TEST_UNKNOWN_METHOD,"qa_compliance",v.stage,
                    "Does supported evidence generalize beyond the original narrow scene?",
                    ["H1: multiple independent projects retain quality",
                     "H2: result overfits the tested scene"],
                    "Hold out a second project and different camera/lighting; compare blind reviewer outcomes",
                    ["second-project preview","cross-domain report","reviewer notes"],74,ref,
                    requires_human=True,gain="MEDIUM"))
        if unknown:
            tasks.extend([
                self._task(
                    "NEW_NICHE_FORMAT_DNA",TaskType.DISCOVER_NEW_NICHE,
                    "audience_research",Stage.RESEARCH,
                    "What visual/audio/retention grammar makes this unfamiliar niche distinctive?",
                    ["H1: existing studio adapters cover enough production scope",
                     "H2: new department/capability is required"],
                    "Research 3 legally referenceable original/competitor examples at abstract feature level; document sources, audience and risks",
                    ["research source ledger","niche opportunity hypothesis",
                     "copyright-safe format DNA"],96),
                self._task(
                    "NEW_NICHE_PRODUCTION_TECH",TaskType.INVENTORY_CAPABILITIES,
                    "rnd_security",Stage.RESEARCH,
                    "What actual media pipeline and new capabilities are needed?",
                    ["H1: existing fully evidenced local tool chain suffices",
                     "H2: qualified external tool or bespoke engine integration is needed"],
                    "Extract shot needs; compare official software/manual/repo model cards and local inventory",
                    ["candidate matrix","hardware fit","scope-specific missing capabilities"],90),
            ])
        else:
            for i,stage in enumerate(stage_report.stage_decisions):
                choice=stage["selection"]
                st=Stage(stage["stage"])
                if choice["status"]=="PRODUCTION_METHOD_SELECTED":
                    continue
                reviews=choice["reviews"]
                available=[x["method_id"] for x in reviews if x["preview_candidate"]]
                title=",".join(stage["capabilities"])
                tasks.append(self._task(
                    "STAGE_"+st.value+"_"+str(i),
                    TaskType.MEASURE_PERFORMANCE if available else TaskType.INVENTORY_CAPABILITIES,
                    "rnd_security",st,
                    "What can produce "+title+" reliably with minimal accepted-minute cost?",
                    ["H1: available local candidates can be qualified after measurement",
                     "H2: no current tool meets creative/technical/licensing requirements"],
                    "Match the same 15–30s original shot to a reference; measure quality, VRAM, time, retries, human effort and independent licence status",
                    ["golden shot contract","2 candidate outputs if possible",
                     "human review","accepted-minute cost ledger"],
                    79 if is_kids and st in (Stage.MUSIC,Stage.VOICE,Stage.CHARACTER_RIG,Stage.FINAL_QC) else 65,
                    requires_human=is_kids and st in (Stage.MUSIC,Stage.VOICE,Stage.CHARACTER_RIG,Stage.FINAL_QC),
                    gain="HIGH" if not available else "MEDIUM"))
        if is_kids:
            tasks.append(self._task(
                "PRESCHOOL_CREATIVITY_AND_SAFETY",TaskType.HUMAN_CREATIVE_REVIEW,
                "curriculum_child_safety",Stage.FINAL_QC,
                "Are lessons, choreography, original composition and child safety expert-approved?",
                ["H1: story teaches intended age-appropriate material safely",
                 "H2: scene is confusing, overly derivative or unsafe for young children"],
                "Review original character bible, scores, music stems, scripts, storyboards and child-safety constraints",
                ["expert reviewer signoff","curriculum correction log","music rights proof"],99,requires_human=True))
        if not request.source_rights_cleared:
            tasks.append(self._task(
                "ORIGINAL_RIGHTS_LEDGER",TaskType.VERIFY_LICENSE,
                "qa_compliance",Stage.RESEARCH,
                "Do supplied video, voice, model, music and character assets have proper usage rights?",
                ["H1: all first-party/licensed assets can be documented",
                 "H2: unknown ownership prevents legal deployment"],
                "Audit source references and each underlying model/weight/song/performer authorization",
                ["rights ledger","license reviewer findings"],98,requires_human=True))
        # Deduplicate by deterministic stable IDs; max tasks is a hard research
        # queue cap, not a success criterion or total-money-cost cap.
        tasks.sort(key=lambda t:(-t.heuristic_priority,t.task_id))
        seen=set()
        tasks=[x for x in tasks if not (x.task_id in seen or seen.add(x.task_id))]
        selected=tasks[:request.max_research_tasks]
        postponed=[x.task_id for x in tasks[request.max_research_tasks:]]
        uncertain=[
            "QUALITY_ARTISTIC_JUDGEMENT_PENDING",
            "TRUE_ACCEPTED_MINUTE_COST_UNKNOWN",
            "LOCAL_EXECUTABLE_VIDEO_MODEL_QUALIFICATION_PENDING",
        ]
        if unknown:uncertain.append("NICHE_PRODUCTION_FORMAT_NOT_YET_RESEARCHED")
        if any(v.status=="CONFLICT_REQUIRES_TEST" for v in verdicts):
            uncertain.append("CONTRADICTORY_EVIDENCE_NOT_RESOLVED")
        if request.reference_video_urls:
            uncertain.append("USER_LINKS_NOT_AUTOMATICALLY_VIEWED_OR_DOWNLOADED")
        if is_kids:uncertain.append("EARLY_CHILDHOOD_EXPERT_AND_SONG_RIGHTS_REQUIRED")
        reasons=[
            "ADVISORY_DELIBERATION_ONLY_NO_RUNTIME_EXECUTION",
            "TASK_PRIORITY_IS_HEURISTIC_NOT_EMPIRICAL_PROBABILITY_OR_DOLLAR_VALUE",
            "EVIDENCE_CONFLICT_REQUIRES_INDEPENDENT_REPRODUCTION",
            "NO_PAID_API_OR_BACKGROUND_RESEARCH_TRIGGERED",
            "NO_UNREVIEWED_LEARNING_RULE_PROMOTION",
        ]
        if request.daily_gpu_minutes_budget is not None:
            reasons.append("GPU_MINUTES_BUDGET_UNENFORCEABLE_UNTIL_MEASURED_ESTIMATES_EXIST")
        if request.budget_usd_for_experiments is not None:
            reasons.append("DOLLAR_BUDGET_IS_HARD_LIMIT_FOR_FUTURE_EXECUTOR_NOT_THIS_RESEARCH_PLANNER")
        return DecisionReasoningReport(
            project_id=request.project_id,niche_id=request.niche_id,
            status="UNKNOWN_NICHE_REQUIRES_DISCOVERY" if unknown else "RND_PLAN_AVAILABLE",
            experimental_claim_verdicts=verdicts,specialists=critics,
            experiment_priority_queue=selected,postponed_task_ids=postponed,
            niche_stage_blockers=stages,
            required_human_signoffs=sorted({
                x.concern for x in critics if x.reviewer in {
                    ReviewerPerspective.COMPLIANCE_COUNSEL,
                    ReviewerPerspective.EDUCATION_CHILD_SAFETY,
                    ReviewerPerspective.CREATIVE_DIRECTOR,
                }
            }),
            uncertainty_register=uncertain,decision_notices=reasons,
        )
