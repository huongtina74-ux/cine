from __future__ import annotations
"""v1.6.36 real same-scene Blender Workbench vs Eevee comparison.

Actual pixels/frames, wall time and global RTX memory observations from subprocess
are evidence. Output is a renderer A/B within ONE SOFTWARE, not Blender vs
Godot vs AI, nor a subjective viewer quality or total USD-cost certificate.
"""
import hashlib
import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Literal
from pydantic import BaseModel,Field,model_validator

class RenderSample(BaseModel):
    engine: Literal["workbench","eevee"]
    backend_name: str
    blender_scene_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    source_worker_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    actual_rendered_frame_count: int = Field(gt=0)
    fps: int = Field(gt=0)
    image_resolution: tuple[int,int]
    png_frame_hashes: list[str] = Field(min_length=1)
    render_wall_seconds: float = Field(gt=0)
    encode_wall_seconds: float = Field(gt=0)
    mp4_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    mp4_path: str
    mp4_bytes: int = Field(gt=0)
    video_codec: str
    decoded_frame_count: int = Field(gt=0)
    audio_present: bool = False
    png_mean_luminance: float | None = Field(default=None,ge=0,le=255)
    png_edge_variance: float | None = Field(default=None,ge=0)
    measured_global_gpu_used_peak_mib: float | None = Field(default=None,ge=0)
    measured_global_gpu_baseline_mib: float | None = Field(default=None,ge=0)
    global_gpu_memory_is_not_blender_vram: bool = True
    software_runtime_tested: bool = True
    royalty_licence_cleared: bool = False
    human_creative_quality_reviewed: bool = False
    accepted_minute_cost_usd: float | None = None
    closed_source_model_deployment_cleared: bool = False
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def all_frames_verified(self):
        if self.actual_rendered_frame_count!=len(self.png_frame_hashes):
            raise ValueError("FRAME_SHA_COUNT_MISMATCH")
        if self.decoded_frame_count!=self.actual_rendered_frame_count:
            raise ValueError("ENCODED_DECODE_FRAME_COUNT_MISMATCH")
        return self

class GoldenShotBenchmark(BaseModel):
    status:Literal["REAL_SAME_SCENE_RENDER_ENGINE_AB_PASS_PRODUCTION_BLOCKED",
                   "PARTIAL_OR_FAILED_PRODUCTION_BLOCKED"]
    source_scene:str
    source_scene_sha256:str
    original_rig_source:str
    source_contract:str
    actual_two_engines_tested:bool
    different_video_software_tested:bool=False
    head_to_head_quality_claim:bool=False
    objective_speed_faster_engine:str|None=None
    true_electricity_dollars_measured:bool=False
    accepted_minute_cost_usd_measured:bool=False
    per_process_peak_vram_measured:bool=False
    human_blind_review_complete:bool=False
    production_release_authorized:bool=False
    results:list[RenderSample]
    blockers:list[str]
    errors:dict[str,str]=Field(default_factory=dict)

def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):
            h.update(chunk)
    return h.hexdigest()

def _gpu_memory_total_mib()->float|None:
    nvsmi=shutil.which("nvidia-smi")
    if not nvsmi:return None
    try:
        p=subprocess.run([nvsmi,"--query-gpu=memory.used",
                         "--format=csv,noheader,nounits"],
                         capture_output=True,text=True,timeout=4,check=False)
        if p.returncode!=0:return None
        return float(p.stdout.splitlines()[0].strip())
    except (OSError,ValueError,IndexError,subprocess.TimeoutExpired):
        return None

