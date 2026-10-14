from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from cinefactory.animal_long_slide import (
    LongSlideAssetRegistry,
    LongSlideExecutionPlanner,
    LongSlideProducer,
    MotionCompatibilityGraph,
)
from cinefactory.audio import CommandTTS, EspeakTTS
from cinefactory.autopilot.scaffold import LocalScaffoldPlanner
from cinefactory.domain.models import (
    AssetBibleSpec,
    DirectorPlan,
    ScriptSpec,
    ShotSpecBatch,
    StorySpec,
)
from cinefactory.media.ffmpeg import FFmpegToolchain
from cinefactory.post.editor import AutoEditor
from cinefactory.post.mastering import MasteringService
from cinefactory.production.asset_factory import AssetFactory
from cinefactory.production.contracts import DailiesReport, StoryboardGateReport
from cinefactory.production.storyboard import StoryboardGate
from cinefactory.production.video_factory import VideoFactory

from .acquisition import ToolTaskKnowledgeResolver
from .company_runner import (
    StageExecutionContext,
    StageHandlerRegistry,
    StageHandlerResult,
)
from .company_control import (
    EpisodeProductionSheet,
    FormatDNA,
    FormatDNACompiler,
    HumanApprovalGate,
    HumanApprovalState,
    ProductionSheetCompiler,
    SpendGate,
    SpendGatePolicy,
    SpendGateRequest,
)
from .block_adapter import CompanyToBlockAdapter, detect_block_style
from .block_production import BlockAnimationProducer
from .long_slide_adapter import LongSlideCompanyAdapter
from .contracts import ArtifactState, CapabilityKind, DepartmentId, PlanningInputKind
from .color_department import ColorBible, ColorPlan, ShotColorState
from .craft_execution import (
    AudioIntentCompiler,
    CameraDiagnosticsReport,
    ColorIntentCompiler,
    CraftExecutionBundle,
    CraftExecutionCompiler,
    CreativeIntentGraph,
    LightingColorIntentPlan,
    PerformanceDirectionPlan,
    SoundSpottingPlan,
)
from .creative_pipeline import (
    AnimaticPlan,
    CinematographyBible,
    CinematographyBibleCompiler,
    CreativeDevelopmentBrief,
    CreativeDevelopmentCompiler,
    CreativeReviewConference,
    CreativeReviewReport,
    DirectorTreatment,
    DirectorTreatmentCompiler,
    LayoutTechvisCompiler,
    LayoutTechvisPlan,
    ScriptReviewReport,
    ScriptReviewer,
    SemanticStoryboard,
    StoryArchitecture,
    StoryArchitectureCompiler,
    StoryboardAnimaticCompiler,
)
from .editorial import (
    EditDecision,
    EditDecisionGraph,
    EditReason,
    EditorialCompiler,
)
from .intelligence import NichePlaybookCompiler, PatternEvidence, PatternMiner
from .reference_intelligence import (
    ReferenceAcquisitionPolicy,
    ReferenceIntelligenceEngine,
    ResearchConfidenceEvaluator,
    ResearchPortfolioBuilder,
)
from .planning import PlanningDepartment, ProductionHandoff, ProductionStrategy, SceneToolPlanner
from .production_conference import (
    ProductionConferenceDecision,
    ProductionConferenceRoom,
)
from .adaptive_production import AdaptiveProductionSupervisor
from .scene_conference import (
    SceneProductionConference,
    SceneProductionConferenceReport,
)
from .script_intelligence import (
    ScriptInputCompiler,
    ScriptSourceMode,
    ScriptSourcePack,
)
from .production import ProductionRecipe
from .audio_department import (
    AudioCue,
    AudioPlan,
    AudioRole,
    DialogueLineTiming,
    DialogueLock,
    DialogueLockState,
    LipSyncPlan,
)
from .audio_conference import (
    AudioConferenceRequest,
    AudioObjective,
    AudioProductionConference,
    AudioProductionConferenceReport,
    default_audio_engine_candidates,
)
from .visual_model_conference import (
    VisualModality,
    VisualModelConference,
    VisualModelRequest,
    VisualObjective,
    default_visual_model_candidates,
)
from .qc_department import QCLayer, StudioQCFinding


class FilmHandlerConfig(BaseModel):
    production_mode: str = "slate"
    asset_workflow_id: str | None = None
    asset_workflow_version: str = "1"
    keyframe_workflow_id: str | None = None
    keyframe_workflow_version: str = "1"
    video_workflow_id: str | None = None
    video_workflow_version: str = "1"
    asset_candidates: int = Field(default=2, ge=1, le=6)
    keyframe_candidates: int = Field(default=2, ge=1, le=6)
    pilot_count: int = Field(default=2, ge=1, le=6)
    render_width: int = Field(default=1280, gt=0)
    render_height: int = Field(default=720, gt=0)
    master_width: int = Field(default=3840, gt=0)
    master_height: int = Field(default=2160, gt=0)
    fps: float = Field(default=24.0, gt=0)
    max_repair_rounds: int = Field(default=2, ge=0, le=5)
    min_visual_score: float = Field(default=0.72, ge=0.0, le=1.0)
    early_accept_score: float = Field(default=0.88, ge=0.0, le=1.0)
    turbo_dispatch: bool = False
    turbo_timeout_seconds: int = Field(default=1800, ge=30, le=21600)
    offline_3d_backend: str = "auto"
    allow_diagnostic_slate: bool = True
    block_quality_profile: str = "rtx3060_fast"
    blender_preview: bool = False
    tts_mode: str = "none"
    tts_command: str | None = None
    cosyvoice_command: str | None = None
    cosyvoice_vram_gb: float | None = Field(default=None, ge=0.0)
    cosyvoice_vram_verified: bool = False
    cosyvoice_production_qualified: bool = False
    voice: str | None = None
    require_lipsync: bool = False
    audio_vram_budget_gb: float = Field(default=12.0, ge=0.0)
    audio_min_quality: float = Field(default=0.70, ge=0.0, le=1.0)
    audio_require_commercial_safe: bool = True
    audio_require_vram_verified: bool = True
    voice_reference_map: dict[str, str] = Field(default_factory=dict)
    audio_enhancement_required: bool = False
    audio_source_separation_required: bool = False
    visual_vram_budget_gb: float = Field(default=12.0, ge=0.0)
    visual_model_min_quality: float = Field(default=0.70, ge=0.0, le=1.0)
    visual_require_commercial_safe: bool = True
    visual_require_vram_verified: bool = True
    allow_cloud_visual: bool = False
    allow_paid_visual: bool = False
    visual_cloud_budget_usd: float = Field(default=0.0, ge=0.0)
    require_human_topic_approval: bool = False
    require_human_spend_approval: bool = False
    require_human_final_approval: bool = False
    spend_local_only: bool = True
    spend_max_paid_usd: float = Field(default=0.0, ge=0.0)
    spend_max_pilot_count: int | None = Field(
        default=None,
        ge=1,
        le=6,
    )
    auto_reference_analysis: bool = True
    reference_max_duration_seconds: int = Field(
        default=2400,
        ge=30,
        le=21600,
    )
    reference_max_height: int = Field(
        default=720,
        ge=144,
        le=2160,
    )
    reference_channel_sample_size: int = Field(
        default=5,
        ge=1,
        le=20,
    )
    enable_research_handoff: bool = False


