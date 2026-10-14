from __future__ import annotations

import pytest

from cinefactory.studio.contracts import DepartmentId, KnowledgeScope, LearningCandidate
from cinefactory.studio.self_improvement import (
    LearningPromotionBoard,
    ResearchActionKind,
    SelfImprovementPlanner,
)


def test_unknown_problem_starts_with_minimal_repro_and_research():
    plan = SelfImprovementPlanner().plan(
        "NEW_TOOL_FAILURE",
        ["unexpected unknown failure"],
        DepartmentId.RND,
        tool_id="premiere",
    )
    assert plan.production_change_allowed is False
    kinds = [x.kind for x in plan.research_actions]
    assert ResearchActionKind.BUILD_MINIMAL_REPRO in kinds
    assert ResearchActionKind.READ_OFFICIAL_DOCS in kinds
    assert ResearchActionKind.ADD_REGRESSION in kinds


def test_known_problem_generates_sandbox_experiments():
    plan = SelfImprovementPlanner().plan(
        "ANIM_FOOT",
        ["character has foot sliding"],
        DepartmentId.PERFORMANCE,
        tool_id="blender",
    )
    assert plan.known_problem is True
    assert any(x.kind is ResearchActionKind.RUN_SANDBOX_EXPERIMENT for x in plan.research_actions)


def test_studio_learning_requires_multiple_evidence_refs():
    board = LearningPromotionBoard()
    candidate = LearningCandidate(
        observation="a technique worked",
        hypothesis="may improve output",
        scope=KnowledgeScope.STUDIO,
        evidence_refs=["P1"],
        sandbox_passed=True,
        regression_passed=True,
    )
    passed, findings = board.review_learning(candidate)
    assert passed is False
    assert "STUDIO_SCOPE_REQUIRES_MULTIPLE_EVIDENCE_REFS" in findings


def test_learning_promotes_only_after_sandbox_and_regression():
    board = LearningPromotionBoard()
    candidate = LearningCandidate(
        observation="repeated result",
        hypothesis="stable improvement",
        scope=KnowledgeScope.DOMAIN,
        evidence_refs=["E1", "E2"],
        sandbox_passed=True,
        regression_passed=True,
    )
    promoted = board.promote_learning(candidate)
    assert promoted.promoted is True
