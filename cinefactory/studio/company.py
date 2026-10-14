from __future__ import annotations

from pydantic import BaseModel, Field

from .contracts import (
    MediaFormat,
    PlanningInputKind,
    PlanningInputRef,
    StudioProjectSpec,
)
from .control_plane import StudioPlan
from .channel_franchise_v206 import ChannelLibrary, ChannelEpisodeStrategy
from .minecraft_subniche_v207 import (
    Route as MinecraftRoute, Lane as MinecraftLane, classify_minecraft,
    canonical_subniche, CATALOG as MINECRAFT_SUBNICHES,
)
from .intake import PortfolioGreenlight, ProjectIntake
from .packs import PackComposition
from .project_dna import ProjectDNA
from .project_pod import ProjectPod
from .production import ProductionRecipe
from .quality import QualityProfile
from .script_intelligence import (
    ScriptInputCompiler,
    ScriptSourcePack,
)


class CompanyStage(BaseModel):
    stage_id: str
    owner: str
    required: bool = True
    gate: str | None = None
    artifacts_in: list[str] = Field(default_factory=list)
    artifacts_out: list[str] = Field(default_factory=list)


class CompanyBlueprint(BaseModel):
    project: StudioProjectSpec
    studio_plan: StudioPlan
    project_dna: ProjectDNA
    project_pod: ProjectPod
    packs: PackComposition
    production_recipe: ProductionRecipe
    quality_profile: QualityProfile
    script_source_pack: ScriptSourcePack | None = None
    project_intake: ProjectIntake | None = None
    portfolio_greenlight: PortfolioGreenlight | None = None
    stages: list[CompanyStage] = Field(default_factory=list)
    executable: bool = False
    blockers: list[str] = Field(default_factory=list)
    strict_stage_receipts: bool = False
    pilot_only: bool = False
    approved_pilot_work_order_sha256: str | None = None
    channel_episode_strategy: ChannelEpisodeStrategy | None = None
    minecraft_route: MinecraftRoute | None = None
    technology_research_advisory: dict | None = None
    department_technology_advisory: dict | None = None


