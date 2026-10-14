from __future__ import annotations

from cinefactory.production.contracts import (
    DailiesReport,
    ShotDailiesReport,
    TakeRecord,
)
from cinefactory.studio.contracts import CapabilityKind
from cinefactory.studio.planning import (
    CapabilityAssignment,
    PlanningMode,
    ProductionHandoff,
    SceneProductionPlan,
)
from cinefactory.studio.production_conference import (
    ConferenceLane,
    ProductionConferenceDecision,
    ProductionConferenceRoom,
)
from cinefactory.studio.production_memory import (
    MemoryAdviceAction,
    ProductionExperience,
    ProductionExperienceStore,
)


def _global(project_id: str, lane: ConferenceLane):
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


def _experience(
    *,
    exp_id: str,
    project_id: str,
    tool_id: str,
    lane: ConferenceLane,
    passed: bool,
    margin: float,
    repair: int,
    complexity: str = "MEDIUM",
    continuity: str = "MEDIUM",
):
    return ProductionExperience(
        experience_id=exp_id,
        project_id=project_id,
        scene_id="SC",
        tool_id=tool_id,
        lane=lane,
        specialized_objective="NONE",
        complexity_bucket=complexity,
        continuity_bucket=continuity,
        passed=passed,
        average_selected_score=max(0.0, min(1.0, 0.80 + margin)),
        worst_selected_score=max(0.0, min(1.0, 0.80 + margin)),
        qc_target=0.80,
        qc_margin=margin,
        max_repair_round=repair,
        shot_count=1,
    )


def _handoff(
    *,
    project_id: str,
    lane: ConferenceLane,
    complexity: float = 0.50,
    continuity: float = 0.50,
    tool_id: str = "blender",
):
    assignment = CapabilityAssignment(
        capability_kind=CapabilityKind.OFFLINE_3D,
        selected_capability_id="blender.local",
        selected_tool_id=tool_id,
        execution_ready=True,
        commercial_safe=True,
        score=0.9,
    )
    policy = next(
        item.policy
        for item in ProductionConferenceRoom.proposals(project_id)
        if item.lane is lane
    )
    scene = SceneProductionPlan(
        scene_id="SC_TARGET",
        shot_ids=["SH1"],
        purpose="test scene",
        render_candidate_kinds=[CapabilityKind.OFFLINE_3D],
        render_assignment=assignment,
        assignments=[assignment],
        scene_conference_lane=lane.value,
        scene_conference_policy=policy.model_dump(mode="json"),
        scene_conference_metrics={
            "complexity_score": complexity,
            "continuity_risk": continuity,
            "specialized_objective": None,
        },
    )
    return ProductionHandoff(
        project_id=project_id,
        strategy_id="STRAT",
        planning_mode=PlanningMode.CINEMATIC_3D,
        scene_plans=[scene],
        selected_tool_ids=[tool_id],
        executable=True,
    )


def test_memory_requires_three_matching_cross_project_samples(tmp_path):
    store = ProductionExperienceStore(tmp_path)
    for index in range(2):
        store.append(
            _experience(
                exp_id=f"EXP{index}",
                project_id=f"OLD{index}",
                tool_id="blender",
                lane=ConferenceLane.BALANCED,
                passed=False,
                margin=-0.10,
                repair=2,
            )
        )

    advice = store.advise(
        project_id="NEW",
        scene_id="SC_TARGET",
        tool_id="blender",
        current_lane=ConferenceLane.BALANCED,
        metrics={
            "complexity_score": 0.50,
            "continuity_risk": 0.50,
            "specialized_objective": None,
        },
        global_lane=ConferenceLane.BALANCED,
    )

    assert advice.action is MemoryAdviceAction.KEEP
    assert advice.sample_count == 2
    assert advice.confidence == 0.25


def test_weak_cross_episode_history_escalates_one_lane_and_keeps_tool(
    tmp_path,
):
    store = ProductionExperienceStore(tmp_path)
    for index in range(3):
        store.append(
            _experience(
                exp_id=f"WEAK{index}",
                project_id=f"OLD{index}",
                tool_id="blender",
                lane=ConferenceLane.BALANCED,
                passed=index == 0,
                margin=0.01,
                repair=1,
            )
        )

    handoff = _handoff(
        project_id="NEW",
        lane=ConferenceLane.BALANCED,
    )
    adjusted, application = store.apply_to_handoff(
        project_id="NEW",
        handoff=handoff,
        conference=_global(
            "NEW",
            ConferenceLane.BALANCED,
        ),
    )

    advice = application.advices[0]
    scene = adjusted.scene_plans[0]
    assert advice.action is MemoryAdviceAction.ESCALATE
    assert advice.applied is True
    assert advice.recommended_lane is ConferenceLane.QUALITY_FIRST
    assert scene.scene_conference_lane == "QUALITY_FIRST"
    assert scene.render_assignment.selected_tool_id == "blender"
    assert adjusted.selected_tool_ids == ["blender"]
    assert "cross_episode_memory_escalate" in scene.notes


