from __future__ import annotations
"""v1.6.35 evidence-level video research, no invented competitor frame analyses."""
import hashlib
import json
from pathlib import Path
import pytest
from pydantic import ValidationError

from cinefactory.studio.video_production_intelligence_v195 import (
    VideoProductionIntelligence,VideoReferenceInput,
    VideoProofLevel, ProductionObservationHandoff,
)
from cinefactory.studio.reference_intelligence import VideoSourceMetadata

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"verification"/"v195_video_production_intelligence"
LOCAL_VIDEO=ROOT/"data"/"verification"/"v185_alignment_reid"/"two_actors_speech_audible.mp4"

def local_request(**extra):
    obj=dict(niche_id="minecraft",project_id="test",
             local_file=str(LOCAL_VIDEO),source_video_id="test_owned",
             first_party_or_authorized_media=True)
    obj.update(extra)
    return VideoReferenceInput(**obj)

def test_real_owned_media_v185_has_framed_and_audio_evidence():
    obj=ProductionObservationHandoff.model_validate_json(
        (OUT/"v195_owned_voxel_v185_decoded_evidence.json").read_text(encoding="utf-8"))
    a=obj.observations
    assert a.proof_level==VideoProofLevel.LOCAL_OWNED_MEDIA_DECODED
    assert a.decoded_media_observed and not a.metadata_only
    assert a.video_frame_count==90
    assert a.image_width==640 and a.image_height==360
    assert a.scene_cuts==0
    assert a.audio_stream_analyzed
    assert a.measured_silence_ratio is not None
    assert a.source_sha256==hashlib.sha256(LOCAL_VIDEO.read_bytes()).hexdigest()

def test_second_real_owned_media_is_distinct_and_checks_audio():
    a=ProductionObservationHandoff.model_validate_json(
        (OUT/"v195_owned_voxel_v185_decoded_evidence.json").read_text(encoding="utf-8"))
    b=ProductionObservationHandoff.model_validate_json(
        (OUT/"v195_owned_voxel_v186_decoded_evidence.json").read_text(encoding="utf-8"))
    assert a.observations.source_sha256!=b.observations.source_sha256
    assert b.observations.video_frame_count==90
    assert b.observations.camera_motion_proxy=="STATIC_DOMINANT"
    assert b.observations.measured_silence_ratio is not None
    assert b.observations.measured_silence_ratio>a.observations.measured_silence_ratio

def test_public_bigschool_has_real_metadata_but_no_content():
    obj=ProductionObservationHandoff.model_validate_json(
        (OUT/"bigschool_public_metadata_only_evidence.json").read_text(encoding="utf-8"))
    a=obj.observations
    assert a.video_id=="n3PT62-WX20"
    assert a.source_channel_public_metadata=="BigSchool"
    assert a.video_duration_seconds>1800
    assert a.views_public_metadata>100000
    assert a.proof_level==VideoProofLevel.PUBLIC_YOUTUBE_METADATA_ONLY
    assert a.scene_cuts is None
    assert a.camera_motion_proxy is None
    assert a.measured_silence_ratio is None
    assert not a.decoded_media_observed
    assert not a.audio_stream_analyzed
    assert not a.transcript_cues_analyzed
    assert not a.video_engine_identified
    assert not a.character_rig_identified
    assert "VIDEO_CONTENT_UNAVAILABLE" in obj.blocked_capabilities

def test_summary_media_limitations_are_declared():
    s=json.loads((OUT/"study_summary_v195.json").read_text(encoding="utf-8"))
    assert s["local_owned_media_count"]==2
    assert s["local_decoded_video_frame_counts"]==[90,90]
    assert s["public_metadata_only_study_done"]
    assert not s["public_video_frames_decoded"]
    assert not s["public_video_downloaded"]
    assert not s["competitor_production_method_proven"]
    assert not s["production_tools_benchmarked_cross_engine"]
    assert not s["production_release_authorized"]
    assert s["no_paid_API_used"]

def test_local_media_explicit_consent_required():
    with pytest.raises(ValidationError,match="LOCAL_MEDIA_RIGHTS_ATTESTATION_REQUIRED"):
        VideoReferenceInput(niche_id="minecraft",project_id="x",local_file=str(LOCAL_VIDEO))

