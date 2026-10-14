from __future__ import annotations
"""v1.6.36: genuine Blender same-scene multi-render-engine and repeatability QA."""
import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from cinefactory.studio.golden_shot_benchmark_v196 import (
    GoldenShotBenchmark,RenderSample,RenderRepeatabilityEvidence,
    GoldenShotBenchmarkLab,sha,
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"verification"/"v196_golden_benchmark"

@pytest.fixture(scope="module")
def primary():
    return GoldenShotBenchmark.model_validate_json(
        (OUT/"real_render_engine_ab_evidence_v196.json").read_text(encoding="utf-8"))

@pytest.fixture(scope="module")
def repeat():
    return RenderRepeatabilityEvidence.model_validate_json(
        (OUT/"repeatability_benchmark_evidence_v196.json").read_text(encoding="utf-8"))

@pytest.fixture(scope="module")
def pixel():
    return json.loads((OUT/"pixel_repeatability_v196.json").read_text(encoding="utf-8"))

def test_actual_original_blender_scene_byte_hash(primary):
    scene=Path(primary.source_scene)
    assert scene.is_file()
    assert scene.suffix==".blend"
    assert sha(scene)==primary.source_scene_sha256
    assert scene.stat().st_size>200000

def test_real_worker_source_provenance_unchanged(primary):
    worker=Path(primary.original_rig_source)
    assert worker.is_file()
    assert worker.name=="blender_animation_worker.py"
    for item in primary.results:
        assert item.source_worker_sha256==sha(worker)

def test_golden_shot_is_actual_two_actors_still_not_license_approved(primary):
    contract=json.loads(Path(primary.source_contract).read_text(encoding="utf-8"))
    assert contract["actor_count"]==2
    assert contract["factory_character_ids"]==["mc_a","mc_b"]
    assert contract["same_scene_for_all_backends"]
    assert contract["frames"]==24
    assert contract["resolution"]==[480,270]
    assert contract["fps"]==12
    assert contract["not_independent_asset_or_IP_signoff"]

def test_two_actual_golden_clip_variants_pass(primary):
    assert primary.status=="REAL_SAME_SCENE_RENDER_ENGINE_AB_PASS_PRODUCTION_BLOCKED"
    assert primary.actual_two_engines_tested and len(primary.results)==2
    assert {s.engine for s in primary.results}=={"workbench","eevee"}
    assert primary.errors=={}

def test_both_render_engines_use_exact_same_blend_sha(primary):
    assert len({x.blender_scene_sha256 for x in primary.results})==1
    assert {x.blender_scene_sha256 for x in primary.results}=={
        primary.source_scene_sha256}

def test_no_cross_software_engine_claim(primary):
    assert not primary.different_video_software_tested
    assert all("Blender" in r.backend_name for r in primary.results)
    assert not primary.head_to_head_quality_claim

def test_all_genuine_output_movies_present_and_hash_verified(primary):
    for item in primary.results:
        file=Path(item.mp4_path)
        assert file.is_file()
        assert file.stat().st_size==item.mp4_bytes
        assert sha(file)==item.mp4_sha256
        assert item.video_codec=="h264"

def test_exact_output_duration_fps_frame_resolution(primary):
    assert all(x.actual_rendered_frame_count==24 and x.decoded_frame_count==24
               for x in primary.results)
    assert all(x.image_resolution==(480,270) and x.fps==12
               for x in primary.results)
    assert all(not x.audio_present for x in primary.results)

def test_each_png_source_has_fresh_sha_and_24_frames(primary):
    for item in primary.results:
        files=sorted((OUT/"frames"/item.engine).glob("frame_*.png"))
        assert len(files)==24
        assert [sha(f) for f in files]==item.png_frame_hashes

def test_animated_clip_contains_real_frame_variation(primary):
    for item in primary.results:
        assert len(set(item.png_frame_hashes))>1

def test_no_gpu_perprocess_vram_assumption(primary):
    assert not primary.per_process_peak_vram_measured
    for r in primary.results:
        assert r.global_gpu_memory_is_not_blender_vram
        assert r.measured_global_gpu_used_peak_mib is not None
        assert r.measured_global_gpu_baseline_mib is not None
        assert r.measured_global_gpu_used_peak_mib>=r.measured_global_gpu_baseline_mib

def test_qualitative_blind_viewer_quality_remains_unapproved(primary):
    assert not primary.human_blind_review_complete
    assert not primary.head_to_head_quality_claim
    assert not primary.production_release_authorized
    assert all(not item.human_creative_quality_reviewed for item in primary.results)

def test_total_accepted_minute_cost_is_unknown(primary):
    assert not primary.accepted_minute_cost_usd_measured
    assert not primary.true_electricity_dollars_measured
    assert all(item.accepted_minute_cost_usd is None for item in primary.results)

def test_renderer_brightness_is_observation_not_artistic_score(primary):
    observations={r.engine:r for r in primary.results}
    assert observations["eevee"].png_mean_luminance>observations["workbench"].png_mean_luminance
    assert all(0<r.png_mean_luminance<255 for r in observations.values())
    assert all(r.png_edge_variance>0 for r in observations.values())

def test_first_run_winner_not_premature_production_winner(primary):
    assert primary.objective_speed_faster_engine=="eevee"
    assert not primary.production_release_authorized

def test_counterbalanced_all_eight_real_trial_renders(repeat):
    assert repeat.status=="SAME_PROJECT_THREE_EXTRA_TRIALS_COMPLETE_NOT_PRODUCTION_CERTIFIED"
    assert len(repeat.reports)==8
    assert repeat.render_order==[
        "workbench","eevee","eevee","workbench",
        "workbench","eevee","eevee","workbench"]
    assert len([x for x in repeat.reports if x.engine=="eevee"])==4
    assert len([x for x in repeat.reports if x.engine=="workbench"])==4
    assert repeat.errors=={}

def test_each_rerender_trial_has_24_real_frames(repeat):
    assert all(len(rec.png_frame_hashes)==24 for rec in repeat.reports)
    assert all(rec.decoded_frame_count==24 for rec in repeat.reports)
    assert all(sha(Path(rec.mp4_path))==rec.mp4_sha256 for rec in repeat.reports)

def test_global_scene_sha_constant_for_every_repetition(primary,repeat):
    assert repeat.exact_original_scene_sha256==primary.source_scene_sha256
    assert all(x.blender_scene_sha256==primary.source_scene_sha256 for x in repeat.reports)

def test_repeated_medians_reverse_first_run_speed_winner(primary,repeat):
    assert repeat.fastest_median_engine=="workbench"
    med=repeat.median_render_seconds_by_engine
    assert med["workbench"]<med["eevee"]
    assert repeat.first_run_is_not_representative
    assert not repeat.production_selected

def test_bytewise_png_sha_not_a_substitute_for_pixel_comparison(repeat,pixel):
    # Container can encode a visually identical PNG differently across
    # repeated process runs; compare decoded pixels, not bytes alone.
    assert repeat.output_bytewise_deterministic=={"workbench":False,"eevee":False}
    assert all(row["pixel_exact_frame_ratio"]==1. for row in pixel["renderer"].values())
    assert all(row["median_pixel_mae_0_to_255"]==0.
               for row in pixel["renderer"].values())
    assert all(row["maximum_single_pixel_channel_difference"]==0
               for row in pixel["renderer"].values())

def test_pixel_replay_provenance_contains_all_144_comparisons(pixel):
    assert pixel["status"]=="REAL_SAME_BLENDER_PROJECT_PIXEL_REPEATABILITY_AUDITED"
    assert all(v["total_cross_run_frames"]==72 for v in pixel["renderer"].values())
    assert not pixel["renderer"]["workbench"]["human_rated_appearance_comparison"]
    assert pixel["difference_is_not_subjective_image_quality_score"]

def test_primary_comparison_contact_sheet_contains_6_real_source_frames():
    ref=json.loads((OUT/"contact_sheet_frame_manifest_v196.json").read_text(encoding="utf-8"))
    contact=OUT/"golden_renderer_comparison_v196.jpg"
    assert contact.is_file()
    assert sha(contact)==ref["contact_sheet_sha256"]
    assert len(ref["frames"])==6
    assert not ref["human_artistic_qc_passed"]
    for f in ref["frames"]:
        assert sha(Path(f["file"]))==f["sha256"]

def test_render_sample_rejects_sha_count_fabrication(primary):
    item=primary.results[0].model_dump(mode="json")
    item["png_frame_hashes"]=item["png_frame_hashes"][:2]
    with pytest.raises(ValidationError,match="FRAME_SHA_COUNT_MISMATCH"):
        RenderSample.model_validate(item)

def test_render_sample_rejects_reported_decode_mismatch(primary):
    item=primary.results[0].model_dump(mode="json")
    item["decoded_frame_count"]=777
    with pytest.raises(ValidationError,match="ENCODED_DECODE_FRAME_COUNT_MISMATCH"):
        RenderSample.model_validate(item)

def test_no_automatic_render_permission():
    service=GoldenShotBenchmarkLab(ROOT)
    with pytest.raises(PermissionError,match="EXPLICIT_ORIGINAL_SCENE_AUTHORIZATION"):
        service.run_explicit()
    with pytest.raises(PermissionError,match="EXPLICIT_ORIGINAL_SCENE_AUTHORIZATION"):
        service.repeat_explicit()

def test_company_exposes_same_benchmark_lab_with_no_auto_execution(primary,repeat):
    from cinefactory.appctx import build_context
    context=build_context(ROOT)
    assert context.golden_shot_benchmark_lab is context.studio.professional_company.golden_shot_benchmark_lab
    assert context.golden_shot_benchmark_lab.latest().source_scene_sha256==primary.source_scene_sha256
    assert context.golden_shot_benchmark_lab.latest_repeatability().render_order==repeat.render_order

def test_rights_human_reviews_and_cross_software_still_block_production(primary,repeat):
    assert not repeat.human_quality_approved
    assert not repeat.cross_software_comparison_complete
    assert not repeat.production_selected
    assert all(not r.royalty_licence_cleared for r in repeat.reports)
    assert "NO_COMMERCIAL_MEDIA_IP_AND_RIGHTS_SIGNOFF" in primary.blockers
