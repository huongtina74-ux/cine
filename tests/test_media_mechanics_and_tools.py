from __future__ import annotations
import json,subprocess
from pathlib import Path
import pytest

from cinefactory.research_intelligence.media_mechanics import prepare_media_mechanics
from cinefactory.production import tool_runtime_audit as tools


@pytest.fixture
def mini_video(tmp_path):
    p=tmp_path/"owned_test.mp4"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","lavfi","-i","testsrc2=size=640x360:duration=3:rate=12",
        "-f","lavfi","-i","sine=frequency=440:duration=3",
        "-c:v","mpeg4","-q:v","5","-c:a","aac","-shortest",str(p)],
        check=True,timeout=30)
    return p


def test_full_mechanical_study_measures_audio_and_not_fiction(mini_video,tmp_path):
    r=prepare_media_mechanics(mini_video,tmp_path/"study",permission="OWNED",
                               max_scan_seconds=5,fps=3)
    assert r["coverage_ratio"]==1.0
    assert r["segment_count"]>=1
    assert r["audio_status"]=="SILENCE_ENVELOPE_MEASURED_NO_SEMANTICS"
    assert r["timeline_sha256"]
    assert all(x["script"]=="NOT_OBSERVED" for x in r["observation_worklist"])
    assert r["production_permission"] is False


def test_incomplete_footage_window_is_reported(mini_video,tmp_path):
    # Actual authorized source is 3 seconds; 2 seconds is below the minimum timeline
    # scan window, so invalid configuration must fail rather than claim full coverage.
    with pytest.raises(ValueError):
        prepare_media_mechanics(mini_video,tmp_path/"partial",permission="OWNED",
                                max_scan_seconds=2)


def test_unlicensed_video_is_blocked(mini_video,tmp_path):
    with pytest.raises(PermissionError):
        prepare_media_mechanics(mini_video,tmp_path/"not_authorized",permission="UNKNOWN")


def test_tool_audit_is_readonly_and_never_promotes_models(monkeypatch,tmp_path):
    monkeypatch.setattr(tools,"_binary",lambda *a,**k:None)
    monkeypatch.setattr(tools,"_comfy_loopback",lambda:{"state":"COMFY_LOOPBACK_API_RESPONDED","workflows_validated":False})
    monkeypatch.setattr(tools,"_gpus",lambda:{"state":"GPU_HARDWARE_OBSERVED","devices":[{"name":"test","memory_mib":12288}]})
    r=tools.audit_local_toolchains(tmp_path/"audit.json")
    assert r["comfyui"]["state"]=="COMFY_LOOPBACK_API_RESPONDED"
    assert r["lanes"]["comfyui_controlled_ai_video"]["production_quality"]=="NOT_BENCHMARKED"
    assert r["tool_versions"]["blender"]["state"]=="BINARY_ABSENT"
    assert r["production_permission"] is False
    assert r["models_or_checkpoints_license_verified"] is False
    with pytest.raises(FileExistsError):
        tools.audit_local_toolchains(tmp_path/"audit.json")


def test_actual_render_sha_can_promote_runtime_only_not_quality(mini_video,tmp_path,monkeypatch):
    import hashlib
    monkeypatch.setattr(tools,"_binary",lambda *a,**k:None)
    monkeypatch.setattr(tools,"_comfy_loopback",
                        lambda:{"state":"COMFY_LOOPBACK_API_RESPONDED"})
    monkeypatch.setattr(tools,"_gpus",lambda:{"state":"NO_NVIDIA_QUERY","devices":[]})
    evidence=tmp_path/"pilot.json"
    evidence.write_text(json.dumps({
        "schema":"cine.studio.wan_local_smoke.v1",
        "state":"LOCAL_VIDEO_RENDERED_UNREVIEWED",
        "video_path":str(mini_video),
        "video_sha256":hashlib.sha256(mini_video.read_bytes()).hexdigest(),
        "frame_count":36,"wall_seconds":2.6}),encoding="utf-8")
    report=tools.audit_local_toolchains(tmp_path/"runtime.json",pilot_report=evidence)
    lane=report["lanes"]["comfyui_controlled_ai_video"]
    assert lane["runtime_state"]=="LOCAL_VIDEO_EXECUTED_UNREVIEWED"
    assert lane["production_quality"]=="NOT_BENCHMARKED"
    assert report["actual_local_video_smoke"]["width"]==640
    assert not report["actual_local_video_smoke"]["quality_reviewed"]
    evidence_json=json.loads(evidence.read_text(encoding="utf-8"))
    evidence_json["video_sha256"]="0"*64
    evidence.write_text(json.dumps(evidence_json),encoding="utf-8")
    with pytest.raises(ValueError,match="hash-correct"):
        tools.audit_local_toolchains(tmp_path/"tampered.json",pilot_report=evidence)


def test_ffmpeg_version_probe_uses_single_dash(monkeypatch):
    from types import SimpleNamespace
    observed=[]
    def fake_version(cmd,**kwargs):
        observed.append(cmd)
        return SimpleNamespace(returncode=0,stdout="ffmpeg version 7.1",stderr="")
    monkeypatch.setattr(tools.subprocess,"run",fake_version)
    assert tools._safe_version(r"C:\tools\ffmpeg.exe")["state"]=="EXECUTABLE_VERSION_OBSERVED"
    assert observed[0][1]=="-version"
    assert tools._safe_version(r"C:\tools\blender.exe")["state"]=="EXECUTABLE_VERSION_OBSERVED"
    assert observed[1][1]=="--version"
