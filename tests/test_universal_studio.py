import pytest

from pydantic import ValidationError

from cinefactory.production.intent import BackendKind, ProductionIntentRouter, WorkflowFamily, WorldTarget
from cinefactory.studio.blackboard import ArtifactPermissionError, StudioBlackboard
from cinefactory.studio.capabilities import CapabilityProvider, CapabilityRegistry, TechnicalDirector
from cinefactory.studio.contracts import ArtifactProvenance, CapabilityKind, CapabilityStatus
from cinefactory.studio.contracts import DepartmentId, KnowledgeScope, MediaFormat, SkillEvaluation, SkillManifest, StudioProject
from cinefactory.studio.departments import default_department_registry
from cinefactory.studio.entities import EntityKind, EntityRegistry, EntityRepresentation, PersistentEntity
from cinefactory.studio.evidence import ClaimRecord, EvidenceMap, EvidenceSource, SourceTier
from cinefactory.studio.format_director import FormatDirector
from cinefactory.studio.learning import LearningPolicy, LearningRecord, LearningState
from cinefactory.studio.segments import MediaSegment, SegmentGraph, SegmentRequirement
from cinefactory.studio.skills import SkillPromotionError, SkillRegistry

def test_tutorial_is_not_forced_into_story():
    project = StudioProject(goal="Teach Blender", media_format=MediaFormat.TUTORIAL)
    assert project.story_required is False


def test_documentary_requires_evidence():
    project = StudioProject(goal="Document a topic", media_format=MediaFormat.DOCUMENTARY)
    assert project.evidence_required is True


def test_gameplay_requires_actual_gameplay():
    project = StudioProject(goal="Minecraft challenge", media_format=MediaFormat.GAMEPLAY)
    assert project.actual_gameplay_required is True


def test_format_director_uses_non_scene_segments():
    project = StudioProject(goal="Teach a tool", media_format=MediaFormat.TUTORIAL)
    graph = FormatDirector().compile_outline(project)
    assert graph.segments
    assert all(item.kind.value == "TUTORIAL_STEP" for item in graph.segments)

def test_segment_graph_rejects_cycle():
    a = MediaSegment(segment_id="A", kind="NARRATIVE_SCENE", purpose="first", dependencies=["B"])
    b = MediaSegment(segment_id="B", kind="NARRATIVE_SCENE", purpose="second", dependencies=["A"])
    with pytest.raises(ValidationError):
        SegmentGraph(segments=[a, b])


def test_capability_router_fails_closed():
    registry = CapabilityRegistry()
    director = TechnicalDirector(registry)
    segment = MediaSegment(
        segment_id="SEG_GAME",
        kind="GAMEPLAY_BEAT",
        purpose="play actual game",
        requirements=[SegmentRequirement(capability=CapabilityKind.GAME_RUNTIME)],
    )
    plans, findings = director.compile_segment(segment)
    assert plans == []
    assert findings == ["SEG_GAME:NO_EXECUTABLE_PROVIDER:GAME_RUNTIME"]


def test_planned_provider_is_not_selected():
    registry = CapabilityRegistry()
    registry.register(CapabilityProvider(provider_id="game.planned", kind=CapabilityKind.GAME_RUNTIME, status=CapabilityStatus.PLANNED, executable=False, commercial_safe=True))
    director = TechnicalDirector(registry)
    need = SegmentRequirement(capability=CapabilityKind.GAME_RUNTIME)
    assert director.choose(need)[0] is None

def test_blackboard_enforces_owner(tmp_path):
    board = StudioBlackboard(tmp_path)
    provenance = ArtifactProvenance(producer="test")
    with pytest.raises(ArtifactPermissionError):
        board.write("P1", "SCRIPT", DepartmentId.DIRECTION, DepartmentId.WRITERS_ROOM, {"x": 1}, provenance)


def test_blackboard_version_and_lock(tmp_path):
    board = StudioBlackboard(tmp_path)
    provenance = ArtifactProvenance(producer="writer")
    first = board.write("P1", "SCRIPT", DepartmentId.WRITERS_ROOM, DepartmentId.WRITERS_ROOM, {"draft": 1}, provenance)
    assert first.version == 1
    locked = board.lock("P1", "SCRIPT", DepartmentId.WRITERS_ROOM)
    assert locked.state.value == "LOCKED"
    second = board.revise("P1", "SCRIPT", DepartmentId.WRITERS_ROOM, {"draft": 2}, provenance)
    assert second.version == 2
    assert board.payload(second) == {"draft": 2}


