from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from cinefactory.domain.models import DirectorPlan, ScriptSpec, ShotSpec, ShotSpecBatch

from .audio_department import AudioCue, AudioPlan, AudioRole
from .color_department import ColorBible, ColorPlan, ShotColorState
from .creative_pipeline import (
    AnimaticPlan,
    CinematographyBible,
    DirectorTreatment,
    StoryArchitecture,
)


class CraftSeverity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKER = "BLOCKER"


class CraftFinding(BaseModel):
    code: str
    severity: CraftSeverity
    shot_id: str | None = None
    scene_id: str | None = None
    message: str
    evidence: dict[str, Any] = Field(default_factory=dict)


class ShotCreativeIntent(BaseModel):
    shot_id: str
    scene_id: str
    beat_id: str | None = None
    scene_purpose: str
    beat_purpose: str | None = None
    shot_purpose: str
    audience_know: str
    audience_feel: str
    audience_endpoint: str
    performance_objectives: dict[str, str] = Field(default_factory=dict)
    camera_purpose: str
    edit_intent: str
    sound_intent: str
    lighting_intent: list[str] = Field(default_factory=list)
    continuity_contract: dict[str, Any] = Field(default_factory=dict)


class SceneCreativeIntent(BaseModel):
    scene_id: str
    purpose: str
    audience_know: str
    audience_feel: str
    beat_ids: list[str] = Field(default_factory=list)
    shot_ids: list[str] = Field(default_factory=list)


class CreativeIntentGraph(BaseModel):
    project_id: str
    scenes: list[SceneCreativeIntent] = Field(default_factory=list)
    shots: list[ShotCreativeIntent] = Field(default_factory=list)
    mapping_findings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_shots(self) -> "CreativeIntentGraph":
        ids = [shot.shot_id for shot in self.shots]
        if len(ids) != len(set(ids)):
            raise ValueError("creative intent graph shot ids must be unique")
        return self


class PerformanceDirectionBeat(BaseModel):
    shot_id: str
    scene_id: str
    subject_id: str
    objective: str
    action_verb: str
    gaze_target: str | None = None
    expression_intent: str | None = None
    gesture_intent: str | None = None
    reaction_trigger: str | None = None
    reaction_delay_seconds: float | None = Field(default=None, ge=0)
    pose_readability: str = "readable silhouette at key pose"
    body_mechanics: list[str] = Field(default_factory=list)
    timing_notes: list[str] = Field(default_factory=list)


class PerformanceDirectionPlan(BaseModel):
    project_id: str
    beats: list[PerformanceDirectionBeat] = Field(default_factory=list)
    findings: list[CraftFinding] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(x.severity is CraftSeverity.BLOCKER for x in self.findings)


class CameraDiagnosticsReport(BaseModel):
    project_id: str
    findings: list[CraftFinding] = Field(default_factory=list)
    checked_shots: int = Field(ge=0)

    @property
    def passed(self) -> bool:
        return not any(x.severity is CraftSeverity.BLOCKER for x in self.findings)


class ShotLightingColorIntent(BaseModel):
    shot_id: str
    scene_id: str
    narrative_purpose: str
    light_state: str | None = None
    time_of_day: str | None = None
    exposure_priority: str = "protect focal subject readability"
    continuity_priority: str = "match adjacent shots before decorative grading"
    color_intent: str = "support scene emotion without identity drift"


class LightingColorIntentPlan(BaseModel):
    project_id: str
    shots: list[ShotLightingColorIntent] = Field(default_factory=list)
    global_rules: list[str] = Field(default_factory=list)


class SoundSpot(BaseModel):
    spot_id: str
    shot_id: str
    scene_id: str
    purpose: str
    dialogue_priority: bool = True
    ambience_intent: str = "preserve spatial continuity"
    foley_events: list[str] = Field(default_factory=list)
    sfx_events: list[str] = Field(default_factory=list)
    music_intent: str = "support dramatic change without masking speech"
    silence_intent: str | None = None


class SoundSpottingPlan(BaseModel):
    project_id: str
    spots: list[SoundSpot] = Field(default_factory=list)
    global_rules: list[str] = Field(default_factory=list)


class CraftExecutionBundle(BaseModel):
    project_id: str
    creative_intent_graph: CreativeIntentGraph
    camera_diagnostics: CameraDiagnosticsReport
    performance_direction: PerformanceDirectionPlan
    lighting_color_intent: LightingColorIntentPlan
    sound_spotting: SoundSpottingPlan

    @property
    def passed(self) -> bool:
        return (
            self.camera_diagnostics.passed
            and self.performance_direction.passed
        )


