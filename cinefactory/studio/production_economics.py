from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from cinefactory.domain.enums import FailureCode
from cinefactory.production.contracts import RepairDirective


class ProductionShotClass(StrEnum):
    HERO = "HERO"
    A = "A"
    B = "B"
    C = "C"
    BACKGROUND = "BACKGROUND"


class EconomicsAction(StrEnum):
    ACCEPT = "ACCEPT"
    REPAIR_LOCAL = "REPAIR_LOCAL"
    SWITCH_METHOD = "SWITCH_METHOD"
    ESCALATE_UPSTREAM = "ESCALATE_UPSTREAM"
    STOP_BUDGET = "STOP_BUDGET"


class ShotEconomicsProfile(BaseModel):
    shot_class: ProductionShotClass
    base_gpu_seconds: float = Field(gt=0)
    gpu_seconds_per_output_second: float = Field(gt=0)
    max_local_repairs: int = Field(ge=0, le=10)
    quality_floor: float = Field(ge=0.0, le=1.0)
    min_strategy_samples: int = Field(default=3, ge=1)
    min_strategy_success_rate: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
    )
    max_repair_waste_ratio: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
    )

    def gpu_budget(self, duration_seconds: float) -> float:
        return max(
            self.base_gpu_seconds,
            self.base_gpu_seconds
            + self.gpu_seconds_per_output_second
            * max(0.0, float(duration_seconds)),
        )


class ProductionEconomicsPolicy(BaseModel):
    profiles: dict[
        ProductionShotClass,
        ShotEconomicsProfile,
    ] = Field(default_factory=dict)
    min_project_samples_for_yield_gate: int = Field(
        default=5,
        ge=1,
    )
    first_pass_yield_floor: float = Field(
        default=0.55,
        ge=0.0,
        le=1.0,
    )
    project_gpu_budget_multiplier: float = Field(
        default=1.15,
        gt=0.0,
    )

    @classmethod
    def professional_default(cls) -> "ProductionEconomicsPolicy":
        rows = [
            ShotEconomicsProfile(
                shot_class=ProductionShotClass.HERO,
                base_gpu_seconds=120.0,
                gpu_seconds_per_output_second=60.0,
                max_local_repairs=4,
                quality_floor=0.92,
                min_strategy_samples=4,
                min_strategy_success_rate=0.18,
                max_repair_waste_ratio=0.92,
            ),
            ShotEconomicsProfile(
                shot_class=ProductionShotClass.A,
                base_gpu_seconds=90.0,
                gpu_seconds_per_output_second=45.0,
                max_local_repairs=3,
                quality_floor=0.88,
                min_strategy_samples=4,
                min_strategy_success_rate=0.22,
                max_repair_waste_ratio=0.88,
            ),
            ShotEconomicsProfile(
                shot_class=ProductionShotClass.B,
                base_gpu_seconds=60.0,
                gpu_seconds_per_output_second=30.0,
                max_local_repairs=2,
                quality_floor=0.82,
                min_strategy_samples=3,
                min_strategy_success_rate=0.25,
                max_repair_waste_ratio=0.82,
            ),
            ShotEconomicsProfile(
                shot_class=ProductionShotClass.C,
                base_gpu_seconds=40.0,
                gpu_seconds_per_output_second=20.0,
                max_local_repairs=1,
                quality_floor=0.76,
                min_strategy_samples=3,
                min_strategy_success_rate=0.30,
                max_repair_waste_ratio=0.75,
            ),
            ShotEconomicsProfile(
                shot_class=ProductionShotClass.BACKGROUND,
                base_gpu_seconds=25.0,
                gpu_seconds_per_output_second=12.0,
                max_local_repairs=1,
                quality_floor=0.70,
                min_strategy_samples=2,
                min_strategy_success_rate=0.35,
                max_repair_waste_ratio=0.70,
            ),
        ]
        return cls(
            profiles={row.shot_class: row for row in rows}
        )


class ShotBudget(BaseModel):
    shot_id: str
    shot_class: ProductionShotClass
    max_gpu_seconds: float = Field(gt=0)
    max_local_repairs: int = Field(ge=0)
    quality_floor: float = Field(ge=0.0, le=1.0)
    min_strategy_samples: int = Field(ge=1)
    min_strategy_success_rate: float = Field(
        ge=0.0,
        le=1.0,
    )
    max_repair_waste_ratio: float = Field(
        ge=0.0,
        le=1.0,
    )


