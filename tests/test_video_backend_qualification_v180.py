from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace

import yaml

from cinefactory.models.registry import ModelRegistry
from cinefactory.studio.capability_execution_lab import (
    CapabilityExecutionLab,
)
from cinefactory.studio.cross_backend_video import (
    CrossBackendVideoService,
    VideoBackendId,
    VideoBackendProfile,
    VideoModelFile,
)
from cinefactory.studio.video_backend_qualification import (
    VideoBackendQualificationController,
    VideoBackendQualificationStore,
)
from cinefactory.workflows.registry import WorkflowRegistry


class _Qualification:
    qualified = True


class _QualificationBoard:
    def decision(self, tool_id: str):
        assert tool_id == "comfyui"
        return _Qualification()


class _Studio:
    production_qualification = _QualificationBoard()


class _Executors:
    pass


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ctx(tmp_path: Path):
    artifact = tmp_path / "wan.safetensors"
    artifact.write_bytes(b"wan-test-model")
    digest = _sha(artifact)

    registry_path = tmp_path / "models.yaml"
    registry_path.write_text(
        yaml.safe_dump(
            {
                "models": [
                    {
                        "model_id": "wan.test",
                        "revision": f"sha256:{digest}",
                        "modality": "video",
                        "local_path": artifact.name,
                        "code_license": "Apache-2.0",
                        "weights_license": "Apache-2.0",
                        "commercial_use_reviewed": True,
                        "output_terms_reviewed": True,
                        "approved_for_production": False,
                        "notes": [
                            "Production approval remains false until qualification passes."
                        ],
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    models = ModelRegistry(registry_path).load()

    workflow_root = tmp_path / "workflows"
    workflow_dir = workflow_root / "video"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "workflow.json").write_text(
        "{}",
        encoding="utf-8",
    )
    (workflow_dir / "workflow.manifest.yaml").write_text(
        yaml.safe_dump(
            {
                "workflow_id": "comfy.test.video",
                "version": "1",
                "executor_id": "local.comfyui",
                "media_type": "video",
                "model_id": "wan.test",
                "model_revision": f"sha256:{digest}",
                "workflow_file": "workflow.json",
                "local_only": True,
                "notes": [],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    workflows = WorkflowRegistry(workflow_root).load()

    profile = VideoBackendProfile(
        backend_id=VideoBackendId.WAN21_FUN_INPAINT_13B,
        normalizer_id="blockvideo.test.v1",
        workflow_id="comfy.test.video",
        workflow_version="1",
        model_id="wan.test",
        model_revision=f"sha256:{digest}",
        diffusion_model=artifact.name,
        text_encoder="unused",
        vae="unused",
        model_files=[
            VideoModelFile(
                role="diffusion_model",
                relative_path=artifact.name,
                sha256=digest,
            )
        ],
        license_name="Apache-2.0",
        commercial_use_reviewed=True,
    )
    service = CrossBackendVideoService(
        tmp_path,
        _Executors(),
        profile=profile,
    )
    lab = CapabilityExecutionLab(tmp_path)
    ctx = SimpleNamespace(
        root=tmp_path,
        studio=_Studio(),
        workflows=workflows,
        models=models,
        cross_backend_video=service,
        capability_execution_lab=lab,
    )
    controller = VideoBackendQualificationController(
        ctx,
        service=service,
        store=VideoBackendQualificationStore(
            tmp_path / "qualification"
        ),
    )
    return ctx, controller, profile


def _result(
    tmp_path: Path,
    profile: VideoBackendProfile,
    case_id: str,
    *,
    identity: float = 0.95,
):
    output = tmp_path / f"{case_id}.mp4"
    output.write_bytes(b"fake-mp4")
    return {
        "path": str(output),
        "duration": 1.0625,
        "fps": 16.0,
        "qc_passed": True,
        "visual_qc": {
            "passed": True,
            "black_seconds": 0.0,
            "freeze_seconds": 0.0,
        },
        "rendered_frame_qc": {"passed": True},
        "identity_qc": {
            "passed": True,
            "measured": True,
            "score": identity,
        },
        "performance_qc": {
            "passed": True,
            "score": 1.0,
        },
        "geometry_qc": {
            "passed": True,
            "targets": [],
        },
        "creative_intent_bound": True,
        "render_state": {
            "camera": {
                "start": {"shot_size": "MS"},
                "end": {"shot_size": "MS"},
            }
        },
        "backend_contract": {
            "backend_id": profile.backend_id.value,
            "normalizer_id": profile.normalizer_id,
            "workflow_id": profile.workflow_id,
            "workflow_version": profile.workflow_version,
            "model_id": profile.model_id,
            "model_revision": profile.model_revision,
            "recurring_identity_required": True,
            "duration_seconds": 1.0625,
            "fps": 16,
        },
    }


def test_one_case_is_not_enough(tmp_path):
    ctx, controller, profile = _ctx(tmp_path)
    result = _result(
        tmp_path,
        profile,
        "A",
    )
    attestation, _ = controller.evaluate(
        runtime_results=[("A", result)]
    )
    assert attestation.passed is False
    assert (
        "VIDEO_QUALIFICATION_INSUFFICIENT_CASES"
        in attestation.blockers
    )


def test_identity_floor_blocks_qualification(tmp_path):
    ctx, controller, profile = _ctx(tmp_path)
    good = _result(
        tmp_path,
        profile,
        "A",
        identity=0.95,
    )
    weak = _result(
        tmp_path,
        profile,
        "B",
        identity=0.50,
    )
    attestation, _ = controller.evaluate(
        runtime_results=[
            ("A", good),
            ("B", weak),
        ]
    )
    assert attestation.passed is False
    assert "VIDEO_IDENTITY_SCORE_BELOW_FLOOR" in (
        attestation.blockers
    )


def test_two_good_cases_promote_exact_model(tmp_path):
    ctx, controller, profile = _ctx(tmp_path)
    first = _result(
        tmp_path,
        profile,
        "A",
        identity=0.95,
    )
    second = _result(
        tmp_path,
        profile,
        "B",
        identity=0.91,
    )
    attestation, path = controller.evaluate(
        runtime_results=[
            ("A", first),
            ("B", second),
        ]
    )
    assert attestation.passed is True
    promoted = controller.promote_model(path)
    assert promoted.approved_for_production is True

    reloaded = ModelRegistry(
        ctx.models.path
    ).load()
    persisted = reloaded.get(
        profile.model_id,
        profile.model_revision,
    )
    assert persisted.approved_for_production is True
    assert any(
        "Production qualification evidence:"
        in note
        for note in persisted.notes
    )
    assert not any(
        note.lower().startswith(
            "production approval remains false until"
        )
        for note in persisted.notes
    )


def test_attestation_outside_trusted_store_cannot_promote(
    tmp_path,
):
    ctx, controller, profile = _ctx(tmp_path)
    fake = tmp_path / "fake-attestation.json"
    fake.write_text(
        '{"passed": true}',
        encoding="utf-8",
    )
    try:
        controller.promote_model(fake)
    except RuntimeError as exc:
        assert (
            "VIDEO_QUALIFICATION_EVIDENCE_OUTSIDE_TRUSTED_STORE"
            in str(exc)
        )
    else:
        raise AssertionError(
            "outside attestation unexpectedly trusted"
        )


def test_app_context_shares_video_backend_qualification():
    from cinefactory.appctx import build_context

    root = Path(__file__).resolve().parents[1]
    ctx = build_context(root)
    assert (
        ctx.video_backend_qualification
        is ctx.studio.professional_company
        .video_backend_qualification
    )
    assert (
        ctx.video_backend_qualification.service
        is ctx.cross_backend_video
    )


def test_wan_workflow_uses_reference_at_both_temporal_boundaries(
    tmp_path,
):
    from cinefactory.studio.cross_backend_video import (
        CameraIntentContract,
        CanonicalBlockVideoRequest,
        ReferenceConditioning,
        ReferenceSourceKind,
        WAN21_FUN_INPAINT_PROFILE,
    )

    service = CrossBackendVideoService(
        tmp_path,
        _Executors(),
        profile=WAN21_FUN_INPAINT_PROFILE,
    )
    request = CanonicalBlockVideoRequest(
        project_id="P",
        episode_id="E",
        shot_id="S01",
        backend_id=(
            WAN21_FUN_INPAINT_PROFILE.backend_id
        ),
        normalizer_id=(
            WAN21_FUN_INPAINT_PROFILE.normalizer_id
        ),
        workflow_id=(
            WAN21_FUN_INPAINT_PROFILE.workflow_id
        ),
        workflow_version=(
            WAN21_FUN_INPAINT_PROFILE.workflow_version
        ),
        model_id=(
            WAN21_FUN_INPAINT_PROFILE.model_id
        ),
        model_revision=(
            WAN21_FUN_INPAINT_PROFILE.model_revision
        ),
        prompt="keep identity",
        negative_prompt="identity drift",
        width=320,
        height=176,
        fps=16,
        frame_count=17,
        duration_seconds=1.0625,
        seed=123,
        reference=ReferenceConditioning(
            required=True,
            source_kind=ReferenceSourceKind.IMAGE,
            source_path=str(tmp_path / "ref.png"),
            source_sha256="abc",
            staged_filename="ref.png",
            actor_ids=["A"],
            rig_ids=["mc_a"],
        ),
        camera=CameraIntentContract(),
        recurring_identity_required=True,
        semantic_performance_required=False,
        source_visual_style="MINECRAFT",
        scene_id="SC1",
        output_path=str(tmp_path / "out.mp4"),
        render_preview=True,
    )
    workflow = service.build_workflow(request)
    inputs = workflow["7"]["inputs"]
    assert inputs["start_image"] == ["6", 0]
    assert inputs["end_image"] == ["6", 0]
