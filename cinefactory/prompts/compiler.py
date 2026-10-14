from __future__ import annotations

from dataclasses import dataclass

from cinefactory.domain.models import AssetBibleSpec, ShotSpec


@dataclass(frozen=True)
class CompiledPrompt:
    positive: str
    negative: str
    metadata: dict


class ShotPromptCompiler:
    """Compile semantic ShotSpec into model-facing text without changing creative intent."""

    def compile_video(self, shot: ShotSpec, bible: AssetBibleSpec | None = None, *, repair_hint: str | None = None) -> CompiledPrompt:
        chars = []
        for character_id, perf in shot.performance.items():
            chars.append(
                f"{character_id}: objective {perf.objective}; playable action {perf.action_verb}; "
                f"outward mask {perf.outward_mask or 'natural'}; micro-expression {perf.micro_expression}; "
                f"body behavior {perf.body_behavior}; listening {perf.listening_behavior}"
            )
        action = "; ".join(
            f"{a.actor} {a.action}" + (f" toward {a.target}" if a.target else "")
            for a in shot.action_beats
        ) or "single clear motivated action"
        cam = shot.camera
        move = cam.movement
        positive = (
            f"Narrative purpose: {shot.narrative_purpose}. Audience endpoint: {shot.audience_endpoint}. "
            f"Shot: {cam.shot_size}, {cam.lens_mm or 'natural'}mm lens, {cam.camera_height or 'natural'} height, "
            f"{cam.angle or 'neutral'} angle, camera side {cam.camera_side or shot.entry_state.camera_side or 'maintain axis'}. "
            f"Composition: {cam.composition or 'story-motivated composition'}. Focus: {cam.focus_target or 'primary story subject'}. "
            f"Camera movement: {move.kind}; purpose: {move.purpose}; amplitude: {move.amplitude or 'minimal'}; "
            f"speed: {move.speed or 'natural'}. Performance: {' | '.join(chars) if chars else 'natural restrained performance'}. "
            f"Action: {action}. Continuity entry location: {shot.entry_state.location_id or 'unchanged'}. "
            f"Duration approximately {shot.duration_seconds:.2f} seconds. Preserve identity, wardrobe, props, screen direction, eyeline, lighting and spatial continuity."
        )
        negative = (
            "identity drift, face morphing, wardrobe change, prop teleportation, wrong eyeline, wrong screen direction, "
            "random camera motion, unmotivated zoom, excessive gestures, duplicate limbs, warped hands, text artifacts, "
            "flicker, temporal instability, abrupt lighting change, background drift"
        )
        if bible is not None:
            positive += f" Visual style lock: {bible.visual_style_lock}."
        if repair_hint:
            positive += f" Repair constraint: {repair_hint}"
        return CompiledPrompt(positive=positive, negative=negative, metadata={"shot_id": shot.shot_id})

    def compile_keyframe(self, shot: ShotSpec, bible: AssetBibleSpec | None = None, *, repair_hint: str | None = None) -> CompiledPrompt:
        video = self.compile_video(shot, bible, repair_hint=repair_hint)
        positive = "Single cinematic keyframe. " + video.positive.replace(
            f"Duration approximately {shot.duration_seconds:.2f} seconds.", "Freeze the decisive readable moment of the shot."
        )
        return CompiledPrompt(positive=positive, negative=video.negative, metadata={**video.metadata, "mode": "keyframe"})
