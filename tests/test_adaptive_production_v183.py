from __future__ import annotations

from cinefactory.production.contracts import (
    DailiesReport,
    ShotDailiesReport,
    TakeRecord,
)
from cinefactory.studio.adaptive_production import (
    AdaptationAction,
    AdaptiveProductionSupervisor,
)
from cinefactory.studio.production_conference import (
    ConferenceLane,
    ProductionConferenceDecision,
    ProductionConferenceRoom,
)


def _global(
    project_id: str,
    lane: ConferenceLane,
) -> ProductionConferenceDecision:
    proposals = ProductionConferenceRoom.proposals(project_id)
    selected = next(
        item for item in proposals if item.lane is lane
    )
    return ProductionConferenceDecision(
        project_id=project_id,
        proposals=proposals,
        selected_proposal_id=selected.proposal_id,
        selected_lane=selected.lane,
        selected_policy=selected.policy,
        proposal_scores={
            item.proposal_id: (
                0.9 if item.lane is lane else 0.7
            )
            for item in proposals
        },
        executable=True,
    )


def _policy(
    project_id: str,
    lane: ConferenceLane,
) -> dict:
    proposal = next(
        item
        for item in ProductionConferenceRoom.proposals(project_id)
        if item.lane is lane
    )
    return proposal.policy.model_dump(mode="json")


def _batch(
    project_id: str,
    *,
    scene_id: str,
    tool_id: str,
    lane: ConferenceLane,
    risk: float,
    complexity: float,
    specialized: str | None = None,
) -> dict:
    return {
        "scene_id": scene_id,
        "tool_id": tool_id,
        "scene_lane": lane.value,
        "policy": _policy(project_id, lane),
        "metrics": {
            "continuity_risk": risk,
            "complexity_score": complexity,
            "specialized_objective": specialized,
        },
        "shots": [],
    }


def _dailies(
    *,
    score: float,
    repair_round: int = 0,
    passed: bool = True,
) -> DailiesReport:
    take = TakeRecord(
        take_id="T1",
        shot_id="SH1",
        path="take.mp4" if passed else "",
        technical_pass=passed,
        visual_pass=passed,
        aggregate_score=score if passed else 0.0,
        repair_round=repair_round,
    )
    shot = ShotDailiesReport(
        shot_id="SH1",
        passed=passed,
        selected_take_id="T1" if passed else None,
        selected_path="take.mp4" if passed else None,
        selected_score=score if passed else 0.0,
        takes=[take],
        findings=[] if passed else ["QC_FAILED"],
    )
    return DailiesReport(
        passed=passed,
        shots=[shot],
        findings=[] if passed else ["NO_ACCEPTED_TAKE:SH1"],
    )


def test_weak_margin_or_repair_escalates_pending_same_backend_scene():
    project_id = "STU_ADAPT_ESC"
    supervisor = AdaptiveProductionSupervisor(
        project_id=project_id,
        global_decision=_global(
            project_id,
            ConferenceLane.BALANCED,
        ),
    )
    current = _batch(
        project_id,
        scene_id="SC_A",
        tool_id="comfyui",
        lane=ConferenceLane.FAST_LEAN,
        risk=0.2,
        complexity=0.2,
    )
    pending = _batch(
        project_id,
        scene_id="SC_B",
        tool_id="comfyui",
        lane=ConferenceLane.FAST_LEAN,
        risk=0.55,
        complexity=0.55,
    )

    changes = supervisor.observe_and_rebudget(
        batch=current,
        budget={"qc_target": 0.74},
        dailies=_dailies(
            score=0.77,
            repair_round=1,
        ),
        remaining_batches=[pending],
    )

    assert len(changes) == 1
    assert changes[0].action is AdaptationAction.ESCALATE
    assert changes[0].previous_lane == "FAST_LEAN"
    assert changes[0].new_lane == "BALANCED"
    assert pending["scene_lane"] == "BALANCED"
    assert pending["tool_id"] == "comfyui"
    assert (
        pending["policy"]["qc_target"]
        > current["policy"]["qc_target"]
    )


def test_strong_margin_deescalates_only_low_risk_pending_scene():
    project_id = "STU_ADAPT_DOWN"
    supervisor = AdaptiveProductionSupervisor(
        project_id=project_id,
        global_decision=_global(
            project_id,
            ConferenceLane.BALANCED,
        ),
    )
    current = _batch(
        project_id,
        scene_id="SC_A",
        tool_id="blender",
        lane=ConferenceLane.BALANCED,
        risk=0.25,
        complexity=0.25,
    )
    low_risk = _batch(
        project_id,
        scene_id="SC_B",
        tool_id="blender",
        lane=ConferenceLane.BALANCED,
        risk=0.10,
        complexity=0.20,
    )
    high_risk = _batch(
        project_id,
        scene_id="SC_C",
        tool_id="blender",
        lane=ConferenceLane.BALANCED,
        risk=0.72,
        complexity=0.80,
    )

    changes = supervisor.observe_and_rebudget(
        batch=current,
        budget={"qc_target": 0.80},
        dailies=_dailies(score=0.95),
        remaining_batches=[low_risk, high_risk],
    )

    assert len(changes) == 1
    assert changes[0].action is AdaptationAction.DEESCALATE
    assert changes[0].target_scene_id == "SC_B"
    assert low_risk["scene_lane"] == "FAST_LEAN"
    assert high_risk["scene_lane"] == "BALANCED"
    assert low_risk["tool_id"] == "blender"
    assert high_risk["tool_id"] == "blender"


def test_quality_first_global_policy_never_deescalates():
    project_id = "STU_ADAPT_QUALITY"
    supervisor = AdaptiveProductionSupervisor(
        project_id=project_id,
        global_decision=_global(
            project_id,
            ConferenceLane.QUALITY_FIRST,
        ),
    )
    current = _batch(
        project_id,
        scene_id="SC_A",
        tool_id="blender",
        lane=ConferenceLane.QUALITY_FIRST,
        risk=0.10,
        complexity=0.10,
    )
    pending = _batch(
        project_id,
        scene_id="SC_B",
        tool_id="blender",
        lane=ConferenceLane.BALANCED,
        risk=0.05,
        complexity=0.10,
    )

    changes = supervisor.observe_and_rebudget(
        batch=current,
        budget={"qc_target": 0.86},
        dailies=_dailies(score=1.0),
        remaining_batches=[pending],
    )

    assert changes == []
    assert pending["scene_lane"] == "BALANCED"


def test_adaptation_never_crosses_backend_boundary():
    project_id = "STU_ADAPT_BACKEND"
    supervisor = AdaptiveProductionSupervisor(
        project_id=project_id,
        global_decision=_global(
            project_id,
            ConferenceLane.BALANCED,
        ),
    )
    current = _batch(
        project_id,
        scene_id="SC_A",
        tool_id="comfyui",
        lane=ConferenceLane.FAST_LEAN,
        risk=0.20,
        complexity=0.20,
    )
    other_backend = _batch(
        project_id,
        scene_id="SC_B",
        tool_id="blender",
        lane=ConferenceLane.FAST_LEAN,
        risk=0.70,
        complexity=0.80,
    )

    changes = supervisor.observe_and_rebudget(
        batch=current,
        budget={"qc_target": 0.74},
        dailies=_dailies(
            score=0.40,
            repair_round=2,
            passed=False,
        ),
        remaining_batches=[other_backend],
    )

    assert changes == []
    assert other_backend["tool_id"] == "blender"
    assert other_backend["scene_lane"] == "FAST_LEAN"
    assert supervisor.report.outcomes[0].passed is False
