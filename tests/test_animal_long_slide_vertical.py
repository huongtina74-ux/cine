from __future__ import annotations

from pathlib import Path

from cinefactory.animal_long_slide import (
    AssetFoundry,
    AssetKind,
    AssetManifest,
    LicenseState,
    LongSlideAssetGate,
    LongSlideAssetRegistry,
    LongSlideAssetQualifier,
    LongSlideEpisodePlanner,
    LongSlideExecutionPlanner,
    LongSlideProducer,
    LongSlideQC,
    MotionCompatibilityGraph,
    MotionProfile,
    QualificationState,
    SceneCompatibilityGate,
    SemanticNoveltyScorer,
    SkeletonFamily,
)
from cinefactory.qc.visual_command import VisualQCResponse
from cinefactory.appctx import build_context
from cinefactory.studio.company import CompanyOrchestrator
from cinefactory.studio.contracts import MediaFormat, StudioProjectSpec
from cinefactory.studio.format_director import UniversalMediaClassifier
from cinefactory.studio.long_slide_adapter import LongSlideCompanyAdapter


ROOT = Path(__file__).resolve().parents[1]


def test_classifier_recognizes_long_slide_as_procedural_animation():
    product = UniversalMediaClassifier().classify(
        "Make a Long Slide Game with elephant tiger gorilla and funny 3D animals"
    )
    assert product.format is MediaFormat.ANIMATION
    assert product.actual_gameplay_required is False
    assert product.story_required is False
    assert product.constraints["domain"] == "animation.animal_long_slide"
    assert product.constraints["vertical"] == "animal_long_slide"
    assert product.constraints["dialogue_required"] is False


def test_company_blueprint_uses_long_slide_pack_without_dialogue_lock():
    runtime = build_context(ROOT)
    project = StudioProjectSpec(
        prompt="Animal Fountain Crossing Long Slide animation with elephant and tiger",
        duration_seconds=120,
        language="en",
    )
    blueprint = CompanyOrchestrator(runtime.studio).build_blueprint(project)

    assert blueprint.studio_plan.product.format is MediaFormat.ANIMATION
    assert blueprint.packs.domain_pack is not None
    assert blueprint.packs.domain_pack.pack_id == "domain.animation.animal_long_slide"
    assert blueprint.packs.execution_pack is not None
    assert blueprint.packs.execution_pack.pack_id == "execution.offline3d"

    voice_stage = next(s for s in blueprint.stages if s.stage_id == "VOICE_PREP")
    assert voice_stage.required is False
    assert any(s.stage_id == "DIRECTION" for s in blueprint.stages)
    assert any(s.stage_id == "PRODUCTION_DESIGN" for s in blueprint.stages)
    assert any(s.stage_id == "CINEMATOGRAPHY" for s in blueprint.stages)


def test_long_slide_planner_is_deterministic_and_qc_clean():
    planner = LongSlideEpisodePlanner(seed=42)
    episode = planner.plan(
        project_id="STU_TEST",
        episode_id="EP_001",
        title="Original animal challenge",
        target_duration_seconds=180,
        animals=["elephant", "tiger", "gorilla", "cow"],
    )
    same = LongSlideEpisodePlanner(seed=42).plan(
        project_id="STU_TEST",
        episode_id="EP_001",
        title="Original animal challenge",
        target_duration_seconds=180,
        animals=["elephant", "tiger", "gorilla", "cow"],
    )

    assert episode.originality_signature == same.originality_signature
    assert abs(episode.planned_duration_seconds - 180) < 0.01
    assert len(episode.modules) >= 4
    assert all(
        a.animal_id != b.animal_id
        for a, b in zip(episode.modules, episode.modules[1:])
    )
    assert all(module.camera_beats for module in episode.modules)
    assert all(module.events for module in episode.modules)
    assert LongSlideQC().review(episode).passed is True


def test_long_slide_seed_changes_originality_signature():
    kwargs = dict(
        project_id="STU_TEST",
        episode_id="EP_001",
        title="Variation",
        target_duration_seconds=120,
        animals=["elephant", "tiger", "gorilla"],
    )
    a = LongSlideEpisodePlanner(seed=1).plan(**kwargs)
    b = LongSlideEpisodePlanner(seed=2).plan(**kwargs)
    assert a.originality_signature != b.originality_signature


