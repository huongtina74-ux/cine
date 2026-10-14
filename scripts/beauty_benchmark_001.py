from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.block_animation.contracts import (
    ActionCue,
    ActorPlacement,
    BlenderAnimationJob,
    CameraIntent,
    CrowdCue,
    EpisodeSpec,
    ExpressionCue,
    PropBindingCue,
    ReactionTrigger,
    SemanticEventCue,
    TransformSpec,
    Vec3,
)
from cinefactory.block_animation.execution import BlockExecutionPlanner
from cinefactory.block_animation.runtime import BlockAnimationRuntime
from cinefactory.block_animation.visual_qc import BlockVisualQC
from cinefactory.turbo.blender import PersistentBlenderWorker
from cinefactory.turbo.metrics import gpu_snapshot


def transform(x: float, y: float, z: float = 0.0) -> TransformSpec:
    return TransformSpec(location=Vec3(x=x, y=y, z=z))


def cast(
    *,
    a_location: tuple[float, float] = (-4.5, -3.5),
    b_location: tuple[float, float] = (0.0, 0.0),
    c_location: tuple[float, float] = (2.3, 0.2),
) -> list[ActorPlacement]:
    foreground = [
        ActorPlacement(actor_id="A", rig_id="block_humanoid_a", transform=transform(*a_location), facing_target="B"),
        ActorPlacement(actor_id="B", rig_id="block_humanoid_b", transform=transform(*b_location), facing_target="A"),
        ActorPlacement(actor_id="C", rig_id="block_humanoid_a", transform=transform(*c_location), facing_target="B"),
    ]
    background_positions = [
        (-4.2, 2.1), (-2.5, 2.5), (2.5, 2.5), (4.2, 2.1),
        (-4.0, -0.8), (4.0, -0.8), (-1.7, 3.6), (1.7, 3.6),
    ]
    background = [
        ActorPlacement(
            actor_id=f"BG{i + 1}",
            rig_id="block_humanoid_b" if i % 2 else "block_humanoid_a",
            transform=transform(x, y),
            facing_target="B",
            crowd_group="classroom",
        )
        for i, (x, y) in enumerate(background_positions)
    ]
    return foreground + background


def background_crowd(behavior: str = "attentive_idle", start: float = 0.0, end: float | None = None) -> CrowdCue:
    return CrowdCue(
        group_id="classroom",
        actor_ids=[f"BG{i}" for i in range(1, 9)],
        behavior_id=behavior,
        start_seconds=start,
        end_seconds=end,
    )


def shot(
    shot_id: str,
    duration: float,
    purpose: str,
    pattern: str,
    targets: list[str],
    *,
    a_location: tuple[float, float] = (-4.5, -3.5),
    b_location: tuple[float, float] = (0.0, 0.0),
    c_location: tuple[float, float] = (2.3, 0.2),
    actions: list[ActionCue] | None = None,
    expressions: list[ExpressionCue] | None = None,
    reactions: list[ReactionTrigger] | None = None,
    props: list[PropBindingCue] | None = None,
    crowd: list[CrowdCue] | None = None,
    events: list[SemanticEventCue] | None = None,
) -> dict:
    from cinefactory.block_animation.contracts import ShotPerformanceSpec

    return ShotPerformanceSpec(
        shot_id=shot_id,
        scene_template_id="block_classroom",
        duration_seconds=duration,
        actors=cast(a_location=a_location, b_location=b_location, c_location=c_location),
        actions=actions or [],
        expressions=expressions or [],
        reactions=reactions or [],
        props=props or [],
        camera=CameraIntent(purpose=purpose, pattern_id=pattern, targets=targets),
        crowd=crowd or [background_crowd()],
        events=events or [],
        narrative_purpose=shot_id,
    )


