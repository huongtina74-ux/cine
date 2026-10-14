from __future__ import annotations

from cinefactory.domain.enums import FailureCode
from cinefactory.production.contracts import RepairDirective


class FailureRouter:
    """Maps observed media failures to the smallest owning layer.

    The router intentionally does not turn story/director failures into generic rerenders.
    Those require upstream creative repair. Render-local failures can be retried with a
    constrained directive and the same canonical ShotSpec/keyframe.
    """

    def classify(self, shot_id: str, findings: list[str]) -> RepairDirective:
        upper = [x.upper() for x in findings]
        joined = " | ".join(upper)

        if any(k in joined for k in ("RIGHTS", "LICENSE", "CONSENT")):
            return RepairDirective(
                shot_id=shot_id, failure_code=FailureCode.RIGHTS_FAIL, owner="RIGHTS_ENGINE",
                retryable=False, action="STOP_AND_REVIEW_RIGHTS", findings=findings,
            )
        if any(k in joined for k in ("SECURITY", "PUBLIC_ENDPOINT", "UNTRUSTED_NODE")):
            return RepairDirective(
                shot_id=shot_id, failure_code=FailureCode.SECURITY_FAIL, owner="SECURITY_ENGINE",
                retryable=False, action="STOP_AND_OPEN_INCIDENT", findings=findings,
            )
        if any(
            k in joined
            for k in (
                "QUALITY_CLASS_FLOOR",
                "SHOT_CLASS_QUALITY",
                "QUALITY_TARGET_MISS",
            )
        ):
            return RepairDirective(
                shot_id=shot_id,
                failure_code=FailureCode.MODEL_CAPABILITY,
                owner="PRODUCTION_METHOD_PLANNER",
                retryable=False,
                action="SWITCH_TO_HIGHER_QUALITY_METHOD",
                prompt_directive=(
                    "Hard QC may pass, but measured craft score is below the "
                    "approved shot-class quality floor. Preserve creative intent "
                    "and select a more capable qualified production method."
                ),
                invalidates=["VIDEO_TAKE", "METHOD_SELECTION"],
                findings=findings,
            )
        if any(k in joined for k in ("FACE", "IDENTITY", "CHARACTER_DRIFT")):
            return RepairDirective(
                shot_id=shot_id, failure_code=FailureCode.IDENTITY_DRIFT, owner="ASSET_ENGINE",
                retryable=True, action="RENDER_WITH_STRONGER_CANONICAL_REFERENCES",
                prompt_directive="Preserve the canonical face, hair, body proportions and wardrobe exactly; do not reinterpret identity.",
                invalidates=["VIDEO_TAKE"], findings=findings,
            )
        if any(k in joined for k in ("COSTUME", "PROP", "EYELINE", "SCREEN_DIRECTION", "CONTINUITY")):
            return RepairDirective(
                shot_id=shot_id, failure_code=FailureCode.CONTINUITY_FAIL, owner="CONTINUITY_ENGINE",
                retryable=True, action="RENDER_FROM_LOCKED_ENTRY_STATE",
                prompt_directive="Strictly preserve entry-state costume, props, eyeline, screen direction, positions and lighting anchors.",
                invalidates=["VIDEO_TAKE"], findings=findings,
            )
        if any(k in joined for k in ("CAMERA", "FRAMING", "LENS", "COMPOSITION")):
            return RepairDirective(
                shot_id=shot_id, failure_code=FailureCode.CAMERA_INTENT_FAIL, owner="CINEMATOGRAPHY_ENGINE",
                retryable=True, action="RENDER_WITH_CAMERA_CONSTRAINTS",
                prompt_directive="Do not invent camera behavior. Match the approved framing, lens intent, camera side, focus target and movement timing exactly.",
                invalidates=["VIDEO_TAKE"], findings=findings,
            )
        if any(k in joined for k in ("PERFORMANCE", "EXPRESSION", "GESTURE", "ACTING")):
            return RepairDirective(
                shot_id=shot_id, failure_code=FailureCode.PERFORMANCE_FAIL, owner="PERFORMANCE_ENGINE",
                retryable=True, action="RENDER_WITH_PERFORMANCE_CONSTRAINTS",
                prompt_directive="Prioritize the approved playable objective, restrained body behavior, eye behavior and micro-expression; avoid generic emoting.",
                invalidates=["VIDEO_TAKE"], findings=findings,
            )
        if any(k in joined for k in ("ACTION", "PHYSICS", "LIMB", "CONTACT")):
            return RepairDirective(
                shot_id=shot_id, failure_code=FailureCode.ACTION_FAIL, owner="BLOCKING_ACTION_ENGINE",
                retryable=True, action="SIMPLIFY_OR_REASSERT_ACTION_LEDGER",
                prompt_directive="Execute only the approved primary physical action with readable contact, direction and end state; no extra actions.",
                invalidates=["VIDEO_TAKE"], findings=findings,
            )
        if any(
            k in joined
            for k in (
                "EXPOSURE",
                "UNDEREXPOSED",
                "OVEREXPOSED",
                "HIGHLIGHT",
                "SHADOW_CLIP",
                "COLOR_WARNING",
                "COLOR_DRIFT",
                "CUT_APPEARANCE",
                "LOOKDEV",
                "LIGHTING_APPEARANCE",
                "LOW_CONTRAST",
            )
        ):
            return RepairDirective(
                shot_id=shot_id,
                failure_code=FailureCode.LOOKDEV_FAIL,
                owner="LIGHTING_COLOR_ENGINE",
                retryable=True,
                action="REBALANCE_LIGHTING_AND_COLOR",
                prompt_directive=(
                    "Preserve approved story/camera/performance. Repair only "
                    "exposure, light balance, highlight/shadow clipping and "
                    "same-scene color continuity against the accepted reference."
                ),
                invalidates=["VIDEO_TAKE"],
                findings=findings,
            )
        if any(k in joined for k in ("FLICKER", "DECODE", "BLACK_FRAME", "FROZEN", "MISSING", "TECHNICAL", "TEMPORAL")):
            return RepairDirective(
                shot_id=shot_id, failure_code=FailureCode.TECHNICAL_FAIL, owner="RENDER_ENGINE",
                retryable=True, action="RERENDER_LOCAL_WITH_NEW_SEED",
                prompt_directive="Preserve the approved shot while avoiding temporal artifacts, flicker, frozen frames and malformed anatomy.",
                invalidates=["VIDEO_TAKE"], findings=findings,
            )
        if any(k in joined for k in ("STORY_BEAT", "NARRATIVE", "MEANING", "AUDIENCE_ENDPOINT")):
            return RepairDirective(
                shot_id=shot_id, failure_code=FailureCode.CAMERA_INTENT_FAIL, owner="DIRECTOR_ENGINE",
                retryable=False, action="RETURN_TO_DIRECTOR_PLAN", invalidates=["SHOT_SPEC", "KEYFRAME", "VIDEO_TAKE"], findings=findings,
            )
        return RepairDirective(
            shot_id=shot_id, failure_code=FailureCode.UNKNOWN, owner="QC_SUPERVISOR",
            retryable=False, action="MANUAL_OR_AGENT_REVIEW_REQUIRED", findings=findings,
        )


    def classify_all(
        self,
        shot_id: str,
        findings: list[str],
    ) -> list[RepairDirective]:
        """Return the minimal distinct repair owners for a failed shot.

        Rendered identity drift can be caused by a global lookdev/exposure shift.
        When that co-occurs with explicit lookdev evidence and there is no
        structural/canonical identity failure, suppress the redundant asset
        rerender and repair lookdev first.
        """
        if not findings:
            return [
                self.classify(
                    shot_id,
                    ["UNKNOWN_QC_FAILURE"],
                )
            ]

        upper = [str(item).upper() for item in findings]
        joined = " | ".join(upper)
        has_lookdev = any(
            token in joined
            for token in (
                "EXPOSURE",
                "UNDEREXPOSED",
                "OVEREXPOSED",
                "HIGHLIGHT",
                "SHADOW_CLIP",
                "COLOR_WARNING",
                "COLOR_DRIFT",
                "CUT_APPEARANCE",
                "LOOKDEV",
                "LIGHTING_APPEARANCE",
                "LOW_CONTRAST",
            )
        )
        has_structural_identity = any(
            token in joined
            for token in (
                "IDENTITY_STRUCTURE",
                "RIG_STYLE_MISMATCH",
                "REQUIRED_PARTS_MISSING",
                "CANONICAL_IDENTITY",
                "FACE_IDENTITY",
                "CHARACTER_DRIFT",
            )
        )

        directives: dict[
            tuple[FailureCode, str, str],
            RepairDirective,
        ] = {}
        for finding in findings:
            upper_finding = str(finding).upper()
            if (
                "RENDERED_IDENTITY_DRIFT" in upper_finding
                and has_lookdev
                and not has_structural_identity
            ):
                # Appearance drift is plausibly explained by a measured
                # whole-shot lookdev failure. Repair the smallest owning
                # layer first instead of invalidating canonical assets.
                continue

            directive = self.classify(
                shot_id,
                [str(finding)],
            )
            key = (
                directive.failure_code,
                directive.owner,
                directive.action,
            )
            existing = directives.get(key)
            if existing is None:
                directives[key] = directive
            else:
                existing.findings.extend(
                    item
                    for item in directive.findings
                    if item not in existing.findings
                )

        if not directives:
            # This occurs when all identity-proxy findings were suppressed by
            # a co-occurring lookdev root cause. Route the full evidence once.
            directive = self.classify(shot_id, findings)
            if (
                directive.failure_code is FailureCode.IDENTITY_DRIFT
                and has_lookdev
                and not has_structural_identity
            ):
                directive = self.classify(
                    shot_id,
                    [
                        item
                        for item in findings
                        if "RENDERED_IDENTITY_DRIFT"
                        not in str(item).upper()
                    ]
                    or ["LOOKDEV_APPEARANCE_DRIFT"]
                )
            directives[
                (
                    directive.failure_code,
                    directive.owner,
                    directive.action,
                )
            ] = directive

        priority = {
            FailureCode.RIGHTS_FAIL: 0,
            FailureCode.SECURITY_FAIL: 1,
            FailureCode.IDENTITY_DRIFT: 2,
            FailureCode.CONTINUITY_FAIL: 3,
            FailureCode.CAMERA_INTENT_FAIL: 4,
            FailureCode.PERFORMANCE_FAIL: 5,
            FailureCode.ACTION_FAIL: 6,
            FailureCode.LOOKDEV_FAIL: 7,
            FailureCode.TECHNICAL_FAIL: 8,
            FailureCode.UNKNOWN: 99,
        }
        return sorted(
            directives.values(),
            key=lambda item: (
                priority.get(item.failure_code, 50),
                item.owner,
                item.action,
            ),
        )
