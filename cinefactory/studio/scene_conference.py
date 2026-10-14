from __future__ import annotations

from collections import Counter
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from cinefactory.domain.enums import ShotComplexity

from .contracts import CapabilityKind

from .production_conference import (
    ConferenceLane,
    ConferencePolicy,
    ProductionConferenceDecision,
)


class SceneProductionObjective(StrEnum):
    RETENTION_HOOK = "RETENTION_HOOK"
    PERFORMANCE_CONTINUITY = "PERFORMANCE_CONTINUITY"
    AUTHENTIC_GAMEPLAY = "AUTHENTIC_GAMEPLAY"
    GENERATIVE_MONTAGE = "GENERATIVE_MONTAGE"
    SCREEN_DEMO = "SCREEN_DEMO"
    MOTION_EXPLAINER = "MOTION_EXPLAINER"
    FOOTAGE_REALISM = "FOOTAGE_REALISM"
    ACTION = "ACTION"
    CONNECTIVE = "CONNECTIVE"


class SceneConferenceMetrics(BaseModel):
    shot_count: int = Field(ge=1)
    duration_seconds: float = Field(ge=0.0)
    performance_ratio: float = Field(ge=0.0, le=1.0)
    multi_actor_performance_ratio: float = Field(ge=0.0, le=1.0)
    action_density: float = Field(ge=0.0)
    complexity_score: float = Field(ge=0.0, le=1.0)
    hero_or_red_ratio: float = Field(ge=0.0, le=1.0)
    continuity_risk: float = Field(ge=0.0, le=1.0)
    specialized_objective: str | None = None


class SceneConferenceDecision(BaseModel):
    scene_id: str
    selected_lane: ConferenceLane
    selected_policy: ConferencePolicy
    metrics: SceneConferenceMetrics
    production_objective: SceneProductionObjective = SceneProductionObjective.CONNECTIVE
    required_capability_kind: CapabilityKind | None = None
    preferred_capability_kinds: list[CapabilityKind] = Field(default_factory=list)
    optimization_bias: dict[str, float] = Field(default_factory=dict)
    backend_switch_allowed: bool = False
    continuity_anchor: bool = True
    reasons: list[str] = Field(default_factory=list)


class SceneProductionConferenceReport(BaseModel):
    project_id: str
    global_lane: ConferenceLane
    scenes: list[SceneConferenceDecision] = Field(default_factory=list)
    backend_switch_budget: int = Field(default=0, ge=0)
    continuity_policy: str = "keep renderer class stable unless scene objective justifies a switch"

    def decision_for(self, scene_id: str) -> SceneConferenceDecision | None:
        for item in self.scenes:
            if item.scene_id == scene_id:
                return item
        return None

    def policy_map(self) -> dict[str, dict[str, Any]]:
        return {
            item.scene_id: item.model_dump(mode="json")
            for item in self.scenes
        }