class CreativeIntentCompiler:
    @staticmethod
    def _norm(value: str | None) -> str:
        return " ".join((value or "").strip().lower().split())

    def compile(
        self,
        *,
        project_id: str,
        story: StoryArchitecture,
        script: ScriptSpec,
        director: DirectorPlan,
        treatment: DirectorTreatment,
        shots: ShotSpecBatch,
    ) -> CreativeIntentGraph:
        script_by_scene = {scene.scene_id: scene for scene in script.scenes}
        director_by_scene = {scene.scene_id: scene for scene in director.scenes}
        treatment_by_scene = {scene.scene_id: scene for scene in treatment.scenes}
        shots_by_scene: dict[str, list[ShotSpec]] = {}
        for shot in shots.shots:
            shots_by_scene.setdefault(shot.scene_id, []).append(shot)

        beat_by_change = {
            self._norm(beat.change): beat
            for beat in story.beats
            if self._norm(beat.change)
        }
        mapping_findings: list[str] = []
        scenes: list[SceneCreativeIntent] = []
        shot_intents: list[ShotCreativeIntent] = []

        for scene_id, script_scene in script_by_scene.items():
            directed = director_by_scene.get(scene_id)
            treated = treatment_by_scene.get(scene_id)
            if directed is None or treated is None:
                mapping_findings.append(
                    f"{scene_id}:DIRECTOR_OR_TREATMENT_MISSING"
                )
                continue
            beat = beat_by_change.get(self._norm(script_scene.dramatic_event))
            if beat is None:
                mapping_findings.append(
                    f"{scene_id}:STORY_BEAT_MAPPING_UNRESOLVED"
                )
            scene_shots = shots_by_scene.get(scene_id, [])
            scenes.append(
                SceneCreativeIntent(
                    scene_id=scene_id,
                    purpose=treated.purpose,
                    audience_know=directed.audience_know,
                    audience_feel=directed.audience_feel,
                    beat_ids=[beat.beat_id] if beat else [],
                    shot_ids=[shot.shot_id for shot in scene_shots],
                )
            )
            for shot in scene_shots:
                performance_objectives = {
                    subject_id: perf.objective
                    for subject_id, perf in shot.performance.items()
                }
                light_values = [
                    value
                    for value in (
                        shot.entry_state.light_state,
                        shot.entry_state.time_of_day,
                    )
                    if value
                ]
                shot_intents.append(
                    ShotCreativeIntent(
                        shot_id=shot.shot_id,
                        scene_id=scene_id,
                        beat_id=beat.beat_id if beat else None,
                        scene_purpose=treated.purpose,
                        beat_purpose=beat.purpose if beat else None,
                        shot_purpose=shot.narrative_purpose,
                        audience_know=directed.audience_know,
                        audience_feel=directed.audience_feel,
                        audience_endpoint=shot.audience_endpoint,
                        performance_objectives=performance_objectives,
                        camera_purpose=shot.camera.narrative_purpose,
                        edit_intent=shot.edit_intent or treated.editorial_priority,
                        sound_intent=treated.sound_priority,
                        lighting_intent=light_values,
                        continuity_contract={
                            "entry_state": shot.entry_state.model_dump(mode="json"),
                            "exit_state": shot.exit_state.model_dump(mode="json"),
                            "camera_side": shot.camera.camera_side,
                            "motion_axis": shot.entry_state.motion_axis,
                        },
                    )
                )

        return CreativeIntentGraph(
            project_id=project_id,
            scenes=scenes,
            shots=shot_intents,
            mapping_findings=mapping_findings,
        )