def stage_blueprint(
    media_format: MediaFormat,
    evidence_required: bool,
    *,
    voice_required: bool | None = None,
    professional_governance: bool = False,
    professional_niche: str | None = None,
    native_media_lane: bool = False,
) -> list[CompanyStage]:
    from .specialist_media_lanes_v205 import is_specialist_lane, build_specialist_stages
    # Explicit narrative-film authoring retains the historical story pipeline;
    # the new native-media lanes apply to non-film, documentary, audio and
    # inferred generic projects without Minecraft/Roblox-style previsualization.
    if (
        professional_governance
        and is_specialist_lane(professional_niche)
        and (native_media_lane or media_format != MediaFormat.NARRATIVE_FILM)
    ):
        return build_specialist_stages(professional_niche)
    stages = [
        CompanyStage(
            stage_id="PROJECT_INTAKE",
            owner="STUDIO_MANAGEMENT",
            artifacts_in=["project_brief"],
            artifacts_out=["project_intake"],
            gate="INTAKE_VALIDATION",
        ),
        CompanyStage(
            stage_id="PORTFOLIO_GREENLIGHT",
            owner="STUDIO_MANAGEMENT",
            artifacts_in=["project_intake"],
            artifacts_out=["portfolio_greenlight"],
            gate="NICHE_PORTFOLIO_GREENLIGHT",
        ),
        CompanyStage(
            stage_id="INTELLIGENCE",
            owner="INTELLIGENCE",
            artifacts_in=[
                "project_brief",
                "references",
                "project_intake",
                "portfolio_greenlight",
            ],
            artifacts_out=[
                "research_pack",
                "research_confidence",
                "research_portfolio",
                "competitor_profiles",
                "niche_playbook",
            ],
            gate="RESEARCH_QUALITY",
        ),
        CompanyStage(
            stage_id="EVIDENCE",
            owner="EVIDENCE",
            required=evidence_required,
            artifacts_in=["research_pack"],
            artifacts_out=["evidence_map"],
            gate="EVIDENCE_INTEGRITY" if evidence_required else None,
        ),
        CompanyStage(
            stage_id="CORPORATE_PREFLIGHT",
            owner="STUDIO_MANAGEMENT",
            artifacts_in=[
                "project_intake",
                "portfolio_greenlight",
                "research_pack",
                "competitor_profiles",
                "niche_playbook",
            ],
            artifacts_out=["corporate_preflight", "seo_discovery_brief"],
            gate="FINANCE_RIGHTS_RISK_DISCOVERY",
        ),
        CompanyStage(
            stage_id="CREATIVE_STRATEGY",
            owner="CREATIVE_STRATEGY",
            artifacts_in=[
                "research_pack",
                "niche_playbook",
                "evidence_map",
                "corporate_preflight",
                "seo_discovery_brief",
            ],
            artifacts_out=[
                "creative_brief",
                "project_dna",
                "format_dna",
                "human_topic_gate",
            ],
            gate="ORIGINALITY_AND_AUDIENCE_PROMISE",
        ),
        CompanyStage(
            stage_id="PLANNING",
            owner="PLANNING",
            artifacts_in=[
                "research_pack",
                "research_confidence",
                "research_portfolio",
                "competitor_profiles",
                "niche_playbook",
                "creative_brief",
                "project_dna",
                "format_dna",
                "human_topic_gate",
            ],
            artifacts_out=[
                "production_strategy",
                "reference_pattern_map",
                "originality_boundaries",
                "script_source_pack",
                "production_conference",
            ],
            gate="PRODUCTION_STRATEGY_LOCK",
        ),
        CompanyStage(
            stage_id="WRITING",
            owner="WRITERS_ROOM",
            artifacts_in=[
                "creative_brief",
                "project_dna",
                "production_strategy",
                "script_source_pack",
                "production_conference",
                "evidence_map",
            ],
            artifacts_out=["script", "beat_graph"],
            gate="SCRIPT_QUALITY",
        ),
        CompanyStage(
            stage_id="LOGIC",
            owner="SCRIPT_LOGIC",
            artifacts_in=["script"],
            artifacts_out=["logic_report", "continuity_contract"],
            gate="LOGIC_AND_CAUSALITY",
        ),
    ]
    if media_format in {
        MediaFormat.NARRATIVE,
        MediaFormat.NARRATIVE_FILM,
        MediaFormat.ANIMATION,
        MediaFormat.GAMEPLAY,
        MediaFormat.COMMERCIAL,
        MediaFormat.MUSIC_VIDEO,
    }:
        # Dialogue-before-animation is a hard dependency only where lip-sync is intrinsic.
        # Other formats may add narration/dialogue later in the AUDIO stage.
        if voice_required is None:
            voice_required = media_format is MediaFormat.ANIMATION
        stages.extend([
            CompanyStage(
                stage_id="DIRECTION",
                owner="DIRECTION",
                artifacts_in=["script", "project_dna", "logic_report"],
                artifacts_out=["director_cut", "blocking_plan", "performance_intent"],
                gate="DIRECTOR_GATE",
            ),
            CompanyStage(
                stage_id="PERFORMANCE",
                owner="PERFORMANCE",
                artifacts_in=["director_cut", "script"],
                artifacts_out=["performance_plan"],
                gate="PERFORMANCE_INTENT",
            ),
            CompanyStage(
                stage_id="PRODUCTION_DESIGN",
                owner="PRODUCTION_DESIGN",
                artifacts_in=["project_dna", "director_cut", "script"],
                artifacts_out=["asset_bible", "world_bible", "design_bible"],
                gate="DESIGN_LOCK",
            ),
            CompanyStage(
                stage_id="CINEMATOGRAPHY",
                owner="CINEMATOGRAPHY",
                artifacts_in=["director_cut", "blocking_plan", "project_dna"],
                artifacts_out=["shot_book", "camera_plan", "lighting_plan"],
                gate="CAMERA_CONTINUITY",
            ),
            CompanyStage(
                stage_id="ASSET_BUILD",
                owner="ASSETS",
                artifacts_in=["asset_bible", "design_bible"],
                artifacts_out=["assets", "asset_manifest", "canonical_references"],
                gate="ASSET_IDENTITY_LOCK",
            ),
            CompanyStage(
                stage_id="VOICE_PREP",
                owner="AUDIO",
                required=voice_required,
                artifacts_in=["script", "director_cut", "performance_plan"],
                artifacts_out=[
                    "voice_tracks",
                    "dialogue_lock",
                    "lipsync_plan",
                    "audio_production_conference",
                ],
                gate="DIALOGUE_LOCK",
            ),
            CompanyStage(
                stage_id="PREVIS",
                owner="DIRECTION",
                artifacts_in=["shot_book", "assets", "performance_plan"],
                artifacts_out=["storyboard", "keyframes", "previs_report"],
                gate="KEYFRAME_APPROVAL",
            ),
        ])
    stages.extend([
        CompanyStage(
            stage_id="TECHNICAL_DIRECTION",
            owner="TECHNICAL_DIRECTION",
            artifacts_in=[
                "project_dna", "format_dna", "production_strategy",
                "production_conference", "director_cut", "shot_book",
                "asset_manifest", "performance_plan", "previs_report",
            ],
            artifacts_out=[
                "production_recipe",
                "resource_plan",
                "routing_decisions",
                "scene_tool_plan",
                "scene_production_conference",
                "visual_model_conference",
                "production_memory_advice",
                "production_handoff",
                "production_sheet",
                "production_sheet_lock",
                "spend_gate",
                "human_spend_gate",
            ],
            gate="CAPABILITY_PREFLIGHT",
        ),
        CompanyStage(
            stage_id="PRODUCTION",
            owner="PRODUCTION",
            artifacts_in=[
                "production_recipe", "production_handoff", "assets", "keyframes",
                "performance_plan", "dialogue_lock", "format_dna",
                "production_sheet", "production_sheet_lock", "spend_gate",
                "human_spend_gate",
            ],
            artifacts_out=[
                "dailies",
                "production_backend",
                "adaptive_production_report",
            ],
            gate="DAILIES_GATE",
        ),
        CompanyStage(
            stage_id="EDITORIAL",
            owner="EDITORIAL",
            artifacts_in=["dailies", "script", "director_cut"],
            artifacts_out=["edit_decision_graph", "timeline"],
            gate="EDITORIAL_GATE",
        ),
        CompanyStage(
            stage_id="AUDIO",
            owner="AUDIO",
            artifacts_in=["timeline", "script", "director_cut"],
            artifacts_out=[
                "voice_master",
                "sound_plan",
                "audio_master",
                "audio_post_conference",
                "audio_execution_report",
            ],
            gate="AUDIO_GATE",
        ),
        CompanyStage(
            stage_id="FINISHING",
            owner="COLOR",
            artifacts_in=["timeline", "audio_master"],
            artifacts_out=["master_candidate"],
            gate="FINISHING_GATE",
        ),
        CompanyStage(
            stage_id="FINAL_QC",
            owner="QC",
            artifacts_in=["master_candidate"],
            artifacts_out=[
                "qc_report",
                "repair_requests",
                "approved_master",
                "human_final_gate",
            ],
            gate="FINAL_WATCHABILITY",
        ),
        CompanyStage(
            stage_id="PACKAGING",
            owner="PACKAGING",
            artifacts_in=[
                "approved_master",
                "project_dna",
                "human_final_gate",
            ],
            artifacts_out=["release_package"],
            gate="PLATFORM_AND_BRAND",
        ),
        CompanyStage(
            stage_id="ANALYTICS_LEARNING",
            owner="ANALYTICS",
            artifacts_in=["release_package", "performance_metrics"],
            artifacts_out=["observations", "hypotheses", "learning_candidates"],
            gate="LEARNING_PROMOTION_POLICY",
        ),
    ])
    if professional_governance:
        # Publishing is a separate owner-authorized, provider-verified event.
        # Packaging alone must never be treated as actual publication.
        analytics = next(x for x in stages if x.stage_id == "ANALYTICS_LEARNING")
        analytics.artifacts_in.append("publication_receipt")
        stage_pos = stages.index(analytics)
        stages.insert(stage_pos, CompanyStage(
            stage_id="PUBLISHING", owner="OPERATIONS",
            artifacts_in=["release_package","approved_master","human_final_gate"],
            artifacts_out=["publication_receipt"],
            gate="OWNER_AUTHORIZED_PRIVATE_FIRST_PUBLICATION",
        ))
        niche_id = (professional_niche or "").strip().lower()
        story_niches = {
            "minecraft",
            "roblox_animation",
            "audio_storytelling_seniors",
        }
        visual_cinematic_niches = {
            "minecraft",
            "roblox_animation",
        }
        use_story_pipeline = niche_id in story_niches
        use_visual_cinematic_pipeline = niche_id in visual_cinematic_niches

        stages.append(
            CompanyStage(
                stage_id="CREATIVE_DEVELOPMENT",
                owner="CREATIVE_STRATEGY",
                artifacts_in=[
                    "corporate_preflight",
                    "seo_discovery_brief",
                    "research_pack",
                    "niche_playbook",
                ],
                artifacts_out=[
                    "creative_development_brief",
                    "audience_promise_contract",
                ],
                gate="CREATIVE_DEVELOPMENT_GREENLIGHT",
            )
        )

        if use_story_pipeline:
            stages.extend([
                CompanyStage(
                    stage_id="STORY_ARCHITECTURE",
                    owner="WRITERS_ROOM",
                    artifacts_in=[
                        "creative_development_brief",
                        "creative_brief",
                        "project_dna",
                        "production_strategy",
                        "script_source_pack",
                    ],
                    artifacts_out=["story", "story_architecture"],
                    gate="STORY_ARCHITECTURE_GATE",
                ),
                CompanyStage(
                    stage_id="SCRIPT_REVIEW",
                    owner="SCRIPT_LOGIC",
                    artifacts_in=[
                        "story",
                        "story_architecture",
                        "script",
                        "beat_graph",
                    ],
                    artifacts_out=["script_review"],
                    gate="INDEPENDENT_SCRIPT_REVIEW",
                ),
                CompanyStage(
                    stage_id="DIRECTOR_TREATMENT",
                    owner="DIRECTION",
                    artifacts_in=[
                        "script",
                        "story_architecture",
                        "script_review",
                        "logic_report",
                        "project_dna",
                    ],
                    artifacts_out=["director_treatment"],
                    gate="DIRECTOR_TREATMENT_GATE",
                ),
            ])

        if use_visual_cinematic_pipeline:
            stages.extend([
                CompanyStage(
                    stage_id="STORYBOARD_EDITORIAL",
                    owner="EDITORIAL",
                    artifacts_in=[
                        "shot_book",
                        "director_cut",
                        "director_treatment",
                        "script",
                        "cinematography_bible",
                    ],
                    artifacts_out=[
                        "semantic_storyboard",
                        "animatic_plan",
                        "storyboard_review",
                    ],
                    gate="STORYBOARD_ANIMATIC_GATE",
                ),
                CompanyStage(
                    stage_id="CRAFT_EXECUTION_DESIGN",
                    owner="DIRECTION",
                    artifacts_in=[
                        "story_architecture",
                        "script",
                        "director_cut",
                        "director_treatment",
                        "shot_book",
                        "cinematography_bible",
                        "animatic_plan",
                    ],
                    artifacts_out=[
                        "creative_intent_graph",
                        "camera_diagnostics",
                        "performance_direction",
                        "lighting_color_intent",
                        "sound_spotting",
                    ],
                    gate="CRAFT_EXECUTION_INTENT_GATE",
                ),
                CompanyStage(
                    stage_id="LAYOUT_TECHVIS",
                    owner="CINEMATOGRAPHY",
                    artifacts_in=[
                        "shot_book",
                        "semantic_storyboard",
                        "animatic_plan",
                        "creative_intent_graph",
                        "camera_diagnostics",
                        "asset_bible",
                        "assets",
                    ],
                    artifacts_out=["layout_techvis"],
                    gate="LAYOUT_TECHVIS_GATE",
                ),
                CompanyStage(
                    stage_id="CREATIVE_REVIEW",
                    owner="STUDIO_MANAGEMENT",
                    artifacts_in=[
                        "script_review",
                        "director_treatment",
                        "semantic_storyboard",
                        "animatic_plan",
                        "cinematography_bible",
                        "camera_diagnostics",
                        "performance_direction",
                        "creative_intent_graph",
                        "lighting_color_intent",
                        "sound_spotting",
                        "layout_techvis",
                        "previs_report",
                    ],
                    artifacts_out=["creative_review_approval"],
                    gate="CROSS_DEPARTMENT_CREATIVE_REVIEW",
                ),
            ])

        stage_map = {stage.stage_id: stage for stage in stages}
        stage_map["CREATIVE_STRATEGY"].artifacts_in.extend([
            "creative_development_brief",
            "audience_promise_contract",
        ])
        if use_story_pipeline:
            stage_map["WRITING"].artifacts_in.extend([
                "story",
                "story_architecture",
            ])
            stage_map["LOGIC"].artifacts_in.append("script_review")
            if "DIRECTION" in stage_map:
                stage_map["DIRECTION"].artifacts_in.append(
                    "director_treatment"
                )

        if use_visual_cinematic_pipeline:
            stage_map["CINEMATOGRAPHY"].artifacts_out.append(
                "cinematography_bible"
            )
            stage_map["PREVIS"].artifacts_in.extend([
                "semantic_storyboard",
                "animatic_plan",
                "layout_techvis",
            ])
            stage_map["TECHNICAL_DIRECTION"].artifacts_in.extend([
                "creative_review_approval",
                "creative_intent_graph",
                "camera_diagnostics",
                "performance_direction",
                "lighting_color_intent",
                "sound_spotting",
            ])
            stage_map["PRODUCTION"].artifacts_in.extend([
                "creative_intent_graph",
                "performance_direction",
            ])
            stage_map["EDITORIAL"].artifacts_in.append(
                "creative_intent_graph"
            )
            stage_map["AUDIO"].artifacts_in.extend([
                "sound_spotting",
                "shot_book",
            ])
            stage_map["FINISHING"].artifacts_in.append(
                "lighting_color_intent"
            )
            stage_map["FINISHING"].artifacts_out.append(
                "color_plan"
            )

    if not professional_governance:
        professional_stage_ids = {
            "PROJECT_INTAKE",
            "PORTFOLIO_GREENLIGHT",
            "CORPORATE_PREFLIGHT",
        }
        professional_artifacts = {
            "project_intake",
            "portfolio_greenlight",
            "corporate_preflight",
            "seo_discovery_brief",
        }
        stages = [
            stage
            for stage in stages
            if stage.stage_id not in professional_stage_ids
        ]
        for stage in stages:
            stage.artifacts_in = [
                item
                for item in stage.artifacts_in
                if item not in professional_artifacts
            ]
    return stages