def test_unknown_input_and_both_sources_rejected():
    with pytest.raises(ValidationError,match="MUST_SUPPLY_EXACTLY_ONE_VIDEO_SOURCE"):
        VideoReferenceInput(niche_id="minecraft",project_id="x")
    with pytest.raises(ValidationError,match="MUST_SUPPLY_EXACTLY_ONE_VIDEO_SOURCE"):
        VideoReferenceInput(niche_id="minecraft",project_id="x",
            local_file=str(LOCAL_VIDEO),youtube_video_id="n3PT62-WX20",
            first_party_or_authorized_media=True)

@pytest.mark.parametrize("video",[
    "https://127.0.0.1/hi","../private","invalid","../../.env",
    "n3PT62-WX20&format=best","n3PT62-WX20/../../",
])
def test_untrusted_video_id_not_a_network_url(video):
    with pytest.raises(ValidationError,match="YOUTUBE_ID_NOT_CANONICAL"):
        VideoReferenceInput(niche_id="minecraft",project_id="x",youtube_video_id=video)

def test_refuse_paid_api_and_raw_copy():
    with pytest.raises(ValidationError,match="VIDEO_RESEARCH_REJECTS_RAW_COPY_OR_PAID_API"):
        VideoReferenceInput(niche_id="minecraft",project_id="x",youtube_video_id="n3PT62-WX20",
                            external_paid_api_allowed=True)
    with pytest.raises(ValidationError,match="VIDEO_RESEARCH_REJECTS_RAW_COPY_OR_PAID_API"):
        VideoReferenceInput(niche_id="minecraft",project_id="x",youtube_video_id="n3PT62-WX20",
                            save_raw_copyrighted_media=True)

def test_subtitle_study_unavailable_from_metadata_only():
    with pytest.raises(ValidationError,match="SUBTITLE_CONTENT_NOT_AVAILABLE_VIA_METADATA_ONLY"):
        VideoReferenceInput(niche_id="minecraft",project_id="x",youtube_video_id="n3PT62-WX20",
                            analyze_automatic_transcript=True)

def test_path_outside_project_disallowed(tmp_path):
    media=tmp_path/"untrusted.mp4"
    media.write_bytes(b"untrusted")
    with pytest.raises(ValueError):
        VideoProductionIntelligence(ROOT).study(local_request(local_file=str(media)))

def test_unknown_niche_requires_signed_blueprint():
    with pytest.raises(ValueError,match="UNKNOWN_NICHE"):
        VideoProductionIntelligence(ROOT).study(
            local_request(niche_id="new_unknown_anime_film"))

def test_local_nonexistent_file_cannot_be_marked_decoded():
    with pytest.raises(FileNotFoundError):
        VideoProductionIntelligence(ROOT).study(
            local_request(local_file=str(ROOT/"not_a_video.mp4")))

def test_fake_public_metadata_cannot_become_visual_evidence(monkeypatch):
    from cinefactory.studio.reference_intelligence import ReferenceVideoDecomposer
    def fake_metadata(self,url):
        assert url=="https://www.youtube.com/watch?v=n3PT62-WX20"
        return (VideoSourceMetadata(
            video_id="n3PT62-WX20",source_url=url,
            duration_seconds=1100,channel="fixture",view_count=999),
            {})
    monkeypatch.setattr(ReferenceVideoDecomposer,"metadata",fake_metadata)
    r=VideoProductionIntelligence(ROOT).study(VideoReferenceInput(
        niche_id="minecraft",project_id="test",youtube_video_id="n3PT62-WX20"))
    assert r.observations.metadata_only
    assert r.observations.camera_motion_proxy is None
    assert r.observations.source_sha256 is None
    assert not r.production_method_selected
    assert not r.content_or_music_rights_reviewed