class CameraDiagnostics:
    _SHOT_SIZE_ORDER = {
        "extreme wide": 0,
        "wide": 1,
        "full": 2,
        "medium wide": 3,
        "medium": 4,
        "medium close-up": 5,
        "close-up": 6,
        "extreme close-up": 7,
    }

    @staticmethod
    def _same_scene_pairs(shots: list[ShotSpec]):
        for previous, current in zip(shots, shots[1:]):
            if previous.scene_id == current.scene_id:
                yield previous, current

    def validate(
        self,
        project_id: str,
        shots: ShotSpecBatch,
    ) -> CameraDiagnosticsReport:
        findings: list[CraftFinding] = []
        ordered = shots.shots

        for shot in ordered:
            move = shot.camera.movement
            if move.kind != "static" and not move.purpose.strip():
                findings.append(
                    CraftFinding(
                        code="UNMOTIVATED_CAMERA_MOVE",
                        severity=CraftSeverity.BLOCKER,
                        shot_id=shot.shot_id,
                        scene_id=shot.scene_id,
                        message="camera movement requires narrative/information/emotional purpose",
                    )
                )
            if (
                shot.camera.camera_side
                and shot.entry_state.camera_side
                and shot.camera.camera_side != shot.entry_state.camera_side
            ):
                findings.append(
                    CraftFinding(
                        code="CAMERA_SIDE_CONTRACT_MISMATCH",
                        severity=CraftSeverity.BLOCKER,
                        shot_id=shot.shot_id,
                        scene_id=shot.scene_id,
                        message="camera specification and world-state camera side disagree",
                        evidence={
                            "camera": shot.camera.camera_side,
                            "world": shot.entry_state.camera_side,
                        },
                    )
                )
            for subject_id, state in shot.entry_state.characters.items():
                if state.eyeline is None:
                    findings.append(
                        CraftFinding(
                            code="EYELINE_UNSPECIFIED",
                            severity=CraftSeverity.WARNING,
                            shot_id=shot.shot_id,
                            scene_id=shot.scene_id,
                            message=f"{subject_id} has no eyeline target",
                        )
                    )

        for previous, current in self._same_scene_pairs(ordered):
            prev_side = previous.camera.camera_side or previous.entry_state.camera_side
            curr_side = current.camera.camera_side or current.entry_state.camera_side
            if prev_side and curr_side and prev_side != curr_side:
                findings.append(
                    CraftFinding(
                        code="POSSIBLE_180_AXIS_CROSS",
                        severity=CraftSeverity.BLOCKER,
                        shot_id=current.shot_id,
                        scene_id=current.scene_id,
                        message="camera side changed inside one scene without an encoded axis reset",
                        evidence={"from": prev_side, "to": curr_side},
                    )
                )

            prev_axis = previous.entry_state.motion_axis
            curr_axis = current.entry_state.motion_axis
            if prev_axis and curr_axis and prev_axis != curr_axis:
                findings.append(
                    CraftFinding(
                        code="SCREEN_DIRECTION_AXIS_CHANGED",
                        severity=CraftSeverity.WARNING,
                        shot_id=current.shot_id,
                        scene_id=current.scene_id,
                        message="motion axis changed across adjacent coverage",
                        evidence={"from": prev_axis, "to": curr_axis},
                    )
                )

            if (
                previous.camera.lens_mm is not None
                and current.camera.lens_mm is not None
            ):
                delta = abs(current.camera.lens_mm - previous.camera.lens_mm)
                ratio = max(
                    current.camera.lens_mm,
                    previous.camera.lens_mm,
                ) / min(
                    current.camera.lens_mm,
                    previous.camera.lens_mm,
                )
                if delta < 8 and previous.camera.shot_size != current.camera.shot_size:
                    findings.append(
                        CraftFinding(
                            code="SMALL_LENS_CHANGE_VERIFY_JUMP_CUT",
                            severity=CraftSeverity.WARNING,
                            shot_id=current.shot_id,
                            scene_id=current.scene_id,
                            message="small focal-length change with framing change may read as a lens/framing jump",
                            evidence={"delta_mm": delta},
                        )
                    )
                if ratio >= 2.5:
                    findings.append(
                        CraftFinding(
                            code="EXTREME_LENS_JUMP",
                            severity=CraftSeverity.WARNING,
                            shot_id=current.shot_id,
                            scene_id=current.scene_id,
                            message="large focal-length jump should be motivated by perspective or emotion",
                            evidence={
                                "from_mm": previous.camera.lens_mm,
                                "to_mm": current.camera.lens_mm,
                            },
                        )
                    )

            a = self._SHOT_SIZE_ORDER.get(previous.camera.shot_size.lower())
            b = self._SHOT_SIZE_ORDER.get(current.camera.shot_size.lower())
            if a is not None and b is not None and abs(a - b) == 0:
                findings.append(
                    CraftFinding(
                        code="REPEATED_SHOT_SIZE_VERIFY_PURPOSE",
                        severity=CraftSeverity.INFO,
                        shot_id=current.shot_id,
                        scene_id=current.scene_id,
                        message="adjacent coverage repeats shot size; verify angle/performance/information change justifies the cut",
                    )
                )

        return CameraDiagnosticsReport(
            project_id=project_id,
            findings=findings,
            checked_shots=len(ordered),
        )