def attach_channel_franchise_stages(
    stages: list[CompanyStage], strategy: ChannelEpisodeStrategy
) -> list[CompanyStage]:
    """Wire persistent original-channel planning into the real film DAG."""
    required = {
        "PROJECT_INTAKE", "CREATIVE_STRATEGY", "STORY_ARCHITECTURE",
        "WRITING", "PRODUCTION", "FINAL_QC", "PACKAGING",
    }
    stage_ids = {stage.stage_id for stage in stages}
    if not required.issubset(stage_ids):
        raise ValueError(
            "CHANNEL_FRANCHISE_REQUIRES_FULL_STORY_PIPELINE:"
            + ",".join(sorted(required - stage_ids))
        )
    stages = [s.model_copy(deep=True) for s in stages]
    stages.insert(
        next(i for i,s in enumerate(stages) if s.stage_id == "CREATIVE_STRATEGY"),
        CompanyStage(
            stage_id="CHANNEL_IDENTITY", owner="CREATIVE_STRATEGY",
            artifacts_in=["project_intake"],
            artifacts_out=["channel_identity", "episode_strategy"],
            gate="IMMUTABLE_CHANNEL_BIBLE_PROVENANCE",
        ),
    )
    stages.insert(
        next(i for i,s in enumerate(stages) if s.stage_id == "PLANNING"),
        CompanyStage(
            stage_id="SERIES_EDITORIAL", owner="STUDIO_MANAGEMENT",
            artifacts_in=["channel_identity", "episode_strategy", "creative_brief"],
            artifacts_out=["series_editorial_plan"],
            gate="SERIES_CONTINUITY_AND_ORIGINALITY_PLANNING",
        ),
    )
    by_id = {s.stage_id: s for s in stages}
    by_id["CREATIVE_STRATEGY"].artifacts_in.append("episode_strategy")
    for name in ("STORY_ARCHITECTURE", "WRITING", "PRODUCTION", "FINAL_QC", "PACKAGING"):
        by_id[name].artifacts_in.append("series_editorial_plan")
    by_id["PACKAGING"].artifacts_in.append("channel_identity")
    return stages


