"""Read-only capability audit for local media software / GPU and ComfyUI.

Never equate executable presence, a model name, or GPU capacity with approved
rendering quality. Remote/cloud/MCP tools require independent legal and
runtime authorization before production.
"""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess
import http.client
from datetime import datetime,timezone
from pathlib import Path

from .niche_production_conference import TOOL_CATALOG


def _binary(name, env_var=None, fallbacks=()):
    candidates = []
    if env_var and os.environ.get(env_var):
        candidates.append(os.environ[env_var])
    resolved = shutil.which(name)
    if resolved:candidates.append(resolved)
    candidates += [p for p in fallbacks if p]
    for item in candidates:
        if Path(item).is_file():
            return str(Path(item).resolve())
    return None


def _safe_version(binary, *, timeout=12):
    if not binary:return {"state":"BINARY_ABSENT"}
    try:
        # FFmpeg/FFprobe use -version; Blender uses --version.
        flag="-version" if Path(binary).stem.lower() in ("ffmpeg","ffprobe") else "--version"
        p=subprocess.run([binary,flag],text=True,capture_output=True,
                         timeout=timeout,check=False)
        return {"state":"EXECUTABLE_VERSION_OBSERVED" if p.returncode==0 else "VERSION_COMMAND_FAILED",
                "reported_version":((p.stdout or p.stderr).splitlines() or [""])[0][:240],
                "exit_code":p.returncode}
    except (OSError,subprocess.TimeoutExpired) as exc:
        return {"state":"VERSION_COMMAND_FAILED","reason":str(exc)[:160]}


def _comfy_loopback():
    # No arbitrary external host/endpoint, credentials or user-supplied URL.
    try:
        c=http.client.HTTPConnection("127.0.0.1",8188,timeout=3)
        c.request("GET","/system_stats")
        res=c.getresponse()
        if res.status!=200: return {"state":"LOOPBACK_API_UNHEALTHY","http_status":res.status}
        payload=json.loads(res.read(500_000).decode("utf-8"))
        return {"state":"COMFY_LOOPBACK_API_RESPONDED",
                "system":str(payload.get("system",{}).get("comfyui_version","UNKNOWN")),
                "device_count":len(payload.get("devices",[]) if isinstance(payload.get("devices"),list) else []),
                "workflow_models_checked":False,
                "workflows_validated":False}
    except (OSError,ValueError,TypeError) as err:
        return {"state":"COMFY_LOOPBACK_NOT_AVAILABLE","reason":type(err).__name__}
    finally:
        try:c.close()
        except (NameError,OSError):pass


def _gpus():
    exe=shutil.which("nvidia-smi")
    if not exe:return {"state":"NO_NVIDIA_QUERY","devices":[]}
    try:
        res=subprocess.run([exe,"--query-gpu=name,memory.total",
                            "--format=csv,noheader,nounits"],capture_output=True,text=True,
                           timeout=10,check=False)
        if res.returncode!=0:return {"state":"GPU_QUERY_FAILED","devices":[]}
        rows=[]
        for line in res.stdout.splitlines()[:16]:
            if "," not in line:continue
            name,raw=line.rsplit(",",1)
            try:memory=int(raw.strip())
            except ValueError:continue
            rows.append({"name":name.strip(),"memory_mib":memory})
        return {"state":"GPU_HARDWARE_OBSERVED" if rows else "GPU_QUERY_EMPTY","devices":rows}
    except (OSError,subprocess.TimeoutExpired):
        return {"state":"GPU_QUERY_FAILED","devices":[]}


