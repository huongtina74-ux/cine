from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from cinefactory.production.contracts import DailiesReport

from .planning import ProductionHandoff
from .production_conference import (
    ConferenceLane,
    ProductionConferenceDecision,
)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryAdviceAction(StrEnum):
    KEEP = "KEEP"
    ESCALATE = "ESCALATE"
    DEESCALATE = "DEESCALATE"


class ProductionExperience(BaseModel):
    experience_id: str
    project_id: str
    scene_id: str
    tool_id: str
    lane: ConferenceLane
    specialized_objective: str = "NONE"
    complexity_bucket: str
    continuity_bucket: str
    passed: bool
    average_selected_score: float = Field(ge=0.0, le=1.0)
    worst_selected_score: float = Field(ge=0.0, le=1.0)
    qc_target: float = Field(ge=0.0, le=1.0)
    qc_margin: float
    max_repair_round: int = Field(ge=0)
    shot_count: int = Field(ge=0)
    recorded_at: str = Field(default_factory=_utcnow)


class ProductionMemoryAdvice(BaseModel):
    scene_id: str
    tool_id: str
    current_lane: ConferenceLane
    action: MemoryAdviceAction
    recommended_lane: ConferenceLane
    sample_count: int = Field(ge=0)
    success_rate: float = Field(ge=0.0, le=1.0)
    repair_rate: float = Field(ge=0.0, le=1.0)
    average_qc_margin: float
    confidence: float = Field(ge=0.0, le=1.0)
    applied: bool = False
    evidence_experience_ids: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)


class ProductionMemoryApplication(BaseModel):
    project_id: str
    advices: list[ProductionMemoryAdvice] = Field(default_factory=list)
    adjusted_scene_ids: list[str] = Field(default_factory=list)


