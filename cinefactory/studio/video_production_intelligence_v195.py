from __future__ import annotations
"""v1.6.35: evidence-level media and video production research conference.

Reuses existing FFmpeg/OpenCV ReferenceVideoDecomposer; does NOT infer the
hidden renderer, rigs, model, sound studio or SOP from final pixels.
Local source must be inside the project root with first-party/rights attested.
Public YouTube metadata uses yt-dlp with exact fixed watch URL only, no video
download, no premium API, no transcript invented from absent subtitles.
"""
import hashlib
import re
from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Literal
from pydantic import BaseModel,Field,model_validator

from .reference_intelligence import (
    ReferenceVideoDecomposer, ReferenceAcquisitionPolicy,
    ReferenceDecomposition,VideoSourceMetadata,
)
from .niche_research_conference_v192 import NicheResearchConference
from .production_tool_catalog_v191 import NICHE_BLUEPRINTS
from .production_selection_council import Stage

VALID_VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")


class VideoProofLevel(StrEnum):
    LOCAL_OWNED_MEDIA_DECODED = "LOCAL_OWNED_MEDIA_DECODED"
    PUBLIC_YOUTUBE_METADATA_ONLY = "PUBLIC_YOUTUBE_METADATA_ONLY"


class VideoReferenceInput(BaseModel):
    niche_id: str
    project_id: str
    source_video_id: str | None = None
    local_file: str | None = None
    youtube_video_id: str | None = None
    first_party_or_authorized_media: bool = False
    analyze_automatic_transcript: bool = False
    max_duration_seconds: int = Field(default=2400,ge=10,le=3600)
    source_is_original_or_licensed: bool = False
    save_raw_copyrighted_media: bool = False
    external_paid_api_allowed: bool = False

    @model_validator(mode="after")
    def enforce_source_policy(self):
        if bool(self.local_file)==bool(self.youtube_video_id):
            raise ValueError("MUST_SUPPLY_EXACTLY_ONE_VIDEO_SOURCE")
        if self.local_file and not self.first_party_or_authorized_media:
            raise ValueError("LOCAL_MEDIA_RIGHTS_ATTESTATION_REQUIRED")
        if self.save_raw_copyrighted_media or self.external_paid_api_allowed:
            raise ValueError("VIDEO_RESEARCH_REJECTS_RAW_COPY_OR_PAID_API")
        if self.analyze_automatic_transcript and self.youtube_video_id:
            raise ValueError("SUBTITLE_CONTENT_NOT_AVAILABLE_VIA_METADATA_ONLY")
        if self.youtube_video_id and not VALID_VIDEO_ID.fullmatch(self.youtube_video_id):
            raise ValueError("YOUTUBE_ID_NOT_CANONICAL")
        return self


class ObservedVideoSignals(BaseModel):
    proof_level: VideoProofLevel
    video_id: str
    source_sha256: str | None = None
    decoded_media_observed: bool = False
    audiovisual_analysis_complete: bool = False
    metadata_only: bool = True
    video_duration_seconds: float | None = None
    video_frame_count: int | None = None
    image_width: int | None = None
    image_height: int | None = None
    scene_cuts: int | None = None
    cuts_per_minute: float | None = None
    camera_motion_proxy: str | None = None
    camera_motion_confidence: float | None = None
    measured_silence_ratio: float | None = None
    audio_stream_analyzed: bool = False
    transcript_cues_analyzed: bool = False
    video_engine_identified: bool = False
    character_rig_identified: bool = False
    competitor_original_media_retained: bool = False
    views_public_metadata: int | None = None
    upload_date_public_metadata: str | None = None
    source_channel_public_metadata: str | None = None
    notes: list[str] = Field(default_factory=list)


class ProductionMethodPossibility(BaseModel):
    method_family: str
    status: Literal["CANDIDATE_NOT_DEDUCED_FROM_PIXELS"]="CANDIDATE_NOT_DEDUCED_FROM_PIXELS"
    supporting_observation: str | None = None
    cannot_conclude: list[str] = Field(min_length=1)
    next_validation: str
    executable_qualified: bool = False
    production_approved: bool = False