def test_asset_gate_blocks_unlicensed_or_unready_assets():
    blocked = AssetManifest(
        asset_id="external_elephant",
        kind=AssetKind.ANIMAL,
        license_state=LicenseState.UNKNOWN,
        commercial_use=False,
        production_ready=False,
    )
    approved = AssetManifest(
        asset_id="owned_slide",
        kind=AssetKind.SCENE,
        license_state=LicenseState.APPROVED,
        commercial_use=True,
        production_ready=True,
        technical_qc_passed=True,
        visual_qc_passed=True,
    )
    assert LongSlideAssetGate.blockers([blocked, approved]) == [
        "external_elephant: asset not production-safe"
    ]
    assert LongSlideAssetGate.blockers([approved]) == []


def test_company_adapter_plans_vertical_episode():
    project = StudioProjectSpec(
        prompt="Long Slide 3D animal game",
        duration_seconds=90,
    )
    adapter = LongSlideCompanyAdapter()
    assert adapter.matches(project)
    episode = adapter.plan_episode(
        project,
        seed=7,
        animals=["cow", "tiger", "elephant"],
    )
    assert episode.metadata["vertical"] == "animal_long_slide"
    assert episode.planned_duration_seconds == 90


def test_execution_plan_fails_closed_when_assets_are_missing(tmp_path):
    episode = LongSlideEpisodePlanner(seed=3).plan(
        project_id="STU_TEST",
        episode_id="EP_ASSETS",
        title="Asset gate",
        target_duration_seconds=60,
        animals=["cow", "tiger"],
    )
    plan = LongSlideExecutionPlanner(LongSlideAssetRegistry()).plan(
        episode,
        output_dir=tmp_path / "renders",
    )
    assert plan.executable is False
    assert plan.jobs
    assert any(item.startswith("MISSING_ASSET:animal.") for item in plan.blockers)
    assert any(item.startswith("MISSING_ASSET:scene.") for item in plan.blockers)


def test_execution_plan_unlocks_when_every_required_asset_is_approved(tmp_path):
    episode = LongSlideEpisodePlanner(seed=5).plan(
        project_id="STU_TEST",
        episode_id="EP_READY",
        title="Ready pack",
        target_duration_seconds=60,
        animals=["cow", "horse"],
    )
    required = set()
    for module in episode.modules:
        required.update(LongSlideExecutionPlanner.required_assets(module))

    assets = []
    for asset_id in sorted(required):
        prefix = asset_id.split(".", 1)[0]
        kind = {
            "animal": AssetKind.ANIMAL,
            "scene": AssetKind.SCENE,
            "obstacle": AssetKind.OBSTACLE,
            "animation": AssetKind.ANIMATION,
        }[prefix]
        assets.append(
            AssetManifest(
                asset_id=asset_id,
                kind=kind,
                license_state=LicenseState.APPROVED,
                commercial_use=True,
                production_ready=True,
                technical_qc_passed=True,
                visual_qc_passed=True,
            )
        )

    motions = MotionCompatibilityGraph([
        MotionProfile(
            motion_id="motion.test.hoofed.run",
            semantic_action="run",
            skeleton_family=SkeletonFamily.HOOFED,
            preview_ready=True,
            production_ready=True,
        ),
    ])
    plan = LongSlideExecutionPlanner(
        LongSlideAssetRegistry(assets),
        motions,
    ).plan(
        episode,
        output_dir=tmp_path / "renders",
        width=640,
        height=360,
        fps=24,
    )
    assert plan.executable is True
    assert plan.blockers == []
    assert len(plan.jobs) == len(episode.modules)
    assert all(job.width == 640 and job.height == 360 for job in plan.jobs)


def test_source_pack_registry_contains_vetted_cc0_sources():
    packs = AssetFoundry.load_source_packs(ROOT)
    by_id = {pack.pack_id: pack for pack in packs}
    vetted = {
        "quaternius.ultimate_animated_animals",
        "quaternius.farm_animals",
        "gobkit.animal_pack",
        "gobkit.dino_pack",
        "kenney.prototype_kit",
    }
    assert vetted <= set(by_id)
    assert all(
        by_id[pack_id].license_state is LicenseState.APPROVED
        and by_id[pack_id].commercial_use is True
        for pack_id in vetted
    )
    assert by_id["fab.animated_animals_mega"].license_state is LicenseState.UNKNOWN
    assert by_id["fab.animated_animals_mega"].commercial_use is False


