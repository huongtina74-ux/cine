"""v211: source-bounded self-expanding CineFactory technology R&D."""
from __future__ import annotations
from datetime import datetime,timezone
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner
from cinefactory.cli import app
from cinefactory.studio.technology_discovery_v211 import (
    production_family,propose_technology_for_format,search_public_github,
    search_public_huggingface,merge_to_pending,merge_hf_to_pending,
    run_technology_discovery,
)

A="https://github.com/new-lab/BlenderBetterRig"
B="https://huggingface.co/researcher/OriginalRigModel"

def fake_public_fetch(url):
    if url.startswith("https://api.github.com/search/repositories?"):
        return json.dumps({"total_count":3,"items":[
            {"full_name":"new-lab/BlenderBetterRig",
             "html_url":A,"name":"BlenderBetterRig",
             "description":"Blender character animation rig auto retargeting",
             "private":False,"archived":False,"disabled":False,
             "stargazers_count":242,"pushed_at":"2026-10-10T00:00:00Z",
             "license":{"spdx_id":"MIT"}},
            {"full_name":"bad-lab/MinecraftGameplay",
             "html_url":"https://github.com/bad-lab/MinecraftGameplay",
             "name":"MinecraftGameplay",
             "description":"realtime livestream capture OBS game speedrun recorder",
             "private":False,"archived":False,"disabled":False},
            {"full_name":"fake/Lure",
             "html_url":"https://evil.example.com/fake/Lure",
             "name":"Blender rig", "description":"Blender auto rig",
             "private":False,"archived":False,"disabled":False},
        ]}).encode()
    if url.startswith("https://huggingface.co/api/models?"):
        return json.dumps([
            {"id":"researcher/OriginalRigModel","private":False,
             "pipeline_tag":"image-to-3d","downloads":250,
             "lastModified":"2026-10-09T05:00:00.000Z"},
            {"id":"owner/Bogus/Path","private":False},
            {"id":"missing/PrivateModel","private":True},
        ]).encode()
    raise AssertionError("Unexpected public host or endpoint: "+url)

@pytest.mark.parametrize("minor,want",[
    ("minecraft_story_adventure","FILM_3D"),
    ("minecraft_school_comedy","FILM_3D"),
    ("minecraft_animated_challenge","FILM_3D"),
    ("minecraft_recorded_survival","GAME_CAPTURE"),
    ("minecraft_gameplay_tutorial","GAME_CAPTURE"),
    ("minecraft_live_gameplay","LIVE_CAPTURE"),
    ("minecraft_scripted_machinima","MACHINIMA"),
    ("roblox_animation","FILM_3D"),
    ("long_slide_game","SLIDE_3D"),
    ("asmr_sleep","REAL_ASMR"),
    ("audio_storytelling_seniors","VOICE_STORY"),
    ("rain_sleep_white_noise","AMBIENCE"),
    ("fishing_silent","FIELD_CAPTURE"),
    ("preschool_musical","MUSICAL_3D"),
    ("daily_english","EXPLAINER"),
])
def test_source_truth_format_technology_route(minor,want):
    assert production_family(minor)==want

def test_minecraft_gameplay_never_inherits_animated_studio_tech():
    story=propose_technology_for_format("minecraft_school_comedy")
    actual=propose_technology_for_format("minecraft_recorded_survival")
    live=propose_technology_for_format("minecraft_live_gameplay")
    assert story["format_family"]=="FILM_3D"
    assert actual["format_family"]=="GAME_CAPTURE"
    assert live["format_family"]=="LIVE_CAPTURE"
    sid={x["id"] for x in story["recommendations"]}
    aid={x["id"] for x in actual["recommendations"]}
    assert "blender" in sid and "blender" not in aid
    assert not {"flux_klein4b","qwen3tts","unirig"} & aid
    assert "ffmpeg" in aid
    assert not any(x["licensed_commercial_output_verified"]
                   for x in story["recommendations"])
    assert story["competitor_actual_tools_attributed"] is False