class PerformanceDirectionCompiler:
    def compile(
        self,
        project_id: str,
        shots: ShotSpecBatch,
    ) -> PerformanceDirectionPlan:
        beats: list[PerformanceDirectionBeat] = []
        findings: list[CraftFinding] = []
        for shot in shots.shots:
            for subject_id, perf in shot.performance.items():
                action_verb = perf.action_verb.strip()
                if not perf.objective.strip():
                    findings.append(
                        CraftFinding(
                            code="PERFORMANCE_OBJECTIVE_MISSING",
                            severity=CraftSeverity.BLOCKER,
                            shot_id=shot.shot_id,
                            scene_id=shot.scene_id,
                            message=f"{subject_id} has no playable objective",
                        )
                    )
                if not action_verb:
                    findings.append(
                        CraftFinding(
                            code="PERFORMANCE_ACTION_VERB_MISSING",
                            severity=CraftSeverity.BLOCKER,
                            shot_id=shot.shot_id,
                            scene_id=shot.scene_id,
                            message=f"{subject_id} has no action verb",
                        )
                    )
                state = shot.entry_state.characters.get(subject_id)
                gaze = state.eyeline if state is not None else None
                micro = perf.micro_expression or {}
                body = perf.body_behavior or {}
                listening = perf.listening_behavior or {}
                beats.append(
                    PerformanceDirectionBeat(
                        shot_id=shot.shot_id,
                        scene_id=shot.scene_id,
                        subject_id=subject_id,
                        objective=perf.objective,
                        action_verb=perf.action_verb,
                        gaze_target=gaze,
                        expression_intent=str(micro.get("eyes") or perf.outward_mask or ""),
                        gesture_intent=str(body.get("gesture") or ""),
                        reaction_trigger=str(listening.get("trigger") or "") or None,
                        reaction_delay_seconds=None,
                        body_mechanics=[
                            "preserve foot contact during planted phase",
                            "maintain believable balance and weight transfer",
                            "prop contacts must align in world space",
                        ],
                        timing_notes=[
                            "stimulus precedes recognition and response",
                            "protect readable holds after major emotional/information changes",
                        ],
                    )
                )
        return PerformanceDirectionPlan(
            project_id=project_id,
            beats=beats,
            findings=findings,
        )


class LightingColorIntentCompiler:
    def compile(
        self,
        project_id: str,
        shots: ShotSpecBatch,
    ) -> LightingColorIntentPlan:
        return LightingColorIntentPlan(
            project_id=project_id,
            shots=[
                ShotLightingColorIntent(
                    shot_id=shot.shot_id,
                    scene_id=shot.scene_id,
                    narrative_purpose=shot.narrative_purpose,
                    light_state=shot.entry_state.light_state,
                    time_of_day=shot.entry_state.time_of_day,
                )
                for shot in shots.shots
            ],
            global_rules=[
                "readability and continuity before decorative contrast",
                "protect recurring character identity and material colors",
                "match adjacent shots before local polish",
                "exposure changes require motivated environment or story change",
            ],
        )


class SoundSpottingCompiler:
    def compile(
        self,
        project_id: str,
        shots: ShotSpecBatch,
        director: DirectorPlan,
    ) -> SoundSpottingPlan:
        direction = {scene.scene_id: scene for scene in director.scenes}
        spots: list[SoundSpot] = []
        for shot in shots.shots:
            scene = direction.get(shot.scene_id)
            foley = [
                f"{beat.actor}:{beat.action}"
                for beat in shot.action_beats
                if beat.action.strip()
            ]
            spots.append(
                SoundSpot(
                    spot_id=f"SND_{shot.shot_id}",
                    shot_id=shot.shot_id,
                    scene_id=shot.scene_id,
                    purpose=(
                        scene.sound_intent
                        if scene and scene.sound_intent
                        else "support shot narrative purpose and spatial continuity"
                    ),
                    dialogue_priority=True,
                    ambience_intent=(
                        f"stable ambience for {shot.entry_state.location_id or 'scene'}"
                    ),
                    foley_events=foley,
                    music_intent="support scene turn; duck under dialogue and important Foley",
                )
            )
        return SoundSpottingPlan(
            project_id=project_id,
            spots=spots,
            global_rules=[
                "dialogue intelligibility first",
                "ambience follows acoustic location continuity",
                "Foley/SFX reinforce causality and weight",
                "music does not pre-empt emotional information",
                "silence is an intentional tool, not a missing layer",
            ],
        )


