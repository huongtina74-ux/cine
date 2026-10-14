from __future__ import annotations

from pathlib import Path

from cinefactory.appctx import build_context
from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.block_animation.contracts import (
    ActorPlacement,
    CameraIntent,
    EpisodeSpec,
    ShotPerformanceSpec,
)
from cinefactory.studio.shot_routing import (
    ShotRouteMode,
    ShotRoutingAdapter,
)


ROOT = Path(__file__).resolve().parents[1]


def _compiled_shot(
    *,
    creative_intent: dict | None = None,
    performance_directives: list[dict] | None = None,
):
    episode = EpisodeSpec(
        project_id="P183",
        episode_id="E183",
        title="routing",
        fps=24,
        width=320,
        height=180,
        quality_profile="preview",
        shots=[
            ShotPerformanceSpec(
                shot_id="S01",
                scene_template_id="minecraft_classroom",
                duration_seconds=1.0,
                actors=[
                    ActorPlacement(
                        actor_id="A",
                        rig_id="mc_a",
                        marker="hero_a",
                    )
                ],
                camera=CameraIntent(
                    purpose="fidelity_medium",
                    pattern_id="fidelity_medium",
                    targets=["A"],
                ),
                creative_intent=dict(
                    creative_intent or {}
                ),
                performance_directives=list(
                    performance_directives or []
                ),
            )
        ],
    )
    return EpisodeAssembler.from_root(ROOT).compile(
        episode
    ).shots[0]


def test_default_route_preserves_blender_when_not_enabled():
    ctx = build_context(ROOT)
    shot = _compiled_shot(
        creative_intent={
            "generative_video_preferred": True
        }
    )
    route = ctx.shot_router.route(
        project_id="P",
        episode_id="E",
        shot=shot,
        episode_metadata={},
    )
    assert route.mode is ShotRouteMode.DEFAULT_BLENDER
    assert route.proactive is False
    assert route.method_decision is None


def test_precise_camera_routes_to_controlled_cycles():
    ctx = build_context(ROOT)
    shot = _compiled_shot(
        creative_intent={
            "precise_camera_required": True,
        }
    )
    route = ctx.shot_router.route(
        project_id="P",
        episode_id="E",
        shot=shot,
        episode_metadata={
            "proactive_hybrid_routing": True,
        },
    )
    assert route.mode is ShotRouteMode.CONTROLLED_BLENDER
    assert route.selected_method_id == (
        "blender.cycles.quality"
    )
    assert route.selected_handler == (
        "blender.animation.render"
    )
    assert route.precise_camera_required is True


def test_semantic_performance_routes_to_controlled_cycles():
    ctx = build_context(ROOT)
    shot = _compiled_shot(
        creative_intent={
            "semantic_performance_required": True,
        },
        performance_directives=[
            {
                "actor_id": "A",
                "role": "SPEAKER",
                "objective": "persuade",
            }
        ],
    )
    route = ctx.shot_router.route(
        project_id="P",
        episode_id="E",
        shot=shot,
        episode_metadata={
            "proactive_hybrid_routing": True,
        },
    )
    assert route.mode is ShotRouteMode.CONTROLLED_BLENDER
    assert route.selected_method_id == (
        "blender.cycles.quality"
    )
    assert route.semantic_performance_required is True


def test_reference_conditioned_generative_route_selects_wan(
    tmp_path,
):
    ctx = build_context(ROOT)
    reference = tmp_path / "reference.mp4"
    reference.write_bytes(b"reference")
    shot = _compiled_shot(
        creative_intent={
            "generative_video_preferred": True,
            "reference_frame_path": str(reference),
        }
    )
    route = ctx.shot_router.route(
        project_id="P",
        episode_id="E",
        shot=shot,
        episode_metadata={
            "proactive_hybrid_routing": True,
        },
    )
    assert route.mode is ShotRouteMode.GENERATIVE_VIDEO
    assert route.selected_method_id == (
        "comfyui.wan21.fun.inpaint.1.3b"
    )
    assert route.selected_handler == "block.video.comfy"
    assert route.reference_frame_path == str(reference)


def test_strict_generative_route_without_reference_blocks():
    ctx = build_context(ROOT)
    shot = _compiled_shot(
        creative_intent={
            "generative_video_preferred": True,
            "hybrid_routing_strict": True,
        }
    )
    router = ShotRoutingAdapter(
        ctx.method_switch,
        character_factory=None,
    )
    route = router.route(
        project_id="P",
        episode_id="E",
        shot=shot,
        episode_metadata={
            "proactive_hybrid_routing": True,
        },
    )
    assert route.mode is ShotRouteMode.BLOCKED
    assert "GENERATIVE_ROUTE_REFERENCE_REQUIRED" in (
        route.blockers
    )


def test_non_strict_generative_route_without_reference_falls_back():
    ctx = build_context(ROOT)
    shot = _compiled_shot(
        creative_intent={
            "generative_video_preferred": True,
        }
    )
    router = ShotRoutingAdapter(
        ctx.method_switch,
        character_factory=None,
    )
    route = router.route(
        project_id="P",
        episode_id="E",
        shot=shot,
        episode_metadata={
            "proactive_hybrid_routing": True,
        },
    )
    assert route.mode is ShotRouteMode.DEFAULT_BLENDER
    assert "GENERATIVE_ROUTE_REFERENCE_REQUIRED" in (
        route.blockers
    )


def test_app_context_shares_shot_router():
    ctx = build_context(ROOT)
    assert (
        ctx.shot_router
        is ctx.studio.professional_company.shot_router
    )
    assert ctx.shot_router.method_switch is ctx.method_switch
    assert (
        ctx.shot_router.character_factory
        is ctx.character_factory
    )