class SceneProductionConference:
    """Choose an execution lane per scene under the global conference policy.

    This layer does not select a concrete tool. It sets per-scene quality/speed
    budgets and whether continuity permits a renderer-class change. Technical
    Direction still performs executable tool routing afterward.
    """

    _COMPLEXITY = {
        ShotComplexity.GREEN: 0.20,
        ShotComplexity.YELLOW: 0.45,
        ShotComplexity.RED: 0.78,
        ShotComplexity.HERO: 1.00,
    }

    _SPECIALIZED = (
        (
            "AI_VIDEO",
            (
                "dream",
                "dreamlike",
                "surreal",
                "abstract montage",
                "memory montage",
                "vision",
                "impossible transformation",
                "fantasy transition",
                "generative",
            ),
        ),
        (
            "SCREEN_CAPTURE",
            (
                "screen demo",
                "screen recording",
                "desktop",
                "software interface",
                "click through",
                "ui walkthrough",
            ),
        ),
        (
            "GAME_RUNTIME",
            (
                "real gameplay",
                "gameplay",
                "playthrough",
                "walkthrough",
                "speedrun",
                "in-game",
            ),
        ),
        (
            "FOOTAGE",
            (
                "b-roll",
                "b roll",
                "archive footage",
                "live action",
                "real-world footage",
                "documentary footage",
            ),
        ),
        (
            "MOTION_GRAPHICS",
            (
                "chart",
                "graph",
                "infographic",
                "kinetic text",
                "data visualization",
                "motion graphic",
            ),
        ),
    )

    @staticmethod
    def _scene_text(shots: list[Any]) -> str:
        parts: list[str] = []
        for shot in shots:
            for value in (
                getattr(shot, "narrative_purpose", None),
                getattr(shot, "audience_endpoint", None),
                getattr(shot, "edit_intent", None),
            ):
                if value:
                    parts.append(str(value))
            camera = getattr(shot, "camera", None)
            if camera is not None:
                for value in (
                    getattr(camera, "narrative_purpose", None),
                    getattr(camera, "shot_size", None),
                ):
                    if value:
                        parts.append(str(value))
        return " ".join(parts).lower()

    @classmethod
    def _specialized_objective(cls, text: str) -> str | None:
        for label, keywords in cls._SPECIALIZED:
            if any(keyword in text for keyword in keywords):
                return label
        return None

    @classmethod
    def _metrics(cls, shots: list[Any]) -> SceneConferenceMetrics:
        shot_count = len(shots)
        duration = sum(
            float(getattr(shot, "duration_seconds", 0.0) or 0.0)
            for shot in shots
        )
        performance_shots = 0
        multi_actor = 0
        action_beats = 0
        complexity_values: list[float] = []
        hero_or_red = 0

        for shot in shots:
            performance = getattr(shot, "performance", {}) or {}
            if performance:
                performance_shots += 1
            if len(performance) >= 2:
                multi_actor += 1
            action_beats += len(
                getattr(shot, "action_beats", []) or []
            )
            complexity = getattr(
                shot,
                "complexity",
                ShotComplexity.GREEN,
            )
            try:
                complexity = ShotComplexity(complexity)
            except ValueError:
                complexity = ShotComplexity.GREEN
            score = cls._COMPLEXITY[complexity]
            complexity_values.append(score)
            if complexity in {
                ShotComplexity.RED,
                ShotComplexity.HERO,
            }:
                hero_or_red += 1

        performance_ratio = performance_shots / shot_count
        multi_actor_ratio = multi_actor / shot_count
        complexity_score = (
            sum(complexity_values) / len(complexity_values)
            if complexity_values
            else 0.0
        )
        hero_ratio = hero_or_red / shot_count
        action_density = action_beats / shot_count

        # Continuity risk rises with acting, multi-character blocking, action
        # density and high-complexity shots. It is intentionally bounded.
        continuity_risk = min(
            1.0,
            performance_ratio * 0.35
            + multi_actor_ratio * 0.20
            + min(1.0, action_density / 3.0) * 0.15
            + complexity_score * 0.20
            + hero_ratio * 0.10,
        )
        text = cls._scene_text(shots)
        specialized = cls._specialized_objective(text)
        return SceneConferenceMetrics(
            shot_count=shot_count,
            duration_seconds=round(duration, 3),
            performance_ratio=round(performance_ratio, 4),
            multi_actor_performance_ratio=round(
                multi_actor_ratio,
                4,
            ),
            action_density=round(action_density, 4),
            complexity_score=round(complexity_score, 4),
            hero_or_red_ratio=round(hero_ratio, 4),
            continuity_risk=round(continuity_risk, 4),
            specialized_objective=specialized,
        )

    @staticmethod
    def _policies(
        global_decision: ProductionConferenceDecision,
    ) -> dict[ConferenceLane, ConferencePolicy]:
        result: dict[ConferenceLane, ConferencePolicy] = {}
        for proposal in global_decision.proposals:
            result[proposal.lane] = proposal.policy
        if (
            global_decision.selected_lane is not None
            and global_decision.selected_policy is not None
        ):
            result.setdefault(
                global_decision.selected_lane,
                global_decision.selected_policy,
            )
        return result

    @staticmethod
    def _lane_scores(
        metrics: SceneConferenceMetrics,
        global_lane: ConferenceLane,
    ) -> dict[ConferenceLane, float]:
        # The global lane is the prior, not a hard lock. High performance or
        # hero complexity can escalate a scene to QUALITY; simple connective
        # material can de-escalate to FAST in a balanced/fast production.
        scores = {
            ConferenceLane.QUALITY_FIRST: 0.58,
            ConferenceLane.BALANCED: 0.66,
            ConferenceLane.FAST_LEAN: 0.52,
        }
        scores[global_lane] += 0.18

        quality_pressure = min(
            1.0,
            metrics.performance_ratio * 0.35
            + metrics.multi_actor_performance_ratio * 0.20
            + metrics.complexity_score * 0.25
            + metrics.hero_or_red_ratio * 0.20,
        )
        scores[ConferenceLane.QUALITY_FIRST] += (
            0.34 * quality_pressure
        )
        scores[ConferenceLane.BALANCED] += (
            0.12 * quality_pressure
        )
        scores[ConferenceLane.FAST_LEAN] -= (
            0.18 * quality_pressure
        )

        simple_pressure = max(
            0.0,
            1.0
            - metrics.complexity_score
            - metrics.performance_ratio * 0.45,
        )
        if metrics.shot_count <= 2:
            simple_pressure += 0.08
        simple_pressure = min(1.0, simple_pressure)
        scores[ConferenceLane.FAST_LEAN] += (
            0.20 * simple_pressure
        )
        scores[ConferenceLane.BALANCED] += (
            0.08 * simple_pressure
        )

        # Specialized transition/visualization scenes often benefit from a
        # selective backend and a balanced rather than maximally expensive lane.
        if metrics.specialized_objective:
            scores[ConferenceLane.BALANCED] += 0.16
            if metrics.continuity_risk < 0.45:
                scores[ConferenceLane.FAST_LEAN] += 0.06

        return {
            lane: round(max(0.0, value), 4)
            for lane, value in scores.items()
        }

    @staticmethod
    def _execution_directive(
        metrics: SceneConferenceMetrics,
        *,
        scene_index: int,
    ) -> tuple[
        SceneProductionObjective,
        CapabilityKind | None,
        list[CapabilityKind],
        dict[str, float],
        list[str],
    ]:
        specialized = metrics.specialized_objective
        if specialized == "GAME_RUNTIME":
            return (
                SceneProductionObjective.AUTHENTIC_GAMEPLAY,
                CapabilityKind.GAME_RUNTIME,
                [CapabilityKind.GAME_RUNTIME],
                {"quality": 0.04, "speed": 0.02, "determinism": 0.08},
                ["authentic gameplay requires a real game runtime"],
            )
        if specialized == "AI_VIDEO":
            return (
                SceneProductionObjective.GENERATIVE_MONTAGE,
                None,
                [CapabilityKind.AI_VIDEO, CapabilityKind.OFFLINE_3D],
                {"quality": 0.05, "speed": 0.04},
                ["generative montage prefers qualified AI video when continuity permits"],
            )
        if specialized == "SCREEN_CAPTURE":
            return (
                SceneProductionObjective.SCREEN_DEMO,
                None,
                [CapabilityKind.SCREEN_CAPTURE],
                {"determinism": 0.08, "speed": 0.04},
                ["screen demonstration prefers executable screen capture"],
            )
        if specialized == "MOTION_GRAPHICS":
            return (
                SceneProductionObjective.MOTION_EXPLAINER,
                None,
                [CapabilityKind.MOTION_GRAPHICS],
                {"quality": 0.04, "speed": 0.05},
                ["data/explainer scene prefers motion graphics"],
            )
        if specialized == "FOOTAGE":
            return (
                SceneProductionObjective.FOOTAGE_REALISM,
                None,
                [CapabilityKind.FOOTAGE],
                {"quality": 0.05, "determinism": 0.03},
                ["real-world evidence scene prefers footage"],
            )
        if scene_index == 0:
            return (
                SceneProductionObjective.RETENTION_HOOK,
                None,
                [],
                {"quality": 0.05, "speed": 0.10, "determinism": 0.03},
                ["opening scene prioritizes retention, pacing and fast iteration"],
            )
        if metrics.performance_ratio >= 0.5:
            return (
                SceneProductionObjective.PERFORMANCE_CONTINUITY,
                None,
                [CapabilityKind.OFFLINE_3D, CapabilityKind.REALTIME_3D],
                {"quality": 0.10, "determinism": 0.08, "speed": -0.03},
                ["performance-heavy scene prioritizes acting and identity continuity"],
            )
        if metrics.action_density >= 1.0:
            return (
                SceneProductionObjective.ACTION,
                None,
                [CapabilityKind.OFFLINE_3D, CapabilityKind.REALTIME_3D],
                {"quality": 0.06, "speed": 0.03, "determinism": 0.04},
                ["action scene prioritizes motion readability and stable staging"],
            )
        return (
            SceneProductionObjective.CONNECTIVE,
            None,
            [],
            {"speed": 0.06, "availability": 0.03},
            ["connective scene favors throughput while preserving global continuity"],
        )

    @staticmethod
    def _switch_allowed(
        metrics: SceneConferenceMetrics,
    ) -> tuple[bool, list[str]]:
        reasons: list[str] = []
        if metrics.specialized_objective is None:
            return False, [
                "no specialized scene objective justifies renderer-class change"
            ]
        if metrics.specialized_objective == "GAME_RUNTIME":
            return True, [
                "authentic gameplay requirement overrides renderer-class continuity pin"
            ]
        if metrics.continuity_risk >= 0.72:
            return False, [
                (
                    "specialized objective exists but continuity risk is too "
                    "high for automatic renderer-class switching"
                )
            ]
        reasons.append(
            "specialized_objective="
            + metrics.specialized_objective
        )
        reasons.append(
            "continuity risk is below automatic switch threshold"
        )
        return True, reasons

    def deliberate(
        self,
        *,
        project_id: str,
        shots: list[Any],
        global_decision: ProductionConferenceDecision,
    ) -> SceneProductionConferenceReport:
        if (
            not global_decision.executable
            or global_decision.selected_lane is None
            or global_decision.selected_policy is None
        ):
            raise ValueError(
                "SCENE_CONFERENCE_REQUIRES_EXECUTABLE_GLOBAL_CONFERENCE"
            )

        by_scene: dict[str, list[Any]] = {}
        for shot in shots:
            by_scene.setdefault(
                str(getattr(shot, "scene_id")),
                [],
            ).append(shot)

        policies = self._policies(global_decision)
        decisions: list[SceneConferenceDecision] = []
        switch_budget = 0
        for scene_index, (scene_id, scene_shots) in enumerate(by_scene.items()):
            metrics = self._metrics(scene_shots)
            scores = self._lane_scores(
                metrics,
                global_decision.selected_lane,
            )
            selected_lane = max(
                scores,
                key=lambda lane: (
                    scores[lane],
                    {
                        ConferenceLane.BALANCED: 2,
                        ConferenceLane.QUALITY_FIRST: 1,
                        ConferenceLane.FAST_LEAN: 0,
                    }[lane],
                ),
            )
            policy = policies.get(selected_lane)
            if policy is None:
                policy = global_decision.selected_policy
                selected_lane = global_decision.selected_lane

            (
                production_objective,
                required_capability_kind,
                preferred_capability_kinds,
                optimization_bias,
                directive_reasons,
            ) = self._execution_directive(
                metrics,
                scene_index=scene_index,
            )
            switch_allowed, switch_reasons = self._switch_allowed(
                metrics
            )
            if switch_allowed:
                switch_budget += 1

            reasons = [
                (
                    "scene_lane_scores="
                    + ",".join(
                        f"{lane.value}:{scores[lane]:.4f}"
                        for lane in ConferenceLane
                    )
                ),
                (
                    "global_lane_prior="
                    + global_decision.selected_lane.value
                ),
                (
                    "continuity_risk="
                    + f"{metrics.continuity_risk:.4f}"
                ),
                *switch_reasons,
                *directive_reasons,
            ]
            if (
                metrics.performance_ratio >= 0.5
                or metrics.hero_or_red_ratio > 0
            ):
                reasons.append(
                    "acting/hero complexity increased quality pressure"
                )

            decisions.append(
                SceneConferenceDecision(
                    scene_id=scene_id,
                    selected_lane=selected_lane,
                    selected_policy=policy,
                    metrics=metrics,
                    production_objective=production_objective,
                    required_capability_kind=required_capability_kind,
                    preferred_capability_kinds=preferred_capability_kinds,
                    optimization_bias=optimization_bias,
                    backend_switch_allowed=switch_allowed,
                    continuity_anchor=not switch_allowed,
                    reasons=reasons,
                )
            )

        return SceneProductionConferenceReport(
            project_id=project_id,
            global_lane=global_decision.selected_lane,
            scenes=decisions,
            backend_switch_budget=switch_budget,
        )