def test_unknown_format_refuses_generic_tool_guess():
    x=propose_technology_for_format("minecraft cinematic unknown",major_niche="minecraft")
    assert x["format_family"]=="UNRESOLVED"
    assert x["recommendations"]==[]
    assert x["network_queries_allowed_only_in_public_discovery"]==[]

def test_fixed_free_public_sources_not_video_titles_and_no_credit_calls():
    x=run_technology_discovery(
        Path.cwd(),minor_niche="minecraft_school_comedy",
        discover_public=False,fetch=lambda u:pytest.fail("NOT_ALLOWED_NETWORK"))
    assert x["source_errors"]==[]
    assert x["public_queries_attempted"]==0
    assert x["no_paid_api_used"] is True
    assert x["no_model_installation"] is True
    assert x["niche_fit"]["format_family"]=="FILM_3D"

def test_github_public_search_rejects_cross_media_and_untrusted_url():
    items,errors=search_public_github("FILM_3D",fetch=fake_public_fetch)
    assert errors==[]
    assert len(items)==1
    assert items[0]["canonical_url"]==A
    assert items[0]["repo_license_claim"]=="MIT"
    assert items[0]["commercial_output_rights_verified"] is False
    assert items[0]["producer_tool_chain_attribution_verified"] is False
    assert "character" in items[0]["description"].lower()

def test_hf_public_model_search_never_certifies_model_rights():
    items,errors=search_public_huggingface("FILM_3D",fetch=fake_public_fetch)
    assert not errors
    assert len(items)==1
    assert items[0]["canonical_url"]==B
    assert items[0]["model_card_license_claim"]=="UNKNOWN_NOT_FETCHED"
    assert items[0]["model_weight_license_verified"] is False

def test_real_public_candidates_go_to_pending_not_production(tmp_path):
    report=run_technology_discovery(
        tmp_path,minor_niche="minecraft_school_comedy",major_niche="minecraft",
        discover_public=True,fetch=fake_public_fetch)
    assert report["public_queries_attempted"]==1
    assert report["source_errors"]==[]
    assert not report["production_technologies_changed"]
    repos=report["pending_queue"]["pending_additions"]
    weights=report["model_pending_queue"]["pending_additions"]
    assert len(repos)==1
    assert len(weights)==1
    for pending in repos+weights:
        data=json.loads(Path(pending["path"]).read_text(encoding="utf8"))
        assert data["candidate_status"].startswith("PENDING")
        assert data["production_permissions"]["auto_install"] is False
        assert data["production_permissions"]["paid_api"] is False
        assert data["production_permissions"]["publish"] is False
        assert data["production_permissions"]["license_approved"] is False
        assert data["context"]["format_family"]=="FILM_3D"
    # The read-only licensed radar remains unchanged at all times.
    from cinefactory.studio.technology_radar_v210 import load_technology_radar
    core=load_technology_radar()
    assert core["entry_count"]==96
    assert all(not x["deploy_approved"] for x in core["items"])
    # Repeated requests do not keep appending the same unqualified candidate.
    again=run_technology_discovery(
        tmp_path,minor_niche="minecraft_school_comedy",major_niche="minecraft",
        discover_public=True,fetch=fake_public_fetch)
    assert not again["pending_queue"]["pending_additions"]
    assert not again["model_pending_queue"]["pending_additions"]

def test_research_incorrect_family_source_is_rejected(tmp_path):
    x,errs=search_public_github("FILM_3D",fetch=fake_public_fetch)
    wrong=propose_technology_for_format("minecraft_live_gameplay")
    report=merge_to_pending(tmp_path,context=wrong,candidate_rows=x)
    assert report["pending_additions"]==[]
    assert report["rejected_count"]==1

