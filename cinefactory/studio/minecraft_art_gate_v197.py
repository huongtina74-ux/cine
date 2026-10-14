"""v1.6.37 Minecraft professional art/production acceptance gate.

Intent: stop cheap procedural test shots being mislabeled as complete Youtube
animation. Fail closed on missing skin/rig/facial performance/audio/shot coverage.
This is review policy: independent artistic review is always mandatory.
"""
from __future__ import annotations
from pathlib import Path
from pydantic import BaseModel,Field

class MinecraftShotEvidence(BaseModel):
    title:str
    video_path: str | None = None
    resolution_x:int=Field(gt=0)
    resolution_y:int=Field(gt=0)
    fps:int=Field(gt=0)
    duration_seconds:float=Field(ge=0)
    character_count:int=Field(ge=0)
    original_skin_texture_files:list[str]=Field(default_factory=list)
    unique_character_faces:int=Field(default=0,ge=0)
    facial_expression_cues:int=Field(default=0,ge=0)
    mouth_or_viseme_cues:int=Field(default=0,ge=0)
    emotion_acting_keys:int=Field(default=0,ge=0)
    animation_clips:list[str]=Field(default_factory=list)
    articulated_arm_or_leg_pivot:bool=False
    controlled_character_identity:bool=False
    original_world_and_props:bool=False
    camera_shot_count:int=Field(ge=0)
    camera_plan_approved:bool=False
    physically_readable_depth:bool=False
    artistic_lighting_reviewed:bool=False
    dialogue_required:bool=False
    dialogue_audio_present:bool=False
    music_required:bool=False
    music_present:bool=False
    audio_master_loudness_checked:bool=False
    license_clearance_complete:bool=False
    original_story_reviewed:bool=False
    independent_qa_approved:bool=False
    natively_executed_real_media:bool=False
    benchmark_only:bool=False

class MinecraftArtGate(BaseModel):
    decision:str
    hard_blockers:list[str]
    review_requests:list[str]
    potential_stage:str
    video_is_publishable:bool=False

def evaluate_minecraft_art(e:MinecraftShotEvidence)->MinecraftArtGate:
    fail=[]
    need=[]
    if e.benchmark_only:
        fail.append("RENDER_BENCHMARK_CANNOT_BE_RELEASED_AS_FINISHED_EPISODE")
    if e.resolution_x<1920 or e.resolution_y<1080 or e.fps<24:
        fail.append("FINAL_DELIVERY_BELOW_1080P24")
    if e.duration_seconds<30:
        fail.append("MISSING_REAL_30_SECOND_OR_LONGER_ACCEPTANCE_PILOT")
    if e.character_count<2:
        need.append("REQUIRE_CHARACTER_RELATIONSHIP_AND_DIALOGUE_DEPENDING_ON_STORY")
    if len(e.original_skin_texture_files)<e.character_count or not e.original_skin_texture_files:
        fail.append("PRODUCTION_PIXEL_SKIN_TEXTURES_MISSING")
    if e.unique_character_faces<e.character_count or e.facial_expression_cues<2:
        fail.append("NONEXPRESSIVE_GENERIC_FACES")
    if e.mouth_or_viseme_cues==0 and e.dialogue_required:
        fail.append("LIPSYNC_OR_DIALOGUE_MOUTH_MISSING")
    if e.emotion_acting_keys<4 or len(e.animation_clips)<2:
        fail.append("ANIMATION_ACTING_LIBRARY_AND_BEATS_INSUFFICIENT")
    if not e.articulated_arm_or_leg_pivot:
        fail.append("LIMB_RIG_WITH_SHOULDER_ELBOW_HIP_PIVOT_MISSING")
    if not e.controlled_character_identity:
        fail.append("CHARACTER_IDENTITY_NOT_VALIDATED")
    if not e.original_world_and_props:
        fail.append("ORIGINAL_WORLD_OR_PROPS_NOT_VALIDATED")
    if e.camera_shot_count<3 or not e.camera_plan_approved:
        fail.append("DIRECTOR_STORYBOARD_AND_CAMERA_COVERAGE_MISSING")
    if not e.physically_readable_depth or not e.artistic_lighting_reviewed:
        fail.append("SCENE_LIGHTING_DEPTH_AND_READABILITY_UNREVIEWED")
    if e.dialogue_required and not e.dialogue_audio_present:
        fail.append("SCRIPTED_DIALOGUE_AUDIO_MISSING")
    if e.music_required and not e.music_present:
        fail.append("SCRIPTED_MUSIC_MISSING")
    if not e.audio_master_loudness_checked:
        fail.append("AUDIO_POST_QC_MISSING")
    if not e.license_clearance_complete:
        fail.append("MODEL_ASSET_SKIN_SFX_AND_AUDIO_RIGHTS_UNCLEARED")
    if not e.original_story_reviewed:
        fail.append("ORIGINAL_NARRATIVE_ART_DIRECTOR_REVIEW_MISSING")
    if not e.independent_qa_approved:
        fail.append("INDEPENDENT_HUMAN_VIDEO_QC_MISSING")
    if not e.natively_executed_real_media or not e.video_path:
        fail.append("NO_ACTUAL_FINAL_MEDIA_PROVEN")
    return MinecraftArtGate(
        decision="BLOCKED_MINECRAFT_ART_PRODUCTION" if fail else "READY_FOR_SEPARATE_PUBLICATION_AUTHORIZATION",
        hard_blockers=sorted(set(fail)),
        review_requests=need,
        potential_stage=("TECHNICAL_PROTOTYPE" if e.benchmark_only else "ART_REVIEW_CANDIDATE"),
        video_is_publishable=False,
    )