def audit_local_toolchains(output:str|Path, *, blender_exe=None, pilot_report=None) -> dict:
    result_path=Path(output)
    if result_path.exists():raise FileExistsError("Tool audit is immutable")
    pff=_binary("ffmpeg")
    pprobe=_binary("ffprobe")
    blender=_binary("blender",env_var="BLENDER_BINARY",
                    fallbacks=[blender_exe,
                    r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe",
                    r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"])
    binaries={"ffmpeg":{"path":pff,**_safe_version(pff)},
              "ffprobe":{"path":pprobe,**_safe_version(pprobe)},
              "blender":{"path":blender,**_safe_version(blender)}}
    runtime_comfy=_comfy_loopback()
    gpus=_gpus()
    real_video_smoke=None
    if pilot_report is not None:
        p=Path(pilot_report).resolve(strict=True)
        packet=json.loads(p.read_text(encoding="utf-8"))
        if packet.get("schema")!="cine.studio.wan_local_smoke.v1":
            raise ValueError("Unknown video smoke evidence type")
        path=Path(packet.get("video_path","")).resolve(strict=True)
        if (packet.get("state")!="LOCAL_VIDEO_RENDERED_UNREVIEWED"
            or hashlib.sha256(path.read_bytes()).hexdigest()!=packet.get("video_sha256")):
            raise ValueError("Local video smoke evidence is not independently hash-correct")
        inspected=subprocess.run(["ffprobe","-v","error","-show_entries","stream=width,height:format=duration",
                                  "-of","json",str(path)],capture_output=True,text=True,timeout=20)
        if inspected.returncode!=0:
            raise ValueError("Pilot media could not be decoded")
        detail=json.loads(inspected.stdout)
        video=next((x for x in detail["streams"] if x.get("width") and x.get("height")),None)
        if video is None or float(detail["format"].get("duration",0))<=0:
            raise ValueError("Expected an actual playable pilot")
        real_video_smoke={"pilot_report_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
                          "video_sha256":packet["video_sha256"],"frame_count":packet.get("frame_count"),
                          "width":video["width"],"height":video["height"],
                          "duration_seconds":float(detail["format"]["duration"]),
                          "wall_seconds":packet.get("wall_seconds"),
                          "quality_reviewed":False,"commercial_rights_cleared":False}
    lanes={}
    for lane,metadata in TOOL_CATALOG.items():
        if lane=="blender_character_animation":
            runtime_state=("EXECUTABLE_PRESENT_RENDER_NOT_BENCHMARKED" if binaries["blender"]["state"]=="EXECUTABLE_VERSION_OBSERVED"
                           else "CANDIDATE_RUNTIME_NOT_VERIFIED")
        elif lane=="comfyui_controlled_ai_video":
            runtime_state=("LOCAL_VIDEO_EXECUTED_UNREVIEWED" if real_video_smoke
                           else "API_LIVE_WORKFLOW_UNBENCHMARKED" if runtime_comfy["state"]=="COMFY_LOOPBACK_API_RESPONDED"
                           else "CANDIDATE_RUNTIME_NOT_VERIFIED")
        elif lane in ("audio_environment","remotion_graphics","resolve_master_finishing"):
            runtime_state=("FFMPEG_ONLY_OTHER_TOOLS_UNVERIFIED" if pff else "CANDIDATE_RUNTIME_NOT_VERIFIED")
        else:
            runtime_state="CANDIDATE_RUNTIME_NOT_VERIFIED"
        lanes[lane]={"runtime_state":runtime_state,
                     "license_state":"NOT_CLEARED",
                     "production_quality":"NOT_BENCHMARKED",
                     "official_reference":metadata["official"],
                     "critical_tests":metadata["critical_tests"],
                     "commercial_use_permission":False}
    record={
        "schema":"cine.studio.local_tool_runtime_audit.v1",
        "observed_at_utc":datetime.now(timezone.utc).isoformat(),
        "state":"LOCAL_CAPABILITY_DISCOVERY_ONLY",
        "tool_versions":binaries,
        "comfyui":runtime_comfy,"gpu_pool":gpus,
        "actual_local_video_smoke":real_video_smoke,
        "lanes":lanes,
        "hardware_ceiling_policy":"NO_ASSUMED_MAX_GPU_WORKER_COUNT_OR_VRAM",
        "outside_cloud_saas_mcp_services_probed":False,
        "models_or_checkpoints_license_verified":False,
        "same_shot_quality_bakeoff_completed":False,
        "production_permission":False,
        "human_director_and_qc_approval_authenticated":False,
    }
    result_path.parent.mkdir(parents=True,exist_ok=True)
    result_path.write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return record


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--output",required=True)
    cli.add_argument("--blender-exe")
    cli.add_argument("--pilot-report")
    args=cli.parse_args()
    r=audit_local_toolchains(args.output,blender_exe=args.blender_exe,
                             pilot_report=args.pilot_report)
    print(json.dumps({"state":r["state"],"blender":r["tool_versions"]["blender"]["state"],
                      "comfyui":r["comfyui"]["state"],"gpu":r["gpu_pool"]["state"],
                      "same_shot_quality_bakeoff_completed":False}))
