from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.block_animation.camera_qc import validate_compiled_camera_plan
from cinefactory.block_animation.contracts import (
    ActionCue,
    ActorPlacement,
    BlenderAnimationJob,
    CameraIntent,
    CrowdCue,
    EpisodeSpec,
    ExpressionCue,
    PropBindingCue,
    SemanticEventCue,
    ShotPerformanceSpec,
    TransformSpec,
    Vec3,
)
from cinefactory.block_animation.execution import BlockExecutionPlanner
from cinefactory.block_animation.runtime import BlockAnimationRuntime
from cinefactory.block_animation.styles import style_asset_manifest, validate_episode_style
from cinefactory.block_animation.visual_qc import BlockVisualQC
from cinefactory.turbo.blender import PersistentBlenderWorker
from cinefactory.turbo.metrics import gpu_snapshot


def transform(x: float, y: float, z: float = 0.0) -> TransformSpec:
    return TransformSpec(location=Vec3(x=x, y=y, z=z))


def style_definition(style: str) -> dict:
    if style == "MINECRAFT":
        return {
            "scene": "minecraft_classroom",
            "principal": ["mc_a", "mc_b", "mc_c"],
            "crowd": ["mc_crowd_1", "mc_crowd_2", "mc_crowd_3", "mc_a", "mc_b", "mc_c"],
            "prop": "minecraft_book",
            "label": "Minecraft Visual Fidelity",
        }
    return {
        "scene": "roblox_classroom",
        "principal": ["r6_a", "r6_b", "r6_c"],
        "crowd": ["r6_crowd_1", "r6_crowd_2", "r6_crowd_3", "r6_a", "r6_b", "r6_c"],
        "prop": "roblox_book",
        "label": "Roblox Visual Fidelity",
    }


def cast(style: str, beat: str = "default") -> list[ActorPlacement]:
    spec = style_definition(style)
    pa, pb, pc = spec["principal"]
    positions = {
        "default": ((-2.4, 0.7), (0.0, 0.8), (2.4, 1.0)),
        "entrance": ((-4.0, -2.4), (0.0, 0.8), (2.4, 1.0)),
        "walk": ((-2.9, -0.9), (0.0, 0.8), (2.4, 1.0)),
        "presentation": ((-1.7, -0.4), (1.2, 0.1), (2.4, 1.0)),
    }
    a, b, c = positions.get(beat, positions["default"])
    actors = [
        ActorPlacement(actor_id="A", rig_id=pa, transform=transform(*a), facing_target="B"),
        ActorPlacement(actor_id="B", rig_id=pb, transform=transform(*b), facing_target="A"),
        ActorPlacement(actor_id="C", rig_id=pc, transform=transform(*c), facing_target="B"),
    ]
    background_positions = [(-4.4, 2.8), (-2.4, 3.3), (2.4, 3.3), (4.4, 2.8), (-1.1, 4.0), (1.1, 4.0)]
    for index, (x, y) in enumerate(background_positions):
        actors.append(
            ActorPlacement(
                actor_id=f"BG{index + 1}",
                rig_id=spec["crowd"][index],
                transform=transform(x, y),
                facing_target="B",
                crowd_group="classroom",
            )
        )
    return actors


def crowd(style: str, behavior: str, start: float, end: float) -> CrowdCue:
    return CrowdCue(
        group_id="classroom",
        actor_ids=[f"BG{i}" for i in range(1, 7)],
        behavior_id=behavior,
        start_seconds=start,
        end_seconds=end,
    )


def beat(
    style: str,
    shot_id: str,
    duration: float,
    purpose: str,
    pattern: str,
    targets: list[str],
    *,
    cast_beat: str = "default",
    actions: list[ActionCue] | None = None,
    expressions: list[ExpressionCue] | None = None,
    props: list[PropBindingCue] | None = None,
    crowd_cues: list[CrowdCue] | None = None,
    events: list[SemanticEventCue] | None = None,
) -> ShotPerformanceSpec:
    spec = style_definition(style)
    return ShotPerformanceSpec(
        shot_id=shot_id,
        scene_template_id=spec["scene"],
        duration_seconds=duration,
        actors=cast(style, cast_beat),
        actions=actions or [],
        expressions=expressions or [],
        props=props or [],
        camera=CameraIntent(
            purpose=purpose,
            pattern_id=pattern,
            targets=targets,
            prop_id=(props[0].prop_id if props else None),
        ),
        crowd=crowd_cues or [crowd(style, "attentive_idle", 0.0, duration)],
        events=events or [],
        narrative_purpose=shot_id,
    )


