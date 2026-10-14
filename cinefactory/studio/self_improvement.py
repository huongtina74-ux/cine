from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from .contracts import DepartmentId, KnowledgeScope, LearningCandidate, SkillManifest
from .knowledge import KnowledgeItem, KnowledgeKind, SourceTier, SkillCompiler
from .problem_solving import RootCauseEngine
from .rnd import ExternalToolCandidate, ExternalToolIntake


class ResearchActionKind(StrEnum):
    READ_OFFICIAL_DOCS = "READ_OFFICIAL_DOCS"
    READ_OFFICIAL_SDK = "READ_OFFICIAL_SDK"
    SEARCH_MAINTAINER_REPO = "SEARCH_MAINTAINER_REPO"
    READ_BOOK_OR_GUIDE = "READ_BOOK_OR_GUIDE"
    BUILD_MINIMAL_REPRO = "BUILD_MINIMAL_REPRO"
    RUN_SANDBOX_EXPERIMENT = "RUN_SANDBOX_EXPERIMENT"
    BENCHMARK = "BENCHMARK"
    ADD_REGRESSION = "ADD_REGRESSION"


class ResearchAction(BaseModel):
    kind: ResearchActionKind
    query: str
    priority: int = Field(default=50, ge=0, le=100)
    expected_artifact: str


class ImprovementPlan(BaseModel):
    problem_code: str
    owner: DepartmentId
    known_problem: bool = False
    research_actions: list[ResearchAction] = Field(default_factory=list)
    candidate_skill_id: str | None = None
    production_change_allowed: bool = False
    reasons: list[str] = Field(default_factory=list)
class SelfImprovementPlanner:
    """Turns unknown failures into controlled research and experiments, not immediate self-modification."""

    SOURCE_ORDER = [
        ResearchActionKind.READ_OFFICIAL_DOCS,
        ResearchActionKind.READ_OFFICIAL_SDK,
        ResearchActionKind.SEARCH_MAINTAINER_REPO,
        ResearchActionKind.READ_BOOK_OR_GUIDE,
    ]

    def __init__(self, root_causes: RootCauseEngine | None = None) -> None:
        self.root_causes = root_causes or RootCauseEngine()

    def plan(
        self,
        problem_code: str,
        symptoms: list[str],
        owner: DepartmentId,
        *,
        tool_id: str | None = None,
    ) -> ImprovementPlan:
        record = self.root_causes.hypotheses(problem_code, symptoms, owner=owner)
        unknown = all(h.cause == "unknown_root_cause" for h in record.hypotheses)
        actions: list[ResearchAction] = []

        if unknown:
            actions.append(
                ResearchAction(
                    kind=ResearchActionKind.BUILD_MINIMAL_REPRO,
                    query=f"Create the smallest reproducible case for {problem_code}: {symptoms}",
                    priority=100,
                    expected_artifact="minimal_reproduction",
                )
            )
            subject = tool_id or owner.value.lower()
            for offset, kind in enumerate(self.SOURCE_ORDER):
                actions.append(
                    ResearchAction(
                        kind=kind,
                        query=f"{subject} {problem_code} {' '.join(symptoms)}",
                        priority=90 - offset * 10,
                        expected_artifact="knowledge_candidates",
                    )
                )
        else:
            for hyp in record.hypotheses:
                actions.append(
                    ResearchAction(
                        kind=ResearchActionKind.RUN_SANDBOX_EXPERIMENT,
                        query=f"{hyp.test}; expected: {hyp.expected_result}",
                        priority=int(60 + hyp.confidence * 40),
                        expected_artifact=f"experiment_{hyp.hypothesis_id}",
                    )
                )

        actions.extend([
            ResearchAction(
                kind=ResearchActionKind.BENCHMARK,
                query=f"Benchmark candidate repair for {problem_code}",
                priority=70,
                expected_artifact="benchmark_report",
            ),
            ResearchAction(
                kind=ResearchActionKind.ADD_REGRESSION,
                query=f"Create a deterministic regression for {problem_code}",
                priority=80,
                expected_artifact="regression_test",
            ),
        ])
        return ImprovementPlan(
            problem_code=problem_code,
            owner=owner,
            known_problem=not unknown,
            research_actions=actions,
            candidate_skill_id=f"repair.{problem_code.lower()}",
            production_change_allowed=False,
            reasons=["research and sandbox required before production promotion"],
        )
class LearningPromotionBoard:
    """Separates learning evidence from production promotion."""

    def review_learning(self, candidate: LearningCandidate) -> tuple[bool, list[str]]:
        findings: list[str] = []
        if not candidate.sandbox_passed:
            findings.append("SANDBOX_NOT_PASSED")
        if not candidate.regression_passed:
            findings.append("REGRESSION_NOT_PASSED")
        if candidate.scope is KnowledgeScope.STUDIO and len(candidate.evidence_refs) < 2:
            findings.append("STUDIO_SCOPE_REQUIRES_MULTIPLE_EVIDENCE_REFS")
        return not findings, findings

    def promote_learning(self, candidate: LearningCandidate) -> LearningCandidate:
        passed, findings = self.review_learning(candidate)
        if not passed:
            raise ValueError(";".join(findings))
        return candidate.model_copy(update={"promoted": True})


class KnowledgeToSkillPipeline:
    def __init__(self) -> None:
        self.compiler = SkillCompiler()

    def compile(
        self,
        *,
        skill_id: str,
        version: str,
        owner: DepartmentId,
        craft_domain: str,
        knowledge: list[KnowledgeItem],
        tool_binding: str | None = None,
        commercial_safe: bool | None = None,
        security_reviewed: bool = False,
    ) -> SkillManifest:
        return self.compiler.compile_candidate(
            skill_id=skill_id,
            version=version,
            owner=owner,
            craft_domain=craft_domain,
            knowledge=knowledge,
            tool_binding=tool_binding,
            commercial_safe=commercial_safe,
            security_reviewed=security_reviewed,
        )
