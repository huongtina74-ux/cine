"""Reproducible, CPU-only SmolVLM image smoke benchmark with objective labels.

Uses PINNED local model. No cloud inference, no GPU VRAM, no channel/publishing action.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = "HuggingFaceTB/SmolVLM2-256M-Video-Instruct"
REVISION = "067788b187b95ebe7b2e040b3e4299e342e5b8fd"


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",required=True)
    parser.add_argument("--max-samples",type=int,default=3)
    parser.add_argument("--deps-dir",help="Optional isolated, previously installed dependencies")
    args=parser.parse_args()
    if args.deps_dir:
        installed=Path(args.deps_dir).resolve(strict=True)
        sys.path.insert(0,str(installed))
    if not 1<=args.max_samples<=4:
        raise ValueError("1..4 controlled images required")
    out=Path(args.output_dir).resolve()
    if out.exists():
        raise FileExistsError("No overwrite of prior benchmark evidence")
    out.mkdir(parents=True)
    os.environ["HF_HUB_OFFLINE"]="1"
    os.environ["TRANSFORMERS_OFFLINE"]="1"
    os.environ["TOKENIZERS_PARALLELISM"]="false"
    os.environ["OMP_NUM_THREADS"]="2"
    os.environ["MKL_NUM_THREADS"]="2"
    from PIL import Image,ImageDraw
    import psutil
    import torch
    from transformers import AutoProcessor,AutoModelForImageTextToText

    torch.set_num_threads(2)
    hardware={"torch_cuda_available":torch.cuda.is_available(),
              "torch_version":torch.__version__,"run_device":"cpu",
              "free_ram_gib_initial":round(psutil.virtual_memory().available/(1024**3),2)}
    if hardware["free_ram_gib_initial"]<5:
        raise RuntimeError("Insufficient free RAM; benchmark refused")
    cache=Path.home()/".cache"/"huggingface"/"hub"/"models--HuggingFaceTB--SmolVLM2-256M-Video-Instruct"/"snapshots"/REVISION
    if not (cache/"model.safetensors").is_file():
        raise FileNotFoundError("Pinned model weight not found in local cache")
    cases=[
        ("redblue","Is the large background mostly red? Answer YES or NO.","YES",
         (220,35,35),"blue_square"),
        ("green","Is the large background mostly red? Answer YES or NO.","NO",
         (36,190,59),"yellow_circle"),
        ("white","Is a solid blue square clearly visible? Answer YES or NO.","NO",
         (240,240,240),"black_text"),
        ("redblue2","Is there a solid blue square clearly visible? Answer YES or NO.","YES",
         (220,35,35),"blue_square"),
    ][:args.max_samples]
    for name,question,truth,bg,shape in cases:
        im=Image.new("RGB",(256,256),bg)
        dr=ImageDraw.Draw(im)
        if shape=="blue_square":dr.rectangle((85,85,165,165),fill=(12,25,230))
        elif shape=="yellow_circle":dr.ellipse((70,70,180,180),fill=(240,230,12))
        elif shape=="black_text":dr.text((80,100),"HELLO",fill=(0,0,0))
        im.save(out/(name+".png"))
    report={"schema":"cine.research.vlm_cpu_smoke.v1",
            "started_at":datetime.now(timezone.utc).isoformat(),
            "model":REPO,"revision":REVISION,
            "license":"apache-2.0","hardware":hardware,
            "dataset":"controlled synthetic geometric images, NOT YouTube videos",
            "target_of_claims":"controlled scene visible background/object only",
            "confidence_in_generalization":"LOW_SMALL_SAMPLE",
            "state":"RUNNING", "tests":[],
            "production_permission":False, "model_deploy_approved":False}
    def save():
        (out/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    save()
    print("MODEL_LOADING_CPU",flush=True)
    load_start=time.monotonic()
    proc=psutil.Process(os.getpid())
    try:
        processor=AutoProcessor.from_pretrained(str(cache),local_files_only=True,trust_remote_code=False)
        model=AutoModelForImageTextToText.from_pretrained(
            str(cache),local_files_only=True,trust_remote_code=False,
            torch_dtype=torch.float32,low_cpu_mem_usage=False).eval().to("cpu")
        report["load_seconds"]=round(time.monotonic()-load_start,3)
        report["rss_after_load_mib"]=round(proc.memory_info().rss/(1024**2),1)
        print("MODEL_LOADED",report["load_seconds"],report["rss_after_load_mib"],flush=True)
        for name,question,truth,_,_ in cases:
            msg=[{"role":"user","content":[
                {"type":"image","path":str(out/(name+".png"))},
                {"type":"text","text":question}]}]
            encoded=processor.apply_chat_template(
                msg,add_generation_prompt=True,tokenize=True,return_dict=True,return_tensors="pt")
            t=time.monotonic()
            with torch.inference_mode():
                ids=model.generate(**encoded,do_sample=False,max_new_tokens=12)
            raw=processor.decode(ids[0][encoded["input_ids"].shape[-1]:],skip_special_tokens=True)
            normalized=raw.strip().upper()
            pred=normalized.split()[0].strip(".,:;! ") if normalized else "UNKNOWN"
            item={"id":name,"question":question,"ground_truth":truth,
                  "prediction":pred,"raw_text":raw[:300],
                  "correct":pred==truth,
                  "inference_seconds":round(time.monotonic()-t,3),
                  "image_path":str(out/(name+".png"))}
            report["tests"].append(item)
            print("CASE",name,raw[:75],"correct",item["correct"],"seconds",item["inference_seconds"],flush=True)
            save()
        correct=sum(case["correct"] for case in report["tests"])
        report["state"]="CPU_EXPERIMENT_COMPLETE"
        report["accuracy"]=round(correct/len(report["tests"]),3)
        report["n"]=len(report["tests"])
        report["rss_final_mib"]=round(proc.memory_info().rss/(1024**2),1)
        report["total_elapsed_seconds"]=round(time.monotonic()-load_start,3)
    except Exception as exc:
        report["state"]="CPU_EXPERIMENT_FAILED"
        report["failure_type"]=type(exc).__name__
        report["failure_summary"]=str(exc)[:200]
    report["completed_at"]=datetime.now(timezone.utc).isoformat()
    save()
    print("FINAL",report["state"],"accuracy",report.get("accuracy"),flush=True)
    return 0 if report["state"]=="CPU_EXPERIMENT_COMPLETE" else 2


if __name__=="__main__":
    raise SystemExit(main())