def test_strong_low_risk_history_can_deescalate_one_lane(tmp_path):
    store = ProductionExperienceStore(tmp_path)
    for index in range(4):
        store.append(
            _experience(
                exp_id=f"STRONG{index}",
                project_id=f"OLD{index}",
                tool_id="blender",
                lane=ConferenceLane.BALANCED,
                passed=True,
                margin=0.16,
                repair=0,
                complexity="LOW",
                continuity="LOW",
            )
        )

    handoff = _handoff(
        project_id="NEW",
        lane=ConferenceLane.BALANCED,
        complexity=0.20,
        continuity=0.10,
    )
    adjusted, application = store.apply_to_handoff(
        project_id="NEW",
        handoff=handoff,
        conference=_global(
            "NEW",
            ConferenceLane.BALANCED,
        ),
    )

    advice = application.advices[0]
    assert advice.action is MemoryAdviceAction.DEESCALATE
    assert advice.applied is True
    assert adjusted.scene_plans[0].scene_conference_lane == "FAST_LEAN"
    assert (
        adjusted.scene_plans[0].render_assignment.selected_tool_id
        == "blender"
    )


def test_current_project_records_are_excluded_from_advice(tmp_path):
    store = ProductionExperienceStore(tmp_path)
    for index in range(3):
        store.append(
            _experience(
                exp_id=f"SELF{index}",
                project_id="CURRENT",
                tool_id="blender",
                lane=ConferenceLane.BALANCED,
                passed=False,
                margin=-0.20,
                repair=2,
            )
        )

    advice = store.advise(
        project_id="CURRENT",
        scene_id="SC_TARGET",
        tool_id="blender",
        current_lane=ConferenceLane.BALANCED,
        metrics={
            "complexity_score": 0.50,
            "continuity_risk": 0.50,
            "specialized_objective": None,
        },
        global_lane=ConferenceLane.BALANCED,
    )

    assert advice.sample_count == 0
    assert advice.action is MemoryAdviceAction.KEEP


def test_quality_first_global_policy_does_not_deescalate(tmp_path):
    store = ProductionExperienceStore(tmp_path)
    for index in range(4):
        store.append(
            _experience(
                exp_id=f"Q{index}",
                project_id=f"OLD{index}",
                tool_id="blender",
                lane=ConferenceLane.BALANCED,
                passed=True,
                margin=0.20,
                repair=0,
                complexity="LOW",
                continuity="LOW",
            )
        )

    advice = store.advise(
        project_id="NEW",
        scene_id="SC_TARGET",
        tool_id="blender",
        current_lane=ConferenceLane.BALANCED,
        metrics={
            "complexity_score": 0.20,
            "continuity_risk": 0.10,
            "specialized_objective": None,
        },
        global_lane=ConferenceLane.QUALITY_FIRST,
    )

    assert advice.action is MemoryAdviceAction.KEEP


def test_record_scene_persists_and_skips_diagnostic_backend(tmp_path):
    store = ProductionExperienceStore(tmp_path)
    dailies = DailiesReport(
        passed=True,
        shots=[
            ShotDailiesReport(
                shot_id="SH1",
                passed=True,
                selected_take_id="T1",
                selected_path="scene.mp4",
                selected_score=0.91,
                takes=[
                    TakeRecord(
                        take_id="T1",
                        shot_id="SH1",
                        path="scene.mp4",
                        technical_pass=True,
                        visual_pass=True,
                        aggregate_score=0.91,
                        repair_round=1,
                    )
                ],
            )
        ],
    )
    batch = {
        "scene_id": "SC1",
        "tool_id": "blender",
        "scene_lane": "BALANCED",
        "metrics": {
            "complexity_score": 0.52,
            "continuity_risk": 0.48,
            "specialized_objective": None,
        },
    }
    budget = {"qc_target": 0.80}

    experience = store.record_scene(
        project_id="PROJECT_A",
        batch=batch,
        budget=budget,
        dailies=dailies,
    )

    assert experience is not None
    assert experience.tool_id == "blender"
    assert experience.qc_margin == 0.11
    assert experience.max_repair_round == 1

    reopened = ProductionExperienceStore(tmp_path)
    items = reopened.list()
    assert len(items) == 1
    assert items[0].experience_id == experience.experience_id

    skipped = reopened.record_scene(
        project_id="PROJECT_A",
        batch={
            **batch,
            "tool_id": "diagnostic_slate",
        },
        budget=budget,
        dailies=dailies,
    )
    assert skipped is None
    assert len(reopened.list()) == 1
