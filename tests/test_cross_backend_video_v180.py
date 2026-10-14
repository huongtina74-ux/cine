from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from PIL import Image

from cinefactory.block_animation.assembler import (
    EpisodeAssembler,
)
from cinefactory.models.registry import ModelRegistry
from cinefactory.studio.capabilities import CapabilityRegistry
from cinefactory.studio.capability_execution_lab import (
    CapabilityExecutionLab,
)
from cinefactory.studio.contracts import (
    CapabilityKind,
    CapabilityOffer,
)
from cinefactory.studio.cross_backend_video import (
    CrossBackendVideoService,
    VideoBackendId,
    VideoBackendProfile,
    VideoModelFile,
)
from cinefactory.studio.production_method_switch import (
    MethodSwitchPolicy,
    MethodSwitchRequest,
    ProductionMethodSwitchController,
)
from cinefactory.studio.video_backend_qualification import (
    VideoBackendQualificationController,
    VideoBackendQualificationStore,
)
from cinefactory.workflows.registry import WorkflowRegistry


ROOT = Path(__file__).resolve().parents[1]


class _Qualification:
    def decision(self, tool_id: str):
        if tool_id != "comfyui":
            raise KeyError(tool_id)
        return SimpleNamespace(qualified=True)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _environment(tmp_path: Path):
    model_bytes = b"wan-diffusion-test"
    text_bytes = b"umt5-test"
    vae_bytes = b"vae-test"
    files = {
        "models/diffusion.safetensors": model_bytes,
        "models/text.safetensors": text_bytes,
        "models/vae.safetensors": vae_bytes,
    }
    for relative, payload in files.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)

    revision = "sha256:" + _sha(model_bytes)
    profile = VideoBackendProfile(
        backend_id=VideoBackendId.WAN21_FUN_INPAINT_13B,
        normalizer_id="blockvideo.wan21.fun.inpaint.v1",
        workflow_id="comfy.wan21.fun.inpaint.1.3b",
        workflow_version="1",
        model_id="wan2.1-fun-inpaint-1.3b",
        model_revision=revision,
        diffusion_model="diffusion.safetensors",
        text_encoder="text.safetensors",
        vae="vae.safetensors",
        model_files=[
            VideoModelFile(
                role="diffusion_model",
                relative_path="models/diffusion.safetensors",
                sha256=_sha(model_bytes),
            ),
            VideoModelFile(
                role="text_encoder",
                relative_path="models/text.safetensors",
                sha256=_sha(text_bytes),
            ),
            VideoModelFile(
                role="vae",
                relative_path="models/vae.safetensors",
                sha256=_sha(vae_bytes),
            ),
        ],
        license_name="Apache-2.0",
        commercial_use_reviewed=True,
        max_vram_gb=12.0,
        scheduler_required_vram_gb=8.0,
    )
    service = CrossBackendVideoService(
        tmp_path,
        SimpleNamespace(),
        profile=profile,
    )

    registry_path = tmp_path / "models" / "registry.yaml"
    registry_path.write_text(
        yaml.safe_dump(
            {
                "models": [
                    {
                        "model_id": profile.model_id,
                        "revision": revision,
                        "modality": "video",
                        "local_path": (
                            "models/diffusion.safetensors"
                        ),
                        "code_license": "Apache-2.0",
                        "weights_license": "Apache-2.0",
                        "commercial_use_reviewed": True,
                        "output_terms_reviewed": True,
                        "approved_for_production": False,
                        "notes": ["test model"],
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    models = ModelRegistry(registry_path).load()

    workflow_root = tmp_path / "workflows"
    folder = workflow_root / "comfyui"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "workflow.json").write_text(
        json.dumps(
            {
                "1": {
                    "class_type": "SaveImage",
                    "inputs": {},
                }
            }
        ),
        encoding="utf-8",
    )
    (folder / "workflow.manifest.yaml").write_text(
        yaml.safe_dump(
            {
                "workflow_id": profile.workflow_id,
                "version": profile.workflow_version,
                "executor_id": "local.comfyui",
                "media_type": "video",
                "model_id": profile.model_id,
                "model_revision": profile.model_revision,
                "workflow_file": "workflow.json",
                "local_only": True,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    workflows = WorkflowRegistry(workflow_root).load()

    capabilities = CapabilityRegistry(
        offers=[
            CapabilityOffer(
                capability_id="comfyui.local.video",
                kind=CapabilityKind.AI_VIDEO,
                provider="ComfyUI",
                executable=True,
                local=True,
                commercial_safe=True,
                deterministic=0.55,
                quality=0.72,
                speed=0.38,
                control=0.66,
                vram_gb=12.0,
            )
        ]
    )
    studio = SimpleNamespace(
        capabilities=capabilities,
        production_qualification=_Qualification(),
    )
    ctx = SimpleNamespace(
        root=tmp_path,
        studio=studio,
        workflows=workflows,
        models=models,
        cross_backend_video=service,
        capability_execution_lab=CapabilityExecutionLab(
            tmp_path
        ),
    )
    return ctx, profile, service, models


def _runtime_result(
    tmp_path: Path,
    profile: VideoBackendProfile,
    case_id: str,
    *,
    identity: float = 0.95,
    qc_passed: bool = True,
):
    path = tmp_path / f"{case_id}.mp4"
    path.write_bytes(b"video-evidence")
    duration = 1.0625
    fps = 16.0
    return {
        "path": str(path),
        "duration": duration,
        "fps": fps,
        "qc_passed": qc_passed,
        "qc_findings": [],
        "visual_qc": {
            "passed": qc_passed,
            "black_seconds": 0.0,
            "freeze_seconds": 0.0,
            "findings": [],
        },
        "rendered_frame_qc": {
            "passed": qc_passed,
            "findings": [],
        },
        "identity_qc": {
            "passed": identity >= 0.80,
            "score": identity,
            "measured": True,
        },
        "performance_qc": {
            "passed": True,
            "score": 1.0,
            "warnings": [
                "NO_SEMANTIC_PERFORMANCE_REQUIREMENT"
            ],
            "blockers": [],
        },
        "geometry_qc": {
            "passed": True,
            "warnings": [
                "CAMERA_INTENT_BOUND_BUT_NOT_GEOMETRICALLY_MEASURED"
            ],
            "blockers": [],
            "targets": [],
        },
        "creative_intent_bound": True,
        "render_state": {
            "camera": {
                "start": {"lens_mm": 48.0},
                "end": {"lens_mm": 48.0},
            }
        },
        "backend_contract": {
            "backend_id": profile.backend_id.value,
            "normalizer_id": profile.normalizer_id,
            "workflow_id": profile.workflow_id,
            "workflow_version": profile.workflow_version,
            "model_id": profile.model_id,
            "model_revision": profile.model_revision,
            "duration_seconds": duration,
            "fps": 16,
            "recurring_identity_required": True,
        },
    }


def _compiled_shot():
    import runpy

    ns = runpy.run_path(
        str(
            ROOT
            / "tests"
            / "test_block_auto_repair_v173.py"
        )
    )
    episode = ns["_episode"]()
    return EpisodeAssembler.from_root(ROOT).compile(
        episode
    ).shots[0]


def test_cross_backend_normalizer_requires_reference_and_scopes_hard_gates(
    tmp_path,
):
    _, profile, service, _ = _environment(tmp_path)
    shot = _compiled_shot()

    missing = service.normalize_shot(
        project_id="P",
        episode_id="E",
        shot=shot,
        output_path=tmp_path / "out.mp4",
        reference_frame_path=None,
        recurring_identity_required=True,
        semantic_performance_required=False,
        precise_camera_required=False,
        render_preview=True,
        seed=1,
    )
    assert missing.passed is False
    assert "RECURRING_IDENTITY_REFERENCE_REQUIRED" in (
        missing.blockers
    )

    reference = tmp_path / "reference.png"
    Image.new(
        "RGB",
        (64, 64),
        (120, 80, 60),
    ).save(reference)
    valid = service.normalize_shot(
        project_id="P",
        episode_id="E",
        shot=shot,
        output_path=tmp_path / "out.mp4",
        reference_frame_path=reference,
        recurring_identity_required=True,
        semantic_performance_required=False,
        precise_camera_required=False,
        render_preview=True,
        seed=1,
    )
    assert valid.passed is True
    assert valid.request is not None
    assert valid.request.normalizer_id == (
        profile.normalizer_id
    )
    assert valid.request.reference.source_sha256

    fake_spec = SimpleNamespace(
        normalizer_id=profile.normalizer_id
    )
    exact = service.assess_method_request(
        SimpleNamespace(
            recurring_identity_required=True,
            reference_frame_path=str(reference),
            precise_camera_required=True,
            semantic_performance_required=False,
        ),
        fake_spec,
    )
    assert "PRECISE_CAMERA_GEOMETRY_UNSUPPORTED" in exact

    semantic = service.assess_method_request(
        SimpleNamespace(
            recurring_identity_required=True,
            reference_frame_path=str(reference),
            precise_camera_required=False,
            semantic_performance_required=True,
        ),
        fake_spec,
    )
    assert (
        "SEMANTIC_PERFORMANCE_VIDEO_QC_NOT_QUALIFIED"
        in semantic
    )


def test_video_qualification_needs_multiple_cases_and_identity_floor(
    tmp_path,
):
    ctx, profile, service, _ = _environment(tmp_path)
    controller = VideoBackendQualificationController(
        ctx,
        service=service,
        store=VideoBackendQualificationStore(
            tmp_path / "qual"
        ),
    )

    one, _ = controller.evaluate(
        runtime_results=[
            (
                "A",
                _runtime_result(
                    tmp_path,
                    profile,
                    "A",
                ),
            )
        ]
    )
    assert one.passed is False
    assert (
        "VIDEO_QUALIFICATION_INSUFFICIENT_CASES"
        in one.blockers
    )

    weak, _ = controller.evaluate(
        runtime_results=[
            (
                "A2",
                _runtime_result(
                    tmp_path,
                    profile,
                    "A2",
                    identity=0.95,
                ),
            ),
            (
                "B2",
                _runtime_result(
                    tmp_path,
                    profile,
                    "B2",
                    identity=0.50,
                ),
            ),
        ]
    )
    assert weak.passed is False
    assert (
        "VIDEO_IDENTITY_SCORE_BELOW_FLOOR"
        in weak.blockers
    )


def test_passing_attestation_can_persist_model_approval_and_unlock_wan(
    tmp_path,
):
    ctx, profile, service, models = _environment(tmp_path)
    controller = VideoBackendQualificationController(
        ctx,
        service=service,
        store=VideoBackendQualificationStore(
            tmp_path / "qual"
        ),
    )
    attestation, path = controller.evaluate(
        runtime_results=[
            (
                "A",
                _runtime_result(
                    tmp_path,
                    profile,
                    "A",
                    identity=0.94,
                ),
            ),
            (
                "B",
                _runtime_result(
                    tmp_path,
                    profile,
                    "B",
                    identity=0.91,
                ),
            ),
        ]
    )
    assert attestation.passed is True
    assert attestation.benchmark_matrix.passed is True

    outside = tmp_path / "outside.json"
    outside.write_text(
        attestation.model_dump_json(indent=2),
        encoding="utf-8",
    )
    with pytest.raises(
        RuntimeError,
        match="OUTSIDE_TRUSTED_STORE",
    ):
        controller.promote_model(outside)

    promoted = controller.promote_model(path)
    assert promoted.approved_for_production is True
    reloaded = ModelRegistry(
        models.path
    ).load()
    assert (
        reloaded.require_approved(
            profile.model_id,
            profile.model_revision,
        ).approved_for_production
        is True
    )

    method_ctx = SimpleNamespace(
        root=tmp_path,
        studio=ctx.studio,
        workflows=ctx.workflows,
        models=models,
        cross_backend_video=service,
    )
    switcher = ProductionMethodSwitchController(
        method_ctx
    )
    reference = tmp_path / "reference.png"
    Image.new(
        "RGB",
        (64, 64),
        (100, 80, 60),
    ).save(reference)

    request = MethodSwitchRequest(
        project_id="P",
        episode_id="E",
        shot_id="S01",
        current_tool_id="blender",
        current_method_id="blender.cycles.quality",
        policy=(
            MethodSwitchPolicy
            .QUALITY_FIRST_ALTERNATIVE
        ),
        min_quality=0.70,
        max_vram_gb=12.0,
        local_only=True,
        commercial_safe=True,
        continuity_priority=True,
        backend_switch_allowed=True,
        recurring_identity_required=True,
        reference_frame_path=str(reference),
        precise_camera_required=False,
        semantic_performance_required=False,
        visual_style="MINECRAFT",
    )
    decision = switcher.deliberate(request)
    assert decision.executable is True
    assert decision.selected_method_id == (
        "comfyui.wan21.fun.inpaint.1.3b"
    )

    exact = switcher.deliberate(
        request.model_copy(
            update={
                "precise_camera_required": True
            }
        )
    )
    wan_exact = next(
        item
        for item in exact.assessments
        if item.method_id
        == "comfyui.wan21.fun.inpaint.1.3b"
    )
    assert (
        "PRECISE_CAMERA_GEOMETRY_UNSUPPORTED"
        in wan_exact.blockers
    )

    semantic = switcher.deliberate(
        request.model_copy(
            update={
                "semantic_performance_required": True
            }
        )
    )
    wan_semantic = next(
        item
        for item in semantic.assessments
        if item.method_id
        == "comfyui.wan21.fun.inpaint.1.3b"
    )
    assert (
        "SEMANTIC_PERFORMANCE_VIDEO_QC_NOT_QUALIFIED"
        in wan_semantic.blockers
    )
