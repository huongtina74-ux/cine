from __future__ import annotations

import runpy
from pathlib import Path

from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.block_animation.rendered_frame_qc import (
    ActorAppearanceEvidence,
)
from cinefactory.studio.character_factory import (
    CharacterBackendId,
    CharacterFactory,
    CharacterFactoryStore,
    CharacterReferencePack,
)

ROOT = Path(__file__).resolve().parents[1]


def _evidence(
    actor_id: str,
    *,
    bin_index: int,
    rgb: list[float],
    ahash64: str,
) -> ActorAppearanceEvidence:
    hist = [0.0] * 48
    hist[bin_index] = 1.0
    return ActorAppearanceEvidence(
        actor_id=actor_id,
        screen_box={
            "x0": 0.3,
            "y0": 0.2,
            "x1": 0.7,
            "y1": 0.8,
            "area": 0.24,
        },
        crop_width=40,
        crop_height=60,
        luma_mean=sum(rgb) / 3,
        saturation_mean=0.4,
        rgb_mean=rgb,
        hsv_histogram=hist,
        ahash64=ahash64,
    )


def test_bootstrap_creates_global_minecraft_and_roblox_identity(tmp_path):
    factory = CharacterFactory(
        ROOT,
        store=CharacterFactoryStore(tmp_path / "cf"),
    )
    mc = factory.record_for_rig("mc_a")
    r6 = factory.record_for_rig("r6_a")

    assert mc.global_character_id == "CHAR_MC_A"
    assert r6.global_character_id == "CHAR_R6_A"
    assert mc.immutable_traits["hair"] == "blue"
    assert r6.immutable_traits["clothing"] == (
        "orange_jacket_navy_pants"
    )
    assert {
        item.backend_id for item in mc.bindings
    } >= {
        CharacterBackendId.BLENDER_BLOCK,
        CharacterBackendId.MINECRAFT_RUNTIME,
        CharacterBackendId.WAN21,
    }
    assert {
        item.backend_id for item in r6.bindings
    } >= {
        CharacterBackendId.BLENDER_BLOCK,
        CharacterBackendId.ROBLOX_STUDIO_R6,
        CharacterBackendId.WAN21,
    }


def test_capture_actor_reference_from_real_blender_sidecar(tmp_path):
    factory = CharacterFactory(
        ROOT,
        store=CharacterFactoryStore(tmp_path / "cf"),
    )
    source = (
        ROOT
        / "data"
        / "verification"
        / "v179_candidate_promotion"
        / "cycles_matrix"
        / "S01.cycles.golden.mp4"
    )
    pack = factory.capture_reference_from_render(
        source_media=source,
        actor_id="A",
        rig_id="mc_a",
    )
    assert pack.global_character_id == "CHAR_MC_A"
    assert pack.evidence.actor_id == "A"
    assert Path(pack.crop_path).is_file()
    assert pack.screen_box["area"] > 0
    assert (
        factory.store.get_record("CHAR_MC_A")
        .reference_ids
    )


def test_character_state_is_versioned_not_overwritten(tmp_path):
    factory = CharacterFactory(
        ROOT,
        store=CharacterFactoryStore(tmp_path / "cf"),
    )
    before = factory.record_for_rig("r6_a")
    updated = factory.update_state(
        before.global_character_id,
        costume_id="winter_jacket_v2",
        accessories=["glasses", "backpack"],
        notes=["SCENE_CHANGE_APPROVED"],
    )
    assert len(updated.state_versions) == 2
    assert updated.current_state.version == 2
    assert updated.current_state.costume_id == "winter_jacket_v2"
    assert updated.state_versions[0].costume_id != (
        updated.current_state.costume_id
    )


def test_actor_identity_collision_is_detected(tmp_path):
    store = CharacterFactoryStore(tmp_path / "cf")
    factory = CharacterFactory(ROOT, store=store)

    a = factory.record_for_rig("mc_a")
    b = factory.record_for_rig("mc_b")
    ev_a = _evidence(
        "A",
        bin_index=0,
        rgb=[0.05, 0.05, 0.05],
        ahash64="0000000000000000",
    )
    ev_b = _evidence(
        "B",
        bin_index=47,
        rgb=[0.95, 0.95, 0.95],
        ahash64="ffffffffffffffff",
    )
    for record, actor_id, ref_id, evidence in (
        (a, "A", "REF_A", ev_a),
        (b, "B", "REF_B", ev_b),
    ):
        store.save_reference(
            CharacterReferencePack(
                reference_id=ref_id,
                global_character_id=record.global_character_id,
                actor_id=actor_id,
                rig_id=record.display_name,
                backend_id=CharacterBackendId.BLENDER_BLOCK,
                source_media_path="synthetic.mp4",
                source_media_sha256="0" * 64,
                crop_path="synthetic.png",
                crop_sha256="1" * 64,
                screen_box=evidence.screen_box,
                evidence=evidence,
            )
        )

    report = factory.evaluate_output(
        actor_reference_ids={
            "A": "REF_A",
            "B": "REF_B",
        },
        global_character_ids={
            "A": a.global_character_id,
            "B": b.global_character_id,
        },
        current_actors={
            "A": ev_b.model_copy(
                update={"actor_id": "A"}
            ),
            "B": ev_b,
        },
    )
    assert report.passed is False
    assert any(
        item.startswith("CHARACTER_IDENTITY_COLLISION:A:")
        for item in report.collision_findings
    )


