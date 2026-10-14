from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.appctx import build_context
from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.block_animation.contracts import (
    ActorPlacement,
    CameraIntent,
    EpisodeSpec,
    ShotPerformanceSpec,
)
from cinefactory.studio.block_production import BlockAnimationProducer
from cinefactory.studio.dialogue_performance import DialogueLineIntent
from cinefactory.studio.production_method_switch import (
    MethodSwitchPolicy,
    MethodSwitchRequest,
)
from cinefactory.turbo.contracts import (
    ResourceClass,
    WorkerSpec,
    WorkState,
)
from cinefactory.turbo.daemon import FactoryDaemon
from cinefactory.turbo.store import TurboStore


def _base_episode(ctx) -> tuple[EpisodeSpec, object]:
    base_shot = ShotPerformanceSpec(
        shot_id="S01",
        scene_template_id="minecraft_classroom",
        duration_seconds=4.0,
        actors=[
            ActorPlacement(
                actor_id="A",
                rig_id="mc_a",
                marker="hero_a",
                facing_target="B",
            ),
            ActorPlacement(
                actor_id="B",
                rig_id="mc_b",
                marker="hero_b",
                facing_target="A",
            ),
        ],
        camera=CameraIntent(
            purpose="fidelity_group",
            pattern_id="fidelity_group",
            targets=["A", "B"],
        ),
        creative_intent={
            "scene_id": "SC_DIALOGUE_AB",
            "mood": "tense but readable",
            "story_beat": "A confronts B; B reveals a denial",
        },
        narrative_purpose="two-character confrontation and reaction",
    )
    lines = [
        DialogueLineIntent(
            line_id="L1",
            speaker_id="A",
            listener_ids=["B"],
            text="Tell me what happened.",
            objective="force B to reveal the truth",
            action_verb="reveal",
            subtext="A already suspects B",
            emotion="angry",
            start_seconds=0.35,
            end_seconds=1.45,
            reaction_delay_seconds=0.16,
            voice_emotion="controlled anger",
        ),
        DialogueLineIntent(
            line_id="L2",
            speaker_id="B",
            listener_ids=["A"],
            text="I did not take it.",
            objective="make A doubt the accusation",
            action_verb="reveal",
            subtext="B is frightened but tries to appear certain",
            emotion="surprised",
            start_seconds=2.00,
            end_seconds=3.15,
            reaction_delay_seconds=0.18,
            voice_emotion="defensive surprise",
        ),
    ]
    compilation = ctx.dialogue_performance.compile(
        shot_id=base_shot.shot_id,
        duration_seconds=base_shot.duration_seconds,
        actor_ids=["A", "B"],
        lines=lines,
    )
    assert compilation.qc.passed is True
    shot = ctx.dialogue_performance.apply_to_shot(
        base_shot,
        compilation,
    )
    episode = EpisodeSpec(
        project_id="V182_DIALOGUE_MULTI",
        episode_id="V182_DIALOGUE_MULTI",
        title="v1.6.22 multi-character dialogue",
        fps=24,
        width=320,
        height=180,
        quality_profile="preview",
        shots=[shot],
    )
    return episode, compilation