def build_episode(style: str) -> EpisodeSpec:
    spec = style_definition(style)
    prop = spec["prop"]
    return EpisodeSpec(
        project_id=f"P_CINEFACTORY_V162_{style}",
        episode_id=f"EP_V162_{style}",
        title=spec["label"],
        fps=24,
        width=1920,
        height=1080,
        render_engine="BLENDER_EEVEE_NEXT",
        quality_profile="rtx3060_quality",
        blocked_reference_tokens=["BigSchool", "Maizen", "Aphmau", "Roblox YouTuber"],
        metadata={
            "benchmark": "v1.6.2_visual_fidelity",
            "visual_style": style,
            "visual_style_gate": True,
            "human_review_required": True,
            "production_api_spend": 0,
            "true_hand_transfer_supported": False,
        },
        shots=[
            beat(style, "BEAT01_ESTABLISH", 2.8, "fidelity_establish", "fidelity_establish", ["A", "B", "C"]),
            beat(
                style,
                "BEAT02_ENTRANCE",
                2.5,
                "fidelity_track",
                "fidelity_track",
                ["A"],
                cast_beat="entrance",
                actions=[ActionCue(actor_id="A", clip_id="walk", start_seconds=0.0, end_seconds=2.2, intensity=.8)],
            ),
            beat(
                style,
                "BEAT03_NOTICE",
                2.3,
                "fidelity_medium",
                "fidelity_medium",
                ["B"],
                expressions=[ExpressionCue(actor_id="B", expression_id="confused", start_seconds=.4, end_seconds=1.8, intensity=.7)],
                actions=[ActionCue(actor_id="B", clip_id="turn_head", start_seconds=.25, end_seconds=1.0, intensity=.7)],
            ),
            beat(
                style,
                "BEAT04_REACTION",
                2.3,
                "fidelity_reaction",
                "fidelity_reaction",
                ["B"],
                expressions=[ExpressionCue(actor_id="B", expression_id="surprised", start_seconds=.35, end_seconds=1.8, intensity=.9)],
                actions=[ActionCue(actor_id="B", clip_id="shock_recoil", start_seconds=.45, end_seconds=1.4, intensity=.8)],
                events=[SemanticEventCue(event_id="reveal_spark", at_seconds=.9, source_actor_id="B", intensity=.55)],
            ),
            beat(
                style,
                "BEAT05_WALK_TO_DESK",
                2.6,
                "fidelity_track",
                "fidelity_track",
                ["A"],
                cast_beat="walk",
                actions=[ActionCue(actor_id="A", clip_id="walk", start_seconds=0.0, end_seconds=2.3, intensity=.8)],
            ),
            beat(
                style,
                "BEAT06_PICKUP",
                2.4,
                "fidelity_prop_insert",
                "fidelity_prop_insert",
                ["A"],
                props=[PropBindingCue(prop_id=prop, actor_id="A", socket="right_hand", start_seconds=.55, end_seconds=2.25)],
                actions=[ActionCue(actor_id="A", clip_id="grab", start_seconds=.45, end_seconds=1.25, intensity=.75)],
            ),
            beat(
                style,
                "BEAT07_PRESENT",
                2.8,
                "fidelity_presentation",
                "fidelity_presentation",
                ["A", "B"],
                cast_beat="presentation",
                props=[PropBindingCue(prop_id=prop, actor_id="A", socket="right_hand", start_seconds=0.0, end_seconds=2.7)],
                actions=[
                    ActionCue(actor_id="A", clip_id="point", start_seconds=.35, end_seconds=1.7, intensity=.65),
                    ActionCue(actor_id="B", clip_id="turn_head", start_seconds=.75, end_seconds=1.5, intensity=.6),
                ],
                expressions=[ExpressionCue(actor_id="B", expression_id="happy", start_seconds=1.0, end_seconds=2.3, intensity=.7)],
                events=[SemanticEventCue(event_id="whoosh", at_seconds=1.0, source_actor_id="A", target_id="B", intensity=.55)],
            ),
            beat(
                style,
                "BEAT08_C_REACTS",
                2.2,
                "fidelity_reaction",
                "fidelity_reaction",
                ["C"],
                actions=[ActionCue(actor_id="C", clip_id="laugh_body", start_seconds=.3, end_seconds=1.8, intensity=.8)],
                expressions=[ExpressionCue(actor_id="C", expression_id="laugh", start_seconds=.3, end_seconds=1.9, intensity=.85)],
            ),
            beat(
                style,
                "BEAT09_CROWD",
                2.6,
                "fidelity_group",
                "fidelity_group",
                ["A", "B", "C"],
                crowd_cues=[crowd(style, "group_surprise", .25, 2.3)],
                events=[SemanticEventCue(event_id="impact_hit", at_seconds=.8, source_actor_id="C", intensity=.35)],
            ),
            beat(
                style,
                "BEAT10_TRACKING",
                2.4,
                "fidelity_track",
                "fidelity_track",
                ["A"],
                cast_beat="walk",
                props=[PropBindingCue(prop_id=prop, actor_id="A", socket="right_hand", start_seconds=.0, end_seconds=2.2)],
                actions=[ActionCue(actor_id="A", clip_id="walk", start_seconds=.0, end_seconds=2.1, intensity=.55)],
            ),
            beat(
                style,
                "BEAT11_ORBIT",
                2.6,
                "fidelity_orbit",
                "fidelity_orbit",
                ["A", "B", "C"],
                props=[PropBindingCue(prop_id=prop, actor_id="A", socket="right_hand", start_seconds=.0, end_seconds=2.4)],
                crowd_cues=[crowd(style, "attentive_idle", 0.0, 2.3)],
            ),
            beat(
                style,
                "BEAT12_FINAL_GROUP",
                3.0,
                "fidelity_group",
                "fidelity_group",
                ["A", "B", "C"],
                props=[PropBindingCue(prop_id=prop, actor_id="A", socket="right_hand", start_seconds=.0, end_seconds=2.7)],
                crowd_cues=[crowd(style, "group_surprise", .2, 2.7)],
                expressions=[ExpressionCue(actor_id="C", expression_id="laugh", start_seconds=.6, end_seconds=2.4, intensity=.75)],
                events=[SemanticEventCue(event_id="reveal_spark", at_seconds=1.4, source_actor_id="A", intensity=.35)],
            ),
        ],
    )


