from __future__ import annotations
"""CineFactory 1.6.32 R&D is auditable and refuses to fake research quality."""
import json
from pathlib import Path
import pytest
from pydantic import ValidationError

from cinefactory.studio.niche_research_conference_v192 import (
    DEPARTMENT_PLAYBOOK,OFFICIAL_SOURCE_SNAPSHOT,ResearchMaturity,
    NicheResearchConference,NicheResearchConferenceReport
)
from cinefactory.studio.research_brief_parser_v192 import (
    ProductionResearchInput,analyze_research_input,
)
from cinefactory.studio.production_selection_council import Stage
from cinefactory.studio.codec_ab_experiment_v192 import CodecExperimentEvidence

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"verification"/"v192_department_research"

@pytest.fixture(scope="module")
def preschool():
    return NicheResearchConference(ROOT).convene(
        "preschool_3d_musical",project_id="EXAMPLE_PRESCHOOL",
        context={
            "script_text":"Scene 1: Little child sings the ABC song and dances.\nScene 2: A character says the letters and waves.",
            "reference_video_urls":["https://www.youtube.com/watch?v=EXAMPLE"],
        })

def test_22_department_sops_are_present():
    assert len(DEPARTMENT_PLAYBOOK)==22
    assert {"executive","audience_research","creative_direction","script",
            "curriculum_child_safety","songwriting_music","voice_cast",
            "concept_character_ip","rigging","storyboard","animation",
            "game_simulation","camera_lighting","ai_generatives",
            "capture_foley","audio_post","editorial_2d","localization",
            "qa_compliance","compute_finance","distribution_analytics",
            "rnd_security"}==set(DEPARTMENT_PLAYBOOK)

def test_every_department_has_input_question_output_qc():
    for item in DEPARTMENT_PLAYBOOK.values():
        assert item.inputs and item.research_questions
        assert item.deliverables and item.objective_qc
        assert item.last_verified_quality is False

def test_all_sources_have_bounded_claims_and_are_not_pretend_license_approved():
    assert len(OFFICIAL_SOURCE_SNAPSHOT)>=10
    for source in OFFICIAL_SOURCE_SNAPSHOT.values():
        assert source.url.startswith("https://")
        assert source.publisher and source.claim_scope
        assert not source.verified_for_scope
        assert not source.license_review_complete

def test_research_department_cites_known_sources():
    for item in DEPARTMENT_PLAYBOOK.values():
        assert set(item.source_ids)<=set(OFFICIAL_SOURCE_SNAPSHOT)

def test_preschool_requires_music_child_education_and_organic_rig(preschool):
    ids={x.department_id for x in preschool.department_reviews}
    assert {"songwriting_music","curriculum_child_safety","voice_cast",
            "rigging","animation","qa_compliance"}<=ids
    assert "PRESCHOOL_IP_EDUCATIONAL_CHILD_SAFETY_MUSIC_RIGHTS_HUMAN_GATES" in preschool.blockers

def test_minecraft_research_does_not_insert_preschool_review():
    report=NicheResearchConference(ROOT).convene("minecraft")
    assert "curriculum_child_safety" not in {r.department_id for r in report.department_reviews}
    assert not report.production_qualified

def test_longslide_consults_game_simulation():
    report=NicheResearchConference(ROOT).convene("long_slices_game")
    assert "game_simulation" in {r.department_id for r in report.department_reviews}
    assert Stage.GAME_RUNTIME in {e.stage for e in report.experiments}

def test_asrm_real_recording_consults_capture():
    report=NicheResearchConference(ROOT).convene("asmr_sleep_hands_objects")
    assert "capture_foley" in {r.department_id for r in report.department_reviews}

def test_official_source_ledger_is_bounded_not_invented(preschool):
    assert preschool.source_ledger
    assert all(x.source_id in OFFICIAL_SOURCE_SNAPSHOT for x in preschool.source_ledger)
    assert not preschool.source_claims_are_verified_for_scope

def test_conference_only_plans_experiments(preschool):
    assert len(preschool.experiments)>=10
    assert all(x.benchmark_status==ResearchMaturity.BENCHMARK_PENDING for x in preschool.experiments)
    assert all(not x.execution_authorized and not x.eligible_to_promote for x in preschool.experiments)
    assert all(x.human_signoff_required and x.license_gate for x in preschool.experiments)