def build_episode() -> EpisodeSpec:
    return EpisodeSpec(
        project_id="P_CINEFACTORY_BEAUTY_001",
        episode_id="EP_BEAUTY_001",
        title="CineFactory Beauty Benchmark #001",
        fps=24,
        width=1920,
        height=1080,
        render_engine="BLENDER_EEVEE_NEXT",
        quality_profile="rtx3060_quality",
        blocked_reference_tokens=["BigSchool", "Minecraft", "Roblox"],
        metadata={
            "benchmark": "v1.6.1_beauty_001",
            "prop_transfer_supported": False,
            "beats": [
                "establishing classroom",
                "A enters",
                "B notices A",
                "B surprise reaction",
                "A walks to table",
                "A picks up book",
                "camera push-in",
                "A presents book toward B without transfer",
                "C laughs",
                "varied crowd reaction",
                "orbit camera",
                "final group reaction",
            ],
        },
        shots=[
            shot("BEAT01_ESTABLISH", 4.0, "comedy_reveal", "reveal_wide", ["A", "B", "C"]),
            shot(
                "BEAT02_ENTRANCE", 4.0, "chase", "chase_track", ["A"],
                actions=[ActionCue(actor_id="A", clip_id="walk", start_seconds=0.0, end_seconds=3.6, intensity=0.9)],
            ),
            shot(
                "BEAT03_NOTICE", 3.5, "reaction", "reaction_close", ["B"],
                actions=[ActionCue(actor_id="B", clip_id="turn_head", start_seconds=0.35, end_seconds=1.0, intensity=0.8)],
                expressions=[ExpressionCue(actor_id="B", expression_id="confused", start_seconds=0.55, end_seconds=2.3, intensity=0.8)],
            ),
            shot(
                "BEAT04_SURPRISE", 3.5, "reaction", "reaction_close", ["B"],
                actions=[ActionCue(actor_id="B", clip_id="shock_recoil", start_seconds=0.8, end_seconds=1.7, intensity=0.8)],
                expressions=[ExpressionCue(actor_id="B", expression_id="surprised", start_seconds=0.7, end_seconds=2.0, intensity=0.9)],
                events=[SemanticEventCue(event_id="reveal_spark", at_seconds=1.0, source_actor_id="B", intensity=0.7)],
            ),
            shot(
                "BEAT05_TABLE_WALK", 4.5, "chase", "chase_track", ["A"],
                actions=[
                    ActionCue(actor_id="A", clip_id="walk", start_seconds=0.1, end_seconds=3.9, intensity=0.85),
                    ActionCue(actor_id="A", clip_id="point", start_seconds=3.0, end_seconds=4.2, intensity=0.55),
                ],
            ),
            shot(
                "BEAT06_PICKUP", 3.5, "important_prop", "prop_insert", ["A"],
                actions=[ActionCue(actor_id="A", clip_id="grab", start_seconds=0.7, end_seconds=1.8, intensity=0.8)],
                props=[PropBindingCue(prop_id="book", actor_id="A", socket="left_hand", start_seconds=0.85, end_seconds=3.2)],
            ),
            shot(
                "BEAT07_PUSH_IN", 4.0, "reaction", "reaction_close", ["A"],
                actions=[ActionCue(actor_id="A", clip_id="point", start_seconds=0.45, end_seconds=2.2, intensity=0.75)],
                props=[PropBindingCue(prop_id="book", actor_id="A", socket="left_hand", start_seconds=0.0, end_seconds=3.8)],
                expressions=[ExpressionCue(actor_id="A", expression_id="smug", start_seconds=0.5, end_seconds=3.2, intensity=0.65)],
            ),
            shot(
                "BEAT08_PRESENT", 4.5, "presentation", "presentation_group", ["A", "B"],
                a_location=(-1.8, -0.8),
                actions=[
                    ActionCue(actor_id="A", clip_id="point", start_seconds=0.4, end_seconds=2.0, intensity=0.7),
                    ActionCue(actor_id="B", clip_id="turn_head", start_seconds=1.0, end_seconds=2.0, intensity=0.7),
                ],
                expressions=[ExpressionCue(actor_id="B", expression_id="confused", start_seconds=1.3, end_seconds=3.6, intensity=0.7)],
                props=[PropBindingCue(prop_id="book", actor_id="A", socket="left_hand", start_seconds=0.0, end_seconds=4.0)],
                events=[SemanticEventCue(event_id="whoosh", at_seconds=1.5, source_actor_id="A", target_id="B", intensity=0.8)],
            ),
            shot(
                "BEAT09_C_LAUGHS", 3.5, "reaction", "reaction_close", ["C"],
                actions=[ActionCue(actor_id="C", clip_id="laugh_body", start_seconds=0.5, end_seconds=2.6, intensity=0.85)],
                expressions=[ExpressionCue(actor_id="C", expression_id="laugh", start_seconds=0.45, end_seconds=2.8, intensity=0.9)],
            ),
            shot(
                "BEAT10_CROWD_REACTS", 4.5, "group_reaction", "group_reaction", ["A", "B", "C"],
                actions=[ActionCue(actor_id="C", clip_id="laugh_body", start_seconds=0.6, end_seconds=2.6, intensity=0.65)],
                expressions=[ExpressionCue(actor_id="C", expression_id="laugh", start_seconds=0.6, end_seconds=2.8, intensity=0.7)],
                crowd=[background_crowd("group_surprise", start=0.5, end=4.1)],
                events=[SemanticEventCue(event_id="impact_hit", at_seconds=1.1, source_actor_id="C", intensity=0.45)],
            ),
            shot(
                "BEAT11_ORBIT", 4.5, "group_orbit", "orbit_group", ["A", "B", "C"],
                actions=[ActionCue(actor_id="A", clip_id="turn_head", start_seconds=0.7, end_seconds=1.6, intensity=0.6)],
                props=[PropBindingCue(prop_id="book", actor_id="A", socket="left_hand", start_seconds=0.0, end_seconds=4.0)],
                crowd=[background_crowd("attentive_idle", start=0.0, end=4.0)],
            ),
            shot(
                "BEAT12_FINAL_GROUP", 5.5, "group_reaction", "group_reaction", ["A", "B", "C"],
                actions=[
                    ActionCue(actor_id="A", clip_id="turn_head", start_seconds=0.7, end_seconds=1.5, intensity=0.55),
                    ActionCue(actor_id="C", clip_id="laugh_body", start_seconds=1.1, end_seconds=3.0, intensity=0.75),
                ],
                expressions=[ExpressionCue(actor_id="C", expression_id="laugh", start_seconds=1.0, end_seconds=3.2, intensity=0.8)],
                props=[PropBindingCue(prop_id="book", actor_id="A", socket="left_hand", start_seconds=0.0, end_seconds=3.8)],
                crowd=[background_crowd("group_surprise", start=0.7, end=4.6)],
                events=[SemanticEventCue(event_id="reveal_spark", at_seconds=2.0, source_actor_id="A", intensity=0.45)],
            ),
        ],
    )