class EconomicsDecision(BaseModel):
    shot_id: str
    shot_class: ProductionShotClass
    action: EconomicsAction
    reason_codes: list[str] = Field(default_factory=list)
    gpu_seconds_spent: float = Field(default=0.0, ge=0.0)
    gpu_seconds_remaining: float = Field(default=0.0, ge=0.0)
    projected_next_gpu_seconds: float = Field(
        default=0.0,
        ge=0.0,
    )
    project_gpu_seconds: float = Field(default=0.0, ge=0.0)
    project_gpu_budget: float | None = Field(default=None, gt=0.0)
    current_repair_round: int = Field(default=0, ge=0)
    allowed_repair_rounds: int = Field(default=0, ge=0)
    quality_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    quality_floor: float = Field(ge=0.0, le=1.0)
    repair_waste_ratio: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )
    strategy_hint: dict[str, Any] = Field(default_factory=dict)
    escalation_owner: str | None = None
    recommended_method_policy: str | None = None

    @property
    def allows_local_repair(self) -> bool:
        return self.action is EconomicsAction.REPAIR_LOCAL


class ProductionEconomicsController:
    """Quality-preserving budget controller for autonomous production.

    Hard QC is authoritative. This controller never accepts a failed take to
    save compute. It only decides whether another local repair is economically
    justified or the shot must stop/switch/escalate.
    """

    def __init__(
        self,
        policy: ProductionEconomicsPolicy | None = None,
    ) -> None:
        self.policy = (
            policy
            or ProductionEconomicsPolicy.professional_default()
        )

    @staticmethod
    def resolve_shot_class(
        shot: Any,
        *,
        episode_metadata: dict[str, Any] | None = None,
    ) -> ProductionShotClass:
        metadata = episode_metadata or {}
        shot_id = str(getattr(shot, "shot_id", ""))
        maps = metadata.get("shot_classes") or {}
        raw = maps.get(shot_id) if isinstance(maps, dict) else None

        intent = getattr(shot, "creative_intent", {}) or {}
        if raw is None:
            for key in (
                "production_class",
                "shot_class",
                "quality_class",
                "quality_tier",
            ):
                if intent.get(key):
                    raw = intent.get(key)
                    break

        if raw is None:
            complexity = str(
                intent.get("complexity")
                or intent.get("shot_complexity")
                or ""
            ).upper()
            raw = {
                "HERO": "HERO",
                "RED": "A",
                "YELLOW": "B",
                "GREEN": "C",
            }.get(complexity)

        if raw is None:
            return ProductionShotClass.B

        normalized = str(raw).strip().upper()
        aliases = {
            "HERO": ProductionShotClass.HERO,
            "A": ProductionShotClass.A,
            "RED": ProductionShotClass.A,
            "B": ProductionShotClass.B,
            "YELLOW": ProductionShotClass.B,
            "C": ProductionShotClass.C,
            "GREEN": ProductionShotClass.C,
            "BG": ProductionShotClass.BACKGROUND,
            "BACKGROUND": ProductionShotClass.BACKGROUND,
            "EXTRA": ProductionShotClass.BACKGROUND,
        }
        return aliases.get(normalized, ProductionShotClass.B)

    def budget_for(
        self,
        shot: Any,
        *,
        episode_metadata: dict[str, Any] | None = None,
        global_max_repair_rounds: int | None = None,
    ) -> ShotBudget:
        shot_class = self.resolve_shot_class(
            shot,
            episode_metadata=episode_metadata,
        )
        profile = self.policy.profiles[shot_class]
        max_repairs = profile.max_local_repairs
        if global_max_repair_rounds is not None:
            max_repairs = min(
                max_repairs,
                max(0, int(global_max_repair_rounds)),
            )

        intent = getattr(shot, "creative_intent", {}) or {}
        overrides = intent.get("economics") or {}
        duration = float(
            getattr(shot, "duration_seconds", 0.0) or 0.0
        )
        max_gpu_seconds = float(
            overrides.get(
                "max_gpu_seconds",
                profile.gpu_budget(duration),
            )
        )
        max_repairs = int(
            overrides.get(
                "max_local_repairs",
                max_repairs,
            )
        )
        quality_floor = float(
            overrides.get(
                "quality_floor",
                profile.quality_floor,
            )
        )
        return ShotBudget(
            shot_id=str(getattr(shot, "shot_id", "")),
            shot_class=shot_class,
            max_gpu_seconds=max(0.001, max_gpu_seconds),
            max_local_repairs=max(0, max_repairs),
            quality_floor=max(
                0.0,
                min(1.0, quality_floor),
            ),
            min_strategy_samples=profile.min_strategy_samples,
            min_strategy_success_rate=(
                profile.min_strategy_success_rate
            ),
            max_repair_waste_ratio=(
                profile.max_repair_waste_ratio
            ),
        )

    def project_gpu_budget(
        self,
        shots: list[Any],
        *,
        episode_metadata: dict[str, Any] | None = None,
        global_max_repair_rounds: int | None = None,
    ) -> float | None:
        metadata = episode_metadata or {}
        economics = metadata.get("economics") or {}
        override = economics.get("max_project_gpu_seconds")
        if override is not None:
            return max(0.001, float(override))
        if not shots:
            return None
        total = sum(
            self.budget_for(
                shot,
                episode_metadata=metadata,
                global_max_repair_rounds=(
                    global_max_repair_rounds
                ),
            ).max_gpu_seconds
            for shot in shots
        )
        return total * self.policy.project_gpu_budget_multiplier

    @staticmethod
    def _strategy_hint(
        directives: list[RepairDirective],
        memory_hints: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        candidates = []
        for directive in directives:
            hint = memory_hints.get(
                directive.failure_code.value
            )
            if hint:
                candidates.append(
                    {
                        "failure_code": (
                            directive.failure_code.value
                        ),
                        **dict(hint),
                    }
                )
        if not candidates:
            return {}
        return max(
            candidates,
            key=lambda row: (
                int(row.get("attempts", 0) or 0),
                float(row.get("success_rate", 0.0) or 0.0),
                float(row.get("average_score", 0.0) or 0.0),
            ),
        )

    def decide_after_failure(
        self,
        *,
        shot: Any,
        directives: list[RepairDirective],
        current_repair_round: int,
        gpu_seconds_spent: float,
        gpu_wasted_seconds: float,
        mean_gpu_attempt_seconds: float,
        project_gpu_seconds: float,
        project_gpu_budget: float | None,
        global_max_repair_rounds: int,
        episode_metadata: dict[str, Any] | None = None,
        memory_hints: dict[str, dict[str, Any]] | None = None,
        quality_score: float | None = None,
        local_repair_supported: bool = True,
    ) -> EconomicsDecision:
        budget = self.budget_for(
            shot,
            episode_metadata=episode_metadata,
            global_max_repair_rounds=global_max_repair_rounds,
        )
        hints = memory_hints or {}
        hint = self._strategy_hint(directives, hints)
        projected = max(
            0.001,
            float(mean_gpu_attempt_seconds or 0.0),
        )
        if projected <= 0.001:
            duration = float(
                getattr(shot, "duration_seconds", 1.0)
                or 1.0
            )
            projected = max(
                0.25,
                min(
                    budget.max_gpu_seconds,
                    duration * 2.0,
                ),
            )
        remaining = max(
            0.0,
            budget.max_gpu_seconds
            - max(0.0, float(gpu_seconds_spent)),
        )
        waste_ratio = (
            max(0.0, float(gpu_wasted_seconds))
            / max(0.001, float(gpu_seconds_spent))
            if gpu_seconds_spent > 0
            else 0.0
        )

        reasons: list[str] = []
        action = EconomicsAction.REPAIR_LOCAL
        owner: str | None = None
        method: str | None = None

        high_value = budget.shot_class in {
            ProductionShotClass.HERO,
            ProductionShotClass.A,
        }
        medium_value = budget.shot_class is ProductionShotClass.B

        if not directives:
            action = EconomicsAction.ESCALATE_UPSTREAM
            owner = "PRODUCTION_SUPERVISOR"
            reasons.append("NO_REPAIR_DIRECTIVE")
        elif not local_repair_supported:
            action = EconomicsAction.ESCALATE_UPSTREAM
            owner = "PRODUCTION_METHOD_PLANNER"
            reasons.append("LOCAL_REPAIR_UNSUPPORTED")
        elif (
            project_gpu_budget is not None
            and project_gpu_seconds + projected
            > project_gpu_budget
        ):
            if high_value:
                action = EconomicsAction.ESCALATE_UPSTREAM
                owner = "PRODUCER_FINANCE_REVIEW"
                method = "QUALITY_FIRST_ALTERNATIVE"
            else:
                action = EconomicsAction.STOP_BUDGET
                owner = "PRODUCER"
            reasons.append("PROJECT_GPU_BUDGET_EXHAUSTED")
        elif (
            gpu_seconds_spent + projected
            > budget.max_gpu_seconds
        ):
            if high_value:
                action = EconomicsAction.SWITCH_METHOD
                owner = "PRODUCTION_METHOD_PLANNER"
                method = "QUALITY_FIRST_ALTERNATIVE"
            elif medium_value:
                action = EconomicsAction.ESCALATE_UPSTREAM
                owner = "PRODUCTION_SUPERVISOR"
                method = "BALANCED_ALTERNATIVE"
            else:
                action = EconomicsAction.STOP_BUDGET
                owner = "PRODUCER"
                method = "FAST_LEAN_OR_DROP"
            reasons.append("SHOT_GPU_BUDGET_EXHAUSTED")
        elif (
            current_repair_round
            >= budget.max_local_repairs
        ):
            if high_value:
                action = EconomicsAction.SWITCH_METHOD
                owner = "PRODUCTION_METHOD_PLANNER"
                method = "QUALITY_FIRST_ALTERNATIVE"
            elif medium_value:
                action = EconomicsAction.ESCALATE_UPSTREAM
                owner = "PRODUCTION_SUPERVISOR"
                method = "BALANCED_ALTERNATIVE"
            else:
                action = EconomicsAction.STOP_BUDGET
                owner = "PRODUCER"
            reasons.append("LOCAL_REPAIR_ROUND_LIMIT")
        elif (
            current_repair_round >= 2
            and waste_ratio
            > budget.max_repair_waste_ratio
        ):
            if high_value or medium_value:
                action = EconomicsAction.SWITCH_METHOD
                owner = "PRODUCTION_METHOD_PLANNER"
                method = (
                    "QUALITY_FIRST_ALTERNATIVE"
                    if high_value
                    else "BALANCED_ALTERNATIVE"
                )
            else:
                action = EconomicsAction.STOP_BUDGET
                owner = "PRODUCER"
            reasons.append("REPAIR_GPU_WASTE_TOO_HIGH")
        elif hint:
            attempts = int(hint.get("attempts", 0) or 0)
            success_rate = float(
                hint.get("success_rate", 0.0) or 0.0
            )
            if (
                attempts >= budget.min_strategy_samples
                and success_rate
                < budget.min_strategy_success_rate
            ):
                if high_value or medium_value:
                    action = EconomicsAction.SWITCH_METHOD
                    owner = "PRODUCTION_METHOD_PLANNER"
                    method = (
                        "QUALITY_FIRST_ALTERNATIVE"
                        if high_value
                        else "BALANCED_ALTERNATIVE"
                    )
                else:
                    action = EconomicsAction.STOP_BUDGET
                    owner = "PRODUCER"
                reasons.append(
                    "REPAIR_STRATEGY_LOW_HISTORICAL_SUCCESS"
                )

        if (
            action is EconomicsAction.REPAIR_LOCAL
            and quality_score is not None
            and quality_score < budget.quality_floor
        ):
            reasons.append("QUALITY_BELOW_CLASS_FLOOR")

        if action is EconomicsAction.REPAIR_LOCAL:
            owner = owner or "LOCAL_REPAIR_ENGINE"
            reasons.append("LOCAL_REPAIR_WITHIN_BUDGET")

        return EconomicsDecision(
            shot_id=budget.shot_id,
            shot_class=budget.shot_class,
            action=action,
            reason_codes=reasons,
            gpu_seconds_spent=max(
                0.0,
                float(gpu_seconds_spent),
            ),
            gpu_seconds_remaining=remaining,
            projected_next_gpu_seconds=projected,
            project_gpu_seconds=max(
                0.0,
                float(project_gpu_seconds),
            ),
            project_gpu_budget=project_gpu_budget,
            current_repair_round=max(
                0,
                int(current_repair_round),
            ),
            allowed_repair_rounds=budget.max_local_repairs,
            quality_score=quality_score,
            quality_floor=budget.quality_floor,
            repair_waste_ratio=max(
                0.0,
                min(1.0, waste_ratio),
            ),
            strategy_hint=hint,
            escalation_owner=owner,
            recommended_method_policy=method,
        )

    def decision_directive(
        self,
        decision: EconomicsDecision,
    ) -> RepairDirective:
        if decision.action is EconomicsAction.SWITCH_METHOD:
            return RepairDirective(
                shot_id=decision.shot_id,
                failure_code=FailureCode.MODEL_CAPABILITY,
                owner=(
                    decision.escalation_owner
                    or "PRODUCTION_METHOD_PLANNER"
                ),
                retryable=False,
                action="SWITCH_PRODUCTION_METHOD",
                prompt_directive=(
                    "Local repair is no longer economically justified. "
                    "Preserve approved creative intent and choose a different "
                    "qualified production method/toolchain within the class "
                    "quality target."
                ),
                invalidates=["VIDEO_TAKE", "METHOD_SELECTION"],
                findings=list(decision.reason_codes),
            )
        if decision.action is EconomicsAction.STOP_BUDGET:
            return RepairDirective(
                shot_id=decision.shot_id,
                failure_code=FailureCode.COST_POLICY_FAIL,
                owner=decision.escalation_owner or "PRODUCER",
                retryable=False,
                action="STOP_LOCAL_REPAIR_BUDGET",
                prompt_directive=(
                    "Do not accept the failed take. Local repair budget is "
                    "exhausted; producer must drop, redesign, or explicitly "
                    "authorize a new budget."
                ),
                invalidates=["VIDEO_TAKE"],
                findings=list(decision.reason_codes),
            )
        return RepairDirective(
            shot_id=decision.shot_id,
            failure_code=FailureCode.COST_POLICY_FAIL,
            owner=(
                decision.escalation_owner
                or "PRODUCTION_SUPERVISOR"
            ),
            retryable=False,
            action="ESCALATE_PRODUCTION_ECONOMICS",
            prompt_directive=(
                "Hard QC remains failed. Escalate this shot for upstream "
                "method, budget, or creative decision; do not accept it."
            ),
            invalidates=["VIDEO_TAKE"],
            findings=list(decision.reason_codes),
        )

    def kpi_report(
        self,
        execution_metrics: dict[str, Any],
    ) -> dict[str, Any]:
        metrics = dict(execution_metrics or {})
        samples = int(
            metrics.get("render_samples", 0) or 0
        )
        first_pass_yield = float(
            metrics.get("first_pass_yield", 0.0) or 0.0
        )
        flags: list[str] = []
        if (
            samples
            >= self.policy.min_project_samples_for_yield_gate
            and first_pass_yield
            < self.policy.first_pass_yield_floor
        ):
            flags.append("LOW_FIRST_PASS_YIELD")
        if float(
            metrics.get("gpu_waste_ratio", 0.0) or 0.0
        ) > 0.50:
            flags.append("HIGH_GPU_WASTE")
        return {
            "first_pass_yield": first_pass_yield,
            "repair_success_rate": float(
                metrics.get("repair_success_rate", 0.0)
                or 0.0
            ),
            "method_switch_success_rate": float(
                metrics.get(
                    "method_switch_success_rate",
                    0.0,
                )
                or 0.0
            ),
            "method_switch_samples": int(
                metrics.get(
                    "method_switch_samples",
                    0,
                )
                or 0
            ),
            "gpu_waste_ratio": float(
                metrics.get("gpu_waste_ratio", 0.0)
                or 0.0
            ),
            "gpu_seconds_per_accepted_render": (
                metrics.get(
                    "gpu_seconds_per_accepted_render"
                )
            ),
            "flags": flags,
        }