def test_no_free_api_or_unqualified_tool_wins_preschool(preschool):
    assert not preschool.production_qualified
    assert preschool.blocked_stages
    assert all(step["selection"]["production_method_id"] is None for step in preschool.stage_decisions)

def test_two_explicit_script_scenes_are_detected(preschool):
    a=preschool.input_analysis
    assert a is not None
    assert a.script_segments==2
    assert a.media_urls_supplied==1
    assert not a.media_url_content_verified
    assert "REFERENCE_VIDEO_URL_CONTENT_NOT_FETCHED_OR_ANALYZED" in a.blockers
    assert Stage.MUSIC in a.scenes[0].inferred_stages
    assert Stage.ANIMATION in a.scenes[0].inferred_stages
    assert Stage.VOICE in a.scenes[1].inferred_stages

def test_script_hypotheses_are_never_fake_visual_analysis(preschool):
    assert all(x.attribution=="USER_SUPPLIED_SCRIPT_OR_BRIEF_TEXT_ONLY" for x in preschool.input_analysis.scenes)
    assert all(not x.visual_reference_content_inspected for x in preschool.input_analysis.scenes)
    assert all(not x.ready_for_production for x in preschool.input_analysis.scenes)

def test_unknown_niche_blocked():
    with pytest.raises(ValueError,match="UNKNOWN_NICHE"):
        NicheResearchConference(ROOT).convene("new_unresearched_live_stream_type")

def test_script_without_scene_markers_is_one_hypothesis():
    inp=ProductionResearchInput(project_brief="Rain sound for sleep")
    r=analyze_research_input(inp)
    assert r.script_segments==1
    assert Stage.AUDIO_POST in r.scenes[0].inferred_stages

def test_empty_input_cannot_claim_reviewed():
    r=analyze_research_input(ProductionResearchInput(
        reference_video_urls=["https://youtube.com/watch?v=unseen"]))
    assert r.scenes==[]
    assert r.input_kind=="UNINSPECTED_MEDIA_LINKS"
    assert not r.media_url_content_verified
    assert "SCRIPT_AND_PROJECT_BRIEF_MISSING" in r.blockers

def test_invalid_negative_target_duration_fails():
    with pytest.raises(ValidationError):
        ProductionResearchInput(target_duration_minutes=-5)

def test_persisted_playbook_and_all_13_niche_reports():
    d=json.loads((OUT/"department_playbook_v192.json").read_text(encoding="utf-8"))
    assert len(d["departments"])==22
    assert not d["production_qualified"]
    assert not d["ready_to_auto_execute"]
    s=json.loads((OUT/"niche_research_summary_v192.json").read_text(encoding="utf-8"))
    assert len(s)==13
    assert all(not x["production_qualified"] for x in s.values())

def test_110_real_plans_are_falsifiable_but_not_executed():
    summary=json.loads((OUT/"niche_research_summary_v192.json").read_text(encoding="utf-8"))
    assert sum(x["experiment_plans"] for x in summary.values())==110
    for id in summary:
        obj=NicheResearchConferenceReport.model_validate_json(
            (OUT/"niche_research"/(id+".json")).read_text(encoding="utf-8"))
        assert all(not experiment.eligible_to_promote for experiment in obj.experiments)
        assert not obj.external_research_performed_live

def test_encoder_uses_real_existing_cinefactory_clip():
    data=CodecExperimentEvidence.model_validate_json(
        (OUT/"codec_ab"/"codec_ab_evidence_v192.json").read_text(encoding="utf-8"))
    assert Path(data.source).is_file()
    assert "two_actors_speech_audible.mp4" in data.source
    assert len(data.candidates)==3
    assert all(x.decoded_video_frames==90 for x in data.candidates)
    assert all(x.video_codec=="h264" for x in data.candidates)

def test_encoder_all_ssim_measured_from_encoded_files():
    import hashlib
    data=CodecExperimentEvidence.model_validate_json(
        (OUT/"codec_ab"/"codec_ab_evidence_v192.json").read_text(encoding="utf-8"))
    for item in data.candidates:
        assert .90<item.ssim_all<1
        path=Path(item.output)
        assert path.is_file()
        assert path.stat().st_size==item.output_bytes
        assert hashlib.sha256(path.read_bytes()).hexdigest()==item.output_sha256
        assert item.ffmpeg_wallclock_seconds>0

