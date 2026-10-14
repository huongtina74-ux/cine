from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cinefactory.block_animation.contracts import BlenderAnimationJob, CompiledShot


@dataclass(frozen=True)
class ExecutionSummary:
    scene_mode: str
    actor_count: int
    action_count: int
    expression_count: int
    prop_count: int
    crowd_count: int
    event_count: int
    camera_take_id: str | None
    quality_profile: str


class BlockExecutionPlanner:
    """Pure-Python bridge between EpisodeAssembler contracts and render workers.

    Keeping this layer Blender-free makes execution semantics unit-testable even on
    CI machines without Blender/GPU. The Blender worker consumes this normalized plan.
    """

    @staticmethod
    def choose_camera(shot: CompiledShot, camera_take_id: str | None = None) -> dict[str, Any] | None:
        if not shot.camera_takes:
            return None
        if camera_take_id:
            for take in shot.camera_takes:
                if take.take_id == camera_take_id:
                    return take.model_dump(mode="json")
        return shot.camera_takes[0].model_dump(mode="json")

    @classmethod
    def plan(cls, job: BlenderAnimationJob) -> dict[str, Any]:
        shot = job.shot
        crowd_actions: list[dict[str, Any]] = []
        crowd_expressions: list[dict[str, Any]] = []
        for member in shot.crowd:
            crowd_actions.append({
                "actor_id": member.actor_id,
                "clip_id": member.clip_id,
                "start_seconds": member.start_seconds,
                "end_seconds": member.end_seconds,
                "speed": 1.0,
                "intensity": member.intensity,
                "layer": "base",
                "target": None,
                "emit_event": None,
                "source": "crowd",
            })
            if member.expression_id and member.expression_channels:
                crowd_expressions.append({
                    "actor_id": member.actor_id,
                    "expression_id": member.expression_id,
                    "start_seconds": member.start_seconds,
                    "end_seconds": member.end_seconds,
                    "intensity": member.intensity,
                    "channels": dict(member.expression_channels),
                    "source": "crowd",
                })

        return {
            "shot_id": shot.shot_id,
            "duration_seconds": shot.duration_seconds,
            "fps": shot.fps,
            "width": shot.width,
            "height": shot.height,
            "render_engine": shot.render_engine,
            "render_preview": job.render_preview,
            "scene": shot.scene.model_dump(mode="json"),
            "scene_mode": "library" if shot.scene.source_path else "procedural",
            "visual_style": shot.visual_style or shot.scene.style,
            "actors": [x.model_dump(mode="json") for x in shot.actors],
            "rigs": {k: v.model_dump(mode="json") for k, v in shot.rigs.items()},
            "clips": {k: v.model_dump(mode="json") for k, v in shot.clips.items()},
            "actions": [x.model_dump(mode="json") for x in shot.actions] + crowd_actions,
            "expressions": [x.model_dump(mode="json") for x in shot.expressions] + crowd_expressions,
            "gaze": [x.model_dump(mode="json") for x in shot.gaze],
            "reactions": [x.model_dump(mode="json") for x in shot.reactions],
            "creative_intent": dict(shot.creative_intent),
            "performance_directives": list(shot.performance_directives),
            "speech_viseme_tracks": list(shot.creative_intent.get("speech_viseme_tracks") or []),
            "lighting_intent": dict(shot.lighting_intent),
            "props": [x.model_dump(mode="json") for x in shot.props],
            "prop_definitions": {k: v.model_dump(mode="json") for k, v in shot.prop_definitions.items()},
            "events": [x.model_dump(mode="json") for x in shot.events],
            "camera": cls.choose_camera(shot, job.camera_take_id),
            "render_quality": shot.render_quality.model_dump(mode="json"),
            "output_path": job.output_path,
            "temp_dir": job.temp_dir,
        }

    @classmethod
    def summary(cls, job: BlenderAnimationJob) -> ExecutionSummary:
        p = cls.plan(job)
        return ExecutionSummary(
            scene_mode=p["scene_mode"],
            actor_count=len(p["actors"]),
            action_count=len(p["actions"]),
            expression_count=len(p["expressions"]),
            prop_count=len(p["props"]),
            crowd_count=len(job.shot.crowd),
            event_count=len(p["events"]),
            camera_take_id=(p["camera"] or {}).get("take_id"),
            quality_profile=p["render_quality"]["profile_id"],
        )