class ProductionObservationHandoff(BaseModel):
    niche_id: str
    project_id: str
    video_id: str
    proof_level: VideoProofLevel
    observations: ObservedVideoSignals
    potential_method_families: list[ProductionMethodPossibility]
    department_study_requirements: list[str]
    recommended_tests: list[str]
    observation_review_flags: list[str] = Field(default_factory=list)
    blocked_capabilities: list[str]
    infer_hidden_production_pipeline: bool = False
    production_method_selected: bool = False
    content_or_music_rights_reviewed: bool = False
    human_visual_quality_reviewed: bool = False
    source_media_used_for_training: bool = False
    safe_for_creative_abstract_planning: bool = True
    full_competitor_video_and_audio_watched: bool = False
    full_competitor_story_audio_acting_workflow_conclusions_approved: bool = False
    mechanical_decode_or_10s_sample_does_not_replace_entire_watch: bool = True


class VideoProductionIntelligence:
    def __init__(self,root:Path):
        self.root=Path(root).resolve()
        self.research=NicheResearchConference(self.root)

    @staticmethod
    def sha256(path:Path)->str:
        h=hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda:f.read(1024*1024),b""):
                h.update(chunk)
        return h.hexdigest()

    def _methods(self,niche:str,obs:ObservedVideoSignals)->list[ProductionMethodPossibility]:
        selection={
            "minecraft":[("Blender voxel animation","Test original same-scene voxel rig+visemes and moving-camera coverage"),
                         ("Authorized Minecraft runtime","Compare genuine gameplay capture for scenes requiring authentic gameplay")],
            "roblox_animation":[("Blender R6 rig animation","Verify original R6 skin/identity and camera continuity"),
                                ("Roblox Studio runtime","Trial licensed game capture where actual Roblox gameplay is required")],
            "preschool_3d_musical":[("Blender original organic character rig","Produce signed original facial rig and song beat/viseme animatic"),
                                     ("Original music and score studio","Compose owned score/vocals, measure synchronization and curriculum safety")],
            "long_slices_game":[("Godot original physics runtime","Run reproducible original obstacle course; measure collisions and capture"),
                                ("Blender cinematic physical simulation","Render same original path seed and compare camera/physics performance")],
            "ai_family_drama":[("Blender controlled acting","Produce original character close-up and continuity holdouts"),
                               ("Licensed ComfyUI local AI video","Measure 12GB fit, faces/motion, weights license and scene consistency")],
            "asmr_sleep_hands_objects":[("Authentic close-mic capture","Record first-party 30s samples and assess noise/transients"),
                                        ("Audio editor/FFmpeg","Measure clipping, loudness and clicks on owned recordings")],
            "audio_storytelling_seniors":[("Licensed/owned narration","Compare independent listener pacing and clarity"),
                                         ("Local consented TTS","Check pronunciation, rights and longform accepted-minute cost")],
            "rain_sleep_white_noise":[("Owned ambience sound bed","Check source rights and loop/frequency profiles"),
                                      ("FFmpeg mastered visuals","Verify stable audio, codec and no video flicker")],
            "daily_english":[("Curriculum-reviewed audio/graphics","Check pronunciation, subtitle alignment and educational accuracy")],
        }
        if niche not in selection:
            stages=NICHE_BLUEPRINTS[niche].stage_sequence
            options=[("General "+stage.stage.value+" workflow",
                      "Test original golden shot with scoped stage QC") for stage in stages[:2]]
        else:
            options=selection[niche]
        results=[]
        for family,trial in options:
            base={
                "PRECISE_RENDERER_OR_MODEL_NOT_IDENTIFIABLE_FROM_FINAL_VIDEO",
                "UNMEASURED_CREATIVE_QUALITY_AND_LICENSE",
            }
            signal=None
            if obs.decoded_media_observed and obs.camera_motion_proxy:
                signal=("Measured global camera-motion proxy: "+obs.camera_motion_proxy
                        +" (not evidence of a specific 3D/game engine)")
            elif obs.metadata_only:
                base.add("PIXELS_AND_AUDIO_NOT_ACQUIRED")
            results.append(ProductionMethodPossibility(
                method_family=family,supporting_observation=signal,
                cannot_conclude=sorted(base),next_validation=trial,
            ))
        return results

    @staticmethod
    def _handoff(niche:str,project:str,signals:ObservedVideoSignals,
                 methods:list[ProductionMethodPossibility],
                 department_names:list[str],stage_blockers:list[str])->ProductionObservationHandoff:
        checks=[
            "RESEARCH: collect at least 2 independent original sources (abstract format only), avoid cloning IP",
            "TECH: compare candidate engines on same NEW ORIGINAL 15-30s golden scene and actual hardware",
            "CREATIVE: blind reviewer grades story/acting/audio quality against niche-specific rubric",
            "FINANCE: count accepted video minutes, human rework, watts, retries and licensing fees",
        ]
        if signals.metadata_only:
            checks.insert(0,"RESEARCH: obtain explicitly authorized media to measure actual cuts/camera/audio")
        else:
            checks.insert(0,"VISUAL/AUDIO: verify motion proxy and cut detection against annotated sample")
        if niche=="preschool_3d_musical":
            checks.append("CHILD SAFETY: review curriculum, original songs, original character IP and consented singing")
        flags=[]
        if signals.decoded_media_observed and signals.camera_motion_proxy=="STATIC_DOMINANT" and niche in {
            "minecraft","roblox_animation","animal_animation","ai_family_drama",
        }:
            flags.append("CAMERA_STATIC_DOMINANT_REVIEW_IF_SCENE_REQUIRES_COVERAGE")
        if signals.decoded_media_observed and signals.scene_cuts==0:
            flags.append("NO_CUTS_OBSERVED_NOT_AN_AUTOMATIC_EDITING_DEFECT")
        if signals.audio_stream_analyzed and signals.measured_silence_ratio is not None and signals.measured_silence_ratio>=.95:
            flags.append("NEAR_SILENT_AUDIO_REVIEW_ONLY_IF_DIALOGUE_OR_MUSIC_EXPECTED")
        return ProductionObservationHandoff(
            niche_id=niche,project_id=project,video_id=signals.video_id,
            proof_level=signals.proof_level,observations=signals,
            potential_method_families=methods,
            department_study_requirements=department_names,
            recommended_tests=checks,
            observation_review_flags=flags,
            blocked_capabilities=sorted(set(stage_blockers+
                ["COMPETITOR_ENTIRE_MOVING_VIDEO_AND_ORIGINAL_AUDIO_NOT_INDEPENDENTLY_REVIEWED"]+
                (["VIDEO_CONTENT_UNAVAILABLE"] if signals.metadata_only else []))),
        )

    def study(self,request:VideoReferenceInput)->ProductionObservationHandoff:
        if request.niche_id not in NICHE_BLUEPRINTS:
            raise ValueError("UNKNOWN_NICHE_REQUIRES_NEW_BLUEPRINT")
        # Existing v192 conference creates specialist tasks for niche.
        room=self.research.convene(request.niche_id,project_id=request.project_id)
        roles=[r.department_id for r in room.department_reviews]
        stages=room.blocked_stages
        if request.local_file:
            video=Path(request.local_file).resolve()
            video.relative_to(self.root) # disallow unbounded host filesystem reads
            if not video.is_file():
                raise FileNotFoundError(video)
            if video.stat().st_size>180*1024*1024:
                raise ValueError("MEDIA_SIZE_EXCEEDS_LOCAL_STUDY_CAP")
            tool=ReferenceVideoDecomposer(
                self.root,policy=ReferenceAcquisitionPolicy(
                    max_duration_seconds=request.max_duration_seconds,
                    retain_downloaded_media=False,
                ),
            )
            rid=request.source_video_id or video.stem
            result=tool.analyze_local_file(video,video_id=rid,
                source_url="first_party:"+rid,
                source_metadata={"id":rid,"channel":"CineFactory Owned Study"})
            if result.media_sha256!=self.sha256(video):
                raise RuntimeError("SOURCE_MUTATED_DURING_INSPECTION")
            # Derive a frame count from ffprobe so the metric is not invented
            # from nominal FPS/duration alone.
            raw_probe=tool._probe_media(video)
            frame_count=None
            width=None
            height=None
            for st in raw_probe.get("streams",[]):
                if st.get("codec_type")=="video":
                    frames=st.get("nb_frames")
                    if frames and str(frames).isdigit():
                        frame_count=int(frames)
                    width=int(st["width"]) if st.get("width") else None
                    height=int(st["height"]) if st.get("height") else None
                    break
            signals=ObservedVideoSignals(
                proof_level=VideoProofLevel.LOCAL_OWNED_MEDIA_DECODED,
                video_id=rid,source_sha256=result.media_sha256,
                decoded_media_observed=True,audiovisual_analysis_complete=False,
                metadata_only=False,video_duration_seconds=result.source.duration_seconds,
                video_frame_count=frame_count,
                image_width=width,image_height=height,
                scene_cuts=result.visual.cut_count,
                cuts_per_minute=result.visual.cuts_per_minute,
                camera_motion_proxy=result.camera.profile,
                camera_motion_confidence=result.camera.confidence,
                measured_silence_ratio=result.audio.silence_ratio if result.audio.has_audio else None,
                audio_stream_analyzed=result.audio.has_audio,
                transcript_cues_analyzed=result.transcript.available,
                notes=["REAL_OWNED_VIDEO_DECODED_BY_FFMPEG_OPENCV",
                       "CAMERA_MOTION_ESTIMATED_BY_GLOBAL_FLOW_NOT_DIRECT_CAMERA_SENSOR",
                       "VISUAL_ANALYSIS_DOES_NOT_IDENTIFY_BLENDER_GODOT_OR_AI_MODEL",
                       "AUTOMATED_LOCAL_VIDEO_DECOMPOSITION_IS_NOT_A_COMPLETE_HUMAN_AUDIOVISUAL_WATCH"],
            )
        else:
            vid=request.youtube_video_id
            assert vid is not None
            tool=ReferenceVideoDecomposer(self.root,policy=ReferenceAcquisitionPolicy(
                max_duration_seconds=request.max_duration_seconds,
                retain_downloaded_media=False,
            ))
            src,_=tool.metadata("https://www.youtube.com/watch?v="+vid)
            if src.video_id!=vid:
                raise ValueError("YOUTUBE_VIDEO_ID_MISMATCH")
            if src.duration_seconds and src.duration_seconds>request.max_duration_seconds:
                raise RuntimeError("VIDEO_DURATION_EXCEEDS_SCOPE")
            signals=ObservedVideoSignals(
                proof_level=VideoProofLevel.PUBLIC_YOUTUBE_METADATA_ONLY,
                video_id=src.video_id,metadata_only=True,
                video_duration_seconds=src.duration_seconds,
                views_public_metadata=src.view_count,
                upload_date_public_metadata=src.upload_date,
                source_channel_public_metadata=src.channel,
                notes=[
                    "ACTUAL_PUBLIC_YTDLP_METADATA_OBSERVED_NO_FRAMES_DECODED",
                    "TRANSCRIPT_TEXT_NOT_DOWNLOADED_OR_EXTRACTED",
                    "VIDEO_FETCH_SEPARATELY_UNAVAILABLE_403_IN_CURRENT_SESSION",
                    "DO_NOT_INFER_SHOTS_RIG_OR_AUDIO_FROM_METADATA",
                ],
            )
        return self._handoff(
            request.niche_id,request.project_id,signals,
            self._methods(request.niche_id,signals),roles,stages)