def _render(root:Path,out:Path,scene:Path,engine:str)->tuple[float,float|None,float|None]:
    blender=root/".tools/blender-4.5.14-windows-x64/blender.exe"
    script=root/"scripts/blender_golden_scene_v196.py"
    if not blender.is_file() or not script.is_file():
        raise RuntimeError("EXACT_BLENDER_EXECUTABLE_OR_BENCHMARK_SCRIPT_MISSING")
    args=[str(blender),"-b",str(scene),"-t","4",
          "--python",str(script),"--","--mode","render",
          "--root",str(root),"--out",str(out),
          "--engine",engine,"--fps","12","--frames","24",
          "--width","480","--height","270"]
    started=time.perf_counter()
    log=out/(engine+"_render.log")
    baseline=_gpu_memory_total_mib()
    peak=baseline
    with log.open("wb") as f:
        proc=subprocess.Popen(args,stdout=f,stderr=subprocess.STDOUT,cwd=root)
        try:
            while proc.poll() is None:
                if time.perf_counter()-started>420:
                    proc.kill()
                    raise TimeoutError("BLENDER_RENDER_EXCEEDED_420_SECONDS")
                val=_gpu_memory_total_mib()
                if val is not None:peak=max(peak or 0.,val)
                time.sleep(.6)
            ret=proc.wait(timeout=5)
        finally:
            if proc.poll() is None:
                proc.kill();proc.wait(timeout=5)
    elapsed=time.perf_counter()-started
    if ret!=0:
        raise RuntimeError("BLENDER_RENDER_FAILED:"+log.read_text(errors="replace")[-1400:])
    return elapsed,baseline,peak

def _encode_png_sequence(root:Path,out:Path,engine:str)->tuple[Path,float]:
    ffmpeg=shutil.which("ffmpeg")
    if not ffmpeg:raise RuntimeError("FFMPEG_NOT_AVAILABLE")
    target=out/(engine+".mp4")
    cmd=[ffmpeg,"-hide_banner","-loglevel","error","-y",
         "-framerate","12","-start_number","1",
         "-i",str(out/"frames"/engine/"frame_%04d.png"),
         "-c:v","libx264","-preset","fast","-crf","20",
         "-pix_fmt","yuv420p","-r","12","-an","-movflags","+faststart",str(target)]
    t=time.perf_counter()
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=120,cwd=root,check=False)
    elapsed=time.perf_counter()-t
    if p.returncode:raise RuntimeError("FFMPEG_ENCODE_FAILED:"+p.stderr[-800:])
    return target,elapsed

def _probe_media(path:Path)->dict:
    ffprobe=shutil.which("ffprobe")
    if not ffprobe:raise RuntimeError("FFPROBE_NOT_AVAILABLE")
    cmd=[ffprobe,"-v","error","-count_frames","-show_streams",
         "-of","json",str(path)]
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=60,check=True)
    return json.loads(p.stdout)

