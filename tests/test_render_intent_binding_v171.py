from __future__ import annotations

from pathlib import Path

import pytest

from cinefactory.autopilot.scaffold import LocalScaffoldPlanner
from cinefactory.block_animation.assembler import (
    EpisodeAssembler,
    EpisodeAssemblyError,
)
from cinefactory.block_animation.contracts import (
    BlenderAnimationJob,
    GazeCue,
)
from cinefactory.block_animation.execution import BlockExecutionPlanner
from cinefactory.block_animation.runtime import BlockAnimationRuntime
from cinefactory.domain.models import ActionBeat
from cinefactory.studio.block_adapter import (
    BlockProductionStyle,
    CompanyToBlockAdapter,
)
from cinefactory.studio.craft_execution import (
    CreativeIntentGraph,
    LightingColorIntentPlan,
    PerformanceDirectionBeat,
    PerformanceDirectionPlan,
    SceneCreativeIntent,
    ShotCreativeIntent,
    ShotLightingColorIntent,
)


ROOT = Path(__file__).resolve().parents[1]


def _professional_block_inputs():
    planner = LocalScaffoldPlanner()
    story = planner.story(
        "A Minecraft hero notices a rival and points out the hidden clue."
    )
    script = planner.script(story)
    director = planner.director(script)
    shots = planner.shots(script, director)
    shot = shots[1].model_copy(deep=True)

    c01 = shot.entry_state.characters["C01"]
    c02 = c01.model_copy(
        update={
            "character_id": "C02",
            "position": "right-midground",
            "eyeline": "C01",
            "emotion": "angry",
        }
    )
    shot.entry_state.characters["C02"] = c02
    shot.exit_state.characters["C02"] = c02.model_copy(deep=True)
    shot.entry_state.characters["C01"].eyeline = "C02"
    shot.exit_state.characters["C01"].eyeline = "C02"
    shot.performance["C02"] = shot.performance["C01"].model_copy(
        update={
            "objective": "challenge the hero",
            "action_verb": "push",
            "outward_mask": "angry",
        }
    )
    shot.action_beats = [
        ActionBeat(
            actor="C01",
            action="points toward the rival",
            target="C02",
            start_second=0.4,
            end_second=1.2,
        )
    ]

    performance = PerformanceDirectionPlan(
        project_id="P_BIND",
        beats=[
            PerformanceDirectionBeat(
                shot_id=shot.shot_id,
                scene_id=shot.scene_id,
                subject_id="C01",
                objective="make the rival notice the clue",
                action_verb="point",
                gaze_target="C02",
                expression_intent="surprised recognition",
                gesture_intent="point clearly",
                reaction_trigger="reveal",
            ),
            PerformanceDirectionBeat(
                shot_id=shot.shot_id,
                scene_id=shot.scene_id,
                subject_id="C02",
                objective="challenge the hero",
                action_verb="push",
                gaze_target="C01",
                expression_intent="angry resistance",
                gesture_intent="push back",
            ),
        ],
    )

    intent = ShotCreativeIntent(
        shot_id=shot.shot_id,
        scene_id=shot.scene_id,
        beat_id="B02",
        scene_purpose="turn suspicion into confrontation",
        beat_purpose="pressure",
        shot_purpose=shot.narrative_purpose,
        audience_know="the rival has noticed the clue",
        audience_feel="tension",
        audience_endpoint=shot.audience_endpoint,
        performance_objectives={
            "C01": "make the rival notice the clue",
            "C02": "challenge the hero",
        },
        camera_purpose=shot.camera.narrative_purpose,
        edit_intent=shot.edit_intent or "cut after reaction",
        sound_intent="protect reaction and physical contact",
        lighting_intent=["motivated-soft", "DAY"],
        continuity_contract={},
    )
    graph = CreativeIntentGraph(
        project_id="P_BIND",
        scenes=[
            SceneCreativeIntent(
                scene_id=shot.scene_id,
                purpose="turn suspicion into confrontation",
                audience_know="the rival has noticed the clue",
                audience_feel="tension",
                beat_ids=["B02"],
                shot_ids=[shot.shot_id],
            )
        ],
        shots=[intent],
    )
    lighting = LightingColorIntentPlan(
        project_id="P_BIND",
        shots=[
            ShotLightingColorIntent(
                shot_id=shot.shot_id,
                scene_id=shot.scene_id,
                narrative_purpose=shot.narrative_purpose,
                light_state="motivated-soft",
                time_of_day="DAY",
            )
        ],
    )
    return shot, performance, graph, lighting


