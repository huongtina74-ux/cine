from __future__ import annotations

from types import SimpleNamespace

import pytest

from cinefactory.domain.enums import FailureCode
from cinefactory.production.contracts import RepairDirective
from cinefactory.studio.production_economics import (
    EconomicsAction,
    ProductionEconomicsController,
    ProductionShotClass,
)
from cinefactory.turbo.contracts import (
    ExecutionCostSample,
    ResourceClass,
    WorkState,
)
from cinefactory.turbo.store import TurboStore


def _shot(
    shot_id: str = "S01",
    *,
    duration: float = 2.0,
    shot_class: str | None = None,
    economics: dict | None = None,
):
    intent = {}
    if shot_class is not None:
        intent["production_class"] = shot_class
    if economics is not None:
        intent["economics"] = economics
    return SimpleNamespace(
        shot_id=shot_id,
        duration_seconds=duration,
        creative_intent=intent,
    )


def _directive(
    failure_code: FailureCode = FailureCode.LOOKDEV_FAIL,
) -> RepairDirective:
    return RepairDirective(
        shot_id="S01",
        failure_code=failure_code,
        owner="LIGHTING_COLOR_ENGINE",
        retryable=True,
        action="REBALANCE_LIGHTING_AND_COLOR",
        findings=["RENDERED_FRAME_UNDEREXPOSED:HEAD"],
    )


def test_shot_class_resolution_supports_explicit_and_complexity_aliases():
    controller = ProductionEconomicsController()
    assert (
        controller.resolve_shot_class(
            _shot(shot_class="HERO")
        )
        is ProductionShotClass.HERO
    )
    red = _shot()
    red.creative_intent["complexity"] = "RED"
    assert (
        controller.resolve_shot_class(red)
        is ProductionShotClass.A
    )
    background = _shot(shot_class="BG")
    assert (
        controller.resolve_shot_class(background)
        is ProductionShotClass.BACKGROUND
    )


def test_hero_budget_is_larger_than_background_budget():
    controller = ProductionEconomicsController()
    hero = controller.budget_for(
        _shot(shot_class="HERO", duration=3.0),
        global_max_repair_rounds=10,
    )
    background = controller.budget_for(
        _shot(shot_class="BACKGROUND", duration=3.0),
        global_max_repair_rounds=10,
    )
    assert hero.max_gpu_seconds > background.max_gpu_seconds
    assert hero.max_local_repairs > background.max_local_repairs
    assert hero.quality_floor > background.quality_floor


def test_background_stops_after_local_round_limit():
    controller = ProductionEconomicsController()
    shot = _shot(shot_class="BACKGROUND")
    decision = controller.decide_after_failure(
        shot=shot,
        directives=[_directive()],
        current_repair_round=1,
        gpu_seconds_spent=4.0,
        gpu_wasted_seconds=4.0,
        mean_gpu_attempt_seconds=4.0,
        project_gpu_seconds=4.0,
        project_gpu_budget=500.0,
        global_max_repair_rounds=5,
        memory_hints={},
        quality_score=0.4,
        local_repair_supported=True,
    )
    assert decision.action is EconomicsAction.STOP_BUDGET
    assert "LOCAL_REPAIR_ROUND_LIMIT" in decision.reason_codes
    directive = controller.decision_directive(decision)
    assert directive.failure_code is FailureCode.COST_POLICY_FAIL
    assert directive.action == "STOP_LOCAL_REPAIR_BUDGET"


def test_hero_switches_method_when_shot_gpu_budget_would_be_exceeded():
    controller = ProductionEconomicsController()
    shot = _shot(
        shot_class="HERO",
        economics={"max_gpu_seconds": 5.0},
    )
    decision = controller.decide_after_failure(
        shot=shot,
        directives=[_directive()],
        current_repair_round=0,
        gpu_seconds_spent=4.0,
        gpu_wasted_seconds=4.0,
        mean_gpu_attempt_seconds=4.0,
        project_gpu_seconds=4.0,
        project_gpu_budget=100.0,
        global_max_repair_rounds=5,
        memory_hints={},
        quality_score=0.4,
        local_repair_supported=True,
    )
    assert decision.action is EconomicsAction.SWITCH_METHOD
    assert decision.escalation_owner == "PRODUCTION_METHOD_PLANNER"
    assert "SHOT_GPU_BUDGET_EXHAUSTED" in decision.reason_codes
    directive = controller.decision_directive(decision)
    assert directive.failure_code is FailureCode.MODEL_CAPABILITY
    assert directive.action == "SWITCH_PRODUCTION_METHOD"


def test_poor_historical_strategy_switches_method_after_enough_samples():
    controller = ProductionEconomicsController()
    shot = _shot(shot_class="A")
    decision = controller.decide_after_failure(
        shot=shot,
        directives=[_directive()],
        current_repair_round=1,
        gpu_seconds_spent=10.0,
        gpu_wasted_seconds=10.0,
        mean_gpu_attempt_seconds=5.0,
        project_gpu_seconds=10.0,
        project_gpu_budget=1000.0,
        global_max_repair_rounds=5,
        memory_hints={
            "LOOKDEV_FAIL": {
                "strategy": "REBALANCE_LIGHTING_AND_COLOR",
                "attempts": 8,
                "success_rate": 0.05,
                "average_score": 0.3,
            }
        },
        quality_score=0.5,
        local_repair_supported=True,
    )
    assert decision.action is EconomicsAction.SWITCH_METHOD
    assert (
        "REPAIR_STRATEGY_LOW_HISTORICAL_SUCCESS"
        in decision.reason_codes
    )


