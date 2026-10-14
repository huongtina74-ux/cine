"""Reality-check scoring must not confuse artifact, worker, media or AI review with production readiness."""
from cinefactory.studio.company_reality_probe_v265 import grade
def fixtures():
    ready={"production_ready":False,"departments":{
      "STUDIO_MANAGEMENT":{"independent_executable_verified":False,
          "independent_art_quality_qualified":False},
      "EVIDENCE":{"independent_executable_verified":False,
          "independent_art_quality_qualified":False}},
     "workers":{"stored_workers":8,"active_fresh_workers":0,"stale_reported_healthy":8}}
    records=[
      {"stage_id":"PROJECT_INTAKE","state":"SUCCEEDED"},
      {"stage_id":"PORTFOLIO_GREENLIGHT","state":"SUCCEEDED"},
      {"stage_id":"INTELLIGENCE","state":"SUCCEEDED"},
      {"stage_id":"EVIDENCE","state":"SKIPPED"},
      {"stage_id":"CORPORATE_PREFLIGHT","state":"NEEDS_REPAIR"},
      {"stage_id":"WRITING","state":"PENDING"},
      {"stage_id":"DIRECTION","state":"PENDING"}]
    run={"project_id":"PILOT_ONLY","complete":False,"cycles":5,
          "errors":["CORPORATE_PREFLIGHT:CORPORATE_PREFLIGHT_BLOCKED"],
          "ledger":{"records":records}}
    media={"actual_playable_video_audio":True,"full_file_decode_QA":True,
           "camera_3D":False,"media_duration_sec":15,"dimensions":[640,360],
           "offline_TTS":"MICROSOFT_ZIRA_SCRATCH_ONLY"}
    routes={"blender.local":{"available":False},
             "ffmpeg.editorial":{"available":True}}
    return ready,run,media,routes
def test_demo_media_pass_does_not_approve_real_film_or_downstream_company():
    a=grade(*fixtures())
    assert a["automated_test_checks_passed"]==3
    assert a["automated_test_checks_total"]==14
    assert a["checks"]["R10_ACTUAL_MOVING_AND_AUDIBLE_RND_MEDIA"]
    assert not a["checks"]["R7_REAL_3D_ENGINE_VERSIONED"]
    assert not a["checks"]["R13_COMPANY_EPISODE_END_TO_END"]
    assert not a["actual_production_line_complete"]
    assert a["runner_stages"]["EVIDENCE"]=="SKIPPED"
    assert a["runner_stages"]["WRITING"]=="PENDING"
    assert "BLENDER_EXECUTABLE_UNVERIFIED" in a["findings"]
def test_stale_workers_do_not_count_as_running():
    a=grade(*fixtures())
    assert not a["checks"]["R9_ACTIVE_RENDER_WORKER"]
    assert "STALE_WORKER_HEALTH_MUST_NOT_BE_CONSIDERED_ACTIVE" in a["findings"]
def test_bogus_production_ready_is_caught():
    args=fixtures()
    args[0]["production_ready"]=True
    a=grade(*args)
    assert "DECLARED_PRODUCTION_READY_WITHOUT_REAL_CINEMATIC_ACCEPTANCE" in a["findings"]
def test_done_runner_cannot_bypass_corporate_preflight():
    args=fixtures()
    args[1]["complete"]=True
    a=grade(*args)
    assert "RUNNER_BYPASSED_CORPORATE_PREFLIGHT" in a["findings"]
    # A malicious or incorrect ledger says complete, never promote production quality.
    assert a["actual_production_line_complete"] is False
