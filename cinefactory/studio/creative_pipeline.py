from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from cinefactory.domain.models import DirectorPlan, ScriptSpec, ShotSpecBatch, StorySpec

from .project_dna import ProjectDNA


class ReviewSeverity(StrEnum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CreativeDevelopmentBrief(BaseModel):
    project_id: str
    niche_id: str | None = None
    audience_promise: str
    premise: str
    theme_question: str
    emotional_promise: str
    differentiation_axes: list[str] = Field(default_factory=list)
    creative_constraints: list[str] = Field(default_factory=list)
    research_evidence_refs: list[str] = Field(default_factory=list)
    greenlight_questions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_clear_promise(self) -> "CreativeDevelopmentBrief":
        if len(self.audience_promise.strip()) < 8:
            raise ValueError("creative development requires a clear audience promise")
        if len(self.premise.strip()) < 8:
            raise ValueError("creative development requires a usable premise")
        return self


class StoryArchitectureBeat(BaseModel):
    beat_id: str
    purpose: str
    change: str
    audience_question: str | None = None
    setup_ids: list[str] = Field(default_factory=list)
    payoff_ids: list[str] = Field(default_factory=list)


class StoryArchitecture(BaseModel):
    project_id: str
    title: str
    premise: str
    theme: str | None = None
    protagonist_goal: str
    central_conflict: str
    ending_state: str
    beats: list[StoryArchitectureBeat] = Field(min_length=1)
    causality_rules: list[str] = Field(default_factory=list)
    escalation_rules: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_beats(self) -> "StoryArchitecture":
        ids = [beat.beat_id for beat in self.beats]
        if len(ids) != len(set(ids)):
            raise ValueError("story architecture beat ids must be unique")
        return self


class ScriptReviewIssue(BaseModel):
    code: str
    severity: ReviewSeverity
    scene_id: str | None = None
    problem: str
    evidence: str
    impact: str
    recommended_action: str


class ScriptReviewReport(BaseModel):
    project_id: str
    passed: bool
    issues: list[ScriptReviewIssue] = Field(default_factory=list)
    scene_count: int = Field(ge=1)
    dialogue_line_count: int = Field(ge=0)
    action_line_count: int = Field(ge=0)
    independent_reviewer: str = "SCRIPT_LOGIC"

    @model_validator(mode="after")
    def pass_matches_blockers(self) -> "ScriptReviewReport":
        blocking = any(
            issue.severity in {ReviewSeverity.HIGH, ReviewSeverity.CRITICAL}
            for issue in self.issues
        )
        if self.passed == blocking:
            raise ValueError("script review pass state does not match blocking issues")
        return self


class DirectorSceneTreatment(BaseModel):
    scene_id: str
    purpose: str
    audience_know: str
    audience_feel: str
    point_of_view: str
    dramatic_turn: str | None = None
    performance_priority: str
    camera_priority: str
    sound_priority: str
    editorial_priority: str


class DirectorTreatment(BaseModel):
    project_id: str
    visual_concept: str
    story_priority: str = "story_before_spectacle"
    point_of_view_policy: list[str] = Field(default_factory=list)
    performance_principles: list[str] = Field(default_factory=list)
    camera_principles: list[str] = Field(default_factory=list)
    editorial_principles: list[str] = Field(default_factory=list)
    sound_principles: list[str] = Field(default_factory=list)
    scenes: list[DirectorSceneTreatment] = Field(default_factory=list)


class StoryboardPanel(BaseModel):
    panel_id: str
    shot_id: str
    scene_id: str
    narrative_purpose: str
    audience_endpoint: str
    shot_size: str
    lens_mm: float | None = None
    movement: str
    movement_purpose: str | None = None
    subjects: list[str] = Field(default_factory=list)
    action_summary: list[str] = Field(default_factory=list)
    continuity_in: dict[str, Any] = Field(default_factory=dict)
    continuity_out: dict[str, Any] = Field(default_factory=dict)
    edit_intent: str | None = None


class SemanticStoryboard(BaseModel):
    project_id: str
    panels: list[StoryboardPanel] = Field(min_length=1)
    coverage_findings: list[str] = Field(default_factory=list)


class AnimaticBeat(BaseModel):
    shot_id: str
    scene_id: str
    order: int = Field(ge=0)
    duration_seconds: float = Field(gt=0)
    cut_reason: str
    audio_intent: str | None = None


class AnimaticPlan(BaseModel):
    project_id: str
    beats: list[AnimaticBeat] = Field(min_length=1)
    total_duration_seconds: float = Field(gt=0)
    pacing_findings: list[str] = Field(default_factory=list)


class SceneCinematographyStrategy(BaseModel):
    scene_id: str
    shot_ids: list[str] = Field(min_length=1)
    lens_set_mm: list[float] = Field(default_factory=list)
    movement_policy: list[str] = Field(default_factory=list)
    focus_policy: list[str] = Field(default_factory=list)
    screen_direction_policy: list[str] = Field(default_factory=list)
    lighting_intent: list[str] = Field(default_factory=list)


class CinematographyBible(BaseModel):
    project_id: str
    global_grammar: list[str] = Field(default_factory=list)
    lens_policy: list[str] = Field(default_factory=list)
    movement_policy: list[str] = Field(default_factory=list)
    continuity_policy: list[str] = Field(default_factory=list)
    scenes: list[SceneCinematographyStrategy] = Field(default_factory=list)


class LayoutShotPlan(BaseModel):
    shot_id: str
    scene_id: str
    camera_side: str | None = None
    motion_axis: str | None = None
    required_characters: list[str] = Field(default_factory=list)
    required_props: list[str] = Field(default_factory=list)
    camera_movement: str
    movement_window: tuple[float | None, float | None] = (None, None)
    focus_target: str | None = None
    technical_notes: list[str] = Field(default_factory=list)


class LayoutTechvisPlan(BaseModel):
    project_id: str
    shots: list[LayoutShotPlan] = Field(min_length=1)
    passed: bool
    findings: list[str] = Field(default_factory=list)
    technical_constraints: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def pass_matches_findings(self) -> "LayoutTechvisPlan":
        blockers = [x for x in self.findings if x.startswith("BLOCKER:")]
        if self.passed == bool(blockers):
            raise ValueError("layout/techvis pass state does not match blockers")
        return self


class CreativeReviewReport(BaseModel):
    project_id: str
    passed: bool
    review_departments: list[str] = Field(
        default_factory=lambda: [
            "SCRIPT_LOGIC",
            "DIRECTION",
            "EDITORIAL",
            "CINEMATOGRAPHY",
            "PRODUCTION_DESIGN",
        ]
    )
    blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    approved_for_technical_direction: bool = False

    @model_validator(mode="after")
    def coherent_approval(self) -> "CreativeReviewReport":
        expected = not self.blockers
        if self.passed != expected:
            raise ValueError("creative review pass state must reflect blockers")
        if self.approved_for_technical_direction != self.passed:
            raise ValueError("technical-direction approval must match creative review")
        return self


class CreativeDevelopmentCompiler:
    def compile(
        self,
        *,
        project_id: str,
        prompt: str,
        niche_id: str | None,
        seo_brief: dict[str, Any],
        corporate_preflight: dict[str, Any],
    ) -> CreativeDevelopmentBrief:
        audience = (
            f"Deliver the core promise of {niche_id} to the intended viewer"
            if niche_id
            else "Deliver a clear, coherent and original viewer experience"
        )
        premise = prompt.strip()
        if len(premise) < 8:
            premise = f"Original project based on request: {prompt.strip()}"
        return CreativeDevelopmentBrief(
            project_id=project_id,
            niche_id=niche_id,
            audience_promise=audience,
            premise=premise,
            theme_question="What should the viewer understand or feel differently by the end?",
            emotional_promise="Each major unit must create a deliberate information or emotional change.",
            differentiation_axes=[
                "original story/content decisions",
                "clearer audience promise",
                "stronger craft consistency",
                "production repeatability",
            ],
            creative_constraints=[
                "story/content intent before spectacle",
                "no unmotivated filler",
                "no direct copying of competitor expression",
                "camera movement requires purpose",
            ],
            research_evidence_refs=[
                "corporate_preflight",
                "seo_discovery_brief",
            ],
            greenlight_questions=[
                "Why should this project exist now?",
                "What is the viewer promise?",
                "What is meaningfully differentiated?",
                "Can the promise be produced reliably?",
            ],
        )


class StoryArchitectureCompiler:
    def compile(self, project_id: str, story: StorySpec) -> StoryArchitecture:
        beats = [
            StoryArchitectureBeat(
                beat_id=item.beat_id,
                purpose=item.purpose,
                change=item.change,
                audience_question=item.audience_question,
            )
            for item in story.beats
        ]
        return StoryArchitecture(
            project_id=project_id,
            title=story.title,
            premise=story.premise,
            theme=story.theme,
            protagonist_goal=story.protagonist_goal,
            central_conflict=story.central_conflict,
            ending_state=story.ending_state,
            beats=beats,
            causality_rules=[
                "each beat must be caused by prior state or deliberate character choice",
                "major reveals must have setup or motivated discovery",
                "scene outcome must alter knowledge, emotion, power or situation",
            ],
            escalation_rules=[
                "stakes or constraint should change across major beats",
                "repetition without escalation requires explicit purpose",
            ],
        )


class ScriptReviewer:
    def review(
        self,
        project_id: str,
        script: ScriptSpec,
        architecture: StoryArchitecture,
    ) -> ScriptReviewReport:
        issues: list[ScriptReviewIssue] = []
        dialogue_count = 0
        action_count = 0
        for scene in script.scenes:
            dialogue_count += len(scene.dialogue)
            action_count += len(scene.action)
            if not scene.dramatic_event.strip():
                issues.append(
                    ScriptReviewIssue(
                        code="SCENE_DRAMATIC_EVENT_MISSING",
                        severity=ReviewSeverity.HIGH,
                        scene_id=scene.scene_id,
                        problem="scene has no dramatic event",
                        evidence="dramatic_event is empty",
                        impact="scene cannot be directed around a clear change",
                        recommended_action="define the event/change before production",
                    )
                )
            if not scene.action and not scene.dialogue:
                issues.append(
                    ScriptReviewIssue(
                        code="SCENE_CONTENT_EMPTY",
                        severity=ReviewSeverity.HIGH,
                        scene_id=scene.scene_id,
                        problem="scene contains neither action nor dialogue",
                        evidence="action/dialogue arrays are empty",
                        impact="scene has no playable content",
                        recommended_action="write playable action/dialogue or remove the scene",
                    )
                )
            if not scene.location_id.strip():
                issues.append(
                    ScriptReviewIssue(
                        code="SCENE_LOCATION_MISSING",
                        severity=ReviewSeverity.MEDIUM,
                        scene_id=scene.scene_id,
                        problem="scene has no production location id",
                        evidence="location_id is empty",
                        impact="production design and layout cannot lock geography",
                        recommended_action="assign a stable location id",
                    )
                )
        if not architecture.central_conflict.strip():
            issues.append(
                ScriptReviewIssue(
                    code="CENTRAL_CONFLICT_MISSING",
                    severity=ReviewSeverity.CRITICAL,
                    problem="story architecture has no central conflict",
                    evidence="central_conflict is empty",
                    impact="story lacks a governing source of pressure",
                    recommended_action="define central conflict before directing",
                )
            )
        blocking = any(
            issue.severity in {ReviewSeverity.HIGH, ReviewSeverity.CRITICAL}
            for issue in issues
        )
        return ScriptReviewReport(
            project_id=project_id,
            passed=not blocking,
            issues=issues,
            scene_count=len(script.scenes),
            dialogue_line_count=dialogue_count,
            action_line_count=action_count,
        )


class DirectorTreatmentCompiler:
    def compile(
        self,
        project_id: str,
        script: ScriptSpec,
        director: DirectorPlan,
        dna: ProjectDNA,
    ) -> DirectorTreatment:
        by_scene = {scene.scene_id: scene for scene in script.scenes}
        scenes: list[DirectorSceneTreatment] = []
        for scene in director.scenes:
            script_scene = by_scene.get(scene.scene_id)
            purpose = (
                script_scene.dramatic_event
                if script_scene is not None
                else scene.dramatic_event
            )
            scenes.append(
                DirectorSceneTreatment(
                    scene_id=scene.scene_id,
                    purpose=purpose,
                    audience_know=scene.audience_know,
                    audience_feel=scene.audience_feel,
                    point_of_view="character_or_information_priority",
                    dramatic_turn=scene.power_turn,
                    performance_priority=(
                        next(iter(scene.performance_notes.values()), "readable objective and reaction")
                    ),
                    camera_priority=scene.cinematography_intent,
                    sound_priority=scene.sound_intent or "support perspective and dramatic change",
                    editorial_priority=scene.edit_intent or "cut on information, emotion, action or rhythm",
                )
            )
        return DirectorTreatment(
            project_id=project_id,
            visual_concept=director.visual_concept,
            point_of_view_policy=[
                "declare whose experience or information controls each scene",
                "do not reveal information earlier than the dramatic design requires",
            ],
            performance_principles=[
                "objective before gesture",
                "reaction requires trigger",
                "listening behavior is part of performance",
                *director.performance_grammar,
            ],
            camera_principles=[
                "no shot without narrative/emotional/informational purpose",
                "no camera movement without motivation",
                *dna.camera.grammar,
                *dna.camera.movement_policy,
                *director.camera_grammar,
            ],
            editorial_principles=[
                "review shots in sequence, not isolation",
                *dna.editing.pacing_principles,
                *director.editing_grammar,
            ],
            sound_principles=[
                "sound perspective follows story perspective",
                *director.sound_grammar,
            ],
            scenes=scenes,
        )


class StoryboardAnimaticCompiler:
    def compile(
        self,
        project_id: str,
        shots: ShotSpecBatch,
    ) -> tuple[SemanticStoryboard, AnimaticPlan]:
        panels: list[StoryboardPanel] = []
        beats: list[AnimaticBeat] = []
        findings: list[str] = []
        seen_scenes: dict[str, int] = {}
        for order, shot in enumerate(shots.shots):
            seen_scenes[shot.scene_id] = seen_scenes.get(shot.scene_id, 0) + 1
            characters = sorted(shot.entry_state.characters)
            actions = [
                f"{beat.actor}:{beat.action}"
                + (f"->{beat.target}" if beat.target else "")
                for beat in shot.action_beats
            ]
            panels.append(
                StoryboardPanel(
                    panel_id=f"PNL_{shot.shot_id}",
                    shot_id=shot.shot_id,
                    scene_id=shot.scene_id,
                    narrative_purpose=shot.narrative_purpose,
                    audience_endpoint=shot.audience_endpoint,
                    shot_size=shot.camera.shot_size,
                    lens_mm=shot.camera.lens_mm,
                    movement=shot.camera.movement.kind,
                    movement_purpose=shot.camera.movement.purpose,
                    subjects=characters,
                    action_summary=actions,
                    continuity_in=shot.entry_state.model_dump(mode="json"),
                    continuity_out=shot.exit_state.model_dump(mode="json"),
                    edit_intent=shot.edit_intent,
                )
            )
            beats.append(
                AnimaticBeat(
                    shot_id=shot.shot_id,
                    scene_id=shot.scene_id,
                    order=order,
                    duration_seconds=shot.duration_seconds,
                    cut_reason=shot.edit_intent or "preserve dramatic beat",
                )
            )
        for scene_id, count in seen_scenes.items():
            if count == 1:
                findings.append(
                    f"{scene_id}:SINGLE_SHOT_SCENE_VERIFY_COVERAGE_IS_INTENTIONAL"
                )
        total = sum(beat.duration_seconds for beat in beats)
        return (
            SemanticStoryboard(
                project_id=project_id,
                panels=panels,
                coverage_findings=findings,
            ),
            AnimaticPlan(
                project_id=project_id,
                beats=beats,
                total_duration_seconds=total,
                pacing_findings=[],
            ),
        )


class CinematographyBibleCompiler:
    def compile(
        self,
        project_id: str,
        shots: ShotSpecBatch,
        dna: ProjectDNA,
    ) -> CinematographyBible:
        by_scene: dict[str, list] = {}
        for shot in shots.shots:
            by_scene.setdefault(shot.scene_id, []).append(shot)
        scenes: list[SceneCinematographyStrategy] = []
        for scene_id, scene_shots in by_scene.items():
            lenses = sorted(
                {
                    float(shot.camera.lens_mm)
                    for shot in scene_shots
                    if shot.camera.lens_mm is not None
                }
            )
            movement = sorted(
                {
                    f"{shot.camera.movement.kind}:{shot.camera.movement.purpose}"
                    for shot in scene_shots
                }
            )
            focus = sorted(
                {
                    shot.camera.focus_target
                    for shot in scene_shots
                    if shot.camera.focus_target
                }
            )
            directions = sorted(
                {
                    shot.entry_state.camera_side
                    for shot in scene_shots
                    if shot.entry_state.camera_side
                }
            )
            lights = sorted(
                {
                    value
                    for shot in scene_shots
                    for value in (
                        shot.entry_state.light_state,
                        shot.entry_state.time_of_day,
                    )
                    if value
                }
            )
            scenes.append(
                SceneCinematographyStrategy(
                    scene_id=scene_id,
                    shot_ids=[shot.shot_id for shot in scene_shots],
                    lens_set_mm=lenses,
                    movement_policy=movement,
                    focus_policy=focus,
                    screen_direction_policy=directions,
                    lighting_intent=lights,
                )
            )
        return CinematographyBible(
            project_id=project_id,
            global_grammar=list(dna.camera.grammar),
            lens_policy=["lens choice must serve perspective, geography or emotion"],
            movement_policy=list(dna.camera.movement_policy),
            continuity_policy=list(dna.camera.continuity_rules),
            scenes=scenes,
        )


class LayoutTechvisCompiler:
    def compile(
        self,
        project_id: str,
        shots: ShotSpecBatch,
    ) -> LayoutTechvisPlan:
        findings: list[str] = []
        plans: list[LayoutShotPlan] = []
        shot_ids = {shot.shot_id for shot in shots.shots}
        for shot in shots.shots:
            if shot.previous_shot_id and shot.previous_shot_id not in shot_ids:
                findings.append(
                    f"BLOCKER:{shot.shot_id}:PREVIOUS_SHOT_MISSING:{shot.previous_shot_id}"
                )
            if shot.next_shot_id and shot.next_shot_id not in shot_ids:
                findings.append(
                    f"BLOCKER:{shot.shot_id}:NEXT_SHOT_MISSING:{shot.next_shot_id}"
                )
            if (
                shot.previous_shot_id
                and shot.previous_shot_id == shot.shot_id
            ):
                findings.append(
                    f"BLOCKER:{shot.shot_id}:SELF_PREVIOUS_LINK"
                )
            if shot.camera.movement.kind != "static" and not shot.camera.movement.purpose:
                findings.append(
                    f"BLOCKER:{shot.shot_id}:UNMOTIVATED_CAMERA_MOVE"
                )
            required_props = set(shot.entry_state.props)
            for state in shot.entry_state.characters.values():
                required_props.update(state.held_props)
            plans.append(
                LayoutShotPlan(
                    shot_id=shot.shot_id,
                    scene_id=shot.scene_id,
                    camera_side=shot.entry_state.camera_side,
                    motion_axis=shot.entry_state.motion_axis,
                    required_characters=sorted(shot.entry_state.characters),
                    required_props=sorted(required_props),
                    camera_movement=shot.camera.movement.kind,
                    movement_window=(
                        shot.camera.movement.start_second,
                        shot.camera.movement.end_second,
                    ),
                    focus_target=shot.camera.focus_target,
                    technical_notes=[
                        "verify camera collision",
                        "verify subject visibility and eyeline",
                        "verify action fits shot duration",
                    ],
                )
            )
        return LayoutTechvisPlan(
            project_id=project_id,
            shots=plans,
            passed=not any(item.startswith("BLOCKER:") for item in findings),
            findings=findings,
            technical_constraints=[
                "preserve approved camera side unless explicit axis reset is approved",
                "camera path must be collision-free",
                "hero performance must remain readable in final framing",
            ],
        )


class CreativeReviewConference:
    def review(
        self,
        *,
        project_id: str,
        script_review: ScriptReviewReport,
        storyboard: SemanticStoryboard,
        animatic: AnimaticPlan,
        cinematography: CinematographyBible,
        layout_techvis: LayoutTechvisPlan,
        previs_passed: bool,
    ) -> CreativeReviewReport:
        blockers: list[str] = []
        warnings: list[str] = []
        if not script_review.passed:
            blockers.append("SCRIPT_REVIEW_NOT_APPROVED")
        if not storyboard.panels:
            blockers.append("STORYBOARD_EMPTY")
        if animatic.total_duration_seconds <= 0:
            blockers.append("ANIMATIC_DURATION_INVALID")
        if not cinematography.scenes:
            blockers.append("CINEMATOGRAPHY_BIBLE_EMPTY")
        if not layout_techvis.passed:
            blockers.extend(layout_techvis.findings)
        if not previs_passed:
            blockers.append("PREVIS_NOT_APPROVED")
        warnings.extend(storyboard.coverage_findings)
        warnings.extend(animatic.pacing_findings)
        return CreativeReviewReport(
            project_id=project_id,
            passed=not blockers,
            blockers=list(dict.fromkeys(blockers)),
            warnings=list(dict.fromkeys(warnings)),
            approved_for_technical_direction=not blockers,
        )
