from __future__ import annotations
"""v1.6.33 verified learning handoff. No global rules from single experiment.

Existing ControlledExperiment and LearningPolicy do the causal/production
promotion checks. New evidence produces at most an EVALUATED candidate; it
never writes production code, changes registries, or publishes anything.
"""
from enum import StrEnum
from pathlib import Path
from typing import Literal
from pydantic import BaseModel,Field
from .contracts import KnowledgeScope
from .learning import ControlledExperiment,LearningPolicy,LearningRecord,LearningState


class ObservedResearchOutcome(BaseModel):
    experiment_id:str
    niche_id:str
    claim:str
    result_summary:str
    scope:Literal["SHOT","NICHE","STUDIO"]="NICHE"
    control:dict[str,str]
    challenger:dict[str,str]
    evidence_refs:list[str]=Field(default_factory=list)
    independent_review_passed:bool=False
    regression_passed:bool=False
    license_cleared:bool=False
    sample_project_ids:list[str]=Field(default_factory=list)
    confidence:float=Field(default=0.,ge=0.,le=1.)
    verified_metric_not_synthetic:bool=False
    causal_claim:bool=True


class LearningIntakeDecision(BaseModel):
    experiment_id:str
    state:Literal["RECORDED_UNVALIDATED","CANDIDATE_EVALUATED_NOT_PROMOTED"]
    candidate:LearningRecord
    learning_policy_eligible:bool=False
    ready_for_production_promotion:bool=False
    blockers:list[str]=Field(default_factory=list)


class ScientificLearningBridge:
    """Existing company LearningPolicy remains authority for studio learning.

    Run evidence checks before *proposing* learning; keep record immutable by
    default and do not invoke LearningStore.promote, irrespective of scores.
    """
    def prepare(self,observed:ObservedResearchOutcome)->LearningIntakeDecision:
        # Causal claims cannot change multiple variables; exception is safe.
        experiment=ControlledExperiment(
            experiment_id=observed.experiment_id,
            control=observed.control,variant=observed.challenger,
            causal_claim=observed.causal_claim,
            evidence=observed.evidence_refs,
        )
        blockers=[]
        if not observed.evidence_refs:blockers.append("OUTCOME_HAS_NO_ARTIFACT_EVIDENCE")
        if not observed.verified_metric_not_synthetic:
            blockers.append("OUTCOME_NOT_INDEPENDENTLY_MEASURED")
        if not observed.independent_review_passed:
            blockers.append("INDEPENDENT_BLIND_REVIEW_MISSING")
        if not observed.regression_passed:
            blockers.append("REGRESSION_NOT_PASSED")
        if not observed.license_cleared:
            blockers.append("LICENSE_NOT_CLEARED")
        if observed.scope=="STUDIO" and len(set(observed.sample_project_ids))<3:
            blockers.append("UNPROVEN_STUDIO_WIDE_GENERALIZATION")
        if observed.confidence<.8:blockers.append("LOW_CANDIDATE_CONFIDENCE")
        candidate_state=LearningState.EVALUATED if not blockers else LearningState.CANDIDATE
        knowledge=KnowledgeScope.STUDIO if observed.scope=="STUDIO" else KnowledgeScope.PROJECT
        item=LearningRecord(
            scope=knowledge,state=candidate_state,
            subject=observed.niche_id+":"+observed.experiment_id,
            observation=observed.result_summary,
            hypothesis=observed.claim,
            evidence=observed.evidence_refs,
            experiment=experiment.model_dump(mode="json"),
            result={"original_scope":observed.scope,"license_cleared":observed.license_cleared,
                    "independent_review_passed":observed.independent_review_passed,
                    "regression_passed":observed.regression_passed,
                    "verified_metric_not_synthetic":observed.verified_metric_not_synthetic},
            confidence=observed.confidence,
            source_project_ids=sorted(set(observed.sample_project_ids)),
        )
        if not blockers:
            passed,findings=LearningPolicy.can_promote(item)
            if not passed:blockers.extend(findings)
        return LearningIntakeDecision(
            experiment_id=observed.experiment_id,
            state="RECORDED_UNVALIDATED" if blockers else "CANDIDATE_EVALUATED_NOT_PROMOTED",
            candidate=item,
            learning_policy_eligible=not blockers,
            ready_for_production_promotion=False,
            blockers=sorted(set(blockers)),
        )
