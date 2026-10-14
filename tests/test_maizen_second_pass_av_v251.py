"""No manufacturing claims: v251 independent machine AV QC remains distinct from human native G02."""
import json
from typer.testing import CliRunner
from cinefactory.cli import app
from cinefactory.studio.claude_mcp_gateway_v218 import build_server
from cinefactory.studio import maizen_second_pass_av_v251 as m

def test_two_films_mechanical_73_window_av_qc_and_precisely_recorded_native_speed_replays():
 x=m.load_av_second_pass()
 assert len(x["films"])==2
 assert [z["video_id"] for z in x["films"]]==["zhPBXzHsLuo","oX6Azwe5QLg"]
 assert x["films"][1]["original_sound_second_bins_missing"]==0
 assert "CHEST BLOCK" in x["films"][1]["second_pass_observations"][5]["visual"]
 assert not x["second_pass"]["strict_v227_g02_pass"]
 assert not x["second_pass"]["source_independent_human_auditor_attestation"]

def test_audio_pcm_every_source_second_and_source_frame_window_passes():
 r=m.maizen_second_pass_av_evidence()
 assert r["mechanical_sound_frame_qc_all_73_windows"]
 assert r["audio_event_model_second_check_all_73_windows"]
 assert r["visual_sample_second_review_windows"]==73
 assert r["original_source_frames_sampled"]==289
 assert {x["all_30s_windows"] for x in r["source_videos"]}=={35,38}
 for x in r["source_videos"]:
  assert x["independent_pcm_second_pass_complete"]
  assert x["native_speed_targeted_browser_replays_hashed"]
  assert x["audio_event_second_model_all_windows_complete"]
  assert x["audio_1s_bins_covered"]>1000
  assert not x["actual_human_independent_every_frame_every_sound_signoff"]

def test_both_independent_human_av_and_source_gates_remain_locked():
 x=m.maizen_second_pass_av_evidence()
 assert not x["each_video_independent_human_direct_sound_picture_qc_signed_off"]
 assert not x["human_complete_original_SFX_music_listening_achieved"]
 assert not x["v227_strict_g02_gate_passed"]
 assert not x["g03_to_g28_rendering_backend_production_method_approved"]
 assert not x["known_exact_maizen_software_mod_stack"]
 assert "chest" in x["important_corrected_finding"].lower()
 assert x["no_paid_API_used"]

def test_machine_receipts_disappear_closed(monkeypatch,tmp_path):
 monkeypatch.setattr(m,"EVIDENCE",tmp_path/"no-source")
 a=m.maizen_second_pass_av_evidence()
 assert not a["mechanical_sound_frame_qc_all_73_windows"]
 assert not a["audio_event_model_second_check_all_73_windows"]
 assert a["visual_sample_second_review_windows"]==0
 assert not a["v227_strict_g02_gate_passed"]

def test_exposed_read_only_mcp_and_cli():
 assert "maizen_second_pass_av_evidence" in build_server()._tool_manager._tools
 r=CliRunner().invoke(app,["maizen-independent-av"])
 assert r.exit_code==0,str(r.exception)
 x=json.loads(r.output)
 assert x["visual_sample_second_review_windows"]==73
 assert not x["v227_strict_g02_gate_passed"]
