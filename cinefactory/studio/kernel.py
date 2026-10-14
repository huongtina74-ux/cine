from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cinefactory.studio.acquisition import KnowledgeAcquisitionEngine, KnowledgeAcquisitionStore
from cinefactory.studio.blackboard import StudioBlackboard
from cinefactory.studio.capabilities import CapabilityRegistry
from cinefactory.studio.control_plane import StudioControlPlane
from cinefactory.studio.craft_curriculum import CraftCurriculumBootstrap
from cinefactory.studio.defaults import build_default_capability_registry
from cinefactory.studio.departments import DepartmentRegistry, default_department_registry
from cinefactory.studio.execution import ExecutionLedgerStore
from cinefactory.studio.execution_mastery import ExecutionMasteryStore
from cinefactory.studio.format_director import FormatDirector
from cinefactory.studio.knowledge import KnowledgeRegistry
from cinefactory.studio.learning import LearningStore
from cinefactory.studio.problem_solving import ProblemLibrary, RootCauseEngine
from cinefactory.studio.production_qualification import (
    ProductionQualificationStore,
    ToolAdapterRegistry,
)
from cinefactory.studio.production_memory import ProductionExperienceStore
from cinefactory.studio.project_dna import ProjectDNACompiler
from cinefactory.studio.project_pod import ProjectPodBuilder
from cinefactory.studio.reference_intelligence import ReferenceIntelligenceEngine
from cinefactory.studio.packs import PackRegistry, default_pack_registry
from cinefactory.studio.qc_department import QCDepartment
from cinefactory.studio.governance import ChangeRequestStore, StudioTrace
from cinefactory.studio.professional_company import (
    ProfessionalCompanyLayer,
    build_professional_company_layer,
)
from cinefactory.studio.skills import SkillRegistry
from cinefactory.studio.tooling import ToolDoctor, ToolSkillRegistry
from cinefactory.studio.tool_curriculum import ToolCurriculumBootstrap
from cinefactory.studio.tool_knowledge import ToolKnowledgeBootstrap


@dataclass
class StudioKernel:
    root: Path
    blackboard: StudioBlackboard
    departments: DepartmentRegistry
    skills: SkillRegistry
    knowledge: KnowledgeRegistry
    knowledge_acquisition: KnowledgeAcquisitionEngine
    problems: ProblemLibrary
    problem_solver: RootCauseEngine
    learning: LearningStore
    capabilities: CapabilityRegistry
    control_plane: StudioControlPlane
    format_director: FormatDirector
    dna_compiler: ProjectDNACompiler
    pod_builder: ProjectPodBuilder
    packs: PackRegistry
    qc_department: QCDepartment
    change_requests: ChangeRequestStore
    trace: StudioTrace
    tool_doctor: ToolDoctor
    tool_skills: ToolSkillRegistry
    execution_ledgers: ExecutionLedgerStore
    execution_mastery: ExecutionMasteryStore
    tool_adapters: ToolAdapterRegistry
    production_qualification: ProductionQualificationStore
    production_memory: ProductionExperienceStore
    reference_intelligence: ReferenceIntelligenceEngine
    professional_company: ProfessionalCompanyLayer


def build_studio_kernel(root: str | Path) -> StudioKernel:
    root_path = Path(root).resolve()
    studio_data = root_path / "data" / "studio"
    blackboard = StudioBlackboard(root_path / "data" / "projects")
    skills = SkillRegistry(studio_data / "skills")
    knowledge = KnowledgeRegistry(studio_data / "knowledge")
    knowledge_acquisition = KnowledgeAcquisitionEngine(
        KnowledgeAcquisitionStore(studio_data / "acquisition"),
        knowledge,
    )
    problems = ProblemLibrary()
    capabilities = build_default_capability_registry(root_path)
    kernel = StudioKernel(
        root=root_path,
        blackboard=blackboard,
        departments=default_department_registry(),
        skills=skills,
        knowledge=knowledge,
        knowledge_acquisition=knowledge_acquisition,
        problems=problems,
        problem_solver=RootCauseEngine(),
        learning=LearningStore(studio_data / "learning"),
        capabilities=capabilities,
        control_plane=StudioControlPlane(capabilities=capabilities),
        format_director=FormatDirector(),
        dna_compiler=ProjectDNACompiler(),
        pod_builder=ProjectPodBuilder(),
        packs=default_pack_registry(),
        qc_department=QCDepartment(),
        change_requests=ChangeRequestStore(studio_data / "change_requests"),
        trace=StudioTrace(studio_data / "studio_trace.jsonl"),
        tool_doctor=ToolDoctor(root_path),
        tool_skills=ToolSkillRegistry(),
        execution_ledgers=ExecutionLedgerStore(studio_data / "executions"),
        execution_mastery=ExecutionMasteryStore(
            studio_data / "execution_mastery"
        ),
        tool_adapters=ToolAdapterRegistry(),
        production_qualification=ProductionQualificationStore(
            studio_data / "production_qualification"
        ),
        production_memory=ProductionExperienceStore(
            studio_data / "production_memory"
        ),
        reference_intelligence=ReferenceIntelligenceEngine(
            root_path
        ),
        professional_company=build_professional_company_layer(root_path),
    )
    ToolKnowledgeBootstrap().bootstrap(kernel)
    ToolCurriculumBootstrap().bootstrap(kernel)
    CraftCurriculumBootstrap().bootstrap(kernel)
    return kernel