def test_internal_bootstrap_assets_are_registered_but_fail_closed():
    registry = LongSlideAssetRegistry.load(ROOT)
    scene = registry.get("scene.long_slide")
    hammer = registry.get("obstacle.rotating_hammer")
    assert scene.license_state is LicenseState.APPROVED
    assert scene.commercial_use is True
    assert scene.technical_qc_passed is True
    assert scene.visual_qc_passed is False
    assert scene.production_ready is False
    assert registry.resolve_local_path(ROOT, scene).is_file()
    assert registry.resolve_local_path(ROOT, hammer).is_file()


def test_planner_only_uses_scene_compatible_obstacles():
    episode = LongSlideEpisodePlanner(seed=19).plan(
        project_id="STU_COMPAT",
        episode_id="EP_COMPAT",
        title="Compatibility",
        target_duration_seconds=360,
        animals=["cow", "tiger", "gorilla"],
    )
    assert all(
        SceneCompatibilityGate.findings(module) == []
        for module in episode.modules
    )


def test_motion_graph_resolves_by_skeleton_family():
    graph = MotionCompatibilityGraph([
        MotionProfile(
            motion_id="motion.run.hoofed.v1",
            semantic_action="run",
            skeleton_family=SkeletonFamily.HOOFED,
            loopable=True,
            foot_contact_validated=True,
            production_ready=True,
        ),
        MotionProfile(
            motion_id="motion.run.feline.v1",
            semantic_action="run",
            skeleton_family=SkeletonFamily.FELINE,
            loopable=True,
            foot_contact_validated=True,
            production_ready=True,
        ),
    ])
    assert graph.resolve("cow", "run").motion_id == "motion.run.hoofed.v1"
    assert graph.resolve("tiger", "run").motion_id == "motion.run.feline.v1"


def test_semantic_novelty_ignores_seed_only_changes():
    a = LongSlideEpisodePlanner(seed=11).plan(
        project_id="STU_NOVEL",
        episode_id="A",
        title="Novelty",
        target_duration_seconds=90,
        animals=["cow", "tiger", "gorilla"],
    )
    modules = [
        item.model_copy(update={"seed": item.seed + 999})
        for item in a.modules
    ]
    b = a.model_copy(
        update={
            "episode_id": "B",
            "modules": modules,
            "originality_signature": a.signature_for(modules),
        }
    )
    assert a.originality_signature == b.originality_signature
    assert SemanticNoveltyScorer.similarity(a, b) == 1.0


def test_real_asset_catalog_exposes_preview_ready_animals():
    registry = LongSlideAssetRegistry.load(ROOT)
    animals = set(registry.animal_ids(preview=True))
    assert {"cow", "horse", "hippo", "duck", "dinosaur", "buffalo"} <= animals
    assert "gorilla" not in animals


def test_real_motion_catalog_resolves_preview_locomotion_and_blocks_missing():
    motions = MotionCompatibilityGraph.load(ROOT)
    cow = motions.resolve_sequence("cow", ["idle", "run", "slide"], render_preview=True)
    duck = motions.resolve_sequence("duck", ["idle", "run", "impact"], render_preview=True)
    hippo = motions.resolve_sequence("hippo", ["idle", "run"], render_preview=True)
    elephant = motions.resolve_sequence("elephant", ["idle", "run"], render_preview=True)
    assert cow.executable is True
    assert duck.executable is True
    assert hippo.executable is False
    assert any(item.method.value == "PROCEDURAL" for item in cow.resolved)
    assert any("MISSING_MOTION:animal.hippo:run" in x for x in hippo.blockers)
    assert elephant.executable is False
    assert any("MISSING_MOTION:animal.elephant:run" in x for x in elephant.blockers)


def test_real_catalog_can_compile_preview_episode_but_not_final_yet(tmp_path):
    registry = LongSlideAssetRegistry.load(ROOT)
    motions = MotionCompatibilityGraph.load(ROOT)
    episode = LongSlideEpisodePlanner(seed=23).plan(
        project_id="STU_REAL_PREVIEW",
        episode_id="EP_REAL_PREVIEW",
        title="Real asset pilot",
        target_duration_seconds=90,
        animals=["cow", "duck"],
    )
    preview = LongSlideExecutionPlanner(registry, motions).plan(
        episode,
        output_dir=tmp_path / "preview",
        render_preview=True,
    )
    final = LongSlideExecutionPlanner(registry, motions).plan(
        episode,
        output_dir=tmp_path / "final",
        render_preview=False,
    )
    assert preview.executable is True, preview.blockers
    assert all(job.resolved_motions for job in preview.jobs)
    assert final.executable is False
    assert any(item.startswith("UNQUALIFIED_ASSET:") for item in final.blockers)



