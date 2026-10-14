from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from cinefactory.production.contracts import DailiesReport

from .production_conference import (
    ConferenceLane,
    ConferencePolicy,
    ProductionConferenceDecision,
)


class AdaptationAction(StrEnum):
    KEEP = "KEEP"
    ESCALATE = "ESCALATE"
    DEESCALATE = "DEESCALATE"


class SceneExecutionOutcome(BaseModel):
    scene_id: str
    tool_id: str
    lane: str | None = None
    passed: bool
    shot_count: int = Field(ge=0)
    accepted_shot_count: int = Field(ge=0)
    average_selected_score: float = Field(ge=0.0, le=1.0)
    worst_selected_score: float = Field(ge=0.0, le=1.0)
    max_repair_round: int = Field(ge=0)
    failed_shot_ids: list[str] = Field(default_factory=list)
    qc_target: float = Field(ge=0.0, le=1.0)


class AdaptiveBudgetChange(BaseModel):
    source_scene_id: str
    target_scene_id: str
    tool_id: str
    action: AdaptationAction
    previous_lane: str
    new_lane: str
    reason: str
    previous_policy: dict[str, Any] = Field(default_factory=dict)
    new_policy: dict[str, Any] = Field(default_factory=dict)


class AdaptiveProductionReport(BaseModel):
    project_id: str
    outcomes: list[SceneExecutionOutcome] = Field(default_factory=list)
    changes: list[AdaptiveBudgetChange] = Field(default_factory=list)
    hard_constraints: list[str] = Field(
        default_factory=lambda: [
            "never change script or scene content",
            "never change tool/backend class automatically",
            "never override authenticity-sensitive routing",
            "never deescalate high-continuity-risk scenes",
            "never invent a policy outside the conference-approved proposal family",
        ]
    )

    @property
    def adaptation_count(self) -> int:
        return len(self.changes)