def test_cross_backend_request_contains_actor_identity_pack(tmp_path):
    from cinefactory.appctx import build_context

    ctx = build_context(ROOT)
    ns = runpy.run_path(
        str(ROOT / "tests" / "test_block_auto_repair_v173.py")
    )
    compiled = EpisodeAssembler.from_root(ROOT).compile(
        ns["_episode"]()
    )
    source = (
        ROOT
        / "data"
        / "verification"
        / "v179_candidate_promotion"
        / "cycles_matrix"
        / "S01.cycles.golden.mp4"
    )
    normalized = ctx.cross_backend_video.normalize_shot(
        project_id=compiled.project_id,
        episode_id=compiled.episode_id,
        shot=compiled.shots[0],
        output_path=tmp_path / "wan.mp4",
        reference_frame_path=source,
        recurring_identity_required=True,
        semantic_performance_required=False,
        precise_camera_required=False,
        render_preview=True,
        seed=123,
    )
    assert normalized.passed is True
    request = normalized.request
    assert request is not None
    assert request.reference.global_character_ids == {
        "A": "CHAR_MC_A"
    }
    assert request.reference.actor_reference_ids["A"]
    assert request.reference.actor_screen_boxes["A"]["area"] > 0
    assert "global character CHAR_MC_A" in request.prompt


def test_app_context_shares_character_factory():
    from cinefactory.appctx import build_context

    ctx = build_context(ROOT)
    assert (
        ctx.character_factory
        is ctx.studio.professional_company.character_factory
    )
    assert (
        ctx.cross_backend_video.character_factory
        is ctx.character_factory
    )


def test_old_reference_pack_is_invalid_after_state_change(tmp_path):
    factory = CharacterFactory(
        ROOT,
        store=CharacterFactoryStore(tmp_path / "cf"),
    )
    record = factory.record_for_rig("mc_a")
    source = (
        ROOT
        / "data"
        / "verification"
        / "v179_candidate_promotion"
        / "cycles_matrix"
        / "S01.cycles.golden.mp4"
    )
    pack = factory.capture_reference_from_render(
        source_media=source,
        actor_id="A",
        rig_id="mc_a",
    )
    factory.update_state(
        record.global_character_id,
        costume_id="mc_a_winter_v2",
    )
    report = factory.evaluate_output(
        actor_reference_ids={"A": pack.reference_id},
        global_character_ids={
            "A": record.global_character_id
        },
        current_actors={"A": pack.evidence},
    )
    assert report.passed is False
    assert any(
        item.startswith(
            "CHARACTER_REFERENCE_STATE_VERSION_STALE:A:"
        )
        for item in report.findings
    )


def test_cross_backend_transition_measures_same_character(tmp_path):
    factory = CharacterFactory(
        ROOT,
        store=CharacterFactoryStore(tmp_path / "cf"),
    )
    ev = _evidence(
        "A",
        bin_index=4,
        rgb=[0.2, 0.3, 0.4],
        ahash64="0f0f0f0f0f0f0f0f",
    )
    report = factory.evaluate_transition(
        previous_backend=CharacterBackendId.BLENDER_BLOCK,
        current_backend=CharacterBackendId.WAN21,
        actor_to_global={"A": "CHAR_MC_A"},
        previous_actors={"A": ev},
        current_actors={"A": ev},
    )
    assert report.passed is True
    assert report.measured is True
    assert report.minimum_score is not None
    assert report.minimum_score >= 0.999999


def test_same_source_cannot_be_relabeled_as_new_state(tmp_path):
    factory = CharacterFactory(
        ROOT,
        store=CharacterFactoryStore(tmp_path / "cf"),
    )
    source = (
        ROOT
        / "data"
        / "verification"
        / "v179_candidate_promotion"
        / "cycles_matrix"
        / "S01.cycles.golden.mp4"
    )
    first = factory.capture_reference_from_render(
        source_media=source,
        actor_id="A",
        rig_id="mc_a",
    )
    factory.update_state(
        first.global_character_id,
        costume_id="mc_a_costume_v2",
    )
    second = factory.capture_reference_from_render(
        source_media=source,
        actor_id="A",
        rig_id="mc_a",
    )
    assert second.reference_id == first.reference_id
    assert second.state_version == first.state_version == 1
    assert (
        factory.record_for_rig("mc_a")
        .current_state.version
        == 2
    )


def test_actor_tracker_measures_head_mid_tail_from_real_reference(tmp_path):
    factory = CharacterFactory(
        ROOT,
        store=CharacterFactoryStore(tmp_path / "cf"),
    )
    source = (
        ROOT
        / "data"
        / "verification"
        / "v179_candidate_promotion"
        / "cycles_matrix"
        / "S01.cycles.golden.mp4"
    )
    pack = factory.capture_reference_from_render(
        source_media=source,
        actor_id="A",
        rig_id="mc_a",
    )
    tracking = factory.track_video_output(
        actor_reference_ids={"A": pack.reference_id},
        global_character_ids={"A": pack.global_character_id},
        video_path=source,
    )
    assert tracking.passed is True
    assert tracking.measured is True
    assert len(tracking.tracks) == 1
    track = tracking.tracks[0]
    assert track.actor_id == "A"
    assert len(track.samples) == 3
    assert {sample.label for sample in track.samples} == {
        "head",
        "mid",
        "tail",
    }
    assert track.minimum_score is not None
    assert track.minimum_score >= factory.identity_floor
