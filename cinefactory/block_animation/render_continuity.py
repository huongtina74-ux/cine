from __future__ import annotations

import math
from typing import Any

from pydantic import BaseModel, Field


class RenderContinuityCheck(BaseModel):
    code: str
    subject: str
    passed: bool
    hard_failure: bool = False
    value: float | str | None = None
    threshold: float | str | None = None
    message: str


class RenderContinuityResult(BaseModel):
    measured: bool
    passed: bool
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    findings: list[str] = Field(default_factory=list)
    checks: list[RenderContinuityCheck] = Field(default_factory=list)
    previous_shot_id: str | None = None
    current_shot_id: str | None = None
    scene_id: str | None = None


class RenderContinuityEvaluator:
    """Compare actual Blender end/start states across adjacent shots.

    This intentionally avoids judging a scene transition. It only measures when
    both render states declare the same non-empty scene_id.
    """

    @staticmethod
    def _distance(a: list[float], b: list[float]) -> float:
        return math.sqrt(
            sum((float(x) - float(y)) ** 2 for x, y in zip(a, b))
        )

    @staticmethod
    def _angle_delta(a: float, b: float) -> float:
        delta = abs(float(a) - float(b)) % (2 * math.pi)
        return min(delta, 2 * math.pi - delta)

    @staticmethod
    def _relative_delta(a: float, b: float) -> float:
        denom = max(abs(float(a)), abs(float(b)), 1e-6)
        return abs(float(a) - float(b)) / denom

    def compare(
        self,
        previous: dict[str, Any] | None,
        current: dict[str, Any] | None,
    ) -> RenderContinuityResult:
        previous = previous or {}
        current = current or {}
        previous_shot_id = previous.get("shot_id")
        current_shot_id = current.get("shot_id")
        previous_scene = previous.get("scene_id")
        current_scene = current.get("scene_id")

        if not previous or not current:
            return RenderContinuityResult(
                measured=False,
                passed=True,
                findings=["RENDER_CONTINUITY_NOT_MEASURED:MISSING_STATE"],
                previous_shot_id=previous_shot_id,
                current_shot_id=current_shot_id,
            )

        if (
            not previous_scene
            or not current_scene
            or previous_scene != current_scene
        ):
            return RenderContinuityResult(
                measured=False,
                passed=True,
                findings=["RENDER_CONTINUITY_NOT_MEASURED:SCENE_TRANSITION"],
                previous_shot_id=previous_shot_id,
                current_shot_id=current_shot_id,
                scene_id=current_scene,
            )

        checks: list[RenderContinuityCheck] = []
        findings: list[str] = []

        prev_actors = previous.get("actors") or {}
        curr_actors = current.get("actors") or {}
        for actor_id in sorted(set(prev_actors) & set(curr_actors)):
            a = prev_actors[actor_id]
            b = curr_actors[actor_id]

            same_identity = (
                bool(a.get("identity_signature"))
                and a.get("identity_signature")
                == b.get("identity_signature")
            )
            checks.append(
                RenderContinuityCheck(
                    code="IDENTITY_SIGNATURE",
                    subject=actor_id,
                    passed=same_identity,
                    hard_failure=not same_identity,
                    value=(
                        "MATCH"
                        if same_identity
                        else "MISMATCH"
                    ),
                    threshold="MATCH",
                    message=(
                        "scene-rig identity signature must remain stable "
                        "across a same-scene cut"
                    ),
                )
            )

            prev_end = a.get("end") or {}
            curr_start = b.get("start") or {}
            if prev_end.get("root_location") and curr_start.get("root_location"):
                distance = self._distance(
                    prev_end["root_location"],
                    curr_start["root_location"],
                )
                hard = distance > 0.75
                passed = not hard
                checks.append(
                    RenderContinuityCheck(
                        code="ROOT_POSITION",
                        subject=actor_id,
                        passed=passed,
                        hard_failure=hard,
                        value=distance,
                        threshold=0.75,
                        message=(
                            "same-scene actor end/start root positions "
                            "must not jump without an encoded transition"
                        ),
                    )
                )
                if 0.25 < distance <= 0.75:
                    findings.append(
                        f"CONTINUITY_WARNING:{actor_id}:ROOT_POSITION_DRIFT:{distance:.3f}"
                    )

            if prev_end.get("root_rotation") and curr_start.get("root_rotation"):
                yaw = self._angle_delta(
                    prev_end["root_rotation"][2],
                    curr_start["root_rotation"][2],
                )
                hard = yaw > 1.0
                passed = not hard
                checks.append(
                    RenderContinuityCheck(
                        code="ROOT_YAW",
                        subject=actor_id,
                        passed=passed,
                        hard_failure=hard,
                        value=yaw,
                        threshold=1.0,
                        message=(
                            "same-scene actor facing should not flip "
                            "without an encoded transition"
                        ),
                    )
                )
                if 0.35 < yaw <= 1.0:
                    findings.append(
                        f"CONTINUITY_WARNING:{actor_id}:ROOT_YAW_DRIFT:{yaw:.3f}"
                    )

        prev_props = previous.get("props") or {}
        curr_props = current.get("props") or {}
        for prop_id in sorted(set(prev_props) & set(curr_props)):
            a = prev_props[prop_id]
            b = curr_props[prop_id]
            parent_ok = a.get("parent") == b.get("parent")
            checks.append(
                RenderContinuityCheck(
                    code="PROP_PARENT",
                    subject=prop_id,
                    passed=parent_ok,
                    hard_failure=not parent_ok,
                    value=(
                        "MATCH" if parent_ok else "MISMATCH"
                    ),
                    threshold="MATCH",
                    message=(
                        "prop attachment parent must remain stable "
                        "across the same-scene cut"
                    ),
                )
            )
            if a.get("end_location") and b.get("start_location"):
                distance = self._distance(
                    a["end_location"],
                    b["start_location"],
                )
                hard = distance > 0.85
                checks.append(
                    RenderContinuityCheck(
                        code="PROP_POSITION",
                        subject=prop_id,
                        passed=not hard,
                        hard_failure=hard,
                        value=distance,
                        threshold=0.85,
                        message=(
                            "prop world position should remain continuous "
                            "across the cut"
                        ),
                    )
                )
                if 0.30 < distance <= 0.85:
                    findings.append(
                        f"CONTINUITY_WARNING:{prop_id}:PROP_POSITION_DRIFT:{distance:.3f}"
                    )

        prev_light = previous.get("lighting") or {}
        curr_light = current.get("lighting") or {}
        same_light_intent = (
            prev_light.get("light_state") == curr_light.get("light_state")
            and prev_light.get("time_of_day") == curr_light.get("time_of_day")
        )
        if same_light_intent and (prev_light or curr_light):
            for field in (
                "key_energy",
                "fill_energy",
                "rim_energy",
                "world_strength",
            ):
                if field not in prev_light or field not in curr_light:
                    continue
                delta = self._relative_delta(
                    float(prev_light[field]),
                    float(curr_light[field]),
                )
                hard = delta > 0.25
                checks.append(
                    RenderContinuityCheck(
                        code=f"LIGHT_{field.upper()}",
                        subject="lighting",
                        passed=not hard,
                        hard_failure=hard,
                        value=delta,
                        threshold=0.25,
                        message=(
                            "identical lighting intent should produce "
                            "stable adjacent-shot lighting controls"
                        ),
                    )
                )
                if 0.10 < delta <= 0.25:
                    findings.append(
                        f"CONTINUITY_WARNING:LIGHTING:{field}:{delta:.3f}"
                    )

        hard_failures = [
            check
            for check in checks
            if check.hard_failure
        ]
        passed_checks = sum(1 for check in checks if check.passed)
        score = (
            passed_checks / len(checks)
            if checks
            else None
        )
        findings.extend(
            f"CONTINUITY_BLOCKER:{check.subject}:{check.code}"
            for check in hard_failures
        )
        return RenderContinuityResult(
            measured=bool(checks),
            passed=not hard_failures,
            score=score,
            findings=findings,
            checks=checks,
            previous_shot_id=previous_shot_id,
            current_shot_id=current_shot_id,
            scene_id=current_scene,
        )