class AdaptiveProductionSupervisor:
    """Rebudget pending scenes from observed dailies evidence.

    The supervisor only changes the execution budget/lane for pending batches.
    Tool identity, capability class, script, story and authenticity constraints
    are immutable here.
    """

    _ORDER = [
        ConferenceLane.FAST_LEAN,
        ConferenceLane.BALANCED,
        ConferenceLane.QUALITY_FIRST,
    ]

    def __init__(
        self,
        *,
        project_id: str,
        global_decision: ProductionConferenceDecision,
    ) -> None:
        if not global_decision.executable:
            raise ValueError(
                "ADAPTIVE_SUPERVISOR_REQUIRES_EXECUTABLE_CONFERENCE"
            )
        self.project_id = project_id
        self.global_decision = global_decision
        self.report = AdaptiveProductionReport(project_id=project_id)
        self._policies = {
            item.lane: item.policy
            for item in global_decision.proposals
        }
        if (
            global_decision.selected_lane is not None
            and global_decision.selected_policy is not None
        ):
            self._policies.setdefault(
                global_decision.selected_lane,
                global_decision.selected_policy,
            )

    @staticmethod
    def _lane(value: str | None) -> ConferenceLane:
        try:
            return ConferenceLane(value or ConferenceLane.BALANCED.value)
        except ValueError:
            return ConferenceLane.BALANCED

    @classmethod
    def _step_up(cls, lane: ConferenceLane) -> ConferenceLane:
        index = cls._ORDER.index(lane)
        return cls._ORDER[min(len(cls._ORDER) - 1, index + 1)]

    @classmethod
    def _step_down(cls, lane: ConferenceLane) -> ConferenceLane:
        index = cls._ORDER.index(lane)
        return cls._ORDER[max(0, index - 1)]

    @staticmethod
    def _continuity_risk(batch: dict[str, Any]) -> float:
        metrics = batch.get("metrics") or {}
        try:
            return float(metrics.get("continuity_risk", 0.0) or 0.0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _complexity(batch: dict[str, Any]) -> float:
        metrics = batch.get("metrics") or {}
        try:
            return float(metrics.get("complexity_score", 0.0) or 0.0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _specialized(batch: dict[str, Any]) -> bool:
        metrics = batch.get("metrics") or {}
        return bool(metrics.get("specialized_objective"))

    @staticmethod
    def outcome(
        *,
        batch: dict[str, Any],
        budget: dict[str, Any],
        dailies: DailiesReport,
    ) -> SceneExecutionOutcome:
        scores = [
            float(item.selected_score)
            for item in dailies.shots
            if item.passed and (
                item.selected_take_id or item.selected_path
            )
        ]
        failed = [
            str(item.shot_id)
            for item in dailies.shots
            if not item.passed
        ]
        repairs = [
            int(take.repair_round)
            for item in dailies.shots
            for take in item.takes
        ]
        average = sum(scores) / len(scores) if scores else 0.0
        worst = min(scores) if scores else 0.0
        return SceneExecutionOutcome(
            scene_id=str(batch.get("scene_id") or "UNKNOWN_SCENE"),
            tool_id=str(batch.get("tool_id") or "unknown"),
            lane=(
                str(batch.get("scene_lane"))
                if batch.get("scene_lane") is not None
                else None
            ),
            passed=bool(dailies.passed and not failed),
            shot_count=len(dailies.shots),
            accepted_shot_count=len(scores),
            average_selected_score=round(average, 4),
            worst_selected_score=round(worst, 4),
            max_repair_round=max(repairs, default=0),
            failed_shot_ids=failed,
            qc_target=float(budget.get("qc_target", 0.0) or 0.0),
        )

    def _replace_policy(
        self,
        batch: dict[str, Any],
        *,
        new_lane: ConferenceLane,
    ) -> None:
        policy = self._policies.get(new_lane)
        if policy is None:
            return
        batch["scene_lane"] = new_lane.value
        batch["policy"] = policy.model_dump(mode="json")

    def observe_and_rebudget(
        self,
        *,
        batch: dict[str, Any],
        budget: dict[str, Any],
        dailies: DailiesReport,
        remaining_batches: list[dict[str, Any]],
    ) -> list[AdaptiveBudgetChange]:
        outcome = self.outcome(
            batch=batch,
            budget=budget,
            dailies=dailies,
        )
        self.report.outcomes.append(outcome)

        pressure = (
            not outcome.passed
            or outcome.worst_selected_score
            < min(1.0, outcome.qc_target + 0.03)
            or outcome.max_repair_round > 0
        )
        strong = (
            outcome.passed
            and outcome.average_selected_score
            >= min(1.0, outcome.qc_target + 0.12)
            and outcome.max_repair_round == 0
        )

        changes: list[AdaptiveBudgetChange] = []
        for target in remaining_batches:
            if str(target.get("tool_id")) != outcome.tool_id:
                continue

            target_lane = self._lane(
                str(target.get("scene_lane") or "")
            )
            previous_policy = dict(target.get("policy") or {})
            risk = self._continuity_risk(target)
            complexity = self._complexity(target)

            action = AdaptationAction.KEEP
            new_lane = target_lane
            reason = ""

            if pressure and target_lane is not ConferenceLane.QUALITY_FIRST:
                # A weak prior scene on the same backend is evidence to buy
                # more margin for subsequent nontrivial scenes.
                if risk >= 0.30 or complexity >= 0.35 or self._specialized(target):
                    new_lane = self._step_up(target_lane)
                    action = AdaptationAction.ESCALATE
                    reason = (
                        "prior same-backend scene had weak QC margin or repairs; "
                        "increase pending scene execution budget"
                    )

            elif strong:
                global_lane = self.global_decision.selected_lane
                if (
                    global_lane is not ConferenceLane.QUALITY_FIRST
                    and target_lane is not ConferenceLane.FAST_LEAN
                    and risk < 0.30
                    and complexity < 0.35
                    and not self._specialized(target)
                ):
                    new_lane = self._step_down(target_lane)
                    action = AdaptationAction.DEESCALATE
                    reason = (
                        "prior same-backend scene cleared QC with strong margin; "
                        "reduce budget for a low-risk pending scene"
                    )

            if action is AdaptationAction.KEEP or new_lane is target_lane:
                continue

            self._replace_policy(target, new_lane=new_lane)
            change = AdaptiveBudgetChange(
                source_scene_id=outcome.scene_id,
                target_scene_id=str(
                    target.get("scene_id") or "UNKNOWN_SCENE"
                ),
                tool_id=outcome.tool_id,
                action=action,
                previous_lane=target_lane.value,
                new_lane=new_lane.value,
                reason=reason,
                previous_policy=previous_policy,
                new_policy=dict(target.get("policy") or {}),
            )
            changes.append(change)
            self.report.changes.append(change)

        return changes