def test_professional_intent_binds_to_executable_block_cues(tmp_path):
    shot, performance, graph, lighting = _professional_block_inputs()
    episode = CompanyToBlockAdapter().adapt_episode(
        project_id="P_BIND",
        episode_id="EP_BIND",
        title="Intent binding",
        shots=[shot],
        style=BlockProductionStyle.MINECRAFT,
        width=320,
        height=180,
        quality_profile="preview",
        creative_intent_graph=graph,
        performance_direction=performance,
        lighting_color_intent=lighting,
    )
    block_shot = episode.shots[0]

    assert episode.metadata["craft_intent_bound"] is True
    assert {cue.clip_id for cue in block_shot.actions} >= {
        "point",
        "push",
    }
    assert {cue.expression_id for cue in block_shot.expressions} >= {
        "surprised",
        "angry",
    }
    assert {
        (cue.actor_id, cue.target_actor_id)
        for cue in block_shot.gaze
    } >= {("C01", "C02"), ("C02", "C01")}
    assert any(cue.trigger == "reveal" for cue in block_shot.reactions)
    assert block_shot.camera.pattern_id == "fidelity_reaction"
    assert block_shot.creative_intent["beat_id"] == "B02"
    assert len(block_shot.performance_directives) == 2
    assert block_shot.lighting_intent["light_state"] == "motivated-soft"

    compiled = EpisodeAssembler.from_root(ROOT).compile(
        episode,
        output_dir=tmp_path,
    )
    plan = BlockExecutionPlanner.plan(
        BlenderAnimationJob(
            project_id=compiled.project_id,
            episode_id=compiled.episode_id,
            shot=compiled.shots[0],
            output_path=str(tmp_path / "bound.mp4"),
        )
    )
    assert len(plan["gaze"]) == 2
    assert plan["creative_intent"]["beat_id"] == "B02"
    assert len(plan["performance_directives"]) == 2
    assert plan["lighting_intent"]["light_state"] == "motivated-soft"


def test_unknown_gaze_target_fails_episode_assembly():
    shot, _, _, _ = _professional_block_inputs()
    episode = CompanyToBlockAdapter().adapt_episode(
        project_id="P_BAD_GAZE",
        episode_id="EP_BAD_GAZE",
        title="Bad gaze",
        shots=[shot],
        style=BlockProductionStyle.MINECRAFT,
        width=320,
        height=180,
        quality_profile="preview",
    )
    episode.shots[0].gaze = [
        GazeCue(
            actor_id="C01",
            target_actor_id="NOT_AN_ACTOR",
            start_seconds=0,
            end_seconds=0.5,
        )
    ]
    with pytest.raises(EpisodeAssemblyError) as exc:
        EpisodeAssembler.from_root(ROOT).compile(episode)
    assert any(
        finding.code == "UNKNOWN_GAZE_TARGET"
        for finding in exc.value.report.findings
    )


def test_runtime_fails_closed_on_worker_geometry_qc(tmp_path):
    shot, _, _, _ = _professional_block_inputs()
    episode = CompanyToBlockAdapter().adapt_episode(
        project_id="P_GEOM",
        episode_id="EP_GEOM",
        title="Geometry failure",
        shots=[shot],
        style=BlockProductionStyle.MINECRAFT,
        width=320,
        height=180,
        quality_profile="preview",
    )
    compiled = EpisodeAssembler.from_root(ROOT).compile(
        episode,
        output_dir=tmp_path,
    )
    output = tmp_path / "geometry_fail.mp4"
    job = BlenderAnimationJob(
        project_id=compiled.project_id,
        episode_id=compiled.episode_id,
        shot=compiled.shots[0],
        output_path=str(output),
    )

    class Worker:
        pid = 1
        last_result = {
            "geometry_qc": {
                "passed": False,
                "blockers": ["C01:TARGET_OCCLUDED"],
            }
        }

        def execute_animation(self, _job):
            output.write_bytes(b"not-a-real-video")
            return str(output)

    runtime = BlockAnimationRuntime(tmp_path)
    with pytest.raises(RuntimeError, match="geometry QC failed"):
        runtime.render_and_qc(Worker(), job)


