from __future__ import annotations

import hashlib
import json
import math
import shutil
import subprocess
from enum import StrEnum
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from pydantic import BaseModel, Field

from cinefactory.block_animation.contracts import CompiledShot
from cinefactory.block_animation.rendered_frame_qc import (
    RenderedFrameAnalyzer,
)
from cinefactory.block_animation.visual_qc import BlockVisualQC
from cinefactory.media.ffmpeg import FFmpegToolchain
from cinefactory.turbo.contracts import ResourceClass, WorkItem


class VideoBackendId(StrEnum):
    WAN21_FUN_INPAINT_13B = "WAN21_FUN_INPAINT_13B"


class ReferenceSourceKind(StrEnum):
    NONE = "NONE"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


class CrossBackendGateStatus(StrEnum):
    PASS = "PASS"
    BLOCKED = "BLOCKED"
    FAIL = "FAIL"


class VideoModelFile(BaseModel):
    role: str
    relative_path: str
    sha256: str


class VideoBackendProfile(BaseModel):
    backend_id: VideoBackendId
    normalizer_id: str
    workflow_id: str
    workflow_version: str
    model_id: str
    model_revision: str
    diffusion_model: str
    text_encoder: str
    vae: str
    model_files: list[VideoModelFile]
    license_name: str
    commercial_use_reviewed: bool = False
    local_only: bool = True
    supports_reference_image: bool = True
    supports_recurring_identity_proxy: bool = True
    supports_exact_camera_geometry: bool = False
    max_vram_gb: float = 12.0
    scheduler_required_vram_gb: float = 8.0
    preview_width: int = 512
    preview_height: int = 288
    production_width: int = 832
    production_height: int = 480
    preview_frames: int = 17
    production_frames: int = 33
    fps: int = 16
    preview_steps: int = 8
    production_steps: int = 20
    cfg: float = 6.0
    reference_anchor_floor: float = 0.52


WAN21_FUN_INPAINT_PROFILE = VideoBackendProfile(
    backend_id=VideoBackendId.WAN21_FUN_INPAINT_13B,
    normalizer_id="blockvideo.wan21.fun.inpaint.v1",
    workflow_id="comfy.wan21.fun.inpaint.1.3b",
    workflow_version="1",
    model_id="wan2.1-fun-inpaint-1.3b",
    model_revision=(
        "sha256:"
        "8495d2b1673ffb18abb548a64ff3b0e4bd367734f653096f7a8a3ad46954d511"
    ),
    diffusion_model="wan2.1_fun_inp_1.3B_bf16.safetensors",
    text_encoder="umt5_xxl_fp8_e4m3fn_scaled.safetensors",
    vae="wan_2.1_vae.safetensors",
    model_files=[
        VideoModelFile(
            role="diffusion_model",
            relative_path=(
                ".tools/ComfyUI/models/diffusion_models/"
                "wan2.1_fun_inp_1.3B_bf16.safetensors"
            ),
            sha256=(
                "8495d2b1673ffb18abb548a64ff3b0e4bd367734f653096f7a8a3ad46954d511"
            ),
        ),
        VideoModelFile(
            role="text_encoder",
            relative_path=(
                ".tools/ComfyUI/models/text_encoders/"
                "umt5_xxl_fp8_e4m3fn_scaled.safetensors"
            ),
            sha256=(
                "c3355d30191f1f066b26d93fba017ae9809dce6c627dda5f6a66eaa651204f68"
            ),
        ),
        VideoModelFile(
            role="vae",
            relative_path=(
                ".tools/ComfyUI/models/vae/"
                "wan_2.1_vae.safetensors"
            ),
            sha256=(
                "2fc39d31359a4b0a64f55876d8ff7fa8d780956ae2cb13463b0223e15148976b"
            ),
        ),
    ],
    license_name="Apache-2.0",
    commercial_use_reviewed=True,
)


class ReferenceConditioning(BaseModel):
    required: bool
    source_kind: ReferenceSourceKind = ReferenceSourceKind.NONE
    source_path: str | None = None
    source_sha256: str | None = None
    staged_filename: str | None = None
    actor_ids: list[str] = Field(default_factory=list)
    rig_ids: list[str] = Field(default_factory=list)
    actor_screen_boxes: dict[str, dict[str, float]] = Field(
        default_factory=dict
    )
    global_character_ids: dict[str, str] = Field(default_factory=dict)
    actor_reference_ids: dict[str, str] = Field(default_factory=dict)
    actor_identity_descriptors: dict[str, str] = Field(default_factory=dict)


class CameraIntentContract(BaseModel):
    purpose: str = ""
    pattern_id: str | None = None
    motion: str = "static"
    shot_size: str = "MS"
    lens_mm: float | None = None
    motion_strength: float | None = None
    targets: list[str] = Field(default_factory=list)
    exact_geometry_required: bool = False