def test_known_baseline_repo_never_reimported(tmp_path):
    raw={
        "source_kind":"GITHUB_PUBLIC_SEARCH_METADATA",
        "source_identity":"Comfy-Org/ComfyUI",
        "canonical_url":"https://github.com/Comfy-Org/ComfyUI",
        "display_name":"ComfyUI", "description":"animation video",
        "observed_stars":999,"discovery_axis":"FILM_3D",
    }
    ctx=propose_technology_for_format("minecraft_school_comedy")
    r=merge_to_pending(tmp_path,context=ctx,candidate_rows=[raw])
    assert not r["pending_additions"]
    assert r["already_in_96_base"]==["Comfy-Org/ComfyUI"]

def test_source_search_bounds_do_not_permit_unlimited_network():
    with pytest.raises(ValueError,match="BUDGET"):
        search_public_github("FILM_3D",max_queries=100,fetch=fake_public_fetch)
    with pytest.raises(ValueError,match="BUDGET"):
        search_public_huggingface("FILM_3D",max_results=100,fetch=fake_public_fetch)

def test_actual_company_blueprint_receives_non_executable_advisory(tmp_path):
    from cinefactory.studio.company import CompanyOrchestrator
    from cinefactory.studio.kernel import build_studio_kernel
    from cinefactory.studio.contracts import StudioProjectSpec
    bp=CompanyOrchestrator(build_studio_kernel(tmp_path)).build_blueprint(
        StudioProjectSpec(
            niche="minecraft",minecraft_subniche="minecraft_school_comedy",
            prompt="Original Minecraft 3D animated school comedy",
            duration_seconds=60,
        ),professional_governance=True)
    assert bp.technology_research_advisory["format_family"]=="FILM_3D"
    assert bp.technology_research_advisory["automatic_production_backend_selected"] is False
    assert bp.technology_research_advisory["requires_human_license_and_security_review"]

def test_reference_channel_dossier_splits_mixed_technology_lanes():
    from cinefactory.research_intelligence.channel_forensics_runner_v208 import run_forensics
    from cinefactory.studio.channel_forensics_v208 import ChannelSample,Sample
    url="https://www.youtube.com/@TestChannel/videos"
    vids=[
      Sample(video_id="video"+str(i).zfill(6),title=title,duration_seconds=600,
             live_state="NOT_LIVE")
      for i,title in enumerate([
        "Minecraft school animation full episode",
        "Minecraft animated school classroom movie",
        "Minecraft real survival gameplay 100 days",
        "Minecraft survival gameplay real player",
      ],1)
    ]
    payload=run_forensics(url,sample=ChannelSample(
        submitted_url=url,videos=vids,
        collected_at="2026-10-10T10:10:10+00:00"),search=False)
    advisory=payload["technology_advisory"]
    assert advisory["source_is_metadata_not_visual_forensics"]
    assert advisory["actual_competitor_tools_verified"] is False
    d=advisory["by_metadata_format_candidate"]
    assert d["minecraft_school_comedy"]["format_family"]=="FILM_3D"
    assert d["minecraft_recorded_survival"]["format_family"]=="GAME_CAPTURE"
    assert payload["classification"]["dominant_minor_niche"] is None


def test_hf_brand_named_model_is_not_auto_added_to_original_character_backlog():
    def returns_both(url):
        if url.startswith("https://huggingface.co/api/models"):
            return json.dumps([
              {"id":"Muapi/3d-pixar-style-character-design","private":False,
               "pipeline_tag":"image-to-3d"},
              {"id":"open-research/neutral-original-rig","private":False,
               "pipeline_tag":"image-to-3d"},
            ]).encode()
        return fake_public_fetch(url)
    x,errs=search_public_huggingface("FILM_3D",fetch=returns_both)
    assert not errs
    assert [i["source_identity"] for i in x]==[
        "open-research/neutral-original-rig"
    ]


