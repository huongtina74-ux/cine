from __future__ import annotations

import pytest

from cinefactory.studio import (
    ArtifactLockedError,
    BlackboardPermissionError,
    CapabilityRegistry,
    EntityKind,
    EntityRegistry,
    EntityRepresentation,
    FormatDirector,
    KnowledgeGate,
    KnowledgeItem,
    KnowledgeKind,
    PersistentEntity,
    ProductionCompiler,
    QualityProfileRegistry,
    RootCauseEngine,
    SegmentDAG,
    SkillCompiler,
    SkillPromotionError,
    SkillRegistry,
    SourceTier,
    StudioBlackboard,
    StudioControlPlane,
    UniversalMediaClassifier,
)
from cinefactory.studio.contracts import (
    ArtifactState,
    CapabilityKind,
    CapabilityRequirement,
    DepartmentId,
    KnowledgeScope,
    LearningCandidate,
    MediaFormat,
    MediaPurpose,
    MediaSegment,
    SegmentKind,
    SkillEvaluation,
    SkillManifest,
    SkillStatus,
    StudioProjectSpec,
)
def test_blackboard_enforces_ownership_and_lock(tmp_path):
    board = StudioBlackboard(tmp_path)
    meta = board.put(
        "P1", "script", DepartmentId.WRITERS_ROOM, {"text": "draft"}
    )
    assert meta.version == 1
    with pytest.raises(BlackboardPermissionError):
        board.put(
            "P1", "script", DepartmentId.WRITERS_ROOM, {"text": "bad"},
            actor=DepartmentId.EDITORIAL,
        )
    board.lock("P1", "script", actor=DepartmentId.WRITERS_ROOM)
    with pytest.raises(ArtifactLockedError):
        board.put("P1", "script", DepartmentId.WRITERS_ROOM, {"text": "overwrite"})


def test_locked_artifact_revision_preserves_lineage(tmp_path):
    board = StudioBlackboard(tmp_path)
    v1 = board.put("P1", "director_cut", DepartmentId.DIRECTION, {"a": 1})
    board.lock("P1", "director_cut", actor=DepartmentId.DIRECTION)
    v2 = board.revise_locked(
        "P1", "director_cut", DepartmentId.DIRECTION, {"a": 2},
        approved_change_id="CHG_001", upstream_artifact_ids=[v1.artifact_id],
    )
    assert v2.version == 2
    assert board.get_meta("P1", "director_cut", 1).state is ArtifactState.SUPERSEDED
def test_tutorial_is_not_forced_into_story():
    product = UniversalMediaClassifier().classify("Hướng dẫn sử dụng Blender bằng screen recording")
    assert product.format is MediaFormat.TUTORIAL
    assert product.story_required is False
    segments = FormatDirector().compile(product, duration_seconds=120)
    assert any(s.kind is SegmentKind.SCREEN_DEMO for s in segments)


def test_documentary_requires_evidence():
    product = UniversalMediaClassifier().classify("Documentary lịch sử về một thành phố")
    assert product.format is MediaFormat.DOCUMENTARY
    assert product.evidence_required is True


def test_gameplay_requires_runtime_when_prompt_says_gameplay():
    plan = StudioControlPlane().plan(
        StudioProjectSpec(prompt="Minecraft gameplay survival challenge 100 days")
    )
    assert plan.product.format is MediaFormat.GAMEPLAY
    assert plan.product.actual_gameplay_required is True
    assert any("GAME_RUNTIME" in blocker for blocker in plan.blockers)


def test_capability_registry_fails_closed_on_unverified_commercial_model():
    registry = CapabilityRegistry()
    decision = registry.route(
        CapabilityRequirement(kind=CapabilityKind.AI_VIDEO, commercial_safe=True, max_vram_gb=12)
    )
    assert decision.executable is False
    assert any("COMMERCIAL_SAFETY_UNVERIFIED" in x for x in decision.warnings)
def test_skill_cannot_reach_production_without_eval_and_regression(tmp_path):
    registry = SkillRegistry(tmp_path)
    manifest = SkillManifest(
        skill_id="editing.dialogue",
        version="1",
        owner=DepartmentId.EDITORIAL,
        status=SkillStatus.CANDIDATE,
        craft_domain="editorial",
        commercial_safe=True,
    )
    registry.register(manifest)
    with pytest.raises(SkillPromotionError):
        registry.promote("editing.dialogue", "1", SkillStatus.PRODUCTION)

    registry.record_evaluation(
        SkillEvaluation(
            skill_id="editing.dialogue",
            version="1",
            passed=True,
            score=0.95,
            eval_id="functional",
            regression_passed=True,
        )
    )
    promoted = registry.promote("editing.dialogue", "1", SkillStatus.PRODUCTION)
    assert promoted.status is SkillStatus.PRODUCTION