def test_local_repair_continues_when_within_budget_and_strategy_is_viable():
    controller = ProductionEconomicsController()
    shot = _shot(shot_class="B")
    decision = controller.decide_after_failure(
        shot=shot,
        directives=[_directive()],
        current_repair_round=0,
        gpu_seconds_spent=3.0,
        gpu_wasted_seconds=3.0,
        mean_gpu_attempt_seconds=3.0,
        project_gpu_seconds=3.0,
        project_gpu_budget=1000.0,
        global_max_repair_rounds=2,
        memory_hints={},
        quality_score=0.6,
        local_repair_supported=True,
    )
    assert decision.action is EconomicsAction.REPAIR_LOCAL
    assert decision.allows_local_repair is True
    assert "LOCAL_REPAIR_WITHIN_BUDGET" in decision.reason_codes


def test_project_gpu_budget_stops_low_value_shot_before_next_repair():
    controller = ProductionEconomicsController()
    shot = _shot(shot_class="C")
    decision = controller.decide_after_failure(
        shot=shot,
        directives=[_directive()],
        current_repair_round=0,
        gpu_seconds_spent=3.0,
        gpu_wasted_seconds=3.0,
        mean_gpu_attempt_seconds=3.0,
        project_gpu_seconds=9.0,
        project_gpu_budget=10.0,
        global_max_repair_rounds=2,
        memory_hints={},
        quality_score=0.5,
        local_repair_supported=True,
    )
    assert decision.action is EconomicsAction.STOP_BUDGET
    assert "PROJECT_GPU_BUDGET_EXHAUSTED" in decision.reason_codes


def test_execution_cost_summary_exposes_first_pass_and_repair_kpis(tmp_path):
    store = TurboStore(tmp_path / "turbo.db")

    samples = [
        ExecutionCostSample(
            work_id="W1",
            project_id="P1",
            worker_id="gpu",
            kind="block.render",
            resource=ResourceClass.GPU,
            state=WorkState.QC_REJECTED,
            duration_seconds=4.0,
            output_units=24.0,
            accepted=False,
            repair_round=0,
        ),
        ExecutionCostSample(
            work_id="W2",
            project_id="P1",
            worker_id="gpu",
            kind="block.render.repair",
            resource=ResourceClass.GPU,
            state=WorkState.SUCCESS,
            duration_seconds=3.0,
            output_units=24.0,
            accepted=True,
            repair_round=1,
        ),
        ExecutionCostSample(
            work_id="W3",
            project_id="P1",
            worker_id="gpu",
            kind="block.render",
            resource=ResourceClass.GPU,
            state=WorkState.SUCCESS,
            duration_seconds=2.0,
            output_units=24.0,
            accepted=True,
            repair_round=0,
        ),
    ]
    for sample in samples:
        store.add_execution_cost(sample)

    summary = store.execution_cost_summary(project_id="P1")
    assert summary["render_samples"] == 3
    assert summary["first_pass_samples"] == 2
    assert summary["first_pass_accepted"] == 1
    assert summary["first_pass_yield"] == pytest.approx(0.5)
    assert summary["repair_samples"] == 1
    assert summary["repair_successes"] == 1
    assert summary["repair_success_rate"] == pytest.approx(1.0)
    assert summary["accepted_render_count"] == 2
    assert summary["gpu_seconds_per_accepted_render"] == pytest.approx(4.5)

    lineage = store.execution_cost_for_work_ids(["W1", "W2"])
    assert lineage["gpu_seconds"] == pytest.approx(7.0)
    assert lineage["gpu_wasted_seconds"] == pytest.approx(4.0)
    assert lineage["accepted_gpu_samples"] == 1
    assert lineage["rejected_gpu_samples"] == 1


def test_kpi_report_flags_low_first_pass_yield_and_high_gpu_waste():
    controller = ProductionEconomicsController()
    report = controller.kpi_report(
        {
            "render_samples": 10,
            "first_pass_yield": 0.30,
            "repair_success_rate": 0.40,
            "gpu_waste_ratio": 0.65,
            "gpu_seconds_per_accepted_render": 12.0,
        }
    )
    assert "LOW_FIRST_PASS_YIELD" in report["flags"]
    assert "HIGH_GPU_WASTE" in report["flags"]


def test_quality_floor_miss_routes_to_production_method_planner():
    from cinefactory.production.failure_router import FailureRouter

    directive = FailureRouter().classify(
        "S01",
        [
            "QUALITY_CLASS_FLOOR_MISS:HERO:"
            "score=0.81:required=0.92"
        ],
    )
    assert directive.failure_code is FailureCode.MODEL_CAPABILITY
    assert directive.owner == "PRODUCTION_METHOD_PLANNER"
    assert directive.retryable is False
    assert directive.action == "SWITCH_TO_HIGHER_QUALITY_METHOD"