def resolve_blender() -> str:
    return os.environ.get("CINEFACTORY_BLENDER_EXECUTABLE", "blender")


def ffmpeg_executable() -> str:
    configured = os.environ.get("CINEFACTORY_FFMPEG_EXECUTABLE")
    if configured:
        return configured
    return shutil.which("ffmpeg") or r"C:\Users\ADMIN\ffmpeg\bin\ffmpeg.exe"


def make_frame_and_sheet(video: Path, sheet: Path, reference: Path | None = None, reference_source: Path | None = None) -> None:
    ffmpeg = ffmpeg_executable()
    if reference is not None:
        reference.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([ffmpeg, "-y", "-v", "error", "-i", str(reference_source or video), "-frames:v", "1", str(reference)], check=True)
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-v",
            "error",
            "-i",
            str(video),
            "-vf",
            "fps=1/5,scale=480:-1,tile=3x2:padding=8:margin=8",
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(sheet),
        ],
        check=True,
    )


def render_style(style: str) -> dict:
    validation_root = ROOT / "data" / "validation" / "v1.6.2"
    out_root = validation_root / ("minecraft" if style == "MINECRAFT" else "roblox")
    out_root.mkdir(parents=True, exist_ok=True)
    episode = build_episode(style)
    assembler = EpisodeAssembler.from_root(ROOT)
    style_findings = validate_episode_style(episode, assembler.libraries)
    if style_findings:
        raise RuntimeError(f"style gate failed before render: {[finding.model_dump() for finding in style_findings]}")
    compiled = assembler.compile(episode, output_dir=out_root)
    assembler.write_compiled(compiled, out_root / "compiled_episode.json")
    camera_qc = validate_compiled_camera_plan(compiled)
    (out_root / "camera_qc_report.json").write_text(json.dumps(camera_qc, indent=2), encoding="utf-8")
    plans = out_root / "execution_plans"
    plans.mkdir(parents=True, exist_ok=True)
    for shot in compiled.shots:
        plan = BlockExecutionPlanner.plan(
            BlenderAnimationJob(
                project_id=compiled.project_id,
                episode_id=compiled.episode_id,
                shot=shot,
                output_path=str(out_root / "shots" / f"{shot.order:04d}_{shot.shot_id}.mp4"),
            )
        )
        (plans / f"{shot.order:04d}_{shot.shot_id}.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")

    worker = PersistentBlenderWorker(ROOT, blender_executable=resolve_blender(), startup_timeout=180, job_timeout=7200)
    runtime = BlockAnimationRuntime(ROOT)
    startup_started = time.monotonic()
    startup = worker.start()
    startup_seconds = time.monotonic() - startup_started
    pid = startup["pid"]
    rows = []
    try:
        for shot in compiled.shots:
            output = out_root / "shots" / f"{shot.order:04d}_{shot.shot_id}.mp4"
            started = time.monotonic()
            before_gpu = gpu_snapshot()
            result = runtime.render_and_qc(
                worker,
                BlenderAnimationJob(project_id=compiled.project_id, episode_id=compiled.episode_id, shot=shot, output_path=str(output)),
            )
            elapsed = time.monotonic() - started
            rows.append(
                {
                    "shot_id": shot.shot_id,
                    "order": shot.order,
                    "frames": shot.frame_end,
                    "resolution": {"width": shot.width, "height": shot.height},
                    "fps": shot.fps,
                    "render_duration_seconds": elapsed,
                    "seconds_per_frame": elapsed / max(1, shot.frame_end),
                    "persistent_pid": worker.pid,
                    "same_pid": worker.pid == pid,
                    "gpu_before": before_gpu,
                    "gpu_after": gpu_snapshot(),
                    "worker_result": worker.last_result,
                    "result": result,
                }
            )
    finally:
        worker.close()

    master = out_root / ("minecraft_visual_fidelity.mp4" if style == "MINECRAFT" else "roblox_visual_fidelity.mp4")
    assembled = runtime.assemble_episode(
        {
            "episode_id": compiled.episode_id,
            "output_path": str(master),
            "shots": [
                {"shot_id": row["shot_id"], "order": row["order"], "path": str(out_root / "shots" / f"{row['order']:04d}_{row['shot_id']}.mp4")}
                for row in rows
            ],
        }
    )
    master_qc = BlockVisualQC().review(master)
    metrics = {
        "version": "1.6.2-visual-fidelity",
        "style": style,
        "episode_id": compiled.episode_id,
        "title": compiled.title,
        "duration_expected_seconds": sum(shot.duration_seconds for shot in compiled.shots),
        "worker_startup_seconds": startup_seconds,
        "persistent_pid": pid,
        "same_pid_across_shots": all(row["same_pid"] for row in rows),
        "style_gate": {"passed": not style_findings, "human_review_required": True},
        "camera_qc": camera_qc,
        "shots": rows,
        "assembled": assembled,
        "master_visual_qc": {
            "passed": master_qc.passed,
            "findings": master_qc.findings,
            "black_seconds": master_qc.black_seconds,
            "freeze_seconds": master_qc.freeze_seconds,
        },
        "prop_transfer_supported": False,
        "prop_transfer_note": "Timed socket attachment is supported; true hand-to-hand transfer remains deferred rather than faked.",
        "quality_profile": compiled.shots[0].render_quality.profile_id,
        "production_api_spend": 0,
    }
    (out_root / "shot_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (out_root / "qc_report.json").write_text(json.dumps(metrics["master_visual_qc"], indent=2), encoding="utf-8")
    (out_root / "style_gate_report.json").write_text(json.dumps(metrics["style_gate"], indent=2), encoding="utf-8")
    (out_root / "events_manifest.json").write_text(Path(assembled["event_manifest"]).read_text(encoding="utf-8"), encoding="utf-8")
    return {"style": style, "root": out_root, "metrics": metrics, "compiled": compiled, "libraries": assembler.libraries, "master": master}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--style", choices=["MINECRAFT", "ROBLOX", "both"], default="both")
    args = parser.parse_args()
    styles = ["MINECRAFT", "ROBLOX"] if args.style == "both" else [args.style]
    results = [render_style(style) for style in styles]
    root = ROOT / "data" / "validation" / "v1.6.2"
    root.mkdir(parents=True, exist_ok=True)
    for result in results:
        if result["style"] == "MINECRAFT":
            make_frame_and_sheet(
                result["master"],
                root / "minecraft_contact_sheet.jpg",
                root / "minecraft_before_or_v161_reference.png",
                ROOT / "data" / "validation" / "v1.6.1" / "beauty_benchmark_001_before.mp4",
            )
            shutil.copy2(root / "minecraft_contact_sheet.jpg", root / "minecraft_after_contact_sheet.jpg")
        else:
            make_frame_and_sheet(result["master"], root / "roblox_contact_sheet.jpg")
            shutil.copy2(root / "roblox_contact_sheet.jpg", root / "roblox_after_contact_sheet.jpg")
    print(json.dumps({"styles": styles, "output_root": str(root)}, indent=2))


if __name__ == "__main__":
    main()
