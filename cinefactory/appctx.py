from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

import yaml

from cinefactory.core.policy import FactoryPolicy
from cinefactory.creative.store import CreativeStore
from cinefactory.executors.comfyui import ComfyUIExecutor
from cinefactory.executors.local_mock import LocalMockExecutor
from cinefactory.executors.registry import ExecutorRegistry
from cinefactory.pipeline.creative import CreativePipeline
from cinefactory.pipeline.jobs import JobService
from cinefactory.pipeline.orchestrator import PipelineOrchestrator
from cinefactory.models.registry import ModelRegistry
from cinefactory.compliance.rights import RightsGate
from cinefactory.originality import ReferenceLibrary
from cinefactory.storage.database import AssetRepository, AuditLogRepository, Database, JobLedgerRepository, SqlProjectRepository
from cinefactory.workflows.registry import WorkflowRegistry
from cinefactory.turbo.store import TurboStore
from cinefactory.turbo.repair_memory import RepairMemory
from cinefactory.studio import CapabilityRegistry, SkillRegistry, StudioBlackboard, StudioControlPlane
from cinefactory.studio.kernel import StudioKernel, build_studio_kernel
from cinefactory.studio.factory_operations import FactoryOperationsManager, FactoryOperationsStore
from cinefactory.studio.production_method_switch import (
    ProductionMethodSwitchController,
)
from cinefactory.studio.capability_acquisition import (
    CapabilityAcquisitionWorker,
)
from cinefactory.studio.capability_execution_lab import (
    CapabilityExecutionLab,
)
from cinefactory.studio.candidate_promotion import (
    CandidatePromotionController,
)
from cinefactory.studio.production_continuation import (
    ProductionContinuationManager,
)
from cinefactory.studio.cross_backend_video import (
    CrossBackendVideoService,
)
from cinefactory.studio.character_factory import CharacterFactory
from cinefactory.studio.dialogue_performance import DialoguePerformanceEngine
from cinefactory.studio.temporal_reid import TemporalReIDEngine
from cinefactory.studio.real_speech_viseme import RealSpeechVisemeService
from cinefactory.studio.audio_constrained_alignment import AudioConstrainedWordVerifier
from cinefactory.studio.rendered_mouth_qc import RenderedMouthProjectionQC
from cinefactory.studio.source_speaker_attribution import SourceConditionedSpeakerVerifier
from cinefactory.studio.face_mouth_observability import FacePatchMotionMouthDetector
from cinefactory.studio.mouth_image_rig_agreement import MouthRigCrossCheck
from cinefactory.studio.multishot_render_identity import TwoShotImageIdentityVerifier
from cinefactory.studio.full_frame_actor_search import FullFrameReferenceActorScanner
from cinefactory.studio.independent_speech_asr import OfflineIndependentASR
from cinefactory.studio.acoustic_forced_alignment import PocketSphinxAcousticAligner
from cinefactory.studio.phoneme_video_proxy_qc import PhonemeVideoProxyQC
from cinefactory.studio.trained_actor_detector_qc import HeldoutActorDetectorEvaluator
from cinefactory.studio.blender_mask_dataset_qc import BlenderVisibleMaskDatasetAssembler
from cinefactory.studio.multiscene_detector_qc import MultiSceneDetectorEvaluator
from cinefactory.studio.real_rig_domain_qc import RealRigDomainAdmissionQC
from cinefactory.studio.production_tool_catalog_v191 import ProductionPortfolioAdvisor
from cinefactory.studio.niche_research_conference_v192 import NicheResearchConference
from cinefactory.studio.strategic_reasoning_v193 import StrategicResearchReasoner
from cinefactory.studio.scientific_learning_v193 import ScientificLearningBridge
from cinefactory.studio.reasoning_agent_bridge_v193 import ReasoningAgentBridge
from cinefactory.studio.autonomous_source_research_v194 import AutonomousSourceResearchOrchestrator
from cinefactory.studio.video_production_intelligence_v195 import VideoProductionIntelligence
from cinefactory.studio.golden_shot_benchmark_v196 import GoldenShotBenchmarkLab
from cinefactory.studio.daily_youtube_breakout_v199 import DailyYouTubeBreakoutResearchService
from cinefactory.studio.independent_actor_detection import IndependentActorDetectionLab
from cinefactory.studio.audio_visual_sync_qc import AudioVisualSyncVerifier, PerformanceQualificationGate
from cinefactory.studio.shot_routing import ShotRoutingAdapter
from cinefactory.studio.video_backend_qualification import (
    VideoBackendQualificationController,
)