def test_dailies_evidence_never_invents_identity_or_continuity_scores():
    from cinefactory.studio.block_production import BlockAnimationProducer

    evidence = BlockAnimationProducer._evidence_scores(
        {
            "geometry_qc": {
                "passed": True,
                "warnings": ["VERIFY_HEADROOM"],
            },
            "gaze_debug": [
                {"actor_id": "C01", "applied": True},
                {
                    "actor_id": "C02",
                    "applied": False,
                    "reason": "HEAD_CONTROL_UNAVAILABLE",
                },
            ],
            "lighting_debug": {"intent_bound": True},
            "creative_intent_bound": True,
            "performance_directive_count": 2,
            "visual_qc": {"passed": True, "findings": []},
        }
    )

    assert evidence["identity_score"] is None
    assert evidence["continuity_score"] is None
    assert evidence["camera_score"] == pytest.approx(0.95)
    assert evidence["performance_score"] == pytest.approx(0.5)
    assert evidence["aggregate_score"] == pytest.approx(0.725)
    assert evidence["execution_conformance_passed"] is False
    assert (
        evidence["score_semantics"]["identity_score"]
        == "NOT_MEASURED"
    )
    assert (
        evidence["score_semantics"]["camera_score"]
        == "GEOMETRY_FRAMING_OCCLUSION_CONFORMANCE"
    )


def test_block_producer_dailies_fail_when_requested_gaze_is_not_applied(
    tmp_path,
):
    from cinefactory.studio.block_production import BlockAnimationProducer

    shot, performance, graph, lighting = _professional_block_inputs()
    episode = CompanyToBlockAdapter().adapt_episode(
        project_id="P_DAILIES",
        episode_id="EP_DAILIES",
        title="Evidence dailies",
        shots=[shot],
        style=BlockProductionStyle.MINECRAFT,
        width=320,
        height=180,
        quality_profile="preview",
        creative_intent_graph=graph,
        performance_direction=performance,
        lighting_color_intent=lighting,
    )

    class FakeWorker:
        pid = 42

        def start(self):
            return None

        def close(self):
            return None

    class FakeRuntime:
        def render_and_qc(self, worker, job):
            output = Path(job.output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"fake-render")
            return {
                "path": str(output),
                "geometry_qc": {
                    "passed": True,
                    "warnings": [],
                    "blockers": [],
                },
                "gaze_debug": [
                    {
                        "actor_id": "C01",
                        "target_actor_id": "C02",
                        "applied": True,
                    },
                    {
                        "actor_id": "C02",
                        "target_actor_id": "C01",
                        "applied": False,
                        "reason": "HEAD_CONTROL_UNAVAILABLE",
                    },
                ],
                "lighting_debug": {
                    "light_state": "motivated-soft",
                    "intent_bound": True,
                },
                "creative_intent_bound": True,
                "performance_directive_count": 2,
                "visual_qc": {
                    "passed": True,
                    "findings": [],
                },
            }

    producer = BlockAnimationProducer(
        ROOT,
        worker=FakeWorker(),
    )
    producer.runtime = FakeRuntime()
    report = producer.produce(
        episode,
        project_root=tmp_path,
        render_preview=True,
    )

    assert report.passed is False
    take = report.shots[0].takes[0]
    assert take.technical_pass is True
    assert take.visual_pass is False
    assert take.identity_score is None
    assert take.continuity_score is None
    assert take.camera_score == 1.0
    assert take.performance_score == pytest.approx(0.5)
    assert take.evidence["creative_intent_bound"] is True
    assert any(
        item.startswith("GAZE_NOT_APPLIED:C02")
        for item in take.findings
    )
    assert report.shots[0].selected_take_id is None