def test_public_video_duration_exceeds_2400_is_rejected(monkeypatch):
    from cinefactory.studio.reference_intelligence import ReferenceVideoDecomposer
    def fake_metadata(self,url):
        return (VideoSourceMetadata(
            video_id="n3PT62-WX20",source_url=url,duration_seconds=2700),{})
    monkeypatch.setattr(ReferenceVideoDecomposer,"metadata",fake_metadata)
    with pytest.raises(RuntimeError,match="VIDEO_DURATION_EXCEEDS_SCOPE"):
        VideoProductionIntelligence(ROOT).study(VideoReferenceInput(
            niche_id="minecraft",project_id="test",youtube_video_id="n3PT62-WX20",
            max_duration_seconds=2400))

def test_public_id_mismatch_is_rejected_before_any_evidence(monkeypatch):
    from cinefactory.studio.reference_intelligence import ReferenceVideoDecomposer
    def fake_metadata(self,url):
        return (VideoSourceMetadata(
            video_id="aaaaaaaaaaa",source_url=url,duration_seconds=60),{})
    monkeypatch.setattr(ReferenceVideoDecomposer,"metadata",fake_metadata)
    with pytest.raises(ValueError,match="YOUTUBE_VIDEO_ID_MISMATCH"):
        VideoProductionIntelligence(ROOT).study(VideoReferenceInput(
            niche_id="minecraft",project_id="test",youtube_video_id="n3PT62-WX20"))

def test_potential_methods_are_proposals_not_reverse_engineered():
    evidence=ProductionObservationHandoff.model_validate_json(
        (OUT/"v195_owned_voxel_v185_decoded_evidence.json").read_text(encoding="utf-8"))
    assert evidence.potential_method_families
    assert all(not m.executable_qualified and not m.production_approved
               for m in evidence.potential_method_families)
    assert all("PRECISE_RENDERER_OR_MODEL_NOT_IDENTIFIABLE_FROM_FINAL_VIDEO"
               in m.cannot_conclude for m in evidence.potential_method_families)

def test_minecraft_stage_output_routes_to_animation_and_tech_not_claim_best():
    report=ProductionObservationHandoff.model_validate_json(
        (OUT/"v195_owned_voxel_v185_decoded_evidence.json").read_text(encoding="utf-8"))
    assert "animation" in report.department_study_requirements
    assert "camera_lighting" in report.department_study_requirements
    assert "qa_compliance" in report.department_study_requirements
    assert report.recommended_tests
    assert not report.infer_hidden_production_pipeline

def test_preschool_music_and_originality_review_added(monkeypatch):
    from cinefactory.studio.reference_intelligence import ReferenceVideoDecomposer
    def fake_metadata(self,url):
        return (VideoSourceMetadata(
            video_id="n3PT62-WX20",source_url=url,duration_seconds=300),{})
    monkeypatch.setattr(ReferenceVideoDecomposer,"metadata",fake_metadata)
    report=VideoProductionIntelligence(ROOT).study(VideoReferenceInput(
        niche_id="preschool_3d_musical",project_id="song",
        youtube_video_id="n3PT62-WX20"))
    assert any("CHILD SAFETY" in t for t in report.recommended_tests)
    assert any("music" in m.method_family.lower() for m in report.potential_method_families)
    assert not report.human_visual_quality_reviewed
    assert "curriculum_child_safety" in report.department_study_requirements

def test_long_slide_needs_real_simulation_benchmark_not_camera_guess(monkeypatch):
    from cinefactory.studio.reference_intelligence import ReferenceVideoDecomposer
    def fake_metadata(self,url):
        return (VideoSourceMetadata(
            video_id="n3PT62-WX20",source_url=url,duration_seconds=200),{})
    monkeypatch.setattr(ReferenceVideoDecomposer,"metadata",fake_metadata)
    report=VideoProductionIntelligence(ROOT).study(VideoReferenceInput(
        niche_id="long_slices_game",project_id="slide",
        youtube_video_id="n3PT62-WX20"))
    assert any("Godot" in m.method_family for m in report.potential_method_families)
    assert all("PIXELS_AND_AUDIO_NOT_ACQUIRED" in m.cannot_conclude
               for m in report.potential_method_families)
    assert "game_simulation" in report.department_study_requirements
    assert not report.production_method_selected