class FilmCompanyHandlers:
    """Compatibility layer from company departments to proven local factory services."""

    def __init__(
        self,
        runtime: Any,
        *,
        config: FilmHandlerConfig | None = None,
        scaffold: LocalScaffoldPlanner | None = None,
        reference_intelligence: Any | None = None,
    ) -> None:
        self.runtime = runtime
        self.studio = runtime.studio if hasattr(runtime, "studio") else runtime
        self.config = config or FilmHandlerConfig()
        self.scaffold = scaffold or LocalScaffoldPlanner()
        self.media = FFmpegToolchain()
        self.editor = AutoEditor(self.media)
        self.mastering = MasteringService(self.media)
        intelligence_root = Path(
            getattr(
                runtime,
                "root",
                getattr(self.studio, "root", "."),
            )
        )
        shared_reference_intelligence = getattr(
            self.studio,
            "reference_intelligence",
            None,
        )
        self.reference_intelligence = (
            reference_intelligence
            or shared_reference_intelligence
            or ReferenceIntelligenceEngine(
                intelligence_root,
                policy=ReferenceAcquisitionPolicy(
                    max_duration_seconds=(
                        self.config.reference_max_duration_seconds
                    ),
                    max_height=self.config.reference_max_height,
                    max_channel_videos=(
                        self.config.reference_channel_sample_size
                    ),
                ),
            )
        )

    def registry(self, *, niche: str | None = None,
                 production_route=None) -> StageHandlerRegistry:
        from .minecraft_subniche_v207 import Lane
        if (production_route is not None
                and production_route.production_lane is not None
                and production_route.production_lane is not Lane.FILM_ANIMATION):
            from .minecraft_capture_v207 import register_capture_handlers
            return register_capture_handlers()
        from .specialist_media_lanes_v205 import is_specialist_lane
        if is_specialist_lane(niche):
            from .specialist_media_handlers_v205 import register_specialist_handlers
            return register_specialist_handlers(StageHandlerRegistry())
        registry = StageHandlerRegistry()
        registry.register("PROJECT_INTAKE", self.project_intake)
        registry.register("PORTFOLIO_GREENLIGHT", self.portfolio_greenlight)
        registry.register("INTELLIGENCE", self.intelligence)
        if self.config.enable_research_handoff:
            registry.register("EVIDENCE", self.evidence)
        registry.register("CORPORATE_PREFLIGHT", self.corporate_preflight)
        registry.register("CREATIVE_DEVELOPMENT", self.creative_development)
        registry.register("CREATIVE_STRATEGY", self.creative_strategy)
        registry.register("CHANNEL_IDENTITY", self.channel_identity)
        registry.register("SERIES_EDITORIAL", self.series_editorial)
        registry.register("PLANNING", self.planning)
        registry.register("STORY_ARCHITECTURE", self.story_architecture)
        registry.register("WRITING", self.writing)
        registry.register("SCRIPT_REVIEW", self.script_review)
        registry.register("LOGIC", self.logic)
        registry.register("DIRECTOR_TREATMENT", self.director_treatment)
        registry.register("DIRECTION", self.direction)
        registry.register("PERFORMANCE", self.performance)
        registry.register("PRODUCTION_DESIGN", self.production_design)
        registry.register("CINEMATOGRAPHY", self.cinematography)
        registry.register("STORYBOARD_EDITORIAL", self.storyboard_editorial)
        registry.register("CRAFT_EXECUTION_DESIGN", self.craft_execution_design)
        registry.register("LAYOUT_TECHVIS", self.layout_techvis)
        registry.register("CREATIVE_REVIEW", self.creative_review)
        if (
            self.config.tts_mode != "none"
            or bool(self.config.cosyvoice_command)
            or bool(self.config.voice_reference_map)
        ):
            registry.register("VOICE_PREP", self.voice_prep)
        if hasattr(self.runtime, "assets"):
            registry.register("ASSET_BUILD", self.asset_build)
            registry.register("PREVIS", self.previs)
            registry.register("PRODUCTION", self.production)
            registry.register("EDITORIAL", self.editorial)
            registry.register("AUDIO", self.audio)
            registry.register("FINISHING", self.finishing)
            registry.register("FINAL_QC", self.final_qc)
        registry.register("TECHNICAL_DIRECTION", self.technical_direction)
        registry.register("PACKAGING", self.packaging)
        registry.register("PUBLISHING", self.publishing)
        registry.register("ANALYTICS_LEARNING", self.analytics_learning)
        # EVIDENCE is never auto-registered; factual verification must fail closed.
        # VOICE_PREP stays skipped when voice is not configured; configured voice routes fail-closed.
        return registry

    @staticmethod
    def _content(payload: BaseModel | dict | list | str | None) -> Any:
        if isinstance(payload, BaseModel):
            return payload.model_dump(mode="json")
        return payload

    def _write(
        self,
        ctx: StageExecutionContext,
        artifact_type: str,
        payload: BaseModel | dict | list | str | None,
    ) -> None:
        project_id = ctx.blueprint.project.studio_project_id
        owner = DepartmentId(ctx.stage.owner)
        content = self._content(payload)
        try:
            existing = self.studio.blackboard.get(project_id, artifact_type)
            if existing.get("payload") == content:
                return
        except KeyError:
            pass
        self.studio.blackboard.put(
            project_id,
            artifact_type,
            owner,
            content if not isinstance(payload, BaseModel) else payload,
            state=ArtifactState.VALIDATED,
        )

    def _payload(self, ctx: StageExecutionContext, artifact_type: str) -> Any:
        project_id = ctx.blueprint.project.studio_project_id
        return self.studio.blackboard.get(project_id, artifact_type)["payload"]

    def _model(self, ctx: StageExecutionContext, artifact_type: str, model):
        return model.model_validate(self._payload(ctx, artifact_type))

    def _conference_policy(
        self,
        ctx: StageExecutionContext,
    ) -> dict[str, Any]:
        try:
            strategy = self._model(
                ctx,
                "production_strategy",
                ProductionStrategy,
            )
            return dict(strategy.conference_policy)
        except (KeyError, ValueError):
            return {}

    def _conference_candidates(
        self,
        ctx: StageExecutionContext,
        base_count: int,
    ) -> int:
        policy = self._conference_policy(ctx)
        multiplier = float(
            policy.get("candidate_multiplier", 1.0) or 1.0
        )
        return max(
            1,
            min(6, int(round(base_count * multiplier))),
        )

    def _conference_qc_target(
        self,
        ctx: StageExecutionContext,
    ) -> float:
        policy = self._conference_policy(ctx)
        return max(
            self.config.min_visual_score,
            float(policy.get("qc_target", 0.0) or 0.0),
        )

    def _conference_repair_budget(
        self,
        ctx: StageExecutionContext,
    ) -> int:
        policy = self._conference_policy(ctx)
        requested = int(
            policy.get(
                "repair_budget",
                self.config.max_repair_rounds,
            )
            or 0
        )
        return max(
            0,
            min(self.config.max_repair_rounds, requested),
        )

    def _conference_render_size(
        self,
        ctx: StageExecutionContext,
    ) -> tuple[int, int]:
        policy = self._conference_policy(ctx)
        scale = max(
            0.5,
            min(
                1.0,
                float(policy.get("render_scale", 1.0) or 1.0),
            ),
        )
        width = max(
            64,
            int(round(self.config.render_width * scale / 2.0)) * 2,
        )
        height = max(
            64,
            int(round(self.config.render_height * scale / 2.0)) * 2,
        )
        return width, height

    def _audio_candidates(self):
        return default_audio_engine_candidates(
            tts_mode=self.config.tts_mode,
            has_tts_command=bool(self.config.tts_command),
            cosyvoice_executable=bool(self.config.cosyvoice_command),
            cosyvoice_qualified=(
                bool(self.config.cosyvoice_command)
                and self.config.cosyvoice_production_qualified
            ),
            cosyvoice_vram_gb=self.config.cosyvoice_vram_gb,
            cosyvoice_vram_verified=self.config.cosyvoice_vram_verified,
            ffmpeg_executable=True,
        )

    def _audio_request(
        self,
        *,
        job_id: str,
        objective: AudioObjective,
        scene_id: str | None = None,
        line_id: str | None = None,
        speaker_id: str | None = None,
        text: str | None = None,
        voice_reference: str | None = None,
    ) -> AudioConferenceRequest:
        return AudioConferenceRequest(
            job_id=job_id,
            scene_id=scene_id,
            line_id=line_id,
            speaker_id=speaker_id,
            text=text,
            objective=objective,
            min_quality=self.config.audio_min_quality,
            max_vram_gb=self.config.audio_vram_budget_gb,
            require_commercial_safe=self.config.audio_require_commercial_safe,
            require_vram_verified=self.config.audio_require_vram_verified,
            voice_reference=voice_reference,
        )

    @staticmethod
    def _dialogue_objective(line, speaker: str, voice_reference: str | None) -> AudioObjective:
        if voice_reference:
            return AudioObjective.VOICE_CLONE
        if speaker.upper() in {"NARRATOR", "NARRATION", "VOICEOVER", "VO"}:
            return AudioObjective.NARRATION
        expressive_text = " ".join(
            value for value in (line.text, line.subtext or "") if value
        ).lower()
        expressive_markers = (
            "whisper", "angry", "furious", "cry", "crying", "laugh",
            "laughing", "shout", "shouting", "excited", "terrified",
            "sad", "trembling", "softly", "yell", "scream",
        )
        if any(marker in expressive_text for marker in expressive_markers):
            return AudioObjective.EXPRESSIVE_DIALOGUE
        return AudioObjective.CHARACTER_DIALOGUE

    def _tts_for_engine(self, engine_id: str):
        if engine_id == "tts.espeak":
            return EspeakTTS()
        if engine_id == "cosyvoice3.local" and self.config.cosyvoice_command:
            return CommandTTS(self.config.cosyvoice_command)
        if engine_id == "tts.command" and self.config.tts_command:
            return CommandTTS(self.config.tts_command)
        raise RuntimeError(f"audio engine is not executable by VOICE_PREP: {engine_id}")

    def _visual_model_readiness(self) -> tuple[set[str], set[str]]:
        executable: set[str] = set()
        qualified: set[str] = set()
        models = getattr(self.runtime, "models", None)
        workflows = getattr(self.runtime, "workflows", None)
        if models is None or workflows is None:
            return executable, qualified
        runtime_root = Path(getattr(self.runtime, "root", "."))
        for workflow in workflows.list():
            if (
                workflow.executor_id != "local.comfyui"
                or not workflow.local_only
                or not workflow.model_revision
            ):
                continue
            try:
                model = models.get(
                    workflow.model_id,
                    workflow.model_revision,
                )
            except KeyError:
                continue
            if model.local_path:
                model_path = Path(model.local_path)
                if not model_path.is_absolute():
                    model_path = runtime_root / model_path
                if not model_path.is_file():
                    continue
            executable.add(model.model_id)
            try:
                models.require_approved(
                    workflow.model_id,
                    workflow.model_revision,
                )
            except Exception:
                continue
            qualified.add(model.model_id)
        return executable, qualified

    def _visual_candidates(self):
        executable, qualified = self._visual_model_readiness()
        return default_visual_model_candidates(
            executable_model_ids=executable,
            qualified_model_ids=qualified,
            cloud_enabled=self.config.allow_cloud_visual,
        )

    @staticmethod
    def _visual_objective_for_scene(scene) -> VisualObjective:
        objective = str(scene.scene_production_objective or "")
        if objective in {"RETENTION_HOOK", "ACTION"}:
            return VisualObjective.HERO_CINEMATIC
        return VisualObjective.GENERATIVE_VIDEO

    def _visual_model_request(
        self,
        *,
        scene,
        duration_seconds: float,
    ) -> VisualModelRequest:
        return VisualModelRequest(
            request_id=f"VISUAL_{scene.scene_id}",
            scene_id=scene.scene_id,
            modality=VisualModality.VIDEO,
            objective=self._visual_objective_for_scene(scene),
            min_quality=self.config.visual_model_min_quality,
            max_vram_gb=self.config.visual_vram_budget_gb,
            require_commercial_safe=(
                self.config.visual_require_commercial_safe
            ),
            require_vram_verified=(
                self.config.visual_require_vram_verified
            ),
            allow_cloud=self.config.allow_cloud_visual,
            allow_paid=self.config.allow_paid_visual,
            require_reference=True,
            max_cost_usd=self.config.visual_cloud_budget_usd,
            duration_seconds=max(0.0, duration_seconds),
        )

    def _tool_knowledge(
        self,
        ctx: StageExecutionContext,
        *,
        tool_id: str,
        operations: list[str],
        task: str,
        artifact_type: str,
    ):
        context = ToolTaskKnowledgeResolver(self.studio).resolve(
            tool_id=tool_id,
            operations=operations,
            task=task,
            strict=True,
        )
        self._write(ctx, artifact_type, context)
        return context

    def _root(self, ctx: StageExecutionContext) -> Path:
        if ctx.project_root is not None:
            root = ctx.project_root
        elif hasattr(self.runtime, "root"):
            root = Path(self.runtime.root) / "data" / "projects" / ctx.blueprint.project.studio_project_id
        else:
            root = Path(self.studio.root) / "data" / "projects" / ctx.blueprint.project.studio_project_id
        root.mkdir(parents=True, exist_ok=True)
        return root

    @staticmethod
    def _finding(code: str, layer: QCLayer, message: str) -> StageHandlerResult:
        return StageHandlerResult(
            ok=False,
            error=code,
            qc_findings=[
                StudioQCFinding(
                    code=code,
                    layer=layer,
                    message=message,
                )
            ],
        )

    @staticmethod
    def _input_has_abstract_patterns(item) -> bool:
        for key in (
            "patterns",
            "production_patterns",
            "format_patterns",
            "retention_patterns",
            "observations",
        ):
            value = item.metadata.get(key)
            if isinstance(value, str) and value.strip():
                return True
            if isinstance(value, list) and any(
                isinstance(entry, str) and entry.strip()
                for entry in value
            ):
                return True
        return False

    @staticmethod
    def _safe_preanalyzed_profile(item) -> dict[str, Any]:
        return {
            "profile_id": item.input_id,
            "patterns": item.metadata.get("patterns", []),
            "production_patterns": item.metadata.get(
                "production_patterns",
                [],
            ),
            "format_patterns": item.metadata.get(
                "format_patterns",
                [],
            ),
            "retention_patterns": item.metadata.get(
                "retention_patterns",
                [],
            ),
            "observations": item.metadata.get("observations", []),
            "confidence": item.metadata.get("confidence", 0.65),
            "raw_expression_allowed": False,
        }

    def project_intake(self, ctx: StageExecutionContext) -> StageHandlerResult:
        project = ctx.blueprint.project
        engine = self.studio.professional_company.intake
        intake = engine.intake(project)
        self._write(ctx, "project_intake", intake)
        if intake.explicit_niche and not intake.recognized_niche:
            return StageHandlerResult(
                ok=False,
                produced_artifacts=["project_intake"],
                checkpoint_ref="blackboard://project_intake",
                error="UNKNOWN_EXPLICIT_NICHE",
                detail=f"unregistered niche: {intake.resolved_niche}",
            )
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://project_intake",
        )

    def portfolio_greenlight(self, ctx: StageExecutionContext) -> StageHandlerResult:
        project = ctx.blueprint.project
        decision = self.studio.professional_company.intake.portfolio_greenlight(
            project
        )
        self._write(ctx, "portfolio_greenlight", decision)
        if not decision.approved_for_research:
            return StageHandlerResult(
                ok=False,
                produced_artifacts=["portfolio_greenlight"],
                checkpoint_ref="blackboard://portfolio_greenlight",
                error="PORTFOLIO_GREENLIGHT_BLOCKED",
                detail="; ".join(decision.blockers),
            )
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://portfolio_greenlight",
        )

    def evidence(self, ctx: StageExecutionContext) -> StageHandlerResult:
        # This stage is registered only for an explicitly imported company
        # research handoff. The G02 map is a review QUEUE, not a forged PASS.
        from .research_evidence_bridge_v266 import load as load_handoff
        project = ctx.blueprint.project
        research = load_handoff(
            Path(getattr(self.runtime, "root", getattr(self.studio, "root", "."))),
            project.studio_project_id,
        )
        if research is None:
            return StageHandlerResult(
                ok=False, error="RESEARCH_HANDOFF_MISSING",
                detail="No project-bound source data was imported.",
            )
        queue = {
            "project_id": project.studio_project_id,
            "source_video_ids": research["source_video_ids_pending_independent_review"],
            "review_window_count": research["source_30second_window_count"],
            "source_sha256": research["source_sha256"],
            "g02_status": research["g02_status"],
            "reviewer_signed": False,
            "original_native_video_and_audio_semantic_qc_passed": False,
            "film_derived_production_method_approved": False,
        }
        self._write(ctx, "evidence_map", queue)
        return StageHandlerResult(
            ok=False,
            produced_artifacts=["evidence_map"],
            checkpoint_ref="blackboard://evidence_map",
            error="G02_INDEPENDENT_AV_REVIEW_PENDING",
            detail="Full original film and soundtrack require independent timecoded semantic verification.",
        )

    def corporate_preflight(self, ctx: StageExecutionContext) -> StageHandlerResult:
        project = ctx.blueprint.project
        competitor_profiles = self._payload(ctx, "competitor_profiles")
        research_pack = self._payload(ctx, "research_pack")
        decision = self.studio.professional_company.intake.corporate_preflight(
            project,
            competitor_profiles=(
                competitor_profiles
                if isinstance(competitor_profiles, list)
                else []
            ),
            research_pack=(
                research_pack if isinstance(research_pack, dict) else {}
            ),
        )
        resolved_niche = decision.evidence.get("resolved_niche")
        readiness = None
        if resolved_niche:
            readiness = (
                self.studio.professional_company.intake.config.readiness(
                    str(resolved_niche)
                )
            )
        seo_brief = {
            "project_id": project.studio_project_id,
            "platform": project.platform,
            "niche_id": resolved_niche,
            "strict_niche_gate": bool(
                decision.evidence.get("strict_niche_gate")
            ),
            "seo_discovery_ready": decision.seo_discovery_ready,
            "competitor_research_ready": (
                decision.competitor_research_ready
            ),
            "readiness": (
                readiness.model_dump(mode="json")
                if readiness is not None
                else None
            ),
            "required_next_actions": [
                item
                for item in decision.blockers
                if (
                    "SEO" in item
                    or "COMPETITOR" in item
                    or "NICHE_" in item
                )
            ],
            "evidence_policy": {
                "competitor_private_metrics_as_public_fact": False,
                "allowed_labels": [
                    "PUBLIC_FACT",
                    "ESTIMATE",
                    "INFERENCE",
                    "UNKNOWN",
                ],
            },
        }
        self._write(ctx, "corporate_preflight", decision)
        self._write(ctx, "seo_discovery_brief", seo_brief)
        if not decision.approved:
            return StageHandlerResult(
                ok=False,
                produced_artifacts=list(ctx.stage.artifacts_out),
                checkpoint_ref="blackboard://corporate_preflight",
                error="CORPORATE_PREFLIGHT_BLOCKED",
                detail="; ".join(decision.blockers),
            )
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://corporate_preflight",
        )

    def intelligence(self, ctx: StageExecutionContext) -> StageHandlerResult:
        project = ctx.blueprint.project
        niche = project.niche or project.domain or "generic"

        safe_metadata_keys = {
            "patterns",
            "production_patterns",
            "format_patterns",
            "retention_patterns",
            "observations",
            "confidence",
            "max_videos",
        }
        quarantined_input_kinds = {
            PlanningInputKind.COMPETITOR_VIDEO,
            PlanningInputKind.REFERENCE_VIDEO,
            PlanningInputKind.CHANNEL_RESEARCH,
        }
        input_refs = [
            {
                "input_id": item.input_id,
                "kind": item.kind.value,
                "notes": (
                    []
                    if item.kind in quarantined_input_kinds
                    else list(item.notes)
                ),
                "metadata": {
                    key: value
                    for key, value in item.metadata.items()
                    if key in safe_metadata_keys
                },
            }
            for item in project.planning_inputs
        ]
        competitor_profiles: list[dict[str, Any]] = []
        channel_research: list[dict[str, Any]] = []
        research_reports: list[dict[str, Any]] = []
        analyzed_profiles = []
        analyzed_decompositions = []
        promoted_patterns: list[PatternEvidence] = []
        reference_findings: list[str] = []
        reference_summaries: list[dict[str, Any]] = []

        for item in project.planning_inputs:
            record = {
                "input_id": item.input_id,
                "kind": item.kind.value,
                "notes": (
                    []
                    if item.kind in quarantined_input_kinds
                    else list(item.notes)
                ),
                "metadata": {
                    key: value
                    for key, value in item.metadata.items()
                    if key in safe_metadata_keys
                },
                "raw_expression_allowed": False,
            }
            has_patterns = self._input_has_abstract_patterns(item)

            if item.kind in {
                PlanningInputKind.COMPETITOR_VIDEO,
                PlanningInputKind.REFERENCE_VIDEO,
            }:
                if has_patterns:
                    competitor_profiles.append(
                        self._safe_preanalyzed_profile(item)
                    )
                    continue
                if (
                    self.config.auto_reference_analysis
                    and item.uri
                ):
                    try:
                        report = self.reference_intelligence.video(
                            item.uri
                        )
                        safe = report.planning_profile()
                        safe["profile_id"] = item.input_id
                        competitor_profiles.append(safe)
                        analyzed_profiles.append(report.profile)
                        analyzed_decompositions.append(report)
                        reference_summaries.append(
                            {
                                "input_id": item.input_id,
                                "kind": item.kind.value,
                                "video_id": report.source.video_id,
                                "duration_seconds": (
                                    report.source.duration_seconds
                                ),
                                "analysis_features": safe.get(
                                    "analysis_features",
                                    {},
                                ),
                                "raw_expression_allowed": False,
                            }
                        )
                    except Exception as exc:
                        reference_findings.append(
                            "REFERENCE_VIDEO_ANALYSIS_FAILED:"
                            f"{item.input_id}:"
                            f"{type(exc).__name__}:{exc}"
                        )
                continue

            if item.kind is PlanningInputKind.CHANNEL_RESEARCH:
                if has_patterns:
                    channel_research.append(record)
                    competitor_profiles.append(
                        self._safe_preanalyzed_profile(item)
                    )
                    continue
                if (
                    self.config.auto_reference_analysis
                    and item.uri
                ):
                    try:
                        analysis = (
                            self.reference_intelligence.channel(
                                item.uri,
                                niche=niche,
                                limit=(
                                    self.config
                                    .reference_channel_sample_size
                                ),
                            )
                        )
                        safe = analysis.planning_profile()
                        safe["profile_id"] = item.input_id
                        competitor_profiles.append(safe)
                        channel_research.append(
                            {
                                "input_id": item.input_id,
                                "kind": item.kind.value,
                                "sample_count": len(
                                    analysis.profiles
                                ),
                                "pattern_count": len(
                                    analysis.patterns
                                ),
                                "findings": analysis.findings,
                                "raw_expression_allowed": False,
                            }
                        )
                        analyzed_profiles.extend(
                            item.profile
                            for item in analysis.profiles
                        )
                        analyzed_decompositions.extend(
                            analysis.profiles
                        )
                        promoted_patterns.extend(
                            analysis.patterns
                        )
                        reference_findings.extend(
                            analysis.findings
                        )
                    except Exception as exc:
                        reference_findings.append(
                            "CHANNEL_ANALYSIS_FAILED:"
                            f"{item.input_id}:"
                            f"{type(exc).__name__}:{exc}"
                        )
                else:
                    channel_research.append(record)
                continue

            if item.kind is PlanningInputKind.RESEARCH_REPORT:
                research_reports.append(record)

        if len(analyzed_profiles) >= 2:
            promoted_patterns.extend(
                PatternMiner().mine(
                    analyzed_profiles,
                    min_support=2,
                    min_ratio=0.4,
                )
            )

        merged_patterns: dict[
            tuple[str, str],
            PatternEvidence,
        ] = {}
        for pattern in promoted_patterns:
            key = (
                pattern.observation_kind.value,
                pattern.abstraction.strip().lower(),
            )
            current = merged_patterns.get(key)
            if current is None:
                merged_patterns[key] = pattern.model_copy(
                    deep=True
                )
                continue
            video_ids = sorted(
                {
                    *current.sample_video_ids,
                    *pattern.sample_video_ids,
                }
            )
            combined_support = max(
                current.support_count,
                pattern.support_count,
                len(video_ids),
            )
            combined_sample = max(
                current.sample_count,
                pattern.sample_count,
                combined_support,
            )
            total_weight = max(
                1,
                current.support_count + pattern.support_count,
            )
            confidence = (
                current.confidence * current.support_count
                + pattern.confidence * pattern.support_count
            ) / total_weight
            merged_patterns[key] = current.model_copy(
                update={
                    "sample_video_ids": video_ids,
                    "support_count": combined_support,
                    "sample_count": combined_sample,
                    "confidence": min(0.99, confidence),
                }
            )
        deduped_patterns = [
            merged_patterns[key]
            for key in sorted(merged_patterns)
        ]

        gaps: list[str] = []
        if project.planning_inputs and not competitor_profiles:
            gaps.append(
                "reference inputs were supplied but no abstract "
                "competitor/reference patterns were available"
            )
        if len(analyzed_profiles) == 1:
            gaps.append(
                "only one automatically analyzed video is available; "
                "single-video observations are not promoted to niche rules"
            )

        research_confidence = ResearchConfidenceEvaluator().evaluate(
            analyzed_decompositions,
            deduped_patterns,
        )
        playbook = NichePlaybookCompiler().compile(
            niche,
            deduped_patterns,
            gaps=gaps,
        )
        research_portfolio = ResearchPortfolioBuilder().build(
            niche=niche,
            decompositions=analyzed_decompositions,
            patterns=deduped_patterns,
            confidence=research_confidence,
        )
        research_pack = {
            "prompt": project.prompt,
            "mode": (
                "reference_intelligence"
                if analyzed_profiles
                else "local_or_preanalyzed_inputs"
            ),
            "niche": niche,
            "planning_inputs": input_refs,
            "channel_research": channel_research,
            "research_reports": research_reports,
            "reference_analysis": reference_summaries,
            "reference_intelligence_findings": (
                reference_findings
            ),
            "promoted_pattern_count": len(deduped_patterns),
            "research_confidence": (
                research_confidence.model_dump(mode="json")
            ),
            "research_portfolio": (
                research_portfolio.planning_summary()
            ),
            "limitations": [
                (
                    "Automatically analyzed competitor/reference "
                    "expression remains quarantined; only abstract "
                    "observations enter planning."
                ),
                (
                    "A single competitor video may inform observations "
                    "but does not by itself become a niche rule."
                ),
                (
                    "No external factual claim becomes verified merely "
                    "because it appears in a competitor/reference video."
                ),
                (
                    "Evidence-required formats must pass the separate "
                    "EVIDENCE department."
                ),
            ],
        }
        # Versioned external research is bound by project ID and source hashes;
        # never promote metadata or re-observed 1x clips to certified G02.
        from .research_evidence_bridge_v266 import load as load_handoff
        handoff = load_handoff(
            Path(getattr(self.runtime, "root", getattr(self.studio, "root", "."))),
            project.studio_project_id,
        )
        if handoff is not None:
            research_pack["source_research_handoff"] = {
                "schema": handoff["schema"],
                "public_candidate_sample": handoff["public_candidate_sample"],
                "reported_public_metadata_candidates": handoff["reported_public_metadata_candidates"],
                "g02_status": handoff["g02_status"],
                "source_sha256": handoff["source_sha256"],
                "independent_semantic_approval": False,
                "source_based_production_advice_approved": False,
            }
            research_pack["limitations"].append(
                "External Maizen reference videos still require G02 independent native AV semantic audit."
            )
        self._write(ctx, "research_pack", research_pack)
        self._write(
            ctx,
            "research_confidence",
            research_confidence,
        )
        self._write(
            ctx,
            "research_portfolio",
            research_portfolio,
        )
        self._write(
            ctx,
            "competitor_profiles",
            competitor_profiles,
        )
        self._write(ctx, "niche_playbook", playbook)
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://intelligence",
        )

    def creative_development(self, ctx: StageExecutionContext) -> StageHandlerResult:
        project = ctx.blueprint.project
        corporate = dict(self._payload(ctx, "corporate_preflight"))
        seo_brief = dict(self._payload(ctx, "seo_discovery_brief"))
        brief = CreativeDevelopmentCompiler().compile(
            project_id=project.studio_project_id,
            prompt=project.prompt,
            niche_id=(
                ctx.blueprint.project_intake.resolved_niche
                if ctx.blueprint.project_intake is not None
                else project.niche
            ),
            seo_brief=seo_brief,
            corporate_preflight=corporate,
        )
        promise_contract = {
            "project_id": project.studio_project_id,
            "audience_promise": brief.audience_promise,
            "emotional_promise": brief.emotional_promise,
            "must_deliver": [
                "clear opening promise",
                "deliberate change in each major content unit",
                "original expression",
                "production method capable of preserving the promise",
            ],
            "must_avoid": [
                "unmotivated filler",
                "camera spectacle without story/content purpose",
                "competitor-expression copying",
                "silent quality downgrade",
            ],
        }
        self._write(ctx, "creative_development_brief", brief)
        self._write(ctx, "audience_promise_contract", promise_contract)
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://creative_development",
        )

    def channel_identity(self, ctx: StageExecutionContext) -> StageHandlerResult:
        from .channel_franchise_v206 import ChannelLibrary
        pinned = ctx.blueprint.channel_episode_strategy
        if pinned is None:
            return StageHandlerResult(ok=False,error="CHANNEL_STRATEGY_NOT_BOUND")
        library = ChannelLibrary(self.studio.root)
        try:
            bible, digest = library.load(pinned.channel_brand_id)
            if pinned.series_id == "standalone_film":
                fresh=library.resolve_standalone(
                    pinned.channel_brand_id,
                    ctx.blueprint.project.studio_project_id,
                    ctx.blueprint.project.prompt,
                    pinned.subniche,
                )
            else:
                fresh = library.resolve_episode(
                    pinned.channel_brand_id, pinned.series_id, pinned.episode_id,
                    reuse_characters=ctx.blueprint.project.reuse_series_characters,
                )
        except (OSError, ValueError, PermissionError, KeyError) as exc:
            return StageHandlerResult(
                ok=False,error="CHANNEL_BIBLE_UNAVAILABLE_OR_INVALID:" + type(exc).__name__,
            )
        if digest != pinned.source_sha256 or fresh != pinned:
            return StageHandlerResult(ok=False,error="CHANNEL_BIBLE_CHANGED_AFTER_BLUEPRINT")
        cast = {
            c.character_id: c.model_dump(mode="json")
            for c in bible.character_registry
            if c.character_id in pinned.cast_ids
        }
        self._write(ctx, "channel_identity", {
            "schema": "cine.channel.identity_receipt.v206",
            "channel_brand_id": pinned.channel_brand_id,
            "source_sha256": pinned.source_sha256,
            "niche": bible.niche,
            "proposed_brand_name": bible.proposed_brand_name,
            "audience_promise": bible.audience_promise,
            "brand_status": bible.channel_status,
            "characters": cast,
            "world_identity": bible.world_identity,
            "reuse_series_characters":ctx.blueprint.project.reuse_series_characters,
            "new_episode_cast_required":not ctx.blueprint.project.reuse_series_characters,
            "forbidden_imitation": list(bible.forbidden_imitation),
            "youtube_channel_owner_verified": False,
            "release_permission": False,
        })
        self._write(ctx, "episode_strategy", pinned)
        return StageHandlerResult(
            ok=True,produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://channel_identity",
        )

    def series_editorial(self, ctx: StageExecutionContext) -> StageHandlerResult:
        from .channel_franchise_v206 import ChannelEpisodeStrategy
        strategy = self._model(ctx,"episode_strategy",ChannelEpisodeStrategy)
        identity = dict(self._payload(ctx,"channel_identity"))
        creative = dict(self._payload(ctx,"creative_brief"))
        if (identity.get("source_sha256")!=strategy.source_sha256
                or identity.get("channel_brand_id")!=strategy.channel_brand_id):
            return StageHandlerResult(ok=False,error="CHANNEL_EPISODE_LINEAGE_MISMATCH")
        self._write(ctx,"series_editorial_plan",{
            "schema":"cine.channel.editorial_handoff.v206",
            "channel_brand_id":strategy.channel_brand_id,
            "series_id":strategy.series_id,"episode_id":strategy.episode_id,
            "channel_bible_sha256":strategy.source_sha256,
            "format_id":strategy.format_id,"subniche":strategy.subniche,
            "original_premise":strategy.original_premise,
            "opening_hook":strategy.opening_hook,
            "story_conflict":strategy.central_conflict,
            "payoff":strategy.episode_payoff,
            "character_development":(
                strategy.character_development
                if ctx.blueprint.project.reuse_series_characters
                else "NEW_ORIGINAL_CAST_REQUIRES_FRESH_SCRIPT_AND_RIG_REVIEW"
            ),
            "cast_ids":list(strategy.cast_ids),
            "reuse_series_characters":ctx.blueprint.project.reuse_series_characters,
            "world_rules":list(strategy.world_rules),
            "continuity_requirements":list(strategy.continuity_requirements),
            "production_reuse":list(strategy.production_reuse),
            "raw_reference_expression_allowed":False,
            "independent_script_review":"REQUIRED_BEFORE_COMMERCIAL_RELEASE",
            "creative_handoff_present":bool(creative),
            "automatically_greenlit":False,
        })
        return StageHandlerResult(
            ok=True,produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://series_editorial_plan",
        )

    @staticmethod
    def _original_series_prompt(ctx: StageExecutionContext) -> str:
        project=ctx.blueprint.project
        strategy=ctx.blueprint.channel_episode_strategy
        if strategy is None:
            return project.prompt
        return (
            project.prompt + "\n\n"
            "ORIGINAL EPISODE CONTRACT - DO NOT COPY REFERENCE CHANNELS: "
            + strategy.original_premise
            + ". Opening: " + strategy.opening_hook
            + ". Conflict: " + strategy.central_conflict
            + ". Character growth: " + (
                strategy.character_development
                if project.reuse_series_characters
                else "Create a NEW original protagonist and cast for this video; "
                     "never reuse past character names, designs, voices, skins or rigs "
                     "without explicit owner authorization."
            )
            + ". Payoff: " + strategy.episode_payoff
            + ". World rules: " + "; ".join(strategy.world_rules)
            + ". Continuity: " + "; ".join(strategy.continuity_requirements)
        )

    def creative_strategy(self, ctx: StageExecutionContext) -> StageHandlerResult:
        project = ctx.blueprint.project
        strategy = self.scaffold.topic_strategy(project.prompt)
        packaging = self.scaffold.packaging(project.prompt, strategy)
        differentiation = self.scaffold.originality_plan(strategy)
        try:
            development = self._model(
                ctx,
                "creative_development_brief",
                CreativeDevelopmentBrief,
            )
            development_payload = development.model_dump(mode="json")
        except KeyError:
            development_payload = None
        creative_brief = {
            "topic_strategy": strategy.model_dump(mode="json"),
            "channel_episode_context": (
                ctx.blueprint.channel_episode_strategy.model_dump(mode="json")
                if ctx.blueprint.channel_episode_strategy is not None else None
            ),
            "packaging_hypothesis": packaging.model_dump(mode="json"),
            "differentiation_plan": differentiation.model_dump(mode="json"),
            "creative_development": development_payload,
        }
        format_dna = FormatDNACompiler().compile(
            project=project,
            project_dna=ctx.blueprint.project_dna,
            product=ctx.blueprint.studio_plan.product,
        )
        topic_gate = HumanApprovalGate(
            gate_id="HUMAN_TOPIC_APPROVAL",
            project_id=project.studio_project_id,
            purpose="approve topic/creative direction before expensive production",
            required=self.config.require_human_topic_approval,
            state=(
                HumanApprovalState.PENDING
                if self.config.require_human_topic_approval
                else HumanApprovalState.AUTO_APPROVED
            ),
            approver=(
                None
                if self.config.require_human_topic_approval
                else "AUTONOMOUS_POLICY"
            ),
            evidence_refs=["creative_brief", "format_dna"],
        )
        self._write(ctx, "creative_brief", creative_brief)
        self._write(ctx, "project_dna", ctx.blueprint.project_dna)
        self._write(ctx, "format_dna", format_dna)
        self._write(ctx, "human_topic_gate", topic_gate)
        self._write(ctx, "packaging_hypothesis", packaging)
        self._write(ctx, "differentiation_plan", differentiation)
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://creative_strategy",
        )

    def planning(self, ctx: StageExecutionContext) -> StageHandlerResult:
        project = ctx.blueprint.project
        topic_gate = HumanApprovalGate.model_validate(
            self._payload(ctx, "human_topic_gate")
        )
        if not topic_gate.executable:
            return self._finding(
                "HUMAN_TOPIC_APPROVAL_REQUIRED",
                QCLayer.TECHNICAL,
                "planning is waiting for explicit topic approval",
            )
        script_source_pack = (
            ctx.blueprint.script_source_pack
            or ScriptInputCompiler(
                getattr(
                    self.runtime,
                    "root",
                    getattr(self.studio, "root", "."),
                )
            ).compile(project.planning_inputs)
        )
        strategy = PlanningDepartment().compile(
            project=project,
            product=ctx.blueprint.studio_plan.product,
            research_pack=dict(self._payload(ctx, "research_pack")),
            competitor_profiles=self._payload(ctx, "competitor_profiles"),
            niche_playbook=self._payload(ctx, "niche_playbook"),
            research_confidence=self._payload(
                ctx,
                "research_confidence",
            ),
            research_portfolio=self._payload(
                ctx,
                "research_portfolio",
            ),
            script_source_pack=script_source_pack,
        )
        conference = ProductionConferenceRoom().deliberate(
            kernel=self.studio,
            project=project,
            product=ctx.blueprint.studio_plan.product,
            strategy=strategy,
            script_pack=script_source_pack,
        )
        self._write(ctx, "production_conference", conference)
        if not conference.executable:
            self._write(ctx, "production_strategy", strategy)
            self._write(ctx, "script_source_pack", script_source_pack)
            return self._finding(
                "PRODUCTION_CONFERENCE_BLOCKED",
                QCLayer.TECHNICAL,
                "; ".join(conference.blockers)
                or "production conference found no viable execution policy",
            )
        strategy = ProductionConferenceRoom.apply(
            strategy,
            conference,
        )
        self._write(ctx, "production_strategy", strategy)
        self._write(ctx, "script_source_pack", script_source_pack)
        self._write(
            ctx,
            "reference_pattern_map",
            {
                "patterns": [
                    item.model_dump(mode="json")
                    for item in strategy.reference_patterns
                ],
                "source_input_ids": strategy.input_ids,
                "raw_competitor_expression_allowed": False,
            },
        )
        self._write(
            ctx,
            "originality_boundaries",
            {
                "rules": strategy.originality_boundaries,
                "enforcement": "planning_and_writing_context",
            },
        )
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://planning",
        )

    def story_architecture(self, ctx: StageExecutionContext) -> StageHandlerResult:
        project = ctx.blueprint.project
        source = self._model(
            ctx,
            "script_source_pack",
            ScriptSourcePack,
        )
        if source.mode is ScriptSourceMode.LOCKED_SCRIPT:
            if source.compiled_story is not None:
                story = StorySpec.model_validate(source.compiled_story)
            elif source.compiled_script is not None:
                story = ScriptInputCompiler.story_from_script(
                    ScriptSpec.model_validate(source.compiled_script)
                )
            else:
                return self._finding(
                    "STORY_ARCHITECTURE_SOURCE_MISSING",
                    QCLayer.STORY_LOGIC,
                    "locked script source has no compiled story or script",
                )
        elif source.mode is ScriptSourceMode.OUTLINE:
            if source.compiled_story is None:
                return self._finding(
                    "STORY_ARCHITECTURE_OUTLINE_MISSING",
                    QCLayer.STORY_LOGIC,
                    "outline mode requires compiled_story before story architecture",
                )
            story = StorySpec.model_validate(source.compiled_story)
        else:
            story = self.scaffold.story(self._original_series_prompt(ctx))

        architecture = StoryArchitectureCompiler().compile(
            project.studio_project_id,
            story,
        )
        self._write(ctx, "story", story)
        self._write(ctx, "story_architecture", architecture)
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://story_architecture",
        )

    def writing(self, ctx: StageExecutionContext) -> StageHandlerResult:
        project = ctx.blueprint.project
        source = self._model(
            ctx,
            "script_source_pack",
            ScriptSourcePack,
        )
        try:
            story = self._model(ctx, "story", StorySpec)
        except KeyError:
            story = None

        if source.mode is ScriptSourceMode.LOCKED_SCRIPT:
            if source.compiled_script is None:
                return self._finding(
                    "USER_SCRIPT_COMPILE_MISSING",
                    QCLayer.STORY_LOGIC,
                    "locked user script did not compile into ScriptSpec",
                )
            script = ScriptSpec.model_validate(source.compiled_script)
            if story is None:
                if source.compiled_story is not None:
                    story = StorySpec.model_validate(source.compiled_story)
                else:
                    story = ScriptInputCompiler.story_from_script(script)
        elif source.mode is ScriptSourceMode.OUTLINE:
            if story is None:
                if source.compiled_story is None:
                    return self._finding(
                        "SCRIPT_OUTLINE_COMPILE_MISSING",
                        QCLayer.STORY_LOGIC,
                        "script outline did not compile into StorySpec",
                    )
                story = StorySpec.model_validate(source.compiled_story)
            script = self.scaffold.script(story)
        else:
            if story is None:
                story = self.scaffold.story(self._original_series_prompt(ctx))
            script = self.scaffold.script(story)

        self._write(ctx, "story", story)
        self._write(ctx, "script", script)
        self._write(
            ctx,
            "beat_graph",
            {
                **story.model_dump(mode="json"),
                "script_source_mode": source.mode.value,
                "script_revision_policy": (
                    source.revision_policy.value
                ),
                "script_source_hash": (
                    source.primary_content_sha256
                ),
                "channel_episode_lineage": (
                    ctx.blueprint.channel_episode_strategy.model_dump(mode="json")
                    if ctx.blueprint.channel_episode_strategy is not None else None
                ),
                "original_script_independent_review_required": bool(
                    ctx.blueprint.channel_episode_strategy is not None
                ),
            },
        )
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://writing",
        )

    def script_review(self, ctx: StageExecutionContext) -> StageHandlerResult:
        project = ctx.blueprint.project
        script = self._model(ctx, "script", ScriptSpec)
        architecture = self._model(
            ctx,
            "story_architecture",
            StoryArchitecture,
        )
        report = ScriptReviewer().review(
            project.studio_project_id,
            script,
            architecture,
        )
        self._write(ctx, "script_review", report)
        if not report.passed:
            blocking = [
                f"{item.code}:{item.scene_id or 'PROJECT'}"
                for item in report.issues
                if item.severity.value in {"HIGH", "CRITICAL"}
            ]
            return self._finding(
                "SCRIPT_REVIEW_BLOCKED",
                QCLayer.STORY_LOGIC,
                "; ".join(blocking) or "independent script review failed",
            )
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://script_review",
        )

    def logic(self, ctx: StageExecutionContext) -> StageHandlerResult:
        from .script_continuity_v209 import inspect_script_continuity

        script = self._model(ctx, "script", ScriptSpec)
        report, continuity = inspect_script_continuity(script)
        self._write(ctx, "logic_report", report)
        self._write(ctx, "continuity_contract", continuity)
        if not report["passed"]:
            codes = [f["code"] + ":" + f["scene_id"] for f in report["findings"]]
            return self._finding(
                "SCRIPT_LOGIC_CONTRADICTION", QCLayer.STORY_LOGIC,
                "; ".join(codes),
            )
        # Structural pass is NOT an independent claim that plot, acting,
        # original expression or cause-and-effect are creatively qualified.
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://logic",
            detail="STRUCTURAL_ONLY_INDEPENDENT_STORY_REVIEW_PENDING",
        )

    def director_treatment(self, ctx: StageExecutionContext) -> StageHandlerResult:
        project = ctx.blueprint.project
        script = self._model(ctx, "script", ScriptSpec)
        review = self._model(ctx, "script_review", ScriptReviewReport)
        if not review.passed:
            return self._finding(
                "DIRECTOR_TREATMENT_SCRIPT_NOT_APPROVED",
                QCLayer.STORY_LOGIC,
                "director treatment requires an approved independent script review",
            )
        preliminary_director = self.scaffold.director(script)
        treatment = DirectorTreatmentCompiler().compile(
            project.studio_project_id,
            script,
            preliminary_director,
            ctx.blueprint.project_dna,
        )
        self._write(ctx, "director_treatment", treatment)
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://director_treatment",
        )

    def direction(self, ctx: StageExecutionContext) -> StageHandlerResult:
        script = self._model(ctx, "script", ScriptSpec)
        director = self.scaffold.director(script)
        try:
            treatment = self._model(
                ctx,
                "director_treatment",
                DirectorTreatment,
            )
        except KeyError:
            treatment = None
        if treatment is not None:
            planned = {scene.scene_id for scene in director.scenes}
            treated = {scene.scene_id for scene in treatment.scenes}
            if planned != treated:
                return self._finding(
                    "DIRECTOR_TREATMENT_ALIGNMENT_FAILED",
                    QCLayer.STORY_LOGIC,
                    "director plan scene set does not match approved director treatment",
                )
            self._write(
                ctx,
                "director_treatment_alignment",
                {
                    "passed": True,
                    "scene_ids": sorted(planned),
                    "principles": {
                        "story_priority": treatment.story_priority,
                        "camera": treatment.camera_principles,
                        "performance": treatment.performance_principles,
                        "editorial": treatment.editorial_principles,
                        "sound": treatment.sound_principles,
                    },
                },
            )
        blocking = [scene.blocking.model_dump(mode="json") for scene in director.scenes]
        performance_intent = {
            scene.scene_id: scene.performance_notes
            for scene in director.scenes
        }
        self._write(ctx, "director_cut", director)
        self._write(ctx, "blocking_plan", {"scenes": blocking})
        self._write(ctx, "performance_intent", performance_intent)
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://direction",
        )

    def performance(self, ctx: StageExecutionContext) -> StageHandlerResult:
        craft = self._tool_knowledge(
            ctx,
            tool_id="craft.performance",
            operations=[
                "objective",
                "trigger reaction",
                "gaze",
                "pose clarity",
                "body mechanics",
                "timing",
            ],
            task="translate dramatic intent into readable character performance",
            artifact_type="performance_craft_knowledge",
        )
        if craft.blocked:
            return self._finding(
                "CRAFT_KNOWLEDGE_GAP",
                QCLayer.PERFORMANCE,
                "performance:" + ",".join(craft.missing_operations),
            )
        director = self._model(ctx, "director_cut", DirectorPlan)
        plan = {
            "scenes": [
                {
                    "scene_id": scene.scene_id,
                    "performance_notes": scene.performance_notes,
                    "audience_feel": scene.audience_feel,
                }
                for scene in director.scenes
            ],
            "rules": [
                "performance follows objective",
                "reaction must have a trigger",
                "preserve listening behavior",
            ],
            "craft_knowledge_chunk_ids": craft.chunk_ids,
        }
        self._write(ctx, "performance_plan", plan)
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://performance",
        )

    def production_design(self, ctx: StageExecutionContext) -> StageHandlerResult:
        script = self._model(ctx, "script", ScriptSpec)
        bible = self.scaffold.assets(script)
        world_bible = {
            "locations": [item.model_dump(mode="json") for item in bible.scenes],
            "continuity_rule": "preserve topology and lighting anchors",
        }
        design_bible = {
            "visual_style_lock": bible.visual_style_lock,
            "characters": [item.model_dump(mode="json") for item in bible.characters],
            "props": [item.model_dump(mode="json") for item in bible.props],
        }
        self._write(ctx, "asset_bible", bible)
        self._write(ctx, "world_bible", world_bible)
        self._write(ctx, "design_bible", design_bible)
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://production_design",
        )

    def cinematography(self, ctx: StageExecutionContext) -> StageHandlerResult:
        craft = self._tool_knowledge(
            ctx,
            tool_id="craft.cinematography",
            operations=[
                "coverage",
                "eyeline",
                "axis",
                "motivated camera",
                "lens",
                "lighting",
            ],
            task="design coverage, lenses, camera movement and lighting for the scene",
            artifact_type="cinematography_craft_knowledge",
        )
        if craft.blocked:
            return self._finding(
                "CRAFT_KNOWLEDGE_GAP",
                QCLayer.CAMERA,
                "cinematography:" + ",".join(craft.missing_operations),
            )
        script = self._model(ctx, "script", ScriptSpec)
        director = self._model(ctx, "director_cut", DirectorPlan)
        shots = self.scaffold.shots(script, director)
        batch = ShotSpecBatch(shots=shots)
        camera_plan = {
            shot.shot_id: shot.camera.model_dump(mode="json")
            for shot in shots
        }
        lighting_plan = {
            shot.shot_id: {
                "light_state": shot.entry_state.light_state,
                "time_of_day": shot.entry_state.time_of_day,
            }
            for shot in shots
        }
        cinematography_bible = CinematographyBibleCompiler().compile(
            ctx.blueprint.project.studio_project_id,
            batch,
            ctx.blueprint.project_dna,
        )
        self._write(ctx, "shot_book", batch)
        self._write(ctx, "camera_plan", camera_plan)
        self._write(ctx, "lighting_plan", lighting_plan)
        self._write(ctx, "cinematography_bible", cinematography_bible)
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://cinematography",
        )

    def storyboard_editorial(self, ctx: StageExecutionContext) -> StageHandlerResult:
        project = ctx.blueprint.project
        shots = self._model(ctx, "shot_book", ShotSpecBatch)
        storyboard, animatic = StoryboardAnimaticCompiler().compile(
            project.studio_project_id,
            shots,
        )
        review = {
            "project_id": project.studio_project_id,
            "passed": True,
            "panel_count": len(storyboard.panels),
            "animatic_duration_seconds": animatic.total_duration_seconds,
            "coverage_findings": list(storyboard.coverage_findings),
            "review_rules": [
                "storyboard is reviewed as a sequence, not isolated images",
                "reaction shots must be motivated by story/performance",
                "coverage must preserve information order and geography",
                "animatic timing should reveal pacing problems before expensive production",
            ],
        }
        self._write(ctx, "semantic_storyboard", storyboard)
        self._write(ctx, "animatic_plan", animatic)
        self._write(ctx, "storyboard_review", review)
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://storyboard_editorial",
        )

    def asset_build(self, ctx: StageExecutionContext) -> StageHandlerResult:
        bible = self._model(ctx, "asset_bible", AssetBibleSpec)
        root = self._root(ctx)
        conference_qc = self._conference_qc_target(ctx)
        conference_candidates = self._conference_candidates(
            ctx,
            self.config.asset_candidates,
        )
        report = AssetFactory(
            self.runtime,
            visual_qc=None,
            min_visual_score=conference_qc,
            diagnostic_slate=(
                self.config.production_mode == "slate"
                and self.config.allow_diagnostic_slate
            ),
        ).build(
            ctx.blueprint.project.studio_project_id,
            bible,
            root,
            mode=self.config.production_mode,
            workflow_id=self.config.asset_workflow_id,
            workflow_version=self.config.asset_workflow_version,
            candidates_per_asset=conference_candidates,
        )
        if not report.passed:
            return self._finding(
                "ASSET_BUILD_FAILED",
                QCLayer.IDENTITY,
                "; ".join(report.findings) or "canonical asset selection failed",
            )
        selections = [item.model_dump(mode="json") for item in report.selections]
        self._write(ctx, "assets", {"selections": selections})
        self._write(ctx, "asset_manifest", report)
        self._write(
            ctx,
            "canonical_references",
            {item.asset_key: item.selected_path for item in report.selections},
        )
        # AssetFactory mutates reference IDs onto the bible; persist that enriched version.
        self._write(ctx, "asset_bible_built", bible)
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref=str(root / "assets" / "generated"),
        )

    def voice_prep(self, ctx: StageExecutionContext) -> StageHandlerResult:
        script = self._model(ctx, "script", ScriptSpec)
        root = self._root(ctx)

        if (
            not ctx.stage.required
            and self.config.tts_mode == "none"
        ):
            dialogue = DialogueLock(
                project_id=ctx.blueprint.project.studio_project_id,
                state=DialogueLockState.DRAFT,
                lines=[],
            )
            lipsync = LipSyncPlan(
                project_id=ctx.blueprint.project.studio_project_id,
                jobs=[],
                blocked=False,
            )
            self._write(
                ctx,
                "voice_tracks",
                {
                    "tracks": [],
                    "status": "not_required_for_format",
                },
            )
            self._write(ctx, "dialogue_lock", dialogue)
            self._write(ctx, "lipsync_plan", lipsync)
            self._write(
                ctx,
                "audio_production_conference",
                AudioProductionConferenceReport(
                    project_id=ctx.blueprint.project.studio_project_id,
                    decisions=[],
                ),
            )
            return StageHandlerResult(
                ok=True,
                produced_artifacts=list(ctx.stage.artifacts_out),
                checkpoint_ref="voice://not-required",
            )

        conference = AudioProductionConference(self._audio_candidates())
        requests: list[AudioConferenceRequest] = []
        voice_jobs: list[tuple[Any, Any, str, str, str | None]] = []
        line_index = 0
        for scene in script.scenes:
            for line in scene.dialogue:
                line_index += 1
                line_id = f"DLG_{line_index:04d}"
                speaker = line.speaker or "NARRATOR"
                voice_reference = self.config.voice_reference_map.get(speaker)
                objective = self._dialogue_objective(
                    line,
                    speaker,
                    voice_reference,
                )
                requests.append(
                    self._audio_request(
                        job_id=line_id,
                        objective=objective,
                        scene_id=scene.scene_id,
                        line_id=line_id,
                        speaker_id=speaker,
                        text=line.text,
                        voice_reference=voice_reference,
                    )
                )
                voice_jobs.append(
                    (scene, line, line_id, speaker, voice_reference)
                )

        conference_report = conference.run(
            ctx.blueprint.project.studio_project_id,
            requests,
        )
        self._write(
            ctx,
            "audio_production_conference",
            conference_report,
        )
        if conference_report.blocked:
            blocked = [
                item for item in conference_report.decisions if item.blocked
            ]
            details = []
            for decision in blocked:
                gate_failures = sorted({
                    blocker
                    for assessment in decision.assessments
                    for blocker in assessment.blockers
                })
                details.append(
                    f"{decision.job_id}:{decision.objective.value}:"
                    + ",".join(gate_failures)
                )
            return self._finding(
                "AUDIO_PRODUCTION_CONFERENCE_BLOCKED",
                QCLayer.AUDIO,
                "; ".join(details),
            )

        decisions = {
            item.job_id: item for item in conference_report.decisions
        }
        timings: list[DialogueLineTiming] = []
        voice_tracks: list[dict[str, Any]] = []
        cursor = 0.0
        for scene, line, line_id, speaker, voice_reference in voice_jobs:
            decision = decisions[line_id]
            output = root / "audio" / "dialogue" / f"{line_id}.wav"
            rendered = None
            duration = 0.0
            selected_engine = None
            render_errors: list[str] = []
            engine_chain = [
                decision.primary_engine_id,
                *decision.fallback_engine_ids,
            ]
            for engine_id in (item for item in engine_chain if item):
                try:
                    tts = self._tts_for_engine(engine_id)
                    rendered = tts.synthesize(
                        line.text,
                        output,
                        language=ctx.blueprint.project.language,
                        voice=self.config.voice,
                    )
                    duration = self.media.probe(rendered).duration
                    selected_engine = engine_id
                    break
                except Exception as exc:
                    render_errors.append(
                        f"{engine_id}:{type(exc).__name__}:{exc}"
                    )
            if rendered is None or selected_engine is None:
                return self._finding(
                    "VOICE_RENDER_FAILED",
                    QCLayer.AUDIO,
                    f"{line_id}:" + " | ".join(render_errors),
                )
            timings.append(
                DialogueLineTiming(
                    line_id=line_id,
                    segment_id=scene.scene_id,
                    speaker_id=speaker,
                    target_entity_id=speaker,
                    start_seconds=cursor,
                    duration_seconds=max(duration, 0.01),
                    audio_ref=str(rendered),
                )
            )
            voice_tracks.append(
                {
                    "line_id": line_id,
                    "scene_id": scene.scene_id,
                    "speaker_id": speaker,
                    "path": str(rendered),
                    "duration_seconds": duration,
                    "objective": decision.objective.value,
                    "engine_id": selected_engine,
                    "primary_engine_id": decision.primary_engine_id,
                    "fallback_used": selected_engine != decision.primary_engine_id,
                    "voice_reference": voice_reference,
                }
            )
            cursor += duration

        dialogue = DialogueLock(
            project_id=ctx.blueprint.project.studio_project_id,
            state=DialogueLockState.LOCKED,
            lines=timings,
        )
        if self.config.require_lipsync:
            return self._finding(
                "LIPSYNC_CAPABILITY_REQUIRED",
                QCLayer.PERFORMANCE,
                "phoneme lip-sync was requested but no validated local lipsync capability is executable",
            )
        lipsync = LipSyncPlan(
            project_id=ctx.blueprint.project.studio_project_id,
            jobs=[],
            blocked=False,
        )
        self._write(ctx, "voice_tracks", {"tracks": voice_tracks})
        self._write(ctx, "dialogue_lock", dialogue)
        self._write(ctx, "lipsync_plan", lipsync)
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref=str(root / "audio" / "dialogue"),
        )

    def craft_execution_design(self, ctx: StageExecutionContext) -> StageHandlerResult:
        project = ctx.blueprint.project
        bundle = CraftExecutionCompiler().compile(
            project_id=project.studio_project_id,
            story=self._model(ctx, "story_architecture", StoryArchitecture),
            script=self._model(ctx, "script", ScriptSpec),
            director=self._model(ctx, "director_cut", DirectorPlan),
            treatment=self._model(ctx, "director_treatment", DirectorTreatment),
            shots=self._model(ctx, "shot_book", ShotSpecBatch),
            cinematography=self._model(
                ctx,
                "cinematography_bible",
                CinematographyBible,
            ),
            animatic=self._model(ctx, "animatic_plan", AnimaticPlan),
        )
        self._write(
            ctx,
            "creative_intent_graph",
            bundle.creative_intent_graph,
        )
        self._write(
            ctx,
            "camera_diagnostics",
            bundle.camera_diagnostics,
        )
        self._write(
            ctx,
            "performance_direction",
            bundle.performance_direction,
        )
        self._write(
            ctx,
            "lighting_color_intent",
            bundle.lighting_color_intent,
        )
        self._write(
            ctx,
            "sound_spotting",
            bundle.sound_spotting,
        )
        if not bundle.passed:
            blockers = [
                item.code
                for item in bundle.camera_diagnostics.findings
                if item.severity.value == "BLOCKER"
            ]
            blockers.extend(
                item.code
                for item in bundle.performance_direction.findings
                if item.severity.value == "BLOCKER"
            )
            return self._finding(
                "CRAFT_EXECUTION_DESIGN_BLOCKED",
                QCLayer.CAMERA,
                "; ".join(blockers)
                or "camera/performance execution design failed",
            )
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://craft_execution_design",
        )

    def layout_techvis(self, ctx: StageExecutionContext) -> StageHandlerResult:
        project = ctx.blueprint.project
        shots = self._model(ctx, "shot_book", ShotSpecBatch)
        plan = LayoutTechvisCompiler().compile(
            project.studio_project_id,
            shots,
        )
        self._write(ctx, "layout_techvis", plan)
        if not plan.passed:
            return self._finding(
                "LAYOUT_TECHVIS_BLOCKED",
                QCLayer.CAMERA,
                "; ".join(plan.findings) or "layout/techvis validation failed",
            )
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://layout_techvis",
        )

    def previs(self, ctx: StageExecutionContext) -> StageHandlerResult:
        try:
            bible = self._model(ctx, "asset_bible_built", AssetBibleSpec)
        except KeyError:
            bible = self._model(ctx, "asset_bible", AssetBibleSpec)
        shots = self._model(ctx, "shot_book", ShotSpecBatch).shots
        root = self._root(ctx)
        conference_qc = self._conference_qc_target(ctx)
        conference_candidates = self._conference_candidates(
            ctx,
            self.config.keyframe_candidates,
        )
        render_width, render_height = (
            self._conference_render_size(ctx)
        )
        report = StoryboardGate(
            self.runtime,
            visual_qc=None,
            min_visual_score=conference_qc,
            diagnostic_slate=(
                self.config.production_mode == "slate"
                and self.config.allow_diagnostic_slate
            ),
        ).build(
            shots,
            bible,
            root,
            mode=self.config.production_mode,
            workflow_id=self.config.keyframe_workflow_id,
            workflow_version=self.config.keyframe_workflow_version,
            candidates_per_shot=conference_candidates,
            width=render_width,
            height=render_height,
        )
        if not report.passed:
            return self._finding(
                "PREVIS_KEYFRAME_FAILED",
                QCLayer.CAMERA,
                "; ".join(report.findings) or "storyboard approval failed",
            )
        keyframes = {
            item.shot_id: item.selected_path
            for item in report.shots
            if item.selected_path
        }
        self._write(ctx, "storyboard", report)
        self._write(ctx, "keyframes", keyframes)
        self._write(
            ctx,
            "previs_report",
            {
                "passed": True,
                "approved_shots": sorted(keyframes),
                "count": len(keyframes),
            },
        )
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref=str(root / "storyboard" / "keyframes"),
        )

    def creative_review(self, ctx: StageExecutionContext) -> StageHandlerResult:
        project = ctx.blueprint.project
        script_review = self._model(
            ctx,
            "script_review",
            ScriptReviewReport,
        )
        storyboard = self._model(
            ctx,
            "semantic_storyboard",
            SemanticStoryboard,
        )
        animatic = self._model(ctx, "animatic_plan", AnimaticPlan)
        cinematography = self._model(
            ctx,
            "cinematography_bible",
            CinematographyBible,
        )
        layout = self._model(
            ctx,
            "layout_techvis",
            LayoutTechvisPlan,
        )
        previs_report = dict(self._payload(ctx, "previs_report"))
        review = CreativeReviewConference().review(
            project_id=project.studio_project_id,
            script_review=script_review,
            storyboard=storyboard,
            animatic=animatic,
            cinematography=cinematography,
            layout_techvis=layout,
            previs_passed=bool(previs_report.get("passed")),
        )
        camera = self._model(
            ctx,
            "camera_diagnostics",
            CameraDiagnosticsReport,
        )
        performance = self._model(
            ctx,
            "performance_direction",
            PerformanceDirectionPlan,
        )
        extra_blockers: list[str] = []
        if not camera.passed:
            extra_blockers.append("CAMERA_DIAGNOSTICS_NOT_APPROVED")
        if not performance.passed:
            extra_blockers.append("PERFORMANCE_DIRECTION_NOT_APPROVED")
        if extra_blockers:
            merged = list(dict.fromkeys([*review.blockers, *extra_blockers]))
            review = CreativeReviewReport(
                project_id=review.project_id,
                passed=False,
                review_departments=review.review_departments,
                blockers=merged,
                warnings=review.warnings,
                approved_for_technical_direction=False,
            )
        self._write(ctx, "creative_review_approval", review)
        if not review.passed:
            return self._finding(
                "CREATIVE_REVIEW_BLOCKED",
                QCLayer.STORY_LOGIC,
                "; ".join(review.blockers) or "creative review did not approve production",
            )
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://creative_review",
        )

    def technical_direction(self, ctx: StageExecutionContext) -> StageHandlerResult:
        strategy = self._model(
            ctx,
            "production_strategy",
            ProductionStrategy,
        )
        shots = self._model(ctx, "shot_book", ShotSpecBatch).shots
        global_conference = self._model(
            ctx,
            "production_conference",
            ProductionConferenceDecision,
        )
        scene_conference = SceneProductionConference().deliberate(
            project_id=ctx.blueprint.project.studio_project_id,
            shots=shots,
            global_decision=global_conference,
        )
        self._write(
            ctx,
            "scene_production_conference",
            scene_conference,
        )

        scene_ids: list[str] = []
        for shot in shots:
            if shot.scene_id not in scene_ids:
                scene_ids.append(shot.scene_id)
        segment_capabilities: dict[str, list[CapabilityKind]] = {}
        scene_to_segment: dict[str, str] = {}
        for scene_id, segment_plan in zip(
            scene_ids,
            ctx.blueprint.studio_plan.segments,
        ):
            segment_capabilities[scene_id] = list(
                segment_plan.segment.capability_requirements
            )
            scene_to_segment[scene_id] = (
                segment_plan.segment.segment_id
            )

        handoff = SceneToolPlanner(self.studio).compile_handoff(
            project_id=ctx.blueprint.project.studio_project_id,
            strategy=strategy,
            shots=shots,
            segment_capabilities=segment_capabilities,
            scene_policies=scene_conference.policy_map(),
        )

        try:
            intent_graph = self._model(
                ctx,
                "creative_intent_graph",
                CreativeIntentGraph,
            )
        except KeyError:
            intent_graph = None
        try:
            performance_direction = self._model(
                ctx,
                "performance_direction",
                PerformanceDirectionPlan,
            )
        except KeyError:
            performance_direction = None

        if intent_graph is not None:
            intent_by_scene = {
                item.scene_id: item
                for item in intent_graph.scenes
            }
            shot_intent_by_scene: dict[str, list] = {}
            for item in intent_graph.shots:
                shot_intent_by_scene.setdefault(item.scene_id, []).append(item)
            for scene_plan in handoff.scene_plans:
                scene_intent = intent_by_scene.get(scene_plan.scene_id)
                if scene_intent is not None:
                    scene_plan.scene_production_objective = (
                        scene_intent.purpose
                    )
                    scene_plan.notes.extend([
                        f"audience_know={scene_intent.audience_know}",
                        f"audience_feel={scene_intent.audience_feel}",
                    ])
                for shot_intent in shot_intent_by_scene.get(
                    scene_plan.scene_id,
                    [],
                ):
                    scene_plan.notes.append(
                        "shot_intent:"
                        + shot_intent.shot_id
                        + ":"
                        + shot_intent.shot_purpose
                    )

        if performance_direction is not None:
            perf_by_scene: dict[str, list] = {}
            for beat in performance_direction.beats:
                perf_by_scene.setdefault(beat.scene_id, []).append(beat)
            for scene_plan in handoff.scene_plans:
                for beat in perf_by_scene.get(scene_plan.scene_id, []):
                    scene_plan.notes.append(
                        "performance:"
                        + beat.shot_id
                        + ":"
                        + beat.subject_id
                        + ":"
                        + beat.objective
                    )

        memory_application = None
        production_memory = getattr(
            self.studio,
            "production_memory",
            None,
        )
        if production_memory is not None:
            handoff, memory_application = (
                production_memory.apply_to_handoff(
                    project_id=(
                        ctx.blueprint.project.studio_project_id
                    ),
                    handoff=handoff,
                    conference=global_conference,
                )
            )
        self._write(
            ctx,
            "production_memory_advice",
            (
                memory_application
                if memory_application is not None
                else {
                    "project_id": (
                        ctx.blueprint.project.studio_project_id
                    ),
                    "advices": [],
                    "adjusted_scene_ids": [],
                }
            ),
        )

        durations_by_scene: dict[str, float] = {}
        for shot in shots:
            durations_by_scene[str(shot.scene_id)] = (
                durations_by_scene.get(str(shot.scene_id), 0.0)
                + float(shot.duration_seconds or 0.0)
            )
        visual_requests = [
            self._visual_model_request(
                scene=scene,
                duration_seconds=durations_by_scene.get(
                    str(scene.scene_id),
                    0.0,
                ),
            )
            for scene in handoff.scene_plans
            if (
                scene.render_assignment is not None
                and scene.render_assignment.capability_kind
                is CapabilityKind.AI_VIDEO
            )
        ]
        visual_candidates = self._visual_candidates()
        visual_report = VisualModelConference(
            visual_candidates
        ).run(
            ctx.blueprint.project.studio_project_id,
            visual_requests,
        )
        visual_by_scene = {
            item.scene_id: item
            for item in visual_report.decisions
            if item.scene_id is not None
        }
        for scene in handoff.scene_plans:
            decision = visual_by_scene.get(scene.scene_id)
            if decision is None:
                continue
            scene.visual_model_id = decision.primary_model_id
            scene.visual_model_fallback_ids = list(
                decision.fallback_model_ids
            )
            scene.visual_model_blockers = sorted({
                blocker
                for assessment in decision.assessments
                for blocker in assessment.blockers
            }) if decision.blocked else []
            if decision.blocked:
                handoff.blockers.append(
                    f"{scene.scene_id}:NO_QUALIFIED_VISUAL_MODEL"
                )
        handoff.blockers = list(dict.fromkeys(handoff.blockers))
        if handoff.blockers:
            handoff.executable = False
        self._write(
            ctx,
            "visual_model_conference",
            visual_report,
        )

        # Rebind the original semantic recipe to runtime-aware scene choices.
        # A scene may intentionally change renderer class (for example a 3D
        # dialogue scene followed by a generative dream montage), so rebinding
        # happens by segment as well as by capability kind.
        recipe = ctx.blueprint.production_recipe.model_copy(deep=True)
        global_by_kind = {
            assignment.capability_kind: assignment
            for assignment in handoff.global_assignments
            if assignment.execution_ready
        }
        render_by_segment: dict[str, Any] = {}
        for scene in handoff.scene_plans:
            segment_id = scene_to_segment.get(scene.scene_id)
            assignment = scene.render_assignment
            if (
                segment_id
                and assignment is not None
                and assignment.execution_ready
            ):
                render_by_segment[segment_id] = assignment

        runtime_blockers: list[str] = []
        primary_renderer_bound: set[str] = set()
        for task in recipe.tasks:
            assignment = None
            original_kind = task.capability_kind
            if (
                original_kind in SceneToolPlanner.RENDER_KINDS
                and task.segment_id not in primary_renderer_bound
            ):
                assignment = render_by_segment.get(task.segment_id)
                if assignment is not None:
                    task.capability_kind = assignment.capability_kind
                    primary_renderer_bound.add(task.segment_id)
            else:
                assignment = global_by_kind.get(original_kind)

            if assignment is not None:
                task.capability_id = assignment.selected_capability_id
                task.executable = True
                task.payload["selected_tool_id"] = (
                    assignment.selected_tool_id
                )
                task.payload["ideal_capability_id"] = (
                    assignment.ideal_capability_id
                )
                task.payload["fallback_capability_ids"] = list(
                    assignment.fallback_capability_ids
                )
                task.payload["routing_reasons"] = list(
                    assignment.reasons
                )
            if not task.executable:
                runtime_blockers.append(
                    f"{task.task_id}:NO_RUNTIME_APPROVED_BACKEND"
                )
        recipe.blockers = runtime_blockers
        recipe.blocked = bool(runtime_blockers)

        resource_plan: dict[str, Any] = {}
        for task in recipe.tasks:
            resource_plan[task.resource_class] = (
                resource_plan.get(task.resource_class, 0) + 1
            )
        script_profile = strategy.script_production_profile
        if script_profile:
            resource_plan["script_scene_count"] = int(
                script_profile.get("scene_count", 0) or 0
            )
            resource_plan["script_dialogue_lines"] = int(
                script_profile.get("dialogue_line_count", 0) or 0
            )
            resource_plan["script_estimated_seconds"] = int(
                round(
                    float(
                        script_profile.get(
                            "estimated_duration_seconds",
                            0.0,
                        )
                        or 0.0
                    )
                )
            )
            resource_plan["performance_load_percent"] = int(
                round(
                    float(
                        script_profile.get(
                            "performance_load",
                            0.0,
                        )
                        or 0.0
                    )
                    * 100
                )
            )
            resource_plan["continuity_load_percent"] = int(
                round(
                    float(
                        script_profile.get(
                            "continuity_load",
                            0.0,
                        )
                        or 0.0
                    )
                    * 100
                )
            )
            resource_plan["voice_required"] = int(
                CapabilityKind.SPEECH
                in strategy.script_required_capabilities
            )
            resource_plan["lipsync_required"] = int(
                CapabilityKind.LIPSYNC
                in strategy.script_required_capabilities
            )
        if strategy.conference_policy:
            conference_width, conference_height = (
                self._conference_render_size(ctx)
            )
            resource_plan["conference_lane"] = (
                strategy.conference_lane
            )
            resource_plan["conference_score"] = round(
                strategy.conference_score,
                4,
            )
            resource_plan["render_width"] = conference_width
            resource_plan["render_height"] = conference_height
            resource_plan["candidate_multiplier"] = float(
                strategy.conference_policy.get(
                    "candidate_multiplier",
                    1.0,
                )
                or 1.0
            )
            resource_plan["repair_budget"] = (
                self._conference_repair_budget(ctx)
            )
            resource_plan["qc_target"] = (
                self._conference_qc_target(ctx)
            )
            resource_plan["compute_budget_index"] = float(
                strategy.conference_policy.get(
                    "compute_budget_index",
                    0.0,
                )
                or 0.0
            )
            resource_plan["backend_mix_policy"] = str(
                strategy.conference_policy.get(
                    "backend_mix_policy",
                    "unspecified",
                )
            )
        lane_counts: dict[str, int] = {}
        for scene_decision in scene_conference.scenes:
            key = scene_decision.selected_lane.value
            lane_counts[key] = lane_counts.get(key, 0) + 1
        resource_plan["scene_conference_lane_counts"] = lane_counts
        resource_plan["backend_switch_budget"] = (
            scene_conference.backend_switch_budget
        )
        resource_plan["scene_conference_scene_count"] = len(
            scene_conference.scenes
        )

        route_decisions = {
            item.segment.segment_id: [
                route.model_dump(mode="json") for route in item.routes
            ]
            for item in ctx.blueprint.studio_plan.segments
        }
        route_decisions["runtime_handoff"] = {
            "selected_tool_ids": handoff.selected_tool_ids,
            "planning_mode": handoff.planning_mode.value,
            "fallback_policy": handoff.fallback_policy,
            "scene_conference_global_lane": (
                scene_conference.global_lane.value
            ),
            "backend_switch_budget": (
                scene_conference.backend_switch_budget
            ),
        }

        self._write(ctx, "production_recipe", recipe)
        self._write(ctx, "resource_plan", resource_plan)
        self._write(ctx, "routing_decisions", route_decisions)
        self._write(
            ctx,
            "scene_tool_plan",
            {
                "scenes": [
                    item.model_dump(mode="json")
                    for item in handoff.scene_plans
                ],
                "conference": (
                    scene_conference.model_dump(mode="json")
                ),
            },
        )
        self._write(ctx, "production_handoff", handoff)

        blockers = list(dict.fromkeys([*handoff.blockers, *recipe.blockers]))
        diagnostic_override = (
            self.config.production_mode == "slate"
            and self.config.allow_diagnostic_slate
        )
        if blockers and diagnostic_override:
            # Slate mode is explicitly non-production. Preserve fail-closed
            # semantics for real output while allowing isolated/dev pipeline tests.
            for task in recipe.tasks:
                if not task.executable:
                    task.executable = True
                    task.capability_id = "diagnostic.slate"
                    task.payload["diagnostic_override"] = True
            recipe.blocked = False
            recipe.blockers = []
            handoff = handoff.model_copy(
                update={
                    "executable": True,
                    "blockers": [],
                    "fallback_policy": [
                        *handoff.fallback_policy,
                        "DIAGNOSTIC_ONLY: slate output is not production approval",
                    ],
                }
            )
            self._write(ctx, "production_recipe", recipe)
            self._write(ctx, "production_handoff", handoff)
            blockers = []
        if blockers:
            return StageHandlerResult(
                ok=False,
                error="PRODUCTION_HANDOFF_BLOCKED:" + ";".join(blockers),
            )

        format_dna = self._model(ctx, "format_dna", FormatDNA)
        source_artifacts = {
            name: self._payload(ctx, name)
            for name in ProductionSheetCompiler.REQUIRED_SOURCE_ARTIFACTS
        }
        production_sheet = ProductionSheetCompiler().compile(
            project_id=ctx.blueprint.project.studio_project_id,
            format_dna=format_dna,
            shots=shots,
            source_artifacts=source_artifacts,
            production_constraints={
                "planning_mode": handoff.planning_mode.value,
                "selected_tool_ids": list(handoff.selected_tool_ids),
                "scene_global_lane": scene_conference.global_lane.value,
                "visual_primary_models": [
                    item.primary_model_id
                    for item in visual_report.decisions
                    if item.primary_model_id
                ],
                "diagnostic_only": diagnostic_override,
            },
        )

        candidate_by_id = {
            item.model_id: item
            for item in visual_candidates
        }
        estimated_paid_usd = 0.0
        all_local = True
        for decision in visual_report.decisions:
            if not decision.primary_model_id:
                continue
            candidate = candidate_by_id.get(
                decision.primary_model_id
            )
            if candidate is None:
                continue
            all_local = all_local and candidate.local
            if candidate.estimated_cost_per_second_usd is not None:
                estimated_paid_usd += (
                    candidate.estimated_cost_per_second_usd
                    * durations_by_scene.get(
                        str(decision.scene_id),
                        0.0,
                    )
                )
        spend_decision = SpendGate.evaluate(
            SpendGateRequest(
                project_id=ctx.blueprint.project.studio_project_id,
                all_local=all_local,
                estimated_paid_usd=round(
                    estimated_paid_usd,
                    6,
                ),
                pilot_count=self.config.pilot_count,
            ),
            SpendGatePolicy(
                local_only=self.config.spend_local_only,
                max_paid_usd=self.config.spend_max_paid_usd,
                max_pilot_count=self.config.spend_max_pilot_count,
            ),
        )
        human_spend_gate = HumanApprovalGate(
            gate_id="HUMAN_SPEND_APPROVAL",
            project_id=ctx.blueprint.project.studio_project_id,
            purpose=(
                "approve production sheet and resource spend "
                "before production execution"
            ),
            required=self.config.require_human_spend_approval,
            state=(
                HumanApprovalState.PENDING
                if self.config.require_human_spend_approval
                else HumanApprovalState.AUTO_APPROVED
            ),
            approver=(
                None
                if self.config.require_human_spend_approval
                else "AUTONOMOUS_POLICY"
            ),
            evidence_refs=[
                "production_sheet",
                "resource_plan",
                "visual_model_conference",
            ],
        )
        self._write(ctx, "production_sheet", production_sheet)
        self._write(
            ctx,
            "production_sheet_lock",
            {
                "sheet_hash": production_sheet.sheet_hash,
                "format_hash": production_sheet.format_hash,
                "state": production_sheet.state.value,
            },
        )
        self._write(ctx, "spend_gate", spend_decision)
        self._write(ctx, "human_spend_gate", human_spend_gate)

        if not spend_decision.approved:
            return self._finding(
                "SPEND_GATE_BLOCKED",
                QCLayer.TECHNICAL,
                ";".join(spend_decision.reasons),
            )
        if not human_spend_gate.executable:
            return self._finding(
                "HUMAN_SPEND_APPROVAL_REQUIRED",
                QCLayer.TECHNICAL,
                "production is waiting for explicit spend approval",
            )

        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://technical_direction",
        )

    @staticmethod
    def _visual_backend_batches(
        handoff: ProductionHandoff,
        shots: list[Any],
    ) -> tuple[list[dict[str, Any]], list[str]]:
        render_kinds = {
            CapabilityKind.OFFLINE_3D,
            CapabilityKind.REALTIME_3D,
            CapabilityKind.GAME_RUNTIME,
            CapabilityKind.AI_VIDEO,
            CapabilityKind.SCREEN_CAPTURE,
            CapabilityKind.FOOTAGE,
            CapabilityKind.MOTION_GRAPHICS,
        }
        by_id = {str(shot.shot_id): shot for shot in shots}
        batches: list[dict[str, Any]] = []
        unresolved: list[str] = []
        routed: set[str] = set()

        for scene in handoff.scene_plans:
            selected = scene.render_assignment
            if not (
                selected is not None
                and selected.capability_kind in render_kinds
                and selected.execution_ready
                and selected.selected_tool_id
            ):
                candidates = [
                    item
                    for item in scene.assignments
                    if (
                        item.capability_kind in render_kinds
                        and item.execution_ready
                        and item.selected_tool_id
                    )
                ]
                selected = candidates[0] if candidates else None

            batch_shots: list[Any] = []
            for shot_id in scene.shot_ids:
                shot = by_id.get(str(shot_id))
                if shot is None:
                    unresolved.append(f"UNKNOWN_SHOT:{shot_id}")
                    continue
                if selected is None:
                    unresolved.append(
                        f"NO_RENDER_BACKEND:{scene.scene_id}:{shot_id}"
                    )
                    continue
                batch_shots.append(shot)
                routed.add(str(shot_id))

            if selected is not None and batch_shots:
                batches.append(
                    {
                        "scene_id": scene.scene_id,
                        "tool_id": selected.selected_tool_id,
                        "capability_kind": selected.capability_kind,
                        "shots": batch_shots,
                        "scene_lane": scene.scene_conference_lane,
                        "policy": dict(scene.scene_conference_policy),
                        "metrics": dict(scene.scene_conference_metrics),
                        "production_objective": scene.scene_production_objective,
                        "visual_model_id": scene.visual_model_id,
                        "visual_model_fallback_ids": list(
                            scene.visual_model_fallback_ids
                        ),
                        "visual_model_blockers": list(
                            scene.visual_model_blockers
                        ),
                        "required_capability_kind": (
                            scene.required_capability_kind.value
                            if scene.required_capability_kind is not None
                            else None
                        ),
                        "preferred_capability_kinds": [
                            item.value
                            for item in scene.preferred_capability_kinds
                        ],
                        "optimization_bias": dict(scene.optimization_bias),
                        "backend_switch_allowed": (
                            scene.backend_switch_allowed
                        ),
                    }
                )

        for shot in shots:
            if str(shot.shot_id) not in routed:
                unresolved.append(f"UNROUTED_SHOT:{shot.shot_id}")
        return batches, list(dict.fromkeys(unresolved))

    @staticmethod
    def _visual_backend_groups(
        handoff: ProductionHandoff,
        shots: list[Any],
    ) -> tuple[dict[str, list[Any]], list[str]]:
        render_kinds = {
            CapabilityKind.OFFLINE_3D,
            CapabilityKind.REALTIME_3D,
            CapabilityKind.GAME_RUNTIME,
            CapabilityKind.AI_VIDEO,
            CapabilityKind.SCREEN_CAPTURE,
            CapabilityKind.FOOTAGE,
            CapabilityKind.MOTION_GRAPHICS,
        }
        by_id = {str(shot.shot_id): shot for shot in shots}
        groups: dict[str, list[Any]] = {}
        unresolved: list[str] = []
        routed: set[str] = set()

        for scene in handoff.scene_plans:
            selected = scene.render_assignment
            if not (
                selected is not None
                and selected.capability_kind in render_kinds
                and selected.execution_ready
                and selected.selected_tool_id
            ):
                candidates = [
                    item
                    for item in scene.assignments
                    if (
                        item.capability_kind in render_kinds
                        and item.execution_ready
                        and item.selected_tool_id
                    )
                ]
                selected = candidates[0] if candidates else None
            for shot_id in scene.shot_ids:
                shot = by_id.get(str(shot_id))
                if shot is None:
                    unresolved.append(f"UNKNOWN_SHOT:{shot_id}")
                    continue
                if selected is None:
                    unresolved.append(
                        f"NO_RENDER_BACKEND:{scene.scene_id}:{shot_id}"
                    )
                    continue
                groups.setdefault(selected.selected_tool_id, []).append(shot)
                routed.add(str(shot_id))

        for shot in shots:
            if str(shot.shot_id) not in routed:
                unresolved.append(f"UNROUTED_SHOT:{shot.shot_id}")
        return groups, list(dict.fromkeys(unresolved))

    @staticmethod
    def _merge_dailies(
        shots: list[Any],
        reports: list[DailiesReport],
    ) -> DailiesReport:
        by_shot = {
            item.shot_id: item
            for report in reports
            for item in report.shots
        }
        ordered = [
            by_shot[str(shot.shot_id)]
            for shot in shots
            if str(shot.shot_id) in by_shot
        ]
        missing = [
            str(shot.shot_id)
            for shot in shots
            if str(shot.shot_id) not in by_shot
        ]
        findings = [
            finding
            for report in reports
            for finding in report.findings
        ]
        findings.extend(
            f"NO_DAILIES:{shot_id}"
            for shot_id in missing
        )
        failed = [
            item.shot_id
            for item in ordered
            if not item.passed
        ]
        return DailiesReport(
            passed=not missing and not failed,
            shots=ordered,
            findings=list(dict.fromkeys(findings)),
        )

    def _approved_comfy_video_workflow(
        self,
        preferred_model_id: str | None = None,
    ) -> tuple[str | None, str]:
        if self.config.video_workflow_id:
            workflows = getattr(self.runtime, "workflows", None)
            if workflows is not None and preferred_model_id:
                try:
                    configured = workflows.get(
                        self.config.video_workflow_id,
                        self.config.video_workflow_version,
                    )
                except KeyError:
                    return None, self.config.video_workflow_version
                if configured.model_id != preferred_model_id:
                    return None, self.config.video_workflow_version
            return (
                self.config.video_workflow_id,
                self.config.video_workflow_version,
            )
        workflows = getattr(self.runtime, "workflows", None)
        models = getattr(self.runtime, "models", None)
        if workflows is None or models is None:
            return None, self.config.video_workflow_version
        for manifest in workflows.list():
            if (
                manifest.executor_id != "local.comfyui"
                or manifest.media_type.lower() != "video"
                or not manifest.local_only
                or not manifest.model_revision
                or (
                    preferred_model_id is not None
                    and manifest.model_id != preferred_model_id
                )
            ):
                continue
            try:
                models.require_approved(
                    manifest.model_id,
                    manifest.model_revision,
                )
            except Exception:
                continue
            return manifest.workflow_id, manifest.version
        return None, self.config.video_workflow_version

    def _record_production_experience(
        self,
        *,
        project_id: str,
        batch: dict[str, Any],
        budget: dict[str, Any],
        dailies: DailiesReport,
    ) -> dict[str, Any]:
        store = getattr(
            self.studio,
            "production_memory",
            None,
        )
        if store is None:
            return {"recorded": False, "reason": "STORE_UNAVAILABLE"}
        try:
            experience = store.record_scene(
                project_id=project_id,
                batch=batch,
                budget=budget,
                dailies=dailies,
            )
        except Exception as exc:
            return {
                "recorded": False,
                "error": f"{type(exc).__name__}:{exc}",
            }
        if experience is None:
            return {
                "recorded": False,
                "reason": "NON_PRODUCTION_OR_DIAGNOSTIC_BACKEND",
            }
        return {
            "recorded": True,
            "experience_id": experience.experience_id,
        }

    def _scene_batch_budget(
        self,
        batch: dict[str, Any],
    ) -> dict[str, Any]:
        policy = dict(batch.get("policy") or {})
        scale = max(
            0.5,
            min(
                1.0,
                float(policy.get("render_scale", 1.0) or 1.0),
            ),
        )
        width = max(
            64,
            int(round(self.config.render_width * scale / 2.0)) * 2,
        )
        height = max(
            64,
            int(round(self.config.render_height * scale / 2.0)) * 2,
        )
        qc_target = max(
            self.config.min_visual_score,
            float(
                policy.get(
                    "qc_target",
                    self.config.min_visual_score,
                )
                or self.config.min_visual_score
            ),
        )
        repair_budget = max(
            0,
            min(
                self.config.max_repair_rounds,
                int(
                    policy.get(
                        "repair_budget",
                        self.config.max_repair_rounds,
                    )
                    or 0
                ),
            ),
        )
        multiplier = float(
            policy.get("candidate_multiplier", 1.0) or 1.0
        )
        pilot_count = max(
            1,
            min(
                6,
                int(round(self.config.pilot_count * multiplier)),
            ),
        )
        return {
            "scene_id": batch.get("scene_id"),
            "scene_lane": batch.get("scene_lane"),
            "render_scale": round(scale, 4),
            "render_width": width,
            "render_height": height,
            "qc_target": round(qc_target, 4),
            "repair_budget": repair_budget,
            "pilot_count": pilot_count,
            "candidate_multiplier": round(multiplier, 4),
        }

    def production(self, ctx: StageExecutionContext) -> StageHandlerResult:
        if ctx.blueprint.channel_episode_strategy is not None:
            editorial = dict(self._payload(ctx, "series_editorial_plan"))
            pinned = ctx.blueprint.channel_episode_strategy
            if (
                editorial.get("channel_bible_sha256") != pinned.source_sha256
                or editorial.get("episode_id") != pinned.episode_id
            ):
                return self._finding(
                    "CHANNEL_EDITORIAL_HANDOFF_MISMATCH",
                    QCLayer.STORY_LOGIC,
                    "The episode contract changed between channel planning and production",
                )
            from .channel_franchise_v206 import (
                verify_original_cast_rig_readiness,
                verify_fresh_episode_cast_readiness,
            )
            original_cast = (
                verify_original_cast_rig_readiness(self.studio.root, pinned)
                if ctx.blueprint.project.reuse_series_characters
                else verify_fresh_episode_cast_readiness(
                    self.studio.root,
                    ctx.blueprint.project.studio_project_id,
                    pinned.channel_brand_id,
                )
            )
            if not original_cast["ready"]:
                return self._finding(
                    "CHANNEL_ORIGINAL_CHARACTER_FACTORY_NOT_QUALIFIED",
                    QCLayer.TECHNICAL,
                    "; ".join(original_cast["blockers"]),
                )
        # The real company cannot cross the expensive production boundary
        # on a research-only or incomplete niche portfolio greenlight.
        if ctx.blueprint.strict_stage_receipts:
            greenlight = ctx.blueprint.portfolio_greenlight
            if greenlight is not None and not greenlight.approved_for_production:
                return self._finding(
                    "NICHE_PRODUCTION_GREENLIGHT_REQUIRED",
                    QCLayer.TECHNICAL,
                    "Independent niche research, licensing and production readiness are not approved.",
                )
        shots = self._model(ctx, "shot_book", ShotSpecBatch).shots
        root = self._root(ctx)
        runtime_recipe = ProductionRecipe.model_validate(
            self._payload(ctx, "production_recipe")
        )
        handoff = ProductionHandoff.model_validate(
            self._payload(ctx, "production_handoff")
        )
        production_sheet = EpisodeProductionSheet.model_validate(
            self._payload(ctx, "production_sheet")
        )
        sheet_ok, sheet_findings = production_sheet.verify_lock()
        current_sources = {
            name: self._payload(ctx, name)
            for name in production_sheet.source_artifact_hashes
        }
        sources_ok, source_findings = (
            ProductionSheetCompiler().verify_sources(
                production_sheet,
                current_sources,
            )
        )
        format_dna = self._model(ctx, "format_dna", FormatDNA)
        lock_payload = dict(
            self._payload(ctx, "production_sheet_lock")
        )
        if (
            not sheet_ok
            or not sources_ok
            or format_dna.content_hash != production_sheet.format_hash
            or lock_payload.get("sheet_hash")
            != production_sheet.sheet_hash
            or lock_payload.get("format_hash")
            != production_sheet.format_hash
        ):
            return self._finding(
                "PRODUCTION_SHEET_LOCK_INVALID",
                QCLayer.TECHNICAL,
                ";".join(
                    [
                        *sheet_findings,
                        *source_findings,
                    ]
                    or ["PRODUCTION_SHEET_LOCK_MISMATCH"]
                ),
            )
        spend_gate = dict(self._payload(ctx, "spend_gate"))
        if not spend_gate.get("approved"):
            return self._finding(
                "SPEND_GATE_BLOCKED",
                QCLayer.TECHNICAL,
                ";".join(spend_gate.get("reasons") or []),
            )
        human_spend_gate = HumanApprovalGate.model_validate(
            self._payload(ctx, "human_spend_gate")
        )
        if not human_spend_gate.executable:
            return self._finding(
                "HUMAN_SPEND_APPROVAL_REQUIRED",
                QCLayer.TECHNICAL,
                "production is waiting for explicit spend approval",
            )
        if not handoff.executable or runtime_recipe.blocked:
            return self._finding(
                "PRODUCTION_HANDOFF_NOT_EXECUTABLE",
                QCLayer.TECHNICAL,
                ";".join(
                    handoff.blockers
                    or runtime_recipe.blockers
                    or ["runtime planning did not approve a production route"]
                ),
            )
        product = ctx.blueprint.studio_plan.product
        batches, unresolved = self._visual_backend_batches(
            handoff,
            shots,
        )
        diagnostic_allowed = (
            self.config.production_mode == "slate"
            and self.config.allow_diagnostic_slate
        )
        if unresolved and not diagnostic_allowed:
            return self._finding(
                "SHOT_BACKEND_ROUTING_FAILED",
                QCLayer.TECHNICAL,
                ";".join(unresolved),
            )
        if unresolved and diagnostic_allowed:
            routed_ids = {
                str(shot.shot_id)
                for batch in batches
                for shot in batch["shots"]
            }
            diagnostic_shots = [
                shot
                for shot in shots
                if str(shot.shot_id) not in routed_ids
            ]
            if diagnostic_shots:
                batches.append(
                    {
                        "scene_id": "DIAGNOSTIC_UNROUTED",
                        "tool_id": "diagnostic_slate",
                        "capability_kind": None,
                        "shots": diagnostic_shots,
                        "scene_lane": "DIAGNOSTIC",
                        "policy": {},
                        "backend_switch_allowed": False,
                    }
                )

        reports: list[DailiesReport] = []
        backend_routes: list[dict[str, Any]] = []
        global_conference = self._model(
            ctx,
            "production_conference",
            ProductionConferenceDecision,
        )
        adaptive_supervisor = AdaptiveProductionSupervisor(
            project_id=ctx.blueprint.project.studio_project_id,
            global_decision=global_conference,
        )
        style = detect_block_style(
            ctx.blueprint.project.prompt,
            str(product.constraints.get("domain", "")),
        )
        long_slide_vertical = (
            str(product.constraints.get("vertical", ""))
            == "animal_long_slide"
        )

        if style is None and diagnostic_allowed and not long_slide_vertical:
            for batch in batches:
                if batch["tool_id"] == "blender":
                    batch["tool_id"] = "diagnostic_slate"
                    batch["scene_lane"] = (
                        batch.get("scene_lane") or "DIAGNOSTIC"
                    )

        if not batches and diagnostic_allowed:
            batches.append(
                {
                    "scene_id": "DIAGNOSTIC_ALL",
                    "tool_id": "diagnostic_slate",
                    "capability_kind": None,
                    "shots": list(shots),
                    "scene_lane": "DIAGNOSTIC",
                    "policy": {},
                    "backend_switch_allowed": False,
                }
            )

        for batch_index, batch in enumerate(batches):
            tool_id = str(batch["tool_id"])
            grouped_shots = list(batch["shots"])
            budget = self._scene_batch_budget(batch)
            render_width = int(budget["render_width"])
            render_height = int(budget["render_height"])
            conference_qc = float(budget["qc_target"])
            conference_repairs = int(budget["repair_budget"])
            conference_pilot_count = int(budget["pilot_count"])
            if tool_id == "blender":
                if long_slide_vertical and style is None:
                    if self.config.offline_3d_backend not in {
                        "auto",
                        "blender_long_slide",
                    }:
                        return self._finding(
                            "LONG_SLIDE_BLENDER_BACKEND_DISABLED",
                            QCLayer.TECHNICAL,
                            (
                                "Animal Long Slide requires offline_3d_backend "
                                "auto or blender_long_slide."
                            ),
                        )

                    knowledge = self._tool_knowledge(
                        ctx,
                        tool_id="blender",
                        operations=[
                            "scene assembly",
                            "rigging",
                            "animation",
                            "camera",
                            "lighting",
                            "render",
                            "headless batch",
                        ],
                        task=(
                            "assemble and render procedural Animal Long Slide "
                            "modules with deterministic Blender automation"
                        ),
                        artifact_type="production_long_slide_knowledge",
                    )
                    if knowledge.blocked:
                        return self._finding(
                            "TOOL_KNOWLEDGE_GAP",
                            QCLayer.TECHNICAL,
                            "blender_long_slide:"
                            + ",".join(knowledge.missing_operations),
                        )

                    tool = self.studio.tool_doctor.inspect("blender")
                    if not tool.installed or not tool.executable_path:
                        return self._finding(
                            "BLENDER_NOT_AVAILABLE",
                            QCLayer.TECHNICAL,
                            (
                                "Animal Long Slide was routed to Blender but "
                                "the Blender executable is unavailable."
                            ),
                        )

                    long_slide_registry = LongSlideAssetRegistry.load(
                        self.runtime.root
                    )
                    long_slide_motions = MotionCompatibilityGraph.load(
                        self.runtime.root
                    )
                    available_animals = [
                        animal_id
                        for animal_id in long_slide_registry.animal_ids(
                            preview=self.config.blender_preview
                        )
                        if long_slide_motions.resolve_sequence(
                            animal_id,
                            ["idle", "run"],
                            render_preview=self.config.blender_preview,
                        ).executable
                    ]
                    if len(available_animals) < 2:
                        mode = (
                            "preview"
                            if self.config.blender_preview
                            else "production"
                        )
                        return self._finding(
                            "LONG_SLIDE_NO_EXECUTABLE_ANIMALS",
                            QCLayer.TECHNICAL,
                            (
                                f"Animal Long Slide {mode} requires at least "
                                "two qualified animals with locomotion."
                            ),
                        )

                    average_shot_duration = sum(
                        float(shot.duration_seconds)
                        for shot in grouped_shots
                    ) / max(1, len(grouped_shots))
                    source_module_duration = max(
                        8.0,
                        min(30.0, average_shot_duration),
                    )
                    source_target_duration = (
                        source_module_duration * len(grouped_shots)
                    )
                    long_slide_episode = LongSlideCompanyAdapter().plan_episode(
                        ctx.blueprint.project,
                        episode_id=(
                            f"EP_{ctx.blueprint.project.studio_project_id[-8:]}"
                            f"_LS{len(backend_routes) + 1:02d}"
                        ),
                        seed=batch_index + 1,
                        animals=available_animals,
                        target_duration_seconds=source_target_duration,
                        module_count=len(grouped_shots),
                    )
                    long_slide_readiness = LongSlideExecutionPlanner(
                        long_slide_registry,
                        long_slide_motions,
                    ).plan(
                        long_slide_episode,
                        output_dir=root / "renders" / "animal_long_slide",
                        width=render_width,
                        height=render_height,
                        fps=max(12, round(self.config.fps)),
                        render_preview=self.config.blender_preview,
                    )
                    if not long_slide_readiness.executable:
                        return self._finding(
                            "LONG_SLIDE_ASSET_LIBRARY_UNQUALIFIED",
                            QCLayer.TECHNICAL,
                            (
                                "Animal Long Slide is recognized and routed to "
                                "Blender, but required assets/motions are not "
                                "qualified for the requested mode: "
                                + ";".join(long_slide_readiness.blockers[:24])
                            ),
                        )

                    producer = LongSlideProducer(
                        self.runtime.root,
                        blender_executable=tool.executable_path,
                    )
                    group_dailies = producer.produce(
                        long_slide_readiness,
                        company_shot_ids=[
                            str(shot.shot_id)
                            for shot in grouped_shots
                        ],
                        timeout_seconds=self.config.turbo_timeout_seconds,
                    )
                    reports.append(group_dailies)
                    memory_record = self._record_production_experience(
                        project_id=(
                            ctx.blueprint.project.studio_project_id
                        ),
                        batch=batch,
                        budget=budget,
                        dailies=group_dailies,
                    )
                    adaptive_changes = (
                        adaptive_supervisor.observe_and_rebudget(
                            batch=batch,
                            budget=budget,
                            dailies=group_dailies,
                            remaining_batches=batches[
                                batch_index + 1 :
                            ],
                        )
                    )
                    backend_routes.append(
                        {
                            "tool_id": "blender",
                            "scene_id": batch.get("scene_id"),
                            "scene_lane": batch.get("scene_lane"),
                            "production_objective": (
                                batch.get("production_objective")
                            ),
                            "execution_budget": dict(budget),
                            "backend_switch_allowed": bool(
                                batch.get("backend_switch_allowed", False)
                            ),
                            "shot_ids": [
                                str(shot.shot_id)
                                for shot in grouped_shots
                            ],
                            "backend": (
                                "blender_long_slide_preview"
                                if self.config.blender_preview
                                else "blender_long_slide"
                            ),
                            "episode_id": long_slide_episode.episode_id,
                            "animal_pool": available_animals,
                            "originality_signature": (
                                long_slide_episode.originality_signature
                            ),
                            "knowledge_chunk_ids": knowledge.chunk_ids,
                            "adaptations_triggered": [
                                item.model_dump(mode="json")
                                for item in adaptive_changes
                            ],
                            "production_memory_record": memory_record,
                        }
                    )
                    continue
                if style is None:
                    return self._finding(
                        "BLENDER_GENERIC_3D_BINDING_UNAVAILABLE",
                        QCLayer.TECHNICAL,
                        (
                            "Blender was selected for OFFLINE_3D, but the "
                            "current production binder is validated only "
                            "for Minecraft/Roblox block animation. "
                            "Generic cinematic Blender execution remains "
                            "fail-closed until its binder is implemented."
                        ),
                    )
                if self.config.offline_3d_backend not in {
                    "auto",
                    "blender_block",
                }:
                    return self._finding(
                        "BLENDER_BACKEND_DISABLED",
                        QCLayer.TECHNICAL,
                        (
                            "planning selected Blender but the configured "
                            "offline_3d_backend does not permit it"
                        ),
                    )
                knowledge = self._tool_knowledge(
                    ctx,
                    tool_id="blender",
                    operations=[
                        "scene assembly",
                        "rigging",
                        "animation",
                        "camera",
                        "lighting",
                        "render",
                        "headless batch",
                    ],
                    task=(
                        "assemble and render the routed block-animation "
                        "shots with deterministic Blender automation"
                    ),
                    artifact_type="production_tool_knowledge",
                )
                if knowledge.blocked:
                    return self._finding(
                        "TOOL_KNOWLEDGE_GAP",
                        QCLayer.TECHNICAL,
                        "blender:" + ",".join(
                            knowledge.missing_operations
                        ),
                    )
                tool = self.studio.tool_doctor.inspect("blender")
                if not tool.installed or not tool.executable_path:
                    return self._finding(
                        "BLENDER_NOT_AVAILABLE",
                        QCLayer.TECHNICAL,
                        (
                            "planning selected Blender but its executable "
                            "is not available"
                        ),
                    )
                script = self._model(ctx, "script", ScriptSpec)
                try:
                    craft_intent_graph = self._model(
                        ctx,
                        "creative_intent_graph",
                        CreativeIntentGraph,
                    )
                except KeyError:
                    craft_intent_graph = None
                try:
                    craft_performance = self._model(
                        ctx,
                        "performance_direction",
                        PerformanceDirectionPlan,
                    )
                except KeyError:
                    craft_performance = None
                try:
                    craft_lighting = self._model(
                        ctx,
                        "lighting_color_intent",
                        LightingColorIntentPlan,
                    )
                except KeyError:
                    craft_lighting = None
                blocked_tokens = [
                    token
                    for token in ("BigSchool",)
                    if token.lower()
                    in ctx.blueprint.project.prompt.lower()
                ]
                episode = CompanyToBlockAdapter().adapt_episode(
                    project_id=ctx.blueprint.project.studio_project_id,
                    episode_id=(
                        f"EP_{ctx.blueprint.project.studio_project_id[-8:]}"
                        f"_B{len(backend_routes) + 1:02d}"
                    ),
                    title=script.title,
                    shots=grouped_shots,
                    style=style,
                    fps=max(1, round(self.config.fps)),
                    width=render_width,
                    height=render_height,
                    quality_profile=self.config.block_quality_profile,
                    blocked_reference_tokens=blocked_tokens,
                    creative_intent_graph=craft_intent_graph,
                    performance_direction=craft_performance,
                    lighting_color_intent=craft_lighting,
                )
                producer = BlockAnimationProducer(
                    self.runtime.root,
                    blender_executable=tool.executable_path,
                    ctx=self.runtime,
                )
                try:
                    if self.config.turbo_dispatch:
                        group_dailies = producer.produce_turbo(
                            episode,
                            project_root=root,
                            timeout_seconds=(
                                self.config.turbo_timeout_seconds
                            ),
                        )
                    else:
                        group_dailies = producer.produce(
                            episode,
                            project_root=root,
                            render_preview=self.config.blender_preview,
                        )
                finally:
                    producer.close()
                reports.append(group_dailies)
                memory_record = self._record_production_experience(
                    project_id=(
                        ctx.blueprint.project.studio_project_id
                    ),
                    batch=batch,
                    budget=budget,
                    dailies=group_dailies,
                )
                adaptive_changes = (
                    adaptive_supervisor.observe_and_rebudget(
                        batch=batch,
                        budget=budget,
                        dailies=group_dailies,
                        remaining_batches=batches[
                            batch_index + 1 :
                        ],
                    )
                )
                backend_routes.append(
                    {
                        "tool_id": "blender",
                        "scene_id": batch.get("scene_id"),
                        "scene_lane": batch.get("scene_lane"),
                        "production_objective": batch.get("production_objective"),
                        "execution_budget": dict(budget),
                        "backend_switch_allowed": bool(
                            batch.get("backend_switch_allowed", False)
                        ),
                        "shot_ids": [
                            str(shot.shot_id)
                            for shot in grouped_shots
                        ],
                        "backend": (
                            "turbo_persistent_blender_block"
                            if self.config.turbo_dispatch
                            else "persistent_blender_block"
                        ),
                        "style": style.value,
                        "quality_profile": (
                            self.config.block_quality_profile
                        ),
                        "knowledge_chunk_ids": knowledge.chunk_ids,
                        "adaptations_triggered": [
                            item.model_dump(mode="json")
                            for item in adaptive_changes
                        ],
                        "production_memory_record": memory_record,
                    }
                )
                continue

            if tool_id == "comfyui":
                knowledge = self._tool_knowledge(
                    ctx,
                    tool_id="comfyui",
                    operations=[
                        "workflow load",
                        "node validation",
                        "prompt queue",
                        "seed control",
                        "output collection",
                        "provenance",
                    ],
                    task=(
                        "render the routed generative video shots using "
                        "an approved local ComfyUI video workflow"
                    ),
                    artifact_type="production_comfyui_knowledge",
                )
                if knowledge.blocked:
                    return self._finding(
                        "TOOL_KNOWLEDGE_GAP",
                        QCLayer.TECHNICAL,
                        "comfyui:" + ",".join(
                            knowledge.missing_operations
                        ),
                    )
                preferred_model_id = batch.get(
                    "visual_model_id"
                )
                workflow_id, workflow_version = (
                    self._approved_comfy_video_workflow(
                        preferred_model_id=preferred_model_id,
                    )
                )
                if not workflow_id:
                    return self._finding(
                        "COMFYUI_VIDEO_WORKFLOW_UNAVAILABLE",
                        QCLayer.TECHNICAL,
                        (
                            "ComfyUI was selected for video production, "
                            "but no approved local video workflow/model "
                            "is registered"
                        ),
                    )
                try:
                    bible = self._model(
                        ctx,
                        "asset_bible_built",
                        AssetBibleSpec,
                    )
                except KeyError:
                    bible = self._model(
                        ctx,
                        "asset_bible",
                        AssetBibleSpec,
                    )
                keyframes = dict(self._payload(ctx, "keyframes"))
                factory = VideoFactory(
                    self.runtime,
                    visual_qc=None,
                    min_visual_score=conference_qc,
                    early_accept_score=max(
                        self.config.early_accept_score,
                        conference_qc,
                    ),
                    max_repair_rounds=conference_repairs,
                    turbo_dispatch=self.config.turbo_dispatch,
                    turbo_timeout_seconds=(
                        self.config.turbo_timeout_seconds
                    ),
                )
                result = factory.run(
                    project_root=root,
                    shots=grouped_shots,
                    bible=bible,
                    keyframes=keyframes,
                    mode="comfyui",
                    workflow_id=workflow_id,
                    workflow_version=workflow_version,
                    render_width=render_width,
                    render_height=render_height,
                    pilot_count=min(
                        conference_pilot_count,
                        len(grouped_shots),
                    ),
                )
                reports.append(result.dailies)
                memory_record = self._record_production_experience(
                    project_id=(
                        ctx.blueprint.project.studio_project_id
                    ),
                    batch=batch,
                    budget=budget,
                    dailies=result.dailies,
                )
                adaptive_changes = (
                    adaptive_supervisor.observe_and_rebudget(
                        batch=batch,
                        budget=budget,
                        dailies=result.dailies,
                        remaining_batches=batches[
                            batch_index + 1 :
                        ],
                    )
                )
                backend_routes.append(
                    {
                        "tool_id": "comfyui",
                        "scene_id": batch.get("scene_id"),
                        "scene_lane": batch.get("scene_lane"),
                        "production_objective": batch.get("production_objective"),
                        "execution_budget": dict(budget),
                        "backend_switch_allowed": bool(
                            batch.get("backend_switch_allowed", False)
                        ),
                        "shot_ids": [
                            str(shot.shot_id)
                            for shot in grouped_shots
                        ],
                        "backend": "video_factory",
                        "workflow_id": workflow_id,
                        "workflow_version": workflow_version,
                        "knowledge_chunk_ids": knowledge.chunk_ids,
                        "adaptations_triggered": [
                            item.model_dump(mode="json")
                            for item in adaptive_changes
                        ],
                        "production_memory_record": memory_record,
                    }
                )
                continue

            if tool_id == "diagnostic_slate":
                if not diagnostic_allowed:
                    return self._finding(
                        "DIAGNOSTIC_SLATE_DISABLED",
                        QCLayer.TECHNICAL,
                        "diagnostic slate routing is not permitted",
                    )
                try:
                    bible = self._model(
                        ctx,
                        "asset_bible_built",
                        AssetBibleSpec,
                    )
                except KeyError:
                    bible = self._model(
                        ctx,
                        "asset_bible",
                        AssetBibleSpec,
                    )
                keyframes = dict(self._payload(ctx, "keyframes"))
                factory = VideoFactory(
                    self.runtime,
                    visual_qc=None,
                    min_visual_score=conference_qc,
                    early_accept_score=max(
                        self.config.early_accept_score,
                        conference_qc,
                    ),
                    max_repair_rounds=conference_repairs,
                    turbo_dispatch=False,
                    diagnostic_slate=(
                        self.config.production_mode == "slate"
                        and self.config.allow_diagnostic_slate
                    ),
                )
                result = factory.run(
                    project_root=root,
                    shots=grouped_shots,
                    bible=bible,
                    keyframes=keyframes,
                    mode="slate",
                    workflow_id=None,
                    workflow_version="1",
                    render_width=render_width,
                    render_height=render_height,
                    pilot_count=min(
                        conference_pilot_count,
                        len(grouped_shots),
                    ),
                )
                reports.append(result.dailies)
                memory_record = self._record_production_experience(
                    project_id=(
                        ctx.blueprint.project.studio_project_id
                    ),
                    batch=batch,
                    budget=budget,
                    dailies=result.dailies,
                )
                adaptive_changes = (
                    adaptive_supervisor.observe_and_rebudget(
                        batch=batch,
                        budget=budget,
                        dailies=result.dailies,
                        remaining_batches=batches[
                            batch_index + 1 :
                        ],
                    )
                )
                backend_routes.append(
                    {
                        "tool_id": "diagnostic_slate",
                        "scene_id": batch.get("scene_id"),
                        "scene_lane": batch.get("scene_lane"),
                        "production_objective": batch.get("production_objective"),
                        "execution_budget": dict(budget),
                        "backend_switch_allowed": bool(
                            batch.get("backend_switch_allowed", False)
                        ),
                        "shot_ids": [
                            str(shot.shot_id)
                            for shot in grouped_shots
                        ],
                        "backend": "video_factory",
                        "diagnostic": True,
                        "adaptations_triggered": [
                            item.model_dump(mode="json")
                            for item in adaptive_changes
                        ],
                        "production_memory_record": memory_record,
                    }
                )
                continue

            return self._finding(
                "PRODUCTION_BACKEND_NOT_BOUND",
                QCLayer.TECHNICAL,
                (
                    f"planner selected {tool_id} for "
                    f"{len(grouped_shots)} shot(s), but the production "
                    "department has no executable binding for it"
                ),
            )

        dailies = self._merge_dailies(shots, reports)
        backend = {
            "backend": "scene_dispatch",
            "planning_mode": handoff.planning_mode.value,
            "routes": backend_routes,
            "selected_tool_ids": handoff.selected_tool_ids,
            "adaptive_production": {
                "outcome_count": len(
                    adaptive_supervisor.report.outcomes
                ),
                "adaptation_count": (
                    adaptive_supervisor.report.adaptation_count
                ),
            },
            "diagnostic": bool(
                backend_routes
                and all(
                    item.get("diagnostic", False)
                    for item in backend_routes
                )
            ),
        }
        checkpoint = str(root / "renders")

        # Persist execution evidence even when the final dailies gate fails so
        # repair/resume can reason from the work already attempted.
        self._write(ctx, "dailies", dailies)
        self._write(ctx, "production_backend", backend)
        self._write(
            ctx,
            "adaptive_production_report",
            adaptive_supervisor.report,
        )
        if not dailies.passed:
            return self._finding(
                "DAILIES_FAILED",
                QCLayer.TECHNICAL,
                "; ".join(dailies.findings) or "no accepted production take",
            )
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref=checkpoint,
        )

    def editorial(self, ctx: StageExecutionContext) -> StageHandlerResult:
        craft = self._tool_knowledge(
            ctx,
            tool_id="craft.editorial",
            operations=[
                "continuity",
                "cut timing",
                "J/L cut",
                "pacing",
                "reaction",
                "information",
            ],
            task="construct a clear, continuous and well-paced edit",
            artifact_type="editorial_craft_knowledge",
        )
        if craft.blocked:
            return self._finding(
                "CRAFT_KNOWLEDGE_GAP",
                QCLayer.EDITORIAL,
                "editorial:" + ",".join(craft.missing_operations),
            )
        shots = self._model(ctx, "shot_book", ShotSpecBatch).shots
        dailies = DailiesReport.model_validate(self._payload(ctx, "dailies"))
        by_shot = {item.shot_id: item for item in dailies.shots}
        decisions: list[EditDecision] = []
        media_paths: dict[str, str] = {}
        for order, shot in enumerate(shots):
            daily = by_shot.get(shot.shot_id)
            if daily is None or not daily.selected_path:
                return self._finding(
                    "EDITORIAL_SOURCE_MISSING",
                    QCLayer.EDITORIAL,
                    f"no selected take for {shot.shot_id}",
                )
            source_id = f"SRC_{shot.shot_id}"
            media_paths[source_id] = daily.selected_path
            decisions.append(
                EditDecision(
                    decision_id=f"EDIT_{shot.shot_id}",
                    source_id=source_id,
                    segment_id=shot.scene_id,
                    source_in=0,
                    source_out=shot.duration_seconds,
                    timeline_order=order,
                    reason=EditReason.INFORMATION,
                    notes=[shot.edit_intent or "preserve dramatic beat"],
                )
            )
        graph = EditDecisionGraph(
            project_id=ctx.blueprint.project.studio_project_id,
            decisions=decisions,
        )
        timeline = EditorialCompiler().to_timeline(
            graph,
            media_paths,
            fps=self.config.fps,
            width=self.config.render_width,
            height=self.config.render_height,
        )
        knowledge = self._tool_knowledge(
            ctx,
            tool_id="ffmpeg",
            operations=["probe", "concat", "transcode"],
            task="render the backend-neutral timeline into a verified rough cut",
            artifact_type="editorial_tool_knowledge",
        )
        if knowledge.blocked:
            return self._finding(
                "TOOL_KNOWLEDGE_GAP",
                QCLayer.EDITORIAL,
                "ffmpeg:" + ",".join(knowledge.missing_operations),
            )
        root = self._root(ctx)
        rough_path = root / "post" / "rough_cut.mp4"
        rough_path.parent.mkdir(parents=True, exist_ok=True)
        rough = self.editor.render_rough_cut(timeline, rough_path)
        self._write(ctx, "edit_decision_graph", graph)
        self._write(ctx, "timeline", timeline)
        self._write(ctx, "rough_cut", {"path": str(rough)})
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref=str(rough),
        )

    def audio(self, ctx: StageExecutionContext) -> StageHandlerResult:
        craft = self._tool_knowledge(
            ctx,
            tool_id="craft.audio",
            operations=[
                "dialogue priority",
                "ambience",
                "foley",
                "sfx",
                "music",
                "loudness",
                "sync",
            ],
            task="plan and verify the sound design and mix for the locked picture",
            artifact_type="audio_craft_knowledge",
        )
        if craft.blocked:
            return self._finding(
                "CRAFT_KNOWLEDGE_GAP",
                QCLayer.AUDIO,
                "audio:" + ",".join(craft.missing_operations),
            )
        rough = dict(self._payload(ctx, "rough_cut"))
        path = rough.get("path")
        if not path or not Path(path).is_file():
            return self._finding(
                "AUDIO_PICTURE_SOURCE_MISSING",
                QCLayer.AUDIO,
                "rough cut is unavailable for the audio stage",
            )
        post_requests = [
            self._audio_request(
                job_id="AUDIO_MIX_MASTER",
                objective=AudioObjective.MIX_MASTER,
            )
        ]
        if self.config.audio_enhancement_required:
            post_requests.append(
                self._audio_request(
                    job_id="AUDIO_SPEECH_ENHANCEMENT",
                    objective=AudioObjective.SPEECH_ENHANCEMENT,
                )
            )
        if self.config.audio_source_separation_required:
            post_requests.append(
                self._audio_request(
                    job_id="AUDIO_SOURCE_SEPARATION",
                    objective=AudioObjective.SOURCE_SEPARATION,
                )
            )
        post_report = AudioProductionConference(
            self._audio_candidates()
        ).run(
            ctx.blueprint.project.studio_project_id,
            post_requests,
        )
        self._write(ctx, "audio_post_conference", post_report)
        if post_report.blocked:
            blocked = [
                item for item in post_report.decisions if item.blocked
            ]
            details = []
            for decision in blocked:
                gate_failures = sorted({
                    blocker
                    for assessment in decision.assessments
                    for blocker in assessment.blockers
                })
                details.append(
                    f"{decision.job_id}:{decision.objective.value}:"
                    + ",".join(gate_failures)
                )
            return self._finding(
                "AUDIO_POST_CONFERENCE_BLOCKED",
                QCLayer.AUDIO,
                "; ".join(details),
            )

        try:
            spotting = self._model(
                ctx,
                "sound_spotting",
                SoundSpottingPlan,
            )
            shot_batch = self._model(
                ctx,
                "shot_book",
                ShotSpecBatch,
            )
            plan = AudioIntentCompiler().compile(
                ctx.blueprint.project.studio_project_id,
                spotting,
                shot_batch,
            )
        except KeyError:
            plan = AudioPlan(
                project_id=ctx.blueprint.project.studio_project_id
            )
        try:
            voice_payload = dict(self._payload(ctx, "voice_tracks"))
            rendered_tracks = list(voice_payload.get("tracks", []))
        except KeyError:
            rendered_tracks = []
        selected_post_engines = {
            decision.job_id: decision.primary_engine_id
            for decision in post_report.decisions
        }
        voice_master = {
            "mode": (
                "rendered_dialogue_available"
                if rendered_tracks
                else "no_rendered_dialogue"
            ),
            "track_count": len(rendered_tracks),
            "engines": sorted({
                item.get("engine_id")
                for item in rendered_tracks
                if item.get("engine_id")
            }),
        }
        root = self._root(ctx)
        mastered_path = root / "audio" / "master" / "audio_master.mp4"
        try:
            mastered = self.media.master_audio(
                path,
                mastered_path,
                speech_denoise=self.config.audio_enhancement_required,
            )
        except Exception as exc:
            return self._finding(
                "AUDIO_MASTER_EXECUTION_FAILED",
                QCLayer.AUDIO,
                f"{type(exc).__name__}:{exc}",
            )
        audio_master = {
            "path": str(mastered),
            "mode": "ffmpeg_audio_master",
            "routing_only": False,
            "post_engines": selected_post_engines,
            "target_lufs": -16.0,
            "true_peak_db": -1.5,
            "speech_denoise": self.config.audio_enhancement_required,
        }
        execution_report = {
            "executed": True,
            "source": path,
            "output": str(mastered),
            "mix_master_engine": selected_post_engines.get(
                "AUDIO_MIX_MASTER"
            ),
            "speech_enhancement_engine": selected_post_engines.get(
                "AUDIO_SPEECH_ENHANCEMENT"
            ),
            "source_separation_engine": selected_post_engines.get(
                "AUDIO_SOURCE_SEPARATION"
            ),
            "voice_track_count": len(rendered_tracks),
        }
        self._write(ctx, "voice_master", voice_master)
        self._write(ctx, "sound_plan", plan)
        self._write(ctx, "audio_master", audio_master)
        self._write(ctx, "audio_execution_report", execution_report)
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref=str(mastered),
        )

    def finishing(self, ctx: StageExecutionContext) -> StageHandlerResult:
        audio_master = dict(self._payload(ctx, "audio_master"))
        source = audio_master.get("path")
        if not source or not Path(source).is_file():
            return self._finding(
                "FINISH_SOURCE_MISSING",
                QCLayer.TECHNICAL,
                "audio master source is unavailable",
            )
        knowledge = self._tool_knowledge(
            ctx,
            tool_id="ffmpeg",
            operations=["probe", "transcode", "master", "delivery QC"],
            task="master the locked picture/audio source to the delivery contract",
            artifact_type="finishing_tool_knowledge",
        )
        if knowledge.blocked:
            return self._finding(
                "TOOL_KNOWLEDGE_GAP",
                QCLayer.TECHNICAL,
                "ffmpeg:" + ",".join(knowledge.missing_operations),
            )
        try:
            color_intent = self._model(
                ctx,
                "lighting_color_intent",
                LightingColorIntentPlan,
            )
            color_plan = ColorIntentCompiler().compile(
                ctx.blueprint.project.studio_project_id,
                color_intent,
            )
        except KeyError:
            color_plan = ColorPlan(
                project_id=ctx.blueprint.project.studio_project_id,
                bible=ColorBible(
                    look_description="technical finishing only"
                ),
                shots=[],
            )

        self._write(ctx, "color_plan", color_plan)

        root = self._root(ctx)
        output = root / "master" / "master_candidate.mp4"
        output.parent.mkdir(parents=True, exist_ok=True)
        master, qc = self.mastering.master(
            source,
            output,
            width=self.config.master_width,
            height=self.config.master_height,
            fps=self.config.fps,
        )
        if not qc.passed:
            return self._finding(
                "MASTERING_QC_FAILED",
                QCLayer.TECHNICAL,
                "; ".join(qc.findings),
            )
        self._write(
            ctx,
            "master_candidate",
            {
                "path": str(master),
                "width": self.config.master_width,
                "height": self.config.master_height,
                "fps": self.config.fps,
            },
        )
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref=str(master),
        )

    def final_qc(self, ctx: StageExecutionContext) -> StageHandlerResult:
        if (
            ctx.blueprint.strict_stage_receipts
            and self.config.production_mode == "slate"
        ):
            return self._finding(
                "DIAGNOSTIC_SLATE_NOT_PUBLISHABLE",
                QCLayer.TECHNICAL,
                "Synthetic slate validates infrastructure, not original cinematic footage.",
            )
        master = dict(self._payload(ctx, "master_candidate"))
        path = master.get("path")
        if not path or not Path(path).is_file():
            return self._finding(
                "FINAL_MASTER_MISSING",
                QCLayer.TECHNICAL,
                "master candidate is unavailable",
            )
        knowledge = self._tool_knowledge(
            ctx,
            tool_id="ffmpeg",
            operations=["probe", "delivery QC"],
            task="verify the final master against technical delivery requirements",
            artifact_type="final_qc_tool_knowledge",
        )
        if knowledge.blocked:
            return self._finding(
                "TOOL_KNOWLEDGE_GAP",
                QCLayer.TECHNICAL,
                "ffmpeg:" + ",".join(knowledge.missing_operations),
            )
        qc = self.mastering.qc.video(
            path, require_audio=ctx.blueprint.strict_stage_receipts
        )
        report = {
            "passed": qc.passed,
            "findings": list(qc.findings),
            "probe": asdict(qc.probe) if qc.probe else None,
        }
        if not qc.passed:
            return self._finding(
                "FINAL_QC_FAILED",
                QCLayer.TECHNICAL,
                "; ".join(qc.findings),
            )
        if ctx.blueprint.strict_stage_receipts:
            # Technical pass alone NEVER approves cinematic artistry, rights,
            # narrative, acting, music or full-film editing. Human signatures
            # must refer to the exact real master hash.
            from .film_release_gate_v209 import review_original_master
            project_dir = (
                ctx.project_root or
                (self.studio.root/"data"/"projects"/
                 ctx.blueprint.project.studio_project_id)
            )
            film_review = review_original_master(
                project_dir, path,
                duration_target=ctx.blueprint.project.duration_seconds,
            )
            self._write(ctx, "independent_film_review", film_review)
            if not film_review["release_permission"]:
                return self._finding(
                    "INDEPENDENT_FILM_ACCEPTANCE_REQUIRED",
                    QCLayer.TECHNICAL,
                    film_review["status"],
                )
        require_final = (
            self.config.require_human_final_approval
            or ctx.blueprint.strict_stage_receipts
        )
        human_final_gate = HumanApprovalGate(
            gate_id="HUMAN_FINAL_APPROVAL",
            project_id=ctx.blueprint.project.studio_project_id,
            purpose="final human watch before packaging/publish",
            required=require_final,
            state=(
                HumanApprovalState.PENDING
                if require_final
                else HumanApprovalState.AUTO_APPROVED
            ),
            approver=(
                None
                if require_final
                else "AUTONOMOUS_POLICY"
            ),
            evidence_refs=["qc_report", "approved_master"],
        )
        self._write(ctx, "qc_report", report)
        self._write(ctx, "repair_requests", [])
        self._write(ctx, "approved_master", {"path": path})
        self._write(ctx, "human_final_gate", human_final_gate)
        if not human_final_gate.executable:
            return self._finding(
                "HUMAN_FINAL_APPROVAL_REQUIRED",
                QCLayer.TECHNICAL,
                "final master is waiting for explicit human approval",
            )
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref=path,
        )

    def packaging(self, ctx: StageExecutionContext) -> StageHandlerResult:
        human_final_gate = HumanApprovalGate.model_validate(
            self._payload(ctx, "human_final_gate")
        )
        if not human_final_gate.executable:
            return self._finding(
                "HUMAN_FINAL_APPROVAL_REQUIRED",
                QCLayer.TECHNICAL,
                "packaging is blocked pending final human approval",
            )
        script = self._model(ctx, "script", ScriptSpec)
        from cinefactory.originality.models import PackagingHypothesis
        packaging = PackagingHypothesis.model_validate(
            self._payload(ctx, "packaging_hypothesis")
        )
        release = self.scaffold.release_package(script, packaging)
        if ctx.blueprint.channel_episode_strategy is not None:
            strategy = ctx.blueprint.channel_episode_strategy
            release = {
                **release.model_dump(mode="json"),
                "original_channel_episode": {
                    "channel_brand_id": strategy.channel_brand_id,
                    "series_id": strategy.series_id,
                    "episode_id": strategy.episode_id,
                    "channel_bible_sha256": strategy.source_sha256,
                    "not_official_minecraft_branding": True,
                    "channel_release_authorized": False,
                },
            }
        self._write(ctx, "release_package", release)
        return StageHandlerResult(
            ok=True,
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://release_package",
        )

    def publishing(self, ctx: StageExecutionContext) -> StageHandlerResult:
        return StageHandlerResult(
            ok=False,
            error="OWNER_OAUTH_AND_PRIVATE_PROVIDER_READBACK_REQUIRED",
            detail="A release package is not proof a video was uploaded.",
        )

    def analytics_learning(self, ctx: StageExecutionContext) -> StageHandlerResult:
        release = self._payload(ctx, "release_package")
        observations = {
            "status": "AWAITING_PLATFORM_METRICS",
            "release_title": release.get("final_title")
            if isinstance(release, dict)
            else None,
        }
        hypotheses = {
            "status": "PENDING_EVIDENCE",
            "rules": [
                "do not promote learning before post-release evidence",
            ],
        }
        candidates = {
            "status": "PENDING",
            "promotable": False,
        }
        self._write(ctx, "observations", observations)
        self._write(ctx, "hypotheses", hypotheses)
        self._write(ctx, "learning_candidates", candidates)
        # Historic diagnostics may complete their placeholder handoff.
        # Professional runs NEVER treat pending metrics as completed learning.
        if not ctx.blueprint.strict_stage_receipts:
            return StageHandlerResult(
                ok=True,
                produced_artifacts=list(ctx.stage.artifacts_out),
                checkpoint_ref="blackboard://analytics_learning",
                detail="LEGACY_DIAGNOSTIC_HANDOFF_ONLY_NOT_PLATFORM_LEARNING",
            )
        return StageHandlerResult(
            ok=False,
            error="AWAITING_VERIFIED_PLATFORM_METRICS",
            detail="Owned-channel Analytics integration and validation are not completed.",
            produced_artifacts=list(ctx.stage.artifacts_out),
            checkpoint_ref="blackboard://analytics_learning",
        )