def test_encoder_avoids_false_perceived_quality_and_price_claims():
    data=CodecExperimentEvidence.model_validate_json(
        (OUT/"codec_ab"/"codec_ab_evidence_v192.json").read_text(encoding="utf-8"))
    assert not data.production_qualified
    assert not data.human_creative_quality_approved
    assert not data.prices_measured
    assert not data.accepted_video_minutes_known
    assert not data.model_or_engine_quality_comparison
    assert not data.license_and_royalty_approved

def test_company_has_same_research_conference_instance():
    from cinefactory.appctx import build_context
    ctx=build_context(ROOT)
    assert ctx.niche_research_conference is ctx.studio.professional_company.niche_research_conference

def test_json_model_cannot_be_promoted_without_actual_quality_evidence(preschool):
    assert not preschool.creative_quality_human_approved
    assert "NO_AUTOMATIC_PRODUCTION_APPROVAL_WITHOUT_REAL_BENCHMARK_AND_LICENSE" in preschool.blockers


def test_researched_external_cards_do_not_claim_executable_best_tool():
    from cinefactory.studio.external_tool_research_v192 import (
        research_candidate_snapshot,
    )
    snapshot=research_candidate_snapshot()
    assert len(snapshot["cards"])>=4
    assert not snapshot["all_candidates_production_qualified"]
    assert all(not x["production_qualified"] for x in snapshot["cards"])
    assert all(not x["actual_executable_benchmark_complete"] for x in snapshot["cards"])


def test_wan22_reference_24gb_is_blocked_for_native_3060():
    from cinefactory.studio.external_tool_research_v192 import (
        EXTERNAL_RESEARCH_CANDIDATES,
    )
    wan=next(x for x in EXTERNAL_RESEARCH_CANDIDATES if "wan2.2" in x.id)
    assert wan.minimum_vendor_vram_gb==24.
    assert wan.hardware_status=="BLOCKED_UNDER_VENDOR_REFERENCE_GPU_REQUIREMENT"
    assert not wan.checkpoint_license_approved


def test_ltx_2b_is_unverified_for_12gb_not_auto_admitted():
    from cinefactory.studio.external_tool_research_v192 import (
        EXTERNAL_RESEARCH_CANDIDATES,
    )
    ltx=next(x for x in EXTERNAL_RESEARCH_CANDIDATES if "ltxv" in x.id)
    assert ltx.minimum_vendor_vram_gb is None
    assert ltx.hardware_status=="UNKNOWN_MEASURE_ON_ISOLATED_GPU_NO_NATIVE_FIT_CLAIM"
    assert not ltx.actual_creative_quality_reviewed


def test_score_notation_not_equal_original_song_or_rights():
    from cinefactory.studio.external_tool_research_v192 import (
        EXTERNAL_RESEARCH_CANDIDATES,
    )
    mus=next(x for x in EXTERNAL_RESEARCH_CANDIDATES if "musescore" in x.id)
    assert "NO_AUTOMATED_ORIGINAL_COMPOSER" in mus.risks
    assert not mus.checkpoint_license_approved


def test_archived_tts_requires_voice_rights_separate_from_code():
    from cinefactory.studio.external_tool_research_v192 import (
        EXTERNAL_RESEARCH_CANDIDATES,
    )
    piper=next(x for x in EXTERNAL_RESEARCH_CANDIDATES if "piper" in x.id)
    assert "VOICE_WEIGHTS_RIGHTS_UNCHECKED" in piper.risks
    assert "SOURCE_ARCHIVED" in piper.risks


def test_generated_department_handbook_and_preschool_workflow():
    docs=ROOT/"docs"/"CINEFACTORY_DEPARTMENT_PRODUCTION_RESEARCH_V1632.md"
    content=docs.read_text(encoding="utf-8")
    assert "Department operating procedures (22)" in content
    assert "The measured SSIM" in content
    assert "preschool 3d" in content.lower()
    case=NicheResearchConferenceReport.model_validate_json(
        (OUT/"example_preschool_song_research_v192.json").read_text(encoding="utf-8"))
    assert case.input_analysis is not None
    assert case.input_analysis.script_segments==3
    assert all(not x.ready_for_production for x in case.input_analysis.scenes)


def test_extra_source_ledger_persisted_from_repositories():
    inventory=json.loads((OUT/"external_tool_research_v192.json").read_text(encoding="utf-8"))
    assert len(inventory["source_ledger"])==4
    assert inventory["status"]=="RESEARCH_ONLY_NO_DOWNLOAD_OR_PRODUCTION"
    assert all(not ref["license_review_complete"] for ref in inventory["source_ledger"].values())