def main() -> None:
    out = (
        ROOT
        / "data"
        / "verification"
        / "v182_multi_character_dialogue"
    )
    out.mkdir(parents=True, exist_ok=True)
    turbo_db = out / "turbo_v182.db"
    if turbo_db.exists():
        turbo_db.unlink()

    ctx = build_context(ROOT)
    ctx.turbo_store = TurboStore(turbo_db)
    episode, semantic_compilation = _base_episode(ctx)

    blender = (
        ROOT
        / ".tools"
        / "blender-4.5.14-windows-x64"
        / "blender.exe"
    )
    producer = BlockAnimationProducer(
        ROOT,
        blender_executable=str(blender),
        max_repair_rounds=0,
    )
    try:
        dailies = producer.produce(
            episode,
            project_root=out / "blender",
            render_preview=True,
        )
    finally:
        producer.close()

    assert dailies.passed is True
    shot_report = dailies.shots[0]
    assert shot_report.passed is True
    assert shot_report.selected_path
    blender_path = Path(shot_report.selected_path)
    assert blender_path.is_file()

    selected_take = next(
        take
        for take in shot_report.takes
        if take.take_id == shot_report.selected_take_id
    )
    performance_qc = dict(
        selected_take.evidence.get("performance_qc") or {}
    )
    assert performance_qc.get("passed") is True
    assert performance_qc.get("semantic_directive_count") == 4
    semantic_checks = list(
        performance_qc.get("semantic_checks") or []
    )
    assert semantic_checks
    assert all(row.get("passed") for row in semantic_checks)
    assert {
        row.get("type")
        for row in semantic_checks
    } >= {
        "ACTOR_BINDING",
        "GAZE_COVERAGE",
        "SPEAKER_EXPRESSION_COVERAGE",
        "LISTENER_REACTION_TIMING",
    }

    sidecar = blender_path.with_suffix(
        blender_path.suffix + ".frame_qc.json"
    )
    assert sidecar.is_file()
    frame_qc = json.loads(sidecar.read_text(encoding="utf-8"))
    assert {"A", "B"} <= set(frame_qc.get("actors", {}))

    pack_a = ctx.character_factory.capture_reference_from_render(
        source_media=blender_path,
        actor_id="A",
        rig_id="mc_a",
    )
    pack_b = ctx.character_factory.capture_reference_from_render(
        source_media=blender_path,
        actor_id="B",
        rig_id="mc_b",
    )
    assert pack_a.global_character_id == "CHAR_MC_A"
    assert pack_b.global_character_id == "CHAR_MC_B"

    compiled = EpisodeAssembler.from_root(ROOT).compile(
        episode,
        output_dir=out / "wan",
    )
    compiled_shot = compiled.shots[0]

    wan_work = ctx.cross_backend_video.build_work_item(
        compiled=compiled,
        shot=compiled_shot,
        output_path=out / "wan" / "S01.wan.multi_identity.mp4",
        render_preview=True,
        switch_round=1,
        switch_of_work_id="V182_BLENDER_DIALOGUE_REFERENCE",
        reference_frame_path=blender_path,
        recurring_identity_required=True,
        semantic_performance_required=False,
        precise_camera_required=False,
    )
    request = dict(wan_work.payload["video_request"])
    ref = dict(request["reference"])
    assert ref["global_character_ids"] == {
        "A": "CHAR_MC_A",
        "B": "CHAR_MC_B",
    }
    assert set(ref["actor_reference_ids"]) == {"A", "B"}
    assert set(ref["actor_screen_boxes"]) == {"A", "B"}

    ctx.turbo_store.enqueue_work(wan_work)
    gpu = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="v182-multi-character-gpu",
            resources={ResourceClass.GPU},
            capabilities={"block.video.comfy"},
            active_model_affinity=wan_work.model_affinity,
        ),
        poll_seconds=0.05,
    )
    try:
        assert gpu.tick() is True
    finally:
        gpu.close()

    wan_done = ctx.turbo_store.get_work(wan_work.work_id)
    assert wan_done.state is WorkState.SUCCESS
    wan_result = dict(wan_done.result)
    assert wan_result["qc_passed"] is True
    assert wan_result["identity_qc"]["metric"] == (
        "PER_ACTOR_REFERENCE_APPEARANCE"
    )
    identity = dict(
        wan_result["character_identity_qc"] or {}
    )
    tracking = dict(
        wan_result["actor_tracking_qc"] or {}
    )
    assert identity.get("passed") is True
    assert tracking.get("passed") is True
    assert tracking.get("measured") is True
    assert not identity.get("collision_findings")

    assessments = {
        row["actor_id"]: row
        for row in identity["assessments"]
    }
    assert set(assessments) == {"A", "B"}
    assert assessments["A"]["global_character_id"] == "CHAR_MC_A"
    assert assessments["B"]["global_character_id"] == "CHAR_MC_B"

    tracks = {
        row["actor_id"]: row
        for row in tracking["tracks"]
    }
    assert set(tracks) == {"A", "B"}
    for row in tracks.values():
        assert row["measured"] is True
        assert row["passed"] is True
        assert len(row["samples"]) == 3
        assert {
            sample["label"]
            for sample in row["samples"]
        } == {"head", "mid", "tail"}

    # Semantic performance remains fail-closed for Wan until the generated
    # motion itself has semantic-performance evidence, not merely a prompt.
    semantic_request = MethodSwitchRequest(
        project_id=compiled.project_id,
        episode_id=compiled.episode_id,
        shot_id=compiled_shot.shot_id,
        current_tool_id="blender",
        current_method_id="blender.cycles.quality",
        policy=MethodSwitchPolicy.BALANCED_ALTERNATIVE,
        min_quality=0.70,
        max_vram_gb=12.0,
        local_only=True,
        commercial_safe=True,
        max_additional_gpu_seconds=240.0,
        mean_current_attempt_seconds=20.0,
        continuity_priority=True,
        backend_switch_allowed=True,
        recurring_identity_required=True,
        reference_frame_path=str(blender_path),
        precise_camera_required=False,
        semantic_performance_required=True,
        visual_style="MINECRAFT",
        failure_codes=["MODEL_CAPABILITY"],
        required_tags={"reference_conditioning"},
    )
    semantic_decision = ctx.method_switch.deliberate(
        semantic_request
    )
    wan_assessment = next(
        item
        for item in semantic_decision.assessments
        if item.method_id
        == "comfyui.wan21.fun.inpaint.1.3b"
    )
    assert (
        "SEMANTIC_PERFORMANCE_VIDEO_QC_NOT_QUALIFIED"
        in wan_assessment.blockers
    )

    payload = {
        "dialogue_compilation": semantic_compilation.model_dump(
            mode="json"
        ),
        "blender_dialogue": {
            "path": str(blender_path),
            "bytes": blender_path.stat().st_size,
            "selected_take_id": shot_report.selected_take_id,
            "performance_score": selected_take.performance_score,
            "performance_qc": performance_qc,
            "actor_ids": sorted(frame_qc["actors"]),
        },
        "reference_packs": {
            "A": pack_a.model_dump(mode="json"),
            "B": pack_b.model_dump(mode="json"),
        },
        "wan_multi_character": {
            "work_id": wan_work.work_id,
            "state": wan_done.state.value,
            "path": wan_result["path"],
            "bytes": Path(wan_result["path"]).stat().st_size,
            "identity_qc": wan_result["identity_qc"],
            "character_identity_qc": identity,
            "actor_tracking_qc": tracking,
        },
        "wan_semantic_gate": {
            "decision_status": semantic_decision.status.value,
            "wan_blockers": wan_assessment.blockers,
        },
    }
    target = out / "multi_character_dialogue_verification.json"
    target.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
