from __future__ import annotations

from pathlib import Path

from cinefactory.block_animation.contracts import (
    ActorPlacement,
    CameraIntent,
    ShotPerformanceSpec,
)
from cinefactory.studio.dialogue_performance import (
    DialogueLineIntent,
    DialoguePerformanceEngine,
    DialogueRole,
)


def _lines():
    return [
        DialogueLineIntent(
            line_id="L1",
            speaker_id="A",
            listener_ids=["B"],
            text="Why did you take it?",
            objective="force B to answer",
            action_verb="accuse",
            subtext="A already suspects the truth",
            emotion="angry",
            start_seconds=0.25,
            end_seconds=1.45,
            reaction_delay_seconds=0.18,
        ),
        DialogueLineIntent(
            line_id="L2",
            speaker_id="B",
            listener_ids=["A"],
            text="I did not take it.",
            objective="make A doubt the accusation",
            action_verb="reveal",
            subtext="B is hiding fear",
            emotion="surprised",
            start_seconds=1.75,
            end_seconds=3.05,
            reaction_delay_seconds=0.16,
        ),
    ]


def test_dialogue_engine_compiles_speaker_listener_semantics():
    engine = DialoguePerformanceEngine()
    compiled = engine.compile(
        shot_id="S_DIALOGUE",
        duration_seconds=3.6,
        actor_ids=["A", "B"],
        lines=_lines(),
    )

    assert compiled.qc.passed is True
    assert compiled.qc.score == 1.0
    assert len(compiled.directives) == 4

    speakers = [
        item
        for item in compiled.directives
        if item.role is DialogueRole.SPEAKER
    ]
    listeners = [
        item
        for item in compiled.directives
        if item.role is DialogueRole.LISTENER
    ]
    assert {item.actor_id for item in speakers} == {"A", "B"}
    assert {item.actor_id for item in listeners} == {"A", "B"}
    assert all(item.gaze_target for item in compiled.directives)
    assert any(item.clip_id == "point" for item in compiled.actions)
    assert {item.expression_id for item in compiled.expressions} >= {
        "angry",
        "surprised",
    }
    assert {item.trigger for item in compiled.reactions} >= {
        "accusation",
        "reveal",
    }


def test_dialogue_engine_rejects_unknown_listener_and_bad_range():
    engine = DialoguePerformanceEngine()
    lines = [
        DialogueLineIntent(
            line_id="L_BAD",
            speaker_id="A",
            listener_ids=["C"],
            text="Listen.",
            objective="warn",
            action_verb="warn",
            emotion="angry",
            start_seconds=1.0,
            end_seconds=2.8,
        )
    ]
    compiled = engine.compile(
        shot_id="S_BAD",
        duration_seconds=2.0,
        actor_ids=["A", "B"],
        lines=lines,
    )
    assert compiled.qc.passed is False
    assert "L_BAD:DIALOGUE_TIMING_OUT_OF_RANGE" in compiled.qc.blockers
    assert "L_BAD:UNKNOWN_LISTENER:C" in compiled.qc.blockers


def test_apply_to_shot_adds_executable_cues_and_semantic_contract():
    engine = DialoguePerformanceEngine()
    compiled = engine.compile(
        shot_id="S01",
        duration_seconds=3.6,
        actor_ids=["A", "B"],
        lines=_lines(),
    )
    shot = ShotPerformanceSpec(
        shot_id="S01",
        scene_template_id="minecraft_classroom",
        duration_seconds=3.6,
        actors=[
            ActorPlacement(
                actor_id="A",
                rig_id="mc_a",
                marker="hero_a",
            ),
            ActorPlacement(
                actor_id="B",
                rig_id="mc_b",
                marker="hero_b",
            ),
        ],
        camera=CameraIntent(
            purpose="two character confrontation",
            targets=["A", "B"],
        ),
        creative_intent={"scene_id": "SC_DIALOGUE"},
    )
    enriched = engine.apply_to_shot(
        shot,
        compiled,
    )
    assert enriched.creative_intent[
        "semantic_performance_required"
    ] is True
    assert enriched.creative_intent[
        "dialogue_performance_qc"
    ]["passed"] is True
    assert len(enriched.performance_directives) == 4
    assert len(enriched.gaze) >= 4
    assert len(enriched.expressions) == 2
    assert len(enriched.reactions) == 2