class CompanyOrchestrator:
    """Builds a complete company-level plan before any expensive execution begins."""

    def __init__(self, kernel) -> None:
        self.kernel = kernel

    def _packs_for(
        self,
        media_format: MediaFormat,
        *,
        domain: str | None = None,
    ) -> PackComposition:
        domain_pack = None
        genre_pack = None
        execution_pack = self.kernel.packs.get("execution.offline3d")
        platform_pack = self.kernel.packs.get("platform.youtube_longform")

        if (domain or "") == "animation.animal_long_slide":
            domain_pack = self.kernel.packs.get("domain.animation.animal_long_slide")
        elif media_format is MediaFormat.GAMEPLAY or (domain or "").startswith("gaming."):
            domain_pack = self.kernel.packs.get("domain.gaming")
            if media_format is MediaFormat.GAMEPLAY:
                execution_pack = None
        elif media_format is MediaFormat.DOCUMENTARY:
            genre_pack = self.kernel.packs.get("genre.documentary")
        elif media_format is MediaFormat.TUTORIAL:
            genre_pack = self.kernel.packs.get("genre.tutorial")

        return PackComposition(
            domain_pack=domain_pack,
            genre_pack=genre_pack,
            execution_pack=execution_pack,
            platform_pack=platform_pack,
        )

    @staticmethod
    def _sanitize_reference_scripts(
        project: StudioProjectSpec,
        pack: ScriptSourcePack,
    ) -> StudioProjectSpec:
        analyses = {
            item.input_id: item
            for item in pack.reference_script_analyses
        }
        safe_inputs: list[PlanningInputRef] = []
        for item in project.planning_inputs:
            if item.kind is not PlanningInputKind.REFERENCE_SCRIPT:
                safe_inputs.append(item)
                continue
            analysis = analyses.get(item.input_id)
            metadata = {
                "quarantined": True,
                "content_sha256": (
                    analysis.content_sha256
                    if analysis is not None
                    else None
                ),
                "quarantine_error": (
                    None
                    if analysis is not None
                    else "REFERENCE_SCRIPT_ANALYSIS_UNAVAILABLE"
                ),
                "structure_patterns": (
                    analysis.structure_patterns
                    if analysis is not None
                    else []
                ),
                "scene_count": (
                    analysis.scene_count
                    if analysis is not None
                    else None
                ),
                "dialogue_word_ratio": (
                    analysis.dialogue_word_ratio
                    if analysis is not None
                    else None
                ),
                "raw_expression_allowed": False,
            }
            safe_inputs.append(
                PlanningInputRef(
                    input_id=item.input_id,
                    kind=item.kind,
                    uri=None,
                    title=None,
                    content=None,
                    notes=list(item.notes),
                    metadata=metadata,
                )
            )
        return project.model_copy(
            update={"planning_inputs": safe_inputs},
            deep=True,
        )

    def build_blueprint(
        self, project: StudioProjectSpec, *, professional_governance: bool | None = None
    ) -> CompanyBlueprint:
        # Compile user-owned script inputs before format planning. This lets an
        # explicit script inform format and, only when the user did not provide
        # duration, provide a conservative planning-duration estimate.
        script_source_pack = ScriptInputCompiler(
            self.kernel.root
        ).compile(project.planning_inputs)
        planning_project = project
        profile = script_source_pack.production_profile
        if (
            project.duration_seconds is None
            and profile is not None
            and profile.estimated_duration_seconds > 0
        ):
            planning_project = project.model_copy(
                update={
                    "duration_seconds": max(
                        1,
                        int(round(profile.estimated_duration_seconds)),
                    )
                },
                deep=True,
            )

        # Classification may use user-owned SCRIPT/SCRIPT_OUTLINE signals.
        # REFERENCE_SCRIPT is quarantined immediately afterward so raw
        # reference expression does not persist in the company blueprint/ledger.
        plan = self.kernel.control_plane.plan(planning_project)
        safe_project = self._sanitize_reference_scripts(
            planning_project,
            script_source_pack,
        )
        plan = plan.model_copy(
            update={"project": safe_project},
            deep=True,
        )
        # Source-truth routing precedes recipe, DNA, packs and stage creation.
        # Never compile fake narrative-film internals for a real game stream.
        market = self.kernel.professional_company.intake.intake(
            safe_project
        ).resolved_niche
        minecraft_route = None
        if market == "minecraft":
            minecraft_route = classify_minecraft(
                safe_project.prompt, safe_project.minecraft_subniche,
            )
            if minecraft_route.blocker:
                raise ValueError(
                    "MINECRAFT_MODE_REQUIRES_REVIEW:" + minecraft_route.blocker
                )
            if minecraft_route.production_lane is not MinecraftLane.FILM_ANIMATION:
                from .minecraft_subniche_v207 import CATALOG
                source=CATALOG[minecraft_route.subniche_id]
                real=plan.product.model_copy(update={
                    "format":MediaFormat.GAMEPLAY,
                    "actual_gameplay_required":True,
                    "story_required":(
                        minecraft_route.production_lane
                        is MinecraftLane.STAGED_GAME_MACHINIMA
                    ),
                    "source_modalities":[source.source_truth],
                    "constraints":{
                        **plan.product.constraints,
                        "minecraft_production_lane":minecraft_route.production_lane.value,
                        "minecraft_subniche":source.subniche_id,
                        "real_game_runtime_mandatory":True,
                        "is_realtime_live":minecraft_route.production_lane is MinecraftLane.LIVE_RUNTIME,
                    },
                })
                plan=plan.model_copy(update={
                    "product":real,"segments":[],
                    "executable":False,
                    "blockers":[
                        "REAL_GAME_CAPTURE_CAPABILITIES_NOT_VERIFIED",
                    ],
                })
        # A catalogue entry saying "blender.local is executable" is not
        # evidence that Blender actually exists on this computer.  For
        # professionally governed projects, fail closed before compiling the
        # production recipe when concrete backends cannot launch.
        if professional_governance is True:
            from .runtime_route_grounding_v265 import ground_professional_plan
            plan = ground_professional_plan(plan)
        route_map = {
            item.segment.segment_id: item.routes
            for item in plan.segments
        }

        from .production import ProductionCompiler

        recipe = ProductionCompiler().compile(
            safe_project.studio_project_id,
            [item.segment for item in plan.segments],
            route_map,
        )
        if (minecraft_route is not None and
                minecraft_route.production_lane is not MinecraftLane.FILM_ANIMATION):
            recipe=recipe.model_copy(update={
                "blocked":True,
                "blockers":["REQUIRES_ACTUAL_QUALIFIED_GAME_CAPTURE_ENGINE"],
            })
        dna = self.kernel.dna_compiler.compile(
            safe_project,
            plan.product,
        )
        pod = self.kernel.pod_builder.build(
            safe_project.studio_project_id,
            plan.product.format,
        )
        packs = self._packs_for(
            plan.product.format,
            domain=str(plan.product.constraints.get("domain", "")),
        )
        from .quality import QualityProfileRegistry
        quality = QualityProfileRegistry().for_format(plan.product.format)

        professional_intake = self.kernel.professional_company.intake.intake(
            safe_project
        )
        portfolio_greenlight = (
            self.kernel.professional_company.intake.portfolio_greenlight(
                safe_project
            )
        )
        # Pilot-only fast path for an already validated approved niche pod.
        # This never permits a full-length episode or YouTube publishing.
        import os
        from hashlib import sha256
        from .specialist_media_lanes_v205 import is_specialist_lane
        pilot_only = False
        approved_pilot_sha256 = None
        if is_specialist_lane(safe_project.niche):
            workorder = (
                self.kernel.root / "data" / "projects"
                / safe_project.studio_project_id / "inputs"
                / "approved_studio_work_order.json"
            )
            if workorder.is_file():
                key = os.environ.get("CINEFACTORY_OWNER_TRUST_PUBKEY")
                if not key:
                    raise PermissionError("SIGNED_PILOT_OWNER_TRUST_KEY_REQUIRED")
                from .research_studio_handoff_v205 import verify_studio_work_order
                approved = verify_studio_work_order(
                    workorder, trusted_public_key=key,
                )
                if (not approved.get("pilot_only")
                        or not approved.get("production_permission")
                        or approved.get("niche") != safe_project.niche
                        or approved.get("project_id") != safe_project.studio_project_id):
                    raise PermissionError("SIGNED_PILOT_WORKORDER_SCOPE_MISMATCH")
                duration = safe_project.duration_seconds or 0
                if not 30 <= duration <= 60:
                    raise PermissionError("SIGNED_PILOT_ONLY_30_TO_60_SECONDS")
                approved_pilot_sha256 = sha256(workorder.read_bytes()).hexdigest()
                pilot_only = True
                portfolio_greenlight = portfolio_greenlight.model_copy(update={
                    "approved_for_research": True,
                    "approved_for_production": True,
                    "blockers": [],
                    "warnings": list(portfolio_greenlight.warnings) + [
                        "ONLY_SIGNED_ORIGINAL_PILOT_LOCAL_MEDIA_IS_APPROVED",
                        "OTHER_NICHE_CONFIG_GAPS_STILL_REQUIRE_REMEDIATION",
                    ],
                })
        blockers = list(plan.blockers) + list(recipe.blockers)
        if not portfolio_greenlight.approved_for_research:
            blockers.extend(portfolio_greenlight.blockers)
        if professional_governance is None:
            # Every NEW project requires the same governance, even when the
            # operator starts with a prompt rather than a named niche.
            # Legacy non-strict replay remains an explicit opt-out only.
            professional_governance = True
        if professional_governance and not safe_project.niche:
            # A prompt-only unknown format is a development proposal, not
            # an approved film investment and may not dispatch render costs.
            blockers.append("UNCLASSIFIED_NICHE_REQUIRES_OWNER_GREENLIGHT")
        if professional_governance and not portfolio_greenlight.approved_for_production:
            blockers.append("NICHE_PRODUCTION_NOT_GREENLIT")
            blockers.extend(
                f"NICHE_READINESS:{item}"
                for item in portfolio_greenlight.blockers
            )
        stages = stage_blueprint(
            plan.product.format,
            plan.product.evidence_required,
            professional_governance=professional_governance,
            professional_niche=professional_intake.resolved_niche,
            native_media_lane=bool(
                professional_governance and is_specialist_lane(safe_project.niche)
            ),
            voice_required=(
                plan.product.constraints.get("dialogue_required")
                if isinstance(plan.product.constraints.get("dialogue_required"), bool)
                else None
            ),
        )
        channel_strategy = None
        if safe_project.channel_brand_id is not None:
            if not professional_governance or safe_project.niche != "minecraft":
                raise ValueError("CHANNEL_BRAND_REQUIRES_PROFESSIONAL_MINECRAFT_NICHE")
            if safe_project.series_id is None:
                if (minecraft_route is None or
                        minecraft_route.production_lane is not MinecraftLane.FILM_ANIMATION):
                    raise ValueError("CHANNEL_STANDALONE_REQUIRES_COMPATIBLE_ANIMATION_FAMILY")
                channel_strategy=ChannelLibrary(self.kernel.root).resolve_standalone(
                    safe_project.channel_brand_id,
                    safe_project.studio_project_id,
                    safe_project.prompt,
                    minecraft_route.subniche_id,
                )
            else:
                channel_strategy = ChannelLibrary(self.kernel.root).resolve_episode(
                    safe_project.channel_brand_id,
                    safe_project.series_id,
                    safe_project.episode_id,
                    reuse_characters=safe_project.reuse_series_characters,
                )
            stages = attach_channel_franchise_stages(stages, channel_strategy)
            # Project DNA inherits the stable channel promise. Scene-level DNA
            # may specialize it, but it must not silently redefine the channel.
            dna = dna.model_copy(update={
                "brand": dna.brand.model_copy(update={
                    "promise": channel_strategy.brand_promise,
                })
            })
        if minecraft_route is not None:
            if channel_strategy is not None:
                expected=canonical_subniche(channel_strategy.subniche)
                actual=canonical_subniche(minecraft_route.subniche_id)
                if expected!=actual:
                    raise ValueError("SERIES_SUBNICHE_CANNOT_CHANGE_PRODUCTION_MODE")
                if minecraft_route.production_lane is not MinecraftLane.FILM_ANIMATION:
                    raise ValueError("ANIMATION_SERIES_CANNOT_RENDER_REAL_GAMEPLAY")
            if minecraft_route.production_lane is not MinecraftLane.FILM_ANIMATION:
                if channel_strategy is not None:
                    raise ValueError("REAL_GAME_CAPTURE_CANNOT_INHERIT_ANIMATION_SERIES")
                from .minecraft_capture_v207 import capture_stages
                stages=capture_stages(minecraft_route)
                blockers.append("REAL_GAME_CAPTURE_NOT_YET_INDEPENDENTLY_QUALIFIED")
        from .contract_integrity import audit_company_wiring
        wiring = audit_company_wiring(stages)
        blockers.extend(wiring.blocker_codes())
        # Provide research-led technology candidates as an ADVISORY handoff
        # only. Production executor selection and rights approvals are still
        # controlled by existing v209/v191 qualification and owner gates.
        from .technology_discovery_v211 import propose_technology_for_format
        tech_format = (
            minecraft_route.subniche_id if minecraft_route else safe_project.niche
        )
        technology_advisory = (
            propose_technology_for_format(
                tech_format, safe_project.niche
            ) if professional_governance else None
        )
        blueprint = CompanyBlueprint(
            project=safe_project,
            studio_plan=plan,
            project_dna=dna,
            project_pod=pod,
            packs=packs,
            production_recipe=recipe,
            quality_profile=quality,
            script_source_pack=script_source_pack,
            project_intake=professional_intake,
            portfolio_greenlight=portfolio_greenlight,
            stages=stages,
            strict_stage_receipts=professional_governance,
            pilot_only=pilot_only,
            approved_pilot_work_order_sha256=approved_pilot_sha256,
            channel_episode_strategy=channel_strategy,
            minecraft_route=minecraft_route,
            technology_research_advisory=technology_advisory,
            executable=not blockers,
            blockers=blockers,
        )
        from .technology_council_v212 import company_stage_technology_routing
        blueprint.department_technology_advisory = company_stage_technology_routing(
            blueprint
        )
        return blueprint