class CanonicalBlockVideoRequest(BaseModel):
    project_id: str
    episode_id: str
    shot_id: str
    backend_id: VideoBackendId
    normalizer_id: str
    workflow_id: str
    workflow_version: str
    model_id: str
    model_revision: str
    prompt: str
    negative_prompt: str
    width: int
    height: int
    fps: int
    frame_count: int
    duration_seconds: float
    seed: int
    reference: ReferenceConditioning
    camera: CameraIntentContract
    recurring_identity_required: bool
    semantic_performance_required: bool
    source_visual_style: str
    scene_id: str
    output_path: str
    render_preview: bool = False
    sampling_denoise: float = Field(default=1.0, ge=0.0, le=1.0)


class CrossBackendNormalizationResult(BaseModel):
    passed: bool
    blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    request: CanonicalBlockVideoRequest | None = None


class ReferenceAnchorQC(BaseModel):
    passed: bool
    measured: bool
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    histogram_similarity: float | None = Field(default=None, ge=0.0, le=1.0)
    hash_similarity: float | None = Field(default=None, ge=0.0, le=1.0)
    rgb_distance: float | None = Field(default=None, ge=0.0)
    blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class VideoBundleVerification(BaseModel):
    passed: bool
    files: dict[str, dict[str, Any]] = Field(default_factory=dict)
    blockers: list[str] = Field(default_factory=list)