def resolve_blender() -> str:
    configured = os.environ.get("CINEFACTORY_BLENDER_EXECUTABLE")
    if configured:
        return configured
    return "blender"


def run(phase: str) -> dict:
    validation_root = ROOT / "data" / "validation" / "v1.6.1"
    phase_root = validation_root / f"beauty_benchmark_001_{phase}"
    phase_root.mkdir(parents=True, exist_ok=True)
    episode = build_episode()
    assembler = EpisodeAssembler.from_root(ROOT)
    compiled = assembler.compile(episode, output_dir=phase_root)
    assembler.write_compiled(compiled, phase_root / "compiled_episode.json")
    plan_root = phase_root / "execution_plans"
    plan_root.mkdir(parents=True, exist_ok=True)
    for compiled_shot in compiled.shots:
        plan = BlockExecutionPlanner.plan(
            BlenderAnimationJob(
                project_id=compiled.project_id,
                episode_id=compiled.episode_id,
                shot=compiled_shot,
                output_path=str(phase_root / "shots" / f"{compiled_shot.order:04d}_{compiled_shot.shot_id}.mp4"),
            )
        )
        (plan_root / f"{compiled_shot.order:04d}_{compiled_shot.shot_id}.json").write_text(
            json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    worker = PersistentBlenderWorker(
        ROOT,
        blender_executable=resolve_blender(),
        startup_timeout=180,
        job_timeout=7200,
    )
    runtime = BlockAnimationRuntime(ROOT)
    rows: list[dict] = []
    startup_started = time.monotonic()
    startup = worker.start()
    startup_seconds = time.monotonic() - startup_started
    persistent_pid = startup["pid"]
    try:
        for compiled_shot in compiled.shots:
            output_path = phase_root / "shots" / f"{compiled_shot.order:04d}_{compiled_shot.shot_id}.mp4"
            started = time.monotonic()
            gpu_before = gpu_snapshot()
            result = runtime.render_and_qc(
                worker,
                BlenderAnimationJob(
                    project_id=compiled.project_id,
                    episode_id=compiled.episode_id,
                    shot=compiled_shot,
                    output_path=str(output_path),
                ),
            )
            elapsed = time.monotonic() - started
            rows.append(
                {
                    "shot_id": compiled_shot.shot_id,
                    "order": compiled_shot.order,
                    "frames": compiled_shot.frame_end,
                    "resolution": {"width": compiled_shot.width, "height": compiled_shot.height},
                    "render_duration_seconds": elapsed,
                    "seconds_per_frame": elapsed / max(1, compiled_shot.frame_end),
                    "persistent_pid": worker.pid,
                    "same_pid": worker.pid == persistent_pid,
                    "gpu_before": gpu_before,
                    "gpu_after": gpu_snapshot(),
                    "result": result,
                }
            )
    finally:
        worker.close()

    master_path = validation_root / f"beauty_benchmark_001_{phase}.mp4"
    assembled = runtime.assemble_episode(
        {
            "episode_id": compiled.episode_id,
            "output_path": str(master_path),
            "shots": [
                {
                    "shot_id": row["shot_id"],
                    "order": row["order"],
                    "path": str(phase_root / "shots" / f"{row['order']:04d}_{row['shot_id']}.mp4"),
                }
                for row in rows
            ],
        }
    )
    master_qc = BlockVisualQC().review(master_path)
    report = {
        "phase": phase,
        "version": "1.6.1-validation",
        "episode_id": compiled.episode_id,
        "title": compiled.title,
        "duration_expected_seconds": sum(shot.duration_seconds for shot in compiled.shots),
        "persistent_pid": persistent_pid,
        "worker_startup_seconds": startup_seconds,
        "shots": rows,
        "assembled": assembled,
        "master_visual_qc": {
            "passed": master_qc.passed,
            "findings": master_qc.findings,
            "black_seconds": master_qc.black_seconds,
            "freeze_seconds": master_qc.freeze_seconds,
        },
        "prop_transfer_supported": False,
        "prop_transfer_note": "v1.6 supports timed socket attachment; true hand-to-hand transfer is not implemented.",
        "quality_profile": compiled.shots[0].render_quality.profile_id,
    }
    (phase_root / "benchmark_metrics.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (phase_root / "qc_report.json").write_text(json.dumps(report["master_visual_qc"], ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy2(assembled["event_manifest"], phase_root / "events_manifest.json")
    if phase == "after":
        final_dir = validation_root / "beauty_benchmark_001"
        final_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(master_path, final_dir / "master.mp4")
        shutil.copy2(phase_root / "compiled_episode.json", final_dir / "compiled_episode.json")
        shutil.copytree(phase_root / "execution_plans", final_dir / "execution_plans", dirs_exist_ok=True)
        shutil.copytree(phase_root / "shots", final_dir / "shots", dirs_exist_ok=True)
        shutil.copy2(phase_root / "events_manifest.json", final_dir / "events_manifest.json")
        shutil.copy2(phase_root / "benchmark_metrics.json", final_dir / "benchmark_metrics.json")
        shutil.copy2(phase_root / "qc_report.json", final_dir / "qc_report.json")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["before", "after"], default="before")
    args = parser.parse_args()
    run(args.phase)