@dataclass
class AppContext:
    root: Path
    settings: dict
    policy: FactoryPolicy
    db: Database
    projects: SqlProjectRepository
    audit: AuditLogRepository
    jobs: JobLedgerRepository
    assets: AssetRepository
    executors: ExecutorRegistry
    orchestrator: PipelineOrchestrator
    creative: CreativePipeline
    workflows: WorkflowRegistry
    job_service: JobService
    models: ModelRegistry
    rights_gate: RightsGate
    references: ReferenceLibrary
    turbo_store: TurboStore
    repair_memory: RepairMemory
    studio: StudioKernel
    factory_operations: FactoryOperationsManager
    method_switch: ProductionMethodSwitchController
    capability_acquisition: CapabilityAcquisitionWorker
    capability_execution_lab: CapabilityExecutionLab
    candidate_promotion: CandidatePromotionController
    character_factory: CharacterFactory
    dialogue_performance: DialoguePerformanceEngine
    temporal_reid: TemporalReIDEngine
    real_speech_viseme: RealSpeechVisemeService
    audio_word_alignment: AudioConstrainedWordVerifier
    rendered_mouth_qc: RenderedMouthProjectionQC
    speaker_stem_qc: SourceConditionedSpeakerVerifier
    image_mouth_observability: FacePatchMotionMouthDetector
    mouth_rig_crosscheck: MouthRigCrossCheck
    multishot_render_identity: TwoShotImageIdentityVerifier
    full_frame_reference_actor: FullFrameReferenceActorScanner
    offline_independent_asr: OfflineIndependentASR
    acoustic_forced_alignment: PocketSphinxAcousticAligner
    phoneme_video_proxy_qc: PhonemeVideoProxyQC
    trained_actor_detector_qc: HeldoutActorDetectorEvaluator
    blender_mask_dataset_qc: BlenderVisibleMaskDatasetAssembler
    multiscene_detector_qc: MultiSceneDetectorEvaluator
    real_rig_domain_qc: RealRigDomainAdmissionQC
    production_portfolio_advisor: ProductionPortfolioAdvisor
    niche_research_conference: NicheResearchConference
    strategic_research_reasoner: StrategicResearchReasoner
    scientific_learning_bridge: ScientificLearningBridge
    reasoning_agent_bridge: ReasoningAgentBridge
    autonomous_source_research: AutonomousSourceResearchOrchestrator
    video_production_intelligence: VideoProductionIntelligence
    golden_shot_benchmark_lab: GoldenShotBenchmarkLab
    daily_youtube_breakout_research: DailyYouTubeBreakoutResearchService
    independent_actor_detection: IndependentActorDetectionLab
    audio_visual_sync: AudioVisualSyncVerifier
    performance_qualification: PerformanceQualificationGate
    shot_router: ShotRoutingAdapter
    cross_backend_video: CrossBackendVideoService
    video_backend_qualification: VideoBackendQualificationController
    production_continuation: ProductionContinuationManager