def test_department_registry_contains_professional_roles():
    registry = default_department_registry()
    assert registry.get(DepartmentId.DIRECTION).craft_skills
    assert "no shot without purpose" in registry.get(DepartmentId.CINEMATOGRAPHY).rules
    assert registry.get(DepartmentId.RD_KNOWLEDGE).quality_gates

def test_skill_cannot_execute_before_promotion(tmp_path):
    registry = SkillRegistry(tmp_path)
    manifest = SkillManifest(skill_id="editing.dialogue", owner=DepartmentId.EDITORIAL, description="Dialogue editing", commercial_safe=True, code_execution_allowed=True)
    registry.register(manifest)
    assert registry.can_execute("editing.dialogue") is False
    registry.record_evaluation(SkillEvaluation(skill_id="editing.dialogue", passed=True, score=0.9))
    registry.validate_skill("editing.dialogue")
    registry.promote_production("editing.dialogue")
    assert registry.can_execute("editing.dialogue") is True


def test_skill_commercial_unknown_blocks_promotion(tmp_path):
    registry = SkillRegistry(tmp_path)
    manifest = SkillManifest(skill_id="external.model", owner=DepartmentId.GENERATIVE_MEDIA, description="External model", commercial_safe=None, code_execution_allowed=True)
    registry.register(manifest)
    registry.record_evaluation(SkillEvaluation(skill_id="external.model", passed=True, score=0.95))
    registry.validate_skill("external.model")
    with pytest.raises(SkillPromotionError):
        registry.promote_production("external.model", commercial_project=True)


def test_evidence_map_rejects_unknown_source():
    claim = ClaimRecord(text="A factual claim", source_ids=["MISSING"])
    with pytest.raises(ValidationError):
        EvidenceMap(claims=[claim])

def test_studio_learning_needs_multiple_projects():
    record = LearningRecord(
        scope=KnowledgeScope.STUDIO,
        state=LearningState.EVALUATED,
        subject="camera rule",
        observation="worked once",
        evidence=["metric"],
        confidence=0.95,
        source_project_ids=["P1"],
    )
    passed, findings = LearningPolicy.can_promote(record)
    assert passed is False
    assert "STUDIO_RULE_REQUIRES_MULTIPLE_PROJECTS" in findings


def test_production_intent_minecraft_gameplay_fails_closed():
    intent = ProductionIntentRouter().route("Minecraft 100 days gameplay")
    assert intent.workflow_family is WorkflowFamily.GAMEPLAY
    assert intent.world is WorldTarget.MINECRAFT
    assert intent.backend is BackendKind.MINECRAFT_RUNTIME
    assert intent.executable is False
    assert intent.warnings == ["BACKEND_NOT_YET_EXECUTABLE:MINECRAFT_RUNTIME"]


def test_word_craft_does_not_mean_minecraft():
    intent = ProductionIntentRouter().route("A craft documentary about woodworking")
    assert intent.world is WorldTarget.NONE

def test_persistent_entity_supports_multiple_backends():
    entity = PersistentEntity(
        entity_id="HERO",
        kind=EntityKind.CHARACTER,
        canonical_name="Hero",
        identity_lock="same actor identity",
        representations=[
            EntityRepresentation(representation_id="BLEND", backend="blender", asset_ref="hero.blend"),
            EntityRepresentation(representation_id="MC", backend="minecraft", asset_ref="hero.png"),
        ],
    )
    registry = EntityRegistry(entities=[entity])
    assert registry.entities[0].entity_id == "HERO"
    assert len(registry.entities[0].representations) == 2


def test_entity_registry_rejects_duplicate_ids():
    one = PersistentEntity(entity_id="X", kind=EntityKind.PROP, canonical_name="One", identity_lock="stable")
    two = PersistentEntity(entity_id="X", kind=EntityKind.PROP, canonical_name="Two", identity_lock="stable")
    with pytest.raises(ValidationError):
        EntityRegistry(entities=[one, two])