def test_external_executable_skill_requires_security_review(tmp_path):
    registry = SkillRegistry(tmp_path)
    registry.register(
        SkillManifest(
            skill_id="plugin.external",
            version="1",
            owner=DepartmentId.RND,
            status=SkillStatus.CANDIDATE,
            craft_domain="tooling",
            source_type="REPO",
            commercial_safe=True,
            security_reviewed=False,
        )
    )
    registry.record_evaluation(
        SkillEvaluation(
            skill_id="plugin.external", version="1", passed=True,
            score=1.0, eval_id="sandbox", regression_passed=True
        )
    )
    with pytest.raises(SkillPromotionError):
        registry.promote("plugin.external", "1", SkillStatus.PRODUCTION)
def test_learning_promotion_requires_sandbox_and_regression():
    with pytest.raises(ValueError):
        LearningCandidate(
            observation="retention improved",
            hypothesis="faster setup helps",
            scope=KnowledgeScope.CHANNEL,
            promoted=True,
        )


def test_segment_dag_rejects_cycle():
    from cinefactory.studio.production import ProductionTask

    a = ProductionTask(
        task_id="A", segment_id="S1", task_type="x", dependencies=["B"],
        capability_kind=CapabilityKind.QC, executable=True,
    )
    b = ProductionTask(
        task_id="B", segment_id="S1", task_type="x", dependencies=["A"],
        capability_kind=CapabilityKind.QC, executable=True,
    )
    with pytest.raises(ValueError, match="SEGMENT_DAG_CYCLE"):
        SegmentDAG([a, b]).topological_order()


def test_production_compiler_preserves_segment_dependency():
    segment1 = MediaSegment(
        segment_id="SEG_001", kind=SegmentKind.NARRATIVE_SCENE,
        purpose="hook", order=0, capability_requirements=[CapabilityKind.OFFLINE_3D]
    )
    segment2 = MediaSegment(
        segment_id="SEG_002", kind=SegmentKind.NARRATIVE_SCENE,
        purpose="payoff", order=1, dependencies=["SEG_001"],
        capability_requirements=[CapabilityKind.EDITORIAL]
    )
    registry = CapabilityRegistry()
    route_map = {
        "SEG_001": [registry.route(CapabilityRequirement(kind=CapabilityKind.OFFLINE_3D))],
        "SEG_002": [registry.route(CapabilityRequirement(kind=CapabilityKind.EDITORIAL))],
    }
    recipe = ProductionCompiler().compile("P1", [segment1, segment2], route_map)
    assert recipe.blocked is False
    assert len(SegmentDAG(recipe.tasks).topological_order()) == 2
def test_persistent_entity_cross_backend_identity():
    reg = EntityRegistry()
    reg.register(
        PersistentEntity(
            entity_id="ACTOR_01",
            kind=EntityKind.CHARACTER,
            canonical_name="Hero",
            identity_lock={"hair": "black", "shirt": "red"},
        )
    )
    reg.add_representation(
        "ACTOR_01",
        EntityRepresentation(representation_id="BLENDER", backend="Blender", verified=True),
    )
    reg.add_representation(
        "ACTOR_01",
        EntityRepresentation(representation_id="MINECRAFT", backend="Minecraft", verified=False),
    )
    assert len(reg.get("ACTOR_01").representations) == 2


def test_root_cause_engine_generates_testable_hypotheses():
    record = RootCauseEngine().hypotheses(
        "ANIM_001", ["character has foot sliding"], owner=DepartmentId.PERFORMANCE
    )
    assert len(record.hypotheses) >= 2
    assert all(x.test and x.expected_result for x in record.hypotheses)


def test_knowledge_gate_blocks_unverified_heuristic():
    item = KnowledgeItem(
        knowledge_id="K1",
        title="random tip",
        body="cut every 3 seconds",
        kind=KnowledgeKind.HEURISTIC,
        source_tier=SourceTier.UNVERIFIED,
        scope=KnowledgeScope.STUDIO,
        confidence=0.5,
        tested=False,
    )
    decision = KnowledgeGate.review(item)
    assert decision.promotable is False
def test_skill_compiler_accepts_verified_knowledge():
    item = KnowledgeItem(
        knowledge_id="K2",
        title="camera continuity",
        body="preserve screen direction across contiguous coverage unless axis is intentionally reset",
        kind=KnowledgeKind.CONVENTION,
        source_tier=SourceTier.TRUSTED_BOOK,
        scope=KnowledgeScope.STUDIO,
        confidence=0.9,
        tested=True,
    )
    manifest = SkillCompiler().compile_candidate(
        skill_id="camera.continuity",
        version="1",
        owner=DepartmentId.CINEMATOGRAPHY,
        craft_domain="cinematography",
        knowledge=[item],
        commercial_safe=True,
    )
    assert manifest.status is SkillStatus.CANDIDATE


def test_format_specific_qc_profiles():
    qc = QualityProfileRegistry()
    assert "GAMEPLAY_AUTHENTICITY" in qc.for_format(MediaFormat.GAMEPLAY).gates
    assert "FACT_CLAIMS" in qc.for_format(MediaFormat.DOCUMENTARY).gates
    assert "STEP_CORRECTNESS" in qc.for_format(MediaFormat.TUTORIAL).gates
