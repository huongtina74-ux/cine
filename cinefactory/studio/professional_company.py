from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .authority import AuthorityMatrix
from .corporate import CompanyFunctionRegistry
from .handoffs import HandoffRegistry
from .hierarchy import CreativeIntentHierarchy
from .intake import ProjectIntakeEngine
from .maturity import CompanyMaturityAudit
from .niche_os import NicheRegistry
from .review_board import DailiesReviewBoard
from .seo import NicheSEOBrain
from .production_economics import ProductionEconomicsController
from .production_method_switch import ProductionMethodSwitchController
from .capability_acquisition import CapabilityAcquisitionWorker
from .capability_execution_lab import CapabilityExecutionLab
from .candidate_promotion import CandidatePromotionController
from .production_continuation import ProductionContinuationManager
from .cross_backend_video import CrossBackendVideoService
from .character_factory import CharacterFactory
from .dialogue_performance import DialoguePerformanceEngine
from .temporal_reid import TemporalReIDEngine
from .real_speech_viseme import RealSpeechVisemeService
from .audio_constrained_alignment import AudioConstrainedWordVerifier
from .rendered_mouth_qc import RenderedMouthProjectionQC
from .source_speaker_attribution import SourceConditionedSpeakerVerifier
from .face_mouth_observability import FacePatchMotionMouthDetector
from .mouth_image_rig_agreement import MouthRigCrossCheck
from .multishot_render_identity import TwoShotImageIdentityVerifier
from .full_frame_actor_search import FullFrameReferenceActorScanner
from .independent_speech_asr import OfflineIndependentASR
from .acoustic_forced_alignment import PocketSphinxAcousticAligner
from .phoneme_video_proxy_qc import PhonemeVideoProxyQC
from .trained_actor_detector_qc import HeldoutActorDetectorEvaluator
from .blender_mask_dataset_qc import BlenderVisibleMaskDatasetAssembler
from .multiscene_detector_qc import MultiSceneDetectorEvaluator
from .real_rig_domain_qc import RealRigDomainAdmissionQC
from .production_tool_catalog_v191 import ProductionPortfolioAdvisor
from .niche_research_conference_v192 import NicheResearchConference
from .strategic_reasoning_v193 import StrategicResearchReasoner
from .scientific_learning_v193 import ScientificLearningBridge
from .reasoning_agent_bridge_v193 import ReasoningAgentBridge
from .autonomous_source_research_v194 import AutonomousSourceResearchOrchestrator
from .video_production_intelligence_v195 import VideoProductionIntelligence
from .golden_shot_benchmark_v196 import GoldenShotBenchmarkLab
from .daily_youtube_breakout_v199 import DailyYouTubeBreakoutResearchService
from .independent_actor_detection import IndependentActorDetectionLab
from .audio_visual_sync_qc import AudioVisualSyncVerifier, PerformanceQualificationGate
from .shot_routing import ShotRoutingAdapter
from .video_backend_qualification import (
    VideoBackendQualificationController,
)


@dataclass
class ProfessionalCompanyLayer:
    company_functions: CompanyFunctionRegistry
    niches: NicheRegistry
    authority: AuthorityMatrix
    handoffs: HandoffRegistry
    dailies: DailiesReviewBoard
    maturity: CompanyMaturityAudit
    intent_hierarchy: CreativeIntentHierarchy
    seo_brains: dict[str, NicheSEOBrain]
    intake: ProjectIntakeEngine
    economics: ProductionEconomicsController
    method_switch: ProductionMethodSwitchController | None = None
    capability_acquisition: CapabilityAcquisitionWorker | None = None
    capability_execution_lab: CapabilityExecutionLab | None = None
    candidate_promotion: CandidatePromotionController | None = None
    character_factory: CharacterFactory | None = None
    dialogue_performance: DialoguePerformanceEngine | None = None
    temporal_reid: TemporalReIDEngine | None = None
    real_speech_viseme: RealSpeechVisemeService | None = None
    audio_word_alignment: AudioConstrainedWordVerifier | None = None
    rendered_mouth_qc: RenderedMouthProjectionQC | None = None
    speaker_stem_qc: SourceConditionedSpeakerVerifier | None = None
    image_mouth_observability: FacePatchMotionMouthDetector | None = None
    mouth_rig_crosscheck: MouthRigCrossCheck | None = None
    multishot_render_identity: TwoShotImageIdentityVerifier | None = None
    full_frame_reference_actor: FullFrameReferenceActorScanner | None = None
    offline_independent_asr: OfflineIndependentASR | None = None
    acoustic_forced_alignment: PocketSphinxAcousticAligner | None = None
    phoneme_video_proxy_qc: PhonemeVideoProxyQC | None = None
    trained_actor_detector_qc: HeldoutActorDetectorEvaluator | None = None
    blender_mask_dataset_qc: BlenderVisibleMaskDatasetAssembler | None = None
    multiscene_detector_qc: MultiSceneDetectorEvaluator | None = None
    real_rig_domain_qc: RealRigDomainAdmissionQC | None = None
    production_portfolio_advisor: ProductionPortfolioAdvisor | None = None
    niche_research_conference: NicheResearchConference | None = None
    strategic_research_reasoner: StrategicResearchReasoner | None = None
    scientific_learning_bridge: ScientificLearningBridge | None = None
    reasoning_agent_bridge: ReasoningAgentBridge | None = None
    autonomous_source_research: AutonomousSourceResearchOrchestrator | None = None
    video_production_intelligence: VideoProductionIntelligence | None = None
    golden_shot_benchmark_lab: GoldenShotBenchmarkLab | None = None
    daily_youtube_breakout_research: DailyYouTubeBreakoutResearchService | None = None
    independent_actor_detection: IndependentActorDetectionLab | None = None
    audio_visual_sync: AudioVisualSyncVerifier | None = None
    performance_qualification: PerformanceQualificationGate | None = None
    shot_router: ShotRoutingAdapter | None = None
    cross_backend_video: CrossBackendVideoService | None = None
    video_backend_qualification: VideoBackendQualificationController | None = None
    production_continuation: ProductionContinuationManager | None = None

    def seo_for(self, niche_id: str) -> NicheSEOBrain:
        if niche_id not in self.seo_brains:
            if niche_id not in {n.niche_id for n in self.niches.list()}:
                raise KeyError(niche_id)
            self.seo_brains[niche_id] = NicheSEOBrain(niche_id=niche_id)
        return self.seo_brains[niche_id]


def build_professional_company_layer(
    repo_root: str | Path = ".",
) -> ProfessionalCompanyLayer:
    niches = NicheRegistry()
    layer = ProfessionalCompanyLayer(
        company_functions=CompanyFunctionRegistry(),
        niches=niches,
        authority=AuthorityMatrix(),
        handoffs=HandoffRegistry(),
        dailies=DailiesReviewBoard(),
        maturity=CompanyMaturityAudit(),
        intent_hierarchy=CreativeIntentHierarchy(),
        seo_brains={
            niche.niche_id: NicheSEOBrain(niche_id=niche.niche_id)
            for niche in niches.list()
        },
        intake=ProjectIntakeEngine(repo_root, niches=niches),
        economics=ProductionEconomicsController(),
    )
    function_findings = layer.company_functions.validate()
    authority_findings = layer.authority.validate()
    if function_findings or authority_findings:
        raise RuntimeError(
            "PROFESSIONAL_COMPANY_LAYER_INVALID:"
            + ",".join([*function_findings, *authority_findings])
        )
    return layer