def test_planner_can_match_company_shot_count():
    episode = LongSlideEpisodePlanner(seed=31).plan(
        project_id="STU_SHOT_MAP",
        episode_id="EP_SHOT_MAP",
        title="Shot mapping",
        target_duration_seconds=24,
        animals=["cow", "horse"],
        module_count=3,
    )
    assert len(episode.modules) == 3
    assert all(abs(item.duration_seconds - 8.0) < 0.001 for item in episode.modules)
    assert abs(episode.planned_duration_seconds - 24.0) < 0.001


def test_long_slide_producer_preserves_company_shot_ids(tmp_path):
    episode = LongSlideEpisodePlanner(seed=37).plan(
        project_id="STU_PRODUCER",
        episode_id="EP_PRODUCER",
        title="Producer mapping",
        target_duration_seconds=16,
        animals=["cow", "horse"],
        module_count=2,
    )
    required = set()
    for module in episode.modules:
        required.update(LongSlideExecutionPlanner.required_assets(module))

    assets = []
    for asset_id in sorted(required):
        prefix = asset_id.split(".", 1)[0]
        kind = {
            "animal": AssetKind.ANIMAL,
            "scene": AssetKind.SCENE,
            "obstacle": AssetKind.OBSTACLE,
        }[prefix]
        assets.append(
            AssetManifest(
                asset_id=asset_id,
                kind=kind,
                license_state=LicenseState.APPROVED,
                commercial_use=True,
                production_ready=True,
                technical_qc_passed=True,
                visual_qc_passed=True,
            )
        )

    motions = MotionCompatibilityGraph([
        MotionProfile(
            motion_id="motion.test.hoofed.run",
            semantic_action="run",
            skeleton_family=SkeletonFamily.HOOFED,
            preview_ready=True,
            production_ready=True,
        ),
    ])
    plan = LongSlideExecutionPlanner(
        LongSlideAssetRegistry(assets),
        motions,
    ).plan(
        episode,
        output_dir=tmp_path / "renders",
        width=320,
        height=180,
        fps=24,
    )
    assert plan.executable is True, plan.blockers

    class FakeBinder:
        def execute(self, job, *, timeout_seconds=900):
            path = Path(job.output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"x" * 2048)
            return path

    dailies = LongSlideProducer(
        ROOT,
        blender_executable="unused",
        binder=FakeBinder(),
    ).produce(
        plan,
        company_shot_ids=["SHOT_A", "SHOT_B"],
    )
    assert dailies.passed is True
    assert [item.shot_id for item in dailies.shots] == [
        "SHOT_A",
        "SHOT_B",
    ]
    assert all(item.selected_path for item in dailies.shots)



def test_execution_blocks_source_action_from_wrong_animal_binary(tmp_path):
    animal_path = tmp_path / "canonical_cow.blend"
    motion_path = tmp_path / "other_cow.blend"
    scene_path = tmp_path / "scene.blend"
    obstacle_path = tmp_path / "obstacle.blend"
    for path in (animal_path, motion_path, scene_path, obstacle_path):
        path.write_bytes(b"x" * 2048)

    episode = LongSlideEpisodePlanner(seed=41).plan(
        project_id="STU_MOTION_SOURCE",
        episode_id="EP_MOTION_SOURCE",
        title="Motion source gate",
        target_duration_seconds=16,
        animals=["cow", "horse"],
        module_count=2,
    )
    first = episode.modules[0].model_copy(
        update={
            "animal_id": "cow",
            "scene_kind": episode.modules[0].scene_kind,
            "obstacles": [],
            "animation_sequence": ["run"],
        }
    )
    episode = episode.model_copy(
        update={
            "modules": [first],
            "target_duration_seconds": first.duration_seconds,
            "originality_signature": episode.signature_for([first]),
        }
    )
    scene_id = f"scene.{first.scene_kind.value.lower()}"
    registry = LongSlideAssetRegistry(
        [
            AssetManifest(
                asset_id="animal.cow",
                kind=AssetKind.ANIMAL,
                license_state=LicenseState.APPROVED,
                commercial_use=True,
                production_ready=True,
                technical_qc_passed=True,
                visual_qc_passed=True,
                local_path=str(animal_path),
            ),
            AssetManifest(
                asset_id=scene_id,
                kind=AssetKind.SCENE,
                license_state=LicenseState.APPROVED,
                commercial_use=True,
                production_ready=True,
                technical_qc_passed=True,
                visual_qc_passed=True,
                local_path=str(scene_path),
            ),
        ],
        root=tmp_path,
    )
    motions = MotionCompatibilityGraph(
        [
            MotionProfile(
                motion_id="motion.cow.run.wrong_source",
                semantic_action="run",
                skeleton_family=SkeletonFamily.HOOFED,
                animal_id="cow",
                local_path=str(motion_path),
                source_action="Run",
                preview_ready=True,
                production_ready=True,
            )
        ]
    )
    plan = LongSlideExecutionPlanner(registry, motions).plan(
        episode,
        output_dir=tmp_path / "renders",
    )
    assert plan.executable is False
    assert any(
        item.startswith("MOTION_SOURCE_ASSET_MISMATCH:animal.cow:run")
        for item in plan.blockers
    )



