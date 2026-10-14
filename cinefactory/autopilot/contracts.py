from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field
from typing import Literal


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AutopilotRequest(BaseModel):
    prompt: str = Field(min_length=3)
    profile: str = "cinematic_story"
    language: str = "vi"
    duration_seconds: int | None = None
    reasoning_mode: str = "scaffold"  # scaffold | file | command
    reasoning_command: str | None = None
    production_mode: str = "slate"  # slate | comfyui
    quality_tier: Literal["diagnostic", "premium"] = "diagnostic"
    studio_director_plan_file: str | None = None
    studio_conference_file: str | None = None
    workflow_id: str | None = None  # legacy alias for video_workflow_id
    workflow_version: str = "1"
    asset_workflow_id: str | None = None
    asset_workflow_version: str = "1"
    keyframe_workflow_id: str | None = None
    keyframe_workflow_version: str = "1"
    video_workflow_id: str | None = None
    video_workflow_version: str = "1"
    # Optional speed lanes. Missing lanes fall back to video_workflow_id/workflow_id.
    video_fast_workflow_id: str | None = None
    video_fast_workflow_version: str = "1"
    video_standard_workflow_id: str | None = None
    video_standard_workflow_version: str = "1"
    video_master_workflow_id: str | None = None
    video_master_workflow_version: str = "1"
    asset_candidates: int = Field(default=2, ge=1, le=6)
    keyframe_candidates: int = Field(default=2, ge=1, le=6)
    pilot_count: int = Field(default=2, ge=1, le=6)
    visual_qc_command: str | None = None
    require_visual_qc: bool = True
    turbo_dispatch: bool = False
    turbo_timeout_seconds: int = Field(default=1800, ge=30, le=21600)
    min_visual_score: float = Field(default=0.72, ge=0.0, le=1.0)
    early_accept_score: float = Field(default=0.88, ge=0.0, le=1.0)
    max_repair_rounds: int = Field(default=2, ge=0, le=5)
    openchatcut_command: str | None = None
    upscale_command: str | None = None
    render_width: int = 1280
    render_height: int = 720
    tts_mode: str = "none"  # none | espeak | command
    tts_command: str | None = None
    voice: str | None = None
    master_4k: bool = True
    originality_strict: bool = True
    originality_retries: int = Field(default=2, ge=0, le=5)
    include_prior_projects: bool = True
    workflow_family: str | None = None
    world_target: str | None = None
    backend: str | None = None


class StageStatus(BaseModel):
    name: str
    status: str
    detail: str | None = None
    started_at: datetime = Field(default_factory=utcnow)
    finished_at: datetime | None = None


class AutopilotResult(BaseModel):
    project_id: str
    success: bool
    stages: list[StageStatus]
    final_video: str | None = None
    manifest_path: str | None = None
    release_package_path: str | None = None
    warnings: list[str] = Field(default_factory=list)
    quality_certified: bool = False
    release_ready: bool = False