def _assess_frames(root:Path,out:Path,engine:str,scene_sha:str,worker_sha:str,
                   seconds:float,baseline:float|None,peak:float|None)->RenderSample:
    import cv2,numpy as np
    files=sorted((out/"frames"/engine).glob("frame_*.png"))
    if len(files)!=24:
        raise RuntimeError(f"{engine}_WRONG_FRAME_COUNT:{len(files)}")
    hashes=[sha(f) for f in files]
    pics=[]
    for frame_path in (files[0],files[len(files)//2],files[-1]):
        img=cv2.imread(str(frame_path),cv2.IMREAD_COLOR)
        if img is None or img.shape[:2]!=(270,480):
            raise RuntimeError("FRAME_MISSING_OR_WRONG_DIMENSIONS")
        pics.append(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY))
    luminosity=round(float(np.mean([np.mean(img) for img in pics])),4)
    edge=round(float(np.mean([cv2.Laplacian(img,cv2.CV_64F).var() for img in pics])),4)
    if len(set(hashes))<=1:
        raise RuntimeError("ALL_ANIMATION_FRAMES_IDENTICAL")
    encoded,encode_seconds=_encode_png_sequence(root,out,engine)
    probe=_probe_media(encoded)
    vids=[s for s in probe["streams"] if s.get("codec_type")=="video"]
    audios=[s for s in probe["streams"] if s.get("codec_type")=="audio"]
    if len(vids)!=1 or audios:
        raise RuntimeError("VIDEO_STREAM_COUNT_UNEXPECTED")
    stream=vids[0]
    actual_frames=int(stream.get("nb_read_frames") or 0)
    if actual_frames!=24:raise RuntimeError("DECODED_FRAME_COUNT_UNEXPECTED")
    return RenderSample(
        engine=engine,backend_name=(
            "Blender Workbench OpenGL/studio shading"
            if engine=="workbench" else "Blender Eevee Next real-time raster renderer"),
        blender_scene_sha256=scene_sha,source_worker_sha256=worker_sha,
        actual_rendered_frame_count=24,fps=12,image_resolution=(480,270),
        png_frame_hashes=hashes,render_wall_seconds=round(seconds,4),
        encode_wall_seconds=round(encode_seconds,4),
        mp4_sha256=sha(encoded),mp4_path=str(encoded.resolve()),
        mp4_bytes=encoded.stat().st_size,video_codec=stream["codec_name"],
        decoded_frame_count=actual_frames,
        png_mean_luminance=luminosity,png_edge_variance=edge,
        measured_global_gpu_used_peak_mib=peak,
        measured_global_gpu_baseline_mib=baseline,
        notes=["TWO_RENDER_ENGINES_SAME_BLENDER_PROJECT_NOT_TWO_SOFTWARES",
               "LUMINANCE_AND_SHARPNESS_ARE_NOT_PERCEPTUAL_QUALITY_SCORES",
               "GLOBAL_GPU_MEMORY_SHARED_WITH_OTHER_PROCESSES",
               "NO_SCORE_FOR_CHARACTER_ACTING_NARRATIVE_MUSIC_ORIGINALITY",
               "RENDER_TIME_INCLUDES_BLENDER_STARTUP_IN_THIS_ONE_SAMPLE"],
    )

def run_real_golden_benchmark(root:Path)->GoldenShotBenchmark:
    root=Path(root).resolve()
    out=root/"data/verification/v196_golden_benchmark"
    scene=out/"golden_cinefactory_original_scene.blend"
    contract=out/"scene_contract_v196.json"
    assert scene.is_file() and contract.is_file()
    contract_data=json.loads(contract.read_text(encoding="utf-8"))
    if contract_data["frames"]!=24 or contract_data["fps"]!=12 or contract_data["resolution"]!=[480,270]:
        raise ValueError("GOLDEN_SHOT_CONTRACT_MISMATCH")
    scene_sha=sha(scene)
    worker_sha=sha(root/"scripts/blender_animation_worker.py")
    results=[];errors={}
    for engine in ("workbench","eevee"):
        print("REAL_RENDER_START",engine,flush=True)
        try:
            elapsed,baseline,peak=_render(root,out,scene,engine)
            data=_assess_frames(root,out,engine,scene_sha,worker_sha,elapsed,baseline,peak)
            if sha(scene)!=scene_sha:raise RuntimeError("BASE_SCENE_MUTATED_AFTER_RENDER")
            results.append(data)
            print("REAL_RENDER_PASS",engine,"frames",data.actual_rendered_frame_count,
                  "render_wall",data.render_wall_seconds,
                  "peak_global_gpu_mem",data.measured_global_gpu_used_peak_mib,
                  "bytes",data.mp4_bytes,flush=True)
        except Exception as ex:
            errors[engine]=type(ex).__name__+":"+str(ex)[:1800]
            print("REAL_RENDER_BLOCKED",engine,errors[engine],flush=True)
    success=len(results)==2 and not errors
    faster=min(results,key=lambda x:x.render_wall_seconds).engine if success else None
    outcome=GoldenShotBenchmark(
        status="REAL_SAME_SCENE_RENDER_ENGINE_AB_PASS_PRODUCTION_BLOCKED"
               if success else "PARTIAL_OR_FAILED_PRODUCTION_BLOCKED",
        source_scene=str(scene.resolve()),source_scene_sha256=scene_sha,
        original_rig_source=str((root/"scripts/blender_animation_worker.py").resolve()),
        source_contract=str(contract.resolve()),
        actual_two_engines_tested=success,objective_speed_faster_engine=faster,
        results=results,errors=errors,
        blockers=[
            "ONE_SCENE_AND_ONE_RUN_PER_ENGINE_NOT_STATISTICALLY_RELIABLE",
            "WORKBENCH_AND_EEVEE_ARE_BOTH_IN_BLENDER_NOT_COMPETING_STANDALONE_TOOLS",
            "NO_BLIND_HUMAN_ARTISTIC_QUALITY_OR_ORIGINALITY_REVIEW",
            "NO_TOTAL_USD_PER_ACCEPTED_VIDEO_MINUTE_OR_ACTUAL_WATTMETER",
            "GPU_MEM_SAMPLES_ARE_TOTAL_SHARED_GPU_NOT_BLENDER_PROCESS_VRAM",
            "NO_CHILD_STORY_MUSIC_CHARACTER_ACTING_BENCHMARK",
            "NO_COMMERCIAL_MEDIA_IP_AND_RIGHTS_SIGNOFF",
            "DIFFERENT_LOOKS_SSIM_CANNOT_RANK_ARTISTIC_SUPERIORITY",
            "NO_AUTOMATIC_PRODUCTION_PROMOTION_OR_PUBLISHING",
        ])
    (out/"real_render_engine_ab_evidence_v196.json").write_text(
        outcome.model_dump_json(indent=2),encoding="utf-8")
    return outcome

class RenderRepeatabilityEvidence(BaseModel):
    status:Literal["SAME_PROJECT_THREE_EXTRA_TRIALS_COMPLETE_NOT_PRODUCTION_CERTIFIED",
                   "REPEATED_TRIALS_INCOMPLETE"]
    exact_original_scene_sha256:str
    trials_per_engine_expected:int=4
    reports:list[RenderSample]
    render_order:list[str]
    median_render_seconds_by_engine:dict[str,float]
    maximum_render_seconds_by_engine:dict[str,float]
    fastest_median_engine:str|None=None
    first_run_is_not_representative:bool=True
    actual_source_geometry_identical:bool=True
    output_bytewise_deterministic:dict[str,bool]
    cross_software_comparison_complete:bool=False
    human_quality_approved:bool=False
    total_accepted_minute_dollar_cost_measured:bool=False
    production_selected:bool=False
    blockers:list[str]
    errors:dict[str,str]=Field(default_factory=dict)

def repeat_4_trials_on_same_scene(root:Path)->RenderRepeatabilityEvidence:
    """Counterbalanced AB/BA trial order; original run counts as trial 1."""
    import statistics
    root=Path(root).resolve()
    out=root/"data/verification/v196_golden_benchmark"
    main=GoldenShotBenchmark.model_validate_json(
        (out/"real_render_engine_ab_evidence_v196.json").read_text(encoding="utf-8"))
    if not main.actual_two_engines_tested or len(main.results)!=2:
        raise ValueError("CANNOT_RETEST_FAILED_ORIGINAL_EXPERIMENT")
    scene=Path(main.source_scene)
    scene_sha=sha(scene)
    if scene_sha!=main.source_scene_sha256:
        raise RuntimeError("ORIGINAL_SCENE_CHANGED")
    worker_sha=sha(root/"scripts/blender_animation_worker.py")
    results=list(main.results)
    render_order=[s.engine for s in main.results]
    errors={}
    # Four total per candidate: AB, BA, AB, BA. Scheduling order alternates.
    for trial,engines in ((2,("eevee","workbench")),
                          (3,("workbench","eevee")),
                          (4,("eevee","workbench"))):
        for engine in engines:
            run_dir=out/"repeatability"/f"round_{trial:02d}"
            run_dir.mkdir(parents=True,exist_ok=True)
            render_order.append(engine)
            print("COUNTERBALANCED_AB_START",trial,engine,flush=True)
            try:
                seconds,baseline,peak=_render(root,run_dir,scene,engine)
                rec=_assess_frames(root,run_dir,engine,scene_sha,worker_sha,
                                   seconds,baseline,peak)
                if sha(scene)!=scene_sha:raise RuntimeError("MAIN_SCENE_MUTATED")
                results.append(rec)
                print("COUNTERBALANCED_AB_PASS",trial,engine,
                      rec.render_wall_seconds,"s",flush=True)
            except Exception as exc:
                errors[f"round_{trial}_{engine}"]=type(exc).__name__+":"+str(exc)[:1400]
                print("COUNTERBALANCED_AB_FAIL",trial,engine,errors[f"round_{trial}_{engine}"],flush=True)
    by_engine={engine:[s for s in results if s.engine==engine]
               for engine in ("workbench","eevee")}
    full=not errors and all(len(group)==4 for group in by_engine.values())
    medians={
        engine:round(float(statistics.median(row.render_wall_seconds for row in group)),4)
        for engine,group in by_engine.items() if group
    }
    maxima={
        engine:round(max(row.render_wall_seconds for row in group),4)
        for engine,group in by_engine.items() if group
    }
    deterministic={
        engine:len({tuple(row.png_frame_hashes) for row in group})==1
        for engine,group in by_engine.items()
    }
    report=RenderRepeatabilityEvidence(
        status=("SAME_PROJECT_THREE_EXTRA_TRIALS_COMPLETE_NOT_PRODUCTION_CERTIFIED"
                if full else "REPEATED_TRIALS_INCOMPLETE"),
        exact_original_scene_sha256=scene_sha,
        reports=results,render_order=render_order,
        median_render_seconds_by_engine=medians,
        maximum_render_seconds_by_engine=maxima,
        fastest_median_engine=min(medians,key=medians.get) if full else None,
        output_bytewise_deterministic=deterministic,
        errors=errors,
        blockers=[
            "FOUR_RUNS_PER_RENDERER_STILL_SINGLE_SCENE_LOW_RESOLUTION",
            "BLENDER_PROCESS_STARTUP_INCLUDED_ALL_TRIALS",
            "GPU_GLOBAL_VRAM_NONISOLATED_PROCESS_AND_OTHER_USERS",
            "ELECTRICITY_DOLLARS_HUMAN_REWORK_AND_RETRIES_NOT_MEASURED",
            "NO_RELIABLE_ARTISTIC_QUALITY_HUMAN_BLIND_REVIEW",
            "NO_CROSS_TOOL_GODOT_COMFYUI_OR_CHILD_MUSICAL_GOLDEN_SHOT",
            "NO_AUTOMATIC_PRODUCTION_PROMOTION",
        ],
    )
    (out/"repeatability_benchmark_evidence_v196.json").write_text(
        report.model_dump_json(indent=2),encoding="utf-8")
    return report

class GoldenShotBenchmarkLab:
    """Company-visible, opt-in engine benchmark; constructor never renders."""
    def __init__(self,root:Path):
        self.root=Path(root).resolve()

    def latest(self)->GoldenShotBenchmark:
        location=self.root/"data/verification/v196_golden_benchmark/real_render_engine_ab_evidence_v196.json"
        return GoldenShotBenchmark.model_validate_json(location.read_text(encoding="utf-8"))

    def latest_repeatability(self)->RenderRepeatabilityEvidence:
        path=self.root/"data/verification/v196_golden_benchmark/repeatability_benchmark_evidence_v196.json"
        return RenderRepeatabilityEvidence.model_validate_json(path.read_text(encoding="utf-8"))

    def run_explicit(self,*,approved_original_scene:bool=False)->GoldenShotBenchmark:
        if not approved_original_scene:
            raise PermissionError("BENCHMARK_REQUIRES_EXPLICIT_ORIGINAL_SCENE_AUTHORIZATION")
        return run_real_golden_benchmark(self.root)

    def repeat_explicit(self,*,approved_original_scene:bool=False)->RenderRepeatabilityEvidence:
        if not approved_original_scene:
            raise PermissionError("BENCHMARK_REQUIRES_EXPLICIT_ORIGINAL_SCENE_AUTHORIZATION")
        return repeat_4_trials_on_same_scene(self.root)
