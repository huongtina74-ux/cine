from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal
from pydantic import BaseModel, Field, model_validator


class Severity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Vec3(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def as_tuple(self):
        return (self.x, self.y, self.z)


class Euler(Vec3):
    pass


class TransformSpec(BaseModel):
    location: Vec3 = Field(default_factory=Vec3)
    rotation_euler: Euler = Field(default_factory=Euler)
    scale: Vec3 = Field(default_factory=lambda: Vec3(x=1, y=1, z=1))


class CharacterRigDefinition(BaseModel):
    rig_id: str
    source_path: str | None = None
    collection: str | None = None
    armature: str | None = None
    skeleton_profile: str = "BLOCK_HUMANOID_V1"
    style: Literal["DEBUG_BLOCK", "MINECRAFT", "ROBLOX_R6", "ROBLOX_R15"] = "DEBUG_BLOCK"
    skin_path: str | None = None
    material_profile: str = "debug_material_profile"
    expression_profile: str = "generic"
    height_scale: float = Field(default=1.0, gt=0.1, le=4.0)
    skeleton_parts: list[str] = Field(default_factory=list)
    accessories: list[str] = Field(default_factory=list)
    identity: dict[str, Any] = Field(default_factory=dict)
    sockets: dict[str, str] = Field(default_factory=dict)
    expression_map: dict[str, str] = Field(default_factory=dict)
    tags: set[str] = Field(default_factory=set)


class AnimationClipDefinition(BaseModel):
    clip_id: str
    source_path: str | None = None
    action_name: str | None = None
    skeleton_profile: str = "BLOCK_HUMANOID_V1"
    duration_frames: int = Field(default=24, ge=1)
    fps: int = Field(default=24, ge=1)
    loopable: bool = False
    layer: Literal["base", "upper", "additive"] = "base"
    root_motion: bool = False
    compatible_skeleton_profiles: list[str] = Field(default_factory=list)
    tags: set[str] = Field(default_factory=set)

    @property
    def duration_seconds(self):
        return self.duration_frames / self.fps


class ExpressionDefinition(BaseModel):
    expression_id: str
    channels: dict[str, float]
    attack_seconds: float = Field(default=.08, ge=0)
    release_seconds: float = Field(default=.12, ge=0)
    tags: set[str] = Field(default_factory=set)


class ReactionRuleDefinition(BaseModel):
    rule_id: str
    trigger: str
    clip_ids: list[str] = Field(default_factory=list)
    expression_ids: list[str] = Field(default_factory=list)
    min_delay_ms: int = Field(default=80, ge=0)
    max_delay_ms: int = Field(default=320, ge=0)
    min_intensity: float = Field(default=.35, ge=0, le=1.5)
    max_intensity: float = Field(default=.9, ge=0, le=1.5)
    probability: float = Field(default=1, ge=0, le=1)

    @model_validator(mode="after")
    def ranges(self):
        if self.max_delay_ms < self.min_delay_ms:
            raise ValueError("max_delay_ms must be >= min_delay_ms")
        if self.max_intensity < self.min_intensity:
            raise ValueError("max_intensity must be >= min_intensity")
        if not self.clip_ids and not self.expression_ids:
            raise ValueError("reaction rule must provide a clip or expression")
        return self


class PropDefinition(BaseModel):
    prop_id: str
    source_path: str | None = None
    collection: str | None = None
    object_name: str | None = None
    style: str = "DEBUG_BLOCK"
    mesh_source: str | None = None
    dimensions: Vec3 = Field(default_factory=Vec3)
    default_socket: str | None = None
    attach_offset: TransformSpec = Field(default_factory=TransformSpec)
    grip_socket: str | None = None
    grip_offset: Vec3 = Field(default_factory=Vec3)
    grip_rotation: Euler = Field(default_factory=Euler)
    camera_interest_point: Vec3 = Field(default_factory=Vec3)
    tags: set[str] = Field(default_factory=set)


class SceneTemplateDefinition(BaseModel):
    scene_id: str
    source_path: str | None = None
    collection: str | None = None
    markers: dict[str, TransformSpec] = Field(default_factory=dict)
    camera_anchors: dict[str, TransformSpec] = Field(default_factory=dict)
    lighting_profile: str = "stylized_day"
    procedural_kind: Literal["room", "classroom", "street", "arena"] = "room"
    style: str = "DEBUG_BLOCK"
    material_profile: str = "debug_material_profile"
    world_scale: float = Field(default=1, gt=0)
    tags: set[str] = Field(default_factory=set)


class CameraPatternDefinition(BaseModel):
    pattern_id: str
    purpose: str
    shot_size: str
    lens_mm: float = Field(default=50, gt=1)
    motion: Literal["static", "push_in", "pull_out", "track", "orbit", "snap"] = "static"
    target_mode: Literal["single", "pair", "group", "prop"] = "single"
    duration_scale: float = Field(default=1, gt=.05)
    framing_margin: float = Field(default=.14, ge=.02, le=.45)
    motion_strength: float = Field(default=.14, ge=0, le=1)
    dof_fstop: float = Field(default=3.5, ge=.5, le=32)
    camera_roll: float = Field(default=0.0, ge=-15.0, le=15.0)
    horizontal_safe_margin: float = Field(default=.10, ge=.02, le=.45)
    vertical_safe_margin: float = Field(default=.10, ge=.02, le=.45)
    min_subject_occupancy: float = Field(default=.08, ge=.01, le=.95)
    max_subject_occupancy: float = Field(default=.86, ge=.05, le=1.0)


class CrowdBehaviorDefinition(BaseModel):
    behavior_id: str
    clip_ids: list[str]
    expression_ids: list[str] = Field(default_factory=list)
    phase_jitter_seconds: float = Field(default=.35, ge=0)
    intensity_min: float = Field(default=.3, ge=0, le=1.5)
    intensity_max: float = Field(default=.8, ge=0, le=1.5)


class EventDefinition(BaseModel):
    event_id: str
    event_type: Literal["vfx", "sound", "vfx_sound"]
    renderer_event: str | None = None
    sound_asset: str | None = None
    duration_seconds: float = Field(default=.25, ge=0)
    tags: set[str] = Field(default_factory=set)


class RenderQualityProfileDefinition(BaseModel):
    profile_id: str
    engine: Literal["BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH", "CYCLES"] = "BLENDER_EEVEE_NEXT"
    render_percentage: int = Field(default=100, ge=25, le=100)
    taa_samples: int = Field(default=64, ge=1, le=512)
    shadow_resolution_scale: float = Field(default=1.0, ge=.25, le=4)
    ambient_occlusion: bool = True
    contact_shadows: bool = True
    soft_shadows: bool = True
    volumetrics: bool = False
    bloom_strength: float = Field(default=.06, ge=0, le=2)
    motion_blur: bool = True
    motion_blur_shutter: float = Field(default=.35, ge=0, le=1)
    use_dof: bool = True
    transparent_film: bool = False
    color_management: str = "AgX"
    look: str = "AgX - Medium High Contrast"
    exposure: float = Field(default=.0, ge=-5, le=5)
    gamma: float = Field(default=1.0, ge=.2, le=3)
    key_light_energy: float = Field(default=1100, ge=0)
    fill_light_energy: float = Field(default=500, ge=0)
    rim_light_energy: float = Field(default=800, ge=0)
    world_strength: float = Field(default=.35, ge=0, le=5)
    bitrate_mbps: int = Field(default=28, ge=2, le=120)
    tags: set[str] = Field(default_factory=set)


class ActorPlacement(BaseModel):
    actor_id: str
    rig_id: str
    marker: str | None = None
    transform: TransformSpec | None = None
    facing_target: str | None = None
    crowd_group: str | None = None


class ActionCue(BaseModel):
    actor_id: str
    clip_id: str
    start_seconds: float = Field(default=0, ge=0)
    end_seconds: float | None = Field(default=None, ge=0)
    speed: float = Field(default=1, gt=.05, le=4)
    intensity: float = Field(default=1, ge=0, le=1.5)
    layer: Literal["base", "upper", "additive"] | None = None
    target: str | None = None
    emit_event: str | None = None


class ExpressionCue(BaseModel):
    actor_id: str
    expression_id: str
    start_seconds: float = Field(default=0, ge=0)
    end_seconds: float | None = Field(default=None, ge=0)
    intensity: float = Field(default=1, ge=0, le=1.5)


class ReactionTrigger(BaseModel):
    trigger: str
    at_seconds: float = Field(ge=0)
    source_actor_id: str | None = None
    target_actor_ids: list[str] = Field(default_factory=list)


class GazeCue(BaseModel):
    actor_id: str
    target_actor_id: str | None = None
    target_point: Vec3 | None = None
    start_seconds: float = Field(default=0, ge=0)
    end_seconds: float | None = Field(default=None, ge=0)
    intensity: float = Field(default=1.0, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def target_required(self) -> "GazeCue":
        if self.target_actor_id is None and self.target_point is None:
            raise ValueError("gaze cue requires target_actor_id or target_point")
        return self


class PropBindingCue(BaseModel):
    prop_id: str
    actor_id: str
    socket: str | None = None
    start_seconds: float = Field(default=0, ge=0)
    end_seconds: float | None = Field(default=None, ge=0)


class CameraIntent(BaseModel):
    purpose: str
    targets: list[str] = Field(default_factory=list)
    prop_id: str | None = None
    pattern_id: str | None = None
    alternatives: int = Field(default=1, ge=1, le=4)
    camera_roll: float = Field(default=0.0, ge=-15.0, le=15.0)


class CrowdCue(BaseModel):
    group_id: str
    actor_ids: list[str]
    behavior_id: str
    start_seconds: float = Field(default=0, ge=0)
    end_seconds: float | None = Field(default=None, ge=0)


class SemanticEventCue(BaseModel):
    event_id: str
    at_seconds: float = Field(ge=0)
    source_actor_id: str | None = None
    target_id: str | None = None
    intensity: float = Field(default=1, ge=0, le=1.5)


class ShotPerformanceSpec(BaseModel):
    shot_id: str
    scene_template_id: str
    duration_seconds: float = Field(gt=.05, le=120)
    actors: list[ActorPlacement] = Field(default_factory=list)
    actions: list[ActionCue] = Field(default_factory=list)
    expressions: list[ExpressionCue] = Field(default_factory=list)
    reactions: list[ReactionTrigger] = Field(default_factory=list)
    gaze: list[GazeCue] = Field(default_factory=list)
    props: list[PropBindingCue] = Field(default_factory=list)
    camera: CameraIntent
    creative_intent: dict[str, Any] = Field(default_factory=dict)
    performance_directives: list[dict[str, Any]] = Field(default_factory=list)
    lighting_intent: dict[str, Any] = Field(default_factory=dict)
    crowd: list[CrowdCue] = Field(default_factory=list)
    events: list[SemanticEventCue] = Field(default_factory=list)
    narrative_purpose: str = ""


class EpisodeSpec(BaseModel):
    project_id: str
    episode_id: str
    title: str
    fps: int = Field(default=24, ge=12, le=60)
    width: int = Field(default=1280, ge=320, le=3840)
    height: int = Field(default=720, ge=180, le=2160)
    render_engine: Literal["BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH", "CYCLES"] = "BLENDER_EEVEE_NEXT"
    quality_profile: str = "rtx3060_quality"
    shots: list[ShotPerformanceSpec]
    blocked_reference_tokens: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ResolvedExpressionCue(BaseModel):
    actor_id: str
    expression_id: str
    start_seconds: float
    end_seconds: float
    intensity: float
    channels: dict[str, float]


class ResolvedReactionCue(BaseModel):
    actor_id: str
    trigger: str
    source_actor_id: str | None = None
    start_seconds: float
    clip_id: str | None = None
    expression_id: str | None = None
    intensity: float


class ResolvedPropBinding(BaseModel):
    prop_id: str
    actor_id: str
    socket: str
    bone_name: str
    start_seconds: float
    end_seconds: float
    attach_offset: TransformSpec


class CameraTake(BaseModel):
    take_id: str
    pattern_id: str
    purpose: str
    targets: list[str]
    lens_mm: float
    motion: str
    start_seconds: float
    end_seconds: float
    anchor: str | None = None
    prop_id: str | None = None
    shot_size: str = "MS"
    target_mode: str = "single"
    framing_margin: float = .14
    motion_strength: float = .14
    dof_fstop: float = 3.5
    camera_roll: float = 0.0
    horizontal_safe_margin: float = .10
    vertical_safe_margin: float = .10
    min_subject_occupancy: float = .08
    max_subject_occupancy: float = .86


class ResolvedCrowdActor(BaseModel):
    actor_id: str
    behavior_id: str
    clip_id: str
    expression_id: str | None = None
    expression_channels: dict[str, float] = Field(default_factory=dict)
    phase_seconds: float
    intensity: float
    start_seconds: float
    end_seconds: float


class ResolvedEventCue(BaseModel):
    event_id: str
    event_type: str
    at_seconds: float
    renderer_event: str | None = None
    sound_asset: str | None = None
    source_actor_id: str | None = None
    target_id: str | None = None
    intensity: float = 1


class CompiledShot(BaseModel):
    shot_id: str
    order: int
    scene: SceneTemplateDefinition
    duration_seconds: float
    fps: int
    width: int
    height: int
    render_engine: str
    render_quality: RenderQualityProfileDefinition = Field(default_factory=lambda: RenderQualityProfileDefinition(profile_id="default"))
    actors: list[ActorPlacement]
    rigs: dict[str, CharacterRigDefinition]
    actions: list[ActionCue]
    clips: dict[str, AnimationClipDefinition]
    expressions: list[ResolvedExpressionCue]
    reactions: list[ResolvedReactionCue]
    gaze: list[GazeCue] = Field(default_factory=list)
    props: list[ResolvedPropBinding]
    creative_intent: dict[str, Any] = Field(default_factory=dict)
    performance_directives: list[dict[str, Any]] = Field(default_factory=list)
    lighting_intent: dict[str, Any] = Field(default_factory=dict)
    prop_definitions: dict[str, PropDefinition] = Field(default_factory=dict)
    camera_takes: list[CameraTake]
    crowd: list[ResolvedCrowdActor]
    events: list[ResolvedEventCue]
    output_path: str | None = None
    visual_style: str = "DEBUG_BLOCK"

    @property
    def frame_end(self):
        return max(1, round(self.duration_seconds * self.fps))


class QCFinding(BaseModel):
    code: str
    severity: Severity
    message: str
    shot_id: str | None = None
    repaired: bool = False
    detail: dict[str, Any] = Field(default_factory=dict)


class EpisodeQCReport(BaseModel):
    passed: bool
    findings: list[QCFinding] = Field(default_factory=list)
    repairs_applied: int = 0


class CompiledEpisode(BaseModel):
    project_id: str
    episode_id: str
    title: str
    fps: int
    width: int
    height: int
    shots: list[CompiledShot]
    qc: EpisodeQCReport
    library_fingerprint: str
    output_dir: str | None = None


class BlenderAnimationJob(BaseModel):
    project_id: str
    episode_id: str
    shot: CompiledShot
    output_path: str
    temp_dir: str | None = None
    render_preview: bool = False
    camera_take_id: str | None = None


class FactoryEnqueuePlan(BaseModel):
    render_work_ids: list[str]
    timeline_work_ids: list[str]
    assemble_work_id: str
    qc_work_id: str | None = None
