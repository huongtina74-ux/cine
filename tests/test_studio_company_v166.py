from __future__ import annotations

import pytest
from pydantic import ValidationError

from cinefactory.studio.contracts import (
    CapabilityKind,
    CapabilityRequirement,
    MediaFormat,
    StudioProjectSpec,
)
from cinefactory.studio.control_plane import StudioControlPlane
from cinefactory.studio.operations import (
    CostClass,
    CostPolicy,
    JobState,
    QueueManager,
    ResourceManager,
    ResourceSnapshot,
)
from cinefactory.studio.packs import (
    PackComposition,
    PackKind,
    StudioPack,
    default_pack_registry,
)
from cinefactory.studio.production import ProductionCompiler, ProductionTask, ProductionRecipe
from cinefactory.studio.project_pod import ProjectPodBuilder
from cinefactory.studio.rnd import ExternalToolCandidate, ExternalToolIntake, IntakeState


def test_pack_composition_merges_without_duplicates():
    a = StudioPack(pack_id="domain.a", kind=PackKind.DOMAIN, rules=["r1", "r2"])
    b = StudioPack(pack_id="genre.b", kind=PackKind.GENRE, rules=["r2", "r3"])
    c = PackComposition(domain_pack=a, genre_pack=b)
    assert c.merged_rules() == ["r1", "r2", "r3"]


def test_default_gaming_pack_guards_authenticity():
    reg = default_pack_registry()
    pack = reg.get("domain.gaming")
    assert any("fabricated gameplay" in x for x in pack.rules)
def test_project_pod_adds_evidence_for_documentary():
    pod = ProjectPodBuilder().build("P1", MediaFormat.DOCUMENTARY)
    names = {x.department.value for x in pod.roles}
    assert "EVIDENCE" in names
    assert "WRITERS_ROOM" in names


def test_project_pod_adds_runtime_operator_for_gameplay():
    pod = ProjectPodBuilder().build("P1", MediaFormat.GAMEPLAY)
    assert any(x.role_id == "runtime_operator" for x in pod.roles)


def test_queue_manager_respects_dependencies_and_resources():
    recipe = ProductionRecipe(
        project_id="P1",
        tasks=[
            ProductionTask(
                task_id="A",
                segment_id="S1",
                task_type="OFFLINE_3D",
                capability_kind=CapabilityKind.OFFLINE_3D,
                executable=True,
                resource_class="GPU",
            ),
            ProductionTask(
                task_id="B",
                segment_id="S2",
                task_type="EDITORIAL",
                dependencies=["A"],
                capability_kind=CapabilityKind.EDITORIAL,
                executable=True,
                resource_class="IO",
            ),
        ],
    )
    q = QueueManager(recipe)
    first = q.schedule(ResourceSnapshot(gpu_slots=1, io_slots=1))
    assert first.runnable_task_ids == ["A"]
    q.mark("A", JobState.SUCCEEDED)
    second = q.schedule(ResourceSnapshot(gpu_slots=1, io_slots=1))
    assert second.runnable_task_ids == ["B"]
def test_queue_manager_blocks_unexecutable_task():
    recipe = ProductionRecipe(
        project_id="P1",
        tasks=[
            ProductionTask(
                task_id="A",
                segment_id="S1",
                task_type="GAME_RUNTIME",
                capability_kind=CapabilityKind.GAME_RUNTIME,
                executable=False,
                resource_class="GPU",
            )
        ],
    )
    q = QueueManager(recipe)
    result = q.schedule(ResourceSnapshot())
    assert result.blocked_task_ids == ["A"]
    assert q.records["A"].state is JobState.BLOCKED


def test_cost_policy_defaults_to_no_paid_api():
    rm = ResourceManager()
    allowed, reason = rm.authorize_cost(CostClass.PAID_API, estimated_usd=0.01)
    assert allowed is False
    assert reason == "COST_CLASS_NOT_ALLOWED:PAID_API"


def test_external_tool_cannot_be_approved_without_gates():
    with pytest.raises(ValidationError):
        ExternalToolCandidate(
            candidate_id="R1",
            name="random repo",
            source_uri="https://example",
            source_type="REPO",
            state=IntakeState.APPROVED,
        )
def test_external_tool_intake_advances_in_order():
    intake = ExternalToolIntake()
    c = ExternalToolCandidate(
        candidate_id="R1",
        name="tool",
        source_uri="https://example",
        source_type="REPO",
    )
    assert intake.advance(c).state is IntakeState.LICENSE_REVIEW
    c.commercial_use_known = True
    c.commercial_use_allowed = True
    assert intake.advance(c).state is IntakeState.SECURITY_REVIEW
    c.security_reviewed = True
    assert intake.advance(c).state is IntakeState.SANDBOX
    c.sandbox_passed = True
    assert intake.advance(c).state is IntakeState.BENCHMARK
    c.benchmark_passed = True
    assert intake.advance(c).state is IntakeState.ADAPTER
    c.regression_passed = True
    assert intake.advance(c).state is IntakeState.APPROVED


def test_studio_control_and_compiler_form_valid_recipe_for_simple_animation():
    project = StudioProjectSpec(prompt="Create an animated cinematic short", duration_seconds=60)
    control = StudioControlPlane()
    plan = control.plan(project)
    route_map = {item.segment.segment_id: item.routes for item in plan.segments}
    recipe = ProductionCompiler().compile(
        project.studio_project_id,
        [item.segment for item in plan.segments],
        route_map,
    )
    assert recipe.tasks
    assert all(task.segment_id for task in recipe.tasks)