def test_audio_and_asmr_pipeline_not_generic_blender_default():
    for niche in ("audio_storytelling_seniors","asmr_sleep_hands_objects",
                  "rain_sleep_white_noise"):
        engines=VideoProductionIntelligence(ROOT)._methods(
            niche,ProductionObservationHandoff.model_validate_json(
                (OUT/"bigschool_public_metadata_only_evidence.json").read_text(encoding="utf-8")
            ).observations)
        assert engines and all(
            "blender" not in item.method_family.lower()
            and "cinematic rig" not in item.method_family.lower()
            for item in engines
        )
        assert any(
            name in " ".join(x.method_family.lower() for x in engines)
            for name in ("audio","capture","narration","ambience","tts")
        )

def test_all_13_niche_blueprints_can_propose_methods_without_license_claim():
    from cinefactory.studio.production_tool_catalog_v191 import NICHE_BLUEPRINTS
    from cinefactory.studio.video_production_intelligence_v195 import ObservedVideoSignals
    app=VideoProductionIntelligence(ROOT)
    stub=ObservedVideoSignals(proof_level=VideoProofLevel.PUBLIC_YOUTUBE_METADATA_ONLY,
                              video_id="n3PT62-WX20")
    assert len(NICHE_BLUEPRINTS)>=13
    for niche in NICHE_BLUEPRINTS:
        options=app._methods(niche,stub)
        assert options
        assert all(not x.production_approved for x in options)

def test_company_exposes_same_research_intelligence_component():
    from cinefactory.appctx import build_context
    ctx=build_context(ROOT)
    assert ctx.video_production_intelligence is ctx.studio.professional_company.video_production_intelligence


def test_owned_contact_sheet_matches_six_exact_decoded_frame_artifacts():
    data=json.loads((OUT/"owned_frame_evidence_manifest_v195.json").read_text(encoding="utf-8"))
    image=Path(data["contact_sheet_path"])
    assert image.is_file()
    assert hashlib.sha256(image.read_bytes()).hexdigest()==data["contact_sheet_sha256"]
    assert data["owned_frame_count"]==6
    assert not data["external_copyright_media_saved"]
    assert not data["creative_quality_passed"]
    for row in data["frame_evidence"]:
        path=Path(row["decoded_frame_png"])
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row["decoded_frame_png_sha256"]
        assert hashlib.sha256(Path(row["source"]).read_bytes()).hexdigest()==row["source_sha256"]
        assert row["source_is_owned"]
        assert not row["human_artistic_quality_review_complete"]


def test_decoded_qa_frame_is_pixel_identical_to_live_opencv_decode():
    import cv2
    import numpy as np
    from PIL import Image
    data=json.loads((OUT/"owned_frame_evidence_manifest_v195.json").read_text(encoding="utf-8"))
    row=data["frame_evidence"][0]
    video=cv2.VideoCapture(row["source"])
    assert video.isOpened()
    video.set(cv2.CAP_PROP_POS_FRAMES,row["frame_index"])
    ok,frame=video.read()
    video.release()
    assert ok
    png=np.array(Image.open(row["decoded_frame_png"]).convert("RGB"))
    assert np.array_equal(png,cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))


def test_static_animated_camera_raises_review_ticket_not_automatic_failure():
    report=ProductionObservationHandoff.model_validate_json(
        (OUT/"v195_owned_voxel_v185_decoded_evidence.json").read_text(encoding="utf-8"))
    assert "CAMERA_STATIC_DOMINANT_REVIEW_IF_SCENE_REQUIRES_COVERAGE" in report.observation_review_flags
    assert "NO_CUTS_OBSERVED_NOT_AN_AUTOMATIC_EDITING_DEFECT" in report.observation_review_flags
    assert not report.production_method_selected


def test_near_silent_voice_candidate_creates_conditional_audio_qc_review():
    report=ProductionObservationHandoff.model_validate_json(
        (OUT/"v195_owned_voxel_v186_decoded_evidence.json").read_text(encoding="utf-8"))
    assert "NEAR_SILENT_AUDIO_REVIEW_ONLY_IF_DIALOGUE_OR_MUSIC_EXPECTED" in report.observation_review_flags
    assert not report.human_visual_quality_reviewed
    metadata=ProductionObservationHandoff.model_validate_json(
        (OUT/"bigschool_public_metadata_only_evidence.json").read_text(encoding="utf-8"))
    assert metadata.observation_review_flags==[]