class AudioIntentCompiler:
    def compile(
        self,
        project_id: str,
        spotting: SoundSpottingPlan,
        shots: ShotSpecBatch,
    ) -> AudioPlan:
        offsets: dict[str, tuple[float, float]] = {}
        cursor = 0.0
        for shot in shots.shots:
            offsets[shot.shot_id] = (
                cursor,
                float(shot.duration_seconds),
            )
            cursor += float(shot.duration_seconds)

        cues: list[AudioCue] = []
        for spot in spotting.spots:
            start, duration = offsets.get(spot.shot_id, (0.0, 1.0))
            cues.append(
                AudioCue(
                    cue_id=f"{spot.spot_id}_AMB",
                    role=AudioRole.AMBIENCE,
                    segment_id=spot.scene_id,
                    start_seconds=start,
                    duration_seconds=max(duration, 0.01),
                    purpose=spot.ambience_intent,
                )
            )
            for index, event in enumerate(spot.foley_events):
                event_start = min(
                    start + (index + 1) * 0.25,
                    max(start, start + duration - 0.05),
                )
                cues.append(
                    AudioCue(
                        cue_id=f"{spot.spot_id}_FOLEY_{index:02d}",
                        role=AudioRole.FOLEY,
                        segment_id=spot.scene_id,
                        start_seconds=max(0.0, event_start),
                        duration_seconds=0.2,
                        purpose=event,
                    )
                )
        return AudioPlan(
            project_id=project_id,
            cues=cues,
        )


class ColorIntentCompiler:
    def compile(
        self,
        project_id: str,
        intent: LightingColorIntentPlan,
    ) -> ColorPlan:
        return ColorPlan(
            project_id=project_id,
            bible=ColorBible(
                look_description=(
                    "preserve approved project visual identity and "
                    "scene emotional intent"
                ),
                contrast_intent=(
                    "readability and continuity before decorative contrast"
                ),
                saturation_intent=(
                    "stable identity/material color; no arbitrary shot drift"
                ),
                skin_or_identity_protection=[
                    "recurring character identity",
                    "costume/material colors",
                    "important props",
                ],
            ),
            shots=[
                ShotColorState(
                    shot_id=item.shot_id,
                    source_space="scene-linear",
                    approved=False,
                    notes=[
                        f"scene_id={item.scene_id}",
                        f"light_state={item.light_state or 'unspecified'}",
                        f"time_of_day={item.time_of_day or 'unspecified'}",
                        item.exposure_priority,
                        item.continuity_priority,
                        item.color_intent,
                        (
                            "PLAN_ONLY: current ffmpeg finishing path does "
                            "not claim shot-by-shot creative grading"
                        ),
                    ],
                )
                for item in intent.shots
            ],
        )


class CraftExecutionCompiler:
    def compile(
        self,
        *,
        project_id: str,
        story: StoryArchitecture,
        script: ScriptSpec,
        director: DirectorPlan,
        treatment: DirectorTreatment,
        shots: ShotSpecBatch,
        cinematography: CinematographyBible,
        animatic: AnimaticPlan,
    ) -> CraftExecutionBundle:
        del cinematography, animatic  # contracts are upstream requirements; shot data is canonical here.
        intent = CreativeIntentCompiler().compile(
            project_id=project_id,
            story=story,
            script=script,
            director=director,
            treatment=treatment,
            shots=shots,
        )
        camera = CameraDiagnostics().validate(project_id, shots)
        performance = PerformanceDirectionCompiler().compile(
            project_id,
            shots,
        )
        lighting_color = LightingColorIntentCompiler().compile(
            project_id,
            shots,
        )
        sound = SoundSpottingCompiler().compile(
            project_id,
            shots,
            director,
        )
        return CraftExecutionBundle(
            project_id=project_id,
            creative_intent_graph=intent,
            camera_diagnostics=camera,
            performance_direction=performance,
            lighting_color_intent=lighting_color,
            sound_spotting=sound,
        )