def test_block_producer_dailies_keep_measured_semantics_on_success(
    tmp_path,
):
    from cinefactory.studio.block_production import BlockAnimationProducer

    shot, performance, graph, lighting = _professional_block_inputs()
    episode = CompanyToBlockAdapter().adapt_episode(
        project_id="P_DAILIES_OK",
        episode_id="EP_DAILIES_OK",
        title="Evidence dailies success",
        shots=[shot],
        style=BlockProductionStyle.MINECRAFT,
        width=320,
        height=180,
        quality_profile="preview",
        creative_intent_graph=graph,
        performance_direction=performance,
        lighting_color_intent=lighting,
    )

    class FakeWorker:
        pid = 43

        def start(self):
            return None

        def close(self):
            return None

    class FakeRuntime:
        def render_and_qc(self, worker, job):
            output = Path(job.output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"fake-render")
            return {
                "path": str(output),
                "geometry_qc": {
                    "passed": True,
                    "warnings": [],
                    "blockers": [],
                },
                "gaze_debug": [
                    {"actor_id": "C01", "applied": True},
                    {"actor_id": "C02", "applied": True},
                ],
                "lighting_debug": {
                    "light_state": "motivated-soft",
                    "intent_bound": True,
                },
                "creative_intent_bound": True,
                "performance_directive_count": 2,
                "visual_qc": {
                    "passed": True,
                    "findings": [],
                },
            }

    producer = BlockAnimationProducer(
        ROOT,
        worker=FakeWorker(),
    )
    producer.runtime = FakeRuntime()
    report = producer.produce(
        episode,
        project_root=tmp_path,
        render_preview=True,
    )

    assert report.passed is True
    take = report.shots[0].takes[0]
    assert take.identity_score is None
    assert take.continuity_score is None
    assert take.performance_score == 1.0
    assert take.camera_score == 1.0
    assert (
        take.score_semantics["performance_score"]
        == "GAZE_EXECUTION_CONFORMANCE"
    )
    assert (
        take.score_semantics["aggregate_score"]
        == "MEAN_OF_MEASURED_EXECUTION_CONFORMANCE_SCORES"
    )


def test_dailies_evidence_scores_never_fake_unmeasured_dimensions():
    from cinefactory.studio.block_production import BlockAnimationProducer

    scores = BlockAnimationProducer._evidence_scores(
        {
            "geometry_qc": {
                "passed": True,
                "warnings": [],
            },
            "gaze_debug": [
                {"actor_id": "C01", "applied": True},
                {"actor_id": "C02", "applied": True},
            ],
            "lighting_debug": {
                "intent_bound": True,
            },
            "creative_intent_bound": True,
            "performance_directive_count": 2,
            "visual_qc": {"passed": True},
        }
    )
    assert scores["camera_score"] == 1.0
    assert scores["performance_score"] == 1.0
    assert scores["identity_score"] is None
    assert scores["continuity_score"] is None
    assert scores["score_semantics"]["identity_score"] == "NOT_MEASURED"
    assert scores["score_semantics"]["continuity_score"] == "NOT_MEASURED"
    assert scores["execution_conformance_passed"] is True


def test_dailies_evidence_scores_penalize_failed_gaze_execution():
    from cinefactory.studio.block_production import BlockAnimationProducer

    scores = BlockAnimationProducer._evidence_scores(
        {
            "geometry_qc": {
                "passed": True,
                "warnings": [],
            },
            "gaze_debug": [
                {"actor_id": "C01", "applied": True},
                {
                    "actor_id": "C02",
                    "applied": False,
                    "reason": "HEAD_CONTROL_UNAVAILABLE",
                },
            ],
        }
    )
    assert scores["performance_score"] == 0.5
    assert scores["execution_conformance_passed"] is False
    assert any(
        finding.startswith("GAZE_NOT_APPLIED:C02")
        for finding in scores["findings"]
    )