def test_repo_website_homepage_is_advisory_not_visited(tmp_path):
    from cinefactory.studio.technology_discovery_v211 import _homepage_hint
    assert _homepage_hint("https://my-production-studio.example/") is not None
    for risky in [
        "http://unsafe.test","https://localhost/private",
        "https://127.0.0.1:8188/system_stats",
        "https://192.168.0.10/internal",
        "file:///etc/passwd", "https://a.internal/",
    ]:
        assert _homepage_hint(risky) is None
    def fetch(url):
        if url.startswith("https://api.github.com/search"):
            data=json.loads(fake_public_fetch(url))
            data["items"][0]["homepage"]="https://blender-specialist.example/"
            return json.dumps(data).encode()
        return fake_public_fetch(url)
    x=run_technology_discovery(
        tmp_path,minor_niche="minecraft_school_comedy",
        discover_public=True,fetch=fetch)
    p=Path(x["pending_queue"]["pending_additions"][0]["path"])
    event=json.loads(p.read_text(encoding="utf8"))
    assert event["source"]["unverified_vendor_website_hint"]=="https://blender-specialist.example/"
    assert event["source"]["vendor_website_ownership_verified"] is False
    assert event["production_permissions"]["auto_install"] is False


def test_channel_cli_still_defaults_to_offline_and_shows_model_research(tmp_path):
    result=CliRunner().invoke(app,[
        "technology-discover",
        "--minor-niche","minecraft_recorded_survival",
        "--major-niche","minecraft",
    ])
    assert result.exit_code==0,result.output[-1300:]
    obj=json.loads(result.output)
    assert obj["niche_fit"]["format_family"]=="GAME_CAPTURE"
    assert obj["discovery_enabled"] is False
    assert obj["public_network_sources"]==[]
    assert obj["no_paid_api_used"] is True


def test_daily_runner_wired_to_public_research_but_never_auto_installs():
    root=Path(__file__).resolve().parents[1]
    runner=(root/"scripts"/"run_two_track_research_v201.py").read_text(
        encoding="utf8")
    daily=(root/"scripts"/"daily_cinefactory_research_v199.ps1").read_text(
        encoding="utf8")
    assert "args.discover_technologies" in runner
    assert "run_technology_discovery(" in runner
    assert "--discover-technologies" in daily
    assert "--scan-approved --discover-technologies" in daily
    assert '"model_installations":0' in runner
    assert '"production_approvals":0' in runner


def test_pending_queue_read_only_verifies_hash_and_never_approves(tmp_path):
    from cinefactory.studio.technology_discovery_v211 import inspect_pending_technologies
    before=inspect_pending_technologies(tmp_path)
    assert before["total"]==0
    scan=run_technology_discovery(
        tmp_path,minor_niche="minecraft_school_comedy",
        discover_public=True,fetch=fake_public_fetch)
    got=inspect_pending_technologies(tmp_path,limit=2)
    assert got["total"]==2
    assert got["all_are_unqualified"]
    assert got["automatic_install_or_use_allowed"] is False
    assert all(v["independent_license_and_benchmark_required"] for v in got["items"])
    path=Path(scan["pending_queue"]["pending_additions"][0]["path"])
    path.write_bytes(path.read_bytes()+b" ")
    with pytest.raises(RuntimeError,match="HASH_MISMATCH"):
        inspect_pending_technologies(tmp_path)


def test_english_audio_research_rejects_asr_and_source_specific_foreign_tts():
    def multilingual_search(url):
        if url.startswith("https://huggingface.co/api/models"):
            return json.dumps([
                {"id":"regional/Hindi_Text_To_Speech",
                 "private":False,"pipeline_tag":"text-to-speech"},
                {"id":"lab/speech_to_text",
                 "private":False,"pipeline_tag":"automatic-speech-recognition"},
                {"id":"open-lab/OriginalEnglishTTS",
                 "private":False,"pipeline_tag":"text-to-speech"},
            ]).encode()
        return fake_public_fetch(url)
    models,errors=search_public_huggingface(
        "VOICE_STORY",fetch=multilingual_search)
    assert errors==[]
    assert [x["source_identity"] for x in models]==[
        "open-lab/OriginalEnglishTTS"
    ]
    assert all(x["model_weight_license_verified"] is False for x in models)
