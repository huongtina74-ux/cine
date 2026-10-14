from cinefactory.studio.visual_model_conference import (
    VisualModelConference,
    VisualModelRequest,
    VisualModality,
    VisualObjective,
    default_visual_model_candidates,
)


def _conference(*ready, cloud=False):
    ids = set(ready)
    return VisualModelConference(
        default_visual_model_candidates(
            executable_model_ids=ids,
            qualified_model_ids=ids,
            cloud_enabled=cloud,
        )
    )


def test_wan22_5b_is_selected_for_local_commercial_video():
    decision = _conference("wan2.2.ti2v.5b").deliberate(
        VisualModelRequest(
            request_id="V1",
            modality=VisualModality.VIDEO,
            objective=VisualObjective.GENERATIVE_VIDEO,
            max_vram_gb=12.0,
            require_commercial_safe=True,
            require_vram_verified=False,
            require_reference=True,
        )
    )
    assert decision.blocked is False
    assert decision.primary_model_id == "wan2.2.ti2v.5b"


def test_qwen_image_21_is_blocked_for_commercial_project():
    decision = _conference("qwen-image-2.1").deliberate(
        VisualModelRequest(
            request_id="IMG1",
            modality=VisualModality.IMAGE,
            objective=VisualObjective.STORYBOARD_KEYFRAME,
            require_commercial_safe=True,
            require_vram_verified=False,
            require_reference=True,
        )
    )
    qwen = next(
        item for item in decision.assessments
        if item.model_id == "qwen-image-2.1"
    )
    assert qwen.eligible is False
    assert "COMMERCIAL_LICENSE_RESTRICTED" in qwen.blockers


def test_flux2_klein_is_preferred_image_candidate_when_qualified():
    decision = _conference("flux2.klein.4b").deliberate(
        VisualModelRequest(
            request_id="IMG2",
            modality=VisualModality.IMAGE,
            objective=VisualObjective.ASSET_IMAGE,
            max_vram_gb=12.0,
            require_commercial_safe=True,
            require_vram_verified=False,
        )
    )
    assert decision.blocked is False
    assert decision.primary_model_id == "flux2.klein.4b"


def test_unverified_heavy_wan_models_fail_12gb_vram_gate():
    conference = _conference(
        "wan2.2.a14b.gguf",
        "wan.animate2",
        "wan2.2.s2v.14b",
    )
    cases = [
        (VisualObjective.HERO_CINEMATIC, "wan2.2.a14b.gguf", False),
        (VisualObjective.CHARACTER_MOTION, "wan.animate2", False),
        (VisualObjective.AUDIO_DRIVEN_PERFORMANCE, "wan2.2.s2v.14b", True),
    ]
    for objective, model_id, audio_drive in cases:
        decision = conference.deliberate(
            VisualModelRequest(
                request_id=model_id,
                modality=VisualModality.VIDEO,
                objective=objective,
                max_vram_gb=12.0,
                require_vram_verified=True,
                require_reference=True,
                require_audio_drive=audio_drive,
            )
        )
        selected = next(
            item for item in decision.assessments
            if item.model_id == model_id
        )
        assert selected.eligible is False
        assert "VRAM_UNVERIFIED" in selected.blockers


def test_wan27_cloud_never_runs_under_local_zero_cost_policy():
    decision = _conference(cloud=True).deliberate(
        VisualModelRequest(
            request_id="CLOUD1",
            modality=VisualModality.VIDEO,
            objective=VisualObjective.HERO_CINEMATIC,
            allow_cloud=False,
            allow_paid=False,
            require_commercial_safe=False,
            require_vram_verified=False,
        )
    )
    wan = next(
        item for item in decision.assessments
        if item.model_id == "wan2.7.cloud"
    )
    assert "CLOUD_NOT_ALLOWED" in wan.blockers
    assert "PAID_BACKEND_NOT_ALLOWED" in wan.blockers


def test_conditional_ltx_license_fails_strict_commercial_gate():
    decision = _conference("ltx2.5.fast").deliberate(
        VisualModelRequest(
            request_id="LTX1",
            modality=VisualModality.VIDEO,
            objective=VisualObjective.GENERATIVE_VIDEO,
            require_commercial_safe=True,
            require_vram_verified=False,
        )
    )
    ltx = next(
        item for item in decision.assessments
        if item.model_id == "ltx2.5.fast"
    )
    assert "COMMERCIAL_LICENSE_CONDITIONAL" in ltx.blockers


def test_no_installed_models_fails_closed():
    decision = _conference().deliberate(
        VisualModelRequest(
            request_id="NONE",
            modality=VisualModality.VIDEO,
            objective=VisualObjective.GENERATIVE_VIDEO,
            require_vram_verified=False,
        )
    )
    assert decision.blocked is True
    assert decision.primary_model_id is None
    assert decision.reasons == ["NO_VISUAL_MODEL_PASSED_ALL_GATES"]