class CrossBackendVideoService:
    IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm", ".avi"}

    def __init__(
        self,
        root: str | Path,
        executors: Any,
        *,
        profile: VideoBackendProfile | None = None,
        character_factory: Any | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.executors = executors
        self.profile = profile or WAN21_FUN_INPAINT_PROFILE
        self.character_factory = character_factory
        self.media = FFmpegToolchain()
        self.visual_qc = BlockVisualQC(self.media)
        self.frame_qc = RenderedFrameAnalyzer(self.media)
        self.cache_root = self.root / ".cfcache" / "cross_backend_video"
        self.cache_root.mkdir(parents=True, exist_ok=True)
        self.comfy_input = self.root / ".tools" / "ComfyUI" / "input"
        self.comfy_input.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _sha256(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    def verify_bundle(self) -> VideoBundleVerification:
        rows: dict[str, dict[str, Any]] = {}
        blockers: list[str] = []
        for item in self.profile.model_files:
            path = (self.root / item.relative_path).resolve()
            exists = path.is_file()
            digest = self._sha256(path) if exists else None
            matched = bool(
                exists
                and digest
                and digest.lower() == item.sha256.lower()
            )
            rows[item.role] = {
                "path": str(path),
                "exists": exists,
                "sha256": digest,
                "expected_sha256": item.sha256,
                "verified": matched,
                "bytes": path.stat().st_size if exists else 0,
            }
            if not exists:
                blockers.append(f"VIDEO_MODEL_FILE_MISSING:{item.role}")
            elif not matched:
                blockers.append(f"VIDEO_MODEL_HASH_MISMATCH:{item.role}")
        return VideoBundleVerification(
            passed=not blockers,
            files=rows,
            blockers=blockers,
        )

    def assess_method_request(
        self,
        request: Any,
        spec: Any,
    ) -> list[str]:
        blockers: list[str] = []
        bundle = self.verify_bundle()
        blockers.extend(bundle.blockers)
        if (
            getattr(spec, "normalizer_id", None)
            != self.profile.normalizer_id
        ):
            blockers.append("BLOCK_VIDEO_NORMALIZER_ID_MISMATCH")
        reference = getattr(
            request,
            "reference_frame_path",
            None,
        )
        if bool(
            getattr(
                request,
                "recurring_identity_required",
                False,
            )
        ):
            if not self.profile.supports_reference_image:
                blockers.append(
                    "REFERENCE_CONDITIONING_NOT_SUPPORTED"
                )
            if not reference or not Path(str(reference)).is_file():
                blockers.append(
                    "RECURRING_IDENTITY_REFERENCE_REQUIRED"
                )
        if bool(
            getattr(
                request,
                "precise_camera_required",
                False,
            )
        ) and not self.profile.supports_exact_camera_geometry:
            blockers.append(
                "PRECISE_CAMERA_GEOMETRY_UNSUPPORTED"
            )
        if bool(
            getattr(
                request,
                "semantic_performance_required",
                False,
            )
        ):
            blockers.append(
                "SEMANTIC_PERFORMANCE_VIDEO_QC_NOT_QUALIFIED"
            )
        return sorted(set(blockers))

    @staticmethod
    def _fit_dimensions(
        width: int,
        height: int,
        *,
        preview: bool,
        profile: VideoBackendProfile,
    ) -> tuple[int, int]:
        if width >= height:
            max_w = (
                profile.preview_width
                if preview
                else profile.production_width
            )
            max_h = (
                profile.preview_height
                if preview
                else profile.production_height
            )
        else:
            max_w = (
                profile.preview_height
                if preview
                else profile.production_height
            )
            max_h = (
                profile.preview_width
                if preview
                else profile.production_width
            )
        scale = min(max_w / max(width, 1), max_h / max(height, 1))
        if scale > 1.0:
            scale = 1.0
        target_w = max(16, int(round(width * scale / 16.0)) * 16)
        target_h = max(16, int(round(height * scale / 16.0)) * 16)
        return target_w, target_h

    @staticmethod
    def _wan_frame_count(
        duration_seconds: float,
        fps: int,
        *,
        preview: bool,
        profile: VideoBackendProfile,
    ) -> int:
        desired = max(1, int(round(duration_seconds * fps)))
        maximum = (
            profile.preview_frames
            if preview
            else profile.production_frames
        )
        desired = min(desired, maximum)
        # Wan video latent length accepts values 1,5,9,... (step=4).
        n = max(0, int(round((desired - 1) / 4.0)))
        return max(1, min(maximum, 1 + 4 * n))

    @staticmethod
    def _camera_contract(
        shot: CompiledShot,
        *,
        precise_camera_required: bool,
    ) -> CameraIntentContract:
        take = shot.camera_takes[0] if shot.camera_takes else None
        if take is None:
            return CameraIntentContract(
                exact_geometry_required=precise_camera_required
            )
        return CameraIntentContract(
            purpose=str(take.purpose),
            pattern_id=take.pattern_id,
            motion=str(take.motion),
            shot_size=str(take.shot_size),
            lens_mm=float(take.lens_mm),
            motion_strength=float(take.motion_strength),
            targets=list(take.targets),
            exact_geometry_required=precise_camera_required,
        )

    @staticmethod
    def _prompt(
        shot: CompiledShot,
        camera: CameraIntentContract,
    ) -> str:
        pieces = [
            f"visual style {shot.visual_style}",
            f"scene {shot.scene.scene_id}",
            f"camera {camera.shot_size} {camera.motion}",
            f"camera purpose {camera.purpose}",
        ]
        if camera.lens_mm is not None:
            pieces.append(f"{camera.lens_mm:.0f}mm lens")
        for actor in shot.actors:
            rig = shot.rigs.get(actor.rig_id)
            identity = dict((rig.identity if rig else {}) or {})
            identity_text = ", ".join(
                f"{key} {value}"
                for key, value in sorted(identity.items())
                if value not in (None, "", [], {})
            )
            actor_text = (
                f"character {actor.actor_id}, rig {actor.rig_id}"
                + (f", {identity_text}" if identity_text else "")
            )
            pieces.append(actor_text)
        for action in shot.actions:
            pieces.append(
                f"{action.actor_id} performs {action.clip_id}"
            )
        for expression in shot.expressions:
            pieces.append(
                f"{expression.actor_id} expression {expression.expression_id}"
            )
        intent = dict(shot.creative_intent or {})
        for key in (
            "emotion",
            "mood",
            "story_beat",
            "visual_intent",
            "environment",
        ):
            if intent.get(key):
                pieces.append(f"{key} {intent[key]}")
        pieces.extend(
            [
                "preserve character appearance from reference image",
                "consistent proportions and clothing",
                "coherent motion",
                "stable background geometry",
                "no text, no subtitles, no watermark",
            ]
        )
        return ". ".join(str(item) for item in pieces if str(item).strip())

    @staticmethod
    def _negative_prompt() -> str:
        return (
            "identity drift, changing character design, changing clothes, "
            "extra limbs, missing limbs, deformed hands, distorted face, "
            "camera teleport, flicker, temporal inconsistency, duplicate "
            "characters, warped background, text, subtitles, watermark, "
            "overexposure, underexposure, blur, low quality"
        )

    def _reference_source(
        self,
        source_path: str | Path | None,
    ) -> tuple[ReferenceSourceKind, Path | None]:
        if source_path is None:
            return ReferenceSourceKind.NONE, None
        path = Path(source_path).resolve()
        if not path.is_file():
            return ReferenceSourceKind.NONE, None
        suffix = path.suffix.lower()
        if suffix in self.IMAGE_SUFFIXES:
            return ReferenceSourceKind.IMAGE, path
        if suffix in self.VIDEO_SUFFIXES:
            return ReferenceSourceKind.VIDEO, path
        return ReferenceSourceKind.NONE, None

    def stage_reference(
        self,
        source_path: str | Path,
    ) -> tuple[ReferenceSourceKind, Path, str, str]:
        kind, source = self._reference_source(source_path)
        if source is None or kind is ReferenceSourceKind.NONE:
            raise RuntimeError("REFERENCE_SOURCE_UNSUPPORTED_OR_MISSING")

        source_digest = self._sha256(source)
        if kind is ReferenceSourceKind.VIDEO:
            frame = self.cache_root / f"ref_{source_digest[:20]}.png"
            if not frame.exists():
                self.media.extract_frame(
                    source,
                    frame,
                    time_seconds=0.08,
                )
            reference = frame
        else:
            reference = source

        reference_digest = self._sha256(reference)
        suffix = reference.suffix.lower()
        if suffix not in self.IMAGE_SUFFIXES:
            suffix = ".png"
        staged_name = (
            f"cinefactory_ref_{reference_digest[:24]}{suffix}"
        )
        staged = self.comfy_input / staged_name
        if not staged.exists():
            shutil.copy2(reference, staged)
        return kind, reference, reference_digest, staged_name

    def normalize_shot(
        self,
        *,
        project_id: str,
        episode_id: str,
        shot: CompiledShot,
        output_path: str | Path,
        reference_frame_path: str | Path | None,
        recurring_identity_required: bool,
        semantic_performance_required: bool,
        precise_camera_required: bool,
        render_preview: bool,
        seed: int,
    ) -> CrossBackendNormalizationResult:
        blockers: list[str] = []
        warnings: list[str] = []
        bundle = self.verify_bundle()
        blockers.extend(bundle.blockers)

        camera = self._camera_contract(
            shot,
            precise_camera_required=precise_camera_required,
        )
        width, height = self._fit_dimensions(
            shot.width,
            shot.height,
            preview=render_preview,
            profile=self.profile,
        )
        frame_count = self._wan_frame_count(
            shot.duration_seconds,
            self.profile.fps,
            preview=render_preview,
            profile=self.profile,
        )

        required_ref = bool(
            recurring_identity_required
            or shot.actors
        )
        reference = ReferenceConditioning(
            required=required_ref,
            actor_ids=[item.actor_id for item in shot.actors],
            rig_ids=[item.rig_id for item in shot.actors],
        )
        if reference_frame_path:
            try:
                kind, ref_path, digest, staged_name = self.stage_reference(
                    reference_frame_path
                )
                identity_metadata: dict[str, Any] = {}
                if self.character_factory is not None:
                    try:
                        identity_metadata = (
                            self.character_factory
                            .capture_reference_metadata(
                                source_media=(
                                    reference_frame_path
                                ),
                                actors=list(shot.actors),
                            )
                        )
                    except Exception as identity_exc:
                        warnings.append(
                            "CHARACTER_REFERENCE_PACK_CAPTURE_SKIPPED:"
                            f"{type(identity_exc).__name__}:"
                            f"{identity_exc}"
                        )
                reference = reference.model_copy(
                    update={
                        "source_kind": kind,
                        "source_path": str(ref_path),
                        "source_sha256": digest,
                        "staged_filename": staged_name,
                        **identity_metadata,
                    }
                )
            except Exception as exc:
                blockers.append(
                    "REFERENCE_STAGING_FAILED:"
                    f"{type(exc).__name__}:{exc}"
                )
        elif required_ref:
            blockers.append("RECURRING_IDENTITY_REFERENCE_REQUIRED")

        if precise_camera_required:
            blockers.append(
                "PRECISE_CAMERA_GEOMETRY_UNSUPPORTED"
            )
        if semantic_performance_required:
            blockers.append(
                "SEMANTIC_PERFORMANCE_VIDEO_QC_NOT_QUALIFIED"
            )

        normalized_duration = frame_count / self.profile.fps
        if abs(normalized_duration - shot.duration_seconds) > 0.35:
            warnings.append(
                "VIDEO_DURATION_QUANTIZED:"
                f"requested={shot.duration_seconds:.3f}:"
                f"normalized={normalized_duration:.3f}"
            )

        prompt = self._prompt(shot, camera)
        if reference.actor_identity_descriptors:
            prompt += ". identity locks: " + "; ".join(
                f"{actor_id}: {descriptor}"
                for actor_id, descriptor in sorted(
                    reference.actor_identity_descriptors.items()
                )
            )
        if reference.actor_screen_boxes:
            spatial_locks: list[str] = []
            for actor_id, box in sorted(
                reference.actor_screen_boxes.items()
            ):
                center_x = (
                    float(box.get("x0", 0.0))
                    + float(box.get("x1", 0.0))
                ) / 2.0
                if center_x < 0.42:
                    position = "left side of frame"
                elif center_x > 0.58:
                    position = "right side of frame"
                else:
                    position = "center region of frame"
                spatial_locks.append(
                    f"{actor_id} remains in the {position}"
                )
            prompt += (
                ". spatial identity locks: "
                + "; ".join(spatial_locks)
                + "; never swap character identities, clothing, hair, "
                "skin colors, or positions between named actors"
            )

        request = CanonicalBlockVideoRequest(
            project_id=project_id,
            episode_id=episode_id,
            shot_id=shot.shot_id,
            backend_id=self.profile.backend_id,
            normalizer_id=self.profile.normalizer_id,
            workflow_id=self.profile.workflow_id,
            workflow_version=self.profile.workflow_version,
            model_id=self.profile.model_id,
            model_revision=self.profile.model_revision,
            prompt=prompt,
            negative_prompt=self._negative_prompt(),
            width=width,
            height=height,
            fps=self.profile.fps,
            frame_count=frame_count,
            duration_seconds=normalized_duration,
            seed=int(seed),
            reference=reference,
            camera=camera,
            recurring_identity_required=recurring_identity_required,
            semantic_performance_required=semantic_performance_required,
            source_visual_style=str(shot.visual_style),
            scene_id=str(shot.scene.scene_id),
            output_path=str(Path(output_path).resolve()),
            render_preview=render_preview,
            sampling_denoise=(
                0.82
                if len(reference.actor_ids) > 1
                else 1.0
            ),
        )
        return CrossBackendNormalizationResult(
            passed=not blockers,
            blockers=sorted(set(blockers)),
            warnings=warnings,
            request=request,
        )

    def build_workflow(
        self,
        request: CanonicalBlockVideoRequest,
    ) -> dict[str, Any]:
        profile = self.profile
        workflow: dict[str, Any] = {
            "1": {
                "class_type": "UNETLoader",
                "inputs": {
                    "unet_name": profile.diffusion_model,
                    "weight_dtype": "default",
                },
            },
            "2": {
                "class_type": "CLIPLoader",
                "inputs": {
                    "clip_name": profile.text_encoder,
                    "type": "wan",
                    "device": "default",
                },
            },
            "3": {
                "class_type": "VAELoader",
                "inputs": {"vae_name": profile.vae},
            },
            "4": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": request.prompt,
                    "clip": ["2", 0],
                },
            },
            "5": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": request.negative_prompt,
                    "clip": ["2", 0],
                },
            },
        }
        video_inputs: dict[str, Any] = {
            "positive": ["4", 0],
            "negative": ["5", 0],
            "vae": ["3", 0],
            "width": request.width,
            "height": request.height,
            "length": request.frame_count,
            "batch_size": 1,
        }
        if request.reference.staged_filename:
            workflow["6"] = {
                "class_type": "LoadImage",
                "inputs": {
                    "image": request.reference.staged_filename
                },
            }
            video_inputs["start_image"] = ["6", 0]
            # Wan-Fun Inpaint natively supports start/end image anchors.
            # Reusing the canonical reference at both temporal boundaries
            # constrains identity drift across seeds while preserving motion
            # generation between the anchors.
            video_inputs["end_image"] = ["6", 0]

        workflow["7"] = {
            "class_type": "WanFunInpaintToVideo",
            "inputs": video_inputs,
        }
        workflow["8"] = {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "seed": request.seed,
                "steps": (
                    profile.preview_steps
                    if request.render_preview
                    else profile.production_steps
                ),
                "cfg": profile.cfg,
                "sampler_name": "uni_pc",
                "scheduler": "simple",
                "positive": ["7", 0],
                "negative": ["7", 1],
                "latent_image": ["7", 2],
                "denoise": request.sampling_denoise,
            },
        }
        workflow["9"] = {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["8", 0],
                "vae": ["3", 0],
            },
        }
        workflow["10"] = {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["9", 0],
                "filename_prefix": (
                    "CineFactory_Wan21_"
                    + request.shot_id
                ),
            },
        }
        return workflow

    def build_work_item(
        self,
        *,
        compiled: Any,
        shot: CompiledShot,
        output_path: Path,
        render_preview: bool,
        switch_round: int,
        switch_of_work_id: str,
        reference_frame_path: str | Path | None,
        recurring_identity_required: bool,
        semantic_performance_required: bool,
        precise_camera_required: bool,
        continuation: dict[str, Any] | None = None,
    ) -> WorkItem:
        seed_material = (
            f"{compiled.project_id}|{compiled.episode_id}|"
            f"{shot.shot_id}|{switch_round}|{self.profile.model_revision}"
        )
        seed = int(
            hashlib.sha256(seed_material.encode("utf-8")).hexdigest()[:15],
            16,
        )
        normalized = self.normalize_shot(
            project_id=compiled.project_id,
            episode_id=compiled.episode_id,
            shot=shot,
            output_path=output_path,
            reference_frame_path=reference_frame_path,
            recurring_identity_required=recurring_identity_required,
            semantic_performance_required=semantic_performance_required,
            precise_camera_required=precise_camera_required,
            render_preview=render_preview,
            seed=seed,
        )
        if not normalized.passed or normalized.request is None:
            raise RuntimeError(
                "CROSS_BACKEND_NORMALIZATION_BLOCKED:"
                + "|".join(normalized.blockers)
            )
        request = normalized.request
        workflow = self.build_workflow(request)
        output_dir = (
            Path(output_path).resolve().parent
            / (
                ".comfy_"
                + shot.shot_id
                + "_"
                + str(switch_round)
            )
        )
        payload = {
            "video_request": request.model_dump(mode="json"),
            "workflow": workflow,
            "output_dir": str(output_dir),
            "workflow_id": request.workflow_id,
            "workflow_version": request.workflow_version,
            "model_id": request.model_id,
            "model_revision": request.model_revision,
            "method_switch": True,
            "method_id": "comfyui.wan21.fun.inpaint.1.3b",
            "method_switch_round": switch_round,
            "method_switch_of_work_id": switch_of_work_id,
            "required_vram_gb": (
                self.profile.scheduler_required_vram_gb
            ),
            # ComfyUI is a persistent external GPU runtime. Its resident
            # allocations are already included in nvidia-smi used-memory, so
            # scheduler admission must not require the full model footprint
            # a second time. It still verifies total device capacity and
            # incremental scratch headroom.
            "runtime_managed_vram": True,
            "gpu_runtime_id": "comfyui",
            "hot_model_incremental_vram_gb": 0.75,
            "normalizer_id": self.profile.normalizer_id,
            "normalization_warnings": list(normalized.warnings),
        }
        if continuation:
            payload["continuation"] = dict(continuation)
        return WorkItem(
            project_id=compiled.project_id,
            kind="block.video.method_switch",
            handler="block.video.comfy",
            resource=ResourceClass.GPU,
            priority=max(80, 99 - int(shot.order)),
            model_affinity=(
                "COMFYUI:"
                + self.profile.model_id
                + "@"
                + self.profile.model_revision
            ),
            payload=payload,
            max_attempts=1,
        )

    @staticmethod
    def _ahash64(image: Image.Image) -> int:
        gray = image.convert("L").resize((8, 8), Image.Resampling.BILINEAR)
        data = np.asarray(gray, dtype=np.float32)
        bits = (data >= float(data.mean())).reshape(-1)
        value = 0
        for bit in bits:
            value = (value << 1) | int(bool(bit))
        return value

    @staticmethod
    def _hist(image: Image.Image) -> np.ndarray:
        hsv = np.asarray(
            image.convert("HSV").resize((96, 96), Image.Resampling.BILINEAR),
            dtype=np.float32,
        )
        hist, _, _ = np.histogram2d(
            hsv[:, :, 0].reshape(-1),
            hsv[:, :, 1].reshape(-1),
            bins=(12, 4),
            range=((0, 256), (0, 256)),
        )
        hist = hist.astype(np.float64)
        total = float(hist.sum())
        return hist.reshape(-1) / total if total > 0 else hist.reshape(-1)

    def reference_anchor_qc(
        self,
        *,
        reference_path: str | Path | None,
        video_path: str | Path,
    ) -> ReferenceAnchorQC:
        if not reference_path:
            return ReferenceAnchorQC(
                passed=True,
                measured=False,
                warnings=["REFERENCE_ANCHOR_NOT_REQUESTED"],
            )
        reference = Path(reference_path)
        if not reference.is_file():
            return ReferenceAnchorQC(
                passed=False,
                measured=False,
                blockers=["REFERENCE_ANCHOR_FILE_MISSING"],
            )
        head = self.cache_root / (
            "generated_head_"
            + hashlib.sha256(str(video_path).encode("utf-8")).hexdigest()[:18]
            + ".png"
        )
        self.media.extract_frame(
            video_path,
            head,
            time_seconds=0.04,
        )
        with Image.open(reference) as ref_image, Image.open(head) as gen_image:
            ref = ref_image.convert("RGB")
            gen = gen_image.convert("RGB").resize(
                ref.size,
                Image.Resampling.BILINEAR,
            )
            h1 = self._hist(ref)
            h2 = self._hist(gen)
            denom = float(np.linalg.norm(h1) * np.linalg.norm(h2))
            hist_similarity = (
                float(np.dot(h1, h2) / denom)
                if denom > 1e-12
                else 0.0
            )
            hash_similarity = 1.0 - (
                (
                    self._ahash64(ref)
                    ^ self._ahash64(gen)
                ).bit_count()
                / 64.0
            )
            ref_rgb = np.asarray(ref, dtype=np.float32).mean(axis=(0, 1)) / 255.0
            gen_rgb = np.asarray(gen, dtype=np.float32).mean(axis=(0, 1)) / 255.0
            rgb_distance = float(np.linalg.norm(ref_rgb - gen_rgb))
        score = max(
            0.0,
            min(
                1.0,
                0.55 * hist_similarity
                + 0.30 * hash_similarity
                + 0.15 * max(0.0, 1.0 - rgb_distance / 0.65),
            ),
        )
        passed = score >= self.profile.reference_anchor_floor
        return ReferenceAnchorQC(
            passed=passed,
            measured=True,
            score=score,
            histogram_similarity=hist_similarity,
            hash_similarity=hash_similarity,
            rgb_distance=rgb_distance,
            blockers=(
                []
                if passed
                else [
                    "REFERENCE_ANCHOR_DRIFT:"
                    f"score={score:.3f}:"
                    f"required={self.profile.reference_anchor_floor:.3f}"
                ]
            ),
            warnings=(
                []
                if score >= self.profile.reference_anchor_floor + 0.10
                else ["REFERENCE_ANCHOR_NEAR_FLOOR"]
            ),
        )

    def _normalize_media(
        self,
        sources: list[Path],
        request: CanonicalBlockVideoRequest,
    ) -> Path:
        target = Path(request.output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        valid = [Path(path) for path in sources if Path(path).is_file()]
        if not valid:
            raise RuntimeError("CROSS_BACKEND_OUTPUT_ARTIFACTS_MISSING")

        image_suffixes = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
        all_images = all(path.suffix.lower() in image_suffixes for path in valid)
        common = [
            self.media.ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
        ]
        if all_images:
            # ComfyUI SaveImage produces one deterministic image per decoded
            # frame. Re-stage those frames into a short contiguous sequence so
            # FFmpeg never depends on ComfyUI filename numbering semantics.
            digest = hashlib.sha256(
                "|".join(str(path.resolve()) for path in valid).encode("utf-8")
            ).hexdigest()[:16]
            frame_dir = target.parent / (".wan_frames_" + digest)
            if frame_dir.exists():
                shutil.rmtree(frame_dir)
            frame_dir.mkdir(parents=True, exist_ok=True)
            ordered = sorted(valid, key=lambda path: path.name)
            for index, source in enumerate(ordered):
                with Image.open(source) as image:
                    image.convert("RGB").save(
                        frame_dir / f"frame_{index:05d}.png",
                        format="PNG",
                    )
            cmd = [
                *common,
                "-framerate",
                str(request.fps),
                "-start_number",
                "0",
                "-i",
                str(frame_dir / "frame_%05d.png"),
                "-frames:v",
                str(len(ordered)),
            ]
        else:
            source = next(
                (
                    path
                    for path in valid
                    if path.suffix.lower()
                    in {".mp4", ".webm", ".mkv", ".mov", ".avi"}
                ),
                valid[0],
            )
            cmd = [
                *common,
                "-i",
                str(source),
                "-t",
                f"{request.duration_seconds:.6f}",
            ]

        cmd.extend(
            [
                "-an",
                "-vf",
                (
                    f"fps={request.fps},"
                    f"scale={request.width}:{request.height}:"
                    "force_original_aspect_ratio=decrease,"
                    f"pad={request.width}:{request.height}:"
                    "(ow-iw)/2:(oh-ih)/2"
                ),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(target),
            ]
        )
        proc = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            check=False,
            timeout=600,
        )
        if proc.returncode != 0 or not target.is_file():
            raise RuntimeError(
                "CROSS_BACKEND_OUTPUT_NORMALIZATION_FAILED:"
                + (proc.stderr or "")[-1000:]
            )
        return target

    def execute_work_item(self, item: WorkItem) -> dict[str, Any]:
        request = CanonicalBlockVideoRequest.model_validate(
            item.payload["video_request"]
        )
        executor = self.executors.get("local.comfyui")
        preflight = executor.preflight(
            dict(item.payload["workflow"])
        )
        if not preflight.valid:
            raise RuntimeError(
                "CROSS_BACKEND_COMFY_PREFLIGHT_FAILED:"
                + "|".join(preflight.findings)
            )
        result = executor.execute(
            {
                "workflow": dict(item.payload["workflow"]),
                "output_dir": item.payload["output_dir"],
                "workflow_id": request.workflow_id,
                "workflow_version": request.workflow_version,
                "model_id": request.model_id,
                "model_revision": request.model_revision,
                "seed": request.seed,
            }
        )
        if not result.ok or not result.artifacts:
            raise RuntimeError(
                "CROSS_BACKEND_COMFY_EXECUTION_FAILED:"
                + str(result.error or "NO_ARTIFACT")
            )
        sources = [
            Path(path)
            for path in result.artifacts
            if Path(path).is_file()
        ]
        canonical = self._normalize_media(
            sources,
            request,
        )
        probe = self.media.probe(canonical)
        visual = self.visual_qc.review(canonical)
        actor_states = {
            actor_id: {
                "mid": {
                    "screen_box": dict(screen_box)
                },
                "global_character_id": (
                    request.reference.global_character_ids.get(
                        actor_id
                    )
                ),
            }
            for actor_id, screen_box
            in request.reference.actor_screen_boxes.items()
        }
        render_state = {
            "shot_id": request.shot_id,
            "scene_id": request.scene_id,
            "backend": request.backend_id.value,
            "reference_sha256": request.reference.source_sha256,
            "camera": {
                "start": request.camera.model_dump(mode="json"),
                "end": request.camera.model_dump(mode="json"),
            },
            "lighting": {},
            "actors": actor_states,
            "props": {},
        }
        frame_qc = self.frame_qc.analyze(
            canonical,
            render_state=render_state,
        )
        reference_qc = self.reference_anchor_qc(
            reference_path=request.reference.source_path,
            video_path=canonical,
        )
        character_identity_report = None
        actor_tracking_report = None
        if (
            self.character_factory is not None
            and request.reference.actor_reference_ids
        ):
            (
                character_identity_report,
                actor_tracking_report,
            ) = self.character_factory.evaluate_video_output(
                actor_reference_ids=(
                    request.reference.actor_reference_ids
                ),
                global_character_ids=(
                    request.reference.global_character_ids
                ),
                video_path=canonical,
            )

        duration_delta = abs(
            float(probe.duration) - request.duration_seconds
        )
        fps_delta = abs(
            float(probe.fps or 0.0) - float(request.fps)
        )
        contract_blockers: list[str] = []
        if duration_delta > 0.25:
            contract_blockers.append(
                "VIDEO_DURATION_CONTRACT_MISS:"
                f"actual={probe.duration:.3f}:"
                f"expected={request.duration_seconds:.3f}"
            )
        if fps_delta > 0.5:
            contract_blockers.append(
                "VIDEO_FPS_CONTRACT_MISS:"
                f"actual={float(probe.fps or 0.0):.3f}:"
                f"expected={request.fps}"
            )
        if not visual.passed:
            contract_blockers.extend(
                f"VIDEO_VISUAL_QC:{item}"
                for item in visual.findings
            )
        if not frame_qc.passed:
            contract_blockers.extend(
                f"VIDEO_FRAME_QC:{item}"
                for item in frame_qc.findings
            )
        if request.recurring_identity_required:
            if character_identity_report is not None:
                if not character_identity_report.passed:
                    contract_blockers.extend(
                        character_identity_report.findings
                    )
            elif not reference_qc.passed:
                contract_blockers.extend(
                    reference_qc.blockers
                )
        if request.semantic_performance_required:
            contract_blockers.append(
                "SEMANTIC_PERFORMANCE_VIDEO_QC_NOT_QUALIFIED"
            )
        if request.camera.exact_geometry_required:
            contract_blockers.append(
                "PRECISE_CAMERA_GEOMETRY_UNSUPPORTED"
            )

        if character_identity_report is not None:
            identity_payload = {
                "passed": (
                    character_identity_report.passed
                    if request.recurring_identity_required
                    else True
                ),
                "score": (
                    character_identity_report.minimum_score
                ),
                "measured": (
                    character_identity_report.measured
                ),
                "blockers": list(
                    character_identity_report.findings
                ),
                "warnings": [],
                "metric": "PER_ACTOR_REFERENCE_APPEARANCE",
                "actors": [
                    item.model_dump(mode="json")
                    for item in (
                        character_identity_report.assessments
                    )
                ],
                "collision_findings": list(
                    character_identity_report.collision_findings
                ),
                "fallback_reference_anchor": (
                    reference_qc.model_dump(mode="json")
                ),
            }
        else:
            identity_payload = {
                "passed": (
                    reference_qc.passed
                    if request.recurring_identity_required
                    else True
                ),
                "score": reference_qc.score,
                "measured": reference_qc.measured,
                "blockers": list(reference_qc.blockers),
                "warnings": list(reference_qc.warnings),
                "metric": "REFERENCE_FRAME_ANCHOR_SIMILARITY",
            }
        camera_warnings = []
        if not request.camera.exact_geometry_required:
            camera_warnings.append(
                "CAMERA_INTENT_BOUND_BUT_NOT_GEOMETRICALLY_MEASURED"
            )
        geometry_qc = {
            "passed": not request.camera.exact_geometry_required,
            "warnings": camera_warnings,
            "blockers": (
                []
                if not request.camera.exact_geometry_required
                else ["PRECISE_CAMERA_GEOMETRY_UNSUPPORTED"]
            ),
            "targets": [],
            "metric": "CROSS_BACKEND_CAMERA_CONTRACT",
        }
        performance_qc = {
            "passed": not request.semantic_performance_required,
            "score": (
                1.0
                if not request.semantic_performance_required
                else 0.0
            ),
            "warnings": (
                ["NO_SEMANTIC_PERFORMANCE_REQUIREMENT"]
                if not request.semantic_performance_required
                else []
            ),
            "blockers": (
                []
                if not request.semantic_performance_required
                else ["SEMANTIC_PERFORMANCE_VIDEO_QC_NOT_QUALIFIED"]
            ),
        }
        qc_passed = not contract_blockers
        return {
            "path": str(canonical),
            "duration": float(probe.duration),
            "fps": float(probe.fps or 0.0),
            "qc_passed": qc_passed,
            "qc_findings": sorted(set(contract_blockers)),
            "visual_qc": {
                "passed": visual.passed,
                "findings": list(visual.findings),
                "black_seconds": visual.black_seconds,
                "freeze_seconds": visual.freeze_seconds,
            },
            "rendered_frame_qc": frame_qc.model_dump(mode="json"),
            "identity_qc": identity_payload,
            "character_identity_qc": (
                character_identity_report.model_dump(
                    mode="json"
                )
                if character_identity_report is not None
                else None
            ),
            "actor_tracking_qc": (
                actor_tracking_report.model_dump(
                    mode="json"
                )
                if actor_tracking_report is not None
                else None
            ),
            "performance_qc": performance_qc,
            "geometry_qc": geometry_qc,
            "creative_intent_bound": True,
            "performance_directive_count": (
                0
                if not request.semantic_performance_required
                else 1
            ),
            "render_state": render_state,
            "backend_contract": request.model_dump(mode="json"),
            "comfy_metadata": dict(result.metadata or {}),
            "normalizer_id": request.normalizer_id,
        }
