"""Bounded LOCAL Wan video workflow executable smoke for CineFactory.

Uses only 127.0.0.1 ComfyUI and an already installed local checkpoint.
No cloud API, third-party competitor media, automatic model download, YouTube
upload, or creative quality approval. Records actual render wall time and hash.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen

BASE="http://127.0.0.1:8188"
MODEL="wan2.1_fun_inp_1.3B_bf16.safetensors"
T5="umt5_xxl_fp8_e4m3fn_scaled.safetensors"
VAE="wan_2.1_vae.safetensors"


def http_json(endpoint, payload=None, *, timeout=12):
    url=BASE+endpoint
    if payload is None:
        with urlopen(url,timeout=timeout) as stream:return json.load(stream)
    bytes_=json.dumps(payload).encode("utf-8")
    with urlopen(Request(url,data=bytes_,headers={"Content-Type":"application/json"}),
                 timeout=timeout) as stream:return json.load(stream)


def build_workflow(*,seed=2077,steps=8,width=320,height=192,frames=17):
    if not isinstance(seed,int) or not 0<=seed<2**63 or not 2<=steps<=32:
        raise ValueError("Fixed bounded local pilot seed/steps required")
    if width>640 or height>384 or width%16 or height%16 or frames not in range(9,50,4):
        raise ValueError("Safe local probe is deliberately small")
    return {
        "1":{"class_type":"UNETLoader","inputs":{"unet_name":MODEL,"weight_dtype":"default"}},
        "2":{"class_type":"CLIPLoader","inputs":{"clip_name":T5,"type":"wan"}},
        "3":{"class_type":"VAELoader","inputs":{"vae_name":VAE}},
        "4":{"class_type":"CLIPTextEncode","inputs":{"clip":["2",0],
             "text":"Original toy-like wooden robot with expressive bright eyes moves its head slowly beside a blue lamp; single clear continuous camera, clean background, cinematic warm light"}},
        "5":{"class_type":"CLIPTextEncode","inputs":{"clip":["2",0],
             "text":"character identity drifting, blurring, clutter, duplicate body parts, flicker, watermark"}},
        "6":{"class_type":"WanFunInpaintToVideo","inputs":{
             "positive":["4",0],"negative":["5",0],"vae":["3",0],
             "width":width,"height":height,"length":frames,"batch_size":1}},
        "7":{"class_type":"ModelSamplingSD3","inputs":{"model":["1",0],"shift":8.0}},
        "8":{"class_type":"KSampler","inputs":{"model":["7",0],"positive":["6",0],
             "negative":["6",1],"latent_image":["6",2],"seed":seed,
             "steps":steps,"cfg":4.0,"sampler_name":"euler","scheduler":"simple","denoise":1.0}},
        "9":{"class_type":"VAEDecode","inputs":{"samples":["8",0],"vae":["3",0]}},
        "10":{"class_type":"SaveImage","inputs":{"images":["9",0],
              "filename_prefix":"CineFactory_Local_Wan_Technical_Pilot"}},
    }


def _inputs_available(info):
    for name in ("UNETLoader","CLIPLoader","VAELoader","WanFunInpaintToVideo",
                 "CLIPTextEncode","ModelSamplingSD3","KSampler","VAEDecode","SaveImage"):
        if name not in info:return False,"Missing node "+name
    for node, key, model in (("UNETLoader","unet_name",MODEL),
                             ("CLIPLoader","clip_name",T5),
                             ("VAELoader","vae_name",VAE)):
        item=info[node]["input"]["required"][key][0]
        if model not in item:return False,"Missing installed weight "+model
    return True,"Models and nodes listed by live backend; not a render-quality proof"


def run_pilot(output_dir, *, max_wait_seconds=420,seed=2077):
    if not 30<=max_wait_seconds<=1200:raise ValueError("Bounded model job required")
    out=Path(output_dir).resolve()
    if out.exists():raise FileExistsError("No overwrite of prior pilot results")
    out.mkdir(parents=True)
    started=time.monotonic()
    record={"schema":"cine.studio.wan_local_smoke.v1",
            "started_at_utc":datetime.now(timezone.utc).isoformat(),
            "state":"NOT_SUBMITTED","workflow":build_workflow(seed=seed),
            "model_names":[MODEL,T5,VAE],"model_license_verified":False,
            "independent_artistic_qc_passed":False,
            "production_permission":False}
    try:
        info=http_json("/object_info",timeout=15)
        okay,detail=_inputs_available(info)
        if not okay:
            record.update({"state":"BLOCKED_MISSING_MODEL_OR_NODE","reason":detail})
            return record
        request=http_json("/prompt",{"prompt":record["workflow"],
                    "client_id":"cinefactory-local-smoke"},timeout=20)
        if "error" in request:
            record.update({"state":"COMFY_WORKFLOW_VALIDATION_FAILED",
                           "reason":str(request.get("error"))[:800]})
            return record
        ident=request.get("prompt_id")
        if not ident:raise RuntimeError("Comfy backend returned no prompt_id")
        record["prompt_id"]=ident
        deadline=time.monotonic()+max_wait_seconds
        while time.monotonic()<deadline:
            hist=http_json("/history/"+ident,timeout=10).get(ident)
            if hist:
                record["backend_status"]=hist.get("status",{})
                node=hist.get("outputs",{}).get("10",{})
                images=node.get("images",[])
                if not images:
                    record.update({"state":"WORKFLOW_EXECUTION_FAILED_OR_NO_FRAMES",
                                   "reason":str(hist.get("status",{}))[:1000]})
                    return record
                frames_dir=out/"frames";frames_dir.mkdir()
                for i,entry in enumerate(images):
                    query=urlencode({"filename":entry["filename"],
                                    "subfolder":entry.get("subfolder",""),
                                    "type":entry.get("type","output")})
                    with urlopen(BASE+"/view?"+query,timeout=12) as stream:
                        binary=stream.read(8_000_000)
                    if not binary.startswith(b"\x89PNG") or len(binary)>=8_000_000:
                        raise ValueError("Unexpected output image payload")
                    (frames_dir/f"frame_{i:04d}.png").write_bytes(binary)
                video=out/"wan_technical_smoke.mp4"
                ff=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error",
                    "-y","-framerate","8","-i",str(frames_dir/"frame_%04d.png"),
                    "-c:v","libx264","-pix_fmt","yuv420p",str(video)],
                    text=True,capture_output=True,timeout=90)
                if ff.returncode!=0:raise RuntimeError("FFmpeg encode failed: "+ff.stderr[-500:])
                record.update({"state":"LOCAL_VIDEO_RENDERED_UNREVIEWED",
                               "frame_count":len(images),"video_path":str(video),
                               "video_sha256":hashlib.sha256(video.read_bytes()).hexdigest()})
                return record
            time.sleep(2)
        record.update({"state":"LOCAL_MODEL_RENDER_TIMEOUT","reason":"Generation exceeded explicitly bounded pilot period"})
        return record
    except Exception as exc:
        record.update({"state":"PILOT_RUNTIME_FAILED","reason":type(exc).__name__+": "+str(exc)[:700]})
        return record
    finally:
        record["wall_seconds"]=round(time.monotonic()-started,2)
        record["completed_at_utc"]=datetime.now(timezone.utc).isoformat()
        (out/"pilot_report.json").write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--output-dir",required=True)
    cli.add_argument("--max-wait-seconds",type=int,default=420)
    args=cli.parse_args()
    result=run_pilot(args.output_dir,max_wait_seconds=args.max_wait_seconds)
    print(json.dumps({"state":result["state"],"wall_seconds":result.get("wall_seconds"),
                      "frame_count":result.get("frame_count"),"production_permission":False}))
