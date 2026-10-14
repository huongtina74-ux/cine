"""Separate real-game capture/livestream lanes: never substitute Blender movies.

Research, capture permission, playable runtime and owner OAuth are required
for real execution. Stage adapters fail closed where runtime is unqualified.
"""
from __future__ import annotations

from .minecraft_subniche_v207 import Route, Lane
from .company_runner import StageHandlerRegistry, StageHandlerResult, StageExecutionContext

def capture_stages(route: Route) -> list:
    from .company import CompanyStage as S
    if route.production_lane not in {
        Lane.CAPTURED_GAMEPLAY, Lane.LIVE_RUNTIME, Lane.STAGED_GAME_MACHINIMA
    } or route.blocker:
        raise ValueError("NOT_A_VERIFIED_REAL_GAME_PRODUCTION_ROUTE")
    real_source=("LIVE_AUTHENTICATED_GAME_RUNTIME"
                 if route.production_lane is Lane.LIVE_RUNTIME
                 else "OWNED_ACTUAL_GAME_SESSION_RECORDING")
    return [
        S(stage_id="MC_MODE_INTAKE",owner="STUDIO_MANAGEMENT",
          artifacts_in=["project_brief"],artifacts_out=["mc_mode_brief"],
          gate="EXPLICIT_SOURCE_TRUTH_ROUTE"),
        S(stage_id="MC_FORMAT_RESEARCH",owner="INTELLIGENCE",
          artifacts_in=["mc_mode_brief"],artifacts_out=["mc_verified_research"],
          gate="REVIEWED_SUBNICHE_EVIDENCE_REQUIRED"),
        S(stage_id="MC_GAME_SOURCE_RIGHTS",owner="RIGHTS",
          artifacts_in=["mc_verified_research"],
          artifacts_out=["mc_capture_rights","mc_capture_source"],
          gate=real_source),
        S(stage_id="MC_REAL_CAPTURE",owner="PRODUCTION",
          artifacts_in=["mc_capture_source","mc_capture_rights"],
          artifacts_out=["mc_real_capture_video"],
          gate="PLAYABLE_GAME_CAPTURE_OR_AUTHENTICATED_LIVE_STREAM"),
        S(stage_id="MC_CAPTURE_QC",owner="QC",
          artifacts_in=["mc_real_capture_video"],
          artifacts_out=["mc_capture_accepted_master"],
          gate="SOURCE_TRUTH_AND_AUDIENCE_SPECIFIC_QC"),
        S(stage_id="MC_CAPTURE_PACKAGING",owner="PACKAGING",
          artifacts_in=["mc_capture_accepted_master"],
          artifacts_out=["release_package"],gate="PLATFORM_TRUTHFUL_PACKAGING"),
        S(stage_id="PUBLISHING",owner="OPERATIONS",
          artifacts_in=["release_package"],
          artifacts_out=["publication_receipt"],
          gate="OWNER_AUTHORIZED_PRIVATE_FIRST_PUBLICATION"),
        S(stage_id="ANALYTICS_LEARNING",owner="ANALYTICS",
          artifacts_in=["publication_receipt"],
          artifacts_out=["observations","hypotheses","learning_candidates"],
          gate="OWNED_NON_LIVESTREAM_ANALYTICS_OR_EXPLICIT_LIVE_POLICY"),
    ]

def _fail(stage_id: str):
    def handler(ctx: StageExecutionContext) -> StageHandlerResult:
        return StageHandlerResult(
            ok=False,error="MINECRAFT_REAL_GAME_QUALIFICATION_REQUIRED",
            detail=(f"{stage_id} needs real verified game footage/capture rights, "
                    "approved live infrastructure where applicable, and owner "
                    "authorization. Never render a Blender animation as real gameplay."),
        )
    return handler

def register_capture_handlers() -> StageHandlerRegistry:
    registry=StageHandlerRegistry()
    def intake(ctx: StageExecutionContext) -> StageHandlerResult:
        route=ctx.blueprint.minecraft_route
        if route is None or route.blocker or route.production_lane is Lane.FILM_ANIMATION:
            return StageHandlerResult(ok=False,error="MINECRAFT_WRONG_CAPTURE_LANE")
        from .contracts import DepartmentId
        ctx.kernel.blackboard.put(
            ctx.blueprint.project.studio_project_id,
            "mc_mode_brief",
            DepartmentId.STUDIO_MANAGEMENT,
            {
                "production_lane":route.production_lane.value,
                "subniche_id":route.subniche_id,
                "real_game_footage_required":True,
                "source_never_fake_live":True,
                "live_is_not_animated_story":True,
                "production_approved":False,
            },
        )
        return StageHandlerResult(ok=True,produced_artifacts=["mc_mode_brief"])
    registry.register("MC_MODE_INTAKE",intake)
    for name in (
        "MC_FORMAT_RESEARCH","MC_GAME_SOURCE_RIGHTS","MC_REAL_CAPTURE",
        "MC_CAPTURE_QC","MC_CAPTURE_PACKAGING","PUBLISHING",
        "ANALYTICS_LEARNING",
    ):
        registry.register(name,_fail(name))
    return registry