def test_app_context_shares_dialogue_performance_engine():
    from cinefactory.appctx import build_context

    root = Path(__file__).resolve().parents[1]
    ctx = build_context(root)
    assert (
        ctx.dialogue_performance
        is ctx.studio.professional_company.dialogue_performance
    )


def test_execution_plan_preserves_resolved_reactions(tmp_path):
    from cinefactory.block_animation.assembler import EpisodeAssembler
    from cinefactory.block_animation.contracts import (
        BlenderAnimationJob,
        EpisodeSpec,
    )
    from cinefactory.block_animation.execution import BlockExecutionPlanner

    engine = DialoguePerformanceEngine()
    base = ShotPerformanceSpec(
        shot_id="S01",
        scene_template_id="minecraft_classroom",
        duration_seconds=3.6,
        actors=[
            ActorPlacement(
                actor_id="A",
                rig_id="mc_a",
                marker="hero_a",
            ),
            ActorPlacement(
                actor_id="B",
                rig_id="mc_b",
                marker="hero_b",
            ),
        ],
        camera=CameraIntent(
            purpose="fidelity_group",
            pattern_id="fidelity_group",
            targets=["A", "B"],
        ),
        creative_intent={"scene_id": "SC_DIALOGUE"},
    )
    compilation = engine.compile(
        shot_id="S01",
        duration_seconds=3.6,
        actor_ids=["A", "B"],
        lines=_lines(),
    )
    shot = engine.apply_to_shot(base, compilation)
    episode = EpisodeSpec(
        project_id="P",
        episode_id="E",
        title="dialogue",
        fps=24,
        width=320,
        height=180,
        quality_profile="preview",
        shots=[shot],
    )
    compiled = EpisodeAssembler.from_root(
        Path(__file__).resolve().parents[1]
    ).compile(episode)
    cshot = compiled.shots[0]
    assert cshot.reactions
    plan = BlockExecutionPlanner.plan(
        BlenderAnimationJob(
            project_id="P",
            episode_id="E",
            shot=cshot,
            output_path=str(tmp_path / "out.mp4"),
            render_preview=True,
        )
    )
    assert plan["reactions"]
    assert {row["trigger"] for row in plan["reactions"]} >= {
        "accusation",
        "reveal",
    }


def test_multi_character_request_uses_stronger_identity_sampling():
    from cinefactory.studio.cross_backend_video import (
        CameraIntentContract,
        CanonicalBlockVideoRequest,
        ReferenceConditioning,
        ReferenceSourceKind,
        WAN21_FUN_INPAINT_PROFILE,
        CrossBackendVideoService,
    )

    request = CanonicalBlockVideoRequest(
        project_id="P",
        episode_id="E",
        shot_id="S",
        backend_id=WAN21_FUN_INPAINT_PROFILE.backend_id,
        normalizer_id=WAN21_FUN_INPAINT_PROFILE.normalizer_id,
        workflow_id=WAN21_FUN_INPAINT_PROFILE.workflow_id,
        workflow_version=WAN21_FUN_INPAINT_PROFILE.workflow_version,
        model_id=WAN21_FUN_INPAINT_PROFILE.model_id,
        model_revision=WAN21_FUN_INPAINT_PROFILE.model_revision,
        prompt="A left, B right",
        negative_prompt="identity swap",
        width=320,
        height=176,
        fps=16,
        frame_count=17,
        duration_seconds=1.0625,
        seed=1,
        reference=ReferenceConditioning(
            required=True,
            source_kind=ReferenceSourceKind.IMAGE,
            source_path="ref.png",
            source_sha256="x",
            staged_filename="ref.png",
            actor_ids=["A", "B"],
            rig_ids=["mc_a", "mc_b"],
        ),
        camera=CameraIntentContract(),
        recurring_identity_required=True,
        semantic_performance_required=False,
        source_visual_style="MINECRAFT",
        scene_id="SC",
        output_path="out.mp4",
        render_preview=True,
        sampling_denoise=0.82,
    )
    service = CrossBackendVideoService(
        Path(__file__).resolve().parents[1],
        executors=None,
    )
    workflow = service.build_workflow(request)
    assert workflow["8"]["inputs"]["denoise"] == 0.82
