from __future__ import annotations

import math
from typing import Any

from pydantic import BaseModel, Field

from cinefactory.block_animation.contracts import CompiledShot
from cinefactory.domain.enums import FailureCode
from cinefactory.production.contracts import RepairDirective


class AppliedRepair(BaseModel):
    failure_code: FailureCode
    owner: str
    action: str
    changes: dict[str, Any] = Field(default_factory=dict)


class BlockRepairPlan(BaseModel):
    shot_id: str
    repair_round: int = Field(ge=1)
    supported: bool
    repaired_shot: CompiledShot | None = None
    applied: list[AppliedRepair] = Field(default_factory=list)
    skipped: list[str] = Field(default_factory=list)
    memory_hints: list[dict[str, Any]] = Field(default_factory=list)


class LocalBlockRepairPlanner:
    """Bounded local repairs for already-approved block-animation shots.

    This planner never rewrites story, shot purpose, canonical assets, or
    continuity states. It only changes reversible execution parameters.
    """

    SUPPORTED = {
        FailureCode.LOOKDEV_FAIL,
        FailureCode.CAMERA_INTENT_FAIL,
        FailureCode.PERFORMANCE_FAIL,
        FailureCode.ACTION_FAIL,
        FailureCode.TECHNICAL_FAIL,
    }

    @staticmethod
    def _clamp(value: float, low: float, high: float) -> float:
        return max(low, min(high, value))

    @classmethod
    def _lookdev_repair(
        cls,
        shot: CompiledShot,
        directive: RepairDirective,
        evidence: dict[str, Any],
        previous_frame_qc: dict[str, Any] | None,
    ) -> AppliedRepair:
        rendered = dict(evidence.get("rendered_frame_qc") or {})
        current_head = dict(rendered.get("head") or {})
        target_tail = dict(
            (previous_frame_qc or {}).get("tail") or {}
        )
        joined = " | ".join(directive.findings).upper()

        correction = 0.0
        current_luma = current_head.get("luma_mean")
        target_luma = target_tail.get("luma_mean")
        if (
            current_luma is not None
            and target_luma is not None
            and float(current_luma) > 1e-5
            and float(target_luma) > 1e-5
        ):
            correction = math.log2(
                float(target_luma) / float(current_luma)
            )
            correction = cls._clamp(correction, -1.5, 1.5)
        elif "UNDEREXPOSED" in joined:
            correction = 1.5
        elif "OVEREXPOSED" in joined:
            correction = -1.5
        elif "CUT_APPEARANCE" in joined:
            # Direction is unknown without frame metrics. Keep a small
            # conservative correction rather than inventing color changes.
            correction = 0.0

        before = float(shot.render_quality.exposure)
        after = cls._clamp(before + correction, -5.0, 5.0)
        shot.render_quality.exposure = after
        repair_meta = dict(shot.lighting_intent.get("auto_repair") or {})
        repair_meta.update(
            {
                "kind": "LOOKDEV",
                "exposure_before": before,
                "exposure_after": after,
                "exposure_delta": correction,
                "preserve_creative_intent": True,
            }
        )
        shot.lighting_intent["auto_repair"] = repair_meta
        return AppliedRepair(
            failure_code=directive.failure_code,
            owner=directive.owner,
            action=directive.action,
            changes={
                "render_quality.exposure": {
                    "before": before,
                    "after": after,
                }
            },
        )

    @classmethod
    def _camera_repair(
        cls,
        shot: CompiledShot,
        directive: RepairDirective,
    ) -> AppliedRepair:
        changes: dict[str, Any] = {}
        if shot.camera_takes:
            take = shot.camera_takes[0]
            before_lens = float(take.lens_mm)
            before_margin = float(take.framing_margin)
            take.lens_mm = cls._clamp(
                before_lens * 0.82,
                18.0,
                135.0,
            )
            take.framing_margin = cls._clamp(
                before_margin + 0.04,
                0.02,
                0.45,
            )
            take.horizontal_safe_margin = cls._clamp(
                float(take.horizontal_safe_margin) + 0.02,
                0.02,
                0.45,
            )
            take.vertical_safe_margin = cls._clamp(
                float(take.vertical_safe_margin) + 0.02,
                0.02,
                0.45,
            )
            take.motion_strength = max(
                0.0,
                float(take.motion_strength) * 0.85,
            )
            changes = {
                "camera.lens_mm": {
                    "before": before_lens,
                    "after": float(take.lens_mm),
                },
                "camera.framing_margin": {
                    "before": before_margin,
                    "after": float(take.framing_margin),
                },
            }
        return AppliedRepair(
            failure_code=directive.failure_code,
            owner=directive.owner,
            action=directive.action,
            changes=changes,
        )

    @classmethod
    def _performance_repair(
        cls,
        shot: CompiledShot,
        directive: RepairDirective,
    ) -> AppliedRepair:
        changed_actions = 0
        changed_gaze = 0
        for cue in shot.actions:
            before = float(cue.intensity)
            cue.intensity = cls._clamp(
                max(before, 0.85) * 1.12,
                0.0,
                1.5,
            )
            cue.speed = cls._clamp(
                float(cue.speed),
                0.75,
                1.25,
            )
            if cue.intensity != before:
                changed_actions += 1
        for cue in shot.gaze:
            if float(cue.intensity) < 1.0:
                cue.intensity = 1.0
                changed_gaze += 1
        return AppliedRepair(
            failure_code=directive.failure_code,
            owner=directive.owner,
            action=directive.action,
            changes={
                "action_intensity_cues": changed_actions,
                "gaze_intensity_cues": changed_gaze,
            },
        )

    def plan(
        self,
        shot: CompiledShot,
        directives: list[RepairDirective],
        *,
        repair_round: int,
        evidence: dict[str, Any] | None = None,
        previous_frame_qc: dict[str, Any] | None = None,
        preferred_strategies: dict[str, dict[str, Any]] | None = None,
    ) -> BlockRepairPlan:
        repaired = shot.model_copy(deep=True)
        applied: list[AppliedRepair] = []
        skipped: list[str] = []
        memory_hints: list[dict[str, Any]] = []
        evidence = evidence or {}
        preferred_strategies = preferred_strategies or {}

        ordered = sorted(
            directives,
            key=lambda directive: (
                0
                if (
                    preferred_strategies.get(
                        directive.failure_code.value,
                        {},
                    ).get("strategy")
                    == directive.action
                )
                else 1,
                directive.failure_code.value,
                directive.action,
            ),
        )

        for directive in ordered:
            hint = preferred_strategies.get(
                directive.failure_code.value
            )
            if hint:
                memory_hints.append(dict(hint))
            if not directive.retryable:
                skipped.append(
                    f"{directive.failure_code.value}:NON_RETRYABLE"
                )
                continue
            if directive.failure_code not in self.SUPPORTED:
                skipped.append(
                    f"{directive.failure_code.value}:UNSUPPORTED_LOCAL_REPAIR"
                )
                continue

            if directive.failure_code is FailureCode.LOOKDEV_FAIL:
                applied.append(
                    self._lookdev_repair(
                        repaired,
                        directive,
                        evidence,
                        previous_frame_qc,
                    )
                )
            elif directive.failure_code is FailureCode.CAMERA_INTENT_FAIL:
                applied.append(
                    self._camera_repair(
                        repaired,
                        directive,
                    )
                )
            elif directive.failure_code in {
                FailureCode.PERFORMANCE_FAIL,
                FailureCode.ACTION_FAIL,
            }:
                applied.append(
                    self._performance_repair(
                        repaired,
                        directive,
                    )
                )
            elif directive.failure_code is FailureCode.TECHNICAL_FAIL:
                applied.append(
                    AppliedRepair(
                        failure_code=directive.failure_code,
                        owner=directive.owner,
                        action=directive.action,
                        changes={
                            "rerender_same_contract": True,
                        },
                    )
                )

        return BlockRepairPlan(
            shot_id=shot.shot_id,
            repair_round=repair_round,
            supported=bool(applied),
            repaired_shot=repaired if applied else None,
            applied=applied,
            skipped=skipped,
            memory_hints=memory_hints,
        )