def test_asset_qualifier_waits_for_semantic_review(tmp_path):
    asset_file = tmp_path / "scene.blend"
    preview = tmp_path / "scene.png"
    asset_file.write_bytes(b"x" * 2048)
    preview.write_bytes(b"p" * 2048)
    asset = AssetManifest(
        asset_id="scene.test",
        kind=AssetKind.SCENE,
        license_state=LicenseState.APPROVED,
        commercial_use=True,
        local_path=str(asset_file),
        content_sha256="abc123",
        technical_qc_passed=True,
        visual_qc_passed=False,
        production_ready=False,
    )
    qualifier = LongSlideAssetQualifier(
        LongSlideAssetRegistry([asset], root=tmp_path),
    )
    report = qualifier.qualify("scene.test", preview_path=preview)
    assert report.state is QualificationState.AWAITING_VISUAL_REVIEW
    assert report.deterministic_passed is True
    assert report.promotable is False
    assert "SEMANTIC_VISUAL_REVIEW_REQUIRED" in report.blockers


def test_asset_qualifier_promotes_only_after_visual_pass(tmp_path):
    asset_file = tmp_path / "obstacle.blend"
    preview = tmp_path / "obstacle.png"
    asset_file.write_bytes(b"x" * 2048)
    preview.write_bytes(b"p" * 2048)
    asset = AssetManifest(
        asset_id="obstacle.test",
        kind=AssetKind.OBSTACLE,
        license_state=LicenseState.APPROVED,
        commercial_use=True,
        local_path=str(asset_file),
        content_sha256="def456",
        technical_qc_passed=True,
        visual_qc_passed=False,
        production_ready=False,
    )

    class PassingReviewer:
        def review(self, media_path, contract):
            assert Path(media_path) == preview
            assert contract["asset_id"] == "obstacle.test"
            return VisualQCResponse(
                passed=True,
                identity_score=0.90,
                continuity_score=0.88,
                performance_score=0.92,
                camera_score=0.86,
                findings=[],
            )

    qualifier = LongSlideAssetQualifier(
        LongSlideAssetRegistry([asset], root=tmp_path),
        reviewer=PassingReviewer(),
        min_visual_score=0.80,
    )
    report = qualifier.qualify("obstacle.test", preview_path=preview)
    assert report.state is QualificationState.QUALIFIED
    assert report.promotable is True
    promoted = qualifier.promoted_manifest("obstacle.test", report)
    assert promoted.visual_qc_passed is True
    assert promoted.production_ready is True


def test_animal_qualifier_blocks_before_visual_review_when_locomotion_missing(tmp_path):
    asset_file = tmp_path / "elephant.blend"
    preview = tmp_path / "elephant.png"
    asset_file.write_bytes(b"x" * 2048)
    preview.write_bytes(b"p" * 2048)
    asset = AssetManifest(
        asset_id="animal.elephant",
        kind=AssetKind.ANIMAL,
        license_state=LicenseState.APPROVED,
        commercial_use=True,
        local_path=str(asset_file),
        content_sha256="elephant123",
        technical_qc_passed=True,
        rig_profile="test.elephant",
        visual_qc_passed=False,
        production_ready=False,
    )

    class ReviewerMustNotRun:
        def review(self, media_path, contract):
            raise AssertionError("visual reviewer should not run before deterministic gates pass")

    qualifier = LongSlideAssetQualifier(
        LongSlideAssetRegistry([asset], root=tmp_path),
        motions=MotionCompatibilityGraph(),
        reviewer=ReviewerMustNotRun(),
    )
    report = qualifier.qualify("animal.elephant", preview_path=preview)
    assert report.state is QualificationState.BLOCKED
    assert report.visual_reviewed is False
    assert any(
        blocker.startswith("MISSING_MOTION:animal.elephant:run")
        for blocker in report.blockers
    )