class ProductionExperienceStore:
    """Durable, bounded operational memory for production budgeting.

    It never changes scripts or tool assignments. Historical evidence may only
    nudge a scene one conference lane after enough matching samples exist.
    """

    _ORDER = [
        ConferenceLane.FAST_LEAN,
        ConferenceLane.BALANCED,
        ConferenceLane.QUALITY_FIRST,
    ]

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "production_experiences.jsonl"

    @staticmethod
    def _bucket(value: float) -> str:
        if value < 0.30:
            return "LOW"
        if value < 0.65:
            return "MEDIUM"
        return "HIGH"

    @staticmethod
    def _metrics(batch: dict[str, Any]) -> dict[str, Any]:
        raw = batch.get("metrics") or {}
        return raw if isinstance(raw, dict) else {}

    @staticmethod
    def _lane(value: Any) -> ConferenceLane:
        try:
            return ConferenceLane(str(value))
        except ValueError:
            return ConferenceLane.BALANCED

    @classmethod
    def _step_up(cls, lane: ConferenceLane) -> ConferenceLane:
        idx = cls._ORDER.index(lane)
        return cls._ORDER[min(len(cls._ORDER) - 1, idx + 1)]

    @classmethod
    def _step_down(cls, lane: ConferenceLane) -> ConferenceLane:
        idx = cls._ORDER.index(lane)
        return cls._ORDER[max(0, idx - 1)]

    def append(self, experience: ProductionExperience) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    experience.model_dump(mode="json"),
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )

    def list(self) -> list[ProductionExperience]:
        if not self.path.is_file():
            return []
        result: list[ProductionExperience] = []
        for line in self.path.read_text(
            encoding="utf-8",
            errors="ignore",
        ).splitlines():
            if not line.strip():
                continue
            try:
                result.append(
                    ProductionExperience.model_validate_json(line)
                )
            except Exception:
                # Corrupt historical line is ignored rather than poisoning a
                # new production run.
                continue
        return result

    def record_scene(
        self,
        *,
        project_id: str,
        batch: dict[str, Any],
        budget: dict[str, Any],
        dailies: DailiesReport,
    ) -> ProductionExperience | None:
        tool_id = str(batch.get("tool_id") or "")
        if not tool_id or tool_id == "diagnostic_slate":
            return None

        scores = [
            float(item.selected_score)
            for item in dailies.shots
            if item.passed and (item.selected_take_id or item.selected_path)
        ]
        repairs = [
            int(take.repair_round)
            for item in dailies.shots
            for take in item.takes
        ]
        average = sum(scores) / len(scores) if scores else 0.0
        worst = min(scores) if scores else 0.0
        qc_target = float(budget.get("qc_target", 0.0) or 0.0)
        metrics = self._metrics(batch)
        complexity = float(
            metrics.get("complexity_score", 0.0) or 0.0
        )
        continuity = float(
            metrics.get("continuity_risk", 0.0) or 0.0
        )
        specialized = str(
            metrics.get("specialized_objective") or "NONE"
        )
        scene_id = str(batch.get("scene_id") or "UNKNOWN_SCENE")
        lane = self._lane(
            batch.get("scene_lane") or ConferenceLane.BALANCED.value
        )
        sequence = len(self.list()) + 1
        exp = ProductionExperience(
            experience_id=(
                f"EXP_{project_id}_{scene_id}_{sequence:06d}"
            ),
            project_id=project_id,
            scene_id=scene_id,
            tool_id=tool_id,
            lane=lane,
            specialized_objective=specialized,
            complexity_bucket=self._bucket(complexity),
            continuity_bucket=self._bucket(continuity),
            passed=bool(dailies.passed and len(scores) == len(dailies.shots)),
            average_selected_score=round(average, 4),
            worst_selected_score=round(worst, 4),
            qc_target=round(qc_target, 4),
            qc_margin=round(worst - qc_target, 4),
            max_repair_round=max(repairs, default=0),
            shot_count=len(dailies.shots),
        )
        self.append(exp)
        return exp

    def _matches(
        self,
        *,
        tool_id: str,
        lane: ConferenceLane,
        specialized_objective: str,
        complexity_bucket: str,
        continuity_bucket: str,
        exclude_project_id: str | None = None,
    ) -> list[ProductionExperience]:
        return [
            item
            for item in self.list()
            if item.tool_id == tool_id
            and item.lane is lane
            and item.specialized_objective == specialized_objective
            and item.complexity_bucket == complexity_bucket
            and item.continuity_bucket == continuity_bucket
            and (
                exclude_project_id is None
                or item.project_id != exclude_project_id
            )
        ]

    def advise(
        self,
        *,
        project_id: str,
        scene_id: str,
        tool_id: str,
        current_lane: ConferenceLane,
        metrics: dict[str, Any],
        global_lane: ConferenceLane,
    ) -> ProductionMemoryAdvice:
        complexity = float(
            metrics.get("complexity_score", 0.0) or 0.0
        )
        continuity = float(
            metrics.get("continuity_risk", 0.0) or 0.0
        )
        specialized = str(
            metrics.get("specialized_objective") or "NONE"
        )
        matches = self._matches(
            tool_id=tool_id,
            lane=current_lane,
            specialized_objective=specialized,
            complexity_bucket=self._bucket(complexity),
            continuity_bucket=self._bucket(continuity),
            exclude_project_id=project_id,
        )
        sample_count = len(matches)
        if not matches:
            return ProductionMemoryAdvice(
                scene_id=scene_id,
                tool_id=tool_id,
                current_lane=current_lane,
                action=MemoryAdviceAction.KEEP,
                recommended_lane=current_lane,
                sample_count=0,
                success_rate=0.0,
                repair_rate=0.0,
                average_qc_margin=0.0,
                confidence=0.0,
                reasons=["no matching cross-project production evidence"],
            )

        success_rate = sum(item.passed for item in matches) / sample_count
        repair_rate = sum(
            item.max_repair_round > 0 for item in matches
        ) / sample_count
        average_margin = sum(
            item.qc_margin for item in matches
        ) / sample_count
        confidence = min(1.0, sample_count / 8.0)
        action = MemoryAdviceAction.KEEP
        recommended = current_lane
        reasons: list[str] = []

        if sample_count < 3:
            reasons.append(
                "fewer than three matching cross-project samples"
            )
        elif (
            success_rate < 0.80
            or repair_rate >= 0.50
            or average_margin < 0.03
        ):
            recommended = self._step_up(current_lane)
            if recommended is not current_lane:
                action = MemoryAdviceAction.ESCALATE
                reasons.append(
                    "historical matching scenes show weak QC margin, failures, or frequent repairs"
                )
        elif (
            sample_count >= 4
            and success_rate >= 0.98
            and repair_rate <= 0.10
            and average_margin >= 0.12
            and continuity < 0.30
            and complexity < 0.35
            and specialized == "NONE"
            and global_lane is not ConferenceLane.QUALITY_FIRST
        ):
            recommended = self._step_down(current_lane)
            if recommended is not current_lane:
                action = MemoryAdviceAction.DEESCALATE
                reasons.append(
                    "historical matching low-risk scenes consistently clear QC with excess margin"
                )

        if not reasons:
            reasons.append(
                "historical evidence does not justify a budget-lane change"
            )

        return ProductionMemoryAdvice(
            scene_id=scene_id,
            tool_id=tool_id,
            current_lane=current_lane,
            action=action,
            recommended_lane=recommended,
            sample_count=sample_count,
            success_rate=round(success_rate, 4),
            repair_rate=round(repair_rate, 4),
            average_qc_margin=round(average_margin, 4),
            confidence=round(confidence, 4),
            evidence_experience_ids=[
                item.experience_id for item in matches[-8:]
            ],
            reasons=reasons,
        )

    @staticmethod
    def _policies(
        conference: ProductionConferenceDecision,
    ) -> dict[ConferenceLane, dict[str, Any]]:
        return {
            item.lane: item.policy.model_dump(mode="json")
            for item in conference.proposals
        }

    def apply_to_handoff(
        self,
        *,
        project_id: str,
        handoff: ProductionHandoff,
        conference: ProductionConferenceDecision,
    ) -> tuple[ProductionHandoff, ProductionMemoryApplication]:
        if (
            not conference.executable
            or conference.selected_lane is None
        ):
            return handoff, ProductionMemoryApplication(
                project_id=project_id
            )

        policies = self._policies(conference)
        plans = []
        advices: list[ProductionMemoryAdvice] = []
        adjusted: list[str] = []

        for plan in handoff.scene_plans:
            assignment = plan.render_assignment
            tool_id = (
                assignment.selected_tool_id
                if assignment is not None
                and assignment.execution_ready
                else None
            )
            if not tool_id:
                plans.append(plan)
                continue

            try:
                current_lane = ConferenceLane(
                    plan.scene_conference_lane
                    or conference.selected_lane.value
                )
            except ValueError:
                current_lane = conference.selected_lane

            advice = self.advise(
                project_id=project_id,
                scene_id=plan.scene_id,
                tool_id=tool_id,
                current_lane=current_lane,
                metrics=dict(plan.scene_conference_metrics),
                global_lane=conference.selected_lane,
            )
            can_apply = (
                advice.action is not MemoryAdviceAction.KEEP
                and advice.recommended_lane in policies
                and advice.confidence >= 0.375
            )
            # Memory never changes the chosen tool/backend. It only updates the
            # budget policy carried by this already-routed scene plan.
            if can_apply:
                plan = plan.model_copy(
                    update={
                        "scene_conference_lane": (
                            advice.recommended_lane.value
                        ),
                        "scene_conference_policy": dict(
                            policies[advice.recommended_lane]
                        ),
                        "notes": [
                            *plan.notes,
                            (
                                "cross_episode_memory_"
                                + advice.action.value.lower()
                            ),
                        ],
                    },
                    deep=True,
                )
                advice = advice.model_copy(
                    update={"applied": True}
                )
                adjusted.append(plan.scene_id)

            plans.append(plan)
            advices.append(advice)

        return (
            handoff.model_copy(
                update={"scene_plans": plans},
                deep=True,
            ),
            ProductionMemoryApplication(
                project_id=project_id,
                advices=advices,
                adjusted_scene_ids=adjusted,
            ),
        )