def build_context(root: Path | None = None) -> AppContext:
    if root is None:
        env_root = os.getenv("CINEFACTORY_ROOT")
        root = Path(env_root).resolve() if env_root else Path(__file__).resolve().parents[1]
        if not (root / "config" / "settings.yaml").exists() and (Path.cwd() / "config" / "settings.yaml").exists():
            root = Path.cwd().resolve()
    settings = yaml.safe_load((root / "config" / "settings.yaml").read_text(encoding="utf-8"))
    policy = FactoryPolicy.from_yaml(root / "config" / "factory_policy.yaml")

    db_url = os.getenv("CINEFACTORY_DATABASE_URL") or settings.get("database", {}).get("url", "sqlite:///./data/cinefactory.db")
    if db_url.startswith("sqlite:///./"):
        db_url = "sqlite:///" + str((root / db_url.removeprefix("sqlite:///./")).resolve())
    db = Database(db_url)
    db.create_schema()

    projects = SqlProjectRepository(db)
    audit = AuditLogRepository(db)
    jobs = JobLedgerRepository(db)
    assets = AssetRepository(db)

    executors = ExecutorRegistry()
    executors.register(LocalMockExecutor(policy))
    comfy_url = os.getenv("CINEFACTORY_COMFYUI") or settings.get("comfyui", {}).get("base_url", "http://127.0.0.1:8188")
    executors.register(ComfyUIExecutor(policy, base_url=comfy_url))

    orchestrator = PipelineOrchestrator(policy, projects, audit)
    creative_store = CreativeStore(root / "data" / "projects")
    creative = CreativePipeline(creative_store, orchestrator)
    workflows = WorkflowRegistry(root / "workflows").load()
    job_service = JobService(jobs, audit, executors, workflows)
    models = ModelRegistry(root / "models" / "registry.yaml").load()
    rights_gate = RightsGate(assets, models)
    references = ReferenceLibrary(root / "data" / "references")
    turbo_store = TurboStore(root / "data" / "turbo.db")
    repair_memory = RepairMemory(turbo_store)
    studio = build_studio_kernel(root)
    factory_operations = FactoryOperationsManager(
        turbo_store=turbo_store,
        store=FactoryOperationsStore(root / "data" / "studio" / "operations"),
    )
    character_factory = CharacterFactory(root)
    dialogue_performance = DialoguePerformanceEngine()
    temporal_reid = TemporalReIDEngine()
    real_speech_viseme = RealSpeechVisemeService(root)
    audio_word_alignment = AudioConstrainedWordVerifier()
    rendered_mouth_qc = RenderedMouthProjectionQC()
    speaker_stem_qc = SourceConditionedSpeakerVerifier()
    image_mouth_observability = FacePatchMotionMouthDetector()
    mouth_rig_crosscheck = MouthRigCrossCheck()
    multishot_render_identity = TwoShotImageIdentityVerifier()
    full_frame_reference_actor = FullFrameReferenceActorScanner()
    offline_independent_asr = OfflineIndependentASR(root)
    acoustic_forced_alignment = PocketSphinxAcousticAligner(root)
    phoneme_video_proxy_qc = PhonemeVideoProxyQC()
    trained_actor_detector_qc = HeldoutActorDetectorEvaluator()
    blender_mask_dataset_qc = BlenderVisibleMaskDatasetAssembler()
    multiscene_detector_qc = MultiSceneDetectorEvaluator()
    real_rig_domain_qc = RealRigDomainAdmissionQC()
    production_portfolio_advisor = ProductionPortfolioAdvisor(root)
    niche_research_conference = NicheResearchConference(root)
    strategic_research_reasoner = StrategicResearchReasoner(root)
    scientific_learning_bridge = ScientificLearningBridge()
    reasoning_agent_bridge = ReasoningAgentBridge()
    autonomous_source_research = AutonomousSourceResearchOrchestrator(root)
    video_production_intelligence = VideoProductionIntelligence(root)
    golden_shot_benchmark_lab = GoldenShotBenchmarkLab(root)
    daily_youtube_breakout_research = DailyYouTubeBreakoutResearchService(root)
    independent_actor_detection = IndependentActorDetectionLab()
    audio_visual_sync = AudioVisualSyncVerifier()
    performance_qualification = PerformanceQualificationGate()
    cross_backend_video = CrossBackendVideoService(
        root,
        executors,
        character_factory=character_factory,
    )
    provisional = type(
        "_MethodSwitchContext",
        (),
        {
            "root": root,
            "studio": studio,
            "workflows": workflows,
            "models": models,
            "cross_backend_video": cross_backend_video,
        },
    )()
    method_switch = ProductionMethodSwitchController(
        provisional
    )
    shot_router = ShotRoutingAdapter(
        method_switch,
        character_factory=character_factory,
    )
    studio.professional_company.method_switch = (
        method_switch
    )
    studio.professional_company.shot_router = (
        shot_router
    )
    acquisition_context = type(
        "_CapabilityAcquisitionContext",
        (),
        {
            "root": root,
            "studio": studio,
            "workflows": workflows,
            "models": models,
            "method_switch": method_switch,
            "cross_backend_video": cross_backend_video,
            "turbo_store": turbo_store,
        },
    )()
    production_continuation = ProductionContinuationManager(
        root,
        turbo_store,
    )
    acquisition_context.production_continuation = (
        production_continuation
    )
    capability_acquisition = CapabilityAcquisitionWorker(
        acquisition_context
    )
    studio.professional_company.capability_acquisition = (
        capability_acquisition
    )
    capability_execution_lab = (
        capability_acquisition.execution_lab
    )
    studio.professional_company.capability_execution_lab = (
        capability_execution_lab
    )
    candidate_context = type(
        "_CandidatePromotionContext",
        (),
        {
            "root": root,
            "models": models,
            "executors": executors,
            "workflows": workflows,
            "method_switch": method_switch,
            "capability_execution_lab": (
                capability_execution_lab
            ),
        },
    )()
    candidate_promotion = CandidatePromotionController(
        candidate_context
    )
    acquisition_context.candidate_promotion = (
        candidate_promotion
    )
    studio.professional_company.candidate_promotion = (
        candidate_promotion
    )
    studio.professional_company.character_factory = (
        character_factory
    )
    studio.professional_company.dialogue_performance = (
        dialogue_performance
    )
    studio.professional_company.temporal_reid = temporal_reid
    studio.professional_company.real_speech_viseme = real_speech_viseme
    studio.professional_company.audio_word_alignment = audio_word_alignment
    studio.professional_company.rendered_mouth_qc = rendered_mouth_qc
    studio.professional_company.speaker_stem_qc = speaker_stem_qc
    studio.professional_company.image_mouth_observability = image_mouth_observability
    studio.professional_company.mouth_rig_crosscheck = mouth_rig_crosscheck
    studio.professional_company.multishot_render_identity = multishot_render_identity
    studio.professional_company.full_frame_reference_actor = full_frame_reference_actor
    studio.professional_company.offline_independent_asr = offline_independent_asr
    studio.professional_company.acoustic_forced_alignment = acoustic_forced_alignment
    studio.professional_company.phoneme_video_proxy_qc = phoneme_video_proxy_qc
    studio.professional_company.trained_actor_detector_qc = trained_actor_detector_qc
    studio.professional_company.blender_mask_dataset_qc = blender_mask_dataset_qc
    studio.professional_company.multiscene_detector_qc = multiscene_detector_qc
    studio.professional_company.real_rig_domain_qc = real_rig_domain_qc
    studio.professional_company.production_portfolio_advisor = production_portfolio_advisor
    studio.professional_company.niche_research_conference = niche_research_conference
    studio.professional_company.strategic_research_reasoner = strategic_research_reasoner
    studio.professional_company.scientific_learning_bridge = scientific_learning_bridge
    studio.professional_company.reasoning_agent_bridge = reasoning_agent_bridge
    studio.professional_company.autonomous_source_research = autonomous_source_research
    studio.professional_company.video_production_intelligence = video_production_intelligence
    studio.professional_company.golden_shot_benchmark_lab = golden_shot_benchmark_lab
    studio.professional_company.daily_youtube_breakout_research = daily_youtube_breakout_research
    studio.professional_company.independent_actor_detection = independent_actor_detection
    studio.professional_company.audio_visual_sync = audio_visual_sync
    studio.professional_company.performance_qualification = performance_qualification
    studio.professional_company.cross_backend_video = (
        cross_backend_video
    )
    qualification_context = type(
        "_VideoBackendQualificationContext",
        (),
        {
            "root": root,
            "studio": studio,
            "workflows": workflows,
            "models": models,
            "cross_backend_video": cross_backend_video,
            "capability_execution_lab": (
                capability_execution_lab
            ),
        },
    )()
    video_backend_qualification = (
        VideoBackendQualificationController(
            qualification_context
        )
    )
    studio.professional_company.video_backend_qualification = (
        video_backend_qualification
    )
    studio.professional_company.production_continuation = (
        production_continuation
    )

    return AppContext(
        root=root,
        settings=settings,
        policy=policy,
        db=db,
        projects=projects,
        audit=audit,
        jobs=jobs,
        assets=assets,
        executors=executors,
        orchestrator=orchestrator,
        creative=creative,
        workflows=workflows,
        job_service=job_service,
        models=models,
        rights_gate=rights_gate,
        references=references, turbo_store=turbo_store, repair_memory=repair_memory,
        studio=studio,
        factory_operations=factory_operations,
        method_switch=method_switch,
        capability_acquisition=capability_acquisition,
        capability_execution_lab=capability_execution_lab,
        candidate_promotion=candidate_promotion,
        character_factory=character_factory,
        dialogue_performance=dialogue_performance,
        temporal_reid=temporal_reid,
        real_speech_viseme=real_speech_viseme,
        audio_word_alignment=audio_word_alignment,
        rendered_mouth_qc=rendered_mouth_qc,
        speaker_stem_qc=speaker_stem_qc,
        image_mouth_observability=image_mouth_observability,
        mouth_rig_crosscheck=mouth_rig_crosscheck,
        multishot_render_identity=multishot_render_identity,
        full_frame_reference_actor=full_frame_reference_actor,
        offline_independent_asr=offline_independent_asr,
        acoustic_forced_alignment=acoustic_forced_alignment,
        phoneme_video_proxy_qc=phoneme_video_proxy_qc,
        trained_actor_detector_qc=trained_actor_detector_qc,
        blender_mask_dataset_qc=blender_mask_dataset_qc,
        multiscene_detector_qc=multiscene_detector_qc,
        real_rig_domain_qc=real_rig_domain_qc,
        production_portfolio_advisor=production_portfolio_advisor,
        niche_research_conference=niche_research_conference,
        strategic_research_reasoner=strategic_research_reasoner,
        scientific_learning_bridge=scientific_learning_bridge,
        reasoning_agent_bridge=reasoning_agent_bridge,
        autonomous_source_research=autonomous_source_research,
        video_production_intelligence=video_production_intelligence,
        golden_shot_benchmark_lab=golden_shot_benchmark_lab,
        daily_youtube_breakout_research=daily_youtube_breakout_research,
        independent_actor_detection=independent_actor_detection,
        audio_visual_sync=audio_visual_sync,
        performance_qualification=performance_qualification,
        shot_router=shot_router,
        cross_backend_video=cross_backend_video,
        video_backend_qualification=video_backend_qualification,
        production_continuation=production_continuation,
    )
