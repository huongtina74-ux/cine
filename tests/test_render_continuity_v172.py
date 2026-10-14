from __future__ import annotations

from cinefactory.block_animation.render_continuity import (
    RenderContinuityEvaluator,
)
from cinefactory.studio.block_production import BlockAnimationProducer


def _state(
    *,
    shot_id: str,
    scene_id: str = "SC1",
    x: float = 0.0,
    yaw: float = 0.0,
    identity: str = "ID_A",
    key: float = 1000.0,
    prop_parent: str = "HAND",
):
    return {
        "shot_id": shot_id,
        "scene_id": scene_id,
        "actors": {
            "C01": {
                "identity_signature": identity,
                "start": {
                    "root_location": [x, 0.0, 0.0],
                    "root_rotation": [0.0, 0.0, yaw],
                },
                "end": {
                    "root_location": [x, 0.0, 0.0],
                    "root_rotation": [0.0, 0.0, yaw],
                },
            }
        },
        "props": {
            "P1": {
                "parent": prop_parent,
                "start_location": [x, 0.0, 1.0],
                "end_location": [x, 0.0, 1.0],
            }
        },
        "lighting": {
            "light_state": "soft",
            "time_of_day": "DAY",
            "key_energy": key,
            "fill_energy": 500.0,
            "rim_energy": 600.0,
            "world_strength": 0.5,
        },
    }


def test_stable_same_scene_render_continuity_passes():
    previous = _state(shot_id="S1")
    current = _state(shot_id="S2")
    result = RenderContinuityEvaluator().compare(previous, current)
    assert result.measured is True
    assert result.passed is True
    assert result.score == 1.0
    assert result.findings == []


def test_large_actor_position_jump_fails_same_scene_continuity():
    previous = _state(shot_id="S1", x=0.0)
    current = _state(shot_id="S2", x=1.2)
    result = RenderContinuityEvaluator().compare(previous, current)
    assert result.measured is True
    assert result.passed is False
    assert any(
        "ROOT_POSITION" in finding
        for finding in result.findings
    )


def test_scene_transition_is_not_falsely_scored_as_continuity_failure():
    previous = _state(shot_id="S1", scene_id="SC1")
    current = _state(shot_id="S2", scene_id="SC2", x=5.0)
    result = RenderContinuityEvaluator().compare(previous, current)
    assert result.measured is False
    assert result.passed is True
    assert result.score is None
    assert result.findings == [
        "RENDER_CONTINUITY_NOT_MEASURED:SCENE_TRANSITION"
    ]


def test_identity_signature_change_is_hard_continuity_failure():
    previous = _state(shot_id="S1", identity="ID_A")
    current = _state(shot_id="S2", identity="ID_B")
    result = RenderContinuityEvaluator().compare(previous, current)
    assert result.passed is False
    assert any(
        check.code == "IDENTITY_SIGNATURE"
        and check.hard_failure
        for check in result.checks
    )


def test_large_lighting_drift_fails_when_intent_is_unchanged():
    previous = _state(shot_id="S1", key=1000.0)
    current = _state(shot_id="S2", key=1500.0)
    result = RenderContinuityEvaluator().compare(previous, current)
    assert result.passed is False
    assert any(
        check.code == "LIGHT_KEY_ENERGY"
        and check.hard_failure
        for check in result.checks
    )


def test_producer_scores_use_3d_performance_and_adjacent_continuity():
    continuity = RenderContinuityEvaluator().compare(
        _state(shot_id="S1"),
        _state(shot_id="S2"),
    )
    scores = BlockAnimationProducer._evidence_scores(
        {
            "geometry_qc": {
                "passed": True,
                "warnings": [],
            },
            "identity_qc": {
                "passed": True,
                "score": 1.0,
                "blockers": [],
            },
            "performance_qc": {
                "passed": True,
                "score": 0.9,
                "warnings": [],
                "blockers": [],
            },
            "render_state": _state(shot_id="S2"),
            "creative_intent_bound": True,
        },
        continuity=continuity,
    )
    assert scores["performance_score"] == 0.9
    assert scores["continuity_score"] == 1.0
    assert scores["camera_score"] == 1.0
    assert scores["identity_score"] is None
    assert (
        scores["score_semantics"]["performance_score"]
        == "MEASURED_3D_ACTION_GAZE_CONTACT_BALANCE_CONFORMANCE"
    )
    assert (
        scores["score_semantics"]["continuity_score"]
        == "ADJACENT_RENDER_STATE_CONFORMANCE"
    )
    assert scores["execution_conformance_passed"] is True


def test_continuity_failure_blocks_professional_execution_score():
    continuity = RenderContinuityEvaluator().compare(
        _state(shot_id="S1", x=0.0),
        _state(shot_id="S2", x=1.2),
    )
    scores = BlockAnimationProducer._evidence_scores(
        {
            "geometry_qc": {"passed": True, "warnings": []},
            "performance_qc": {
                "passed": True,
                "score": 1.0,
                "warnings": [],
                "blockers": [],
            },
        },
        continuity=continuity,
    )
    assert scores["continuity_score"] is not None
    assert scores["execution_conformance_passed"] is False
    assert any(
        "CONTINUITY_BLOCKER" in finding
        for finding in scores["findings"]
    )
